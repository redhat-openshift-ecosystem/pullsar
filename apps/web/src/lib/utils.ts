import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

// comparison chart colors
export const LINE_COLORS = [
  '#0284c7', // blue
  '#22c55e', // green
  '#ef4444', // red
  '#eab308', // yellow
  '#8b5cf6', // violet
  '#ec4899', // pink
  '#14b8a6', // teal
  '#f97316', // orange
  '#84cc16', // lime
  '#06b6d4', // cyan
]

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const daysAgo = (n: number) => {
  const date = new Date()
  date.setDate(date.getDate() - n)
  return date.toISOString().split('T')[0]
}

export const formatDate = (isoDateString: string) => {
  const date = new Date(isoDateString)
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  })
}

export const capitalizeFirstLetter = (word: string) => {
  return String(word).charAt(0).toUpperCase() + String(word).slice(1)
}

// in the breadcrumbs and item list we display the short name
// e.g. 'image-registry/path/catalog-name' shortens to 'catalog-name'
export function shortCatalogName(fullName: string): string {
  const lastSlashIndex = fullName.lastIndexOf('/')
  if (lastSlashIndex === -1) {
    return fullName
  }

  return fullName.substring(lastSlashIndex + 1)
}

// in the item list we display the short name
// e.g. 'operator-alpha.v1.0.0' shortens to 'v1.0.0'
// as the scope is stored in the breadcrumb and URL,
// we can avoid repeating the operator's name
export function shortBundleName(fullName: string): string {
  const firstDotIndex = fullName.indexOf('.')
  if (firstDotIndex === -1) {
    return fullName
  }

  return fullName.substring(firstDotIndex + 1)
}
