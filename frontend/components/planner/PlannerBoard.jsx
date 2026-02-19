import React from 'react'

export default function PlannerBoard({ plan }) {
  return (
    <div className="planner-board">
      <h2>{plan.name}</h2>
      <div className="buckets">{
        (plan.buckets || []).map(b => (
          <div key={b.id} className="bucket-column">
            <h3>{b.title}</h3>
          </div>
        ))
      }</div>
    </div>
  )
}
