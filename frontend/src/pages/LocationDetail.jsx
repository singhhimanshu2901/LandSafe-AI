import React, { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getIntelligence, getRiskHistory, getAlerts } from '../api/client.js'
import { Line } from 'react-chartjs-2'
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)

export default function LocationDetail() {
  const { id } = useParams()
  const [data, setData] = useState(null)
  const [history, setHistory] = useState([])
  const [alerts, setAlerts] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getIntelligence(id),
      getRiskHistory(id),
      getAlerts()
    ]).then(([intel, hist, allAlerts]) => {
      setData(intel)
      setHistory(hist.reverse()) // older to newer
      setAlerts(allAlerts) // In a real app we'd filter alerts by location_id (if our API supported it), here we just show what we have
      setLoading(false)
    }).catch(e => {
      console.error(e)
      setLoading(false)
    })
  }, [id])

  if (loading) return <div className="container">Loading...</div>
  if (!data) return <div className="container">Error loading location data.</div>

  const chartData = {
    labels: history.map(h => new Date(h.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Risk Probability',
        data: history.map(h => h.probability || 0),
        borderColor: '#c62828',
        backgroundColor: 'rgba(198, 40, 40, 0.5)',
      }
    ]
  }
  
  const chartOptions = {
    responsive: true,
    scales: { y: { min: 0, max: 1 } }
  }

  return (
    <div className="container">
      <Link to="/">&larr; Back to Dashboard</Link>
      <h2>Location Intelligence</h2>
      <p>ID: {data.location_id}</p>
      
      <div className="stats" style={{display: 'flex', gap: '20px', marginBottom: '20px', flexWrap: 'wrap'}}>
        <div className="card" style={{flex: '1 1 300px'}}>
          <h3>Environmental</h3>
          <p>Status: {data.weather.status}</p>
          <p>Rainfall: {data.weather.rainfall != null ? data.weather.rainfall + ' mm' : 'N/A'}</p>
          <p>Temperature: {data.weather.temperature != null ? data.weather.temperature + ' °C' : 'N/A'}</p>
          <p>Humidity: {data.weather.humidity != null ? data.weather.humidity + ' %' : 'N/A'}</p>
          <p>Updated: {data.weather.timestamp ? new Date(data.weather.timestamp).toLocaleString() : 'N/A'}</p>
        </div>
        
        <div className="card" style={{flex: '1 1 300px'}}>
          <h3>Terrain</h3>
          <p>Elevation: {data.elevation != null ? data.elevation + ' m' : 'N/A'}</p>
          <p>Slope: {data.slope != null ? data.slope + ' °' : 'N/A'}</p>
          <p>Terrain Data Status: {data.elevation != null ? 'AVAILABLE' : 'UNAVAILABLE'}</p>
        </div>

        <div className="card" style={{flex: '1 1 300px'}}>
          <h3>Risk Assessment</h3>
          <p>Level: <strong>{data.risk.level}</strong></p>
          <p>Probability: {data.risk.probability != null ? (data.risk.probability * 100).toFixed(1) + '%' : 'N/A'}</p>
          <p>Updated: {data.risk.timestamp ? new Date(data.risk.timestamp).toLocaleString() : 'N/A'}</p>
          <hr />
          <h4>Recommended Action</h4>
          <p><em>Decision-support only. Not an official emergency order.</em></p>
          <p>{data.recommended_action}</p>
        </div>
        
        <div className="card" style={{flex: '1 1 300px'}}>
          <h3>Data Quality</h3>
          <p>Weather: {data.weather.status}</p>
          <p>Sensors (IoT): {data.sensors.status}</p>
          <p>Historical Events: {data.historical.status}</p>
        </div>
      </div>
      
      <div className="card" style={{marginBottom: '20px'}}>
        <h3>AI Explanation</h3>
        {data.ai_explanation && data.ai_explanation.human_explanation ? (
          <>
            <p>{data.ai_explanation.human_explanation}</p>
            <details>
              <summary>Technical Details (Top Features)</summary>
              <ul>
                {data.ai_explanation.top_features && data.ai_explanation.top_features.map(f => (
                  <li key={f.feature}>{f.feature}: {f.value.toFixed(2)} (Importance: {f.importance.toFixed(3)})</li>
                ))}
              </ul>
            </details>
          </>
        ) : (
          <p>No explanation available for this prediction.</p>
        )}
      </div>
      
      <div className="card" style={{marginBottom: '20px'}}>
        <h3>Risk History Trend</h3>
        {history.length > 0 ? (
          <div style={{height: '300px'}}>
            <Line data={chartData} options={chartOptions} />
          </div>
        ) : (
          <p>No historical risk data available.</p>
        )}
      </div>
      
      <div className="card">
        <h3>Recent Warnings (Global)</h3>
        {alerts.length === 0 && <p>No active alerts.</p>}
        <ul>
          {alerts.map(a => (
            <li key={a.id}>[{a.channel}] {a.template} — {new Date(a.sent_at).toLocaleString()}</li>
          ))}
        </ul>
      </div>
    </div>
  )
}
