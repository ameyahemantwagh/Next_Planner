import React, { createContext, useContext, useEffect, useRef, useState } from 'react'
import { AuthContext } from './AuthProvider'

export const WSContext = createContext(null)

export function WebsocketProvider({ children }) {
  const { accessToken, setUser } = useContext(AuthContext)
  const wsRef = useRef(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    if (!accessToken) return
    const url = `${process.env.NEXT_PUBLIC_BACKEND_URL.replace('http','ws')}/ws` // simple conversion
    const ws = new WebSocket(url)
    wsRef.current = ws
    ws.onopen = () => setConnected(true)
    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data)
        // handle messages here
      } catch (err) {
        console.error('WS parse', err)
      }
    }
    ws.onclose = () => setConnected(false)
    return () => {
      try { ws.close() } catch (e) {}
    }
  }, [accessToken])

  const send = (msg) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return
    wsRef.current.send(JSON.stringify(msg))
  }

  return (
    <WSContext.Provider value={{ send, connected }}>
      {children}
    </WSContext.Provider>
  )
}
