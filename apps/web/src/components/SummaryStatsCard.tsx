import type { LucideIcon } from 'lucide-react'

interface Props {
  icon: LucideIcon
  iconColorClass: string
  iconBackgroundColorClass: string
  label: string
  value: number
}

export const SummaryStatsCard = ({
  icon: Icon,
  iconColorClass,
  iconBackgroundColorClass,
  label,
  value,
}: Props) => (
  <div className="flex bg-card/50 border border-border rounded-lg items-center p-4 sm:p-6 space-x-3 overflow-hidden">
    <div
      className={`hidden sm:flex p-3 rounded-full ${iconBackgroundColorClass} ${iconColorClass}`}
    >
      <Icon className={'w-8 h-8'} />
    </div>
    <div className="hidden sm:block">
      <p className="text-3xl font-bold text-summary-accent">
        {value.toLocaleString()}
      </p>
      <p className="text-secondary">{label}</p>
    </div>

    <div className="sm:hidden w-full">
      <p className="text-2xl font-bold text-summary-accent truncate">
        {value.toLocaleString()}
      </p>
      <div className="flex items-center justify-center space-x-2 mt-1">
        <div
          className={`p-1 rounded-full ${iconBackgroundColorClass} ${iconColorClass}`}
        >
          <Icon className={'w-4 h-4'} />
        </div>
        <p className="text-sm text-secondary">{label}</p>
      </div>
    </div>
  </div>
)
