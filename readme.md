# EcoWatch India

EcoWatch India is an advanced environmental monitoring system designed to bridge the gap between hyper-local IoT telemetry and national air quality trends. Built by Team Infinite Builders, it provides real-time tracking, interactive visualization, and AI-driven forecasting to help users make healthier lifestyle decisions.

## 🚀 Key Features

### 📡 Hybrid Live Sensor Network

- **Hardware Integration**: Real-time data from ESP32 microcontrollers equipped with MQ135 (Air Quality) and DHT11 (Temperature/Humidity) sensors
- **Seamless Fallback**: Intelligent backend that switches to professional API data (WAQI) if the local sensor goes offline
- **Telemetry**: 24-hour historical graphs for local sensor data

### 🗺️ Interactive National Heatmap

- **Coverage**: Real-time AQI tracking for 26 major Indian cities
- **Visualization**: Glowing, color-coded heat circles (React-Leaflet) providing instant health indicators
- **Deep Dive**: Historical area charts for every city to visualize long-term pollution trends

### 🔮 AI Analysis & Smart Planner

- **5-Day Forecasting**: Machine learning models predict AQI levels for the upcoming week
- **The "Golden Hour"**: Sophisticated hourly analysis that identifies the best time and worst time to be outdoors based on historical 24-hour cycles

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS (Cyberpunk/Dark UI)
- Recharts (Interactive Analytics)
- Leaflet.js (Mapping)
- Lucide React (Iconography)

### Backend
- FastAPI (Python)
- Uvicorn (ASGI Server)
- SQLite (Relational Database)
- Scikit-Learn (Predictive Modeling)
- Pandas/NumPy (Data Processing)

### Hardware
- ESP32 (Microcontroller)
- MQ135 (Gas/Smoke Sensor)
- DHT11 (Temperature/Humidity)

## 📥 Installation & Setup

### Prerequisites

- Conda or Python 3.9+
- Node.js & npm
- WAQI API Token (for real-time data features)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate environment
conda env create -f environment.yml
conda activate ecowatch-env

# Set environment variable for WAQI token
export WAQI_TOKEN="your_token_here"  # Linux/macOS
set WAQI_TOKEN=your_token_here       # Windows

# Initialize the database (if not already present)
python build_db.py

# Run the API
python app.py
```

The backend will start on `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will start on `http://localhost:5173`

### 3. Hardware Setup (Optional)

1. Open `main.ino` in Arduino IDE
2. Update the following variables:
   - `ssid` - Your WiFi network name
   - `password` - Your WiFi password
   - `serverUrl` - Your computer's local IP address (e.g., `http://192.168.1.100:8000`)
3. Flash the code to your ESP32
4. Connect MQ135 and DHT11 sensors according to the pin configuration in the code

## 📂 Project Structure

```
.
├── backend/               # Main Backend directory
│   ├── app.py            # Backend API logic (FastAPI)
│   ├── environment.yml   # Conda environment config
│   ├── aqi_data.db       # SQLite Database
│   ├── saved_models/     # Trained AI .pkl files
│   └── build_db.py       # Data cleaning and DB ingestion logic
├── frontend/             # React application (Vite)
│   ├── src/             # Source files
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
└── hardware/            # ESP32 Arduino code
    └── main.ino         # Microcontroller firmware
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
WAQI_TOKEN=your_waqi_api_token_here
```

Get your WAQI token 

## 📊 API Endpoints

- `GET /api/sensor/latest` - Latest local sensor readings
- `GET /api/cities` - AQI data for all monitored cities
- `GET /api/forecast/{city}` - 5-day AQI forecast
- `GET /api/golden-hour/{city}` - Best/worst outdoor times
- `POST /api/sensor/data` - Endpoint for ESP32 data upload

## 🏆 Team Infinite Builders

**Focus**: Advanced Environmental Monitoring & AI Integration

**Vision**: Making air quality data accessible, understandable, and actionable for every Indian citizen

**Note**: Real-time API features require a valid WAQI_TOKEN set in your environment variables.