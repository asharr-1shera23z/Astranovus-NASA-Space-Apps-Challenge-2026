import {
  Building2,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  FlaskConical,
  Microscope,
  Navigation,
  Pickaxe,
  Snowflake,
  Sun,
  Users,
  Wind,
  type LucideIcon,
} from 'lucide-react';
import { useState } from 'react';
import type { DataState, Experiment } from '../types/astranovus';
import { DOC_LEVEL_LABEL, DOC_LEVEL_STYLE } from '../utils/mission';
import { StateChip } from './StatusViews';

const ICONS: Record<string, LucideIcon> = {
  MOON_WATER_ICE: Snowflake,
  MARS_SUBSURFACE_ICE: Snowflake,
  MOON_ROVER_MOBILITY: Navigation,
  MARS_ROVER_MOBILITY: Navigation,
  MOON_REGOLITH_DUST: Wind,
  MARS_DUST_THERMAL: Wind,
  MOON_POWER_THERMAL: Sun,
  MOON_HABITAT_OPS: Building2,
  MARS_CREW_OPS: Users,
  MOON_GEO_FIELDWORK: Pickaxe,
  MARS_GEOLOGY_SAMPLING: Pickaxe,
  MARS_ASTROBIOLOGY: Microscope,
};

const ORDER: DataState[] = ['ready', 'partial', 'unavailable'];

/** Best data state across the experiment's compatible reference sites. */
export function bestState(e: Experiment): DataState {
  const states = e.allowed_targets.map((t) => t.readiness.state);
  return ORDER.find((s) => states.includes(s)) ?? 'unavailable';
}

interface Props {
  experiment: Experiment;
  selected: boolean;
  onSelect: () => void;
}

export function ExperimentCard({ experiment: e, selected, onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const Icon = ICONS[e.id] ?? FlaskConical;
  const accent = e.body === 'mars' ? '#F28B45' : '#0B5ED7';

  return (
    <div
      className={`rounded-xl border bg-[#FFFFFF] transition-all flex flex-col ${
        selected ? 'shadow-md' : 'hover:border-[#0B5ED7]/60'
      }`}
      style={{ borderColor: selected ? accent : '#E1E8F0', borderWidth: selected ? 2 : 1 }}
    >
      <button
        type="button"
        onClick={onSelect}
        aria-pressed={selected}
        className="text-left p-4 space-y-2.5 flex-1 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0B5ED7] rounded-t-xl"
      >
        <div className="flex items-start gap-3">
          <span
            className="w-9 h-9 rounded-lg flex items-center justify-center shrink-0 text-[#FFFFFF]"
            style={{ backgroundColor: accent }}
            aria-hidden="true"
          >
            <Icon className="w-5 h-5" />
          </span>
          <div className="min-w-0">
            <h3 className="font-display font-bold text-sm text-[#142B50] leading-snug">{e.name}</h3>
            <div className="mt-1 flex flex-wrap gap-1.5">
              <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold ${DOC_LEVEL_STYLE[e.nasa_documented.level]}`}>
                {DOC_LEVEL_LABEL[e.nasa_documented.level]}
              </span>
              <StateChip state={bestState(e)} />
            </div>
          </div>
        </div>
        <p className="text-xs text-[#68788F] leading-relaxed">{e.what_is_tested}</p>
        <div className="flex flex-wrap gap-1.5">
          {e.environment_requirements.map((r) => (
            <span key={r} className="px-2 py-0.5 rounded bg-[#EDF3FA] text-[10px] font-medium text-[#142B50]">
              {r}
            </span>
          ))}
        </div>
      </button>

      <div className="border-t border-[#E6ECF3]">
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
          className="w-full flex items-center justify-between px-4 py-2 text-[11px] font-semibold text-[#0B5ED7] hover:bg-[#F4F8FF] rounded-b-xl"
        >
          <span>Why it matters, NASA basis &amp; limits</span>
          {open ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
        {open && (
          <div className="px-4 pb-4 space-y-3 text-xs text-[#142B50] leading-relaxed">
            <p>
              <strong>Why:</strong> {e.why}
            </p>
            <div>
              <strong>NASA basis ({DOC_LEVEL_LABEL[e.nasa_documented.level]}):</strong> {e.nasa_documented.summary}
              <ul className="mt-1.5 space-y-1">
                {e.nasa_documented.sources.map((s) => (
                  <li key={s.id}>
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-[#0B5ED7] font-semibold hover:underline"
                    >
                      {s.label}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
            {e.draft_assumption && (
              <p className="bg-[#FFF4E5] border border-[#A15C00]/30 rounded-lg px-3 py-2 text-[#6B3F00]">
                <strong>Draft assumption:</strong> {e.draft_assumption}
              </p>
            )}
            {e.shares_profile_note && <p className="text-[#68788F]">{e.shares_profile_note}</p>}
            <div>
              <strong>Cannot be reproduced on Earth:</strong>
              <ul className="list-disc pl-5 mt-1 text-[#68788F] space-y-0.5">
                {e.cannot_reproduce.map((c) => (
                  <li key={c}>{c}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
