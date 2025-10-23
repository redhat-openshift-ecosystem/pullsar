import { ChevronsRight } from 'lucide-react'
import { TrendIndicator } from './TrendIndicator'
import { UsageLineChart } from './UsageLineChart'
import { OcpVersionSelector } from './OcpVersionSelector'
import type { DateRange } from 'react-day-picker'
import { DateRangeSelector } from './DateRangeSelector'
import { useNavigate } from '@tanstack/react-router'
import { Skeleton } from './ui/skeleton'

interface Props {
  overallData?: {
    total_pulls: number
    trend: number
    chart_data: {
      date: string
      pulls: number
    }[]
  }
  availableOcpVersions: string[]
  currentOcpVersion: string
  currentDateRange: { from?: string; to?: string }
  handleOcpVersionChange: (version: string) => void
  handleDateChange: (range: DateRange | undefined) => void
  isLoading?: boolean
}

export const OverallStatsCard = ({
  overallData,
  availableOcpVersions,
  currentOcpVersion,
  currentDateRange,
  handleOcpVersionChange,
  handleDateChange,
  isLoading,
}: Props) => {
  const navigate = useNavigate()

  const handleCardClick = () => {
    void navigate({ to: '/dashboard', search: true })
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleCardClick()
    }
  }

  if (isLoading || overallData === undefined) {
    return loadingSkeleton()
  }

  const { total_pulls, trend, chart_data } = overallData

  return (
    <div
      role="button"
      tabIndex={0}
      className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden hover:cursor-pointer w-full text-left"
      onClick={handleCardClick}
      onKeyDown={handleKeyDown}
      aria-label="Go to operator usage dashboard."
    >
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
        <div>
          <h3 className="text-2xl font-bold text-summary-accent flex items-center">
            All Operators Usage
            <ChevronsRight className="w-6 h-6 ml-2" />
          </h3>
          <p className="text-secondary text-left">
            Click to see individual catalogs, packages and bundles
          </p>
        </div>
        <div className="flex items-center space-x-4 mt-4 md:mt-0 text-left">
          <OcpVersionSelector
            versions={availableOcpVersions}
            currentVersion={currentOcpVersion}
            onVersionChange={handleOcpVersionChange}
          />
          <DateRangeSelector
            dateRange={currentDateRange}
            onDateChange={handleDateChange}
          />
        </div>
      </div>
      <div className="border-t border-border pt-4 flex flex-col md:flex-row items-center gap-6">
        <div className="flex-shrink-0 grid grid-cols-2 gap-6 text-center">
          <div>
            <p className="text-3xl lg:text-4xl font-bold text-accent">
              {total_pulls.toLocaleString()}
            </p>
            <p className="text-sm text-secondary">Total Pulls</p>
          </div>
          <div className="flex flex-col items-center">
            <TrendIndicator trend={trend} />
            <p className="text-sm text-secondary">Trend</p>
          </div>
        </div>
        <div
          className="w-full flex-grow h-48"
          onClick={(e) => e.stopPropagation()}
        >
          <UsageLineChart series={[{ name: 'Pulls', data: chart_data }]} />
        </div>
      </div>
    </div>
  )
}

const loadingSkeleton = () => {
  return (
    <div className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
        <div>
          <Skeleton className="h-8 w-64 mb-2" />
          <Skeleton className="h-4 w-80" />
        </div>
        <div className="flex items-center space-x-4 mt-4 md:mt-0">
          <div className="space-y-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-10 w-44" />
          </div>
          <div className="space-y-1">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-10 w-56" />
          </div>
        </div>
      </div>
      <div className="border-t border-border pt-4 flex flex-col md:flex-row items-center gap-6">
        <div className="flex-shrink-0 grid grid-cols-2 gap-6 text-center">
          <div>
            <Skeleton className="h-12 w-32 mb-2" />
            <Skeleton className="h-4 w-20" />
          </div>
          <div>
            <Skeleton className="h-12 w-24 mb-2" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
        <div className="w-full flex-grow h-48">
          <Skeleton className="h-full w-full" />
        </div>
      </div>
    </div>
  )
}
