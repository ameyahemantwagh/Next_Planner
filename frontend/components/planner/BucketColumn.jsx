import React from 'react'

export default function BucketColumn({ bucket, tasks }) {
  return (
    <div className="bucket-column" role="list" aria-label={bucket.title}>
      <div className="bucket-header">{bucket.title}</div>
      <div className="task-list">
        {(tasks || []).map(t => (
          <div key={t.id} className="task-card" role="listitem">{t.title}</div>
        ))}
      </div>
    </div>
  )
}
