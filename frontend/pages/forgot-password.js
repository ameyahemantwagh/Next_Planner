import {useState} from 'react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function ForgotPassword(){
  const [email,setEmail]=useState('')
  const [msg,setMsg]=useState(null)
  const [loading,setLoading]=useState(false)

  async function submit(e){
    e.preventDefault()
    setLoading(true)
    const res = await fetch(`${API}/api/auth/forgot-password`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email})})
    const data = await res.json()
    setLoading(false)
    setMsg(data.detail)
  }

  return (
    <div style={{padding:20}}>
      <h2>Forgot Password</h2>
      <form onSubmit={submit}>
        <div>
          <label>Email</label><br/>
          <input value={email} onChange={e=>setEmail(e.target.value)} />
        </div>
        <div style={{marginTop:10}}>
          <button disabled={loading}>{loading? 'Please wait...':'Send reset link'}</button>
        </div>
      </form>
      {msg && <p>{msg}</p>}
    </div>
  )
}
