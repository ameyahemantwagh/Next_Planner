import React from 'react'

export default function Sidebar() {
  return (
    <aside className="panel p-4">
      <div className="text-xs font-semibold text-muted uppercase tracking-wide">Workspace</div>
      <div className="mt-3 space-y-2 text-sm">
        <a className="block rounded-lg px-3 py-2 hover:bg-black/5" href="/">Overview</a>
        <a className="block rounded-lg px-3 py-2 hover:bg-black/5" href="/board/demo">Boards</a>
        <a className="block rounded-lg px-3 py-2 hover:bg-black/5" href="/trial">Trial Access</a>
      </div>
      <div className="mt-6 text-xs font-semibold text-muted uppercase tracking-wide">Account</div>
      <div className="mt-3 space-y-2 text-sm">
        <a className="block rounded-lg px-3 py-2 hover:bg-black/5" href="/signin">Sign In</a>
        <a className="block rounded-lg px-3 py-2 hover:bg-black/5" href="/">Sign Up</a>
      </div>
    </aside>
  )
}
