import { ArrowDownRight, ArrowRight, ArrowUpRight } from 'lucide-react'

interface Props {
  trend: number
  size?: 'sm' | 'lg'
}

export const TrendIndicator = ({ trend, size = 'lg' }: Props) => {
  let color = 'text-trend-stable'
  let Icon = ArrowRight

  if (trend > 0) {
    color = 'text-trend-up'
    Icon = ArrowUpRight
  } else if (trend < 0) {
    color = 'text-trend-down'
    Icon = ArrowDownRight
  }

  const sizeStyles = {
    sm: {
      text: 'text-md font-bold',
      icon: 'w-4 h-4 mr-1',
    },
    lg: {
      text: 'text-lg lg:text-xl font-bold',
      icon: 'w-8 h-8 mr-2',
    },
  }

  const styles = sizeStyles[size]

  return (
    <span className={`flex items-center ${color} ${styles.text}`}>
      <Icon className={styles.icon} />
      {trend > 0 ? '+' : ''}
      {trend.toFixed(1)}
    </span>
  )
}
