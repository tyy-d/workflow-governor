type IconName = 'workflow' | 'target' | 'chevron' | 'file' | 'clock' | 'shield' | 'person' | 'check' | 'panel' | 'search'

const paths: Record<IconName, React.ReactNode> = {
  workflow: <><rect x="3" y="3" width="6" height="6" rx="1"/><rect x="15" y="15" width="6" height="6" rx="1"/><path d="M9 6h4a4 4 0 0 1 4 4v5M15 18h-4a4 4 0 0 1-4-4V9"/></>,
  target: <><circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="M17.7 6.3 21 3M18 3h3v3"/></>,
  chevron: <path d="m9 18 6-6-6-6"/>,
  file: <><path d="M6 2h8l4 4v16H6z"/><path d="M14 2v5h5M9 12h6M9 16h6"/></>,
  clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></>,
  shield: <><path d="M12 3 4.5 6v5.5c0 4.8 3 8 7.5 9.5 4.5-1.5 7.5-4.7 7.5-9.5V6z"/><path d="m9 12 2 2 4-4"/></>,
  person: <><circle cx="12" cy="8" r="3"/><path d="M5 21c.5-5 3-7 7-7s6.5 2 7 7"/></>,
  check: <path d="m5 12 4 4L19 6"/>,
  panel: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16M9 10h12"/></>,
  search: <><circle cx="11" cy="11" r="7"/><path d="m16 16 4 4"/></>,
}

export function Icon({ name, size = 18 }: { name: IconName; size?: number }) {
  return <svg className="icon" width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>
}
