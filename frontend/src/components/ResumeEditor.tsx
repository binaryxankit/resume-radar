import { useState, type FormEvent } from 'react'

import { ApiError, reanalyze } from '../lib/api'
import type { Analysis } from '../lib/api'

export function ResumeEditor({
  analysis,
  token,
  onUpdated,
}: {
  analysis: Analysis
  token: string
  onUpdated: (analysis: Analysis) => void
}) {
  const [text, setText] = useState(analysis.raw_text)
  const [llmApiKey, setLlmApiKey] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault()
    if (!text.trim()) {
      setError('Resume text cannot be empty.')
      return
    }

    setBusy(true)
    setError(null)
    try {
      const updated = await reanalyze(
        token,
        analysis.id,
        text,
        llmApiKey || undefined,
      )
      onUpdated(updated)
    } catch (cause) {
      setError(cause instanceof ApiError ? cause.message : 'Re-analysis failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <section className="rounded-2xl border border-border bg-surface p-6">
      <h2 className="text-lg font-semibold">Edit and re-analyze</h2>
      <p className="mt-1 text-sm text-muted">
        Make changes, then run the score again. A new immutable version is saved each time.
      </p>

      <form onSubmit={handleSubmit} className="mt-4 space-y-3">
        <textarea
          value={text}
          onChange={(event) => setText(event.target.value)}
          rows={16}
          spellCheck={false}
          className="w-full resize-y rounded-xl border border-border bg-surface-2/40 p-4 font-mono text-xs leading-relaxed outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
        />

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="password"
            value={llmApiKey}
            onChange={(event) => setLlmApiKey(event.target.value)}
            placeholder="LLM API key (optional)"
            className="w-full rounded-xl border border-border bg-surface px-3.5 py-2.5 text-sm outline-none transition focus:border-primary focus:ring-2 focus:ring-primary/20"
          />
          <button
            type="submit"
            disabled={busy}
            className="shrink-0 rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-primary-fg transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {busy ? 'Scoring…' : 'Re-run analysis'}
          </button>
        </div>

        {error ? (
          <p className="rounded-lg border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
            {error}
          </p>
        ) : null}
      </form>
    </section>
  )
}
