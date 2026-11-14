import { Download, Globe2, Map as MapIcon } from 'lucide-react';
import { lazy, Suspense, useMemo, useState } from 'react';
import { useMission } from '../state/MissionContext';
import type { Region } from '../types/astranovus';
import { BODY_ACCENT, bodyLabel, buildRegionsCsv, dimLabel, pct, regionsToMapSites } from '../utils/mission';
import { LeafletAnalogMap } from './LeafletAnalogMap';
import { RegionDetail } from './RegionDetail';
import { ErrorPanel, InfoNote, LoadingPanel, StateChip } from './StatusViews';

const EarthAnalogGlobe = lazy(() => import('./EarthAnalogGlobe').then((m) => ({ default: m.EarthAnalogGlobe })));

const CONF_STYLE = {
  high: 'bg-[#EAF7EE] text-[#177A3C] border-[#177A3C]/25',
  medium: 'bg-[#FFF4E5] text-[#A15C00] border-[#A15C00]/30',
  low: 'bg-[#FDECEC] text-[#B42318] border-[#B42318]/25',
} as const;

function downloadCsv(regions: Region[], name: string) {
  const blob = new Blob([buildRegionsCsv(regions)], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `astranovus_${name}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

export function ResultsPanel({ onOpenProfile }: { onOpenProfile: () => void }) {
  const m = useMission();
  const { result, resultStatus, resultError, experiment, targetId } = m;
  const [view, setView] = useState<'map' | 'globe'>('map');

  const sites = useMemo(() => (result ? regionsToMapSites(result.regions) : []), [result]);

  if (resultStatus === 'loading' && !result) {
    return <LoadingPanel message="Asking the ASTRANOVUS engine for the best Earth regions..." />;
  }
  if (resultStatus === 'error') {
    return <ErrorPanel title="Recommendation failed" message={resultError ?? 'Unknown error'} onRetry={() => m.setTarget(targetId!)} />;
  }
  if (!result || !experiment) return null;

  const body = result.experiment.body;
  const accent = BODY_ACCENT[body];
  const unavailable = result.data_state === 'unavailable' && !result.provisional;
  const others = result.allowed_targets.filter((t) => t.id !== result.target_info.id);
  const selected = m.selectedRegion;

  return (
    <div className="space-y-5" aria-live="polite">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <div className="text-xs font-semibold" style={{ color: accent }}>
            Step 4 · Earth analog recommendations
          </div>
          <h2 className="font-display font-bold text-2xl text-[#142B50]">{experiment.name}</h2>
          <p className="text-sm text-[#68788F]">
            {bodyLabel(body)} reference site: <strong className="text-[#142B50]">{result.target_info.name}</strong> · mission profile{' '}
            <span className="font-mono">{experiment.purpose.id}</span> · {result.n_cells_passed} cells passed the gates
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StateChip state={result.provisional ? 'unavailable' : result.data_state} />
          {result.regions.length > 0 && (
            <button
              type="button"
              onClick={() => downloadCsv(result.regions, `${experiment.id}_${result.target_info.id}`)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E1E8F0] bg-[#FFFFFF] text-xs font-semibold text-[#142B50] hover:border-[#0B5ED7]"
            >
              <Download className="w-3.5 h-3.5" /> CSV
            </button>
          )}
        </div>
      </div>

      {result.target_info.is_draft && (
        <InfoNote tone="warn">
          <strong>Draft reference profile.</strong> The rules describing &ldquo;{result.target_info.name}&rdquo; are v0 team drafts written from general
          literature. Evidence status: <strong>{result.target_info.evidence.grounded} of {result.target_info.evidence.total}</strong> rules have a retrieved
          source (qualitative direction only; no LOLA, MOLA, Diviner or CRISM values are used in scoring). Rankings are only as good as this profile.
        </InfoNote>
      )}

      {unavailable && (
        <div role="alert" className="bg-[#FFFFFF] border-2 border-[#B42318]/50 rounded-2xl p-6 space-y-4">
          <div>
            <h3 className="font-display font-bold text-lg text-[#7A1A12]">Not enough real data yet for this experiment</h3>
            <p className="text-sm text-[#142B50] mt-1">
              ASTRANOVUS does not invent recommendations. The Earth grid currently covers{' '}
              <strong>{pct(result.assessment.max_coverage)}</strong> of the criteria this experiment weighs, and at least one required check cannot be
              verified.
            </p>
          </div>
          <ul className="list-disc pl-5 text-xs text-[#7A1A12] space-y-1">
            {result.assessment.notes.map((n) => (
              <li key={n}>{n}</li>
            ))}
          </ul>
          <div className="text-xs text-[#142B50]">
            <strong>Dimensions with no data yet:</strong> {result.assessment.missing_dimensions.map(dimLabel).join(', ') || 'none'}. These are waiting for
            real NASA dataset integration (see Methodology).
          </div>
          {others.length > 0 && (
            <div className="flex flex-wrap gap-2 items-center text-xs">
              <span className="text-[#68788F]">Other compatible reference sites:</span>
              {others.map((t) => (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => m.setTarget(t.id)}
                  className="px-3 py-1.5 rounded-lg border border-[#E1E8F0] bg-[#F4F8FF] font-semibold text-[#142B50] hover:border-[#0B5ED7]"
                >
                  {t.name} · <StateChip state={t.readiness.state} />
                </button>
              ))}
            </div>
          )}
          <button
            type="button"
            onClick={() => m.setAllowUnverified(true)}
            className="px-4 py-2 rounded-lg border border-[#B42318] text-[#B42318] text-xs font-semibold hover:bg-[#FDECEC]"
          >
            Show provisional ranking from available dimensions only (unverified)
          </button>
        </div>
      )}

      {result.provisional && (
        <InfoNote tone="danger">
          <strong>PROVISIONAL, UNVERIFIED.</strong> Required checks cannot be performed because their data is missing:{' '}
          {result.assessment.gate_dimensions_missing.map(dimLabel).join(', ') || 'coverage is below the minimum'}. The ranking uses only the
          dimensions that have data.{' '}
          <button type="button" className="underline font-semibold" onClick={() => m.setAllowUnverified(false)}>
            Hide provisional results
          </button>
        </InfoNote>
      )}

      {!unavailable && result.data_state === 'partial' && (
        <InfoNote tone="warn">
          <strong>Partial data.</strong> Scores use only the dimensions that have data ({pct(result.assessment.max_coverage)} of this experiment&apos;s weighted
          criteria).
          {result.assessment.missing_dimensions.length > 0 && <> Not yet assessed: {result.assessment.missing_dimensions.map(dimLabel).join(', ')}.</>}
          {result.assessment.proxy_dimensions.length > 0 && <> Proxy (not a direct measurement): {result.assessment.proxy_dimensions.map(dimLabel).join(', ')}.</>}
        </InfoNote>
      )}

      {!unavailable && result.regions.length === 0 && (
        <InfoNote>
          No region passed this mission&apos;s gates and the minimum coverage. Try another reference site for this experiment.
        </InfoNote>
      )}

      {result.regions.length > 0 && (
        <>
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
            <div className="lg:col-span-5 space-y-3 lg:max-h-[640px] lg:overflow-y-auto lg:pr-1" role="list" aria-label="Ranked Earth regions">
              {result.regions.map((r) => {
                const isSel = r.id === m.selectedRegionId;
                const strong = r.dimensions.filter((d) => (d.similarity ?? 0) >= 0.7).slice(0, 3);
                const miss = r.dimensions.filter((d) => d.similarity === null);
                return (
                  <div
                    key={r.id}
                    role="listitem"
                    className="rounded-xl bg-[#FFFFFF] border transition-all"
                    style={{ borderColor: isSel ? accent : '#E1E8F0', borderWidth: isSel ? 2 : 1 }}
                  >
                    <button
                      type="button"
                      onClick={() => m.selectRegion(r.id)}
                      aria-pressed={isSel}
                      className="w-full text-left p-4 space-y-2 focus:outline-none focus-visible:ring-2 focus-visible:ring-[#0B5ED7] rounded-xl"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="min-w-0">
                          <div className="text-[11px] font-semibold text-[#68788F]">Rank #{r.rank}</div>
                          <div className="font-display font-bold text-sm text-[#142B50] leading-snug">{r.location_label}</div>
                        </div>
                        <div className="text-right shrink-0">
                          <div className="font-mono font-bold text-xl tabular-nums" style={{ color: accent }}>
                            {r.best_score.toFixed(1)}
                          </div>
                          <div className="text-[10px] text-[#68788F]">/ 100 similarity</div>
                        </div>
                      </div>
                      <div className="flex flex-wrap gap-1.5 text-[10px] font-semibold">
                        <span className={`px-2 py-0.5 rounded-full border ${CONF_STYLE[r.confidence]}`}>{r.confidence} confidence</span>
                        <span className="px-2 py-0.5 rounded-full border border-[#E1E8F0] bg-[#F4F8FF] text-[#142B50]">coverage {pct(r.coverage)}</span>
                        <span className="px-2 py-0.5 rounded-full border border-[#E1E8F0] bg-[#F4F8FF] text-[#142B50]">{r.n_cells} cells</span>
                      </div>
                      <div className="text-[11px] text-[#68788F] leading-snug">
                        {strong.length > 0 && (
                          <span>
                            <strong className="text-[#177A3C]">Strong:</strong> {strong.map((d) => d.name).join(', ')}.{' '}
                          </span>
                        )}
                        {miss.length > 0 && (
                          <span>
                            <strong className="text-[#B42318]">Not assessed:</strong> {miss.map((d) => d.name).join(', ')}.
                          </span>
                        )}
                      </div>
                    </button>
                    <label className="flex items-center gap-2 px-4 pb-3 text-[11px] text-[#68788F] cursor-pointer">
                      <input type="checkbox" checked={m.compareIds.includes(r.id)} onChange={() => m.toggleCompare(r.id)} className="accent-[#0B5ED7]" />
                      Add to comparison
                    </label>
                  </div>
                );
              })}
            </div>

            <div className="lg:col-span-7 space-y-3">
              <div role="group" aria-label="Map view" className="inline-flex glass-light-hud rounded-lg p-0.5">
                {(
                  [
                    ['map', 'Map', MapIcon],
                    ['globe', '3D Globe', Globe2],
                  ] as const
                ).map(([id, label, Icon]) => (
                  <button
                    key={id}
                    type="button"
                    onClick={() => setView(id)}
                    aria-pressed={view === id}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-semibold ${
                      view === id ? 'bg-[#0B5ED7] text-[#FFFFFF]' : 'text-[#142B50] hover:bg-[#EDF3FA]'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" /> {label}
                  </button>
                ))}
              </div>
              {view === 'map' ? (
                <LeafletAnalogMap
                  markers={sites.map((s) => ({
                    id: s.id,
                    name: s.region,
                    country: s.country || 'Recommended region',
                    lat: s.lat,
                    lon: s.lon,
                    score: s.overall_score,
                    coverage: s.data_coverage,
                    role: s.role,
                    published: false,
                  }))}
                  selectedId={m.selectedRegionId}
                  onSelectMarker={m.selectRegion}
                  bodyTheme={bodyLabel(body)}
                  heightClass="h-[420px] lg:h-[560px]"
                />
              ) : (
                <Suspense fallback={<LoadingPanel message="Loading 3D globe..." />}>
                  <EarthAnalogGlobe
                    sites={sites}
                    selectedTarget={{ id: result.target_info.id, body: bodyLabel(body) }}
                    selectedSiteId={m.selectedRegionId}
                    onSelectSite={m.selectRegion}
                    onOpenProfile={(id) => {
                      m.selectRegion(id);
                      onOpenProfile();
                    }}
                    heightClass="h-[420px] lg:h-[560px]"
                  />
                </Suspense>
              )}
            </div>
          </div>

          {selected && (
            <RegionDetail
              region={selected}
              result={result}
              inCompare={m.compareIds.includes(selected.id)}
              onToggleCompare={() => m.toggleCompare(selected.id)}
              onOpenProfile={onOpenProfile}
            />
          )}
        </>
      )}
    </div>
  );
}
