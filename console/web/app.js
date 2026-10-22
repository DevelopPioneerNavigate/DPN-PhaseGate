"use strict";
/* Synthetic-only dashboard. No controls, device connections, or research writes. */
let running = true;
let lastTelemetry = null;
let lastOverview = null;
const el = id => document.getElementById(id);
const safeCount = v => Number.isInteger(v) && v >= 0 ? String(v) : "UNKNOWN";
const number = v => Number.isFinite(v) ? v.toFixed(3) : "--.---";

async function api(path) {
  const res = await fetch(path, {cache:"no-store"});
  if(!res.ok) throw new Error("Demo API " + res.status);
  return res.json();
}
function text(node, value) { if(node) node.textContent = String(value); }

function draw(data) {
  const canvas=el("chart"), ctx=canvas.getContext("2d");
  if(!ctx || !data || !Array.isArray(data.samples)) return;
  const w=canvas.width, h=canvas.height, left=54,right=28,top=26,bottom=31;
  ctx.clearRect(0,0,w,h);
  ctx.fillStyle="#0d172c";ctx.fillRect(0,0,w,h);
  ctx.strokeStyle="#2a3f61";ctx.lineWidth=1;
  for(let i=0;i<=4;i++){
    const y=top+i*(h-top-bottom)/4;
    ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w-right,y);ctx.stroke();
  }
  const xs=i=>left+i*(w-right-left)/Math.max(1,data.samples.length-1);
  const plot=(field,center,scale,color,offset)=>{
    ctx.strokeStyle=color;ctx.lineWidth=2.7;ctx.beginPath();
    data.samples.forEach((p,i)=>{
      const v=Number(p[field]);const y=top+(h-top-bottom)*(offset+(center-v)/scale);
      if(i===0)ctx.moveTo(xs(i),y);else ctx.lineTo(xs(i),y);
    });ctx.stroke();
  };
  // Different labeled axes, not a shared raw scale. Never interpret cross-trace crossings.
  plot("A",45.0,1.2,"#4bdcf2",0.27);
  plot("B",0.0,0.18,"#b58bff",0.73);
  ctx.fillStyle="#4bdcf2";ctx.font="12px Segoe UI, sans-serif";ctx.fillText("A • 45 g CENTER",left+5,top+11);
  ctx.fillStyle="#b58bff";ctx.fillText("B • 0 g CENTER",left+5,top+136);
  ctx.font="11px Segoe UI, sans-serif";ctx.fillStyle="#839cbb";
  ctx.fillText("60 s ago",left,h-9);ctx.fillText("Current synthetic frame",w-205,h-9);
}
function renderEvents(payload) {
  const list=el("event-list");list.replaceChildren();
  (payload.events || []).forEach(evt=>{
    const row=document.createElement("div");row.className="event";
    const id=document.createElement("b");id.textContent=evt.id;
    const label=document.createElement("span");label.textContent=evt.label;
    row.append(id,label);list.appendChild(row);
  });
}
async function refresh(){
  const stamp=new Date().toISOString().slice(11,19);
  text(el("clock"),stamp+" UTC");
  if(!running) return;
  try {
    const [overview,telemetry] = await Promise.all([api("/api/overview"),api("/api/telemetry")]);
    if(overview.mode!=="SYNTHETIC" || telemetry.mode!=="SYNTHETIC")
      throw new Error("Unexpected data mode");
    lastOverview=overview;lastTelemetry=telemetry;
    text(el("metric-sources"),safeCount(overview.sources));
    text(el("metric-hypotheses"),safeCount(overview.hypotheses));
    text(el("metric-runs"),safeCount(overview.experiment_records));
    text(el("mass-A"),number(telemetry.stations[0].mass_g));
    text(el("mass-B"),number(telemetry.stations[1].mass_g));
    draw(telemetry);
  } catch(err) {
    text(el("metric-sources"),"OFFLINE");
    text(el("metric-hypotheses"),"OFFLINE");
    text(el("metric-runs"),"OFFLINE");
    text(el("mass-A"),"--.---");text(el("mass-B"),"--.---");
    console.warn("Synthetic local API unavailable:",err.message);
  }
}
el("toggle-feed").addEventListener("click",()=>{
  running=!running;
  text(el("toggle-feed"),running?"Pause demo":"Resume demo");
  if(running)refresh();
});
el("export-snapshot").addEventListener("click",()=>{
  if(!lastTelemetry) return;
  const sample={mode:"SYNTHETIC", warning:"DEMO ONLY; NOT A PHYSICAL EXPERIMENT",
                overview:lastOverview,telemetry:lastTelemetry};
  const object=new Blob([JSON.stringify(sample,null,2)],{type:"application/json"});
  const u=URL.createObjectURL(object);const a=document.createElement("a");
  a.href=u;a.download="PHASEGATE_SYNTHETIC_DEMO.json";document.body.append(a);a.click();a.remove();
  setTimeout(()=>URL.revokeObjectURL(u),0);
});
api("/api/events").then(renderEvents).catch(()=>text(el("event-list"),"Local demo API unavailable."));
refresh();
setInterval(refresh,1500);
