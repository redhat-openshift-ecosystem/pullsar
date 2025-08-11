import {
  BarChart3,
  BookOpen,
  Box,
  Package,
  type LucideIcon,
} from 'lucide-react'
import { Skeleton } from './ui/skeleton'

interface Props {
  icon: LucideIcon
  iconColorClass: string
  iconBackgroundColorClass: string
  label: string
  value?: number
  isLoading?: boolean
}

interface MinProps {
  value?: number
  isLoading?: boolean
}

export const SummaryStatsCard = ({
  icon: Icon,
  iconColorClass,
  iconBackgroundColorClass,
  label,
  value,
  isLoading,
}: Props) => {
  if (isLoading || value === undefined) {
    return loadingSkeleton()
  }

  return (
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
}

const loadingSkeleton = () => {
  return (
    <div className="flex bg-card/50 border border-border rounded-lg items-center p-4 sm:p-6 space-x-3 overflow-hidden">
      <div className="hidden sm:flex items-center space-x-3">
        <Skeleton className="w-14 h-14 rounded-full" />
        <div className="space-y-2">
          <Skeleton className="h-8 w-24" />
          <Skeleton className="h-4 w-32" />
        </div>
      </div>
      <div className="sm:hidden w-full">
        <Skeleton className="h-8 w-3/4" />
        <div className="flex items-center space-x-2 mt-2">
          <Skeleton className="w-6 h-6 rounded-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    </div>
  )
}

export const CatalogsSummaryStatsCard = ({ value, isLoading }: MinProps) => (
  <SummaryStatsCard
    icon={BookOpen}
    iconColorClass="text-catalogs-icon"
    iconBackgroundColorClass="bg-bg-catalogs-icon/20"
    label="Catalogs Tracked"
    value={value}
    isLoading={isLoading}
  />
)

export const PackagesSummaryStatsCard = ({ value, isLoading }: MinProps) => (
  <SummaryStatsCard
    icon={Package}
    iconColorClass="text-packages-icon"
    iconBackgroundColorClass="bg-bg-packages-icon/20"
    label="Unique Packages"
    value={value}
    isLoading={isLoading}
  />
)

export const BundlesSummaryStatsCard = ({ value, isLoading }: MinProps) => (
  <SummaryStatsCard
    icon={Box}
    iconColorClass="text-bundles-icon"
    iconBackgroundColorClass="bg-bg-bundles-icon/20"
    label="Total Bundles"
    value={value}
    isLoading={isLoading}
  />
)

export const PullsSummaryStatsCard = ({ value, isLoading }: MinProps) => (
  <SummaryStatsCard
    icon={BarChart3}
    iconColorClass="text-pulls-icon"
    iconBackgroundColorClass="bg-bg-pulls-icon/20"
    label="Pulls Recorded"
    value={value}
    isLoading={isLoading}
  />
)
