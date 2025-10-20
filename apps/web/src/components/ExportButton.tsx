import { CustomTooltip } from './CustomTooltip'
import { Button } from './ui/button'
import { Download } from 'lucide-react'

interface Props {
  onClick: () => Promise<void>
  isExportMaxExceeded: boolean
  isExporting: boolean
  isDone: boolean
  exportMaxDays: number
}

export function ExportButton({
  onClick,
  isExportMaxExceeded,
  isExporting,
  isDone,
  exportMaxDays,
}: Props) {
  const buttonContent = (
    <>
      <Download strokeWidth={3} className="mr-2 h-4 w-4" />
      {isExporting ? 'Exporting...' : 'Export as CSV'}
    </>
  )

  const getTooltipMessage = () => {
    if (isExportMaxExceeded) {
      return `Range exceeds ${exportMaxDays} days.`
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
      <CustomTooltip content={getTooltipMessage()}>
        <div className="w-full sm:w-auto lg:self-end">
          <Button className="font-bold w-full sm:w-auto lg:self-end" disabled>
            {buttonContent}
          </Button>
        </div>
      </CustomTooltip>
    )
  }

  return (
    <Button
      className="font-bold w-full sm:w-auto lg:self-end"
      onClick={() => void onClick()}
    >
      {buttonContent}
    </Button>
  )
}
