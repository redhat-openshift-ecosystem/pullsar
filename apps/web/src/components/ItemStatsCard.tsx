import { useState } from 'react'
import { useNavigate, useSearch } from '@tanstack/react-router'
import {
  ChevronDown,
  ChevronRight,
  MinusCircle,
  PlusCircle,
} from 'lucide-react'
import type { ListItem } from '../hooks/useItems'
import { UsageLineChart } from './UsageLineChart'
import { ItemStats } from './ItemStats'
import type { DashboardPageSearchParams } from '../lib/schemas'

interface Props {
  label: string
  item: ListItem
  linkTo?: string
  linkParams?: Record<string, string>
  isSelected?: boolean
  onSelectItem?: (item: ListItem) => void
}

export function ItemStatsCard({
  label,
  item,
  linkTo,
  linkParams,
  isSelected,
  onSelectItem,
}: Props) {
  const currentSearch: DashboardPageSearchParams = useSearch({
    from: '/dashboard',
  })

  const [isExpanded, setIsExpanded] = useState(false)
  const { name, stats } = item

  const navigate = useNavigate()

  const handleCardClick = () => {
    if (linkTo) {
      void navigate({
        to: linkTo,
        params: linkParams,
        search: () => {
          return {
            ...currentSearch,
            page: undefined,
            search_query: undefined,
          }
        },
      })
    }
  }

  const Title = () => (
    <h3 className="text-sm md:text-xl font-bold text-card-foreground">
      {label}
    </h3>
  )

  const WrapperComponent = linkTo ? 'button' : 'div'

  return (
    <WrapperComponent
      type={linkTo ? 'button' : undefined}
      onClick={linkTo ? handleCardClick : undefined}
      className={`bg-card/50 border border-border rounded-lg p-3 overflow-hidden w-full text-left
        ${isSelected && 'outline-3 outline-accent'} 
        ${linkTo && 'hover:cursor-pointer hover:outline-3 hover:outline-accent focus:outline-none focus-visible:ring-2'}`}
    >
      <div className="flex items-center gap-3">
        <div className="flex flex-grow items-center gap-2 min-w-0">
          <button
            onClick={(e) => {
              e.stopPropagation()
              setIsExpanded(!isExpanded)
            }}
            className="p-1 rounded-md hover:cursor-pointer self-center"
          >
            {isExpanded ? (
              <ChevronDown className="w-8 h-8 text-secondary" />
            ) : (
              <ChevronRight className="w-8 h-8 text-secondary" />
            )}
          </button>

          <div className="text-left">
            <Title />
            <div className="md:hidden mt-1">
              <ItemStats stats={stats} layout="mobile" />
            </div>
          </div>
        </div>

        <div className="flex flex-shrink-0 items-center gap-6">
          <div className="hidden md:flex text-right">
            <ItemStats stats={stats} layout="desktop" />
          </div>

          <button
            className={`p-2 rounded-full cursor-pointer
              ${isSelected ? 'bg-bg-remove hover:bg-bg-remove/80 text-trend-down' : 'bg-bg-add hover:bg-bg-add/60 text-accent'}`}
            onClick={(e) => {
              e.stopPropagation()
              if (onSelectItem) {
                onSelectItem(item)
              }
            }}
          >
            {isSelected ? (
              <MinusCircle className="w-8 h-8 md:w-10 md:h-10" />
            ) : (
              <PlusCircle className="w-8 h-8 md:w-10 md:h-10" />
            )}
          </button>
        </div>
      </div>

      {isExpanded && (
        <div id={`chart-${name}`} className="border-t border-border mt-3 pt-4">
          <div className="w-full h-48" onClick={(e) => e.stopPropagation()}>
            <UsageLineChart
              series={[{ name: label, data: stats.chart_data }]}
            />
          </div>
        </div>
      )}
    </WrapperComponent>
  )
}
