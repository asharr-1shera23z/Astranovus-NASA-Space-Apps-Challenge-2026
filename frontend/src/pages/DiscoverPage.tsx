import { useEffect, useMemo, useState } from 'react';
import { fetchCompare, fetchScoredCells, fetchTargets } from '../api/client';
import { DataCoverageStrip, SyntheticDataWarning } from '../components/DataBanners';
import { LeafletAnalogMap } from '../components/LeafletAnalogMap';
import { ErrorPanel, InfoNote, LoadingPanel } from '../components/StatusViews';
import { useMission } from '../state/MissionContext';
import type { BackendTarget, CompareResponse, HeatmapPoint, ScoredCell } from '../types/astranovus';
import { bodyLabel, formatCoords, pct } from '../utils/mission';

export function DiscoverPage() {
  const m = useMission();
  const [targets, setTargets] = useState<BackendTarget[]>([]);
  const [targetId, setTargetId] = useState<string>(m.targetId ?? '');
  const [cells, setCells] = useState<ScoredCell[] | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [minCov, setMinCov] = useState(0.5);
  const [selected, setSelected] = useState<string | null>(null);
  const [cmp, setCmp] = useState<CompareResponse | null>(null);
  const [tick, setTick] = useState(0);

  useEffect(() => {
    const ac = new AbortController();
    fetchTargets(ac.signal)
      .then((t) => {
        setTargets(t);
        setTargetId((cur) => cur || t[0]?.id || '');
      })
      .catch((e: Error) => e.name !== 'AbortError' && setErr(e.message));
    return () => ac.abort();
  }, [tick]);

  useEffect(() => {
    if (!targetId) return;
    const ac = new AbortController();
    setCells(null);
    setErr(null);
    setSelected(null);
    setCmp(null);
    fetchScoredCells(targetId, 5000, ac.signal)
      .then(setCells)
      .catch((e: Error) => e.name !== 'AbortError' && setErr(e.message));
    return () => ac.abort();
  }, [targetId, tick]);

  const target = targets.find((t) => t.id === targetId);
  const body = target ? bodyLabel(target.body) : 'Moon';

  const shown = useMemo(() => (cells ?? []).filter((c) => c.coverage >= minCov), [cells, minCov]);
  const heat: HeatmapPoint[] = useMemo(
    () => shown.map((c) => ({ lat: c.lat, lon: c.lon, intensity: Math.max(0, Math.min(1, c.score / 100)), region_name: '', cluster_id: String(c.cell_id) })),
    [shown]
  );
  const top = useMemo(() => [...shown].sort((a, b) => b.score - a.score).slice(0, 10), [shown]);

  useEffect(() => {
    if (!selected) return;
    const c = top.find((x) => String(x.cell_id) === selected) ?? shown.find((x) => String(x.cell_id) === selected);
    if (!c) return;
    const ac = new AbortController();
    setCmp(null);
    fetchCompare(c.lat, c.lon, ac.signal)
      .then(setCmp)
      .catch(() => undefined);
    return () => ac.abort();
  }, [selected]); // eslint-disable-line react-hooks/exhaustive-deps

  const grouped = (b: 'moon' | 'mars') => targets.filter((t) => t.body === b);

  return (
    <div className="max-w-[1440px] mx-auto px-4 sm:px-8 py-8 space-y-6">
      <div className="space-y-2">
        <h1 className="font-display font-extrabold text-2xl text-[#142B50]">Global similarity heatmap</h1>
        <p className="text-sm text-[#68788F] max-w-3xl">
          How closely every loaded Earth cell resembles one reference site, using that site&apos;s default weights. This is the engine&apos;s generic{' '}
          <span className="font-mono">/score</span> output: it has no experiment-specific multipliers or gates. For mission-specific answers use Explore.
        </p>
        <SyntheticDataWarning />
        <DataCoverageStrip />
        <InfoNote tone="warn">
          Cells with a low coverage value are scored on only a few dimensions and are less trustworthy. Use the slider to hide them. Scores come from the
          engine unchanged; this page only draws them.
        </InfoNote>
      </div>

      <div className="flex flex-wrap items-end gap-4">
        <div>
          <label htmlFor="disc-target" className="block text-[11px] font-semibold text-[#68788F] mb-1">
            Reference site
          </label>
          <select
            id="disc-target"
            value={targetId}
            onChange={(e) => setTargetId(e.target.value)}
            className="bg-[#EDF3FA] border border-[#E1E8F0] text-[#142B50] text-xs font-semibold rounded-lg px-3 py-2"
          >
            <optgroup label="Moon">
              {grouped('moon').map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </optgroup>
            <optgroup label="Mars">
              {grouped('mars').map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </optgroup>
          </select>
        </div>
        <div className="min-w-[240px]">
          <label htmlFor="disc-cov" className="block text-[11px] font-semibold text-[#68788F] mb-1">
            Minimum data coverage: <span className="font-mono text-[#142B50]">{pct(minCov)}</span>
          </label>
          <input
            id="disc-cov"
            type="range"
            min={0}
            max={1}
            step={0.05}
            value={minCov}
            onChange={(e) => setMinCov(Number(e.target.value))}
            className="astranovus-slider w-full"
          />
        </div>
        {cells && (
          <div className="text-xs text-[#68788F]">
            {shown.length} of {cells.length} cells shown
          </div>
        )}
      </div>

      {err && <ErrorPanel message={err} onRetry={() => setTick((t) => t + 1)} />}
      {!err && !cells && <LoadingPanel message="Scoring every Earth cell..." />}

      {cells && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          <div className="lg:col-span-8">
            <LeafletAnalogMap
              markers={top.map((c, i) => ({
                id: String(c.cell_id),
                name: `#${i + 1} cell ${formatCoords(c.lat, c.lon)}`,
                country: 'Grid cell',
                lat: c.lat,
                lon: c.lon,
                score: c.score,
                coverage: c.coverage * 100,
                role: 'top cell',
                published: false,
              }))}
              selectedId={selected}
              onSelectMarker={setSelected}
              heatmapPoints={heat}
              bodyTheme={body as 'Moon' | 'Mars'}
              heightClass="h-[460px] lg:h-[620px]"
            />
          </div>
          <div className="lg:col-span-4 space-y-4">
            <div className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-xl p-4 space-y-2">
              <h2 className="font-display font-bold text-sm text-[#142B50]">Top 10 cells for {target?.name ?? targetId}</h2>
              {top.length === 0 && <p className="text-xs text-[#68788F]">No cell meets the coverage threshold.</p>}
              <ol className="divide-y divide-[#E6ECF3]">
                {top.map((c, i) => {
                  const on = selected === String(c.cell_id);
                  return (
                    <li key={c.cell_id}>
                      <button
                        type="button"
                        onClick={() => setSelected(String(c.cell_id))}
                        aria-pressed={on}
                        className={`w-full text-left py-2 px-2 rounded-md flex items-center justify-between gap-2 text-xs ${on ? 'bg-[#EDF3FA]' : 'hover:bg-[#F4F8FF]'}`}
                      >
                        <span className="font-semibold text-[#142B50]">
                          #{i + 1} · {formatCoords(c.lat, c.lon)}
                        </span>
                        <span className="font-mono tabular-nums text-[#0B5ED7]">
                          {c.score.toFixed(1)} <span className="text-[#68788F]">· cov {pct(c.coverage)}</span>
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ol>
            </div>
            {selected && (
              <div className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-xl p-4 space-y-2">
                <h2 className="font-display font-bold text-sm text-[#142B50]">Selected cell vs every reference site</h2>
                {!cmp && <p className="text-xs text-[#68788F]">Loading...</p>}
                {cmp && (
                  <ul className="space-y-1.5">
                    {cmp.scores
                      .slice()
                      .sort((a, b) => (b.score ?? -1) - (a.score ?? -1))
                      .map((s) => (
                        <li key={s.target} className="flex items-center justify-between gap-2 text-[11px]">
                          <span className="truncate text-[#142B50]">{s.name}</span>
                          <span className="font-mono tabular-nums text-[#0B5ED7]">{s.score === null ? 'n/a' : s.score.toFixed(1)}</span>
                        </li>
                      ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
