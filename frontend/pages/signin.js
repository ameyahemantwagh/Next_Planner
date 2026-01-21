import {useState} from 'react'
import Router from 'next/router'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function SignIn(){
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [loading,setLoading]=useState(false)
  const [msg,setMsg]=useState(null)

  async function submit(e){
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    const res = await fetch(`${API}/api/auth/signin`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({email,password}),
      credentials: 'include'
    })
    const data = await res.json()
    setLoading(false)
    if(res.ok){
      // store access token in memory / simple demo: localStorage
      localStorage.setItem('access_token', data.access_token)
      Router.push('/')
    } else {
      setMsg(data.detail || 'Error')
    }
  }

  return (
    <div style={{padding:20}}>
      <h2>Sign In</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label><br/>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div>
          <label>Password</label><br/>
          <input type="password" value={password} onChange={e=>setPassword(e.target.value)} />
        </div>
        <div style={{marginTop:10}}>
          <button disabled={loading}>{loading? 'Please wait...':'Sign In'}</button>
        </div>
      </form>
      {msg && <p>{msg}</p>}
      <div style={{marginTop:10}}>
        <a href="/forgot-password">Forgot password?</a>
      </div>
    </div>
  )
}
