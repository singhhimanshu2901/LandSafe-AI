import React, { useState } from 'react'
import { useNavigate, useLocation, Link } from 'react-router-dom'
import { registerUser, login } from '../api/client.js'

export default function Register() {
  const [name, setName] = useState('')
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const navigate = useNavigate()
  const location = useLocation()
  
  const queryParams = new URLSearchParams(location.search)
  const redirectUrl = queryParams.get('redirect') || '/'

  const handleRegister = async (e) => {
    e.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Passwords do not match')
      return
    }

    setLoading(true)
    try {
      // Register defaults to 'citizen' role automatically via backend default
      await registerUser({
        name,
        phone,
        password,
        role: 'citizen',
        language: 'en'
      })
      
      // Auto-login after registration
      const data = await login(phone, password)
      localStorage.setItem('token', data.access_token)
      navigate(redirectUrl)
      window.location.reload()
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ maxWidth: '400px', marginTop: '50px' }}>
      <div className="card">
        <h2>Create Account</h2>
        {error && <p style={{ color: '#c62828', background: '#ffebee', padding: '10px', borderRadius: '4px' }}>{error}</p>}
        <form onSubmit={handleRegister}>
          <div style={{ marginBottom: '10px' }}>
            <label>Name:</label>
            <input 
              type="text" 
              value={name} 
              onChange={e => setName(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Phone / Username:</label>
            <input 
              type="text" 
              value={phone} 
              onChange={e => setPhone(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ marginBottom: '10px' }}>
            <label>Password:</label>
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            />
          </div>
          <div style={{ marginBottom: '20px' }}>
            <label>Confirm Password:</label>
            <input 
              type="password" 
              value={confirmPassword} 
              onChange={e => setConfirmPassword(e.target.value)} 
              required 
              style={{ width: '100%', padding: '8px', boxSizing: 'border-box' }}
            />
          </div>
          <button type="submit" disabled={loading} style={{ width: '100%', padding: '10px', background: '#2e7d32', color: 'white', border: 'none', cursor: 'pointer', borderRadius: '4px' }}>
            {loading ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <div style={{ marginTop: '15px', textAlign: 'center' }}>
          <span>Already have an account? </span>
          <Link to={`/login${redirectUrl !== '/' ? '?redirect=' + encodeURIComponent(redirectUrl) : ''}`}>Login</Link>
        </div>
      </div>
    </div>
  )
}
