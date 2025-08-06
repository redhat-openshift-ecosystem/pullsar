import { Link } from '@tanstack/react-router'
import { useTheme } from '../contexts/theme-context'

export function DashboardPage() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <h1>Statistics Dashboard</h1>
      <p>This is where the main dashboard will be.</p>
      <br />
      <Link to="/" className="text-blue-500 hover:underline">
        Go back to Home
      </Link>
      <button
        onClick={toggleTheme}
        className="rounded-md bg-primary py-2 text-primary-foreground transition-colors hover:bg-primary/90"
      >
        Toggle Theme
      </button>
    </div>
  )
}
