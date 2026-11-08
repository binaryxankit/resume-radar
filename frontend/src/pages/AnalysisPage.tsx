import { useCallback, useEffect, useState } from 'react'
import { Link, Navigate, useNavigate, useParams } from 'react-router-dom'

import { AppShell } from '../components/AppShell'
import { IntelPanel } from '../components/IntelPanel'
import { ResumeEditor } from '../components/ResumeEditor'
import { ScoreCard } from '../components/ScoreCard'
import { SuggestionList } from '../components/SuggestionList'
import { exportResume, getAnalysis } from '../lib/api'
import type { Analysis } from '../lib/api'
import { useAuth } from '../lib/auth-context'

export function AnalysisPage() {
  const { token, loading: authLoading } = useAuth()
  const { id } = useParams()
  const navigate = useNavigate()

  const [analysis, setAnalysis] = useState<Analysis | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [exporting, setExporting] = useState(false)
  const [exportError, setExportError] = useState<string | null>(null)

  const analysisId = Number(id)

  const load = useCallback(async () => {
    if (!token || !Number.isFinite(analysisId)) return
    setLoading(true)
    setError(null)
    try {
      setAnalysis(await getAnalysis(token, analysisId))
    } catch {
      setError('Analysis not found.')
    } finally {
      setLoading(false)
    }
  }, [token, analysisId])

  useEffect(() => {
    void load()
  }, [load])

  async function handleExport() {
    if (!token || !analysis) return
    setExporting(true)
    setExportError(null)
    try {
      const blob = await exportResume(token, analysis.id)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `resume-${analysis.id}.docx`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      setExportError('Could not export this resume.')
    } finally {
      setExporting(false)
    }
  }

  if (!authLoading && !token) {
    return <Navigate to="/login" replace />
  }

  return (
    <AppShell>
      <Link
        to="/app"
        className="inline-flex items-center gap-1.5 text-sm text-muted transition hover:text-foreground"
      >
        <span aria-hidden>←</span> Workspace
      </Link>

      {loading ? (
        <p className="mt-8 text-sm text-muted">Loading analysis…</p>
      ) : error || !analysis ? (
        <div className="mt-8 rounded-2xl border border-border bg-surface p-8 text-center">
          <p className="text-sm text-muted">{error ?? 'Analysis not found.'}</p>
          <Link
            to="/app"
            className="mt-4 inline-block rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-fg"
          >
            Back to workspace
          </Link>
        </div>
      ) : (
        <>
          <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
            <div>
              <h1 className="text-3xl font-semibold tracking-tight">{analysis.job_title}</h1>
              <p className="mt-1 text-sm text-muted">
                {analysis.company} · {analysis.role} · {analysis.created_at.slice(0, 10)}
              </p>
              {exportError ? (
                <p className="mt-2 text-xs text-danger">{exportError}</p>
              ) : null}
            </div>
            <button
              type="button"
              onClick={() => void handleExport()}
              disabled={exporting}
              className="rounded-xl border border-border bg-surface px-4 py-2 text-sm font-semibold transition hover:bg-surface-2 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {exporting ? 'Exporting…' : 'Export DOCX'}
            </button>
          </div>

          <div className="mt-8 grid gap-6 lg:grid-cols-[1.6fr_1fr]">
            <div className="space-y-6">
              <ScoreCard analysis={analysis} />

              <section className="rounded-2xl border border-border bg-surface p-6">
                <h2 className="text-lg font-semibold">Suggestions</h2>
                <p className="mt-1 text-sm text-muted">
                  Prioritized by severity. Generated from deterministic rules, refined by the LLM
                  when enabled.
                </p>
                <div className="mt-4">
                  <SuggestionList suggestions={analysis.suggestions} />
                </div>
              </section>

              <ResumeEditor
                key={analysis.id}
                analysis={analysis}
                token={token ?? ''}
                onUpdated={(updated) =>
                  navigate(`/app/analyses/${updated.id}`, { replace: true })
                }
              />
            </div>

            <div className="space-y-6">
              <IntelPanel
                token={token ?? ''}
                company={analysis.company}
                role={analysis.role}
              />

              <section className="rounded-2xl border border-border bg-surface p-6">
                <h2 className="text-lg font-semibold">Detected sections</h2>
                {Object.keys(analysis.sections).length === 0 ? (
                  <p className="mt-3 text-sm text-muted">
                    No standard sections detected. Use clear headings like Experience and Skills.
                  </p>
                ) : (
                  <ul className="mt-3 space-y-2">
                    {Object.entries(analysis.sections).map(([name, lines]) => (
                      <li
                        key={name}
                        className="flex items-center justify-between gap-3 rounded-lg border border-border px-3 py-2 text-sm"
                      >
                        <span className="capitalize">{name}</span>
                        <span className="text-xs text-muted">{lines.length} lines</span>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>
          </div>
        </>
      )}
    </AppShell>
  )
}
