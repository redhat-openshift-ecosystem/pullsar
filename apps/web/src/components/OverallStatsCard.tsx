import { ChevronsRight } from 'lucide-react'
import { TrendIndicator } from './TrendIndicator'
import { UsageLineChart } from './UsageLineChart'
import { OcpVersionSelector } from './OcpVersionSelector'
import type { DateRange } from 'react-day-picker'
import { DateRangeSelector } from './DateRangeSelector'
import { useNavigate } from '@tanstack/react-router'

interface Props {
  totalPulls: number
  trend: number
  chartData: {
    date: string
    pulls: number
  }[]
  availableOcpVersions: string[]
  currentOcpVersion: string
  currentDateRange: { from?: string; to?: string }
  handleOcpVersionChange: (version: string) => void
  handleDateChange: (range: DateRange | undefined) => void
}

export const OverallStatsCard = ({
  totalPulls,
  trend,
  chartData,
  availableOcpVersions,
  currentOcpVersion,
  currentDateRange,
  handleOcpVersionChange,
  handleDateChange,
}: Props) => {
  const navigate = useNavigate()

  const handleCardClick = () => {
    navigate({ to: '/dashboard' })
  }

  return (
    <div className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-4">
        <div onClick={handleCardClick} className="hover:cursor-pointer hover:">
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
            <p className="text-3xl lg:text-5xl font-bold text-accent">
              {totalPulls.toLocaleString()}
            </p>
            <p className="text-sm text-secondary">Total Pulls</p>
          </div>
          <div>
            <TrendIndicator trend={trend} />
            <p className="text-sm text-secondary">Trend</p>
          </div>
        </div>
        <div className="w-full flex-grow h-48">
          <UsageLineChart chartData={chartData} />
        </div>
      </div>
    </div>
  )
}
