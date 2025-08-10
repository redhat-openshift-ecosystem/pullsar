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

interface Props {
  chartData: {
    date: string
    pulls: number
  }[]
}

export const UsageLineChart = ({ chartData }: Props) => {
  const { theme } = useTheme()

  // resolve colors manually as line charts don't support Tailwind classes
  const accent = theme === 'dark' ? '#818cf8' : '#0284c7' // --accent
  const secondary = theme === 'dark' ? '#9ca3af' : '#355188' // --secondary
  const toolTipBackground = theme === 'dark' ? '#1f293780' : '#ffffff80' // --bg-card / 50

  return (
    <ResponsiveContainer width="100%" height="100%">
      <LineChart data={chartData}>
        <CartesianGrid vertical={false} stroke={secondary} strokeWidth={0.5} />
        <XAxis
          dataKey="date"
          fontSize={12}
          tickLine={false}
          stroke={secondary}
          dy={8}
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
        <Line
          type="monotone"
          dataKey="pulls"
          stroke={accent}
          strokeWidth={2}
          dot={{ r: 2, fill: accent }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
