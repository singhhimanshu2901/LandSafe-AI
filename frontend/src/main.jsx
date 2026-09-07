import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import FieldReport from './pages/FieldReport.jsx'
import Login from './pages/Login.jsx'
import LocationDetail from './pages/LocationDetail.jsx'
import Analytics from './pages/Analytics.jsx'
import AdminIncidents from './pages/AdminIncidents.jsx'
import './styles.css'

function App() {
  const token = localStorage.getItem('token')
  const handleLogout = () => {
    localStorage.removeItem('token')
    window.location.href = '/login'
  }

  return (
    <BrowserRouter>
      <nav className="navbar">
        <span className="brand">Landsafe AI</span>
        <Link to="/" style={{marginRight: '15px', color: 'white'}}>Dashboard</Link>
        <Link to="/analytics" style={{marginRight: '15px', color: 'white'}}>Analytics</Link>
        <Link to="/report" style={{marginRight: '15px', color: 'white'}}>Submit Report</Link>
        <Link to="/incidents" style={{marginRight: '15px', color: 'white'}}>Incidents (Admin)</Link>
        {token ? (
          <button onClick={handleLogout} style={{marginLeft: 'auto', background: 'transparent', color: 'white', border: '1px solid white', padding: '4px 8px', cursor: 'pointer'}}>Logout</button>
        ) : (
          <Link to="/login" style={{marginLeft: 'auto'}}>Login</Link>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/location/:id" element={<LocationDetail />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/report" element={<FieldReport />} />
        <Route path="/incidents" element={<AdminIncidents />} />
        <Route path="/login" element={<Login />} />
      </Routes>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
