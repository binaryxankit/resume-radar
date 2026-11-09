const API_BASE = import.meta.env.VITE_API_URL ?? ''

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

export type User = {
  id: number
  email: string
  created_at: string
}

export type Severity = 'critical' | 'warning' | 'info'

export type Suggestion = {
  id: number
  category: string
  severity: Severity
  message: string
  evidence: string | null
  proposed_text: string | null
  accepted_at: string | null
}

export type Finding = {
  category: string
  severity: Severity
  message: string
  evidence: string | null
}

export type ScoreBreakdown = {
  overall: number
  keyword_coverage: number
  section_completeness: number
  impact_score: number
  format_score: number
  matched_keywords: string[]
  missing_keywords: string[]
  findings: Finding[]
}

export type Contact = {
  name?: string | null
  email?: string | null
  phone?: string | null
  links?: string[]
}

export type Analysis = {
  id: number
  company: string
  role: string
  job_title: string
  ats_score: number
  score: ScoreBreakdown
  matched_keywords: string[]
  missing_keywords: string[]
  sections: Record<string, string[]>
  contact: Contact
  raw_text: string
  suggestions: Suggestion[]
  resume_id: number
  resume_version_id: number
  created_at: string
}

export type AnalysisSummary = {
  id: number
  company: string
  role: string
  job_title: string
  ats_score: number
  created_at: string
}

export type AnalysisHistory = {
  items: AnalysisSummary[]
  total: number
  limit: number
  offset: number
}

export type HistoryQuery = {
  q?: string
  limit?: number
  offset?: number
}

export type Insight = {
  id: number
  kind: string
  title: string
  summary: string
  source_url: string
  source_kind: string
  confidence: number
  fetched_at: string
}

export type Intel = {
  company: string
  role: string | null
  cached: boolean
  source_available: boolean
  insights: Insight[]
}

export type CreateAnalysisInput = {
  file: File
  jobDescription: string
  companyName: string
  roleTitle: string
  roleLevel?: string
  sourceUrl?: string
  llmApiKey?: string
}

type RequestOptions = Omit<RequestInit, 'body'> & {
  token?: string
  body?: BodyInit
  json?: unknown
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { token, json, body, headers, ...rest } = options
  const finalHeaders = new Headers(headers)

  if (token) {
    finalHeaders.set('Authorization', `Bearer ${token}`)
  }

  let payload = body
  if (json !== undefined) {
    finalHeaders.set('Content-Type', 'application/json')
    payload = JSON.stringify(json)
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: finalHeaders,
    body: payload,
  })

  if (!response.ok) {
    let detail = response.statusText
    const contentType = response.headers.get('content-type') ?? ''
    if (contentType.includes('application/json')) {
      const data = (await response.json()) as { detail?: unknown }
      detail =
        typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    }
    throw new ApiError(detail || 'Request failed', response.status)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return (await response.json()) as T
}

export function registerUser(email: string, password: string): Promise<User> {
  return request<User>('/api/auth/register', {
    method: 'POST',
    json: { email, password },
  })
}

export function loginUser(email: string, password: string): Promise<string> {
  return request<{ access_token: string }>('/api/auth/login', {
    method: 'POST',
    json: { email, password },
  }).then((data) => data.access_token)
}

export function fetchMe(token: string): Promise<User> {
  return request<User>('/api/auth/me', { token })
}

export function createAnalysis(
  token: string,
  input: CreateAnalysisInput,
): Promise<Analysis> {
  const form = new FormData()
  form.append('file', input.file)
  form.append('job_description', input.jobDescription)
  form.append('company_name', input.companyName)
  form.append('role_title', input.roleTitle)
  if (input.roleLevel) form.append('role_level', input.roleLevel)
  if (input.sourceUrl) form.append('source_url', input.sourceUrl)

  return request<Analysis>('/api/analyses', {
    method: 'POST',
    token,
    body: form,
    headers: input.llmApiKey ? { 'X-LLM-API-Key': input.llmApiKey } : undefined,
  })
}

export function listAnalyses(
  token: string,
  query: HistoryQuery = {},
): Promise<AnalysisHistory> {
  const params = new URLSearchParams()
  if (query.q) params.set('q', query.q)
  if (query.limit) params.set('limit', String(query.limit))
  if (query.offset) params.set('offset', String(query.offset))
  const search = params.toString()
  return request<AnalysisHistory>(`/api/analyses${search ? `?${search}` : ''}`, {
    token,
  })
}

export function getAnalysis(token: string, id: number): Promise<Analysis> {
  return request<Analysis>(`/api/analyses/${id}`, { token })
}

export function reanalyze(
  token: string,
  id: number,
  rawText: string,
  llmApiKey?: string,
): Promise<Analysis> {
  return request<Analysis>(`/api/analyses/${id}/reanalyze`, {
    method: 'POST',
    token,
    json: { raw_text: rawText },
    headers: llmApiKey ? { 'X-LLM-API-Key': llmApiKey } : undefined,
  })
}

export async function exportResume(token: string, id: number): Promise<Blob> {
  const response = await fetch(`${API_BASE}/api/analyses/${id}/export`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new ApiError('Export failed', response.status)
  }
  return response.blob()
}

export function getIntel(
  token: string,
  company: string,
  role?: string | null,
  refresh = false,
): Promise<Intel> {
  const params = new URLSearchParams({ company })
  if (role) params.set('role', role)
  if (refresh) params.set('refresh', 'true')
  return request<Intel>(`/api/intel?${params.toString()}`, { token })
}
