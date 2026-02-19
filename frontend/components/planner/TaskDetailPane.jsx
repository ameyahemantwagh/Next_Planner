import React from 'react'

export default function TaskDetailPane({ task, onClose }) {
  if (!task) return null
  return (
    <div className="task-detail-pane">
      <button onClick={onClose}>Close</button>
      <h3>{task.title}</h3>
      <p>{task.description}</p>
    </div>
  )
}
