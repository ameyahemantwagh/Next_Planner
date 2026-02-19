import useSWR from 'swr'
import axios from 'axios'

const fetcher = (url, token) => axios.get(url, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.data)

export function usePlan(planId, token) {
  const { data, error, mutate } = useSWR(planId ? [`/api/planner/plans/${planId}/snapshot`, token] : null, fetcher)
  return { data, error, mutate }
}
