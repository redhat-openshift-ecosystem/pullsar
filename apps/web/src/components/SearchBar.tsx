import { Input } from './ui/input'
import { Search } from 'lucide-react'
import { Button } from './ui/button'
import { useEffect, useState } from 'react'

interface Props {
  placeholder: string
  currentQuery: string
  onSearchSubmit: (query: string) => void
}
const SearchBar = ({ placeholder, currentQuery, onSearchSubmit }: Props) => {
  const [inputValue, setInputValue] = useState(currentQuery)

  useEffect(() => {
    setInputValue(currentQuery)
  }, [currentQuery])

  const handleSearchSubmit = () => {
    onSearchSubmit(inputValue)
  }

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-secondary mb-1">
        Search
      </label>
      <div className="w-full mr-8 relative flex items-center">
        <Input
          type="search"
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearchSubmit()}
          className="rounded-r-none"
        />
        <Button
          className="flex items-center justify-center aspect-square rounded-l-none"
          onClick={handleSearchSubmit}
        >
          <Search strokeWidth={3} />
        </Button>
      </div>
    </div>
  )
}
export default SearchBar
