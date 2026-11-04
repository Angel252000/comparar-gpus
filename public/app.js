const $ = id => document.getElementById(id);
const mejor = {"FPS promedio": 1, "Rendimiento": 1, "VRAM": 1, "FPS/$100": 1, "TDP": -1, "Precio": -1};

async function consultar(url) {
  $("msg").textContent = ""; $("t").hidden = true; $("g").textContent = "";
  let r, d;
  try {
    r = await fetch(url);
    d = await r.json();
  } catch {
    $("msg").textContent = "No se pudo conectar con el servidor. Intenta de nuevo.";
    return;
  }
  if (!r.ok) {
    $("msg").textContent = d.error + (d.sugerencias?.length ? " Sugerencias: " + d.sugerencias.join(", ") : "") +
      (d.disponibles ? " Disponibles: " + d.disponibles.join(", ") : "");
    return;
  }
  $("h1").textContent = d.gpu_1; $("h2").textContent = d.gpu_2;
  $("t").querySelector("tbody").innerHTML = d.filas.map(f => {
    const s = (mejor[f.metrica] || 0) * Math.sign(f.v1 - f.v2);
    const c1 = s > 0 ? "win" : "", c2 = s < 0 ? "win" : "";
    return `<tr><td>${f.metrica}</td><td class="${c1}">${f.v1}${f.unidad}</td><td class="${c2}">${f.v2}${f.unidad}</td></tr>`;
  }).join("");
  $("t").hidden = false;
  const g = d.ganadores;
  $("g").textContent = `Mas rapida: ${g.mas_rapida} · Mejor valor: ${g.mejor_valor} · Mas eficiente: ${g.mas_eficiente}`;
}

$("f").addEventListener("submit", e => {
  e.preventDefault();
  consultar("/api/comparar?q=" + encodeURIComponent($("q").value));
});
$("bs").addEventListener("click", () =>
  consultar(`/api/comparar?gpu1=${encodeURIComponent($("s1").value)}&gpu2=${encodeURIComponent($("s2").value)}`));

fetch("/api/comparar?lista=1").then(r => r.json()).then(d => {
  const o = d.gpus.map(n => `<option>${n}</option>`).join("");
  $("s1").innerHTML = o; $("s2").innerHTML = o; $("s2").selectedIndex = 1;
});
