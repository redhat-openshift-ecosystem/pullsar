import { z } from 'zod'
import { daysAgo } from '../lib/utils'

const zodDateString = z
  .string()
  .regex(/^\d{4}-\d{2}-\d{2}$/, 'Date must be in YYYY-MM-DD format.')

export const homePageSearchDefaults = {
  ocp_version: 'v4.18',
  start_date: daysAgo(15),
  end_date: daysAgo(1),
}

export const homePageSearchSchema = z.object({
  ocp_version: z
    .string()
    .optional()
    .default(homePageSearchDefaults.ocp_version),
  start_date: zodDateString
    .optional()
    .default(homePageSearchDefaults.start_date),
  end_date: zodDateString.optional().default(homePageSearchDefaults.end_date),
})
