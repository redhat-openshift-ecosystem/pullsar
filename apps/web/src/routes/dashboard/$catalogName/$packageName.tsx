import { createFileRoute, useParams, useSearch } from '@tanstack/react-router'
import { useItems } from '../../../hooks/useItems'

export const Route = createFileRoute('/dashboard/$catalogName/$packageName')({
  component: BundleListPage,
})

function BundleListPage() {
  const { catalogName, packageName } = useParams({
    from: '/dashboard/$catalogName/$packageName',
  })

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
    catalog_name: catalogName,
    package_name: packageName,
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

  const { items: bundles } = data

  return (
    <div>
      <h3 className="text-lg text-secondary">
        in Catalog: {catalogName} in Package: {packageName}
      </h3>
      <ul className="mt-4 list-disc pl-5 space-y-2">
        {bundles.map((bundle) => (
          <li key={bundle.name}>
            {bundle.name}
            <span className="ml-4 text-sm text-gray-500">
              ({bundle.stats.total_pulls.toLocaleString()} pulls)
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
