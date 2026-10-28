import json
from typing import Dict, Any

def generate_digital_twin_html(fleet_data: Dict[str, Any], selected_machine_id: str = "M-01") -> str:
    """
    Generates a high-performance, self-contained Three.js 3D WebGL industrial factory floor
    with permanently visible overhead DOM labels for all 6 machines, distinct geometric machinery,
    moving conveyor parts, rotating motors, oscillating hydraulic press, swiveling robotic arm,
    autonomous patrol inspection AGV, dynamic status stack beacons, interactive selection,
    and a reliable Canvas 2D isometric fallback if WebGL/CDN is unavailable.
    """
    fleet_json = json.dumps(fleet_data)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>EdgeGuard AI 3D Digital Twin</title>
<style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
        background: #0b0e14;
        overflow: hidden;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "JetBrains Mono", sans-serif;
        user-select: none;
        width: 100vw;
        height: 100vh;
    }}
    #scene-wrapper {{
        position: relative;
        width: 100vw;
        height: 100vh;
        overflow: hidden;
    }}
    #webgl-canvas {{
        width: 100%;
        height: 100%;
        display: block;
    }}
    #fallback-canvas {{
        display: none;
        width: 100%;
        height: 100%;
        background: #0b0e14;
    }}

    /* Top HUD status overlay */
    #top-hud {{
        position: absolute;
        top: 10px;
        left: 12px;
        pointer-events: none;
        z-index: 20;
        display: flex;
        gap: 8px;
        align-items: center;
    }}
    .hud-pill {{
        background: rgba(15, 23, 42, 0.88);
        border: 1px solid rgba(56, 189, 248, 0.35);
        backdrop-filter: blur(8px);
        padding: 5px 11px;
        border-radius: 6px;
        color: #e2e8f0;
        font-size: 11px;
        display: inline-flex;
        align-items: center;
        gap: 7px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
    }}
    .hud-title {{
        color: #38bdf8;
        font-weight: 700;
        letter-spacing: 0.5px;
    }}
    .badge-live {{
        display: inline-block;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 9.5px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }}
    .badge-normal {{ background: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid #10b981; }}
    .badge-warning {{ background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }}
    .badge-critical {{ background: rgba(239, 68, 68, 0.25); color: #ef4444; border: 1px solid #ef4444; animation: blink 1.2s infinite; }}

    @keyframes blink {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

    /* Quick Inspector HUD (Corner card) */
    #inspector-hud {{
        position: absolute;
        top: 10px;
        right: 12px;
        background: rgba(15, 23, 42, 0.92);
        border: 1px solid rgba(56, 189, 248, 0.4);
        backdrop-filter: blur(8px);
        border-radius: 6px;
        padding: 8px 12px;
        color: #e2e8f0;
        font-size: 11px;
        z-index: 20;
        min-width: 190px;
        box-shadow: 0 4px 18px rgba(0,0,0,0.6);
        pointer-events: none;
    }}
    .insp-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 4px;
        margin-bottom: 5px;
    }}
    .insp-id {{
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        color: #38bdf8;
    }}
    .insp-row {{
        display: flex;
        justify-content: space-between;
        font-size: 10px;
        color: #94a3b8;
        margin-top: 2px;
    }}
    .insp-val {{
        color: #ffffff;
        font-weight: 600;
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Controls bar at bottom */
    #bottom-controls {{
        position: absolute;
        bottom: 10px;
        left: 12px;
        right: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        pointer-events: none;
        z-index: 20;
    }}
    .ctrl-hint {{
        background: rgba(15, 23, 42, 0.82);
        border: 1px solid rgba(255,255,255,0.1);
        color: #94a3b8;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 10px;
    }}
    #reset-cam-btn {{
        pointer-events: auto;
        background: #1e293b;
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 10.5px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
    }}
    #reset-cam-btn:hover {{
        background: #38bdf8;
        color: #0b0e14;
    }}

    /* Permanent Overhead Machine Labels */
    #labels-container {{
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 15;
    }}
    .machine-label {{
        position: absolute;
        pointer-events: auto;
        cursor: pointer;
        background: rgba(11, 17, 29, 0.90);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 6px;
        padding: 4px 9px;
        color: #ffffff;
        font-size: 11px;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.7);
        backdrop-filter: blur(6px);
        transform: translate(-50%, -100%);
        transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
    }}
    .machine-label:hover {{
        border-color: #00d2ff;
        background: rgba(15, 23, 42, 0.98);
        box-shadow: 0 0 14px rgba(0, 210, 255, 0.7);
    }}
    .machine-label.selected {{
        border: 1.5px solid #00f0ff;
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.85), inset 0 0 8px rgba(0, 240, 255, 0.25);
        background: rgba(14, 30, 52, 0.98);
    }}
    .status-dot {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        flex-shrink: 0;
    }}
    .dot-normal {{ background: #10b981; box-shadow: 0 0 7px #10b981; }}
    .dot-warning {{ background: #f59e0b; box-shadow: 0 0 7px #f59e0b; }}
    .dot-critical {{ background: #ef4444; box-shadow: 0 0 9px #ef4444; animation: blink 1.1s infinite; }}
    .m-id {{
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }}
    .m-div {{ color: #475569; }}
    .m-name {{ color: #f1f5f9; font-weight: 500; }}

    /* Hover Tooltip */
    #tooltip {{
        position: absolute;
        display: none;
        background: rgba(15, 23, 42, 0.96);
        border: 1px solid #38bdf8;
        padding: 6px 10px;
        border-radius: 4px;
        color: #fff;
        font-size: 11px;
        pointer-events: none;
        z-index: 30;
        box-shadow: 0 4px 12px rgba(0,0,0,0.7);
    }}
</style>
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
<div id="scene-wrapper">
    <!-- Top HUD Bar -->
    <div id="top-hud">
        <div class="hud-pill">
            <span class="hud-title">🏭 FACTORY DIGITAL TWIN</span>
            <span>|</span>
            <span>FLEET: <b>6/6 ONLINE</b></span>
            <span>|</span>
            <span>AGV PATROL: <span class="badge-live badge-normal">ACTIVE</span></span>
        </div>
    </div>

    <!-- Live Quick Inspector HUD for Selected Machine -->
    <div id="inspector-hud">
        <div class="insp-header">
            <span class="insp-id" id="insp-title">M-01 CNC Machine</span>
            <span id="insp-badge" class="badge-live badge-normal">NORMAL</span>
        </div>
        <div class="insp-row"><span>Process Temp:</span><span class="insp-val" id="insp-temp">40.2 °C</span></div>
        <div class="insp-row"><span>Vibration:</span><span class="insp-val" id="insp-vib">2.1 mm/s</span></div>
        <div class="insp-row"><span>Rotational Speed:</span><span class="insp-val" id="insp-rpm">1640 RPM</span></div>
        <div class="insp-row"><span>Torque:</span><span class="insp-val" id="insp-torq">47.5 Nm</span></div>
        <div class="insp-row"><span>ML Risk Score:</span><span class="insp-val" id="insp-risk">1.2%</span></div>
    </div>

    <!-- Bottom Controls & Hints -->
    <div id="bottom-controls">
        <button id="reset-cam-btn">↺ Reset Camera View</button>
        <div class="ctrl-hint">🖱️ Left Drag: Orbit | Right Drag: Pan | Scroll: Zoom | Click Machine to Select</div>
    </div>

    <!-- Persistent Overhead Labels Container -->
    <div id="labels-container">
        <!-- 6 Machine Labels will be bound here -->
    </div>

    <div id="tooltip"></div>
    <canvas id="fallback-canvas"></canvas>
    <div id="webgl-container" style="width:100%; height:100%;"></div>
</div>

<script>
    // -------------------------------------------------------------
    // Global Data & Configuration
    // -------------------------------------------------------------
    const fleetData = {fleet_json};
    let currentSelectedId = "{selected_machine_id}" || "M-01";

    const MACHINE_SPECS = [
        {{ id: "M-01", name: "CNC Machine", type: "cnc", x: -16, z: -8, labelY: 6.8 }},
        {{ id: "M-02", name: "Industrial Motor", type: "motor", x: 0, z: -8, labelY: 6.5 }},
        {{ id: "M-03", name: "Hydraulic Press", type: "press", x: 16, z: -8, labelY: 7.4 }},
        {{ id: "M-04", name: "Conveyor System", type: "conveyor", x: -16, z: 8, labelY: 5.6 }},
        {{ id: "M-05", name: "Cooling Unit", type: "cooling", x: 0, z: 8, labelY: 6.6 }},
        {{ id: "M-06", name: "Assembly Station", type: "robot", x: 16, z: 8, labelY: 7.0 }}
    ];

    // Helper: Determine status level and color
    function getStatusInfo(mData) {{
        if (!mData) return {{ state: "Normal", color: "#10b981", badgeClass: "badge-normal", dotClass: "dot-normal" }};
        const state = mData.health_state || (mData.prediction === 1 ? "Critical" : (mData.risk_score_pct >= 32 ? "Warning" : "Normal"));
        if (state === "Critical") return {{ state: "Critical", color: "#ef4444", badgeClass: "badge-critical", dotClass: "dot-critical" }};
        if (state === "Warning") return {{ state: "Warning", color: "#f59e0b", badgeClass: "badge-warning", dotClass: "dot-warning" }};
        return {{ state: "Normal", color: "#10b981", badgeClass: "badge-normal", dotClass: "dot-normal" }};
    }}

    // Update Quick Inspector HUD
    function updateInspectorHUD(mId) {{
        const spec = MACHINE_SPECS.find(s => s.id === mId) || MACHINE_SPECS[0];
        const mData = fleetData[mId] || {{}};
        const sInfo = getStatusInfo(mData);

        const titleEl = document.getElementById('insp-title');
        const badgeEl = document.getElementById('insp-badge');
        const tempEl = document.getElementById('insp-temp');
        const vibEl = document.getElementById('insp-vib');
        const rpmEl = document.getElementById('insp-rpm');
        const torqEl = document.getElementById('insp-torq');
        const riskEl = document.getElementById('insp-risk');

        if (titleEl) titleEl.innerText = `${{spec.id}} ${{spec.name}}`;
        if (badgeEl) {{
            badgeEl.innerText = sInfo.state.toUpperCase();
            badgeEl.className = `badge-live ${{sInfo.badgeClass}}`;
        }}

        const r = mData.reading || {{}};
        if (tempEl) tempEl.innerText = `${{r.process_temperature ?? '--'}} °C`;
        if (vibEl) vibEl.innerText = `${{mData.vibration ?? '--'}} mm/s`;
        if (rpmEl) rpmEl.innerText = `${{r.rotational_speed ?? '--'}} RPM`;
        if (torqEl) torqEl.innerText = `${{r.torque ?? '--'}} Nm`;
        if (riskEl) riskEl.innerText = `${{mData.risk_score_pct ?? '0.0'}}%`;
    }}

    // -------------------------------------------------------------
    // Machine Selection Handler
    // -------------------------------------------------------------
    let selectionHalo = null;
    let selectionBeam = null;

    function selectMachine(machineId) {{
        currentSelectedId = machineId;
        updateInspectorHUD(machineId);

        // Update DOM labels selection styling
        MACHINE_SPECS.forEach(s => {{
            const lbl = document.getElementById('label-' + s.id);
            if (lbl) {{
                if (s.id === machineId) {{
                    lbl.classList.add('selected');
                }} else {{
                    lbl.classList.remove('selected');
                }}
            }}
        }});

        // Move 3D Hologram selection ring & beam
        const targetSpec = MACHINE_SPECS.find(s => s.id === machineId);
        if (targetSpec && selectionHalo && selectionBeam) {{
            selectionHalo.position.set(targetSpec.x, 0.45, targetSpec.z);
            selectionBeam.position.set(targetSpec.x, 3.4, targetSpec.z);
            selectionHalo.visible = true;
            selectionBeam.visible = true;
        }}

        // Attempt communication with parent Streamlit application
        try {{
            window.parent.postMessage({{
                type: 'streamlit:setComponentValue',
                value: machineId
            }}, '*');
        }} catch(e) {{}}

        try {{
            const p = window.parent;
            if (p && p.location) {{
                const url = new URL(p.location.href);
                if (url.searchParams.get('selected_machine') !== machineId) {{
                    url.searchParams.set('selected_machine', machineId);
                    p.history.replaceState(null, '', url);
                }}
            }}
        }} catch(e) {{}}
    }}

    // Build the 6 permanent labels in DOM
    const labelsContainer = document.getElementById('labels-container');
    MACHINE_SPECS.forEach(s => {{
        const mData = fleetData[s.id] || {{}};
        const sInfo = getStatusInfo(mData);

        const lbl = document.createElement('div');
        lbl.id = 'label-' + s.id;
        lbl.className = 'machine-label' + (s.id === currentSelectedId ? ' selected' : '');
        lbl.innerHTML = `
            <span class="status-dot ${{sInfo.dotClass}}" id="dot-${{s.id}}"></span>
            <span class="m-id">${{s.id}}</span>
            <span class="m-div">|</span>
            <span class="m-name">${{s.name}}</span>
        `;
        lbl.addEventListener('click', (e) => {{
            e.stopPropagation();
            selectMachine(s.id);
        }});
        labelsContainer.appendChild(lbl);
    }});

    // Initialize inspector with current selected machine
    updateInspectorHUD(currentSelectedId);

    // -------------------------------------------------------------
    // THREE.JS 3D SCENE SETUP & FALLBACK CHECK
    // -------------------------------------------------------------
    if (typeof THREE === 'undefined') {{
        // Three.js failed to load from CDN -> Run Canvas Fallback
        initCanvasFallback();
    }} else {{
        try {{
            initThreeScene();
        }} catch(err) {{
            console.error("Three.js initialization error, falling back to 2D Canvas:", err);
            initCanvasFallback();
        }}
    }}

    function initThreeScene() {{
        const container = document.getElementById('webgl-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0d14);
        scene.fog = new THREE.FogExp2(0x0a0d14, 0.014);

        const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(28, 24, 32);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: false, powerPreference: "high-performance" }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.maxPolarAngle = Math.PI / 2.05;
        controls.minDistance = 10;
        controls.maxDistance = 80;
        controls.target.set(0, 0, 0);

        document.getElementById('reset-cam-btn').addEventListener('click', () => {{
            camera.position.set(28, 24, 32);
            controls.target.set(0, 0, 0);
        }});

        // Lighting
        const ambientLight = new THREE.AmbientLight(0x1e293b, 1.9);
        scene.add(ambientLight);

        const hemiLight = new THREE.HemisphereLight(0x38bdf8, 0x0f172a, 0.95);
        hemiLight.position.set(0, 50, 0);
        scene.add(hemiLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 1.25);
        dirLight.position.set(24, 38, 22);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        dirLight.shadow.camera.near = 0.5;
        dirLight.shadow.camera.far = 110;
        const d = 32;
        dirLight.shadow.camera.left = -d;
        dirLight.shadow.camera.right = d;
        dirLight.shadow.camera.top = d;
        dirLight.shadow.camera.bottom = -d;
        scene.add(dirLight);

        // Ambient Point Lights (Cyan Highlights)
        const pLight1 = new THREE.PointLight(0x00d2ff, 1.6, 32);
        pLight1.position.set(-16, 9, 0);
        scene.add(pLight1);

        const pLight2 = new THREE.PointLight(0x38bdf8, 1.6, 32);
        pLight2.position.set(16, 9, 0);
        scene.add(pLight2);

        // Factory Floor & Grid
        const floorGeo = new THREE.PlaneGeometry(68, 52);
        const floorMat = new THREE.MeshStandardMaterial({{
            color: 0x0f141e,
            roughness: 0.82,
            metalness: 0.25
        }});
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        const grid = new THREE.GridHelper(68, 34, 0x00d2ff, 0x1e293b);
        grid.position.y = 0.02;
        scene.add(grid);

        // Safety Perimeter Borders
        const borderGeo = new THREE.BoxGeometry(68, 0.15, 0.3);
        const borderMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
        const bTop = new THREE.Mesh(borderGeo, borderMat);
        bTop.position.set(0, 0.08, -25);
        scene.add(bTop);
        const bBot = new THREE.Mesh(borderGeo, borderMat);
        bBot.position.set(0, 0.08, 25);
        scene.add(bBot);

        // Central Aisle Guide Strip for AGV
        const aisleGeo = new THREE.PlaneGeometry(60, 0.15);
        const aisleMat = new THREE.MeshBasicMaterial({{ color: 0x0284c7, transparent: true, opacity: 0.4 }});
        const aisle1 = new THREE.Mesh(aisleGeo, aisleMat);
        aisle1.rotation.x = -Math.PI / 2;
        aisle1.position.set(0, 0.03, -2);
        scene.add(aisle1);
        const aisle2 = new THREE.Mesh(aisleGeo, aisleMat);
        aisle2.rotation.x = -Math.PI / 2;
        aisle2.position.set(0, 0.03, 2);
        scene.add(aisle2);

        // Animated components collection
        const animatedParts = [];
        const interactiveMeshes = [];
        const machineGroupsMap = {{}};

        // Material Presets
        const bodyMat = new THREE.MeshStandardMaterial({{ color: 0x243044, metalness: 0.65, roughness: 0.35 }});
        const darkMetalMat = new THREE.MeshStandardMaterial({{ color: 0x111827, metalness: 0.82, roughness: 0.25 }});
        const chromeMat = new THREE.MeshStandardMaterial({{ color: 0xd1d5db, metalness: 0.9, roughness: 0.15 }});
        const cyanAccentMat = new THREE.MeshStandardMaterial({{ color: 0x00d2ff, metalness: 0.5, roughness: 0.3 }});

        // ---------------------------------------------------------
        // BUILD INDIVIDUAL MACHINE GEOMETRIES
        // ---------------------------------------------------------
        MACHINE_SPECS.forEach(cfg => {{
            const mData = fleetData[cfg.id] || {{}};
            const sInfo = getStatusInfo(mData);
            const group = new THREE.Group();
            group.position.set(cfg.x, 0, cfg.z);
            group.userData = {{ id: cfg.id, name: cfg.name, spec: cfg }};

            // Foundation Plinth
            const plinthGeo = new THREE.BoxGeometry(6.6, 0.4, 5.4);
            const plinthMat = new THREE.MeshStandardMaterial({{ color: 0x161e2e, roughness: 0.9, metalness: 0.1 }});
            const plinth = new THREE.Mesh(plinthGeo, plinthMat);
            plinth.position.set(0, 0.2, 0);
            plinth.receiveShadow = true;
            plinth.castShadow = true;
            group.add(plinth);

            // Machine Specific Geometry
            if (cfg.type === "cnc") {{
                // 1. M-01: CNC Machine
                // Main Enclosure Cabinet
                const cabGeo = new THREE.BoxGeometry(4.4, 4.4, 4.0);
                const cab = new THREE.Mesh(cabGeo, bodyMat);
                cab.position.set(0, 2.5, 0);
                cab.castShadow = true;
                group.add(cab);

                // Tinted Acrylic Safety Window
                const winGeo = new THREE.BoxGeometry(2.6, 2.5, 0.2);
                const winMat = new THREE.MeshPhysicalMaterial({{
                    color: 0x38bdf8,
                    transparent: true,
                    opacity: 0.45,
                    roughness: 0.1,
                    transmission: 0.65
                }});
                const win = new THREE.Mesh(winGeo, winMat);
                win.position.set(0, 2.7, 2.05);
                group.add(win);

                // High-Speed Vertical Spindle Inside
                const spindleGeo = new THREE.CylinderGeometry(0.24, 0.1, 1.4, 16);
                const spindle = new THREE.Mesh(spindleGeo, chromeMat);
                spindle.position.set(0, 2.7, 0.5);
                group.add(spindle);
                animatedParts.push({{ mesh: spindle, type: "rotateY", speed: sInfo.state === "Critical" ? 0.45 : 0.22 }});

                // CNC Touchscreen Control Pendant
                const armGeo = new THREE.BoxGeometry(0.15, 0.15, 1.2);
                const arm = new THREE.Mesh(armGeo, darkMetalMat);
                arm.position.set(2.4, 3.2, 1.4);
                group.add(arm);

                const screenGeo = new THREE.BoxGeometry(0.8, 0.6, 0.1);
                const screenMat = new THREE.MeshBasicMaterial({{ color: 0x00d2ff }});
                const screen = new THREE.Mesh(screenGeo, screenMat);
                screen.position.set(2.4, 3.2, 2.0);
                group.add(screen);

            }} else if (cfg.type === "motor") {{
                // 2. M-02: Industrial Motor
                // Stator Cylindrical Housing with Cooling Fins
                const statorGeo = new THREE.CylinderGeometry(1.4, 1.4, 3.8, 24);
                statorGeo.rotateZ(Math.PI / 2);
                const stator = new THREE.Mesh(statorGeo, bodyMat);
                stator.position.set(0, 1.8, 0);
                stator.castShadow = true;
                group.add(stator);

                // Longitudinal Cooling Ribs
                for (let a = 0; a < Math.PI * 2; a += Math.PI / 4) {{
                    const ribGeo = new THREE.BoxGeometry(3.6, 0.12, 0.35);
                    const rib = new THREE.Mesh(ribGeo, darkMetalMat);
                    rib.position.set(0, 1.8 + Math.cos(a) * 1.4, Math.sin(a) * 1.4);
                    group.add(rib);
                }}

                // Output Drive Shaft & Heavy Coupling
                const shaftGeo = new THREE.CylinderGeometry(0.38, 0.38, 1.4, 16);
                shaftGeo.rotateZ(Math.PI / 2);
                const shaft = new THREE.Mesh(shaftGeo, chromeMat);
                shaft.position.set(2.4, 1.8, 0);
                group.add(shaft);

                // Coupling Flange
                const flangeGeo = new THREE.CylinderGeometry(0.7, 0.7, 0.35, 16);
                flangeGeo.rotateZ(Math.PI / 2);
                const flange = new THREE.Mesh(flangeGeo, darkMetalMat);
                flange.position.set(2.3, 1.8, 0);
                group.add(flange);

                // Rear Fan Shroud
                const shroudGeo = new THREE.CylinderGeometry(1.2, 1.2, 0.8, 20);
                shroudGeo.rotateZ(Math.PI / 2);
                const shroud = new THREE.Mesh(shroudGeo, darkMetalMat);
                shroud.position.set(-2.2, 1.8, 0);
                group.add(shroud);

                // Top Electrical Junction Box
                const jboxGeo = new THREE.BoxGeometry(1.2, 0.8, 1.0);
                const jbox = new THREE.Mesh(jboxGeo, darkMetalMat);
                jbox.position.set(0, 3.4, 0);
                group.add(jbox);

                animatedParts.push({{ mesh: shaft, type: "rotateX", speed: sInfo.state === "Critical" ? 0.5 : 0.25 }});
                animatedParts.push({{ mesh: flange, type: "rotateX", speed: sInfo.state === "Critical" ? 0.5 : 0.25 }});

            }} else if (cfg.type === "press") {{
                // 3. M-03: Hydraulic Press
                // 4 Heavy Steel Tie-Rod Columns
                const colGeo = new THREE.CylinderGeometry(0.32, 0.32, 5.6, 16);
                const c1 = new THREE.Mesh(colGeo, darkMetalMat); c1.position.set(-1.8, 3.0, -1.2);
                const c2 = new THREE.Mesh(colGeo, darkMetalMat); c2.position.set(1.8, 3.0, -1.2);
                const c3 = new THREE.Mesh(colGeo, darkMetalMat); c3.position.set(-1.8, 3.0, 1.2);
                const c4 = new THREE.Mesh(colGeo, darkMetalMat); c4.position.set(1.8, 3.0, 1.2);
                group.add(c1); group.add(c2); group.add(c3); group.add(c4);

                // Upper Crown
                const topGeo = new THREE.BoxGeometry(4.8, 1.3, 3.2);
                const topCrown = new THREE.Mesh(topGeo, bodyMat);
                topCrown.position.set(0, 5.5, 0);
                group.add(topCrown);

                // Main Hydraulic Cylinder
                const cylGeo = new THREE.CylinderGeometry(0.8, 0.8, 1.6, 20);
                const cyl = new THREE.Mesh(cylGeo, darkMetalMat);
                cyl.position.set(0, 4.4, 0);
                group.add(cyl);

                // Moving Press Ram Die (Reciprocating motion)
                const ramGeo = new THREE.BoxGeometry(3.4, 0.9, 2.4);
                const ramMat = new THREE.MeshStandardMaterial({{ color: 0xef4444, metalness: 0.6, roughness: 0.3 }});
                const ram = new THREE.Mesh(ramGeo, ramMat);
                ram.position.set(0, 2.6, 0);
                group.add(ram);

                // Safety Optical Light Curtains
                const curtainGeo = new THREE.CylinderGeometry(0.08, 0.08, 4.0, 8);
                const curtainMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
                const curL = new THREE.Mesh(curtainGeo, curtainMat); curL.position.set(-2.0, 2.4, 1.6);
                const curR = new THREE.Mesh(curtainGeo, curtainMat); curR.position.set(2.0, 2.4, 1.6);
                group.add(curL); group.add(curR);

                animatedParts.push({{ mesh: ram, type: "oscillateY", base: 2.6, amp: 0.85, freq: sInfo.state === "Critical" ? 3.5 : 1.6 }});

            }} else if (cfg.type === "conveyor") {{
                // 4. M-04: Conveyor System
                // Structural Frame
                const frameGeo = new THREE.BoxGeometry(6.4, 0.8, 2.4);
                const frame = new THREE.Mesh(frameGeo, bodyMat);
                frame.position.set(0, 1.2, 0);
                group.add(frame);

                // Support Legs
                const legGeo = new THREE.CylinderGeometry(0.12, 0.12, 1.0, 8);
                const l1 = new THREE.Mesh(legGeo, darkMetalMat); l1.position.set(-2.8, 0.7, -1.0);
                const l2 = new THREE.Mesh(legGeo, darkMetalMat); l2.position.set(2.8, 0.7, -1.0);
                const l3 = new THREE.Mesh(legGeo, darkMetalMat); l3.position.set(-2.8, 0.7, 1.0);
                const l4 = new THREE.Mesh(legGeo, darkMetalMat); l4.position.set(2.8, 0.7, 1.0);
                group.add(l1); group.add(l2); group.add(l3); group.add(l4);

                // Conveyor Belt
                const beltGeo = new THREE.BoxGeometry(6.2, 0.08, 2.0);
                const beltMat = new THREE.MeshStandardMaterial({{ color: 0x0f172a, roughness: 0.95 }});
                const belt = new THREE.Mesh(beltGeo, beltMat);
                belt.position.set(0, 1.65, 0);
                group.add(belt);

                // Drive Motor on End
                const dMotorGeo = new THREE.CylinderGeometry(0.45, 0.45, 1.0, 16);
                dMotorGeo.rotateZ(Math.PI / 2);
                const dMotor = new THREE.Mesh(dMotorGeo, darkMetalMat);
                dMotor.position.set(3.4, 1.2, 0);
                group.add(dMotor);

                // Moving Pallets on the belt
                const p1 = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.6, 0.9), new THREE.MeshStandardMaterial({{ color: 0xf59e0b }}));
                p1.position.set(-2.2, 2.0, 0);
                group.add(p1);

                const p2 = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.6, 0.9), new THREE.MeshStandardMaterial({{ color: 0x38bdf8 }}));
                p2.position.set(0.4, 2.0, 0);
                group.add(p2);

                animatedParts.push({{ mesh: p1, type: "conveyorMove", minX: -2.8, maxX: 2.8, speed: sInfo.state === "Critical" ? 0.06 : 0.025 }});
                animatedParts.push({{ mesh: p2, type: "conveyorMove", minX: -2.8, maxX: 2.8, speed: sInfo.state === "Critical" ? 0.06 : 0.025 }});

            }} else if (cfg.type === "cooling") {{
                // 5. M-05: Cooling Unit (Industrial Chiller)
                // Main Chiller Cabinet
                const cabGeo = new THREE.BoxGeometry(4.8, 3.4, 3.6);
                const cab = new THREE.Mesh(cabGeo, bodyMat);
                cab.position.set(0, 2.1, 0);
                group.add(cab);

                // Louvered Ventilation Side Panels
                const louverGeo = new THREE.BoxGeometry(4.4, 2.4, 0.1);
                const louverMat = new THREE.MeshStandardMaterial({{ color: 0x111827, roughness: 0.9 }});
                const louverFront = new THREE.Mesh(louverGeo, louverMat); louverFront.position.set(0, 2.1, 1.82);
                const louverBack = new THREE.Mesh(louverGeo, louverMat); louverBack.position.set(0, 2.1, -1.82);
                group.add(louverFront); group.add(louverBack);

                // Twin Top Exhaust Fan Cowls
                const cowlGeo = new THREE.CylinderGeometry(0.95, 0.95, 0.6, 20);
                const cowl1 = new THREE.Mesh(cowlGeo, darkMetalMat); cowl1.position.set(-1.3, 4.0, 0);
                const cowl2 = new THREE.Mesh(cowlGeo, darkMetalMat); cowl2.position.set(1.3, 4.0, 0);
                group.add(cowl1); group.add(cowl2);

                // Fan Blades
                function makeFan() {{
                    const fanG = new THREE.Group();
                    for (let i = 0; i < 4; i++) {{
                        const bGeo = new THREE.BoxGeometry(0.7, 0.05, 0.22);
                        const blade = new THREE.Mesh(bGeo, chromeMat);
                        blade.rotation.y = (Math.PI / 2) * i;
                        fanG.add(blade);
                    }}
                    return fanG;
                }}
                const fan1 = makeFan(); fan1.position.set(-1.3, 4.2, 0); group.add(fan1);
                const fan2 = makeFan(); fan2.position.set(1.3, 4.2, 0); group.add(fan2);

                animatedParts.push({{ mesh: fan1, type: "rotateY", speed: sInfo.state === "Critical" ? 0.45 : 0.2 }});
                animatedParts.push({{ mesh: fan2, type: "rotateY", speed: sInfo.state === "Critical" ? -0.45 : -0.2 }});

                // Chiller Coolant Piping (Cyan supply, Orange return)
                const pipe1 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 1.8, 12), cyanAccentMat);
                pipe1.position.set(-2.55, 2.2, -0.6);
                pipe1.rotation.z = Math.PI / 2;
                group.add(pipe1);

                const pipe2 = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 1.8, 12), new THREE.MeshStandardMaterial({{ color: 0xf97316 }}));
                pipe2.position.set(-2.55, 2.2, 0.6);
                pipe2.rotation.z = Math.PI / 2;
                group.add(pipe2);

            }} else if (cfg.type === "robot") {{
                // 6. M-06: Assembly Station (Robotic Cell)
                // Safety Enclosure Cage Pillars
                const cagePoleGeo = new THREE.CylinderGeometry(0.08, 0.08, 4.8, 8);
                const cageMat = new THREE.MeshBasicMaterial({{ color: 0xf59e0b }});
                const cp1 = new THREE.Mesh(cagePoleGeo, cageMat); cp1.position.set(-2.3, 2.4, -1.7);
                const cp2 = new THREE.Mesh(cagePoleGeo, cageMat); cp2.position.set(2.3, 2.4, -1.7);
                const cp3 = new THREE.Mesh(cagePoleGeo, cageMat); cp3.position.set(-2.3, 2.4, 1.7);
                const cp4 = new THREE.Mesh(cagePoleGeo, cageMat); cp4.position.set(2.3, 2.4, 1.7);
                group.add(cp1); group.add(cp2); group.add(cp3); group.add(cp4);

                // Base Pedestal
                const pedGeo = new THREE.CylinderGeometry(1.0, 1.2, 1.2, 16);
                const ped = new THREE.Mesh(pedGeo, darkMetalMat);
                ped.position.set(0, 1.0, 0);
                group.add(ped);

                // Swiveling Arm Shoulder
                const armGroup = new THREE.Group();
                armGroup.position.set(0, 1.6, 0);

                const lowerArm = new THREE.Mesh(new THREE.BoxGeometry(0.5, 2.4, 0.5), bodyMat);
                lowerArm.position.set(0, 1.2, 0);
                armGroup.add(lowerArm);

                // Forearm & Elbow
                const foreArmGroup = new THREE.Group();
                foreArmGroup.position.set(0, 2.3, 0);
                const foreArm = new THREE.Mesh(new THREE.BoxGeometry(0.4, 2.0, 0.4), new THREE.MeshStandardMaterial({{ color: 0x0284c7 }}));
                foreArm.position.set(0.3, 0.8, 0);
                foreArm.rotation.z = -0.55;
                foreArmGroup.add(foreArm);

                // Precision End-Effector / Welding Torch Head
                const toolGeo = new THREE.ConeGeometry(0.2, 0.6, 12);
                toolGeo.rotateZ(Math.PI);
                const tool = new THREE.Mesh(toolGeo, new THREE.MeshBasicMaterial({{ color: 0x00ffff }}));
                tool.position.set(0.9, 0.1, 0);
                foreArmGroup.add(tool);

                armGroup.add(foreArmGroup);
                group.add(armGroup);

                animatedParts.push({{ mesh: armGroup, type: "swivelArm", speed: sInfo.state === "Critical" ? 2.8 : 1.4 }});
                animatedParts.push({{ mesh: foreArmGroup, type: "nodArm", speed: sInfo.state === "Critical" ? 3.2 : 1.6 }});
            }}

            // -----------------------------------------------------
            // Stack Beacon Indicator on top of every machine
            // -----------------------------------------------------
            const poleGeo = new THREE.CylinderGeometry(0.06, 0.06, 1.2, 8);
            const pole = new THREE.Mesh(poleGeo, darkMetalMat);
            pole.position.set(2.0, cfg.labelY - 1.2, 1.6);
            group.add(pole);

            const beaconColor = (sInfo.state === "Critical") ? 0xef4444 : (sInfo.state === "Warning" ? 0xf59e0b : 0x10b981);
            const beaconMat = new THREE.MeshStandardMaterial({{
                color: beaconColor,
                emissive: beaconColor,
                emissiveIntensity: sInfo.state === "Critical" ? 1.8 : 0.85,
                roughness: 0.2
            }});
            const beacon = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.22, 0.5, 16), beaconMat);
            beacon.position.set(2.0, cfg.labelY - 0.55, 1.6);
            group.add(beacon);

            if (sInfo.state === "Critical") {{
                const beaconLight = new THREE.PointLight(0xef4444, 2.8, 9);
                beaconLight.position.set(2.0, cfg.labelY - 0.4, 1.6);
                group.add(beaconLight);
                animatedParts.push({{ light: beaconLight, type: "pulseLight" }});
            }}

            scene.add(group);
            machineGroupsMap[cfg.id] = group;
            interactiveMeshes.push(group);
        }});

        // ---------------------------------------------------------
        // Dynamic Holographic Selection Ring & Beam
        // ---------------------------------------------------------
        const haloGeo = new THREE.RingGeometry(3.6, 4.0, 36);
        haloGeo.rotateX(-Math.PI / 2);
        const haloMat = new THREE.MeshBasicMaterial({{
            color: 0x00f0ff,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 0.9
        }});
        selectionHalo = new THREE.Mesh(haloGeo, haloMat);
        selectionHalo.position.set(0, 0.45, 0);
        scene.add(selectionHalo);

        const beamGeo = new THREE.CylinderGeometry(3.5, 3.5, 6.2, 32, 1, true);
        const beamMat = new THREE.MeshBasicMaterial({{
            color: 0x00d2ff,
            transparent: true,
            opacity: 0.12,
            side: THREE.DoubleSide
        }});
        selectionBeam = new THREE.Mesh(beamGeo, beamMat);
        selectionBeam.position.set(0, 3.4, 0);
        scene.add(selectionBeam);

        // Position halo to initially selected machine
        const initSpec = MACHINE_SPECS.find(s => s.id === currentSelectedId) || MACHINE_SPECS[0];
        selectionHalo.position.set(initSpec.x, 0.45, initSpec.z);
        selectionBeam.position.set(initSpec.x, 3.4, initSpec.z);

        // ---------------------------------------------------------
        // Autonomous Inspection Robot (AGV) Patrol Unit
        // ---------------------------------------------------------
        const agvGroup = new THREE.Group();
        const agvBody = new THREE.Mesh(
            new THREE.BoxGeometry(1.7, 0.65, 1.2),
            new THREE.MeshStandardMaterial({{ color: 0x0284c7, metalness: 0.8, roughness: 0.3 }})
        );
        agvBody.position.y = 0.45;
        agvGroup.add(agvBody);

        // AGV Wheels
        const wGeo = new THREE.CylinderGeometry(0.26, 0.26, 0.2, 16);
        wGeo.rotateZ(Math.PI / 2);
        const wMat = new THREE.MeshStandardMaterial({{ color: 0x111827 }});
        const w1 = new THREE.Mesh(wGeo, wMat); w1.position.set(-0.65, 0.26, 0.6);
        const w2 = new THREE.Mesh(wGeo, wMat); w2.position.set(0.65, 0.26, 0.6);
        const w3 = new THREE.Mesh(wGeo, wMat); w3.position.set(-0.65, 0.26, -0.6);
        const w4 = new THREE.Mesh(wGeo, wMat); w4.position.set(0.65, 0.26, -0.6);
        agvGroup.add(w1); agvGroup.add(w2); agvGroup.add(w3); agvGroup.add(w4);

        // LiDAR Scanning Dome
        const dome = new THREE.Mesh(
            new THREE.CylinderGeometry(0.24, 0.24, 0.22, 16),
            new THREE.MeshBasicMaterial({{ color: 0x00f0ff }})
        );
        dome.position.set(0, 0.9, 0);
        agvGroup.add(dome);

        const agvScannerLight = new THREE.PointLight(0x00f0ff, 1.8, 7);
        agvScannerLight.position.set(0, 1.1, 0);
        agvGroup.add(agvScannerLight);

        scene.add(agvGroup);

        const waypoints = [
            new THREE.Vector3(-18, 0, -2),
            new THREE.Vector3(18, 0, -2),
            new THREE.Vector3(18, 0, 2),
            new THREE.Vector3(-18, 0, 2)
        ];
        let currentWpIndex = 0;

        // ---------------------------------------------------------
        // Raycaster & Click Selection on 3D Meshes
        // ---------------------------------------------------------
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const tooltip = document.getElementById('tooltip');

        function findMachineFromHit(obj) {{
            let curr = obj;
            while (curr) {{
                if (curr.userData && curr.userData.id) {{
                    return curr.userData;
                }}
                curr = curr.parent;
            }}
            return null;
        }}

        window.addEventListener('mousemove', (e) => {{
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(interactiveMeshes, true);

            let hitMachine = null;
            if (intersects.length > 0) {{
                hitMachine = findMachineFromHit(intersects[0].object);
            }}

            if (hitMachine) {{
                renderer.domElement.style.cursor = 'pointer';
                tooltip.style.display = 'block';
                tooltip.style.left = (e.clientX + 14) + 'px';
                tooltip.style.top = (e.clientY + 14) + 'px';
                const sInfo = getStatusInfo(fleetData[hitMachine.id]);
                tooltip.innerHTML = `<b>${{hitMachine.id}}</b>: ${{hitMachine.name}}<br>Status: <span style="color:${{sInfo.color}};font-weight:700;">${{sInfo.state.toUpperCase()}}</span><br><i>Click to inspect machine</i>`;
            }} else {{
                renderer.domElement.style.cursor = 'default';
                tooltip.style.display = 'none';
            }}
        }});

        window.addEventListener('click', (e) => {{
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObjects(interactiveMeshes, true);
            if (intersects.length > 0) {{
                const hit = findMachineFromHit(intersects[0].object);
                if (hit && hit.id) {{
                    selectMachine(hit.id);
                }}
            }}
        }});

        // ---------------------------------------------------------
        // Animation Loop & Permanent Label Positioning
        // ---------------------------------------------------------
        const clock = new THREE.Clock();
        const tempVec = new THREE.Vector3();

        function animate() {{
            requestAnimationFrame(animate);
            const delta = clock.getDelta();
            const time = clock.getElapsedTime();

            controls.update();

            // Animate Mechanical Subsystems
            animatedParts.forEach(p => {{
                if (p.type === "rotateY") p.mesh.rotation.y += p.speed;
                if (p.type === "rotateX") p.mesh.rotation.x += p.speed;
                if (p.type === "oscillateY") p.mesh.position.y = p.base + Math.sin(time * p.freq) * p.amp;
                if (p.type === "conveyorMove") {{
                    p.mesh.position.x += p.speed;
                    if (p.mesh.position.x > p.maxX) p.mesh.position.x = p.minX;
                }}
                if (p.type === "swivelArm") p.mesh.rotation.y = Math.sin(time * p.speed) * 0.75;
                if (p.type === "nodArm") p.mesh.rotation.z = Math.sin(time * p.speed) * 0.35 - 0.55;
                if (p.type === "pulseLight") p.light.intensity = 1.6 + Math.sin(time * 8) * 1.5;
            }});

            // Animate selection halo pulsing
            if (selectionHalo) {{
                const s = 1.0 + Math.sin(time * 3) * 0.05;
                selectionHalo.scale.set(s, s, s);
            }}

            // Move Autonomous Inspection Robot (AGV)
            const targetWp = waypoints[currentWpIndex];
            const dir = new THREE.Vector3().subVectors(targetWp, agvGroup.position);
            const dist = dir.length();
            if (dist < 0.25) {{
                currentWpIndex = (currentWpIndex + 1) % waypoints.length;
            }} else {{
                dir.normalize();
                agvGroup.position.addScaledVector(dir, delta * 4.2);
                const angle = Math.atan2(dir.x, dir.z);
                agvGroup.rotation.y = angle;
            }}

            // Update Permanent Overhead Labels (World Space -> 2D Screen Space)
            MACHINE_SPECS.forEach(spec => {{
                const lbl = document.getElementById('label-' + spec.id);
                if (!lbl) return;

                tempVec.set(spec.x, spec.labelY, spec.z);
                tempVec.project(camera);

                // Check if machine is in front of camera lens
                if (tempVec.z > 1.0) {{
                    lbl.style.display = 'none';
                }} else {{
                    lbl.style.display = 'inline-flex';
                    const x = (tempVec.x * 0.5 + 0.5) * window.innerWidth;
                    const y = (-(tempVec.y * 0.5) + 0.5) * window.innerHeight;
                    lbl.style.left = `${{x}}px`;
                    lbl.style.top = `${{y}}px`;
                }}
            }});

            renderer.render(scene, camera);
        }}

        animate();

        // Responsive Resizing
        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    }}

    // -------------------------------------------------------------
    // Canvas 2.5D Isometric Fallback (If Three.js fails to load)
    // -------------------------------------------------------------
    function initCanvasFallback() {{
        const webglCont = document.getElementById('webgl-container');
        if (webglCont) webglCont.style.display = 'none';
        const canvas = document.getElementById('fallback-canvas');
        canvas.style.display = 'block';
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {{
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }}
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        let t = 0;
        function drawIsometricScene() {{
            t += 0.03;
            ctx.fillStyle = '#0a0d14';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            const cx = canvas.width / 2;
            const cy = canvas.height / 2 - 20;

            // Draw Isometric Grid
            ctx.strokeStyle = '#1e293b';
            ctx.lineWidth = 1;
            for (let i = -6; i <= 6; i++) {{
                ctx.beginPath();
                ctx.moveTo(cx + (i - 6) * 45, cy + (i + 6) * 22);
                ctx.lineTo(cx + (i + 6) * 45, cy + (i - 6) * 22);
                ctx.stroke();

                ctx.beginPath();
                ctx.moveTo(cx + (-6 + i) * 45, cy + (-6 - i) * 22);
                ctx.lineTo(cx + (6 + i) * 45, cy + (6 - i) * 22);
                ctx.stroke();
            }}

            // Render 6 Machines with isometric projection
            MACHINE_SPECS.forEach(s => {{
                const mData = fleetData[s.id] || {{}};
                const sInfo = getStatusInfo(mData);

                // Simple Iso conversion
                const ix = cx + (s.x * 2.2 - s.z * 1.5) * 8;
                const iy = cy + (s.x * 1.1 + s.z * 1.5) * 4.5;

                // Base plinth
                ctx.fillStyle = s.id === currentSelectedId ? '#00f0ff' : '#1e293b';
                ctx.fillRect(ix - 32, iy - 20, 64, 40);

                // Machine body block
                ctx.fillStyle = sInfo.color;
                ctx.fillRect(ix - 24, iy - 48, 48, 36);

                // Update DOM label positions in fallback mode
                const lbl = document.getElementById('label-' + s.id);
                if (lbl) {{
                    lbl.style.display = 'inline-flex';
                    lbl.style.left = `${{ix}}px`;
                    lbl.style.top = `${{iy - 56}}px`;
                }}
            }});

            requestAnimationFrame(drawIsometricScene);
        }}
        drawIsometricScene();
    }}
</script>
</body>
</html>"""
    return html
