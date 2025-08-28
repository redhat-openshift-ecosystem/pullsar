import { createFileRoute, useParams } from '@tanstack/react-router'
import { type ListItem } from '../../../hooks/useItems'
import { ItemList } from '../../../components/ItemList'
import { ItemStatsCard } from '../../../components/ItemStatsCard'
import { shortBundleName, shortCatalogName } from '../../../lib/utils'

export const Route = createFileRoute('/dashboard/$catalogName/$packageName')({
  component: BundleListPage,
})

export function BundleListPage() {
  const { catalogName, packageName } = useParams({
    from: '/dashboard/$catalogName/$packageName',
  })

  return (
    <ItemList
      pathParams={{
        catalog_name: catalogName,
        package_name: packageName,
      }}
      breadcrumbs={[
        { to: '/dashboard', label: 'Catalogs' },
        {
          to: '/dashboard/$catalogName',
          params: { catalogName },
          label: shortCatalogName(catalogName),
        },
        {
          to: '/dashboard/$catalogName/$packageName',
          params: { catalogName, packageName },
          label: packageName,
        },
      ]}
      renderItem={(bundle: ListItem) => (
        <ItemStatsCard label={shortBundleName(bundle.name)} item={bundle} />
      )}
    />
  )
}
