import { RadarIcon } from './icons'

export function Logo() {
  return (
    <a href="#top" className="group flex items-center gap-2.5" aria-label="ResumeRadar home">
      <span className="grid size-9 place-items-center rounded-xl bg-primary/10 ring-1 ring-primary/20 transition group-hover:bg-primary/15">
        <RadarIcon className="size-5 text-primary" />
      </span>
      <span className="text-[15px] font-semibold tracking-tight">
        Resume<span className="text-muted">Radar</span>
      </span>
    </a>
  )
}
