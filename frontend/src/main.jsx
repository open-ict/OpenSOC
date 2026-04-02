import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  const [token, setToken] = useState('')
  const [email, setEmail] = useState('admin@example.com')
  const [password, setPassword] = useState('ChangeMe123!')
  const [data, setData] = useState(null)
  const [provider, setProvider] = useState('wazuh_api')
  const [rotatePassword, setRotatePassword] = useState('')
  const [syncType, setSyncType] = useState('agents')

  useEffect(() => {
    const hash = window.location.hash || ''
    if (hash.startsWith('#token=')) {
      setToken(hash.replace('#token=', ''))
    }
  }, [])

  const login = async () => {
    const r = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    })
    const j = await r.json()
    setToken(j.access_token)
  }

  const load = async (path, options = {}) => {
    const r = await fetch(path, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
        ...(options.headers || {})
      }
    })
    const j = await r.json()
    setData(j)
  }

  const queueSync = async () => {
    await load('/api/ops/jobs/sync', { method: 'POST', body: JSON.stringify({ sync_type: syncType }) })
  }

  const rotate = async () => {
    await load(`/api/ops/rotate-secret/${provider}`, { method: 'POST', body: JSON.stringify({ password: rotatePassword }) })
  }

  const oidcLogin = () => {
    window.location.href = '/api/auth/oidc/login'
  }

  return <div style={{fontFamily:'Arial', padding:24, maxWidth:1100, margin:'0 auto'}}>
    <h1>OpenSOC v6</h1>
    <p>Production hardening starter dashboard</p>
    <div style={{display:'grid', gridTemplateColumns:'repeat(2, minmax(0, 1fr))', gap:12, marginBottom:16}}>
      <div style={{padding:16, border:'1px solid #ddd', borderRadius:12}}>
        <h3>Authentication</h3>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder='email' style={{display:'block', width:'100%', marginBottom:8}} />
        <input value={password} onChange={e=>setPassword(e.target.value)} type='password' placeholder='password' style={{display:'block', width:'100%', marginBottom:8}} />
        <div style={{display:'flex', gap:8}}>
          <button onClick={login}>Login</button>
          <button onClick={oidcLogin}>OIDC Login</button>
        </div>
        <div style={{marginTop:8, fontSize:12, color:'#555'}}>JWT present: {token ? 'yes' : 'no'}</div>
      </div>
      <div style={{padding:16, border:'1px solid #ddd', borderRadius:12}}>
        <h3>Secret Rotation</h3>
        <input value={provider} onChange={e=>setProvider(e.target.value)} placeholder='provider' style={{display:'block', width:'100%', marginBottom:8}} />
        <input value={rotatePassword} onChange={e=>setRotatePassword(e.target.value)} type='password' placeholder='new secret' style={{display:'block', width:'100%', marginBottom:8}} />
        <button onClick={rotate}>Rotate Secret</button>
      </div>
    </div>

    <div style={{display:'grid', gridTemplateColumns:'repeat(3, minmax(0, 1fr))', gap:8}}>
      <button onClick={()=>load('/api/me')}>Me</button>
      <button onClick={()=>load('/api/billing')}>Billing</button>
      <button onClick={()=>load('/api/integrations/wazuh')}>Integrations</button>
      <button onClick={()=>load('/api/endpoints')}>Endpoints</button>
      <button onClick={()=>load('/api/alerts')}>Alerts</button>
      <button onClick={()=>load('/api/audit-logs')}>Audit Logs</button>
      <button onClick={()=>load('/api/notifications')}>Notifications</button>
      <button onClick={()=>load('/api/ops/metrics')}>Metrics</button>
      <button onClick={()=>load('/api/ops/jobs')}>Sync Jobs</button>
      <button onClick={()=>load('/api/ops/jobs/dead-letter')}>Dead Letter Queue</button>
      <button onClick={()=>load('/api/ops/wazuh-health')}>Wazuh Health</button>
      <button onClick={()=>load('/health/ready')}>Readiness</button>
    </div>

    <div style={{marginTop:16, padding:16, border:'1px solid #ddd', borderRadius:12}}>
      <h3>Queue Operations</h3>
      <input value={syncType} onChange={e=>setSyncType(e.target.value)} placeholder='agents or alerts' style={{marginRight:8}} />
      <button onClick={queueSync}>Queue Sync Job</button>
      <button onClick={()=>load('/api/ops/test-notification', {method:'POST'})} style={{marginLeft:8}}>Queue Test Notification</button>
    </div>

    <pre style={{marginTop:20, background:'#f5f5f5', padding:16, borderRadius:8, whiteSpace:'pre-wrap'}}>{JSON.stringify(data, null, 2)}</pre>
  </div>
}

createRoot(document.getElementById('root')).render(<App />)
