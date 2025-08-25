import { useQuery } from '@tanstack/react-query'

interface ChartDataPoint {
  date: string
  pulls: number
}

interface AggregatedPulls {
  total_pulls: number
  trend: number | null
  chart_data: ChartDataPoint[]
}

export interface CatalogListItem {
  name: string
  stats: AggregatedPulls
}

export interface CatalogsParams {
  ocp_version: string
  start_date: string
  end_date: string
}

const fetchCatalogs = async (
  params: CatalogsParams
): Promise<CatalogListItem[]> => {
  const searchParams = new URLSearchParams({
    ocp_version: params.ocp_version,
    start_date: params.start_date,
    end_date: params.end_date,
  })

  const response = await fetch(`/api/v1/catalogs?${searchParams.toString()}`)

  if (!response.ok) {
    throw new Error('Failed to fetch catalogs')
  }
  const data = (await response.json()) as CatalogListItem[]
  return data
}

export const useCatalogs = (params: CatalogsParams) =>
  useQuery({
    queryKey: ['catalogs', params],
    queryFn: () => fetchCatalogs(params),
    enabled: !!params.ocp_version && !!params.start_date && !!params.end_date,
  })
