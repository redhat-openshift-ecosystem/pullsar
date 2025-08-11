import { useNavigate, useSearch } from '@tanstack/react-router'

import { BookOpen, Package, Box, BarChart3 } from 'lucide-react'
import { SummaryStatsCard } from '../components/SummaryStatsCard'
import { ComparisonTutorial } from '../components/ComparisonTutorial'
import { OverallStatsCard } from '../components/OverallStatsCard'
import type { DateRange } from 'react-day-picker'
import { format } from 'date-fns'
import { useOcpVersions } from '../hooks/useOcpVersions'
import { useSummaryStats } from '../hooks/useSummaryStats'
import { useOverallPulls } from '../hooks/useOverallPulls'

export function HomePage() {
  const { ocp_version, start_date, end_date } = useSearch({ from: '/' })
  const navigate = useNavigate({ from: '/' })

  const { data: availableOcpVersions, isLoading: isLoadingOcpVersions } =
    useOcpVersions()
  const { data: summaryStatsData, isLoading: isLoadingSummaryStats } =
    useSummaryStats()
  const { data: overallData, isLoading: isLoadingOverallData } =
    useOverallPulls({
      ocp_version,
      start_date,
      end_date,
    })

  const handleOcpVersionChange = (version: string) => {
    navigate({
      search: (prev) => ({ ...prev, ocp_version: version }),
    })
  }

  const handleDateChange = (range: DateRange | undefined) => {
    if (!range || !range.from || !range.to) {
      return
    }

    const { from, to } = range
    navigate({
      search: (prev) => ({
        ...prev,
        start_date: format(from, 'yyyy-MM-dd'),
        end_date: format(to, 'yyyy-MM-dd'),
      }),
    })
  }

  return (
    <div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center pb-16 mt-15">
          <h1 className="text-5xl font-extrabold text-text-header sm:text-6xl md:text-7xl text-shadow-lg">
            Welcome to Pullsar
          </h1>
          <p className="mt-4 max-w-2xl mx-auto text-xl text-secondary">
            An automated tool for tracking and visualizing daily pull counts of
            OpenShift operators based on Quay.io logs
          </p>
        </div>
        <div className="grid grid-cols-2 xl:grid-cols-4 gap-6 pb-16">
          <SummaryStatsCard
            icon={BookOpen}
            iconColorClass="text-catalogs-icon"
            iconBackgroundColorClass="bg-bg-catalogs-icon/20"
            label="Catalogs Tracked"
            value={summaryStatsData?.total_catalogs}
            isLoading={isLoadingSummaryStats}
          />
          <SummaryStatsCard
            icon={Package}
            iconColorClass="text-packages-icon"
            iconBackgroundColorClass="bg-bg-packages-icon/20"
            label="Unique Packages"
            value={summaryStatsData?.total_packages}
            isLoading={isLoadingSummaryStats}
          />
          <SummaryStatsCard
            icon={Box}
            iconColorClass="text-bundles-icon"
            iconBackgroundColorClass="bg-bg-bundles-icon/20"
            label="Total Bundles"
            value={summaryStatsData?.total_bundles}
            isLoading={isLoadingSummaryStats}
          />
          <SummaryStatsCard
            icon={BarChart3}
            iconColorClass="text-pulls-icon"
            iconBackgroundColorClass="bg-bg-pulls-icon/20"
            label="Pulls Recorded"
            value={summaryStatsData?.total_pulls}
            isLoading={isLoadingSummaryStats}
          />
        </div>
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <main className="pb-16 -mt-8">
          <OverallStatsCard
            overallData={overallData}
            availableOcpVersions={availableOcpVersions ?? []}
            currentOcpVersion={ocp_version}
            currentDateRange={{ from: start_date, to: end_date }}
            handleOcpVersionChange={handleOcpVersionChange}
            handleDateChange={handleDateChange}
            isLoading={isLoadingOcpVersions || isLoadingOverallData}
          />
          <div className="mt-16">
            <ComparisonTutorial />
          </div>
        </main>
      </div>
    </div>
  )
}
