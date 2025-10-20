import { Moon, Sun } from 'lucide-react'
import { useTheme } from '../contexts/theme-context'
import { CustomTooltip } from './CustomTooltip'

export const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme()
  const iconStyleClass = 'w-8 h-8 sm:w-10 sm:h-10 text-accent'
  const isDark = theme === 'dark'
  const tooltipText = isDark ? 'Switch to light mode.' : 'Switch to dark mode.'

  return (
    <CustomTooltip content={tooltipText}>
      <button
        onClick={toggleTheme}
        className="p-2 rounded-full bg-bg-add cursor-pointer hover:bg-bg-add/80"
        aria-label={tooltipText}
      >
        {isDark ? (
          <Moon className={iconStyleClass} />
        ) : (
          <Sun className={iconStyleClass} />
        )}
      </button>
    </CustomTooltip>
  )
}
