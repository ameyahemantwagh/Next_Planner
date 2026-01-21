import {useState} from 'react'

const API = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:9003'

export default function SignUp(){
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [email,setEmail]=useState('')
  const [password,setPassword]=useState('')
  const [loading,setLoading]=useState(false)
  const [msg,setMsg]=useState(null)

  async function submit(e){
    e.preventDefault()
    setLoading(true)
    setMsg(null)
    const res = await fetch(`${API}/api/auth/signup`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({first_name: firstName, last_name: lastName, email, password})
    })
    const data = await res.json()
    setLoading(false)
    if(res.ok){
      setMsg(data.detail || 'Registered successfully')
    } else {
      setMsg(data.detail || 'Error')
    }
  }

  return (
    <div className="container" style={{maxWidth:480, margin:'40px auto', background:'rgba(58, 175, 169, 0.15)', padding:24, borderRadius:8}}>
      <h2 style={{marginTop:0}}>Next Planner</h2>

      <div style={{display:'flex', gap:8, marginBottom:12}}>
        <a href={`${API}/api/auth/oauth/google`} style={{flex:1, padding:10, background:'#dd4b39', color:'#fff', textAlign:'center', borderRadius:4}}>Google</a>
        <a href={`${API}/api/auth/oauth/microsoft`} style={{flex:1, padding:10, background:'#2F2F8A', color:'#fff', textAlign:'center', borderRadius:4}}>Microsoft</a>
        <a href={`${API}/api/auth/oauth/github`} style={{flex:1, padding:10, background:'#24292e', color:'#fff', textAlign:'center', borderRadius:4}}>GitHub</a>
      </div>

      <form onSubmit={submit}>
        <div style={{display:'flex', gap:8}}>
          <div style={{flex:1}}>
            <label>First Name</label><br/>
            <input required value={firstName} onChange={e=>setFirstName(e.target.value)} />
          </div>
          <div style={{flex:1}}>
            <label>Last Name</label><br/>
            <input required value={lastName} onChange={e=>setLastName(e.target.value)} />
          </div>
        </div>

        <div style={{marginTop:8}}>
          <label>Email</label><br/>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} />
        </div>

        <div style={{marginTop:8}}>
          <label>Password</label><br/>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} />
        </div>

        <div style={{marginTop:12}}>
          <button disabled={loading} style={{width:'100%', padding:10}}>{loading? 'Please wait...':'Sign Up'}</button>
        </div>
      </form>

      {msg && <p style={{marginTop:12}}>{msg}</p>}
    </div>
  )
}