import { ArrowDownRight, ArrowUpRight } from 'lucide-react'

interface Props {
  trend: number
}

export const TrendIndicator = ({ trend }: Props) => {
  if (trend === Infinity)
    return (
      <span className="text-sm font-medium text-accent flex items-center">
        New Activity
      </span>
    )
  if (trend === 0)
    return (
      <span className="text-sm font-medium text-secondary flex items-center">
        Stable
      </span>
    )
  const isPositive = trend >= 0
  const color = isPositive ? 'text-trend-up' : 'text-trend-down'
  const Icon = isPositive ? ArrowUpRight : ArrowDownRight

  return (
    <span
      className={`text-2xl lg:text-3xl font-bold flex items-center ${color}`}
    >
      <Icon className="w-8 h-8 mr-2" />
      {isPositive ? '+' : ''}
      {trend.toFixed(1)}%
    </span>
  )
}
