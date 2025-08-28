import { useNavigate, useSearch } from '@tanstack/react-router'
import { useItems, type Params, type ListItem } from '../hooks/useItems'
import CustomPagination from './CustomPagination'
import { BreadcrumbNav } from './BreadcrumbNav'
import { Skeleton } from './ui/skeleton'
import type { DashboardPageSearchParams } from '../lib/schemas'

interface Breadcrumb {
  to: string
  label: string
  params?: Record<string, string>
}

interface Props {
  breadcrumbs: Breadcrumb[]
  renderItem: (item: ListItem) => React.ReactNode
  pathParams?: {
    catalog_name?: string
    package_name?: string
  }
}

export function ItemList({ breadcrumbs, renderItem, pathParams }: Props) {
  const navigate = useNavigate({ from: '/dashboard' })
  const searchParams: DashboardPageSearchParams = useSearch({
    from: '/dashboard',
  })

  const useItemsParams: Params = {
    ...searchParams,
    ...pathParams,
  }

  const { data, isLoading } = useItems(useItemsParams)

  const handlePageChange = (newPage: number) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({ ...prev, page: newPage }),
    })
  }

  if (isLoading || !data) {
    return getLoadingSkeleton()
  }

  const { items, total_count, page_size } = data
  const totalPages = Math.ceil(total_count / page_size)

  return (
    <div className="mt-15 flex flex-col">
      <BreadcrumbNav breadcrumbs={breadcrumbs} />

      <div className="flex flex-col gap-4">
        {items.map((item) => (
          <div key={item.name}>{renderItem(item)}</div>
        ))}
      </div>

      {items.length === 0 && (
        <p className="mt-4 self-center font-bold">No items found.</p>
      )}

      {totalPages > 1 && (
        <div className="mt-8 self-end">
          <CustomPagination
            pagination={{
              page: useItemsParams.page,
              totalPages,
              totalCount: total_count,
            }}
            handlePageChange={handlePageChange}
          />
        </div>
      )}
    </div>
  )
}

function getLoadingSkeleton() {
  return (
    <div className="mt-15 flex flex-col">
      <Skeleton className="h-7 w-2/3 md:w-1/3 mb-4 rounded" />

      <div className="flex flex-col gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-20 w-full rounded-lg" />
        ))}
      </div>

      <Skeleton className="h-9 w-64 mt-8 self-end rounded" />
    </div>
  )
}
