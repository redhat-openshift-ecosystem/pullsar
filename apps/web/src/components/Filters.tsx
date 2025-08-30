import type { DateRange } from 'react-day-picker'
import { OcpVersionSelector } from './OcpVersionSelector'
import { DateRangeSelector } from './DateRangeSelector'
import SearchBar from './SearchBar'
import { SortSelector } from './SortSelector'
import { Button } from './ui/button'
import { Funnel } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { Skeleton } from './ui/skeleton'
import { useParams, useSearch } from '@tanstack/react-router'
import { useExportCsv } from '../hooks/useExportCsv'
import { differenceInDays, parseISO } from 'date-fns'
import { ExportButton } from './ExportButton'
import { EXPORT_MAX_DAYS } from '../lib/utils'

interface Props {
  availableOcpVersions: string[]
  currentOcpVersion: string
  currentDateRange: { from?: string; to?: string }
  currentSearchQuery: string
  availableSortTypes: string[]
  currentSortType: string
  isDesc: boolean
  handleOcpVersionChange: (version: string) => void
  handleDateChange: (range: DateRange | undefined) => void
  handleSearchChange: (query: string) => void
  handleSortTypeChange: (type: string) => void
  handleSortDirectionChange: (isDesc: boolean) => void
  isLoading?: boolean
}

export const Filters = ({
  availableOcpVersions,
  currentOcpVersion,
  currentDateRange,
  currentSearchQuery,
  availableSortTypes,
  currentSortType,
  isDesc,
  handleOcpVersionChange,
  handleDateChange,
  handleSearchChange,
  handleSortTypeChange,
  handleSortDirectionChange,
  isLoading,
}: Props) => {
  const [isExpanded, setIsExpanded] = useState(false)
  const [exportPerformed, setExportPerformed] = useState(false)

  const search = useSearch({ from: '/dashboard' })
  const params = useParams({ strict: false })

  const { exportData, isExporting } = useExportCsv(() =>
    setExportPerformed(true)
  )

  useEffect(() => {
    setExportPerformed(false)
  }, [search, params])

  const isExportMaxExceeded = useMemo(() => {
    const from = search.start_date ? parseISO(search.start_date) : null
    const to = search.end_date ? parseISO(search.end_date) : null
    if (!from || !to) return false
    return differenceInDays(to, from) > EXPORT_MAX_DAYS
  }, [search.start_date, search.end_date])

  if (
    isLoading ||
    availableOcpVersions.length === 0 ||
    availableSortTypes.length === 0
  ) {
    return getLoadingSkeleton()
  }

  return (
    <div className="sticky top-2 z-10 bg-card/95 border border-border rounded-lg p-3 overflow-hidden text-left">
      <div className="flex flex-col lg:flex-row lg:items-center lg:gap-4">
        <div className="flex items-center gap-2 w-full lg:flex-1">
          <SearchBar
            placeholder="Filter by name..."
            currentQuery={currentSearchQuery}
            onSearchSubmit={handleSearchChange}
          />
          <div className="hidden sm:block lg:w-auto">
            <DateRangeSelector
              dateRange={currentDateRange}
              onDateChange={handleDateChange}
            />
          </div>
          <Button
            className={`lg:hidden flex self-end ${isExpanded && 'bg-bg-active text-text-header'}`}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <Funnel strokeWidth={3} />
          </Button>
        </div>

        {/* mobile - vertical section expanded/hidden with 'funnel' button, 
            desktop - lg:flex makes sure items are always visible
            on big screen and the layout becomes horizontal */}
        <div
          className={`
            ${isExpanded ? 'flex' : 'hidden'} flex-col gap-4 mt-4
            lg:mt-0 lg:flex lg:flex-row lg:items-center lg:gap-4
          `}
        >
          <div className="w-full sm:hidden">
            <DateRangeSelector
              dateRange={currentDateRange}
              onDateChange={handleDateChange}
            />
          </div>
          <div className="flex gap-4 w-full lg:w-auto">
            <div className="flex-1">
              <OcpVersionSelector
                versions={availableOcpVersions}
                currentVersion={currentOcpVersion}
                onVersionChange={handleOcpVersionChange}
              />
            </div>
            <div className="flex-1">
              <SortSelector
                types={availableSortTypes}
                currentType={currentSortType}
                isDesc={isDesc}
                onTypeChange={handleSortTypeChange}
                onDirectionChange={handleSortDirectionChange}
              />
            </div>
          </div>
          <ExportButton
            onClick={() => exportData(search)}
            isExportMaxExceeded={isExportMaxExceeded}
            isExporting={isExporting}
            isDone={exportPerformed}
          />
        </div>
      </div>
    </div>
  )
}

const getLoadingSkeleton = () => {
  return (
    <div className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden text-left">
      <div className="flex flex-col lg:flex-row lg:items-center lg:gap-4">
        <div className="flex items-center gap-2 w-full lg:flex-1">
          <Skeleton className="h-9 w-full" />
          <Skeleton className="hidden sm:block h-9 w-56" />
          <Skeleton className="lg:hidden h-9 w-9 flex-shrink-0" />
        </div>
        <div className="hidden lg:flex lg:items-center lg:gap-4">
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-9 w-48" />
          <Skeleton className="h-9 w-40" />
        </div>
      </div>
    </div>
  )
}
