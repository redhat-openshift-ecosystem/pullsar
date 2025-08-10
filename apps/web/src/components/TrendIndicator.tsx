import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-react'

interface Props {
  trend?: number
}

export const TrendIndicator = ({ trend }: Props) => {
  if (!trend && trend !== 0)
    return (
      <span className="text-sm font-medium text-accent flex items-center">
        New Activity
      </span>
    )

  let color = 'text-trend-stable'
  let Icon = ArrowRight

  if (trend > 0) {
    color = 'text-trend-up'
    Icon = ArrowUpRight
  } else if (trend < 0) {
    color = 'text-trend-down'
    Icon = ArrowDownRight
  }

  return (
    <span
      className={`text-2xl lg:text-3xl font-bold flex items-center ${color}`}
    >
      <Icon className="w-8 h-8 mr-2" />
      {trend.toFixed(1)}%
    </span>
  )
}
