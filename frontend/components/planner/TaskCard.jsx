import React from 'react'

export default function TaskCard({ task, onClick }) {
  return (
    <div className="task-card" role="listitem" tabIndex={0} onClick={() => onClick && onClick(task)}>
      <div className="task-title">{task.title}</div>
      <div className="task-meta">{task.percent_complete}%</div>
    </div>
  )
}
