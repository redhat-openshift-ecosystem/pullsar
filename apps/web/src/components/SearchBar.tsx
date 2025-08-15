import { useRef } from 'react'
import { Input } from './ui/input'
import { Search } from 'lucide-react'
import { Button } from './ui/button'

interface Props {
  placeholder: string
}
const SearchBar = ({ placeholder }: Props) => {
  const inputRef = useRef<HTMLInputElement>(null)
  const handleSearchSubmit = () => {
    if (inputRef.current) {
      const searchQuery = inputRef.current.value
      if (searchQuery) {
        // TODO
      }
    }
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-secondary mb-1">
        Search
      </label>
      <div className="w-full mr-8 relative flex items-center">
        <Input
          type="search"
          ref={inputRef}
          placeholder={placeholder}
          onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
          className="rounded-r-none"
        />
        <Button
          className="flex items-center justify-center aspect-square
          rounded-l-none"
          onClick={() => handleSearchSubmit()}
        >
          <Search strokeWidth={3} />
        </Button>
      </div>
    </div>
  )
}
export default SearchBar
