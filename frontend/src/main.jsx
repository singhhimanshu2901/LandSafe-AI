import React, { useMemo } from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom'
import Dashboard from './pages/Dashboard.jsx'
import FieldReport from './pages/FieldReport.jsx'
import Login from './pages/Login.jsx'
import Register from './pages/Register.jsx'
import LocationDetail from './pages/LocationDetail.jsx'
import Analytics from './pages/Analytics.jsx'
import AdminIncidents from './pages/AdminIncidents.jsx'
import './styles.css'

function parseJwt(token) {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
  } catch (e) {
    return null;
  }
}

function App() {
  const token = localStorage.getItem('token')
  const payload = useMemo(() => token ? parseJwt(token) : null, [token])
  const role = payload?.role || 'public'
  
  const isAdmin = ['district_admin', 'state_admin', 'super_admin'].includes(role)

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
        
        {isAdmin && (
          <Link to="/incidents" style={{marginRight: '15px', color: 'white'}}>Incidents (Admin)</Link>
        )}
        
        {token ? (
          <button onClick={handleLogout} style={{marginLeft: 'auto', background: 'transparent', color: 'white', border: '1px solid white', padding: '4px 8px', cursor: 'pointer', borderRadius: '4px'}}>Logout</button>
        ) : (
          <div style={{marginLeft: 'auto'}}>
            <Link to="/login" style={{color: 'white', marginRight: '15px'}}>Login</Link>
            <Link to="/register" style={{color: 'white', border: '1px solid white', padding: '4px 8px', borderRadius: '4px', textDecoration: 'none'}}>Register</Link>
          </div>
        )}
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/location/:id" element={<LocationDetail />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/report" element={<FieldReport />} />
        <Route path="/incidents" element={<AdminIncidents />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </BrowserRouter>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(<App />)
