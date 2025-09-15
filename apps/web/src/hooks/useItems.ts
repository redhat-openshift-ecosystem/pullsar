import { useQuery } from '@tanstack/react-query'
import { API_BASE } from './api'

interface ChartDataPoint {
  date: string
  pulls: number
}

interface AggregatedPulls {
  total_pulls: number
  trend: number
  chart_data: ChartDataPoint[]
}

export interface ListItem {
  name: string
  stats: AggregatedPulls
}

export interface Params {
  ocp_version: string
  start_date: string
  end_date: string
  search_query: string
  sort_type: string
  is_desc: boolean
  page: number
  catalog_name?: string
  package_name?: string
}

export interface PaginatedResponse {
  total_count: number
  page_size: number
  items: ListItem[]
}

const fetchItems = async (params: Params): Promise<PaginatedResponse> => {
  const searchParams = new URLSearchParams({
    ocp_version: params.ocp_version,
    start_date: params.start_date,
    end_date: params.end_date,
    search_query: params.search_query,
    sort_type: params.sort_type,
    is_desc: String(params.is_desc),
    page: String(params.page),
  })

  let url = API_BASE + '/catalogs'
  if (params.catalog_name) {
    url += `/${params.catalog_name}/packages`
    if (params.package_name) {
      url += `/${params.package_name}/bundles`
    }
  }

  const response = await fetch(url + '?' + searchParams.toString())

  if (!response.ok) {
    throw new Error('Failed to fetch items')
  }
  const data = (await response.json()) as PaginatedResponse
  return data
}

export const useItems = (params: Params) =>
  useQuery({
    queryKey: ['items', params],
    queryFn: () => fetchItems(params),
  })
