import { createFileRoute, useParams } from '@tanstack/react-router'
import { type ListItem } from '../../../hooks/useItems'
import { ItemList } from '../../../components/ItemList'
import { ItemStatsCard } from '../../../components/ItemStatsCard'
import { shortCatalogName } from '../../../lib/utils'

export const Route = createFileRoute('/dashboard/$catalogName/')({
  component: PackageListPage,
})

export function PackageListPage() {
  const { catalogName } = useParams({ from: '/dashboard/$catalogName/' })

  return (
    <ItemList
      pathParams={{ catalog_name: catalogName }}
      breadcrumbs={[
        { to: '/dashboard', label: 'Catalogs' },
        {
          to: '/dashboard/$catalogName',
          params: { catalogName },
          label: shortCatalogName(catalogName),
        },
      ]}
      renderItem={(pkg: ListItem) => (
        <ItemStatsCard
          label={pkg.name}
          item={pkg}
          linkTo="/dashboard/$catalogName/$packageName"
          linkParams={{ catalogName, packageName: pkg.name }}
        />
      )}
    />
  )
}
