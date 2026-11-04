/* GPU 3D procedural (Three.js r128): carcasa, 3 ventiladores, tira de color de la marca y bracket.
   Se dibuja una en cada mitad; setColors() cambia el acento cuando cambia la marca. */
(function () {
  if (!window.THREE) return;
  const reducir = matchMedia("(prefers-reduced-motion: reduce)").matches;

  function crearGPU() {
    const g = new THREE.Group(), fans = [];
    const mat = (c, m, r) => new THREE.MeshStandardMaterial({ color: c, metalness: m, roughness: r });
    const caja = (w, h, d, m, x, y, z) => { const o = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m); o.position.set(x, y, z); g.add(o); return o; };

    caja(3, 1.2, 0.4, mat(0x1b1d21, 0.5, 0.45), 0, 0, 0);                  // carcasa
    caja(3, 1.16, 0.05, mat(0x2b2f36, 0.8, 0.3), 0, 0, -0.23);             // backplate
    caja(0.06, 1.3, 0.7, mat(0xb9bec6, 0.9, 0.25), -1.53, 0, 0.05);        // bracket
    caja(1.7, 0.1, 0.06, mat(0xc9a43a, 1, 0.3), 0.3, -0.66, 0);            // conector dorado
    const acento = new THREE.MeshStandardMaterial({ color: 0x3f8a16, emissive: 0x3f8a16, emissiveIntensity: 0.9, metalness: 0.2, roughness: 0.3 });
    caja(3.02, 0.06, 0.42, acento, 0, 0.6, 0);                             // tira de marca
    caja(3.02, 0.03, 0.42, acento, 0, -0.52, 0);

    for (let i = -1; i <= 1; i++) {
      const f = new THREE.Group(); f.position.set(i * 0.98, 0, 0.21);
      const aro = new THREE.Mesh(new THREE.TorusGeometry(0.47, 0.035, 12, 48), mat(0x0c0d0f, 0.6, 0.4)); f.add(aro);
      const rot = new THREE.Group();
      const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.13, 0.06, 24), mat(0x2a2d33, 0.8, 0.3));
      hub.rotation.x = Math.PI / 2; rot.add(hub);
      for (let b = 0; b < 9; b++) {
        const aspa = new THREE.Mesh(new THREE.BoxGeometry(0.17, 0.33, 0.012), mat(0x3a3e46, 0.4, 0.55));
        const a = (b / 9) * Math.PI * 2;
        aspa.position.set(Math.cos(a) * 0.27, Math.sin(a) * 0.27, 0);
        aspa.rotation.z = a - Math.PI / 2; aspa.rotation.y = 0.45;       // inclinacion de la aspa
        rot.add(aspa);
      }
      f.add(rot); g.add(f); fans.push(rot);
    }
    return { g, fans, acento };
  }

  function montar(canvas, sentido) {
    let r;
    try { r = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true }); } catch { return null; }
    r.setPixelRatio(Math.min(devicePixelRatio, 2));
    const s = new THREE.Scene(), cam = new THREE.PerspectiveCamera(32, 1, 0.1, 50);
    cam.position.set(0, 0.2, 6.2);
    s.add(new THREE.AmbientLight(0xffffff, 0.55));
    const d = new THREE.DirectionalLight(0xffffff, 1.3); d.position.set(3, 4, 5); s.add(d);
    const luz = new THREE.PointLight(0x3f8a16, 1.4, 14); luz.position.set(-3, -1, 3); s.add(luz);
    const gpu = crearGPU(); s.add(gpu.g);
    function ajustar() {
      const w = canvas.clientWidth, h = canvas.clientHeight;
      r.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix();
    }
    addEventListener("resize", ajustar); ajustar();
    let t = sentido * 1.3;
    function frame() {
      t += 0.012;
      gpu.g.rotation.y = reducir ? sentido * 0.5 : Math.sin(t) * 0.55 + sentido * 0.25;
      gpu.g.rotation.x = -0.22; gpu.g.rotation.z = 0.04 * sentido;
      if (!reducir) gpu.fans.forEach(f => (f.rotation.z -= 0.09));
      r.render(s, cam); requestAnimationFrame(frame);
    }
    frame();
    return (hex) => { const c = new THREE.Color(hex); gpu.acento.color.copy(c); gpu.acento.emissive.copy(c); luz.color.copy(c); };
  }

  const a = montar(document.getElementById("c1"), 1), b = montar(document.getElementById("c2"), -1);
  window.GPU3D = { setColors(ca, cb) { a && a(ca); b && b(cb); } };
})();
