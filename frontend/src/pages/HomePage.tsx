import { ArrowRight, Compass, Globe2, Layers, ShieldCheck, Target } from 'lucide-react';
import { lazy, Suspense, useMemo } from 'react';
import { MEDIA } from '../assets/media';
import { SyntheticDataWarning } from '../components/DataBanners';
import type { PageId } from '../components/Navbar';
import { LoadingPanel, StatusChip } from '../components/StatusViews';
import { useMission } from '../state/MissionContext';
import type { Body } from '../types/astranovus';
import { bodyLabel, DOC_LEVEL_LABEL, DOC_LEVEL_STYLE, dimLabel, regionsToMapSites } from '../utils/mission';

const EarthAnalogGlobe = lazy(() => import('../components/EarthAnalogGlobe').then((m) => ({ default: m.EarthAnalogGlobe })));

export function HomePage({ onNavigate }: { onNavigate: (page: PageId) => void }) {
  const m = useMission();
  const body = m.body;

  const sites = useMemo(() => (m.result ? regionsToMapSites(m.result.regions) : []), [m.result]);
  const startBody = (b: Body) => {
    m.setBody(b);
    onNavigate('explore');
  };

  return (
    <div className="space-y-8 pb-12">
      <section className="relative overflow-hidden bg-[#FFFFFF] border-b border-[#E1E8F0] min-h-[540px] lg:min-h-[600px] flex items-center">
        <img
          src={MEDIA.heroAstronautEarth}
          alt="Astronaut standing on lunar terrain overlooking Earth"
          className="absolute inset-0 w-full h-full object-cover object-right select-none pointer-events-none"
        />
        <div
          className="absolute inset-0 bg-gradient-to-r from-[#FFFFFF]/96 via-[#FFFFFF]/92 to-[#FFFFFF]/75 lg:from-[#FFFFFF] lg:via-[#FFFFFF]/85 lg:via-38% lg:to-transparent pointer-events-none"
          aria-hidden="true"
        />
        <div className="max-w-[1440px] w-full mx-auto px-4 sm:px-8 py-12 lg:py-16 relative z-10">
          <div className="max-w-xl space-y-5">
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-[#EDF3FA] border border-[#0B5ED7]/15 text-xs font-semibold tracking-wide text-[#0B5ED7]">
              Team Astravant · NASA Space Apps Challenge 2026
            </div>
            <h1 className="font-display font-extrabold text-5xl sm:text-6xl leading-[1.03] tracking-tight">
              <span className="text-[#142B50]">ASTRA</span>
              <span className="text-[#0B5ED7]">NOVUS</span>
            </h1>
            <p className="font-display font-bold text-xl sm:text-2xl text-[#142B50]">Explore. Compare. Prepare.</p>
            <p className="text-sm sm:text-base text-[#142B50]/85 max-w-md leading-relaxed">
              Tell us what you want to test on the Moon or Mars. ASTRANOVUS recommends the Earth regions that best fit that specific mission
              objective, and shows exactly how much real data stands behind each answer.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-1">
              <button
                type="button"
                onClick={() => startBody('moon')}
                className="inline-flex items-center gap-3 pl-2 pr-6 py-2 rounded-full border bg-gradient-to-r from-[#0B5ED7] to-[#3A94F3] border-[#0B5ED7] text-[#FFFFFF] shadow-sm hover:brightness-105 transition"
              >
                <img src={MEDIA.moonSurface} alt="" className="w-8 h-8 rounded-full object-cover border border-[#FFFFFF]/60 shrink-0" />
                <span className="font-display font-bold text-sm">Moon missions</span>
              </button>
              <button
                type="button"
                onClick={() => startBody('mars')}
                className="inline-flex items-center gap-3 pl-2 pr-6 py-2 rounded-full border bg-gradient-to-r from-[#F28B45] to-[#E06D22] border-[#F28B45] text-[#FFFFFF] shadow-sm hover:brightness-105 transition"
              >
                <img src={MEDIA.marsSurface} alt="" className="w-8 h-8 rounded-full object-cover border border-[#FFFFFF]/60 shrink-0" />
                <span className="font-display font-bold text-sm">Mars missions</span>
              </button>
            </div>
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => onNavigate('explore')}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-[#0B5ED7] hover:bg-[#094DB3] text-[#FFFFFF] text-sm font-semibold transition-colors shadow-md"
              >
                <span>Start mission workflow</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => onNavigate('discover')}
                className="inline-flex items-center gap-2 px-5 py-3.5 rounded-full bg-[#FFFFFF] border border-[#0B5ED7] text-[#0B5ED7] hover:bg-[#EDF3FA] text-sm font-semibold transition-colors"
              >
                <span>Global Heatmap</span>
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="max-w-[1440px] mx-auto px-4 sm:px-8 space-y-4">
        <SyntheticDataWarning />
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {[
            {
              label: 'Mission experiments',
              value: `${m.experiments.length || '–'} scenarios`,
              text: 'Moon and Mars field-testing objectives, each linked to NASA sources',
              Icon: Compass,
            },
            {
              label: 'Reference sites',
              value: `${m.health?.targets ?? '–'} profiles`,
              text: 'Planetary environments the engine compares Earth against (draft rules)',
              Icon: Target,
            },
            {
              label: 'Dimensions with real data',
              value: m.dataStatus ? `${m.dataStatus.n_dimensions_with_data} of ${m.dataStatus.n_dimensions}` : '–',
              text: m.dataStatus ? `${m.dataStatus.grid.cells} Earth land cells loaded` : 'Waiting for the backend',
              Icon: Layers,
            },
            {
              label: 'Data transparency',
              value: 'Explicit gaps',
              text: 'Missing, proxy and derived data are always labelled, never silently zero',
              Icon: ShieldCheck,
            },
          ].map(({ label, value, text, Icon }) => (
            <div key={label} className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-xl p-5 shadow-xs">
              <div className="flex items-center justify-between text-[#68788F] text-xs font-medium mb-2">
                <span>{label}</span>
                <Icon className="w-4 h-4 text-[#0B5ED7]" />
              </div>
              <div className="font-display font-bold text-2xl text-[#142B50] tabular-nums">{value}</div>
              <p className="text-xs text-[#68788F] mt-1">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="max-w-[1440px] mx-auto px-4 sm:px-8">
        <h2 className="font-display font-bold text-2xl text-[#142B50] mb-4">How ASTRANOVUS works</h2>
        <ol className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            ['1', 'Pick the body', 'Moon or Mars.'],
            ['2', 'Pick the experiment', 'For example water-ice prospecting, rover mobility or astrobiology instrument testing.'],
            ['3', 'Pick the reference site', 'Only environments that fit that experiment are offered.'],
            ['4', 'Get Earth regions', 'Ranked, with reasons, datasets, weak points and missing data.'],
          ].map(([n, t, d]) => (
            <li key={n} className="glass-panel rounded-xl p-5 space-y-1.5">
              <span className="w-7 h-7 rounded-full bg-[#0B5ED7] text-[#FFFFFF] text-xs font-bold flex items-center justify-center">{n}</span>
              <div className="font-display font-bold text-sm text-[#142B50]">{t}</div>
              <p className="text-xs text-[#68788F]">{d}</p>
            </li>
          ))}
        </ol>
      </section>

      <section className="max-w-[1440px] mx-auto px-4 sm:px-8">
        <div className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-2xl p-5 sm:p-6 shadow-xs space-y-4">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#0B5ED7]">
                <Globe2 className="w-4 h-4" />
                <span>3D Earth</span>
              </div>
              <h2 className="font-display font-bold text-xl sm:text-2xl text-[#142B50] mt-1">
                {m.result && sites.length > 0 ? 'Your latest recommended regions' : 'Interactive Earth orbital explorer'}
              </h2>
              <p className="text-xs sm:text-sm text-[#68788F] mt-0.5">
                {m.result && sites.length > 0
                  ? `${m.experiment?.name ?? ''} · reference site ${m.result.target_info.name}. Drag to rotate.`
                  : 'Run a mission workflow and the recommended regions appear here as beacons.'}
              </p>
            </div>
            <button
              type="button"
              onClick={() => onNavigate('explore')}
              className="text-xs sm:text-sm font-semibold text-[#0B5ED7] hover:underline inline-flex items-center gap-1 whitespace-nowrap"
            >
              <span>{sites.length ? 'Open full results' : 'Start a mission'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
          <Suspense fallback={<LoadingPanel message="Loading 3D globe..." />}>
            <EarthAnalogGlobe
              sites={sites}
              selectedTarget={body ? { id: m.targetId ?? '', body: bodyLabel(body) } : undefined}
              selectedSiteId={m.selectedRegionId}
              onSelectSite={m.selectRegion}
              onOpenProfile={(id) => {
                m.selectRegion(id);
                onNavigate('profiles');
              }}
              heightClass="h-[420px] sm:h-[460px] lg:h-[500px]"
            />
          </Suspense>
        </div>
      </section>

      {m.experiments.length > 0 && (
        <section className="max-w-[1440px] mx-auto px-4 sm:px-8">
          <h2 className="font-display font-bold text-2xl text-[#142B50] mb-1">What you can test</h2>
          <p className="text-sm text-[#68788F] mb-4">
            Labels show whether NASA documents the activity itself or ASTRANOVUS is proposing the scenario.
          </p>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            {(['moon', 'mars'] as Body[]).map((b) => (
              <div key={b} className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-xl p-5 space-y-2">
                <h3 className="font-display font-bold text-base text-[#142B50]">{bodyLabel(b)}</h3>
                <ul className="divide-y divide-[#E6ECF3]">
                  {m.experiments
                    .filter((e) => e.body === b)
                    .map((e) => (
                      <li key={e.id}>
                        <button
                          type="button"
                          onClick={() => {
                            m.setExperiment(e.id);
                            onNavigate('explore');
                          }}
                          className="w-full text-left py-2.5 flex items-center justify-between gap-3 hover:bg-[#F4F8FF] rounded-md px-2"
                        >
                          <span className="text-sm font-semibold text-[#142B50]">{e.name}</span>
                          <span className={`px-2 py-0.5 rounded-full border text-[10px] font-semibold whitespace-nowrap ${DOC_LEVEL_STYLE[e.nasa_documented.level]}`}>
                            {DOC_LEVEL_LABEL[e.nasa_documented.level]}
                          </span>
                        </button>
                      </li>
                    ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}

      {m.dataStatus && (
        <section className="max-w-[1440px] mx-auto px-4 sm:px-8">
          <div className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-2xl p-5 sm:p-6 space-y-3">
            <h2 className="font-display font-bold text-xl text-[#142B50]">What the Earth data covers today</h2>
            <p className="text-xs text-[#68788F]">
              Honest status of the eight comparison dimensions in the loaded grid. Real NASA dataset integration for the missing ones is still in progress.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {m.dataStatus.dimensions.map((d) => (
                <div key={d.id} className="rounded-lg border border-[#E1E8F0] bg-[#F4F8FF] p-3 space-y-1.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs font-semibold text-[#142B50]">{dimLabel(d.id)}</span>
                    <StatusChip status={d.status} />
                  </div>
                  <div className="text-[11px] text-[#68788F]">{Math.round(d.cell_coverage * 100)}% of cells have a value</div>
                </div>
              ))}
            </div>
            <button type="button" onClick={() => onNavigate('methodology')} className="text-xs font-semibold text-[#0B5ED7] hover:underline">
              Read the methodology →
            </button>
          </div>
        </section>
      )}

      <section className="max-w-[1440px] mx-auto px-4 sm:px-8">
        <div className="bg-[#FFFFFF] border border-[#E1E8F0] rounded-2xl overflow-hidden shadow-xs grid grid-cols-1 lg:grid-cols-12 items-center">
          <div className="lg:col-span-5 h-56 lg:h-64">
            <img src={MEDIA.roverTesting} alt="Field engineering team testing a six-wheeled planetary rover in analog terrain" className="w-full h-full object-cover" />
          </div>
          <div className="lg:col-span-7 p-6 lg:p-8 space-y-4">
            <div className="text-xs font-semibold text-[#0B5ED7]">Field-campaign planning</div>
            <h2 className="font-display font-bold text-2xl text-[#142B50]">Compare recommended regions side by side</h2>
            <p className="text-sm text-[#68788F] leading-relaxed">
              After running an experiment, add regions to the comparison to see strengths, weaknesses and missing data next to each other.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => onNavigate('compare')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#0B5ED7] hover:bg-[#094DB3] text-[#FFFFFF] text-xs font-semibold transition-colors"
              >
                Open comparison
              </button>
              <button
                type="button"
                onClick={() => onNavigate('methodology')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-[#EDF3FA] hover:bg-[#E1E8F0] border border-[#E1E8F0] text-[#142B50] text-xs font-semibold transition-colors"
              >
                How scores are computed
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
