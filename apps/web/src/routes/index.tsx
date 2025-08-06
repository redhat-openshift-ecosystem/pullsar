import { createFileRoute, stripSearchParams } from '@tanstack/react-router'
import { HomePage } from '../pages/HomePage'
import { homePageSearchDefaults, homePageSearchSchema } from '../utils/schemas'
import { zodValidator } from '@tanstack/zod-adapter'

export const Route = createFileRoute('/')({
  validateSearch: zodValidator(homePageSearchSchema),
  search: {
    middlewares: [stripSearchParams(homePageSearchDefaults)],
  },
  component: HomePage,
})
