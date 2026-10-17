import { useEffect, useState } from 'react'
import { getHealth, getItems, login } from './api'
import './App.css'

function App() {
  const [health, setHealth] = useState(null)
  const [items, setItems] = useState([])
  const [error, setError] = useState(null)
  const [token, setToken] = useState(null)
  const [email, setEmail] = useState('alice@example.com')
  const [password, setPassword] = useState('secret123')

  // Check health on mount
  useEffect(() => {
    getHealth()
      .then(data => setHealth(data.status))
      .catch(err => setError(err.message))
  }, [])

  // Fetch items when token changes
  useEffect(() => {
    if (token) {
      getItems(token)
        .then(data => setItems(data))
        .catch(err => setError(err.message))
    }
  }, [token])

  const handleLogin = async (e) => {
    e.preventDefault()
    setError(null)
    try {
      const data = await login(email, password)
      setToken(data.access_token)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Frontend ↔ Backend Integration</h1>
      
      <div style={{ marginBottom: '2rem', padding: '1rem', background: '#f5f5f5', borderRadius: '8px' }}>
        <h2>Backend Status: {health === 'ok' ? '✅ Connected' : '❌ Disconnected or Loading'}</h2>
        {error && <p style={{ color: 'red' }}>Error: {error}</p>}
      </div>

      {!token ? (
        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: '300px' }}>
          <h3>Login to see items</h3>
          <p style={{ fontSize: '0.8rem', color: '#666' }}>
            Note: Run `pytest` in the backend first to seed the test user, or register a new one manually.
          </p>
          <input 
            type="email" 
            value={email} 
            onChange={e => setEmail(e.target.value)} 
            placeholder="Email" 
            required 
          />
          <input 
            type="password" 
            value={password} 
            onChange={e => setPassword(e.target.value)} 
            placeholder="Password" 
            required 
          />
          <button type="submit">Login</button>
        </form>
      ) : (
        <div>
          <h3>Welcome! Here are your items:</h3>
          {items.length === 0 ? (
            <p>No items found.</p>
          ) : (
            <ul>
              {items.map(item => (
                <li key={item.id}>
                  <strong>{item.title}</strong> - {item.description || 'No description'}
                </li>
              ))}
            </ul>
          )}
          <button onClick={() => setToken(null)} style={{ marginTop: '1rem' }}>Logout</button>
        </div>
      )}
    </div>
  )
}

export default App
