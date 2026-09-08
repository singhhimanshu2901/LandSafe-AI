import React, { useEffect, useState } from 'react'
import { api, getReports } from '../api/client.js'

export default function AdminIncidents() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState('ALL')

  const fetchReports = () => {
    getReports().then(data => {
      setReports(data)
      setLoading(false)
    }).catch(e => {
      if (e.response && e.response.status === 401) {
        window.location.href = '/login?redirect=' + encodeURIComponent('/incidents')
      } else if (e.response && e.response.status === 403) {
        setError('Authorized personnel only. You do not have permission to access this area.')
      } else {
        setError('Error loading reports. Please try again later.')
      }
      setLoading(false)
    })
  }

  useEffect(() => {
    fetchReports()
    
    // Reliable polling for real-time updates (every 10 seconds)
    const interval = setInterval(() => {
        getReports().then(data => setReports(data)).catch(() => {})
    }, 10000)
    
    return () => clearInterval(interval)
  }, [])

  const updateStatus = async (id, newStatus) => {
    const note = prompt("Optional resolution notes:")
    try {
      await api.patch(`/reports/${id}/status`, { status: newStatus, resolution_notes: note })
      fetchReports()
    } catch (e) {
      alert("Failed to update status. Are you an admin?")
    }
  }

  const downloadEvidence = async (id) => {
    try {
      const res = await api.get(`/reports/${id}/evidence`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `evidence_${id}.jpg`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (e) {
      alert("Failed to download evidence. You may not be authorized or the file is unavailable.")
    }
  }

  if (loading) return <div className="container">Loading incidents...</div>
  if (error) {
    return (
      <div className="container">
        <h2>Access Denied</h2>
        <div className="card" style={{padding: '30px', textAlign: 'center', marginTop: '20px'}}>
          <h3 style={{color: '#c62828'}}>Restricted Area</h3>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  const filtered = filter === 'ALL' ? reports : reports.filter(r => r.severity === filter || r.status === filter)

  return (
    <div className="container">
      <h2>Admin Incident Management</h2>
      <div style={{marginBottom: '20px'}}>
        <label>Filter: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="ALL">All</option>
          <option value="NEW">Status: NEW</option>
          <option value="UNDER REVIEW">Status: UNDER REVIEW</option>
          <option value="high">Severity: High</option>
          <option value="medium">Severity: Medium</option>
        </select>
      </div>

      <table style={{width: '100%', textAlign: 'left', borderCollapse: 'collapse'}}>
        <thead>
          <tr style={{background: '#f5f5f5'}}>
            <th style={{padding: '10px'}}>Time</th>
            <th>Type</th>
            <th>Severity</th>
            <th>Location</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {filtered.map(r => (
            <tr key={r.id} style={{borderBottom: '1px solid #ddd'}}>
              <td style={{padding: '10px'}}>{new Date(r.created_at).toLocaleString()}</td>
              <td>{r.category}</td>
              <td>{r.severity}</td>
              <td>{r.lat.toFixed(4)}, {r.lon.toFixed(4)}</td>
              <td><strong>{r.status}</strong></td>
              <td>
                {r.media_ref ? (
                    <button onClick={() => downloadEvidence(r.id)} style={{display: 'block', marginBottom: '5px', padding: '5px', cursor: 'pointer', background: '#1976d2', color: 'white', border: 'none'}}>View Evidence</button>
                ) : (
                    <span style={{display: 'block', marginBottom: '5px', color: '#999'}}>No Evidence</span>
                )}
                <select value={r.status} onChange={e => updateStatus(r.id, e.target.value)}>
                  <option value="NEW">NEW</option>
                  <option value="UNDER REVIEW">UNDER REVIEW</option>
                  <option value="VERIFIED">VERIFIED</option>
                  <option value="ASSIGNED">ASSIGNED</option>
                  <option value="IN PROGRESS">IN PROGRESS</option>
                  <option value="RESOLVED">RESOLVED</option>
                </select>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {filtered.length === 0 && <p>No incidents found.</p>}
    </div>
  )
}
