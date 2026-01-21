import {useState} from 'react'
import Router from 'next/router'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function Trial(){
  const [email,setEmail]=useState('')
  const [msg,setMsg]=useState(null)
  const [loading,setLoading]=useState(false)

  async function submit(e){
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    const res = await fetch(`${API}/api/auth/trial`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email}), credentials: 'include'})
    const data = await res.json()
    setLoading(false)
    if(res.ok){
      localStorage.setItem('access_token', data.access_token)
      Router.push('/')
    } else {
      setMsg(data.detail || 'Error')
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Request 24h Trial Access</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label><br/>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div style={{marginTop:10}}>
          <button disabled={loading}>{loading? 'Please wait...':'Request Trial'}</button>
        </div>
      </form>
      {msg && <p>{msg}</p>}
    </div>
  )
}
