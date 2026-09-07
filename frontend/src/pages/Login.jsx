import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login } from '../api/client.js'

export default function Login() {
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const data = await login(phone, password)
      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '50px' }}>
      <div className="card">
        <h2>Login</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        <form onSubmit={handleLogin}>
          <div style={{ marginBottom: '10px' }}>
            <label>Phone / Username:</label>
            <input 
              type="text" 
              value={phone} 
              onChange={e => setPhone(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px' }}
            />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label>Password:</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px' }}
            />
          </div>
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px', background: '#2e7d32', color: 'white', border: 'none' }}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  )
}
