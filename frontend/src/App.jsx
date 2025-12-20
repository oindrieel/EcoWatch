import React, { useState, useEffect } from 'react';
// ✅ REAL IMPORTS (Active)
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';

import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Wind, Map as MapIcon, Activity, Trophy, AlertTriangle, Clock, Sun, Moon, Info, Calendar, Thermometer, Droplets, Signal, Globe } from 'lucide-react';

// --- COMPONENT: NAV BAR ---
const NavBar = ({ activeTab, setActiveTab }) => (
  <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-xl border border-slate-700 rounded-full px-6 py-3 shadow-2xl z-[1000] flex gap-8">
    {[
      { id: 'dashboard', icon: Activity, label: 'Overview' },
      { id: 'live', icon: Signal, label: 'Live Sensor' },
      { id: 'map', icon: MapIcon, label: 'Live Map' },
      { id: 'forecast', icon: Calendar, label: 'Forecast' },
    ].map((item) => (
      <button
        key={item.id}
        onClick={() => setActiveTab(item.id)}
        className={`flex flex-col items-center gap-1 transition-all ${
          activeTab === item.id 
            ? 'text-teal-400 scale-110' 
            : 'text-slate-500 hover:text-slate-300'
        }`}
      >
        <item.icon size={20} />
        <span className="text-[10px] font-bold uppercase tracking-wider">{item.label}</span>
      </button>
    ))}
  </nav>
);

