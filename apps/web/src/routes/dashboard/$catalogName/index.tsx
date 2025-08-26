import {
  createFileRoute,
  Link,
  useParams,
  useSearch,
} from '@tanstack/react-router'
import { useItems } from '../../../hooks/useItems'

export const Route = createFileRoute('/dashboard/$catalogName/')({
  component: PackageListPage,
})

function PackageListPage() {
  const { catalogName } = useParams({ from: '/dashboard/$catalogName/' })
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

  const { items: packages } = data

  return (
    <div>
      <h2 className="text-2xl font-bold">
        Packages in <span className="text-accent">{catalogName}</span>
      </h2>
      <ul className="mt-4 list-disc pl-5 space-y-2">
        {packages.map((pkg) => (
          <li key={pkg.name}>
            <Link
              to="/dashboard/$catalogName/$packageName"
              params={{ catalogName, packageName: pkg.name }}
              search={true}
              className="text-blue-500 hover:underline"
            >
              {pkg.name}
            </Link>
            <span className="ml-4 text-sm text-gray-500">
              ({pkg.stats.total_pulls.toLocaleString()} pulls)
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
