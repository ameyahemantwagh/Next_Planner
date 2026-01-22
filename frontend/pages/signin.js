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
    let res, data
    try {
      res = await fetch(`${API}/api/auth/signin`, {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({email,password}),
        credentials: 'include'
      })
    } catch (err) {
      setLoading(false)
      setMsg('Network error: ' + (err.message || 'Failed to reach server'))
      return
    }

    try {
      data = await res.json()
    } catch (err) {
      setLoading(false)
      setMsg('Invalid server response')
      return
    }

    setLoading(false)
    if(res.ok){
      localStorage.setItem('access_token', data.access_token)
      Router.push('/')
    } else {
      setMsg(data.detail || 'Error')
    }
  }

  return (
    <div className="container">
      <h2>Next Planner</h2>

      <div className="social-row">
        <a href={`${API}/api/auth/oauth/google`} className="oauth-link google">Google</a>
        <a href={`${API}/api/auth/oauth/microsoft`} className="oauth-link microsoft">Microsoft</a>
        <a href={`${API}/api/auth/oauth/github`} className="oauth-link github">GitHub</a>
      </div>

      <form onSubmit={submit}>
        <div className="mt-8">
          <label>Email</label>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} />
        </div>

        <div className="mt-8">
          <label>Password</label>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} />
        </div>

        <div className="mt-12">
          <button type="submit" disabled={loading} className="btn-full block">{loading? 'Please wait...':'Sign In'}</button>
        </div>
      </form>

      {msg && <p className="msg">{msg}</p>}
      <p className="mt-8 text-center">Do not have an account? <a href="/">Sign Up</a></p>
    </div>
  )
}
