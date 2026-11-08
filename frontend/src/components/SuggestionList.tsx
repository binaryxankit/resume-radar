import type { Suggestion } from '../lib/api'

const severityTone: Record<Suggestion['severity'], string> = {
  critical: 'bg-danger',
  warning: 'bg-warning',
  info: 'bg-accent',
}

const severityText: Record<Suggestion['severity'], string> = {
  critical: 'text-danger',
  warning: 'text-warning',
  info: 'text-accent',
}

export function SuggestionList({ suggestions }: { suggestions: Suggestion[] }) {
  if (suggestions.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-border px-4 py-8 text-center text-sm text-muted">
        No suggestions for this analysis.
      </p>
    )
  }

  return (
    <ul className="space-y-3">
      {suggestions.map((suggestion) => (
        <li key={suggestion.id} className="rounded-xl border border-border bg-surface p-4">
          <div className="flex items-start gap-3">
            <span
              className={`mt-1.5 size-2 shrink-0 rounded-full ${severityTone[suggestion.severity]}`}
            />
            <div className="min-w-0">
              <p className="flex flex-wrap items-center gap-2 text-xs">
                <span className={`font-semibold uppercase tracking-wide ${severityText[suggestion.severity]}`}>
                  {suggestion.severity}
                </span>
                <span className="text-muted">{suggestion.category}</span>
              </p>
              <p className="mt-1 text-sm leading-relaxed">{suggestion.message}</p>
              {suggestion.evidence ? (
                <p className="mt-2 text-xs text-muted">{suggestion.evidence}</p>
              ) : null}
              {suggestion.proposed_text ? (
                <pre className="mt-2 whitespace-pre-wrap rounded-lg bg-surface-2/70 p-3 text-xs leading-relaxed">
                  {suggestion.proposed_text}
                </pre>
              ) : null}
            </div>
          </div>
        </li>
      ))}
    </ul>
  )
}
