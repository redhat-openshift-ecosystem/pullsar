import { useQuery } from '@tanstack/react-query'

const fetchSortTypes = async (): Promise<string[]> => {
  const response = await fetch('/api/v1/sort-types')
  if (!response.ok) throw new Error('Failed to fetch sort types')

  const data = (await response.json()) as string[]
  return data
}

export const useSortTypes = () =>
  useQuery({
    queryKey: ['sortTypes'],
    queryFn: fetchSortTypes,
  })
