import { useSearch, Link } from '@tanstack/react-router'
import { useTheme } from '../contexts/theme-context'

export function HomePage() {
  const { ocp_version, start_date, end_date } = useSearch({ from: '/' })
  const { theme, toggleTheme } = useTheme()

  return (
    <div>
      <h1 className="text-xl font-bold text-cyan-400 underline bg-red-50">
        Welcome to the Pullsar Homepage
      </h1>
      <p>Currently viewing stats for OCP Version: {ocp_version}</p>
      <p>Start Date: {start_date || 'Not set'}</p>
      <p>End Date: {end_date || 'Not set'}</p>
      <br />
      <Link to="/dashboard" className="text-blue-500 hover:underline">
        Go to Dashboard
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
