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

export interface PackageListItem {
  name: string
  stats: AggregatedPulls
}

export interface PackagesParams {
  catalog_name: string
  ocp_version: string
  start_date: string
  end_date: string
}

const fetchPackages = async (
  params: PackagesParams
): Promise<PackageListItem[]> => {
  const searchParams = new URLSearchParams({
    ocp_version: params.ocp_version,
    start_date: params.start_date,
    end_date: params.end_date,
  })

  const response = await fetch(
    `/api/v1/catalogs/${params.catalog_name}/packages?${searchParams.toString()}`
  )

  if (!response.ok) {
    throw new Error(
      'Failed to fetch packages for catalog: ' + params.catalog_name
    )
  }
  const data = (await response.json()) as PackageListItem[]
  return data
}

export const usePackages = (params: PackagesParams) =>
  useQuery({
    queryKey: ['packages', params],
    queryFn: () => fetchPackages(params),
    enabled:
      !!params.catalog_name &&
      !!params.ocp_version &&
      !!params.start_date &&
      !!params.end_date,
  })
