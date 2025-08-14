import type { DateRange } from 'react-day-picker'
import { OcpVersionSelector } from './OcpVersionSelector'
import { DateRangeSelector } from './DateRangeSelector'
import SearchBar from './SearchBar'

interface Props {
  availableOcpVersions: string[]
  currentOcpVersion: string
  currentDateRange: { from?: string; to?: string }
  handleOcpVersionChange: (version: string) => void
  handleDateChange: (range: DateRange | undefined) => void
  isLoading?: boolean
}

export const Filters = ({
  availableOcpVersions,
  currentOcpVersion,
  currentDateRange,
  handleOcpVersionChange,
  handleDateChange,
  isLoading,
}: Props) => {
  return (
    <div className="bg-card/50 border border-border rounded-lg p-3 overflow-hidden flex items-center space-x-4 text-left">
      <OcpVersionSelector
        versions={availableOcpVersions}
        currentVersion={currentOcpVersion}
        onVersionChange={handleOcpVersionChange}
      />
      <DateRangeSelector
        dateRange={currentDateRange}
        onDateChange={handleDateChange}
      />
      <SearchBar placeholder='Search catalogs, packages, bundles...' />
    </div>
  )
}
