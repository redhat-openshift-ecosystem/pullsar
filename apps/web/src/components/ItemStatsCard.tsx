import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import {
  ChevronDown,
  ChevronRight,
  MinusCircle,
  PlusCircle,
} from 'lucide-react'
import type { ListItem } from '../hooks/useItems'
import { UsageLineChart } from './UsageLineChart'
import { ItemStats } from './ItemStats'

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
  const [isExpanded, setIsExpanded] = useState(false)
  const { name, stats } = item

  const navigate = useNavigate()

  const handleCardClick = () => {
    if (linkTo) {
      void navigate({ to: linkTo, params: linkParams })
    }
  }

  const Title = () => (
    <h3 className="text-sm md:text-xl font-bold text-card-foreground">
      {label}
    </h3>
  )

  return (
    <div
      className={`bg-card/50 border border-border rounded-lg p-3 overflow-hidden
        ${isSelected && 'outline-3 outline-accent'} ${linkTo && 'hover:cursor-pointer hover:outline-3 hover:outline-accent'}`}
      onClick={handleCardClick}
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
              onSelectItem && onSelectItem(item)
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
    </div>
  )
}
