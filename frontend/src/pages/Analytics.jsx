import React, { useEffect, useState } from 'react'
import { api } from '../api/client.js'
import { Scatter, Bar, Pie } from 'react-chartjs-2'

export default function Analytics() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/analytics').then(r => {
      setData(r.data)
      setLoading(false)
    }).catch(e => {
      console.error(e)
      setLoading(false)
    })
  }, [])

  if (loading) return <div className="container">Loading Analytics...</div>
  if (!data) return <div className="container">Error loading analytics.</div>

  const rainRiskData = {
    datasets: [{
      label: 'Rainfall vs Risk Probability',
      data: data.rainfall_risk.map(d => ({ x: d.rainfall_1h, y: d.probability })),
      backgroundColor: 'rgba(54, 162, 235, 0.5)'
    }]
  }

  const rainRiskOptions = {
    scales: {
      x: { title: { display: true, text: 'Rainfall 1h (mm)' } },
      y: { title: { display: true, text: 'Risk Probability' }, min: 0, max: 1 }
    }
  }
  
  const riskDistData = {
    labels: data.risk_distribution.map(d => d.level),
    datasets: [{
      label: 'Active Locations by Risk',
      data: data.risk_distribution.map(d => d.count),
      backgroundColor: ['#2e7d32', '#f9a825', '#ef6c00', '#c62828']
    }]
  }
  
  const qualityData = {
    labels: ['Live/Partial', 'Stale/Unavailable'],
    datasets: [{
      data: [data.data_quality.live_or_partial, data.data_quality.stale],
      backgroundColor: ['#4caf50', '#9e9e9e']
    }]
  }

  return (
    <div className="container">
      <h2>Advanced Risk Analytics</h2>
      <p>Using purely observational database records. Not a causal scientific proof.</p>
      
      <div className="stats" style={{display: 'flex', gap: '20px', marginBottom: '20px'}}>
        <div className="card" style={{flex: 1}}>
          <h3>Total Warnings Issued</h3>
          <p style={{fontSize: '2em'}}>{data.warning_count}</p>
        </div>
      </div>
      
      <div style={{display: 'flex', flexWrap: 'wrap', gap: '20px'}}>
        <div className="card" style={{flex: '1 1 400px', height: '300px'}}>
          <h3>Rainfall vs Risk Probability</h3>
          {data.rainfall_risk.length > 0 ? <Scatter data={rainRiskData} options={rainRiskOptions} /> : <p>INSUFFICIENT DATA</p>}
        </div>
        
        <div className="card" style={{flex: '1 1 300px', height: '300px'}}>
          <h3>Current Risk Distribution</h3>
          {data.risk_distribution.length > 0 ? <Bar data={riskDistData} /> : <p>INSUFFICIENT DATA</p>}
        </div>
        
        <div className="card" style={{flex: '1 1 300px', height: '300px'}}>
          <h3>Data Quality</h3>
          <Pie data={qualityData} />
        </div>
      </div>
    </div>
  )
}
