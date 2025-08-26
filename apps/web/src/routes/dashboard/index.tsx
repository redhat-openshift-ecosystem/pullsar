import { createFileRoute, Link, useSearch } from '@tanstack/react-router'
import { useItems } from '../../hooks/useItems'

export const Route = createFileRoute('/dashboard/')({
  component: CatalogListPage,
})

function CatalogListPage() {
  const {
    ocp_version,
    start_date,
    end_date,
    search_query,
    sort_type,
    is_desc,
    page,
  } = useSearch({
    from: '/dashboard',
  })

  const { data, isLoading } = useItems({
    ocp_version,
    start_date,
    end_date,
    search_query,
    sort_type,
    is_desc,
    page,
  })

  if (isLoading || !data) {
    return <div>Loading...</div>
  }

  const { items: catalogs } = data

  return (
    <div>
      <h2 className="text-2xl font-bold">Available Catalogs</h2>
      <ul className="mt-4 list-disc pl-5 space-y-2">
        {catalogs.map((catalog) => (
          <li key={catalog.name}>
            <Link
              to="/dashboard/$catalogName"
              params={{ catalogName: catalog.name }}
              search={true}
              className="text-blue-500 hover:underline"
            >
              {catalog.name}
            </Link>
            <span className="ml-4 text-sm text-gray-500">
              ({catalog.stats.total_pulls.toLocaleString()} pulls)
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
