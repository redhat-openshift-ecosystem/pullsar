import { createFileRoute, useSearch } from '@tanstack/react-router'
import { ItemList } from '../../components/ItemList'
import type { ListItem } from '../../hooks/useItems'
import { ItemStatsCard } from '../../components/ItemStatsCard'
import { shortCatalogName } from '../../lib/utils'
import { useOverallPulls } from '../../hooks/useOverallPulls'
import type { DashboardPageSearchParams } from '../../lib/schemas'
import { useApiConfig } from '../../hooks/useApiConfig'

const DEFAULT_ALL_OPERATORS_CATALOG = 'All Operators'

export const Route = createFileRoute('/dashboard/')({
  component: CatalogListPage,
})

export function CatalogListPage() {
  const { ocp_version, start_date, end_date }: DashboardPageSearchParams =
    useSearch({
      from: '/dashboard',
    })

  const { data: apiConfig, isLoading: isApiConfigLoading } = useApiConfig()
  const allOperatorsCatalog =
    apiConfig?.all_operators_catalog ?? DEFAULT_ALL_OPERATORS_CATALOG

  const { data, isLoading } = useOverallPulls({
    ocp_version,
    start_date,
    end_date,
  })

  const allOperatorsItem: ListItem | undefined = data
    ? { name: allOperatorsCatalog, stats: data }
    : undefined

  return (
    <ItemList
      pathParams={{}}
      breadcrumbs={[{ to: '/dashboard', label: 'Catalogs' }]}
      renderItem={(catalog: ListItem) => (
        <ItemStatsCard
          label={shortCatalogName(catalog.name)}
          item={catalog}
          linkTo="/dashboard/$catalogName"
          linkParams={{ catalogName: catalog.name }}
        />
      )}
      extraItem={allOperatorsItem}
      isExtraItemLoading={isLoading || isApiConfigLoading}
    />
  )
}
