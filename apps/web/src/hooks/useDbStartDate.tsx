import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

interface StartDateResponse {
  db_start_date: string // the date in "YYYY-MM-DD" format
}

const fetchDbStartDate = async (): Promise<string> => {
  const response = await fetch(`${API_BASE}/db-start-date`)
  if (!response.ok) {
    throw new Error('Failed to fetch the DB start date configuration.')
  }

  const data = (await response.json()) as StartDateResponse
  return data.db_start_date
}

export const useDbStartDate = () =>
  useQuery({
    queryKey: ['dbStartDate'],
    queryFn: fetchDbStartDate,
    staleTime: Infinity,
    retry: 3,
  })
