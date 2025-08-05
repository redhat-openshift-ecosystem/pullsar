import { createFileRoute } from '@tanstack/react-router'
import { z } from 'zod'
import { HomePage } from '../pages/HomePage'

const homeSearchSchema = z.object({
  ocp_version: z.string().optional(),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
})

export const Route = createFileRoute('/')({
  validateSearch: (search) => homeSearchSchema.parse(search),
  component: HomePage,
})
