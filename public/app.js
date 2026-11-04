const $ = id => document.getElementById(id);
const COLOR = {NVIDIA: "#3F8A16", AMD: "#CD2C26", Intel: "#2462CF"};
// mas es mejor, salvo TDP y precio
const mejor = {"FPS promedio": 1, "Rendimiento": 1, "VRAM": 1, "FPS/$100": 1, "TDP": -1, "Precio": -1};

async function consultar(url) {
  $("msg").textContent = "";
  let r, d;
  try {
    r = await fetch(url);
    d = await r.json();
  } catch {
    $("msg").textContent = "No se pudo conectar con el servidor. Intenta de nuevo.";
    return;
  }
  if (!r.ok) {
    $("msg").textContent = d.error + (d.sugerencias?.length ? " Sugerencias: " + d.sugerencias.join(", ") : "");
    return;
  }
  // colores y nombres de cada mitad
  document.documentElement.style.setProperty("--ca", COLOR[d.marca_1]);
  document.documentElement.style.setProperty("--cb", COLOR[d.marca_2]);
  window.GPU3D?.setColors(COLOR[d.marca_1], COLOR[d.marca_2]);
  $("ga").textContent = d.gpu_1; $("gb").textContent = d.gpu_2;
  $("h1").textContent = d.gpu_1; $("h2").textContent = d.gpu_2;
  if ($("s1").value !== d.gpu_1) $("s1").value = d.gpu_1;
  if ($("s2").value !== d.gpu_2) $("s2").value = d.gpu_2;
  $("t").querySelector("tbody").innerHTML = d.filas.map(f => {
    const s = (mejor[f.metrica] || 0) * Math.sign(f.v1 - f.v2);
    return `<tr><td>${f.metrica}</td><td class="${s > 0 ? "win l" : ""}">${f.v1}${f.unidad}</td><td class="${s < 0 ? "win r" : ""}">${f.v2}${f.unidad}</td></tr>`;
  }).join("");
  const g = d.ganadores;
  $("g").innerHTML = `Mas rapida: <b>${g.mas_rapida}</b> · Mejor valor: <b>${g.mejor_valor}</b> · Mas eficiente: <b>${g.mas_eficiente}</b>`;
}

const porSelector = () => consultar(`/api/comparar?gpu1=${encodeURIComponent($("s1").value)}&gpu2=${encodeURIComponent($("s2").value)}`);
$("s1").addEventListener("change", porSelector);
$("s2").addEventListener("change", porSelector);
$("f").addEventListener("submit", e => {
  e.preventDefault();
  consultar("/api/comparar?q=" + encodeURIComponent($("q").value));
});

// al abrir: llena los selectores y compara un par por defecto
fetch("/api/comparar?lista=1").then(r => r.json()).then(d => {
  const o = d.gpus.map(n => `<option>${n}</option>`).join("");
  $("s1").innerHTML = o; $("s2").innerHTML = o;
  $("s1").value = "RTX 5070"; $("s2").value = "RX 9070 XT";
  porSelector();
}).catch(() => { $("msg").textContent = "No se pudo cargar la lista de GPUs."; });
