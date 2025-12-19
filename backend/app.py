from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import requests
import pandas as pd
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import uvicorn

# ================= CONFIGURATION =================
WAQI_TOKEN = ""  # <--- PASTE YOUR TOKEN HERE
MODELS_DIR = "saved_models"
DB_NAME = "aqi_data.db"
# =================================================

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- HELPER: Database ---
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


# --- HELPER: WAQI Fetcher ---
def fetch_waqi_data(city_name):
    print(f"🌐 Connecting to WAQI API for {city_name}...")
    url = f"https://api.waqi.info/feed/{city_name}/?token={WAQI_TOKEN}"
    try:
        response = requests.get(url, timeout=5)  # Add timeout
        data = response.json()
        if data['status'] != 'ok':
            print(f"❌ WAQI Error for {city_name}: {data.get('data', 'Unknown error')}")
            return None

        result = data['data']
        iaqi = result.get('iaqi', {})

        # Extract features (use 0 as default to prevent crashes)
        return {
            'PM2.5': iaqi.get('pm25', {}).get('v', 0),
            'PM10': iaqi.get('pm10', {}).get('v', 0),
            'NO2': iaqi.get('no2', {}).get('v', 0),
            'CO': iaqi.get('co', {}).get('v', 0),
            'SO2': iaqi.get('so2', {}).get('v', 0),
            'O3': iaqi.get('o3', {}).get('v', 0),
            'AQI': result.get('aqi', 0)
        }
    except Exception as e:
        print(f"❌ Network Error fetching WAQI: {e}")
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


# --- API ENDPOINTS ---

@app.get('/')
def home():
    return {"message": "🌑 EcoWatch AI API Active"}


@app.get('/api/heatmap')
def get_heatmap_data():
    conn = get_db_connection()
    try:
        # FIXED: Use correct column names (latitude, longitude)
        query = '''
            SELECT m.city_name, m.latitude as lat, m.longitude as lng, 
                   (SELECT aqi FROM city_daily WHERE city=m.city_name ORDER BY date DESC LIMIT 1) as avg_aqi
            FROM city_meta m
        '''
        rows = conn.execute(query).fetchall()

        results = []
        for row in rows:
            d = dict(row)
            # Fallback if no daily data exists yet
            if d['avg_aqi'] is None: d['avg_aqi'] = 0
            results.append(d)

        return results
    except sqlite3.OperationalError as e:
        print(f"❌ DB Error in heatmap: {e}")
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
        return {
            "cleanest": data[:5],
            "polluted": data[-5:][::-1]
        }
    except Exception as e:
        print(f"❌ Stats Error: {e}")
        return {"cleanest": [], "polluted": []}
    finally:
        conn.close()


@app.get('/api/trends/{city}')
def get_city_trends(city: str):
    conn = get_db_connection()
    try:
        query = '''
            SELECT date as time, aqi 
            FROM city_daily 
            WHERE city = ? 
            ORDER BY date DESC 
            LIMIT 365
        '''
        rows = conn.execute(query, (city,)).fetchall()
        return {"data": [dict(row) for row in rows][::-1]}
    except Exception as e:
        print(f"❌ Trend Error for {city}: {e}")
        return {"data": []}
    finally:
        conn.close()


