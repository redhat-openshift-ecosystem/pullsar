import { useQuery } from '@tanstack/react-query'

interface SummaryStatsApiResponse {
  total_catalogs: number
  total_packages: number
  total_bundles: number
  total_pulls: number
}

const fetchSummaryStats = async (): Promise<SummaryStatsApiResponse> => {
  const response = await fetch('/api/v1/summary')
  if (!response.ok) throw new Error('Failed to fetch summary stats')
  const data = (await response.json()) as SummaryStatsApiResponse
  return data
}

export const useSummaryStats = () =>
  useQuery({
    queryKey: ['summaryStats'],
    queryFn: fetchSummaryStats,
  })
