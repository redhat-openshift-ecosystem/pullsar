import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

const fetchOcpVersions = async (): Promise<string[]> => {
  const response = await fetch(`${API_BASE}/ocp-versions`)
  if (!response.ok) throw new Error('Failed to fetch OCP versions')

  const data = (await response.json()) as string[]
  return data
}

export const useOcpVersions = () =>
  useQuery({
    queryKey: ['ocpVersions'],
    queryFn: fetchOcpVersions,
  })
