import {useEffect} from 'react'
import {useRouter} from 'next/router'

// Keep this route but redirect to root where the signup UI now lives.
export default function SignupRedirect(){
  const router = useRouter()
  useEffect(()=>{ router.replace('/') }, [router])
  return null
}
