import { useCallback, useEffect, useState } from 'react'

import { getIntel } from '../lib/api'
import type { Intel } from '../lib/api'

export function IntelPanel({
  token,
  company,
  role,
}: {
  token: string
  company: string
  role: string
}) {
  const [data, setData] = useState<Intel | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(
    async (refresh: boolean) => {
      setLoading(true)
      setError(null)
      try {
        setData(await getIntel(token, company, role, refresh))
      } catch {
        setError('Could not load company intel.')
      } finally {
        setLoading(false)
      }
    },
    [token, company, role],
  )

  useEffect(() => {
    void load(false)
  }, [load])

  return (
    <section className="rounded-2xl border border-border bg-surface p-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold">Company intel</h2>
          <p className="mt-1 text-xs text-muted">
            {company}
            {role ? ` · ${role}` : ''}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void load(true)}
          disabled={loading}
          className="rounded-lg border border-border px-3 py-1.5 text-xs font-medium transition hover:bg-surface-2 disabled:opacity-60"
        >
          Refresh
        </button>
      </div>

      {loading ? (
        <p className="mt-4 text-sm text-muted">Loading intel…</p>
      ) : error ? (
        <p className="mt-4 text-sm text-danger">{error}</p>
      ) : !data || !data.source_available ? (
        <p className="mt-4 rounded-xl border border-dashed border-border px-4 py-6 text-sm text-muted">
          Live intel is unavailable. Add Reddit API credentials on the server to enable it.
        </p>
      ) : data.insights.length === 0 ? (
        <p className="mt-4 text-sm text-muted">No discussions found for this role yet.</p>
      ) : (
        <ul className="mt-4 space-y-3">
          {data.insights.map((insight) => (
            <li key={insight.id} className="rounded-xl border border-border p-3">
              <div className="flex items-center justify-between gap-2 text-[11px] uppercase tracking-wide text-muted">
                <span>{insight.kind}</span>
                <span>{Math.round(insight.confidence * 100)}% confidence</span>
              </div>
              <a
                href={insight.source_url}
                target="_blank"
                rel="noreferrer"
                className="mt-1 block text-sm font-medium leading-snug transition hover:text-primary"
              >
                {insight.title}
              </a>
              <p className="mt-1 text-xs text-muted">{insight.summary}</p>
            </li>
          ))}
        </ul>
      )}

      {data?.cached ? (
        <p className="mt-4 text-[11px] text-muted">Served from cache.</p>
      ) : null}
    </section>
  )
}
