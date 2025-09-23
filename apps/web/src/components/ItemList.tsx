import { useNavigate, useSearch } from '@tanstack/react-router'
import { useItems, type Params, type ListItem } from '../hooks/useItems'
import CustomPagination from './CustomPagination'
import { BreadcrumbNav } from './BreadcrumbNav'
import { Skeleton } from './ui/skeleton'
import type { DashboardPageSearchParams } from '../lib/schemas'
import {
  cloneElement,
  Fragment,
  useMemo,
  useState,
  type ReactElement,
} from 'react'
import { ComparisonTray } from './ComparisonTray'
import { ChevronUp } from 'lucide-react'

interface ItemCardPropsToInject {
  isSelected?: boolean
  onSelectItem?: (item: ListItem) => void
}

interface Breadcrumb {
  to: string
  label: string
  params?: Record<string, string>
}

interface Props {
  breadcrumbs: Breadcrumb[]
  renderItem: (item: ListItem) => ReactElement<ItemCardPropsToInject>
  pathParams?: {
    catalog_name?: string
    package_name?: string
  }
  extraItem?: ListItem
  isExtraItemLoading?: boolean
}

export function ItemList({
  breadcrumbs,
  renderItem,
  pathParams,
  extraItem,
  isExtraItemLoading,
}: Props) {
  const navigate = useNavigate({ from: '/dashboard' })
  const searchParams: DashboardPageSearchParams = useSearch({
    from: '/dashboard',
  })

  const useItemsParams: Params = {
    ...searchParams,
    ...pathParams,
  }

  const { data, isLoading } = useItems(useItemsParams)
  const [selectedItems, setSelectedItems] = useState<ListItem[]>([])
  const [isTrayOpen, setIsTrayOpen] = useState(false)

  const combinedItems = useMemo(() => {
    const baseItems = data?.items || []
    if (extraItem) {
      return [extraItem, ...baseItems]
    }
    return baseItems
  }, [data, extraItem])

  const handlePageChange = (newPage: number) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({ ...prev, page: newPage }),
    })
  }

  if (isLoading || !data || isExtraItemLoading) {
    return getLoadingSkeleton()
  }

  const { items, total_count, page_size } = data
  const totalPages = Math.ceil((total_count + (extraItem ? 1 : 0)) / page_size)

  const handleSelectItem = (itemToToggle: ListItem) => {
    setSelectedItems((currentSelected) => {
      const isAlreadySelected = currentSelected.some(
        (item) => item.name === itemToToggle.name
      )
      if (isAlreadySelected) {
        return currentSelected.filter((item) => item.name !== itemToToggle.name)
      }
      return [...currentSelected, itemToToggle]
    })
  }

  return (
    <div className="my-6 md:my-12 flex flex-col gap-6">
      <BreadcrumbNav breadcrumbs={breadcrumbs} isInteractive={true} />

      {/* mobile - pagination on top of list on the left */}
      {totalPages > 1 && (
        <div className="self-start flex lg:hidden">
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

      <div className="flex flex-col gap-4 mb-10 lg:mb-4">
        {combinedItems.map((item, index) => {
          const isSelected = selectedItems.some(
            (selected) => selected.name === item.name
          )
          const itemCard = renderItem(item)
          return (
            <Fragment key={item.name}>
              {cloneElement(itemCard, {
                isSelected,
                onSelectItem: handleSelectItem,
              })}
              {extraItem && index === 0 && (
                <hr className="border-accent border-1" />
              )}
            </Fragment>
          )
        })}
      </div>

      {items.length === 0 && (
        <p className="self-center font-bold">No items found.</p>
      )}

      {/* desktop - pagination below list on the right */}
      {totalPages > 1 && (
        <div className="self-end hidden lg:flex">
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

      {selectedItems.length > 0 && (
        <div className="fixed bottom-0 lg:bottom-2 left-1/2 -translate-x-1/2 z-30 w-full lg:w-fit">
          <button
            onClick={() => setIsTrayOpen(true)}
            className={`flex flex-col items-center text-center text-secondary hover:text-accent
              hover:cursor-pointer transition-colors rounded-t-xl lg:rounded-b-xl border
              border-border border-b-0 lg:border-b-1 bg-bg-comparison/95 w-full
              `}
          >
            <div className="flex flex-col items-center p-2">
              <ChevronUp className="w-10 h-10" />
              <span className="font-semibold">
                Show Comparison ({selectedItems.length})
              </span>
            </div>
          </button>
        </div>
      )}

      {isTrayOpen && (
        <ComparisonTray
          items={selectedItems}
          breadcrumbs={breadcrumbs}
          onItemRemove={handleSelectItem}
          onClose={() => setIsTrayOpen(false)}
          onClearAll={() => setSelectedItems([])}
        />
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
