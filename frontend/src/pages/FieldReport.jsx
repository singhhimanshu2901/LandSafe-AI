import React, { useState, useEffect } from 'react'
import { createReport, uploadEvidence } from '../api/client.js'
import { useNavigate, useLocation } from 'react-router-dom'

const CATEGORIES = ['LANDSLIDE', 'ROAD_BLOCKAGE', 'FLASH_FLOOD', 'SLOPE_FAILURE', 'FALLEN_TREE', 'OTHER']

export default function FieldReport() {
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!localStorage.getItem('token')) {
      navigate('/login?redirect=' + encodeURIComponent(location.pathname))
    }
  }, [navigate, location])

  const [form, setForm] = useState({ lat: '', lon: '', category: 'LANDSLIDE', severity: 'low', description: '' })
  const [status, setStatus] = useState(null)
  const [image, setImage] = useState(null)
  const [uploadStatus, setUploadStatus] = useState(null)

  const useMyLocation = () => {
    navigator.geolocation?.getCurrentPosition(pos => {
      setForm(f => ({ ...f, lat: pos.coords.latitude, lon: pos.coords.longitude }))
    })
  }

  const handleFile = (e) => {
    const file = e.target.files[0]
    if (!file) return
    if (!['image/jpeg', 'image/png', 'image/webp'].includes(file.type)) {
      alert("Only JPEG, PNG, and WEBP formats are allowed.")
      return
    }
    setImage(file)
  }

  const submit = async (e) => {
    e.preventDefault()
    setStatus('Submitting report...')
    setUploadStatus(null)
    try {
      const res = await createReport({ ...form, lat: parseFloat(form.lat), lon: parseFloat(form.lon) })
      setStatus('Report submitted successfully.')
      
      if (image) {
        if (!navigator.onLine) {
            setUploadStatus('Evidence upload requires an internet connection. Report saved locally.')
            return
        }
        setUploadStatus('Uploading evidence...')
        try {
          await uploadEvidence(res.id, image)
          setUploadStatus('Upload successful.')
        } catch (uploadErr) {
          console.error(uploadErr)
          setUploadStatus('Upload failed. The report was saved without evidence.')
        }
      }
    } catch (err) {
      if (err.response?.status === 401) {
          setStatus('Authentication required. Please log in.')
          return
      }
      setStatus('Failed to submit — saved locally, will retry when online.')
      const queue = JSON.parse(localStorage.getItem('landsafe_offline_queue') || '[]')
      queue.push(form)
      localStorage.setItem('landsafe_offline_queue', JSON.stringify(queue))
      if (image) {
          setUploadStatus('Evidence upload requires an internet connection.')
      }
    }
  }

  return (
    <div className="container" style={{maxWidth: '600px', padding: '15px'}}>
      <h2>Field Hazard Report</h2>
      <form onSubmit={submit} className="card" style={{display: 'flex', flexDirection: 'column', gap: '15px'}}>
        <button type="button" onClick={useMyLocation} style={{padding: '15px', fontSize: '1.2em', background: '#e0e0e0', color: '#000'}}>📍 Use My GPS Location</button>
        
        <div style={{display: 'flex', gap: '10px'}}>
            <input placeholder="Latitude" value={form.lat} onChange={e => setForm({ ...form, lat: e.target.value })} required style={{flex: 1, padding: '12px'}} />
            <input placeholder="Longitude" value={form.lon} onChange={e => setForm({ ...form, lon: e.target.value })} required style={{flex: 1, padding: '12px'}} />
        </div>
        
        <label><strong>Incident Type</strong></label>
        <select value={form.category} onChange={e => setForm({ ...form, category: e.target.value })} style={{padding: '12px'}}>
          {CATEGORIES.map(c => <option key={c} value={c}>{c.replace('_', ' ')}</option>)}
        </select>
        
        <label><strong>Severity</strong></label>
        <select value={form.severity} onChange={e => setForm({ ...form, severity: e.target.value })} style={{padding: '12px'}}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        
        <label><strong>Description</strong></label>
        <textarea placeholder="Describe the hazard..." value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} style={{padding: '12px', minHeight: '100px'}} />
        
        <label><strong>Evidence Photo (Optional)</strong></label>
        <input type="file" accept="image/jpeg, image/png, image/webp" onChange={handleFile} style={{padding: '12px'}} />
        {image && (
          <div style={{background: '#f9f9f9', padding: '10px', borderRadius: '5px'}}>
             <p>Selected: {image.name} ({(image.size / 1024 / 1024).toFixed(2)} MB)</p>
             <button type="button" onClick={() => setImage(null)} style={{background: 'red', color: 'white', padding: '5px 10px'}}>Remove Image</button>
          </div>
        )}

        <button type="submit" style={{padding: '15px', fontSize: '1.2em', background: '#2e7d32', color: 'white'}}>Submit Field Report</button>
      </form>
      {status && <p style={{fontWeight: 'bold'}}>{status}</p>}
      {uploadStatus && <p>{uploadStatus}</p>}
    </div>
  )
}
