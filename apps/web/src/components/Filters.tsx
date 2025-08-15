import type { DateRange } from 'react-day-picker'
import { OcpVersionSelector } from './OcpVersionSelector'
import { DateRangeSelector } from './DateRangeSelector'
import SearchBar from './SearchBar'
import { SortSelector } from './SortSelector'
import { Button } from './ui/button'
import { Download, Funnel } from 'lucide-react'
import { useState } from 'react'
import { Skeleton } from './ui/skeleton'

interface Props {
  availableOcpVersions: string[]
  currentOcpVersion: string
  currentDateRange: { from?: string; to?: string }
  availableSortTypes: string[]
  currentSortType: string
  isDesc: boolean
  handleOcpVersionChange: (version: string) => void
  handleDateChange: (range: DateRange | undefined) => void
  handleSortTypeChange: (type: string) => void
  handleSortDirectionChange: (isDesc: boolean) => void
  isLoading?: boolean
}

export const Filters = ({
  availableOcpVersions,
  currentOcpVersion,
  currentDateRange,
  availableSortTypes,
  currentSortType,
  isDesc,
  handleOcpVersionChange,
  handleDateChange,
  handleSortTypeChange,
  handleSortDirectionChange,
  isLoading,
}: Props) => {
  const [isExpanded, setIsExpanded] = useState(false)

  if (isLoading || !availableOcpVersions || !availableSortTypes) {
    return getLoadingSkeleton()
  }

  return (
    <div className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden text-left">
      <div className="flex flex-col lg:flex-row lg:items-center lg:gap-4">
        <div className="flex items-center gap-2 w-full lg:flex-1">
          <SearchBar placeholder="Search catalogs, packages, bundles..." />
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
          <Button className="font-bold w-full sm:w-auto lg:self-end">
            <Download strokeWidth={3} className="mr-2 h-4 w-4" /> Export as CSV
          </Button>
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
