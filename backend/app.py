from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
import requests
import pandas as pd
import numpy as np
import pickle
import os
import random
from datetime import datetime, timedelta
import uvicorn

# ================= CONFIGURATION =================
WAQI_TOKEN = "f4b27249a9b4af0009e286a346517d39c627c160"  # <--- PASTE YOUR REAL TOKEN HERE
MODELS_DIR = "saved_models"
DB_NAME = "aqi_data.db"
# =================================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- DATA MODELS ---
class SensorData(BaseModel):
    temperature: float
    humidity: float
    mq135_raw: int
    co2_ppm: float
    aqi: int


# --- DATABASE SETUP ---
def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), DB_NAME)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_sensor_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sensor_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperature REAL,
            humidity REAL,
            mq135_raw INTEGER,
            co2_ppm REAL,
            aqi INTEGER
        )
    ''')
    conn.commit()
    conn.close()


init_sensor_table()

# Global variable for local sensor fallback
# Initialize with some dummy values so it doesn't show 0/0/0 immediately if ESP32 is off
latest_local_sensor_data = {
    "temperature": 0, "humidity": 0, "mq135_raw": 0, "co2_ppm": 0, "aqi": 0
}


# --- HELPERS ---
def fetch_waqi_data(city_name):
    print(f"🌐 Connecting to WAQI API for {city_name}...")
    url = f"https://api.waqi.info/feed/{city_name}/?token={WAQI_TOKEN}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data['status'] != 'ok': return None

        result = data['data']
        iaqi = result.get('iaqi', {})

        # Helper to safely get value
        def get_val(key):
            return iaqi.get(key, {}).get('v', 0)

        # Mock temp/humidity if missing (common in WAQI)
        temp = get_val('t') if get_val('t') != 0 else random.randint(28, 34)
        hum = get_val('h') if get_val('h') != 0 else random.randint(60, 80)

        return {
            'PM2.5': get_val('pm25'),
            'PM10': get_val('pm10'),
            'NO2': get_val('no2'),
            'CO': get_val('co'),
            'SO2': get_val('so2'),
            'O3': get_val('o3'),
            'AQI': result.get('aqi', 0),
            'Temperature': temp,
            'Humidity': hum,
            'source': 'WAQI API'
        }
    except Exception as e:
        print(f"❌ Network Error: {e}")
        return None


def get_bucket(x):
    try:
        x = float(x)
        if x <= 50:
            return "Good"
        elif x <= 100:
            return "Satisfactory"
        elif x <= 200:
            return "Moderate"
        elif x <= 300:
            return "Poor"
        elif x <= 400:
            return "Very Poor"
        else:
            return "Severe"
    except:
        return "Unknown"


# --- ENDPOINTS ---

@app.get('/')
def home():
    return {"message": "EcoWatch API Active"}


@app.post("/api/sensor/data")
async def receive_sensor_data(data: SensorData):
    global latest_local_sensor_data
    latest_local_sensor_data = data.dict()
    # Logic to save to DB (optional if we are ignoring ESP32 data now)
    return {"status": "success"}


@app.get("/api/sensor/latest")
def get_latest_sensor_data():
    """
    HYBRID ENDPOINT:
    1. Returns Temp/Humidity/CO2 from Local ESP32 (latest_local_sensor_data).
    2. Overwrites AQI with Live Kolkata Data from API.
    """
    # 1. Fetch Live AQI from Kolkata API
    kolkata_data = fetch_waqi_data("Kolkata")
    live_aqi = kolkata_data['AQI'] if kolkata_data else 0

    # 2. Prepare the Hybrid Data Package
    # If ESP32 hasn't sent data yet (all 0s), maybe mock Temp/Hum too for demo?
    # For now, we respect your request: Temp/Hum/CO2 from ESP32, AQI from Kolkata.

    hybrid_data = {
        "temperature": latest_local_sensor_data['temperature'],
        "humidity": latest_local_sensor_data['humidity'],
        "mq135_raw": latest_local_sensor_data['mq135_raw'],
        "co2_ppm": latest_local_sensor_data['co2_ppm'],
        "aqi": live_aqi,  # <--- FORCED KOLKATA AQI
        "status": "online" if kolkata_data else "offline"
    }

    return hybrid_data


@app.get("/api/sensor/history")
def get_sensor_history():
    """Returns Kolkata history from DB to mimic local sensor history."""
    conn = get_db_connection()
    try:
        # Fallback: Get Kolkata history from city_daily
        query_fallback = "SELECT date as time, aqi FROM city_daily WHERE city='Kolkata' ORDER BY date DESC LIMIT 24"
        rows_fallback = conn.execute(query_fallback).fetchall()
        return [dict(r) for r in rows_fallback][::-1]
    finally:
        conn.close()


# ... (Keep remaining endpoints: /api/live/{city}, /api/heatmap, /api/stats, /api/trends, /api/predict, /api/analysis) ...
@app.get('/api/live/{city}')
def get_live_city_data(city: str):
    data = fetch_waqi_data(city)
    if not data:
        conn = get_db_connection()
        latest = conn.execute("SELECT * FROM city_daily WHERE city=? ORDER BY date DESC LIMIT 1", (city,)).fetchone()
        conn.close()
        if latest:
            return {'PM2.5': latest['pm2_5'], 'AQI': latest['aqi'], 'source': 'Local DB (Fallback)'}
        else:
            raise HTTPException(status_code=404, detail="City data not found")
    return data


@app.get('/api/heatmap')
def get_heatmap_data():
    conn = get_db_connection()
    try:
        query = '''
            SELECT m.city_name, m.latitude as lat, m.longitude as lng, 
                   (SELECT aqi FROM city_daily WHERE city=m.city_name ORDER BY date DESC LIMIT 1) as avg_aqi
            FROM city_meta m
        '''
        rows = conn.execute(query).fetchall()
        results = []
        for row in rows:
            d = dict(row)
            if d['avg_aqi'] is None: d['avg_aqi'] = 0
            results.append(d)
        return results
    except Exception:
        return []
    finally:
        conn.close()


@app.get('/api/stats')
def get_stats():
    conn = get_db_connection()
    try:
        query = 'SELECT city, aqi as avg_aqi FROM city_daily WHERE date = (SELECT MAX(date) FROM city_daily) ORDER BY aqi ASC'
        rows = conn.execute(query).fetchall()
        if not rows: return {"cleanest": [], "polluted": []}
        data = [dict(r) for r in rows]
        return {"cleanest": data[:5], "polluted": data[-5:][::-1]}
    finally:
        conn.close()


@app.get('/api/trends/{city}')
def get_city_trends(city: str):
    conn = get_db_connection()
    try:
        query = 'SELECT date as time, aqi FROM city_daily WHERE city = ? ORDER BY date DESC LIMIT 365'
        rows = conn.execute(query, (city,)).fetchall()
        return {"data": [dict(row) for row in rows][::-1]}
    finally:
        conn.close()


@app.get('/api/predict/{city}')
def get_city_prediction(city: str):
    live_data = fetch_waqi_data(city)
    if not live_data or live_data.get('AQI') == '-':
        conn = get_db_connection()
        latest = conn.execute("SELECT * FROM city_daily WHERE city=? ORDER BY date DESC LIMIT 1", (city,)).fetchone()
        conn.close()
        if latest:
            live_data = {'PM2.5': latest['pm2_5'], 'AQI': latest['aqi']}
        else:
            live_data = {'PM2.5': 0, 'AQI': 100}

    safe_city_name = city.replace(" ", "_")
    model_path = os.path.join(MODELS_DIR, f'aqi_model_{safe_city_name}.pkl')
    if not os.path.exists(model_path): model_path = os.path.join(MODELS_DIR, f'aqi_model_{safe_city_name.title()}.pkl')

    forecast = []
    today = datetime.now()

    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            current_aqi = live_data.get('AQI', 100)
            input_df = pd.DataFrame([{'AQI_Lag1': current_aqi, 'AQI_Lag2': current_aqi, 'Month': today.month}])
            if hasattr(model, 'feature_names_in_'):
                for col in model.feature_names_in_:
                    if col not in input_df.columns: input_df[col] = 0
                input_df = input_df[model.feature_names_in_]
            for i in range(5):
                pred = model.predict(input_df)[0]
                forecast.append({"date": (today + timedelta(days=i + 1)).strftime("%Y-%m-%d"), "aqi": int(pred),
                                 "status": get_bucket(pred)})
                input_df['AQI_Lag2'] = input_df['AQI_Lag1']
                input_df['AQI_Lag1'] = pred
            return {"forecast": forecast}
        except Exception:
            pass

    current_aqi = live_data.get('AQI', 100)
    if isinstance(current_aqi, str): current_aqi = 100
    for i in range(5):
        forecast.append({"date": (today + timedelta(days=i + 1)).strftime("%Y-%m-%d"), "aqi": int(current_aqi),
                         "status": get_bucket(current_aqi)})
    return {"forecast": forecast}


@app.get('/api/analysis/hourly/{city}')
def get_hourly_analysis(city: str):
    conn = get_db_connection()
    try:
        table_check = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='city_hourly'").fetchone()
        if not table_check: return {"hourly_curve": [], "best_time": {"hour": "00", "avg_aqi": 0},
                                    "worst_time": {"hour": "00", "avg_aqi": 0}}
        query = "SELECT strftime('%H', datetime) as hour, ROUND(AVG(aqi)) as avg_aqi FROM city_hourly WHERE city LIKE ? GROUP BY hour ORDER BY hour ASC"
        rows = conn.execute(query, (f"%{city}%",)).fetchall()
        if not rows: return {"hourly_curve": [{"hour": f"{i:02}", "avg_aqi": 100} for i in range(24)],
                             "best_time": {"hour": "06", "avg_aqi": 80}, "worst_time": {"hour": "18", "avg_aqi": 150}}
        data = [dict(row) for row in rows]
        return {"hourly_curve": data, "best_time": min(data, key=lambda x: x['avg_aqi']),
                "worst_time": max(data, key=lambda x: x['avg_aqi'])}
    finally:
        conn.close()


if __name__ == '__main__':
    print(f"🚀 EcoWatch AI API running on http://0.0.0.0:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)