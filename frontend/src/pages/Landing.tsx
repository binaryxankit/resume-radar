import type { ComponentType, SVGProps } from 'react'

import {
  ArrowRightIcon,
  BuildingIcon,
  CheckIcon,
  FileIcon,
  GithubIcon,
  ScanIcon,
  ShieldIcon,
  SparklesIcon,
  TargetIcon,
  WandIcon,
  ZapIcon,
} from '../components/icons'
import { Logo } from '../components/Logo'
import { ThemeToggle } from '../components/ThemeToggle'

type IconComponent = ComponentType<SVGProps<SVGSVGElement>>

const navLinks = [
  { label: 'Product', href: '#product' },
  { label: 'How it works', href: '#how' },
  { label: 'Intel', href: '#intel' },
]

const features: { icon: IconComponent; title: string; body: string }[] = [
  {
    icon: ScanIcon,
    title: 'ATS simulation',
    body: 'See how a parser reads your resume: section detection, keyword coverage and formatting warnings, scored transparently.',
  },
  {
    icon: TargetIcon,
    title: 'Job-targeted scoring',
    body: 'Paste a job description and every suggestion is ranked against that role, not a generic template.',
  },
  {
    icon: WandIcon,
    title: 'Inline rewriting',
    body: 'Accept or reject each fix in a diff editor. Every save is a version, so nothing is ever lost.',
  },
  {
    icon: BuildingIcon,
    title: 'Company intel',
    body: 'Interview themes, role signals and the people who matter, cached per company and role.',
  },
]

const steps: { icon: IconComponent; title: string; body: string }[] = [
  {
    icon: FileIcon,
    title: 'Upload your resume',
    body: 'PDF or DOCX. We extract clean text and detect your sections.',
  },
  {
    icon: TargetIcon,
    title: 'Target the role',
    body: 'Paste the job description so analysis is anchored to what matters.',
  },
  {
    icon: SparklesIcon,
    title: 'Fix what matters',
    body: 'Get a ranked gap list, rewrite inline and export when ready.',
  },
]

const suggestions = [
  { tone: 'critical', label: 'Critical', text: 'Add measurable impact to 3 bullet points' },
  { tone: 'warning', label: 'Missing', text: 'Keywords: distributed systems, Kafka, SLOs' },
  { tone: 'good', label: 'Good', text: 'Structure and contact block parse cleanly' },
]

const currentYear = new Date().getFullYear()

const toneStyles: Record<string, string> = {
  critical: 'bg-danger',
  warning: 'bg-warning',
  good: 'bg-success',
}

const signalRows = [
  { label: 'Parser health', value: '96', width: '96%', tone: 'bg-success' },
  { label: 'Keyword coverage', value: '74', width: '74%', tone: 'bg-primary' },
  { label: 'Impact density', value: '61', width: '61%', tone: 'bg-warning' },
]

