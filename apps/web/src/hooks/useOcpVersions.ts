import { useQuery } from '@tanstack/react-query'

const fetchOcpVersions = async (): Promise<string[]> => {
  const response = await fetch('/api/v1/ocp-versions')
  if (!response.ok) throw new Error('Failed to fetch OCP versions')
  return response.json()
}

export const useOcpVersions = () =>
  useQuery({
    queryKey: ['ocpVersions'],
    queryFn: fetchOcpVersions,
  })
