import { ArrowRight, ArrowLeftRight, Database, FlaskConical, Layers } from 'lucide-react';
import type { MissionResult, Region } from '../types/astranovus';
import { BODY_ACCENT, bodyLabel, pct, rankScore, suitabilitySummary } from '../utils/mission';
import { DimensionTable } from './DimensionTable';
import { EarthLimitsNote } from './DataBanners';
import { ScoreDonut } from './ScoreDonut';
import { InfoNote } from './StatusViews';

interface Props {
  region: Region;
  result: MissionResult;
  inCompare: boolean;
  onToggleCompare: () => void;
  onOpenProfile: () => void;
}

export function RegionDetail({ region: r, result, inCompare, onToggleCompare, onOpenProfile }: Props) {
  const body = result.experiment.body;
  const accent = BODY_ACCENT[body];
  const supporting = r.dimensions.filter((d) => d.similarity !== null && d.similarity >= 0.7);
  const weak = r.dimensions.filter((d) => d.similarity !== null && d.similarity < 0.5);
  const missing = r.dimensions.filter((d) => d.similarity === null);
  const datasets = Array.from(new Set(r.dimensions.filter((d) => d.data_status !== 'missing').map((d) => d.source)));

  return (
    <section className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-2xl shadow-xs overflow-hidden" aria-label={`Details for region ${r.rank}`}>
      <div className="p-5 sm:p-6 grid grid-cols-1 md:grid-cols-12 gap-6 border-b border-[#E6ECF3]">
        <div className="md:col-span-8 space-y-2">
          <div className="text-xs font-semibold" style={{ color: accent }}>
            Rank #{r.rank} · {bodyLabel(body)} · {result.experiment.short_name} · reference site {result.target_info.name}
          </div>
          <h2 className="font-display font-bold text-xl text-[#142B50]">{r.location_label}</h2>
          <p className="text-[11px] text-[#68788F]">
            Location name is an approximate label ({r.label_basis}); the engine itself works on grid cells, not named places.
            The marker is this region's highest-scoring grid cell (2.5°); the region joins {r.n_cells} neighbouring top-scoring cell{r.n_cells === 1 ? '' : 's'}{r.n_cells > 10 ? ' and is a wide belt, so conditions vary across it' : ''}.
          </p>
          <p className="text-sm text-[#142B50] leading-relaxed">{suitabilitySummary(r)}</p>
          <div className="flex flex-wrap gap-2 pt-1">
            <button
              type="button"
              onClick={onOpenProfile}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-[#0B5ED7] hover:bg-[#094DB3] text-[#FFFFFF] text-xs font-semibold transition-colors"
            >
              <span>Open full profile</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
            <button
              type="button"
              onClick={onToggleCompare}
              aria-pressed={inCompare}
              className={`inline-flex items-center gap-2 px-4 py-2 rounded-lg border text-xs font-semibold transition-colors ${
                inCompare ? 'bg-[#EDF3FA] border-[#0B5ED7] text-[#0B5ED7]' : 'bg-[#FFFFFF] border-[#E1E8F0] text-[#142B50] hover:border-[#0B5ED7]'
              }`}
            >
              <ArrowLeftRight className="w-3.5 h-3.5" />
              <span>{inCompare ? 'In comparison' : 'Add to comparison'}</span>
            </button>
          </div>
        </div>
        <div className="md:col-span-4 flex flex-col items-center">
          <ScoreDonut score={rankScore(r)} accentColor={accent} label={`${r.confidence} confidence`} />
          <div className="text-[11px] text-[#68788F] text-center mt-1">
            Evidence-adjusted score (raw similarity {r.best_score.toFixed(1)}, data coverage {pct(r.coverage)})
          </div>
        </div>
      </div>

      <div className="p-5 sm:p-6 space-y-6">
        {result.provisional && (
          <InfoNote tone="danger">
            <strong>Provisional result.</strong> Required checks for this experiment could not be verified (see the data banner above). Treat this
            ranking as exploratory only.
          </InfoNote>
        )}
        {r.notes.length > 0 && (
          <InfoNote tone="warn">
            {r.notes.map((n) => (
              <div key={n}>{n}</div>
            ))}
          </InfoNote>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-2">
            <h3 className="font-display font-bold text-sm text-[#142B50]">Why this region matches</h3>
            {supporting.length === 0 ? (
              <p className="text-xs text-[#68788F]">No assessed dimension reaches a strong (70%+) match for this purpose.</p>
            ) : (
              <ul className="space-y-1.5 text-xs text-[#142B50]">
                {supporting.map((d) => (
                  <li key={d.dimension} className="flex justify-between gap-3 bg-[#F4F8FF] border border-[#E1E8F0] rounded-lg px-3 py-2">
                    <span className="font-semibold">{d.name}</span>
                    <span className="font-mono text-[#0B5ED7] tabular-nums">{pct(d.similarity)} match</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <div className="space-y-2">
            <h3 className="font-display font-bold text-sm text-[#142B50]">Weak or missing dimensions</h3>
            {weak.length + missing.length === 0 ? (
              <p className="text-xs text-[#68788F]">None: every assessed dimension is at least a moderate match.</p>
            ) : (
              <ul className="space-y-1.5 text-xs">
                {weak.map((d) => (
                  <li key={d.dimension} className="flex justify-between gap-3 bg-[#FFF4E5] border border-[#A15C00]/25 rounded-lg px-3 py-2 text-[#6B3F00]">
                    <span className="font-semibold">{d.name}</span>
                    <span className="font-mono tabular-nums">{pct(d.similarity)} (weak)</span>
                  </li>
                ))}
                {missing.map((d) => (
                  <li key={d.dimension} className="flex justify-between gap-3 bg-[#FDECEC] border border-[#B42318]/25 rounded-lg px-3 py-2 text-[#7A1A12]">
                    <span className="font-semibold">{d.name}</span>
                    <span>no data yet</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="space-y-2">
          <h3 className="font-display font-bold text-sm text-[#142B50] inline-flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-[#0B5ED7]" /> Every dimension used for this experiment
          </h3>
          <DimensionTable dims={r.dimensions} accent={accent} />
        </div>

        <div className="space-y-2">
          <h3 className="font-display font-bold text-sm text-[#142B50]">Surface and terrain context</h3>
          {r.surface ? (
            <div className="space-y-2">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                {[
                  ['Mean elevation (1 km data)', r.surface.elevation_mean_m === null ? 'n/a' : `${r.surface.elevation_mean_m} m`],
                  ['Relief in cell (P95-P5, 1 km)', r.surface.relief_1km_m === null ? 'n/a' : `${r.surface.relief_1km_m} m`],
                  ['Mean 1 km slope', r.surface.slope_1km_deg === null ? 'n/a' : `${r.surface.slope_1km_deg}°`],
                  ['Elevation source', r.surface.dem_source ?? 'n/a'],
                ].map(([k, v]) => (
                  <div key={String(k)} className="bg-[#F4F8FF] border border-[#E1E8F0] rounded-lg px-3 py-2">
                    <div className="text-[10px] text-[#68788F]">{k}</div>
                    <div className="font-mono font-semibold text-[#142B50]">{v}</div>
                  </div>
                ))}
              </div>
              <p className="text-[11px] text-[#68788F]">
                {r.surface.perennial_snow_ice ? (
                  <strong className="text-[#0B5ED7]">Perennial snow/ice cover (MODIS snow-cover flag; says nothing about glaciers or subsurface ice). </strong>
                ) : (
                  'No perennial snow/ice flag. '
                )}
                {r.surface.snow_mean_valid_pct !== null && <>Mean snow cover over observed months: {r.surface.snow_mean_valid_pct}%. </>}
                These are coarse values averaged over the whole grid cell; they are not site measurements.
              </p>
            </div>
          ) : (
            <p className="text-xs text-[#68788F]">No surface context available for this cell.</p>
          )}
          <h3 className="font-display font-bold text-sm text-[#142B50] pt-2">High-resolution terrain check (NASA SRTM 30 m, local 1° tile)</h3>
          {r.terrain.state === 'verified_local' ? (
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
              {[
                ['Class', r.terrain.terrain_class],
                ['Mean slope', `${r.terrain.slope_mean_deg}°`],
                ['95th pct slope', `${r.terrain.slope_p95_deg}°`],
                ['Relief (P95-P5)', `${r.terrain.relief_m} m`],
                ['Mean elevation', `${r.terrain.elevation_mean_m} m`],
              ].map(([k, v]) => (
                <div key={String(k)} className="bg-[#F4F8FF] border border-[#E1E8F0] rounded-lg px-3 py-2">
                  <div className="text-[10px] text-[#68788F]">{k}</div>
                  <div className="font-mono font-semibold text-[#142B50]">{v}</div>
                </div>
              ))}
            </div>
          ) : (
            <p className={`text-xs rounded-lg px-3 py-2 ${r.terrain.state === 'outside_coverage' ? 'bg-[#FDECEC] text-[#7A1A12]' : 'bg-[#F4F8FF] text-[#68788F]'}`}>{r.terrain.note}</p>
          )}
          <p className="text-[11px] text-[#68788F]">
            Finer 30 m check on the 1°×1° SRTM tile around the cell centre, not the whole cell. It is a verification aid and is not used in the score; the score's terrain dimension uses coarser 1 km relief for the whole cell.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-2">
            <h3 className="font-display font-bold text-sm text-[#142B50] inline-flex items-center gap-1.5">
              <Database className="w-4 h-4 text-[#0B5ED7]" /> Datasets behind the Earth values
            </h3>
            {datasets.length === 0 ? (
              <p className="text-xs text-[#68788F]">No dimension has data for this region.</p>
            ) : (
              <ul className="list-disc pl-5 text-xs text-[#142B50] space-y-1">
                {datasets.map((s) => (
                  <li key={s}>{s}</li>
                ))}
              </ul>
            )}
            <p className="text-[11px] text-[#68788F]">
              All Earth values are percentile ranks among the loaded land cells, not raw physical measurements.
            </p>
          </div>
          <div className="space-y-2">
            <h3 className="font-display font-bold text-sm text-[#142B50] inline-flex items-center gap-1.5">
              <FlaskConical className="w-4 h-4 text-[#0B5ED7]" /> Potential applications here
            </h3>
            <ul className="list-disc pl-5 text-xs text-[#142B50] space-y-1">
              {r.applications.map((a) => (
                <li key={a}>{a}</li>
              ))}
            </ul>
            <p className="text-[11px] text-[#68788F]">
              Applications are ASTRANOVUS suggestions for the selected scenario. Local access, permits, safety and logistics are not assessed.
            </p>
          </div>
        </div>

        <EarthLimitsNote limits={result.limits_on_earth} />
      </div>
    </section>
  );
}
