import { useMemo } from 'react'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import { useTheme } from '../contexts/theme-context'
import { formatDate } from '../lib/utils'

interface ChartPoint {
  date: string
  pulls: number
}

interface Series {
  name: string
  data: ChartPoint[]
}

interface Props {
  series: Series[]
  isComparison?: boolean
}

export const LINE_COLORS = [
  '#0284c7', // blue
  '#22c55e', // green
  '#ef4444', // red
  '#eab308', // yellow
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#14b8a6', // teal
  '#f97316', // orange
  '#84cc16', // lime
  '#06b6d4', // cyan
]

export const UsageLineChart = ({ series, isComparison = false }: Props) => {
  const { theme } = useTheme()

  // resolve colors manually as line charts don't support Tailwind classes
  const accent = theme === 'dark' ? '#818cf8' : '#0284c7' // --accent
  const secondary = theme === 'dark' ? '#9ca3af' : '#355188' // --secondary
  const toolTipBackground = theme === 'dark' ? '#1f293780' : '#ffffff80' // --bg-card / 50

  // transform data only when 'series' property changes
  const transformedData = useMemo(() => {
    const dataMap = new Map<string, Record<string, number | string>>()
    series.forEach((s) => {
      s.data.forEach((point) => {
        if (!dataMap.has(point.date)) {
          dataMap.set(point.date, { date: point.date })
        }
        dataMap.get(point.date)![s.name] = point.pulls
      })
    })
    return Array.from(dataMap.values()).sort(
      (a, b) =>
        new Date(a.date as string).getTime() -
        new Date(b.date as string).getTime()
    )
  }, [series])

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={transformedData}>
        <CartesianGrid vertical={false} stroke={secondary} strokeWidth={0.5} />
        <XAxis
          dataKey="date"
          fontSize={12}
          tickLine={false}
          stroke={secondary}
          dy={8}
          tickFormatter={formatDate}
        />
        <YAxis fontSize={12} tickLine={false} stroke={secondary} />
        <Tooltip
          contentStyle={{
            backdropFilter: 'blur(5px)',
            border: `1px solid ${secondary}`,
            borderRadius: '8px',
            backgroundColor: toolTipBackground,
          }}
        />

        {series.map((s, index) => (
          <Line
            key={s.name}
            type="monotone"
            dataKey={s.name}
            stroke={
              isComparison ? LINE_COLORS[index % LINE_COLORS.length] : accent
            }
            strokeWidth={2}
            dot={isComparison ? false : { r: 2, fill: accent }}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
