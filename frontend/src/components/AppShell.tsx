import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { useAuth } from '../lib/auth-context'
import { Logo } from './Logo'
import { ThemeToggle } from './ThemeToggle'

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout } = useAuth()

  return (
    <div className="min-h-svh">
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-8">
            <Logo />
            <nav className="hidden items-center gap-6 text-sm text-muted md:flex">
              <Link to="/app" className="transition hover:text-foreground">
                Workspace
              </Link>
              <Link to="/" className="transition hover:text-foreground">
                Home
              </Link>
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {user ? (
              <span className="hidden text-sm text-muted sm:inline">{user.email}</span>
            ) : null}
            <ThemeToggle />
            {user ? (
              <button
                type="button"
                onClick={logout}
                className="rounded-lg border border-border px-3 py-1.5 text-sm font-medium transition hover:bg-surface-2"
              >
                Sign out
              </button>
            ) : (
              <Link
                to="/login"
                className="rounded-lg bg-primary px-3 py-1.5 text-sm font-semibold text-primary-fg transition hover:opacity-90"
              >
                Sign in
              </Link>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  )
}
