import {useEffect, useState} from 'react'

function getCsrf(){
  // read csrf_token cookie
  const v = document.cookie.split('; ').find(row => row.startsWith('csrf_token='))
  return v ? v.split('=')[1] : null
}

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function Sessions(){
  const [sessions,setSessions]=useState([])
  const [msg,setMsg]=useState(null)

  async function load(){
    const token = localStorage.getItem('access_token')
    if(!token){ setMsg('Not signed in'); return }
    const res = await fetch(`${API}/api/auth/sessions`, {headers: {Authorization: `Bearer ${token}`}})
    if(res.ok){
      const data = await res.json()
      setSessions(data)
    } else {
      setMsg('Failed to load sessions')
    }
  }

  useEffect(()=>{ load() }, [])

  async function revoke(id){
    const token = localStorage.getItem('access_token')
    const csrf = getCsrf()
    const res = await fetch(`${API}/api/auth/sessions/revoke`, {method:'POST', headers: {Authorization: `Bearer ${token}`, 'Content-Type':'application/json', 'x-csrf': csrf}, body: JSON.stringify({session_id: id}), credentials: 'include'})
    if(res.ok){ load() }
  }

  async function revokeAll(){
    const token = localStorage.getItem('access_token')
    const csrf = getCsrf()
    const res = await fetch(`${API}/api/auth/sessions/revoke-all`, {method:'POST', headers: {Authorization: `Bearer ${token}`, 'x-csrf': csrf}})
    if(res.ok){ load() }
  }

  return (
    <div style={{padding:20}}>
      <h2>Active Sessions</h2>
      {msg && <p>{msg}</p>}
      <button onClick={revokeAll}>Revoke All Sessions</button>
      <ul>
      {sessions.map(s=> (
        <li key={s.id} style={{marginTop:8}}>
          <div><strong>{s.device_info || 'Unknown device'}</strong></div>
          <div>Created: {s.created_at}</div>
          <div>Expires: {s.expires_at}</div>
          <div>Revoked: {s.revoked ? 'Yes':'No'}</div>
          <div><button onClick={()=>revoke(s.id)}>Revoke</button></div>
        </li>
      ))}
      </ul>
    </div>
  )
}
