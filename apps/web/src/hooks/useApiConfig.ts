import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

interface ApiConfig {
  db_start_date: string // the date in "YYYY-MM-DD" format
  export_max_days: number
  all_operators_catalog: string
}

const fetchApiConfig = async (): Promise<ApiConfig> => {
  const response = await fetch(`${API_BASE}/config`)
  if (!response.ok) {
    throw new Error('Failed to fetch API configuration')
  }

  const data = (await response.json()) as ApiConfig
  return data
}

export const useApiConfig = () =>
  useQuery({
    queryKey: ['apiConfig'],
    queryFn: fetchApiConfig,
    staleTime: Infinity,
  })
