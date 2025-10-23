import { Tooltip, TooltipContent, TooltipTrigger } from './ui/tooltip'

interface CustomTooltipProps {
  children: React.ReactNode
  content: React.ReactNode
  disabled?: boolean
}

export function CustomTooltip({
  children,
  content,
  disabled,
}: CustomTooltipProps) {
  if (disabled) {
    return children
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>{children}</TooltipTrigger>
      <TooltipContent>{content}</TooltipContent>
    </Tooltip>
  )
}
