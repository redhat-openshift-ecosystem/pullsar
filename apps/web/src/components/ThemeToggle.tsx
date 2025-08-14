import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/theme-context'

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme()
  const iconStyleClass = 'w-8 h-8 sm:w-10 sm:h-10 text-accent'
  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-full bg-bg-add cursor-pointer hover:bg-bg-add/80"
    >
      {theme === 'dark' ? (
        <Moon className={iconStyleClass} />
      ) : (
        <Sun className={iconStyleClass} />
      )}
    </button>
  )
}
