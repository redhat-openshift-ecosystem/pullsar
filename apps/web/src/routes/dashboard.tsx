import { createFileRoute, stripSearchParams } from '@tanstack/react-router'
import { DashboardPage } from '../pages/DashboardPage'
import { zodValidator } from '@tanstack/zod-adapter'
import {
  dashboardPageSearchDefaults,
  dashboardPageSearchSchema,
} from '../lib/schemas'

export const Route = createFileRoute('/dashboard')({
  validateSearch: zodValidator(dashboardPageSearchSchema),
  search: {
    middlewares: [stripSearchParams(dashboardPageSearchDefaults)],
  },
  component: DashboardPage,
})
