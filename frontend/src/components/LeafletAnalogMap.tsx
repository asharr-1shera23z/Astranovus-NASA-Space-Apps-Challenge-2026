import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Globe, Layers, Minus, Plus, RotateCcw } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import type { HeatmapPoint } from '../types/astranovus';
import {
  BASEMAP_CONFIGS,
  BASEMAP_OPTIONS,
  type BasemapStyleId,
  escapeHtml,
  formatCursorTelemetry,
  getMarkerStyle,
} from '../utils/leafletMapUtils';

export interface MapMarkerItem {
  id: string;
  name: string;
  country: string;
  lat: number;
  lon: number;
  score: number;
  coverage: number;
  role: string;
  published?: boolean;
}

interface LeafletAnalogMapProps {
  markers: MapMarkerItem[];
  selectedId: string | null;
  onSelectMarker: (id: string) => void;
  onOpenProfile?: (id: string) => void;
  heatmapPoints?: HeatmapPoint[];
  heatmapOpacity?: number;
  /** If set, the selected marker is drawn with its true grid-cell footprint (degrees) to show spatial uncertainty. */
  cellSizeDeg?: number;
  bodyTheme: 'Moon' | 'Mars';
  heightClass?: string;
}

export function LeafletAnalogMap({
  markers,
  selectedId,
  onSelectMarker,
  onOpenProfile,
  heatmapPoints = [],
  heatmapOpacity = 0.65,
  cellSizeDeg,
  bodyTheme,
  heightClass = 'h-[480px]',
}: LeafletAnalogMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<L.Map | null>(null);
  const basemapLayerRef = useRef<L.LayerGroup | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);
  const heatmapLayerRef = useRef<L.LayerGroup | null>(null);
  const solarZonesLayerRef = useRef<L.LayerGroup | null>(null);
  const footprintLayerRef = useRef<L.LayerGroup | null>(null);
  const prevSelectedRef = useRef<string | null>(null);

  const [cursorCoords, setCursorCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [showSolarZones, setShowSolarZones] = useState<boolean>(false);
  const [basemapStyle, setBasemapStyle] = useState<BasemapStyleId>('street');

  const onSelectRef = useRef(onSelectMarker);
  const onOpenProfileRef = useRef(onOpenProfile);
  onSelectRef.current = onSelectMarker;
  onOpenProfileRef.current = onOpenProfile;

  // Initialize real Leaflet tile map once
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = L.map(containerRef.current, {
      center: [16, 8],
      zoom: 2,
      minZoom: 2,
      maxZoom: 18,
      zoomControl: false,
      attributionControl: false,
      worldCopyJump: true,
    });

    L.control.attribution({ position: 'bottomright', prefix: false }).addTo(map);
    L.control.scale({ position: 'bottomright', imperial: false, maxWidth: 110 }).addTo(map);

    basemapLayerRef.current = L.layerGroup().addTo(map);
    solarZonesLayerRef.current = L.layerGroup().addTo(map);
    heatmapLayerRef.current = L.layerGroup().addTo(map);
    footprintLayerRef.current = L.layerGroup().addTo(map);
    markersLayerRef.current = L.layerGroup().addTo(map);
    mapRef.current = map;

    map.on('mousemove', (ev: L.LeafletMouseEvent) => {
      const wrapped = ev.latlng.wrap();
      setCursorCoords({
        lat: Number(wrapped.lat.toFixed(2)),
        lon: Number(wrapped.lng.toFixed(2)),
      });
    });

    map.on('mouseout', () => {
      setCursorCoords(null);
    });

    const rafId = requestAnimationFrame(() => {
      map.invalidateSize({ animate: false });
    });
    const resizeObserver = new ResizeObserver(() => {
      map.invalidateSize({ animate: false });
    });
    resizeObserver.observe(containerRef.current);

    return () => {
      cancelAnimationFrame(rafId);
      resizeObserver.disconnect();
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Swap real Leaflet tile layers when basemap style changes
  useEffect(() => {
    const basemapLayer = basemapLayerRef.current;
    if (!basemapLayer) return;
    basemapLayer.clearLayers();

    const cfg = BASEMAP_CONFIGS[basemapStyle];
    const tileOptions: L.TileLayerOptions = {
      maxZoom: cfg.maxZoom,
      attribution: cfg.attribution,
      detectRetina: false,
    };
    if (cfg.subdomains) {
      tileOptions.subdomains = cfg.subdomains;
    }

    L.tileLayer(cfg.tileUrl, tileOptions).addTo(basemapLayer);

    if (cfg.overlayUrl) {
      L.tileLayer(cfg.overlayUrl, {
        maxZoom: cfg.maxZoom,
        opacity: 0.9,
      }).addTo(basemapLayer);
    }
  }, [basemapStyle]);

  // Render optional Solar / Latitude Zone bands (Polar |lat| >= 66.5 and Mid-Latitude 30-60 ice zones)
  useEffect(() => {
    const zoneLayer = solarZonesLayerRef.current;
    if (!zoneLayer) return;
    zoneLayer.clearLayers();

    if (!showSolarZones) return;

    const bands: Array<{ bounds: L.LatLngBoundsExpression; color: string; label: string }> = [
      {
        bounds: [
          [66.5, -180],
          [85, 180],
        ],
        color: '#0EA5E9',
        label: 'Arctic Polar Illumination Zone (|lat| >= 66.5 deg)',
      },
      {
        bounds: [
          [-85, -180],
          [-66.5, 180],
        ],
        color: '#0EA5E9',
        label: 'Antarctic Polar Illumination Zone (|lat| >= 66.5 deg)',
      },
      {
        bounds: [
          [30, -180],
          [60, 180],
        ],
        color: '#F28B45',
        label: 'Northern Mid-Latitude Ice / Arid Belt (30-60 N)',
      },
      {
        bounds: [
          [-60, -180],
          [-30, 180],
        ],
        color: '#F28B45',
        label: 'Southern Mid-Latitude Ice / Arid Belt (30-60 S)',
      },
    ];

    for (const band of bands) {
      L.rectangle(band.bounds, {
        color: band.color,
        weight: 1.2,
        dashArray: '4 4',
        fillColor: band.color,
        fillOpacity: 0.14,
        interactive: false,
      }).addTo(zoneLayer);
    }
  }, [showSolarZones]);

  // Render heatmap intensity layer when points or opacity change
  useEffect(() => {
    const heatLayer = heatmapLayerRef.current;
    if (!heatLayer) return;
    heatLayer.clearLayers();

    if (heatmapPoints.length === 0) return;

    for (const pt of heatmapPoints) {
      const color =
        bodyTheme === 'Mars'
          ? pt.intensity > 0.72
            ? '#F28B45'
            : pt.intensity > 0.55
            ? '#0EA5E9'
            : '#0B5ED7'
          : pt.intensity > 0.72
          ? '#0B5ED7'
          : pt.intensity > 0.55
          ? '#0EA5E9'
          : '#60A5FA';

      L.circle([pt.lat, pt.lon], {
        radius: 260_000 * (0.65 + pt.intensity * 0.6),
        stroke: false,
        fillColor: color,
        fillOpacity: Math.max(0.08, Math.min(0.88, pt.intensity * heatmapOpacity * 0.62)),
        interactive: false,
      }).addTo(heatLayer);
    }
  }, [heatmapPoints, heatmapOpacity, bodyTheme]);

  // Render site markers & pan crisply (no flashy animation) when selection changes
  useEffect(() => {
    const layer = markersLayerRef.current;
    if (!layer) return;
    layer.clearLayers();

    for (const m of markers) {
      const isSelected = m.id === selectedId;
      const marker = L.circleMarker([m.lat, m.lon], getMarkerStyle(m.score, isSelected, bodyTheme));

      marker.bindTooltip(`${m.name} (${m.score.toFixed(1)}%)`, {
        direction: 'top',
        offset: [0, -8],
      });

      const popupEl = document.createElement('div');
      popupEl.className = 'p-3 min-w-[215px] font-sans';
      popupEl.innerHTML = `
        <div style="font-size:11px;color:#68788F;margin-bottom:2px;">${escapeHtml(m.country)} · ${escapeHtml(m.role.replace('_', ' '))}</div>
        <div style="font-family:Montserrat,sans-serif;font-weight:700;font-size:13px;color:#142B50;margin-bottom:6px;">${escapeHtml(m.name)}</div>
        <div style="display:flex;align-items:center;justify-content:space-between;font-size:12px;margin-bottom:8px;">
          <span style="color:#68788F;">Similarity:</span>
          <strong style="color:#0B5ED7;font-family:JetBrains Mono,monospace;">${m.score.toFixed(1)}%</strong>
        </div>
      `;

      if (m.published !== false && onOpenProfileRef.current) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.textContent = 'View Profile →';
        btn.style.cssText =
          'width:100%;padding:6px 10px;background:#0B5ED7;color:#FFFFFF;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;';
        btn.onclick = () => onOpenProfileRef.current?.(m.id);
        popupEl.appendChild(btn);
      }

      marker.bindPopup(popupEl);
      marker.on('click', () => {
        onSelectRef.current(m.id);
      });

      marker.addTo(layer);
    }

    if (
      selectedId &&
      prevSelectedRef.current !== null &&
      prevSelectedRef.current !== selectedId &&
      mapRef.current
    ) {
      const targetMarker = markers.find((m) => m.id === selectedId);
      if (targetMarker) {
        mapRef.current.panTo([targetMarker.lat, targetMarker.lon], { animate: false });
      }
    }
    prevSelectedRef.current = selectedId;
  }, [markers, selectedId, bodyTheme]);

  // Footprint of the selected grid cell: the marker is a cell centre, not a point-sized site.
  useEffect(() => {
    const layer = footprintLayerRef.current;
    if (!layer) return;
    layer.clearLayers();
    const sel = markers.find((m) => m.id === selectedId);
    if (!sel || !cellSizeDeg) return;
    const h = cellSizeDeg / 2;
    L.rectangle(
      [
        [Math.max(-90, sel.lat - h), sel.lon - h],
        [Math.min(90, sel.lat + h), sel.lon + h],
      ],
      { color: '#142B50', weight: 1.5, dashArray: '5 4', fillColor: '#0B5ED7', fillOpacity: 0.08, interactive: false }
    ).addTo(layer);
  }, [markers, selectedId, cellSizeDeg]);

  const activeBasemapBg = BASEMAP_CONFIGS[basemapStyle].backgroundColor;

  return (
    <div
      className={`relative w-full ${heightClass} rounded-xl overflow-hidden border border-[#E1E8F0]`}
      style={{ backgroundColor: activeBasemapBg }}
    >
      <div
        ref={containerRef}
        className="w-full h-full z-0"
        data-testid="analog-leaflet-map"
        data-basemap={basemapStyle}
        aria-label="Interactive global Earth analog Leaflet map"
      />

      {/* Top HUD Bar: Live Coordinates Telemetry + Basemap Layer Switcher + Solar Zones */}
      <div className="absolute top-3 left-3 right-3 z-[400] flex flex-wrap items-start justify-between gap-2 pointer-events-none">
        <div className="glass-dark-hud text-[#FFFFFF] rounded-lg px-3 py-1.5 font-mono text-[11px] tabular-nums">
          {formatCursorTelemetry(cursorCoords)}
        </div>

        <div className="flex flex-wrap items-center gap-1.5 pointer-events-auto">
          <div
            role="group"
            aria-label="Map layer style"
            className="inline-flex items-center glass-light-hud rounded-lg p-0.5"
          >
            <Layers className="w-3.5 h-3.5 text-[#68788F] ml-2 mr-1 hidden sm:block" />
            {BASEMAP_OPTIONS.map((opt) => {
              const active = basemapStyle === opt.id;
              return (
                <button
                  key={opt.id}
                  type="button"
                  onClick={() => setBasemapStyle(opt.id)}
                  aria-pressed={active}
                  className={`px-2.5 py-1 rounded-md text-xs font-semibold transition-all duration-150 ${
                    active
                      ? 'bg-[#0B5ED7] text-[#FFFFFF] shadow-xs'
                      : 'text-[#142B50] hover:bg-[#EDF3FA]/90 hover:text-[#0B5ED7]'
                  }`}
                >
                  {opt.label}
                </button>
              );
            })}
          </div>

          <button
            type="button"
            onClick={() => setShowSolarZones((v) => !v)}
            aria-pressed={showSolarZones}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold shadow-sm transition-all duration-150 hover:-translate-y-0.5 ${
              showSolarZones
                ? 'bg-[#0B5ED7]/95 backdrop-blur-md border-[#0B5ED7] text-[#FFFFFF]'
                : 'glass-light-hud border-transparent text-[#142B50] hover:text-[#0B5ED7]'
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Solar Zones</span>
          </button>
        </div>
      </div>

      {/* Zoom & Reset Controls positioned cleanly above bottom-right scale/attribution */}
      <div className="absolute bottom-14 right-3 z-[400] flex flex-col gap-1.5">
        <button
          type="button"
          onClick={() => mapRef.current?.zoomIn(1, { animate: false })}
          aria-label="Zoom in map"
          className="w-9 h-9 glass-light-hud rounded-lg flex items-center justify-center text-[#142B50] hover:text-[#0B5ED7] hover:scale-105 active:scale-95 transition-all duration-150"
        >
          <Plus className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => mapRef.current?.zoomOut(1, { animate: false })}
          aria-label="Zoom out map"
          className="w-9 h-9 glass-light-hud rounded-lg flex items-center justify-center text-[#142B50] hover:text-[#0B5ED7] hover:scale-105 active:scale-95 transition-all duration-150"
        >
          <Minus className="w-4 h-4" />
        </button>
        <button
          type="button"
          onClick={() => mapRef.current?.setView([16, 8], 2, { animate: false })}
          aria-label="Reset map view"
          className="w-9 h-9 glass-light-hud rounded-lg flex items-center justify-center text-[#142B50] hover:text-[#0B5ED7] hover:scale-105 active:scale-95 transition-all duration-150"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>

      {/* Clean Frosted Glass Map Score Legend Card */}
      <div className="absolute bottom-3 left-3 z-[400] glass-light-hud rounded-xl px-3.5 py-2.5 text-xs space-y-1.5">
        <div className="font-semibold text-[#142B50]">Map Legend</div>
        <div className="flex items-center gap-2 text-[#68788F]">
          <span className="w-3 h-3 rounded-full bg-[#0B5ED7] ring-2 ring-[#142B50]" />
          <span>Selected Location</span>
        </div>
        <div className="flex items-center gap-2 text-[#68788F]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#0EA5E9]" />
          <span>High Match (≥ 80%)</span>
        </div>
        <div className="flex items-center gap-2 text-[#68788F]">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              bodyTheme === 'Mars' ? 'bg-[#F28B45]' : 'bg-[#475569]'
            }`}
          />
          <span>Moderate Match (&lt; 80%)</span>
        </div>
        {showSolarZones && (
          <div className="pt-1 border-t border-[#E6ECF3] text-[10px] text-[#0B5ED7] font-medium">
            Cyan: Polar ≥66.5° · Amber: 30°–60° Belt
          </div>
        )}
      </div>
    </div>
  );
}
