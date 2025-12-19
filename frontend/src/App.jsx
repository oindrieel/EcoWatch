import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Tooltip, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer } from 'recharts';
import { Wind, Map as MapIcon, Activity, Trophy, AlertTriangle, Clock, Sun, Moon, Info } from 'lucide-react';

// --- COMPONENT: NAV BAR ---
const NavBar = ({ activeTab, setActiveTab }) => (
  <nav className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-slate-900/90 backdrop-blur-xl border border-slate-700 rounded-full px-6 py-3 shadow-2xl z-[1000] flex gap-8">
    {[
      { id: 'dashboard', icon: Activity, label: 'Overview' },
      { id: 'map', icon: MapIcon, label: 'Live Map' },
      { id: 'planner', icon: Clock, label: 'Planner' },
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
    {/* Hero Section */}
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

    {/* Stats Grid */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Cleanest Cities */}
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

      {/* Most Polluted */}
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

// --- COMPONENT: PAGE 2 (MAP) ---
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
              radius={Math.max(6, city.avg_aqi / 15)}
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
        <h2 className="text-2xl font-bold text-white mb-2">
          {selectedCity ? selectedCity : "Select a City"}
        </h2>
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
                <RechartsTooltip
                  contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}}
                  itemStyle={{color: '#2dd4bf'}}
                />
                <Area type="monotone" dataKey="aqi" stroke="#2dd4bf" strokeWidth={2} fillOpacity={1} fill="url(#colorAqi)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex items-center justify-center text-slate-600 text-sm">
              Click a circle on the map
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- COMPONENT: PAGE 3 (PLANNER) ---
const PlannerPage = () => {
  const [city, setCity] = useState("Ahmedabad"); // Default
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    fetch(`http://localhost:8080/api/analysis/hourly/${city}`)
      .then(res => res.json())
      .then(data => setAnalysis(data))
      .catch(err => console.error(err));
  }, [city]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-in fade-in">
      <div className="space-y-6">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2">Smart Planner</h2>
          <p className="text-slate-400">AI-driven analysis of hourly pollution cycles.</p>
        </div>

        {analysis && !analysis.error && (
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-teal-900/20 border border-teal-800/50 p-6 rounded-2xl">
              <div className="flex items-center gap-2 text-teal-400 mb-2">
                <Sun size={20} />
                <span className="font-bold text-sm uppercase">Best Time</span>
              </div>
              <div className="text-3xl font-bold text-white">{analysis.best_time.hour}:00</div>
              <div className="text-teal-200/60 text-sm mt-1">{analysis.best_time.avg_aqi} AQI (Avg)</div>
            </div>

            <div className="bg-rose-900/20 border border-rose-800/50 p-6 rounded-2xl">
              <div className="flex items-center gap-2 text-rose-400 mb-2">
                <AlertTriangle size={20} />
                <span className="font-bold text-sm uppercase">Worst Time</span>
              </div>
              <div className="text-3xl font-bold text-white">{analysis.worst_time.hour}:00</div>
              <div className="text-rose-200/60 text-sm mt-1">{analysis.worst_time.avg_aqi} AQI (Avg)</div>
            </div>
          </div>
        )}

        <div className="bg-slate-900/50 p-6 rounded-2xl border border-slate-800">
          <h3 className="text-white font-bold mb-4">Recommendation</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Based on historical data for <span className="text-teal-400 font-bold">{city}</span>, air quality is typically best in the early afternoon.
            Avoid outdoor exercise during peak traffic hours shown in red below.
          </p>
        </div>
      </div>

      {/* Chart Column */}
      <div className="bg-slate-900 rounded-3xl border border-slate-800 p-6">
        <h3 className="text-slate-400 text-sm font-bold uppercase mb-6 tracking-wider">24-Hour Pollution Cycle</h3>
        <div className="h-[300px]">
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
                <Tooltip
                  contentStyle={{backgroundColor: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px'}}
                  labelStyle={{color: '#94a3b8'}}
                />
                <Area type="monotone" dataKey="avg_aqi" stroke="#818cf8" strokeWidth={3} fill="url(#plannerGradient)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-600">Loading Analysis...</div>
          )}
        </div>
      </div>
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
    Promise.all([
      fetch('http://localhost:8080/api/heatmap'),
      fetch('http://localhost:8080/api/stats')
    ]).then(async ([mapRes, statsRes]) => {
      const mapJson = await mapRes.json();
      setMapData(mapJson);
      setStats(await statsRes.json());
      if (mapJson.length > 0) handleCityClick(mapJson[0].city_name);
    }).catch(err => console.error("API Error:", err));
  }, []);

  const handleCityClick = async (cityName) => {
    setSelectedCity(cityName);
    const res = await fetch(`http://localhost:8080/api/trends/${cityName}`);
    const json = await res.json();
    setTrendData(json.data);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-200 font-sans selection:bg-teal-500/30">
      <div className="max-w-7xl mx-auto px-4 md:px-8 py-8 pb-32">

        {/* TAB CONTENT SWITCHER */}
        {activeTab === 'dashboard' && <DashboardPage stats={stats} />}
        {activeTab === 'map' && <MapPage mapData={mapData} selectedCity={selectedCity} handleCityClick={handleCityClick} trendData={trendData} />}
        {activeTab === 'planner' && <PlannerPage />}

      </div>

      <NavBar activeTab={activeTab} setActiveTab={setActiveTab} />
    </div>
  );
}