// --- COMPONENT: PAGE 1 (DASHBOARD) ---
const DashboardPage = ({ stats }) => (
  <div className="space-y-8 animate-in fade-in duration-500">
    <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border border-slate-700 p-8 md:p-12 text-center">
      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-teal-500 via-purple-500 to-orange-500"></div>
      <Wind className="mx-auto text-teal-400 mb-6" size={48} />
      <h1 className="text-4xl md:text-5xl font-bold text-white mb-4 tracking-tight">
        EcoWatch <span className="text-teal-400">India</span>
      </h1>
      <p className="text-slate-400 max-w-2xl mx-auto text-lg">
        Advanced environmental monitoring system. Providing real-time air quality analytics and predictive health insights for 26 major cities.
      </p>
    </div>

    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <Trophy className="text-teal-400" />
          <h3 className="text-xl font-bold text-white">Cleanest Cities</h3>
        </div>
        <div className="space-y-4">
          {stats.cleanest.map((c, i) => (
            <div key={c.city} className="flex items-center justify-between group">
              <div className="flex items-center gap-4">
                <span className="text-slate-600 font-mono">0{i+1}</span>
                <span className="text-slate-300 font-medium group-hover:text-teal-400 transition-colors">{c.city}</span>
              </div>
              <span className="text-teal-400 font-mono font-bold">{c.avg_aqi} AQI</span>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
        <div className="flex items-center gap-3 mb-6">
          <AlertTriangle className="text-rose-500" />
          <h3 className="text-xl font-bold text-white">Critical Zones</h3>
        </div>
        <div className="space-y-4">
          {stats.polluted.map((c, i) => (
            <div key={c.city} className="flex items-center justify-between group">
              <div className="flex items-center gap-4">
                <span className="text-slate-600 font-mono">0{i+1}</span>
                <span className="text-slate-300 font-medium group-hover:text-rose-400 transition-colors">{c.city}</span>
              </div>
              <span className="text-rose-500 font-mono font-bold">{c.avg_aqi} AQI</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  </div>
);

// --- COMPONENT: PAGE 2 (LIVE SENSOR) ---
const LiveSensorPage = () => {
  // Initialize with safe defaults so it never crashes on null
  const [sensorData, setSensorData] = useState({
    temperature: 0,
    humidity: 0,
    mq135_raw: 0,
    co2_ppm: 0,
    aqi: 0,
    status: 'loading'
  });
  const [history, setHistory] = useState([]);
  const city = "Kolkata";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const liveRes = await fetch('http://localhost:8080/api/sensor/latest');
        if (liveRes.ok) {
            const liveJson = await liveRes.json();
            setSensorData(liveJson);
        }

        const histRes = await fetch('http://localhost:8080/api/sensor/history');
        if(histRes.ok) {
            const histJson = await histRes.json();
            setHistory(histJson);
        }
      } catch (err) {
        console.error("Sensor Error:", err);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-8 animate-in fade-in">
      <div className="flex justify-between items-end border-b border-slate-800 pb-6">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Live Local Sensor</h2>
          <p className="text-slate-400">
            Hybrid Mode: Local Telemetry + API Air Quality ({city}).
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-teal-900/30 border border-teal-800 rounded-full text-teal-400 text-xs font-mono animate-pulse">
          <span className="w-2 h-2 rounded-full bg-teal-400"></span>
          STREAM ACTIVE
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* ESP32 Data */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center hover:border-orange-500/50 transition-colors group">
            <Thermometer className="mx-auto text-slate-600 group-hover:text-orange-400 transition-colors mb-3" size={28} />
            <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Temperature</p>
            <p className="text-3xl font-bold text-white font-mono">{sensorData.temperature}°C</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center hover:border-blue-500/50 transition-colors group">
            <Droplets className="mx-auto text-slate-600 group-hover:text-blue-400 transition-colors mb-3" size={28} />
            <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Humidity</p>
            <p className="text-3xl font-bold text-white font-mono">{sensorData.humidity}%</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center hover:border-slate-500/50 transition-colors group">
            <Wind className="mx-auto text-slate-600 group-hover:text-slate-300 transition-colors mb-3" size={28} />
            <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">CO2 Level</p>
            <p className="text-3xl font-bold text-white font-mono">{sensorData.co2_ppm ? sensorData.co2_ppm.toFixed(0) : "0"} <span className="text-xs text-slate-500">PPM</span></p>
        </div>

        {/* API Data (Kolkata) */}
        <div className="bg-slate-900 border border-slate-800 p-6 rounded-2xl text-center relative overflow-hidden group">
            <div className={`absolute inset-0 opacity-0 group-hover:opacity-10 transition-opacity ${sensorData.aqi > 100 ? 'bg-rose-500' : 'bg-teal-500'}`}></div>
            <Activity className={`mx-auto mb-3 ${sensorData.aqi > 100 ? 'text-rose-400' : 'text-teal-400'}`} size={28} />
            <p className="text-slate-500 text-xs uppercase tracking-wider mb-1">Local AQI</p>
            <p className={`text-3xl font-bold font-mono ${sensorData.aqi > 100 ? 'text-rose-400' : 'text-teal-400'}`}>{sensorData.aqi}</p>
        </div>
      </div>

      {/* Historical Chart */}
      <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6">
        <h3 className="text-white font-bold mb-6 flex items-center gap-2">
          <Clock size={18} className="text-teal-400" />
          AQI History
        </h3>
        <div className="h-[300px] w-full">
          {history && history.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient id="sensorAqi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="time" tick={{fontSize: 10, fill: '#64748b'}} tickFormatter={(v) => v.slice(5,10)} axisLine={false} tickLine={false} />
                <YAxis tick={{fontSize: 10, fill: '#64748b'}} axisLine={false} tickLine={false} />
                <RechartsTooltip contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}} itemStyle={{color: '#2dd4bf'}} />
                <Area type="monotone" dataKey="aqi" stroke="#2dd4bf" strokeWidth={2} fillOpacity={1} fill="url(#sensorAqi)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-600">Loading historical data...</div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- COMPONENT: PAGE 3 (MAP) ---
const MapPage = ({ mapData, selectedCity, handleCityClick, trendData }) => {
  const getAqiColor = (aqi) => {
    if (aqi <= 50) return '#2dd4bf'; // teal
    if (aqi <= 100) return '#4ade80'; // green
    if (aqi <= 200) return '#facc15'; // yellow
    if (aqi <= 300) return '#fb923c'; // orange
    if (aqi <= 400) return '#f87171'; // red
    return '#c084fc'; // purple
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[80vh]">
      {/* Map Column */}
      <div className="lg:col-span-2 bg-slate-900 rounded-3xl border border-slate-800 overflow-hidden relative">
        <MapContainer
          center={[22.5937, 78.9629]}
          zoom={5}
          style={{ height: '100%', width: '100%', background: '#0f172a' }}
          zoomControl={false}
        >
          {/* Dark Matter Tiles for Cyberpunk look */}
          <TileLayer
            attribution='&copy; CARTO'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          />
          {mapData.map((city) => (
            <CircleMarker
              key={city.city_name}
              center={[city.lat, city.lng]}
              radius={Math.min(Math.max(3, Math.log(city.avg_aqi || 10) * 3), 15)}
              pathOptions={{
                color: getAqiColor(city.avg_aqi),
                fillColor: getAqiColor(city.avg_aqi),
                fillOpacity: 0.6,
                weight: 0,
              }}
              eventHandlers={{ click: () => handleCityClick(city.city_name) }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={1} className="custom-tooltip">
                <div className="text-center font-sans bg-slate-800 text-white p-2 rounded border border-slate-700">
                    <span className="font-bold block text-sm">{city.city_name}</span>
                    <span className="text-xs text-slate-400">AQI: {city.avg_aqi}</span>
                </div>
              </Tooltip>
            </CircleMarker>
          ))}
        </MapContainer>
        <div className="absolute top-4 left-4 bg-slate-900/90 backdrop-blur px-4 py-2 rounded-lg border border-slate-700 text-xs text-slate-400 z-[500]">
          Interactive Monitor
        </div>
      </div>

      {/* Detail Column */}
      <div className="bg-slate-900/50 rounded-3xl border border-slate-800 p-6 flex flex-col">
        <h2 className="text-2xl font-bold text-white mb-2">{selectedCity ? selectedCity : "Select a City"}</h2>
        <p className="text-slate-500 text-sm mb-6">Historical Analysis</p>
        <div className="flex-1 min-h-[300px]">
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="colorAqi" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2dd4bf" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                <XAxis dataKey="time" tick={{fontSize: 10, fill: '#475569'}} tickFormatter={(v)=>v.slice(0,4)} axisLine={false} tickLine={false} />
                <YAxis tick={{fontSize: 10, fill: '#475569'}} axisLine={false} tickLine={false} />
                <RechartsTooltip contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}} itemStyle={{color: '#2dd4bf'}} />
                <Area type="monotone" dataKey="aqi" stroke="#2dd4bf" strokeWidth={2} fillOpacity={1} fill="url(#colorAqi)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-600 text-sm">Click a circle on the map</div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- COMPONENT: PAGE 4 (FORECAST) ---
const ForecastPage = () => {
  const [city, setCity] = useState("Delhi");
  const [forecast, setForecast] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      fetch(`http://localhost:8080/api/predict/${city}`).then(res => res.json()),
      fetch(`http://localhost:8080/api/analysis/hourly/${city}`).then(res => res.json())
    ]).then(([forecastData, analysisData]) => {
      setForecast(forecastData.forecast || []);
      setAnalysis(analysisData);
      setLoading(false);
    }).catch(err => {
      console.error(err);
      setLoading(false);
    });
  }, [city]);

  const cities = ["Ahmedabad", "Delhi", "Mumbai", "Kolkata", "Bengaluru", "Chennai", "Hyderabad", "Lucknow"];

  return (
    <div className="space-y-8 animate-in fade-in">
      <div className="flex flex-col md:flex-row justify-between items-end gap-4">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">AI Analysis & Forecasting</h2>
          <p className="text-slate-400">Integrated predictive modeling and hourly cycle analysis.</p>
        </div>
        <select
          className="bg-slate-800 text-white border border-slate-700 rounded-lg px-4 py-2 outline-none focus:border-teal-500"
          value={city}
          onChange={(e) => setCity(e.target.value)}
        >
          {cities.map(c => <option key={c} value={c}>{c}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-teal-400 animate-pulse">Analyzing Data...</div>
      ) : (
        <>
          {/* Section 1: 5-Day Forecast with Chart */}
          <div className="grid grid-cols-1 gap-6">
            <div className="grid grid-cols-1 lg:grid-cols-5 gap-4">
              {forecast.map((day, i) => (
                <div key={day.date} className={`relative overflow-hidden rounded-2xl border p-4 ${i === 0 ? 'bg-gradient-to-b from-teal-900/20 to-slate-900 border-teal-500/30' : 'bg-slate-900/50 border-slate-800'}`}>
                  {i === 0 && <span className="absolute top-2 right-2 text-[10px] bg-teal-500/20 text-teal-300 px-2 rounded-full border border-teal-500/30">Tommorow</span>}
                  <p className="text-slate-400 text-xs uppercase tracking-wider font-bold mb-1">{day.date}</p>
                  <div className="flex items-baseline gap-2">
                    <span className="text-2xl font-bold text-white">{day.aqi}</span>
                    <span className="text-xs text-slate-500">AQI</span>
                  </div>
                  <p className={`text-xs mt-2 font-medium ${day.aqi > 200 ? 'text-rose-400' : 'text-teal-400'}`}>{day.status}</p>
                </div>
              ))}
            </div>

            {/* Forecast Trend Chart (NEW) */}
            <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6">
              <h3 className="text-slate-400 text-sm font-bold uppercase mb-6 tracking-wider">5-Day Prediction Trend</h3>
              <div className="h-[300px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={forecast}>
                    <defs>
                      <linearGradient id="forecastGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#14b8a6" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#14b8a6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                    <XAxis dataKey="date" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                    <Tooltip contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}} labelStyle={{color: '#94a3b8'}} />
                    <Area type="monotone" dataKey="aqi" stroke="#14b8a6" strokeWidth={3} fill="url(#forecastGradient)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Section 2: Hourly Planner */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="space-y-4">
              {analysis && !analysis.error && (
                <>
                  <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex items-center justify-between">
                    <div>
                      <p className="text-xs text-teal-400 font-bold uppercase mb-1">Best Time</p>
                      <p className="text-2xl font-bold text-white">{analysis.best_time.hour}:00</p>
                    </div>
                    <Sun className="text-teal-400" />
                  </div>
                  <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl flex items-center justify-between">
                    <div>
                      <p className="text-xs text-rose-400 font-bold uppercase mb-1">Worst Time</p>
                      <p className="text-2xl font-bold text-white">{analysis.worst_time.hour}:00</p>
                    </div>
                    <AlertTriangle className="text-rose-400" />
                  </div>
                </>
              )}
              <div className="bg-slate-900/50 border border-slate-800 p-5 rounded-2xl">
                <p className="text-slate-400 text-sm italic">
                  "Based on historical patterns for {city}, aim for outdoor activities during the 'Best Time' window."
                </p>
              </div>
            </div>

            <div className="lg:col-span-2 bg-slate-900 rounded-3xl border border-slate-800 p-6">
              <h3 className="text-slate-400 text-sm font-bold uppercase mb-6 tracking-wider">Typical 24-Hour Cycle</h3>
              <div className="h-[250px]">
                {analysis && analysis.hourly_curve ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={analysis.hourly_curve}>
                      <defs>
                        <linearGradient id="plannerGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#818cf8" stopOpacity={0.3}/>
                          <stop offset="95%" stopColor="#818cf8" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b" />
                      <XAxis dataKey="hour" tick={{fill: '#64748b', fontSize: 12}} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}} labelStyle={{color: '#94a3b8'}} />
                      <Area type="monotone" dataKey="avg_aqi" stroke="#818cf8" strokeWidth={3} fill="url(#plannerGradient)" />
                    </AreaChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-slate-600">Loading Analysis...</div>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

// --- MAIN APP ---
export default function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [mapData, setMapData] = useState([]);
  const [stats, setStats] = useState({ cleanest: [], polluted: [] });
  const [selectedCity, setSelectedCity] = useState(null);
  const [trendData, setTrendData] = useState([]);

  useEffect(() => {
    // Initial Data Fetch
    // Updated port to 8080
    Promise.all([
      fetch('http://localhost:8080/api/heatmap'),
      fetch('http://localhost:8080/api/stats')
    ]).then(async ([mapRes, statsRes]) => {
      if (mapRes.ok && statsRes.ok) {
        const mapJson = await mapRes.json();
        setMapData(mapJson);
        setStats(await statsRes.json());
        if (mapJson.length > 0) handleCityClick(mapJson[0].city_name);
      } else {
        console.error("Failed to fetch initial data");
      }
    }).catch(err => console.error("API Error:", err));
  }, []);

  const handleCityClick = async (cityName) => {
    setSelectedCity(cityName);
    try {
      const res = await fetch(`http://localhost:8080/api/trends/${cityName}`);
      if (res.ok) {
        const json = await res.json();
        setTrendData(json.data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-teal-500/30">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 pb-32">
        {activeTab === 'dashboard' && <DashboardPage stats={stats} />}
        {activeTab === 'live' && <LiveSensorPage />}
        {activeTab === 'map' && <MapPage mapData={mapData} selectedCity={selectedCity} handleCityClick={handleCityClick} trendData={trendData} />}
        {activeTab === 'forecast' && <ForecastPage />}
      </div>
      <NavBar activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}