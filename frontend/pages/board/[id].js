import React, { useContext } from 'react'
import { useRouter } from 'next/router'
import PlannerBoard from '../../components/planner/PlannerBoard'
import { AuthContext } from '../../providers/AuthProvider'
import { usePlan } from '../../hooks/usePlan'

export default function BoardPage() {
  const router = useRouter()
  const { id } = router.query
  const { accessToken } = useContext(AuthContext)
  const { data, error } = usePlan(id, accessToken)

  if (!data) return <div>Loading...</div>
  return (
    <div>
      <PlannerBoard plan={data.plan} />
    </div>
  )
}
