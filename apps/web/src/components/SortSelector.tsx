import { ArrowDown, ArrowUp } from 'lucide-react'
import { Button } from './ui/button'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from './ui/select'
import { capitalizeFirstLetter } from '../lib/utils'

interface Props {
  types: string[]
  currentType: string
  isDesc: boolean
  onTypeChange: (type: string) => void
  onDirectionChange: (isDesc: boolean) => void
}

export function SortSelector({
  types,
  currentType,
  isDesc,
  onTypeChange,
  onDirectionChange,
}: Props) {
  return (
    <div>
      <label className="block text-sm font-medium text-secondary mb-1">
        Sort By
      </label>
      <div className="flex">
        <Select value={currentType} onValueChange={onTypeChange}>
          <SelectTrigger className="justify-start text-left font-normal bg-input border-border rounded-r-none w-full">
            <SelectValue placeholder="Select sort type" />
          </SelectTrigger>

          <SelectContent>
            <SelectGroup>
              {types.map((type) => (
                <SelectItem key={type} value={type}>
                  {capitalizeFirstLetter(type)}
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
        <Button
          className="flex items-center justify-center aspect-square
          rounded-l-none"
          onClick={() => onDirectionChange(!isDesc)}
        >
          {isDesc ? <ArrowDown strokeWidth={3} /> : <ArrowUp strokeWidth={3} />}
        </Button>
      </div>
    </div>
  )
}
