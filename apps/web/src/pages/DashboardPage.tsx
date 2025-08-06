import { Link } from '@tanstack/react-router'
import { useTheme } from '../contexts/theme-context'
import { Button } from '../components/ui/button'

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
      <Button onClick={toggleTheme}>Toggle Theme</Button>
    </div>
  )
}
