import React from 'react'
import TopNav from './TopNav'
import Sidebar from './Sidebar'

export default function AppShell({ children }) {
  return (
    <div className="app-shell">
      <TopNav />
      <div className="app-container">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-3">
            <Sidebar />
          </div>
          <main className="col-span-12 lg:col-span-9">
            <div className="panel p-6">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}
