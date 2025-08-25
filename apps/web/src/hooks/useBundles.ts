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

export interface BundleListItem {
  name: string
  stats: AggregatedPulls
}

export interface BundlesParams {
  catalog_name: string
  package_name: string
  ocp_version: string
  start_date: string
  end_date: string
}

const fetchBundles = async (
  params: BundlesParams
): Promise<BundleListItem[]> => {
  const searchParams = new URLSearchParams({
    ocp_version: params.ocp_version,
    start_date: params.start_date,
    end_date: params.end_date,
  })

  const response = await fetch(
    `/api/v1/catalogs/${params.catalog_name}/packages/${
      params.package_name
    }/bundles?${searchParams.toString()}`
  )

  if (!response.ok) {
    throw new Error(
      'Failed to fetch bundles for package: ' + params.package_name
    )
  }
  const data = (await response.json()) as BundleListItem[]
  return data
}

export const useBundles = (params: BundlesParams) =>
  useQuery({
    queryKey: ['bundles', params],
    queryFn: () => fetchBundles(params),
    enabled:
      !!params.catalog_name &&
      !!params.package_name &&
      !!params.ocp_version &&
      !!params.start_date &&
      !!params.end_date,
  })
