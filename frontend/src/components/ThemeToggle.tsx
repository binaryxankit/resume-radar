import { MoonIcon, SunIcon } from './icons'
import { useTheme } from '../lib/theme-context'

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light theme' : 'Switch to dark theme'}
      className="grid size-9 place-items-center rounded-lg border border-border text-muted transition hover:bg-surface-2 hover:text-foreground focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
    >
      {isDark ? <SunIcon className="size-4.5" /> : <MoonIcon className="size-4.5" />}
    </button>
  )
}
