import {useState} from 'react'
import {useRouter} from 'next/router'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function VerifyEmail(){
  const r = useRouter()
  const [msg,setMsg]=useState(null)
  const [loading,setLoading]=useState(false)

  async function verify(token){
    setLoading(true)
    const res = await fetch(`${API}/api/auth/verify-email`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token})})
    const data = await res.json()
    setLoading(false)
    setMsg(data.detail)
  }

  if(typeof r.query.token !== 'undefined' && !msg && !loading){
    verify(r.query.token)
  }

  return (
    <div style={{padding:20}}>
      <h2>Verify Email</h2>
      {loading? <p>Verifying...</p> : msg ? <p>{msg}</p> : <p>Waiting for token...</p>}
    </div>
  )
}
