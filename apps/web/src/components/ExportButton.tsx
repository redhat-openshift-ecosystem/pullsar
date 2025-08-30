import { EXPORT_MAX_DAYS } from '../lib/utils'
import { Button } from './ui/button'
import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip'
import { Download } from 'lucide-react'

interface Props {
  onClick: () => void
  isExportMaxExceeded: boolean
  isExporting: boolean
  isDone: boolean
}

export function ExportButton({
  onClick,
  isExportMaxExceeded,
  isExporting,
  isDone,
}: Props) {
  const buttonContent = (
    <>
      <Download strokeWidth={3} className="mr-2 h-4 w-4" />
      {isExporting ? 'Exporting...' : 'Export as CSV'}
    </>
  )

  const getTooltipMessage = () => {
    if (isExportMaxExceeded) {
      return `Range exceeds ${EXPORT_MAX_DAYS} days.`
    }
    if (isDone) {
      return 'Change filters to export again.'
    }
    if (isExporting) {
      return 'Export in progress...'
    }
    return ''
  }

  if (isExportMaxExceeded || isExporting || isDone) {
    return (
      <Tooltip>
        <TooltipTrigger asChild>
          <div className="w-full sm:w-auto lg:self-end">
            <Button className="font-bold w-full sm:w-auto lg:self-end" disabled>
              {buttonContent}
            </Button>
          </div>
        </TooltipTrigger>
        <TooltipContent>
          <p>{getTooltipMessage()}</p>
        </TooltipContent>
      </Tooltip>
    )
  }

  return (
    <Button
      className="font-bold w-full sm:w-auto lg:self-end"
      onClick={onClick}
    >
      {buttonContent}
    </Button>
  )
}
