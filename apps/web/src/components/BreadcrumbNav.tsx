import { Link } from '@tanstack/react-router'
import { ChevronsRight, ArrowLeft, Home, BookOpen, Package } from 'lucide-react'
import { Button } from './ui/button'

const BREADCRUMB_ICONS = [Home, BookOpen, Package]

interface Breadcrumb {
  to: string
  label: string
  params?: Record<string, string>
}

interface Props {
  breadcrumbs: Breadcrumb[]
}

export function BreadcrumbNav({ breadcrumbs }: Props) {
  const size = breadcrumbs.length
  if (size === 0) {
    return null
  }

  const lastCrumb = breadcrumbs[size - 1]
  const secondToLastCrumb = size > 1 ? breadcrumbs[size - 2] : null
  const LastIcon = BREADCRUMB_ICONS[size - 1]

  return (
    <div className="text-sm md:text-lg font-bold text-text-header mb-4">
      {/* mobile - display only last item of the breadcrumbs and 'back' button */}
      <div className="md:hidden flex justify-between items-center">
        <div className="flex items-center gap-2 text-accent truncate">
          {LastIcon && <LastIcon className="w-5 h-5 flex-shrink-0" />}
          <span className="truncate">{lastCrumb.label}</span>
        </div>

        {secondToLastCrumb && (
          <Link to={secondToLastCrumb.to} params={secondToLastCrumb.params}>
            <Button size="sm" className="font-bold">
              <ArrowLeft className="w-4 h-4" strokeWidth={3} />
              Back
            </Button>
          </Link>
        )}
      </div>

      {/* desktop - display all breadcrumbs */}
      <div className="hidden md:flex items-center gap-2">
        {breadcrumbs.map((crumb, index) => {
          const isLast = index === size - 1
          const Icon = BREADCRUMB_ICONS[index]

          return (
            <div
              key={crumb.to}
              className="flex items-center gap-2 text-secondary"
            >
              <Link
                to={crumb.to}
                params={crumb.params}
                className={`hover:cursor-pointer hover:text-accent ${
                  isLast ? 'text-accent pointer-events-none' : ''
                }`}
              >
                <span className="flex items-center gap-2">
                  {Icon && <Icon className="w-5 h-5" />}
                  {crumb.label}
                </span>
              </Link>
              {!isLast && <ChevronsRight className="w-5 h-5" />}
            </div>
          )
        })}
      </div>
    </div>
  )
}
