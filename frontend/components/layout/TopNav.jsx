import React from 'react'

export default function TopNav() {
  return (
    <header className="sticky top-0 z-20 border-b border-black/5 bg-panel/80 backdrop-blur">
      <div className="app-container flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-accent/15 text-accent flex items-center justify-center font-semibold">
            NP
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold">Next Planner</div>
            <div className="text-xs text-muted">Planning workspace</div>
          </div>
        </div>
        <nav className="flex items-center gap-6 text-sm text-muted">
          <a href="/" className="hover:text-text">Home</a>
          <a href="/board/demo" className="hover:text-text">Board</a>
          <a href="/sessions" className="hover:text-text">Sessions</a>
        </nav>
      </div>
    </header>
  )
}
