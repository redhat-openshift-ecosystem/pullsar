import { useSearch, Link } from '@tanstack/react-router'

export function HomePage() {
  const { ocp_version, start_date, end_date } = useSearch({ from: '/' })

  return (
    <div>
      <h1>Welcome to the Pullsar Homepage</h1>
      <p>Currently viewing stats for OCP Version: {ocp_version}</p>
      <p>Start Date: {start_date || 'Not set'}</p>
      <p>End Date: {end_date || 'Not set'}</p>
      <br />
      <Link to="/dashboard" className="text-blue-500 hover:underline">
        Go to Dashboard
      </Link>
    </div>
  )
}
