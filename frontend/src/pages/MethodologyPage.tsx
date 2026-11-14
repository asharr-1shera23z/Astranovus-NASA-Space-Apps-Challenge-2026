import { ExternalLink } from 'lucide-react';
import { useEffect, useState } from 'react';
import { fetchValidation } from '../api/client';
import type { ValidationResponse } from '../types/astranovus';
import { InfoNote, StatusChip } from '../components/StatusViews';
import { useMission } from '../state/MissionContext';
import { DOC_LEVEL_LABEL, dimLabel } from '../utils/mission';

export function MethodologyPage() {
  const m = useMission();
  const [val, setVal] = useState<ValidationResponse | null>(null);
  useEffect(() => {
    const ac = new AbortController();
    fetchValidation(ac.signal).then(setVal).catch(() => undefined);
    return () => ac.abort();
  }, []);
  const sources = new Map<string, { label: string; url: string }>();
  m.experiments.forEach((e) => e.nasa_documented.sources.forEach((s) => sources.set(s.id, s)));

  return (
    <div className="max-w-[1100px] mx-auto px-4 sm:px-8 py-8 space-y-6">
      <h1 className="font-display font-extrabold text-2xl text-[#142B50]">Methodology &amp; honesty statement</h1>
      <InfoNote>{m.dataStatus?.disclaimer ?? 'ASTRANOVUS scores are team-generated estimates, not official NASA ratings.'}</InfoNote>

      <section className="glass-panel rounded-2xl p-6 space-y-3 text-sm text-[#142B50] leading-relaxed">
        <h2 className="font-display font-bold text-lg">How a recommendation is made</h2>
        <ol className="list-decimal pl-5 space-y-1.5">
          <li>Each Earth land cell has up to eight dimensions, stored as percentile ranks (0-1) among the loaded cells. Empty means no data, never zero.</li>
          <li>A planetary reference site is a set of rules per dimension: <em>high</em> (more is better), <em>low</em> (less is better) or <em>band</em> (best inside a range), each with a weight 0-3.</li>
          <li>The experiment you choose maps to a mission profile that multiplies those weights and adds hard gates (must-haves). Cells failing a gate are dropped.</li>
          <li>Score = 100 × Σ(weight × similarity) / Σ(weight) over dimensions that have data. Coverage is the share of weight that had data.</li>
          <li>The top 15% of passing cells are merged into regions when neighbouring. Confidence is high when coverage ≥ 85% and the region has ≥ 3 cells, medium when coverage ≥ 60%, otherwise low.</li>
          <li>Data-unavailable rule (ASTRANOVUS UI layer): if a gate dimension has no data at all, or under 50% of the weighted criteria have data, no ranking is shown by default. A clearly labelled provisional view can be requested.</li>
        </ol>
        <p className="text-xs text-[#68788F]">All scoring runs in the Python engine (model/scoring_core.py, model/recommend.py). The web app only displays its output.</p>
      </section>

      <section className="glass-panel rounded-2xl p-6 space-y-3">
        <h2 className="font-display font-bold text-lg text-[#142B50]">Earth data status (live from the backend)</h2>
        {m.dataStatus && (
          <p className="text-xs text-[#68788F]">
            Grid file {m.dataStatus.grid.file}: {m.dataStatus.grid.cells} cells{m.dataStatus.grid.step_deg ? ` at ${m.dataStatus.grid.step_deg}° spacing` : ''}, latitude {m.dataStatus.grid.lat_range[0]}° to {m.dataStatus.grid.lat_range[1]}°. {m.dataStatus.values_are}.
          </p>
        )}
        <div className="overflow-x-auto">
          <table className="w-full text-xs min-w-[640px]">
            <thead>
              <tr className="text-left text-[#68788F]">
                <th className="py-2 pr-3">Dimension</th>
                <th className="py-2 pr-3">Status</th>
                <th className="py-2 pr-3">Time span</th>
                <th className="py-2 pr-3">Cells with value</th>
                <th className="py-2">Provenance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E6ECF3] align-top">
              {m.dataStatus?.dimensions.map((d) => (
                <tr key={d.id}>
                  <td className="py-2 pr-3 font-semibold text-[#142B50]">{dimLabel(d.id)}</td>
                  <td className="py-2 pr-3">
                    <StatusChip status={d.status} />
                  </td>
                  <td className="py-2 pr-3 text-[#68788F]">{d.temporal || '-'}</td>
                  <td className="py-2 pr-3 font-mono tabular-nums">{Math.round(d.cell_coverage * 100)}%</td>
                  <td className="py-2 text-[#68788F]">{d.provenance}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="glass-panel rounded-2xl p-6 space-y-3">
        <h2 className="font-display font-bold text-lg text-[#142B50]">Data build and cross-checks</h2>
        {m.dataStatus?.build ? (
          <>
            <p className="text-xs text-[#68788F]">
              Built {m.dataStatus.build.built_utc} from {Object.entries(m.dataStatus.build.products).map(([k, v]) => `${k} ${v}`).join(', ')}. MODIS/GPM months:{' '}
              {m.dataStatus.build.temporal_coverage.MODIS_GPM_months.join(', ')}. {m.dataStatus.build.temporal_coverage.note}
            </p>
            <ul className="text-xs text-[#142B50] space-y-1 list-disc pl-5">
              {Object.entries(m.dataStatus.build.cross_checks).map(([k, v]) => (
                <li key={k}>
                  {k}: Spearman rank correlation <span className="font-mono">{v.spearman}</span> (n={v.n})
                </li>
              ))}
            </ul>
            <p className="text-[11px] text-[#68788F]">A negative correlation means the two independent sources disagree on what that dimension measures; this is why D8 now uses MODIS surface temperatures instead of the earlier POWER air-temperature range.</p>
          </>
        ) : (
          <p className="text-xs text-[#68788F]">No build metadata available.</p>
        )}
      </section>

      <section className="glass-panel rounded-2xl p-6 space-y-3">
        <h2 className="font-display font-bold text-lg text-[#142B50]">Validation against known Earth analogs</h2>
        {!val?.available ? (
          <p className="text-xs text-[#68788F]">{val?.note ?? 'Validation results are not available.'}</p>
        ) : (
          <>
            <p className="text-xs text-[#68788F]">
              Real grid built {val.grid_built_utc}. Sites NASA publishes as analog sites, evaluated at their nearest 5° cell with generic target weights. Held-out
              positives are the headline; no rules were tuned on these sites.
            </p>
            {val.heldout && (
              <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs">
                {[
                  ['Pairs', val.heldout.n],
                  ['Median percentile', val.heldout.median_percentile],
                  ['Top-25% hits', val.heldout.top25_hit_rate],
                  ['AUC vs controls', val.heldout.auc_vs_controls ?? 'n/a'],
                  ['Controls median', val.heldout.controls_median_percentile ?? 'n/a'],
                ].map(([k, v]) => (
                  <div key={String(k)} className="bg-[#F4F8FF] border border-[#E1E8F0] rounded-lg px-3 py-2">
                    <div className="text-[10px] text-[#68788F]">{k}</div>
                    <div className="font-mono font-semibold text-[#142B50]">{v}</div>
                  </div>
                ))}
              </div>
            )}
            <p className="text-[11px] text-[#A15C00]">
              Small sample, easy controls (humid lowlands). Missing terrain and rock data ({val.dimensions_missing?.join(', ')}) limit what this test can show. It is
              indicative, not proof.
            </p>
          </>
        )}
      </section>

      <section className="glass-panel rounded-2xl p-6 space-y-3">
        <h2 className="font-display font-bold text-lg text-[#142B50]">Experiments and mission profiles</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-xs min-w-[640px]">
            <thead>
              <tr className="text-left text-[#68788F]">
                <th className="py-2 pr-3">Experiment</th>
                <th className="py-2 pr-3">Profile</th>
                <th className="py-2 pr-3">Weight multipliers</th>
                <th className="py-2 pr-3">Gates</th>
                <th className="py-2">NASA basis</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E6ECF3] align-top">
              {m.experiments.map((e) => (
                <tr key={e.id}>
                  <td className="py-2 pr-3 font-semibold text-[#142B50]">{e.name}</td>
                  <td className="py-2 pr-3 font-mono">{e.purpose.id}</td>
                  <td className="py-2 pr-3 font-mono">{Object.entries(e.purpose.multipliers).map(([k, v]) => `${dimLabel(k)}×${v}`).join(', ') || '-'}</td>
                  <td className="py-2 pr-3">{e.purpose.gates.map((g) => `${dimLabel(g.dim)} ${g.op} ${g.value}`).join('; ') || 'none'}</td>
                  <td className="py-2 text-[#68788F]">{DOC_LEVEL_LABEL[e.nasa_documented.level]}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {m.experimentsMeta && (
          <ul className="text-[11px] text-[#68788F] space-y-0.5">
            {Object.entries(m.experimentsMeta.classification).map(([k, v]) => (
              <li key={k}>
                <strong>{k}:</strong> {v}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="glass-panel rounded-2xl p-6 space-y-3">
        <h2 className="font-display font-bold text-lg text-[#142B50]">NASA sources (checked {m.experimentsMeta?.sources_verified_on ?? ''})</h2>
        <ul className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
          {[...sources.values()].map((s) => (
            <li key={s.url}>
              <a href={s.url} target="_blank" rel="noopener noreferrer" className="flex items-center justify-between p-3 rounded-xl bg-[#FFFFFF] border border-[#E1E8F0] hover:border-[#0B5ED7] text-[#142B50] font-medium">
                <span>{s.label}</span>
                <ExternalLink className="w-3.5 h-3.5 text-[#0B5ED7] shrink-0" />
              </a>
            </li>
          ))}
        </ul>
      </section>

      <section className="rounded-2xl p-6 space-y-2 bg-[#FFF4E5] border border-[#A15C00]/30 text-[#6B3F00] text-xs leading-relaxed">
        <h2 className="font-display font-bold text-base">Known limitations (current state)</h2>
        <ul className="list-disc pl-5 space-y-1">
          <li>Terrain (D4) and rock (D5) have no data yet; MODIS/GPM-derived dimensions cover one year (2024), not a multi-year climatology.</li>
          <li>Moon and Mars reference-site rules are v0 team drafts, not yet grounded in LOLA, MOLA, Diviner or CRISM values.</li>
          <li>Validation uses only a handful of NASA-documented analog sites at 5° resolution; see the validation section above.</li>
          <li>The ice dimension, when present, is a temperature-based proxy, not a snow or ice measurement.</li>
          <li>Region place-names are approximate labels; the engine scores grid cells.</li>
          <li>Earth cannot reproduce lunar or Martian gravity, atmosphere, radiation or dust behaviour.</li>
        </ul>
      </section>
    </div>
  );
}