@app.get('/api/predict/{city}')
def get_city_prediction(city: str):
    print(f"🔮 Prediction requested for: {city}")

    # 1. LIVE DATA FETCH
    live_data = fetch_waqi_data(city)

    # Fallback to DB if live data fails
    if not live_data or live_data['AQI'] == '-':
        print(f"⚠️ Live data unavailable for {city}, fetching latest from DB.")
        conn = get_db_connection()
        latest = conn.execute("SELECT * FROM city_daily WHERE city=? ORDER BY date DESC LIMIT 1", (city,)).fetchone()
        conn.close()

        if latest:
            live_data = {
                'PM2.5': latest['pm2_5'], 'PM10': latest['pm10'], 'NO2': latest['no2'],
                'CO': latest['co'], 'SO2': latest['so2'], 'O3': latest['o3'],
                'AQI': latest['aqi']
            }
        else:
            live_data = {'PM2.5': 0, 'PM10': 0, 'NO2': 0, 'CO': 0, 'SO2': 0, 'O3': 0, 'AQI': 100}

    # 2. MODEL LOADING
    safe_city_name = city.replace(" ", "_")
    model_path = os.path.join(MODELS_DIR, f'aqi_model_{safe_city_name}.pkl')
    if not os.path.exists(model_path):
        model_path = os.path.join(MODELS_DIR, f'aqi_model_{safe_city_name.title()}.pkl')

    # 3. PREDICTION LOGIC
    forecast = []
    today = datetime.now()

    if os.path.exists(model_path):
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)

            # Construct Input (Assume current is lag1 for next prediction)
            input_dict = {
                'PM2.5_Lag1': live_data.get('PM2.5', 0),
                'PM10_Lag1': live_data.get('PM10', 0),
                'NO2_Lag1': live_data.get('NO2', 0),
                'CO_Lag1': live_data.get('CO', 0),
                'SO2_Lag1': live_data.get('SO2', 0),
                'O3_Lag1': live_data.get('O3', 0),
                'AQI_Lag1': live_data['AQI'],
                'AQI_Lag2': live_data['AQI'],
                'AQI_Roll_Mean_7': live_data['AQI'],
                'Month': (today + timedelta(days=1)).month
            }

            curr_aqi = live_data['AQI']
            for i in range(5):
                next_date = today + timedelta(days=i + 1)
                input_dict['Month'] = next_date.month

                input_df = pd.DataFrame([input_dict])

                # Robust Feature Matching
                if hasattr(model, 'feature_names_in_'):
                    for col in model.feature_names_in_:
                        if col not in input_df.columns: input_df[col] = 0
                    input_df = input_df[model.feature_names_in_]

                prediction = model.predict(input_df)[0]

                forecast.append({
                    "date": next_date.strftime("%Y-%m-%d"),
                    "aqi": int(prediction),
                    "status": get_bucket(prediction)
                })

                # Update State
                input_dict['AQI_Lag2'] = input_dict['AQI_Lag1']
                input_dict['AQI_Lag1'] = prediction

            return {"forecast": forecast, "source": "AI Model"}

        except Exception as e:
            print(f"❌ Model Crash for {city}: {e}")
            # Fall through to fallback

    # 4. FALLBACK (Persistence)
    print(f"ℹ️ Using fallback forecast for {city}")
    current_aqi = live_data.get('AQI', 100)
    if isinstance(current_aqi, str) or current_aqi is None: current_aqi = 100

    for i in range(5):
        next_date = today + timedelta(days=i + 1)
        forecast.append({
            "date": next_date.strftime("%Y-%m-%d"),
            "aqi": int(current_aqi),
            "status": get_bucket(current_aqi)
        })

    return {"forecast": forecast, "source": "Fallback"}


@app.get('/api/analysis/hourly/{city}')
def get_hourly_analysis(city: str):
    conn = get_db_connection()
    try:
        query = '''
            SELECT strftime('%H', datetime) as hour, ROUND(AVG(aqi)) as avg_aqi
            FROM city_hourly 
            WHERE city LIKE ? 
            GROUP BY hour 
            ORDER BY hour ASC
        '''
        rows = conn.execute(query, (f"%{city}%",)).fetchall()

        if not rows:
            return {
                "hourly_curve": [{"hour": f"{i:02}", "avg_aqi": 100} for i in range(24)],
                "best_time": {"hour": "06", "avg_aqi": 80},
                "worst_time": {"hour": "18", "avg_aqi": 150}
            }

        data = [dict(row) for row in rows]
        best_hour = min(data, key=lambda x: x['avg_aqi'])
        worst_hour = max(data, key=lambda x: x['avg_aqi'])

        return {
            "hourly_curve": data,
            "best_time": best_hour,
            "worst_time": worst_hour
        }
    except Exception as e:
        print(f"❌ Hourly Analysis Error: {e}")
        return {"error": "Analysis failed"}
    finally:
        conn.close()


if __name__ == '__main__':
    print(f"🚀 EcoWatch AI API running on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)