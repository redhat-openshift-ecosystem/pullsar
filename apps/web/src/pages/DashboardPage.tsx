import { Link } from '@tanstack/react-router'

export function DashboardPage() {
  return (
    <div>
      <h1>Statistics Dashboard</h1>
      <p>This is where the main dashboard will be.</p>
      <br />
      <Link to="/" className="text-blue-500 hover:underline">
        Go back to Home
      </Link>
    </div>
  )
}
