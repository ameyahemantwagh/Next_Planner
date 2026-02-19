import React, { createContext, useState, useEffect } from 'react'

export const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [accessToken, setAccessToken] = useState(null)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const t = localStorage.getItem('access_token')
    if (t) setAccessToken(t)
  }, [])

  const signOut = () => {
    localStorage.removeItem('access_token')
    setAccessToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ accessToken, setAccessToken, user, setUser, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}
