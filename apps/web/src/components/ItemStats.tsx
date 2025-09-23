import type { ListItem } from '../hooks/useItems'
import { TrendIndicator } from './TrendIndicator'

export const ItemStats = ({
  stats,
  layout,
}: {
  stats: ListItem['stats']
  layout: 'mobile' | 'desktop'
}) => {
  if (layout === 'mobile') {
    return (
      <div className="flex items-center gap-2">
        <p className="text-sm text-secondary">Pulls:</p>
        <p className="text-lg font-bold text-accent">
          {stats.total_pulls.toLocaleString()}
        </p>
        <TrendIndicator trend={stats.trend} size="sm" />
      </div>
    )
  }

  return (
    <div className="flex items-center gap-6 text-right">
      <div className="flex flex-col items-center">
        <p className="text-2xl lg:text-3xl font-bold text-accent">
          {stats.total_pulls.toLocaleString()}
        </p>
        <p className="text-xs text-secondary">Total Pulls</p>
      </div>
      <div className="flex flex-col items-center">
        <TrendIndicator trend={stats.trend} size="sm" />
        <p className="text-xs text-secondary">Trend</p>
      </div>
    </div>
  )
}
