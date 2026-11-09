import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate, useSearchParams } from 'react-router-dom'

import { AppShell } from '../components/AppShell'
import { ApiError, createAnalysis, listAnalyses } from '../lib/api'
import type { AnalysisSummary } from '../lib/api'
import { useAuth } from '../lib/auth-context'

const PAGE_SIZE = 20

export function WorkspacePage() {
  const { token, user, loading } = useAuth()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const query = searchParams.get('q')?.trim() ?? ''

  const [history, setHistory] = useState<AnalysisSummary[]>([])
  const [total, setTotal] = useState(0)
  const [loadingMore, setLoadingMore] = useState(false)
  const [historyError, setHistoryError] = useState<string | null>(null)
  const [searchInput, setSearchInput] = useState(query)

  const [file, setFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [roleTitle, setRoleTitle] = useState('')
  const [roleLevel, setRoleLevel] = useState('')
  const [llmApiKey, setLlmApiKey] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const refreshHistory = useCallback(async () => {
    if (!token) return
    try {
      const page = await listAnalyses(token, {
        q: query || undefined,
        limit: PAGE_SIZE,
      })
      setHistory(page.items)
      setTotal(page.total)
      setHistoryError(null)
    } catch {
      setHistoryError('Could not load your analyses.')
    }
  }, [token, query])

  useEffect(() => {
    void refreshHistory()
  }, [refreshHistory])

  useEffect(() => {
    setSearchInput(query)
  }, [query])

  async function loadMore() {
    if (!token || loadingMore) return
    setLoadingMore(true)
    try {
      const page = await listAnalyses(token, {
        q: query || undefined,
        limit: PAGE_SIZE,
        offset: history.length,
      })
      setHistory((current) => [...current, ...page.items])
      setTotal(page.total)
    } catch {
      setHistoryError('Could not load your analyses.')
    } finally {
      setLoadingMore(false)
    }
  }

  if (!loading && !token) {
    return <Navigate to="/login" replace />
  }

  function handleSearch(event: FormEvent) {
    event.preventDefault()
    const next = searchInput.trim()
    setSearchParams(next ? { q: next } : {})
  }

  function clearSearch() {
    setSearchInput('')
    setSearchParams({})
  }

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!token || !file) {
      setError('Choose a resume file (PDF or DOCX).')
      return
    }

    setBusy(true)
    setError(null)
    try {
      const analysis = await createAnalysis(token, {
        file,
        jobDescription,
        companyName,
        roleTitle,
        roleLevel: roleLevel || undefined,
        llmApiKey: llmApiKey || undefined,
      })
      navigate(`/app/analyses/${analysis.id}`)
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : 'Analysis failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <AppShell>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">Workspace</h1>
          <p className="mt-1 text-sm text-muted">
            {user ? `Signed in as ${user.email}` : 'Your resume analyses'}
          </p>
        </div>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-2xl border border-border bg-surface p-6">
          <h2 className="text-lg font-semibold">New analysis</h2>
          <p className="mt-1 text-sm text-muted">
            Upload a resume and paste the job description you are targeting.
          </p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <label className="block">
              <span className="text-sm font-medium">Resume (PDF or DOCX)</span>
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(event) => setFile(event.target.files?.[0] ?? null)}
                className="mt-1.5 block w-full cursor-pointer rounded-xl border border-border bg-surface-2/50 px-3 py-2 text-sm file:mr-3 file:rounded-lg file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-xs file:font-semibold file:text-primary-fg"
              />
            </label>

            <div className="grid gap-4 sm:grid-cols-2">
              <label className="block">
                <span className="text-sm font-medium">Company</span>
                <input
                  required
                  value={companyName}
                  onChange={(event) => setCompanyName(event.target.value)}
                  placeholder="Stripe"
                  className="mt-1.5 w-full rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </label>
              <label className="block">
                <span className="text-sm font-medium">Role</span>
                <input
                  required
                  value={roleTitle}
                  onChange={(event) => setRoleTitle(event.target.value)}
                  placeholder="Senior Backend Engineer"
                  className="mt-1.5 w-full rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
                />
              </label>
            </div>

            <label className="block">
              <span className="text-sm font-medium">Level (optional)</span>
              <input
                value={roleLevel}
                onChange={(event) => setRoleLevel(event.target.value)}
                placeholder="senior"
                className="mt-1.5 w-full rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium">Job description</span>
              <textarea
                required
                minLength={20}
                rows={7}
                value={jobDescription}
                onChange={(event) => setJobDescription(event.target.value)}
                placeholder="Paste the full job description here…"
                className="mt-1.5 w-full resize-y rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </label>

            <label className="block">
              <span className="text-sm font-medium">LLM API key (optional)</span>
              <input
                type="password"
                value={llmApiKey}
                onChange={(event) => setLlmApiKey(event.target.value)}
                placeholder="Use your own key for AI rewrites"
                className="mt-1.5 w-full rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
              />
            </label>

            {error ? (
              <p className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-fg transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {busy ? 'Analyzing…' : 'Analyze resume'}
            </button>
          </form>
        </section>

        <section className="rounded-2xl border border-border bg-surface p-6">
          <div className="flex items-baseline justify-between gap-3">
            <h2 className="text-lg font-semibold">Recent analyses</h2>
            {total > 0 ? (
              <span className="text-xs text-muted">
                {history.length} of {total}
              </span>
            ) : null}
          </div>
          <p className="mt-1 text-sm text-muted">
            Saved per company and role so you can pick up where you left off.
          </p>

          <form onSubmit={handleSearch} className="mt-4 flex gap-2">
            <input
              type="search"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search company, role or title"
              className="w-full rounded-xl border border-border bg-surface px-3.5 py-2 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
            />
            <button
              type="submit"
              className="shrink-0 rounded-xl border border-border px-3 py-2 text-sm font-medium transition hover:bg-surface-2"
            >
              Search
            </button>
            {query ? (
              <button
                type="button"
                onClick={clearSearch}
                className="shrink-0 rounded-xl px-2 py-2 text-sm text-muted transition hover:text-foreground"
              >
                Clear
              </button>
            ) : null}
          </form>

          {historyError ? (
            <p className="mt-4 text-sm text-danger">{historyError}</p>
          ) : null}

          {history.length === 0 ? (
            <p className="mt-6 rounded-xl border border-dashed border-border px-4 py-8 text-center text-sm text-muted">
              {query
                ? `No analyses match “${query}”.`
                : 'No analyses yet. Run your first one on the left.'}
            </p>
          ) : (
            <ul className="mt-4 space-y-2">
              {history.map((item) => (
                <li key={item.id}>
                  <Link
                    to={`/app/analyses/${item.id}`}
                    className="flex items-center justify-between gap-4 rounded-xl border border-border px-4 py-3 transition hover:border-primary/30 hover:bg-surface-2/50"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">{item.job_title}</p>
                      <p className="truncate text-xs text-muted">
                        {item.company} · {item.created_at.slice(0, 10)}
                      </p>
                    </div>
                    <span className="shrink-0 rounded-full bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">
                      {item.ats_score}
                    </span>
                  </Link>
                </li>
              ))}
            </ul>
          )}

          {history.length < total ? (
            <button
              type="button"
              onClick={() => void loadMore()}
              disabled={loadingMore}
              className="mt-4 w-full rounded-xl border border-border px-4 py-2 text-sm font-medium transition hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingMore ? 'Loading…' : 'Load more'}
            </button>
          ) : null}
        </section>
      </div>
    </AppShell>
  )
}
