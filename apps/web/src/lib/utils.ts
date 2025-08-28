import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const daysAgo = (n: number) => {
  const date = new Date()
  date.setDate(date.getDate() - n)
  return date.toISOString().split('T')[0]
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