export function Landing() {
  return (
    <div id="top" className="relative min-h-svh overflow-x-hidden">
      <div
        aria-hidden
        className="pointer-events-none absolute inset-x-0 top-0 -z-10 h-[560px]"
        style={{
          background:
            'radial-gradient(60% 60% at 50% 0%, color-mix(in oklab, var(--primary) 18%, transparent), transparent 70%)',
        }}
      />

      <SiteHeader />

      <main className="mx-auto max-w-6xl px-6">
        <section className="grid items-center gap-14 py-20 lg:grid-cols-[1.05fr_0.95fr] lg:py-28">
          <div>
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs font-medium text-muted">
              <SparklesIcon className="size-3.5 text-primary" />
              AI resume intelligence
            </span>

            <h1 className="mt-6 text-balance text-5xl font-semibold leading-[1.05] tracking-tight sm:text-6xl">
              Tune your resume to the{' '}
              <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                job
              </span>
              , not the template.
            </h1>

            <p className="mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted">
              ResumeRadar parses your resume, simulates ATS screening against a real job
              description and rewrites the gaps, with the company intel that actually matters.
            </p>

            <div className="mt-8 flex flex-wrap items-center gap-3">
              <a
                href="#how"
                className="inline-flex items-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-semibold text-primary-fg shadow-lg shadow-primary/20 transition hover:opacity-90"
              >
                Analyze my resume
                <ArrowRightIcon className="size-4" />
              </a>
              <a
                href="#product"
                className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface px-5 py-3 text-sm font-semibold transition hover:bg-surface-2"
              >
                See how it works
              </a>
            </div>

            <ul className="mt-8 flex flex-wrap gap-x-6 gap-y-2 text-xs text-muted">
              <li className="inline-flex items-center gap-1.5">
                <CheckIcon className="size-3.5 text-success" /> ATS-transparent scoring
              </li>
              <li className="inline-flex items-center gap-1.5">
                <CheckIcon className="size-3.5 text-success" /> No LinkedIn scraping
              </li>
              <li className="inline-flex items-center gap-1.5">
                <CheckIcon className="size-3.5 text-success" /> Your data stays yours
              </li>
            </ul>
          </div>

          <AnalysisCard />
        </section>

        <section id="product" className="border-t border-border py-20">
          <div className="max-w-2xl">
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
              Product
            </p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
              Everything anchored to a target role
            </h2>
            <p className="mt-4 text-muted">
              Most resume tools give generic advice. ResumeRadar ties every suggestion to a
              specific job, company and version of your resume.
            </p>
          </div>

          <div className="mt-10 grid gap-4 sm:grid-cols-2">
            {features.map(({ icon: Icon, title, body }) => (
              <article
                key={title}
                className="group rounded-2xl border border-border bg-surface p-6 transition hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
              >
                <span className="grid size-10 place-items-center rounded-xl bg-primary/10 text-primary ring-1 ring-primary/15">
                  <Icon className="size-5" />
                </span>
                <h3 className="mt-4 font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="how" className="border-t border-border py-20">
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div className="max-w-xl">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                How it works
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
                Three steps to a sharper resume
              </h2>
            </div>
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-surface px-3 py-1.5 text-xs text-muted">
              <ZapIcon className="size-3.5 text-warning" /> First analysis in under a minute
            </span>
          </div>

          <div className="mt-10 grid gap-4 md:grid-cols-3">
            {steps.map(({ icon: Icon, title, body }, index) => (
              <article
                key={title}
                className="relative rounded-2xl border border-border bg-surface p-6"
              >
                <span className="absolute right-5 top-5 text-4xl font-semibold text-border">
                  {String(index + 1).padStart(2, '0')}
                </span>
                <span className="grid size-10 place-items-center rounded-xl bg-surface-2 text-foreground ring-1 ring-border">
                  <Icon className="size-5" />
                </span>
                <h3 className="mt-4 font-semibold">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
              </article>
            ))}
          </div>
        </section>

        <section id="intel" className="border-t border-border py-20">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-primary">
                Intel
              </p>
              <h2 className="mt-3 text-3xl font-semibold tracking-tight sm:text-4xl">
                Context beyond the job description
              </h2>
              <p className="mt-4 text-muted">
                We aggregate public and qualitative signals per company and role, then cache
                them with provenance. Reddit interview themes come through the official API.
                Hiring contacts are public-source only.
              </p>
              <ul className="mt-6 space-y-3 text-sm">
                {[
                  'Interview themes and recurring questions',
                  'Role expectations and skill signals',
                  'Public company and team context',
                  'Cached per company and role, timestamped',
                ].map((item) => (
                  <li key={item} className="flex items-start gap-2.5">
                    <CheckIcon className="mt-0.5 size-4 shrink-0 text-success" />
                    <span className="text-muted">{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            <IntelCard />
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  )
}

function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
        <Logo />

        <nav className="hidden items-center gap-8 text-sm text-muted md:flex">
          {navLinks.map((link) => (
            <a key={link.href} href={link.href} className="transition hover:text-foreground">
              {link.label}
            </a>
          ))}
        </nav>

        <div className="flex items-center gap-2.5">
          <a
            href="https://github.com/binaryxankit/resume-radar"
            target="_blank"
            rel="noreferrer"
            aria-label="View source on GitHub"
            className="hidden size-9 place-items-center rounded-lg border border-border text-muted transition hover:bg-surface-2 hover:text-foreground sm:grid"
          >
            <GithubIcon className="size-4.5" />
          </a>
          <ThemeToggle />
          <a
            href="#how"
            className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-fg transition hover:opacity-90"
          >
            Get started
          </a>
        </div>
      </div>
    </header>
  )
}

function AnalysisCard() {
  return (
    <div className="relative">
      <div
        aria-hidden
        className="absolute -inset-4 -z-10 rounded-[2rem] opacity-60 blur-2xl"
        style={{
          background:
            'linear-gradient(135deg, color-mix(in oklab, var(--primary) 30%, transparent), color-mix(in oklab, var(--accent) 30%, transparent))',
        }}
      />

      <div className="rounded-[1.6rem] border border-border bg-surface p-5 shadow-2xl shadow-black/10">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="grid size-9 place-items-center rounded-lg bg-surface-2 text-sm font-semibold ring-1 ring-border">
              S
            </span>
            <div>
              <p className="text-sm font-semibold">Senior Backend Engineer</p>
              <p className="text-xs text-muted">Stripe</p>
            </div>
          </div>
          <span className="rounded-full bg-success/10 px-2.5 py-1 text-xs font-semibold text-success ring-1 ring-success/20">
            82 match
          </span>
        </div>

        <div className="mt-5 grid grid-cols-[auto_1fr] items-center gap-5 rounded-xl border border-border bg-surface-2/60 p-4">
          <ScoreRing value={82} />
          <div>
            <p className="text-sm font-semibold">ATS readiness</p>
            <p className="mt-0.5 text-xs text-muted">Transparent, rule-based heuristic</p>
            <div className="mt-3 space-y-2">
              {signalRows.map((row) => (
                <div key={row.label}>
                  <div className="flex items-center justify-between text-[11px] text-muted">
                    <span>{row.label}</span>
                    <span className="font-medium text-foreground">{row.value}</span>
                  </div>
                  <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-border">
                    <div className={`h-full rounded-full ${row.tone}`} style={{ width: row.width }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="mt-4 space-y-2">
          {suggestions.map((item) => (
            <div
              key={item.text}
              className="flex items-start gap-2.5 rounded-lg border border-border bg-surface px-3 py-2.5"
            >
              <span
                className={`mt-1.5 size-1.5 shrink-0 rounded-full ${toneStyles[item.tone]}`}
              />
              <p className="text-xs leading-relaxed text-muted">
                <span className="mr-1.5 font-semibold text-foreground">{item.label}</span>
                {item.text}
              </p>
            </div>
          ))}
        </div>

        <div className="mt-4 flex items-center justify-between text-xs text-muted">
          <span>12 fixes · 3 critical</span>
          <span className="inline-flex items-center gap-1 font-medium text-primary">
            Review <ArrowRightIcon className="size-3.5" />
          </span>
        </div>
      </div>
    </div>
  )
}

function ScoreRing({ value }: { value: number }) {
  return (
    <div
      className="grid size-24 place-items-center rounded-full"
      style={{
        background: `conic-gradient(var(--primary) 0 ${value}%, var(--surface-2) ${value}% 100%)`,
      }}
    >
      <div className="grid size-[4.6rem] place-items-center rounded-full bg-surface">
        <span className="text-2xl font-semibold tracking-tight">{value}</span>
      </div>
    </div>
  )
}

function IntelCard() {
  return (
    <div className="rounded-[1.6rem] border border-border bg-surface p-5 shadow-xl shadow-black/5">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <BuildingIcon className="size-4 text-primary" />
          Stripe · Backend
        </div>
        <span className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2.5 py-1 text-[11px] font-medium text-primary ring-1 ring-primary/20">
          <ShieldIcon className="size-3" /> Cached
        </span>
      </div>

      <div className="mt-4 space-y-3">
        {[
          { kind: 'Interview', text: 'System design + API reliability deep dives' },
          { kind: 'Signal', text: 'Strong emphasis on idempotency and SLOs' },
          { kind: 'Source', text: 'Reddit r/ExperiencedDevs · 14 threads' },
        ].map((row) => (
          <div key={row.kind} className="flex gap-3">
            <span className="w-20 shrink-0 text-[11px] font-medium uppercase tracking-wide text-muted">
              {row.kind}
            </span>
            <p className="text-sm text-foreground">{row.text}</p>
          </div>
        ))}
      </div>

      <div className="mt-4 rounded-xl border border-border bg-surface-2/60 p-3 text-xs leading-relaxed text-muted">
        Provenance is stored with every insight. Scores are heuristics, not a vendor verdict.
      </div>
    </div>
  )
}

function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-6xl px-6 py-10">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <Logo />
          <div className="flex items-center gap-5 text-sm text-muted">
            <a href="#product" className="transition hover:text-foreground">
              Product
            </a>
            <a href="#how" className="transition hover:text-foreground">
              How it works
            </a>
            <a
              href="https://github.com/binaryxankit/resume-radar"
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 transition hover:text-foreground"
            >
              <GithubIcon className="size-4" /> Source
            </a>
          </div>
        </div>
        <p className="mt-6 max-w-2xl text-xs leading-relaxed text-muted">
          ResumeRadar is an ATS simulator, not an actual ATS. Scores are transparent heuristics.
          No LinkedIn scraping. Reddit data is accessed through the official API.
        </p>
        <p className="mt-4 text-xs text-muted">
          © {currentYear} ResumeRadar. All rights reserved.
        </p>
      </div>
    </footer>
  )
}
