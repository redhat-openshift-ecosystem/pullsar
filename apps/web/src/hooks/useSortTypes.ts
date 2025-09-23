import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

const fetchSortTypes = async (): Promise<string[]> => {
  const response = await fetch(`${API_BASE}/sort-types`)
  if (!response.ok) throw new Error('Failed to fetch sort types')

  const data = (await response.json()) as string[]
  return data
}

export const useSortTypes = () =>
  useQuery({
    queryKey: ['sortTypes'],
    queryFn: fetchSortTypes,
  })
