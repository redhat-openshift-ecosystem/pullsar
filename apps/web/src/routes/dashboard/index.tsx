import { createFileRoute } from '@tanstack/react-router'
import { ItemList } from '../../components/ItemList'
import type { ListItem } from '../../hooks/useItems'
import { ItemStatsCard } from '../../components/ItemStatsCard'
import { shortCatalogName } from '../../lib/utils'

export const Route = createFileRoute('/dashboard/')({
  component: CatalogListPage,
})

export function CatalogListPage() {
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
    />
  )
}
