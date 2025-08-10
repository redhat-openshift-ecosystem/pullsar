import { useNavigate, useSearch } from '@tanstack/react-router'

import { BookOpen, Package, Box, BarChart3 } from 'lucide-react'
import { SummaryStatsCard } from '../components/SummaryStatsCard'
import { ComparisonTutorial } from '../components/ComparisonTutorial'
import { OverallStatsCard } from '../components/OverallStatsCard'
import type { DateRange } from 'react-day-picker'
import { format } from 'date-fns'

const mockOverallData = {
  total_pulls: 123456,
  trend: 15.2,
  chart_data: Array.from({ length: 10 }, (_, i) => ({
    date: `Day ${i + 1}`,
    pulls: 1000 + i * 50 + Math.floor(Math.random() * 200),
  })),
}

export function HomePage() {
  const { ocp_version, start_date, end_date } = useSearch({ from: '/' })
  const navigate = useNavigate({ from: '/' })

  const availableOcpVersions = ['v4.18', 'v4.17', 'v4.16']

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
            value={4}
          />
          <SummaryStatsCard
            icon={Package}
            iconColorClass="text-packages-icon"
            iconBackgroundColorClass="bg-bg-packages-icon/20"
            label="Unique Packages"
            value={284}
          />
          <SummaryStatsCard
            icon={Box}
            iconColorClass="text-bundles-icon"
            iconBackgroundColorClass="bg-bg-bundles-icon/20"
            label="Total Bundles"
            value={3974}
          />
          <SummaryStatsCard
            icon={BarChart3}
            iconColorClass="text-pulls-icon"
            iconBackgroundColorClass="bg-bg-pulls-icon/20"
            label="Pulls Recorded"
            value={999999}
          />
        </div>
      </div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <main className="pb-16 -mt-8">
          <div>
            <OverallStatsCard
              totalPulls={mockOverallData.total_pulls}
              trend={mockOverallData.trend}
              chartData={mockOverallData.chart_data}
              availableOcpVersions={availableOcpVersions}
              currentOcpVersion={ocp_version}
              currentDateRange={{ from: start_date, to: end_date }}
              handleOcpVersionChange={handleOcpVersionChange}
              handleDateChange={handleDateChange}
            />
          </div>
          <div className="mt-16">
            <ComparisonTutorial />
          </div>
        </main>
      </div>
    </div>
  )
}
