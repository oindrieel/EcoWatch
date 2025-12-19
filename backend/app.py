from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import os
import random
from datetime import datetime, timedelta
import uvicorn

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "aqi_data.db"

# --- 1. HARDCODED DATA (Fallback if DB is missing) ---
CITY_COORDINATES = {
    "Ahmedabad": {"lat": 23.0225, "lng": 72.5714},
    "Aizawl": {"lat": 23.7307, "lng": 92.7173},
    "Amaravati": {"lat": 16.5131, "lng": 80.5165},
    "Amritsar": {"lat": 31.6340, "lng": 74.8723},
    "Bengaluru": {"lat": 12.9716, "lng": 77.5946},
    "Bhopal": {"lat": 23.2599, "lng": 77.4126},
    "Brajrajnagar": {"lat": 21.8217, "lng": 83.9221},
    "Chandigarh": {"lat": 30.7333, "lng": 76.7794},
    "Chennai": {"lat": 13.0827, "lng": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lng": 76.9558},
    "Delhi": {"lat": 28.7041, "lng": 77.1025},
    "Ernakulam": {"lat": 9.9816, "lng": 76.2999},
    "Gurugram": {"lat": 28.4595, "lng": 77.0266},
    "Guwahati": {"lat": 26.1445, "lng": 91.7364},
    "Hyderabad": {"lat": 17.3850, "lng": 78.4867},
    "Jaipur": {"lat": 26.9124, "lng": 75.7873},
    "Jorapokhar": {"lat": 23.7022, "lng": 86.4132},
    "Kochi": {"lat": 9.9312, "lng": 76.2673},
    "Kolkata": {"lat": 22.5726, "lng": 88.3639},
    "Lucknow": {"lat": 26.8467, "lng": 80.9462},
    "Mumbai": {"lat": 19.0760, "lng": 72.8777},
    "Patna": {"lat": 25.5941, "lng": 85.1376},
    "Shillong": {"lat": 25.5788, "lng": 91.8933},
    "Talcher": {"lat": 20.9509, "lng": 85.2163},
    "Thiruvananthapuram": {"lat": 8.5241, "lng": 76.9366},
    "Visakhapatnam": {"lat": 17.6868, "lng": 83.2185}
}


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Checks if DB exists, if not, creates tables and mock data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='city_meta'")
    if cursor.fetchone():
        conn.close()
        return  # DB already exists, skip init

    print("⚠️ Database not found or empty. Initializing with fallback data...")

    # 1. Create Tables
    cursor.execute('CREATE TABLE IF NOT EXISTS city_meta (city_name TEXT PRIMARY KEY, lat REAL, lng REAL)')
    cursor.execute('CREATE TABLE IF NOT EXISTS city_daily (id INTEGER PRIMARY KEY, city TEXT, date DATE, aqi INTEGER)')
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS city_hourly (id INTEGER PRIMARY KEY, city TEXT, datetime TIMESTAMP, aqi INTEGER)')

    # 2. Populate Meta
    for city, coords in CITY_COORDINATES.items():
        cursor.execute("INSERT INTO city_meta VALUES (?, ?, ?)", (city, coords['lat'], coords['lng']))

    # 3. Populate Mock Data (So the app works immediately)
    today = datetime.now()
    for city in CITY_COORDINATES:
        base_aqi = random.randint(50, 350)
        # Daily Data (Last 30 days)
        for i in range(30):
            d = today - timedelta(days=i)
            val = max(20, base_aqi + random.randint(-50, 50))
            cursor.execute("INSERT INTO city_daily (city, date, aqi) VALUES (?, ?, ?)",
                           (city, d.strftime('%Y-%m-%d'), val))

        # Hourly Data (Last 24 hours)
        for i in range(24):
            dt = today - timedelta(hours=i)
            # Make a curve: higher in morning/evening
            hour_mod = 50 if dt.hour in [8, 9, 10, 18, 19, 20] else 0
            val = max(20, base_aqi + random.randint(-20, 20) + hour_mod)
            cursor.execute("INSERT INTO city_hourly (city, datetime, aqi) VALUES (?, ?, ?)",
                           (city, dt.strftime('%Y-%m-%d %H:%M:%S'), val))

    conn.commit()
    conn.close()
    print("✅ Database initialized with fallback data.")


@app.get('/')
def home():
    return {"message": "🌑 EcoWatch API Active"}


# --- ENDPOINTS ---

@app.get('/api/heatmap')
def get_heatmap_data():
    conn = get_db_connection()
    try:
        query = '''
            SELECT m.city_name, m.lat, m.lng, ROUND(AVG(d.aqi)) as avg_aqi
            FROM city_meta m
            JOIN city_daily d ON m.city_name = d.city
            GROUP BY m.city_name
        '''
        rows = conn.execute(query).fetchall()
        return [dict(row) for row in rows]
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


@app.get('/api/stats')
def get_stats():
    conn = get_db_connection()
    try:
        query = 'SELECT city, ROUND(AVG(aqi)) as avg_aqi FROM city_daily GROUP BY city ORDER BY avg_aqi ASC'
        rows = conn.execute(query).fetchall()
        if not rows: return {"cleanest": [], "polluted": []}
        return {
            "cleanest": [dict(r) for r in rows[:5]],
            "polluted": [dict(r) for r in rows[-5:][::-1]]
        }
    except sqlite3.OperationalError:
        return {"cleanest": [], "polluted": []}
    finally:
        conn.close()


@app.get('/api/trends/{city}')
def get_city_trends(city: str):
    conn = get_db_connection()
    try:
        query = 'SELECT date as time, aqi FROM city_daily WHERE city = ? ORDER BY date ASC'
        rows = conn.execute(query, (city,)).fetchall()
        return {"data": [dict(row) for row in rows]}
    finally:
        conn.close()


@app.get('/api/analysis/hourly/{city}')
def get_hourly_analysis(city: str):
    conn = get_db_connection()
    try:
        # SQLite uses strftime('%H', datetime) to extract hour
        query = '''
            SELECT strftime('%H', datetime) as hour, ROUND(AVG(aqi)) as avg_aqi
            FROM city_hourly WHERE city = ? GROUP BY hour ORDER BY hour ASC
        '''
        rows = conn.execute(query, (city,)).fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No data found")

        data = [dict(row) for row in rows]
        best_hour = min(data, key=lambda x: x['avg_aqi'])
        worst_hour = max(data, key=lambda x: x['avg_aqi'])

        return {
            "hourly_curve": data,
            "best_time": best_hour,
            "worst_time": worst_hour
        }
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


if __name__ == '__main__':
    # Initialize DB before starting server
    init_db()
    print(f"🚀 EcoWatch Dark API running on http://127.0.0.1:8080")
    uvicorn.run(app, host="127.0.0.1", port=8080)