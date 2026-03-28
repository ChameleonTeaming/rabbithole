import logging
import json
import os
import collections
import ssl
import datetime
import hmac
import secrets
import base64
import asyncio
import random
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [HIVEMIND] %(message)s')
logger = logging.getLogger("HiveMindHub")

# Persistent Database for Nodes
NODES_FILE = "nodes.json"
def load_nodes():
    if os.path.exists(NODES_FILE):
        try:
            with open(NODES_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_nodes():
    try:
        with open(NODES_FILE, 'w') as f: json.dump(NODES, f)
    except: pass

NODES = load_nodes()
INCIDENTS_DB = collections.deque(maxlen=100)
GLOBAL_BLOCKLIST = set(["103.20.15.1", "45.33.22.11"]) 
SOCKETS = []

SECRET_TOKEN = os.getenv('HIVE_MIND_TOKEN', '6d3574ff21cc17ab6b00405020f2a277')

async def broadcast(data):
    for ws in SOCKETS:
        try: await ws.send_json(data)
        except: pass

def register_node(node_id, ip, persona=None):
    NODES[node_id] = {
        "last_seen": datetime.datetime.now().isoformat(),
        "last_ip": ip,
        "status": "ACTIVE",
        "persona": persona or NODES.get(node_id, {}).get('persona', 'UNKNOWN')
    }
    save_nodes()

async def handle_incident(request):
    try:
        auth = request.headers.get("Authorization")
        if not auth or not hmac.compare_digest(auth, f"Bearer {SECRET_TOKEN}"):
            return web.Response(status=401)

        data = await request.json()
        node_id = data.get('node_id', 'unknown_node')
        event_type = data.get('type', 'incident')
        
        register_node(node_id, request.remote, data.get('persona'))
        
        if event_type == 'incident':
            INCIDENTS_DB.append(data)
            if 'ip' in data: GLOBAL_BLOCKLIST.add(data['ip'])
        
        await broadcast({"type": event_type, "node_id": node_id, "data": data})
        return web.Response(status=201)
    except: return web.Response(status=500)

async def handle_blocklist(request):
    auth = request.headers.get("Authorization")
    if not auth or not hmac.compare_digest(auth, f"Bearer {SECRET_TOKEN}"):
        return web.Response(status=401)
    
    node_id = request.query.get('node_id')
    if node_id:
        register_node(node_id, request.remote)
        
    return web.json_response(list(GLOBAL_BLOCKLIST))

async def handle_ws(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    SOCKETS.append(ws)
    try:
        async for msg in ws:
            if msg.type == web.WSMsgType.TEXT and msg.data == 'close': await ws.close()
    finally:
        if ws in SOCKETS: SOCKETS.remove(ws)
    return ws

async def handle_hub_status(request):
    return web.json_response({
        "status": "OPERATIONAL",
        "node_count": len(NODES),
        "nodes": NODES,
        "blocklist_size": len(GLOBAL_BLOCKLIST)
    })

async def handle_index(request):
    html = """
    <!DOCTYPE html><html><head><title>HIVE_MIND // EXOTIC_COMMAND</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="//unpkg.com/three"></script>
    <script src="//unpkg.com/globe.gl"></script>
    <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root { --neon: #f97316; --cyan: #00f3ff; --bg: #030305; --purple: #a855f7; }
        * { box-sizing: border-box; }
        body, html { 
            background: var(--bg); 
            color: #fff; 
            margin: 0; 
            padding: 0; 
            font-family: 'Rajdhani', sans-serif; 
            min-height: 100vh;
            overflow-y: scroll !important; /* Force native scrollbar */
        }
        
        .scanlines { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06)); z-index: 999; background-size: 100% 4px, 3px 100%; pointer-events: none; }
        .crt-curve { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1000; pointer-events: none; box-shadow: inset 0 0 100px rgba(0,0,0,0.5); background: radial-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 100%); }
        
        #neural-canvas { position: fixed; top: 0; left: 0; z-index: -1; opacity: 0.2; }

        .glass { background: rgba(255, 255, 255, 0.02); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 4px; box-shadow: 0 0 20px rgba(0,0,0,0.5); }
        .neon-border-orange { border-left: 3px solid var(--neon); }
        .neon-border-cyan { border-left: 3px solid var(--cyan); }
        .neon-border-purple { border-left: 3px solid var(--purple); }
        .terminal { font-family: 'Share Tech Mono', monospace; }
        
        @keyframes glitch { 0% { transform: translate(0); } 20% { transform: translate(-2px, 2px); } 40% { transform: translate(-2px, -2px); } 60% { transform: translate(2px, 2px); } 80% { transform: translate(2px, -2px); } 100% { transform: translate(0); } }
        .glitch-active { animation: glitch 0.2s infinite; filter: hue-rotate(90deg); }
        
        .node-pulse { width: 8px; height: 8px; border-radius: 50%; background: var(--cyan); box-shadow: 0 0 10px var(--cyan); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { transform: scale(1); opacity: 1; } 100% { transform: scale(2.5); opacity: 0; } }
        
        #map-container { height: 400px; width: 100%; border-radius: 8px; overflow: hidden; margin-bottom: 2rem; position: relative; border: 1px solid rgba(0, 243, 255, 0.1); }
        .map-label { position: absolute; top: 10px; left: 10px; text-[10px] text-cyan-500 font-mono tracking-widest z-20; }
        
        ::-webkit-scrollbar { width: 10px; }
        ::-webkit-scrollbar-track { background: #050505; }
        ::-webkit-scrollbar-thumb { background: #333; border-radius: 5px; border: 2px solid #050505; }
        ::-webkit-scrollbar-thumb:hover { background: #444; }
    </style></head>
    <body class="p-8">
        <div class="scanlines"></div>
        <div class="crt-curve"></div>
        <canvas id="neural-canvas"></canvas>

        <div class="relative z-10 max-w-[1800px] mx-auto pb-32">
            <header class="flex justify-between items-center mb-12 border-b border-white/5 pb-6">
                <div>
                    <div class="text-[10px] text-orange-500 tracking-[0.8em] font-bold mb-2 uppercase">Neural_Deception_Grid // APEX_CORE</div>
                    <h1 class="text-6xl font-light tracking-tighter uppercase italic">Hive<span class="text-orange-500 font-bold">Mind</span> <span class="text-[12px] tracking-normal not-italic opacity-30">V4.0_ALPHA</span></h1>
                </div>
                <div class="flex gap-12 terminal">
                    <div class="text-right">
                        <div class="text-zinc-600 text-[9px] uppercase tracking-widest">Global_Nodes</div>
                        <div class="text-4xl font-bold text-white" id="node-count">0</div>
                    </div>
                    <div class="text-right">
                        <div class="text-zinc-600 text-[9px] uppercase tracking-widest">Mesh_Integrity</div>
                        <div class="text-4xl font-bold text-cyan-400">100%</div>
                    </div>
                </div>
            </header>

            <div id="map-container" class="glass">
                <div class="map-label uppercase">Global_Attack_Vectors // Real-Time_Attribution</div>
                <div id="map" style="height: 100%; width: 100%;"></div>
            </div>

            <div class="grid grid-cols-12 gap-10">
                <div class="col-span-12 lg:col-span-4 flex flex-col gap-8">
                    <div class="glass p-6 neon-border-orange relative overflow-hidden">
                        <div class="absolute -right-4 -bottom-4 text-orange-500/5 text-9xl font-bold uppercase">Apex</div>
                        <h2 class="text-xs font-bold text-orange-500 mb-6 tracking-[0.4em] uppercase">The_Architect_Oversight</h2>
                        <div id="architect-log" class="space-y-4 terminal">
                            <div class="text-zinc-700 text-[10px] italic">Handshaking with Project Panopticon...</div>
                        </div>
                    </div>

                    <div class="glass p-6 neon-border-cyan">
                        <h2 class="text-xs font-bold text-cyan-400 mb-6 tracking-[0.4em] uppercase">Node_Registry_Matrix</h2>
                        <div id="node-list" class="grid grid-cols-2 gap-3"></div>
                    </div>
                </div>

                <div class="col-span-12 lg:col-span-8 flex flex-col gap-8">
                    <div class="glass p-8 min-h-[600px] flex flex-col border-white/5 neon-border-purple">
                        <div class="flex justify-between items-center mb-8 border-b border-white/5 pb-4">
                            <h2 class="text-lg font-light tracking-[0.3em] uppercase text-purple-400">Neural_Reverse-Engineering_Lab</h2>
                            <div class="text-[10px] text-purple-500 animate-pulse terminal uppercase">AI_Deconstruction_Active</div>
                        </div>
                        <div id="incident-feed" class="flex-1 space-y-6 terminal">
                            <div class="text-zinc-800 italic">Decompiling incoming malicious payloads...</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Neural Canvas
            const canvas = document.getElementById('neural-canvas');
            const ctx = canvas.getContext('2d');
            let particles = [];
            function initCanvas() {
                canvas.width = window.innerWidth; canvas.height = window.innerHeight;
                particles = [];
                for(let i=0; i<80; i++) particles.push({ x: Math.random()*canvas.width, y: Math.random()*canvas.height, vx: (Math.random()-0.5)*0.5, vy: (Math.random()-0.5)*0.5 });
            }
            function drawNeural() {
                ctx.clearRect(0,0,canvas.width, canvas.height);
                ctx.strokeStyle = 'rgba(0, 243, 255, 0.1)'; ctx.fillStyle = 'rgba(0, 243, 255, 0.5)';
                particles.forEach((p, i) => {
                    p.x += p.vx; p.y += p.vy;
                    if(p.x<0 || p.x>canvas.width) p.vx *= -1;
                    if(p.y<0 || p.y>canvas.height) p.vy *= -1;
                    ctx.beginPath(); ctx.arc(p.x, p.y, 1, 0, Math.PI*2); ctx.fill();
                    particles.forEach((p2, j) => {
                        if(i === j) return;
                        let dist = Math.hypot(p.x-p2.x, p.y-p2.y);
                        if(dist < 150) { ctx.lineWidth = 1 - dist/150; ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(p2.x, p2.y); ctx.stroke(); }
                    });
                });
                requestAnimationFrame(drawNeural);
            }
            window.addEventListener('resize', initCanvas);
            initCanvas(); drawNeural();

            // Globe
            const globe = Globe()
                .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
                .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
                .backgroundColor('rgba(0,0,0,0)')
                .pointColor(() => '#f97316').pointAltitude(0.1).pointRadius(0.5)
                .ringColor(() => '#00f3ff').ringMaxRadius(10).ringPropagationSpeed(3).ringRepeatPeriod(1000)
                (document.getElementById('map'));
            globe.controls().autoRotate = true; globe.controls().autoRotateSpeed = 0.5;

            // WS
            const ws = new WebSocket((window.location.protocol === 'https:' ? 'wss:' : 'ws:') + '//' + window.location.host + '/ws');
            const nodes = new Set();
            const ringData = [];

            window.onload = () => {
                fetch('/api/status').then(r => r.json()).then(d => {
                    if(d.nodes) Object.keys(d.nodes).forEach(id => updateNodeList(id));
                });
            };

            ws.onmessage = (e) => {
                const msg = JSON.parse(e.data);
                if(msg.type === 'incident') handleIncident(msg.data, msg.node_id);
                if(['drift', 'breaker', 'hardware'].includes(msg.type)) handleApex(msg.type, msg.data, msg.node_id);
                if(msg.type === 'architect') handleArchitect(msg.data, msg.op_type);
                if(msg.node_id) updateNodeList(msg.node_id);
            };

            function handleIncident(data, nodeId) {
                const feed = document.getElementById('incident-feed');
                const div = document.createElement('div');
                div.className = "p-6 bg-purple-500/[0.02] border border-purple-500/10 rounded-sm hover:bg-purple-500/[0.05] transition-all mb-6";
                div.innerHTML = `<div class="flex justify-between text-[10px] mb-4">
                                    <span class="text-purple-400 font-bold uppercase tracking-widest">Neural_Reverse_Op // ${nodeId}</span>
                                    <span class="text-zinc-600 font-mono">${new Date().toLocaleTimeString()}</span>
                                 </div>
                                 <div class="grid grid-cols-2 gap-4 mb-4 text-[10px]">
                                    <div class="text-zinc-500 uppercase">Origin_IP: <span class="text-white">${data.ip}</span></div>
                                    <div class="text-zinc-500 uppercase">ISP: <span class="text-white">${data.attribution ? data.attribution.isp : 'UNKNOWN'}</span></div>
                                 </div>
                                 <div class="text-white text-xs leading-relaxed border-t border-white/5 pt-4 mt-2 whitespace-pre-wrap">${data.report || 'Tactical data capture successful.'}</div>`;
                feed.prepend(div);
                if(data.attribution && data.attribution.lat) { ringData.push({ lat: data.attribution.lat, lng: data.attribution.lon }); globe.ringsData(ringData); if(ringData.length > 20) ringData.shift(); }
                triggerGlitch();
            }

            function handleApex(type, data, nodeId) {
                const feed = document.getElementById('architect-log');
                const div = document.createElement('div');
                div.className = "p-2 bg-red-500/10 border-l-2 border-red-500 text-[10px] mb-2";
                div.innerHTML = `<span class="text-red-400 font-bold uppercase">${type}</span>: ${data.event} via ${nodeId}`;
                feed.prepend(div);
            }

            function handleArchitect(data, opType) {
                const feed = document.getElementById('architect-log');
                const div = document.createElement('div');
                div.className = "p-2 border-b border-white/5 text-[9px] text-zinc-400 mb-2";
                div.innerHTML = `<span class="text-purple-400 font-bold uppercase">${opType}</span>: ${data.event} -> ${data.status || 'OK'}`;
                feed.prepend(div);
            }

            function updateNodeList(nodeId) {
                nodes.add(nodeId);
                document.getElementById('node-count').innerText = nodes.size;
                const list = document.getElementById('node-list');
                if(!document.getElementById('node-' + nodeId)) {
                    const div = document.createElement('div');
                    div.id = 'node-' + nodeId;
                    div.className = "p-3 glass flex items-center gap-3 border-white/5 mb-2";
                    div.innerHTML = `<div class="node-pulse"></div><div class="text-[10px] font-bold text-white uppercase tracking-tighter">${nodeId}</div>`;
                    list.appendChild(div);
                }
            }

            function triggerGlitch() { document.body.classList.add('glitch-active'); setTimeout(() => document.body.classList.remove('glitch-active'), 300); }
        </script>
    </body></html>
    """
    return web.Response(text=html, content_type='text/html')

async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/', handle_index),
        web.get('/ws', handle_ws),
        web.post('/api/incident', handle_incident),
        web.get('/api/blocklist', handle_blocklist),
        web.get('/api/status', handle_hub_status)
    ])
    return app

if __name__ == '__main__':
    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('cert.pem', 'key.pem')
        web.run_app(init_app(), port=9443, ssl_context=ssl_context)
    except Exception as e:
        exit(1)
