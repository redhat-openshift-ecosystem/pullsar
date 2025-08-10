import { createRootRoute, Outlet } from '@tanstack/react-router'
import { ThemeProvider } from '../contexts/theme-context'
import { ThemeToggle } from '../components/ThemeToggle'

export const Route = createRootRoute({
  component: () => (
    <>
      <ThemeProvider>
        <div className="relative isolate">
          <div
            className="absolute inset-x-0 top-0 -z-10 h-150 bg-gradient-to-b from-custom-background to-background"
            aria-hidden="true"
          />
          <div className="absolute top-4 right-4 z-10">
            <ThemeToggle />
          </div>
          <main className="lg:mx-auto max-w-screen-xl py-8 lg:px-8 text-center">
            <Outlet />
          </main>
        </div>
      </ThemeProvider>
    </>
  ),
})
