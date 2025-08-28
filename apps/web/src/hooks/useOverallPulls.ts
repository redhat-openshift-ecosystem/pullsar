import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

interface OverallPullsApiResponse {
  total_pulls: number
  trend?: number
  chart_data: { date: string; pulls: number }[]
}

interface OverallPullsParams {
  ocp_version: string
  start_date: string
  end_date: string
}

const fetchOverallPulls = async (
  params: OverallPullsParams
): Promise<OverallPullsApiResponse> => {
  const searchParams = new URLSearchParams({
    ocp_version: params.ocp_version,
    start_date: params.start_date,
    end_date: params.end_date,
  })
  const response = await fetch(`${API_BASE}/overall?${searchParams.toString()}`)
  if (!response.ok) throw new Error('Failed to fetch overall pull statistics')
  const data = (await response.json()) as OverallPullsApiResponse
  return data
}

export const useOverallPulls = (params: OverallPullsParams) =>
  useQuery({
    queryKey: ['overallPulls', params],
    queryFn: () => fetchOverallPulls(params),
    enabled: !!params.ocp_version && !!params.start_date && !!params.end_date,
  })
