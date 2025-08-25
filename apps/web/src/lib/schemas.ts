import { z } from 'zod'
import { daysAgo } from '../lib/utils'

const zodDateString = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format.')

export interface HomePageSearchParams {
  ocp_version: string
  start_date: string
  end_date: string
}

export const homePageSearchDefaults = {
  ocp_version: 'v4.18',
  start_date: daysAgo(15),
  end_date: daysAgo(1),
}

export const homePageSearchSchema = z.object({
  ocp_version: z.string().default(homePageSearchDefaults.ocp_version),
  start_date: zodDateString.default(homePageSearchDefaults.start_date),
  end_date: zodDateString.default(homePageSearchDefaults.end_date),
})

export interface DashboardPageSearchParams {
  ocp_version: string
  start_date: string
  end_date: string
  sort_type: string
  is_desc: boolean
}

export const dashboardPageSearchDefaults = {
  ocp_version: 'v4.18',
  start_date: daysAgo(15),
  end_date: daysAgo(1),
  sort_type: 'pulls',
  is_desc: true,
}

export const dashboardPageSearchSchema = z.object({
  ocp_version: z.string().default(dashboardPageSearchDefaults.ocp_version),
  start_date: zodDateString.default(dashboardPageSearchDefaults.start_date),
  end_date: zodDateString.default(dashboardPageSearchDefaults.end_date),
  sort_type: z.string().default(dashboardPageSearchDefaults.sort_type),
  is_desc: z.boolean().default(dashboardPageSearchDefaults.is_desc),
})
