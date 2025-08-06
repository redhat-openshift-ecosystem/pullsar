import { useSearch, Link } from '@tanstack/react-router'
import { useTheme } from '../contexts/theme-context'
import { Button } from '../components/ui/button'

export function HomePage() {
  const { ocp_version, start_date, end_date } = useSearch({ from: '/' })
  const { theme, toggleTheme } = useTheme()

  return (
    <>
      <h1>Hello pullsar hello hello</h1>
      <Button onClick={toggleTheme}>Toggle Theme</Button>
    </>
  )
}
