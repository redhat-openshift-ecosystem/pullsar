import { useState, useEffect, useMemo } from 'react'
import { parseISO, subDays } from 'date-fns'
import { Calendar as CalendarIcon } from 'lucide-react'
import { type DateRange } from 'react-day-picker'
import { Button } from './ui/button'
import { Calendar } from './ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from './ui/popover'
import { useApiConfig } from '../hooks/useApiConfig'

const yesterdayDate = () => subDays(new Date(), 1)

interface Props {
  dateRange: { from?: string; to?: string }
  onDateChange: (range: DateRange | undefined) => void
}

export function DateRangeSelector({ dateRange, onDateChange }: Props) {
  const [isOpen, setIsOpen] = useState(false)

  const { data: apiConfig } = useApiConfig()
  const dbStartDate = useMemo(
    () => (apiConfig?.db_start_date ? parseISO(apiConfig.db_start_date) : null),
    [apiConfig?.db_start_date]
  )

  const [range, setRange] = useState<DateRange | undefined>(() => {
    return dateRange.from && dateRange.to
      ? { from: parseISO(dateRange.from), to: parseISO(dateRange.to) }
      : undefined
  })

  useEffect(() => {
    if (dateRange.from && dateRange.to) {
      setRange({ from: parseISO(dateRange.from), to: parseISO(dateRange.to) })
    }
  }, [dateRange])

  const handleOpenChange = (open: boolean) => {
    if (!open) {
      onDateChange(range)
    }
    setIsOpen(open)
  }

  return (
    <div onClick={(e) => e.stopPropagation()}>
      <label className="block text-sm font-medium text-secondary mb-1">
        Date Range
      </label>
      <Popover open={isOpen} onOpenChange={handleOpenChange}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            className="justify-start text-left font-normal bg-input border-border w-full"
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {range?.from && range?.to
              ? `${range.from.toLocaleDateString()} - ${range.to.toLocaleDateString()}`
              : 'Select date'}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="range"
            selected={range}
            onSelect={(selectedRange) => setRange(selectedRange)}
            numberOfMonths={1}
            disabled={{
              before: dbStartDate || range?.from,
              after: yesterdayDate(),
            }}
          />
        </PopoverContent>
      </Popover>
    </div>
  )
}
