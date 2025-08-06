import { createRootRoute, Outlet } from '@tanstack/react-router'
import { ThemeProvider } from '../contexts/theme-context'

export const Route = createRootRoute({
  component: () => (
    <>
      <ThemeProvider>
        <div className="relative isolate">
          <div
            className="absolute inset-x-0 top-0 -z-10 h-150 bg-gradient-to-b from-custom-background to-background"
            aria-hidden="true"
          />
          <main className="mx-auto max-w-screen-xl p-8 text-center">
            <Outlet />
          </main>
        </div>
      </ThemeProvider>
    </>
  ),
})
