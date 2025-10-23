import { BarChart3 } from 'lucide-react'
import { Filters } from '../components/Filters'
import type { DateRange } from 'react-day-picker'
import { format } from 'date-fns'
import { useOcpVersions } from '../hooks/useOcpVersions'
import type { DashboardPageSearchParams } from '../lib/schemas'
import { Link, Outlet, useNavigate, useSearch } from '@tanstack/react-router'
import { useSortTypes } from '../hooks/useSortTypes'
import { CustomTooltip } from '../components/CustomTooltip'

export function DashboardPage() {
  const currentSearch: DashboardPageSearchParams = useSearch({
    from: '/dashboard',
  })
  const {
    ocp_version,
    start_date,
    end_date,
    search_query,
    sort_type,
    is_desc,
  } = currentSearch
  const navigate = useNavigate({ from: '/dashboard' })

  const { data: availableOcpVersions, isLoading: isLoadingOcpVersions } =
    useOcpVersions()

  const handleOcpVersionChange = (version: string) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({
        ...prev,
        ocp_version: version,
      }),
    })
  }

  const { data: availableSortTypes, isLoading: isLoadingSortTypes } =
    useSortTypes()

  const handleSortTypeChange = (type: string) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({
        ...prev,
        sort_type: type,
      }),
    })
  }

  const handleSortDirectionChange = (isDesc: boolean) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({
        ...prev,
        is_desc: isDesc,
      }),
    })
  }

  const handleDateChange = (range: DateRange | undefined) => {
    if (!range || !range.from || !range.to) {
      return
    }

    const { from, to } = range
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({
        ...prev,
        start_date: format(from, 'yyyy-MM-dd'),
        end_date: format(to, 'yyyy-MM-dd'),
      }),
    })
  }

  const handleSearchChange = (query: string) => {
    void navigate({
      search: (prev: DashboardPageSearchParams) => ({
        ...prev,
        search_query: query,
      }),
    })
  }

  const headerTooltipText = 'Go to Home page.'

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="flex text-left mb-5 md:mt-7">
        <BarChart3
          className={'w-15 h-15 sm:w-25 sm:h-25 mr-1 text-accent'}
          strokeWidth={1}
        />

        <CustomTooltip content={headerTooltipText}>
          <Link
            to="/"
            className="hover:cursor-pointer"
            search={() => ({
              ...currentSearch,
              search_query: undefined,
              sort_type: undefined,
              is_desc: undefined,
              page: undefined,
            })}
            aria-label={headerTooltipText}
          >
            <h1 className="text-2xl font-extrabold text-text-header sm:text-4xl md:text-5xl text-shadow-lg">
              Pullsar Dashboard
            </h1>
            <p className="sm:mt-4 max-w-2xl text-lg sm:text-2xl text-secondary">
              Operator Usage Overview
            </p>
          </Link>
        </CustomTooltip>
      </div>

      <Filters
        availableOcpVersions={availableOcpVersions ?? []}
        currentOcpVersion={ocp_version}
        currentDateRange={{ from: start_date, to: end_date }}
        currentSearchQuery={search_query}
        availableSortTypes={availableSortTypes ?? []}
        currentSortType={sort_type}
        isDesc={is_desc}
        handleOcpVersionChange={handleOcpVersionChange}
        handleDateChange={handleDateChange}
        handleSearchChange={handleSearchChange}
        handleSortTypeChange={handleSortTypeChange}
        handleSortDirectionChange={handleSortDirectionChange}
        isLoading={isLoadingOcpVersions || isLoadingSortTypes}
      />

      <Outlet />
    </div>
  )
}
