import React, { useEffect, useState } from 'react'
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import { getRiskList, getLocations, getAlerts } from '../api/client.js'

const LEVEL_COLORS = {
  'LOW': '#2e7d32', 'MEDIUM': '#f9a825',
  'HIGH': '#ef6c00', 'CRITICAL': '#c62828',
  'DATA UNAVAILABLE': '#9e9e9e'
}

export default function Dashboard() {
  const [locations, setLocations] = useState([])
  const [risks, setRisks] = useState([])
  const [alerts, setAlerts] = useState([])
  const [filterLevel, setFilterLevel] = useState('ALL')

  const fetchData = () => {
    getLocations().then(setLocations).catch(() => {})
    getRiskList().then(setRisks).catch(() => {})
    getAlerts().then(setAlerts).catch(() => {})
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 10000)
    return () => clearInterval(interval)
  }, [])

  const riskByLocation = {}
  for (const r of risks) {
    if (!riskByLocation[r.location_id]) {
      riskByLocation[r.location_id] = r
    }
  }

  const filteredLocations = locations.filter(loc => {
    if (filterLevel === 'ALL') return true;
    const risk = riskByLocation[loc.id];
    return risk && risk.level === filterLevel;
  })
  
  const staleCount = Object.values(riskByLocation).filter(r => r.level === 'DATA UNAVAILABLE').length;
  const criticalCount = Object.values(riskByLocation).filter(r => r.level === 'CRITICAL').length;
  const highCount = Object.values(riskByLocation).filter(r => r.level === 'HIGH').length;

  return (
    <div className="container">
      <h2>Environmental Admin Dashboard</h2>
      
      <div className="stats" style={{display: 'flex', gap: '20px', marginBottom: '20px'}}>
        <div className="stat-box" style={{background: '#f5f5f5', padding: '10px', borderRadius: '5px'}}>
           <strong>Locations:</strong> {locations.length}
        </div>
        <div className="stat-box" style={{background: '#ffebee', padding: '10px', borderRadius: '5px', color: '#c62828'}}>
           <strong>High/Critical:</strong> {highCount + criticalCount}
        </div>
        <div className="stat-box" style={{background: '#fff3e0', padding: '10px', borderRadius: '5px', color: '#ef6c00'}}>
           <strong>Active Warnings:</strong> {alerts.filter(a => a.delivery_status === 'sent').length}
        </div>
        <div className="stat-box" style={{background: '#eeeeee', padding: '10px', borderRadius: '5px', color: '#616161'}}>
           <strong>Stale/Missing Data:</strong> {staleCount}
        </div>
      </div>

      <div style={{marginBottom: '10px'}}>
        <label>Filter by Risk: </label>
        <select value={filterLevel} onChange={e => setFilterLevel(e.target.value)}>
          <option value="ALL">All</option>
          <option value="LOW">Low</option>
          <option value="MEDIUM">Medium</option>
          <option value="HIGH">High</option>
          <option value="CRITICAL">Critical</option>
          <option value="DATA UNAVAILABLE">Data Unavailable</option>
        </select>
      </div>

      <div className="map-wrap" style={{height: '400px'}}>
        <MapContainer center={[26.2, 92.9]} zoom={7} style={{ height: '100%', width: '100%' }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {filteredLocations.map(loc => {
            const risk = riskByLocation[loc.id]
            const color = risk ? LEVEL_COLORS[risk.level] || '#888' : '#888'
            return (
              <CircleMarker key={loc.id} center={[loc.lat, loc.lon]} radius={8} pathOptions={{ color, fillColor: color, fillOpacity: 0.8 }}>
                <Popup>
                  <strong>{loc.village || loc.district || 'Location'}</strong><br />
                  {risk ? (
                    <>
                      <div>Risk: <b>{risk.level}</b></div>
                      {risk.probability != null && <div>Confidence: {(risk.probability*100).toFixed(1)}%</div>}
                      <div>Updated: {new Date(risk.timestamp).toLocaleString()}</div>
                    </>
                  ) : 'No prediction yet'}
                  <div style={{marginTop: '10px'}}>
                    <a href={`/location/${loc.id}`}>View Details &rarr;</a>
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
        </MapContainer>
      </div>

      <div className="card" style={{marginTop: '20px'}}>
        <h3>Recent Alerts</h3>
        {alerts.length === 0 && <p>No alerts yet.</p>}
        <ul>
          {alerts.map(a => (
            <li key={a.id}>[{a.channel}] {a.template} — {new Date(a.sent_at).toLocaleString()}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
