import { useState } from 'react'
import { useParams } from '@tanstack/react-router'
import { type DashboardPageSearchParams } from '../lib/schemas'
import { API_BASE } from './api'

interface ExportParams extends DashboardPageSearchParams {
  catalog_name?: string
  package_name?: string
}

interface URLParams {
  catalog_name?: string
  package_name?: string
}

interface ApiError {
  detail: string
}

export function useExportCsv(onSuccess: () => void) {
  const [isExporting, setIsExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const pathParams: URLParams = useParams({ strict: false })

  const exportData = async (search: DashboardPageSearchParams) => {
    setIsExporting(true)
    setError(null)

    try {
      const allParams: ExportParams = {
        ...search,
        catalog_name:
          'catalogName' in pathParams
            ? (pathParams.catalogName as string)
            : undefined,
        package_name:
          'packageName' in pathParams
            ? (pathParams.packageName as string)
            : undefined,
      }

      const searchParams = new URLSearchParams({
        ocp_version: allParams.ocp_version,
        start_date: allParams.start_date,
        end_date: allParams.end_date,
        sort_type: allParams.sort_type,
        is_desc: String(allParams.is_desc),
      })

      if (allParams.search_query) {
        searchParams.append('search_query', allParams.search_query)
      }
      if (allParams.catalog_name) {
        searchParams.append('catalog_name', allParams.catalog_name)
      }
      if (allParams.package_name) {
        searchParams.append('package_name', allParams.package_name)
      }

      const apiUrl = `${API_BASE}/export/csv?${searchParams.toString()}`

      const response = await fetch(apiUrl)

      if (!response.ok) {
        const errorData = (await response.json()) as ApiError
        throw new Error(errorData.detail || 'Failed to export data.')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `pullsar_export_${new Date().toISOString().split('T')[0]}.csv`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      onSuccess()
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'An unknown error occurred.'
      )
    } finally {
      setIsExporting(false)
    }
  }

  return { exportData, isExporting, error }
}
