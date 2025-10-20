import { useState, useEffect, useMemo } from 'react'
import { ChevronDown, Trash2, X } from 'lucide-react'
import { type ListItem } from '../hooks/useItems'
import { TrendIndicator } from './TrendIndicator'
import { UsageLineChart } from './UsageLineChart'
import { BreadcrumbNav, type Breadcrumb } from './BreadcrumbNav'
import { LINE_COLORS, shortBundleName, shortCatalogName } from '../lib/utils'
import { Button } from './ui/button'
import FocusLock from 'react-focus-lock'

type ColoredListItem = ListItem & { color: string }

interface Props {
  items: ListItem[]
  breadcrumbs: Breadcrumb[]
  onClose: () => void
  onItemRemove: (item: ListItem) => void
  onClearAll: () => void
}

export function ComparisonTray({
  items,
  breadcrumbs,
  onClose,
  onItemRemove,
  onClearAll,
}: Props) {
  const coloredItems = useMemo(
    () =>
      items.map((item, index) => ({
        ...item,
        color: LINE_COLORS[index % LINE_COLORS.length],
      })),
    [items]
  )

  const [visibleItems, setVisibleItems] =
    useState<ColoredListItem[]>(coloredItems)

  useEffect(() => {
    setVisibleItems(coloredItems)
  }, [coloredItems])

  useEffect(() => {
    if (items.length === 0) {
      onClose()
    }
  }, [items, onClose])

  // makes the scrolling focus on the ComparisonTray instead
  // of the background dashboard when ComparisonTray is mounted
  useEffect(() => {
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = 'auto'
    }
  }, [])

  const level = breadcrumbs.length

  const getLabel = (itemName: string): string => {
    if (level === 1) return shortCatalogName(itemName)
    if (level === 3) return shortBundleName(itemName)
    return itemName
  }

  const handleToggleVisibility = (itemToToggle: ColoredListItem) => {
    setVisibleItems((currentVisible) => {
      const isVisible = currentVisible.some(
        (item) => item.name === itemToToggle.name
      )
      return isVisible
        ? currentVisible.filter((item) => item.name !== itemToToggle.name)
        : [...currentVisible, itemToToggle]
    })
  }

  return (
    <FocusLock>
      <div className="fixed bottom-0 left-0 w-full h-full bg-bg-comparison/95 z-40 flex flex-col items-center justify-center border border-border overflow-y-auto">
        <div className="w-full max-w-7xl h-full rounded-t-lg p-4 flex flex-col">
          <div className="w-full max-w-7xl mx-auto flex flex-col h-full">
            <button
              onClick={onClose}
              className="flex flex-col items-center text-secondary hover:text-accent transition-colors cursor-pointer mb-5"
            >
              <ChevronDown className="w-10 h-10" />
              <span className="font-semibold text-sm">Hide Comparison</span>
            </button>
            <div className="flex justify-between items-start mb-4">
              <div className="flex-grow min-w-0">
                <BreadcrumbNav
                  breadcrumbs={breadcrumbs}
                  isInteractive={false}
                />
              </div>
              <Button
                onClick={onClearAll}
                variant={'comparisonTray'}
                className="ml-4 font-semibold"
              >
                <Trash2 />
                Clear All
              </Button>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-4">
              {coloredItems.map((item) => {
                const isVisible = visibleItems.some((v) => v.name === item.name)

                return (
                  <button
                    key={item.name}
                    onClick={() => handleToggleVisibility(item)}
                    className={`bg-card/50 border border-border p-2 rounded-md flex flex-col items-left
                    text-left relative cursor-pointer transition-opacity ${!isVisible && 'opacity-40'}`}
                  >
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        onItemRemove(item)
                      }}
                      className="absolute top-1 right-1 p-0.5 text-secondary"
                    >
                      <X className="w-4 h-4" />
                    </button>

                    <p
                      className="font-bold truncate"
                      style={{ color: item.color }}
                    >
                      {getLabel(item.name)}
                    </p>
                    <p className="text-lg text-foreground font-bold">
                      {item.stats.total_pulls.toLocaleString()}
                    </p>
                    <p className="text-md text-secondary">Total Pulls</p>
                    <TrendIndicator trend={item.stats.trend} size="sm" />
                  </button>
                )
              })}
            </div>

            <div className="flex-grow h-full min-h-60 sm:min-h-100 max-h-120 mt-10">
              <UsageLineChart
                series={visibleItems.map((item) => ({
                  name: getLabel(item.name),
                  data: item.stats.chart_data,
                  color: item.color,
                }))}
                isComparison={true}
              />
            </div>
          </div>
        </div>
      </div>
    </FocusLock>
  )
}
