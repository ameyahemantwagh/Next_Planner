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
    <div className="container">
      <h2>Next Planner</h2>

      <div className="social-row">
        <a href={`${API}/api/auth/oauth/google`} className="oauth-link google">Google</a>
        <a href={`${API}/api/auth/oauth/microsoft`} className="oauth-link microsoft">Microsoft</a>
        <a href={`${API}/api/auth/oauth/github`} className="oauth-link github">GitHub</a>
      </div>

      <form onSubmit={submit}>
        <div className="form-row">
          <div className="form-col">
            <label>First Name</label>
            <input required value={firstName} onChange={e=>setFirstName(e.target.value)} />
          </div>
          <div className="form-col">
            <label>Last Name</label>
            <input required value={lastName} onChange={e=>setLastName(e.target.value)} />
          </div>
        </div>

        <div className="mt-8">
          <label>Email</label>
          <input type="email" required value={email} onChange={e=>setEmail(e.target.value)} />
        </div>

        <div className="mt-8">
          <label>Password</label>
          <input type="password" required value={password} onChange={e=>setPassword(e.target.value)} />
        </div>

        <div className="mt-12">
          <button disabled={loading} className="btn-full">{loading? 'Please wait...':'Sign Up'}</button>
        </div>
      </form>

      {msg && <p className="msg">{msg}</p>}
      <p className="mt-8 text-center">Already have an account? <a href="/signin">Login</a></p>
    </div>
  )
}