import type { HTMLAttributes } from 'react'
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from './ui/pagination'
import { cn } from '../lib/utils'

interface IPagination {
  page: number
  totalPages: number
  totalCount: number
}

interface Props extends HTMLAttributes<HTMLDivElement> {
  pagination: IPagination
  handlePageChange: (newPage: number) => void
}

const CustomPagination = ({
  pagination,
  handlePageChange,
  className,
  ...props
}: Props) => {
  const { page, totalPages } = pagination

  const pageNumbers = getPageNumbers(page, totalPages)

  return (
    <div
      className={cn('w-full lg:w-fit self-center md:self-end', className)}
      {...props}
    >
      <Pagination>
        <PaginationContent>
          <PaginationItem>
            <PaginationPrevious
              onClick={() => handlePageChange(page - 1)}
              className={page === 1 ? 'pointer-events-none opacity-50' : ''}
            />
          </PaginationItem>

          {pageNumbers.map((p, index) => (
            <PaginationItem key={`${p}-${index}`}>
              {typeof p === 'string' ? (
                <PaginationEllipsis />
              ) : (
                <PaginationLink
                  onClick={() => handlePageChange(p)}
                  isActive={page === p}
                >
                  {p}
                </PaginationLink>
              )}
            </PaginationItem>
          ))}

          <PaginationItem>
            <PaginationNext
              onClick={() => handlePageChange(page + 1)}
              className={
                page === totalPages ? 'pointer-events-none opacity-50' : ''
              }
            />
          </PaginationItem>
        </PaginationContent>
      </Pagination>
    </div>
  )
}

const getPageNumbers = (
  currentPage: number,
  totalPages: number
): (number | string)[] => {
  if (totalPages <= 5) {
    return Array.from({ length: totalPages }, (_, i) => i + 1)
  }

  const pages = new Set<number>()

  pages.add(1)
  pages.add(totalPages)

  for (let i = -2; i <= 2; i++) {
    const p = currentPage + i
    if (p > 1 && p < totalPages) {
      pages.add(p)
    }
  }

  const sortedPages = Array.from(pages).sort((a, b) => a - b)
  const result: (number | string)[] = []
  let lastPage: number | null = null

  for (const page of sortedPages) {
    if (lastPage !== null && page - lastPage > 1) {
      result.push('...')
    }
    result.push(page)
    lastPage = page
  }

  return result
}

export default CustomPagination
