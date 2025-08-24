import { ChevronsRight, ChevronUp, PlusCircle } from 'lucide-react'

export const ComparisonTutorial = () => {
  return (
    <div className="text-center">
      <h3 className="text-3xl font-bold text-summary-accent">
        Side-by-Side Comparison
      </h3>
      <p className="mt-2 max-w-2xl mx-auto text-lg text-secondary">
        Compare usage trends of multiple catalogs, packages or bundles at once.
        On dashboard page, add items to a comparison group, then click on Show
        Comparison at the bottom.
      </p>
      <div className="mt-8 flex items-center justify-center gap-6">
        <div className="flex flex-col items-center text-center">
          <div className="p-3 rounded-full bg-bg-add text-accent">
            <PlusCircle className="w-10 h-10" />
          </div>
          <p className="mt-2 font-semibold text-accent">Add to Comparison</p>
        </div>
        <ChevronsRight className="w-8 h-8 text-secondary" />
        <div className="flex flex-col items-center text-center">
          <div className="flex flex-col items-center p-2 rounded-lg text-accent">
            <ChevronUp className="w-15 h-15" />
            <span className="text-accent font-semibold mt-1">
              Show Comparison
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
