import React, { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { AuthProvider } from './AuthProvider'
import { WebsocketProvider } from './WebsocketProvider'

export default function AppProviders({ children }) {
  const [queryClient] = useState(() => new QueryClient())

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <WebsocketProvider>
          {children}
        </WebsocketProvider>
      </AuthProvider>
    </QueryClientProvider>
  )
}
