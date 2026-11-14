import { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";

const API = import.meta.env.VITE_API_URL ?? "/api";
type Target = { id: string; name: string; body: string; description: string };
type Cell = { cell_id: number; lat: number; lon: number; score: number; coverage: number };

// score 0-100 -> colour (red -> yellow -> green)
const color = (s: number) => `hsl(${Math.round((s / 100) * 120)}, 85%, 45%)`;

export default function App() {
  const [targets, setTargets] = useState<Target[]>([]);
  const [target, setTarget] = useState("");
  const [cells, setCells] = useState<Cell[]>([]);
  const [minScore, setMinScore] = useState(0);

  useEffect(() => {
    fetch(`${API}/targets`).then(r => r.json()).then((t: Target[]) => { setTargets(t); setTarget(t[0]?.id ?? ""); });
  }, []);
  useEffect(() => {
    if (!target) return;
    fetch(`${API}/score?target=${target}&min_score=${minScore}&limit=5000`).then(r => r.json()).then(setCells);
  }, [target, minScore]);

  const t = targets.find(x => x.id === target);
  return (
    <div style={{ display: "flex", height: "100vh", fontFamily: "system-ui" }}>
      <aside style={{ width: 300, padding: 16, overflow: "auto", borderRight: "1px solid #ddd" }}>
        <h2 style={{ margin: 0 }}>ASTRANOVUS</h2>
        <p style={{ color: "#666", marginTop: 4 }}>Where on Earth looks like the Moon or Mars?</p>
        <label>Target</label>
        <select value={target} onChange={e => setTarget(e.target.value)} style={{ width: "100%", padding: 6 }}>
          {targets.map(x => <option key={x.id} value={x.id}>{x.body.toUpperCase()} - {x.name}</option>)}
        </select>
        {t && <p style={{ fontSize: 13 }}>{t.description}</p>}
        <label>Min score: {minScore}</label>
        <input type="range" min={0} max={95} value={minScore} onChange={e => setMinScore(+e.target.value)} style={{ width: "100%" }} />
        <p style={{ fontSize: 12, color: "#888" }}>{cells.length} cells shown. TODO (Girl 1/2): site page, compare, weight sliders, methodology.</p>
      </aside>
      <MapContainer center={[20, 30]} zoom={2} style={{ flex: 1 }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap" />
        {cells.map(c => (
          <CircleMarker key={c.cell_id} center={[c.lat, c.lon]} radius={5}
            pathOptions={{ color: color(c.score), fillColor: color(c.score), fillOpacity: 0.7, weight: 0 }}>
            <Tooltip>{c.score.toFixed(1)} / 100 (coverage {(c.coverage * 100).toFixed(0)}%)</Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
