with open('rabbithole.py', 'r') as f:
    lines = f.readlines()

head = lines[:1905]

tail_content = r"""
class CommandCenter:
    def __init__(self, the_void):
        self.the_void, self.app = the_void, web.Application()
        self.app.add_routes([
            web.get('/', self.handle_index), 
            web.get('/api/stats', self.handle_stats),
            web.get('/ws', self.handle_ws)
        ])
        self.username, self.password = os.getenv('DASHBOARD_USER', 'admin'), os.getenv('DASHBOARD_PASS', 'admin')
        self.sockets = []
        if self.username == 'admin' or self.password == 'admin':
            logger.critical("SECURITY ALERT: Dashboard using default credentials. Change immediately via DASHBOARD_PASS environment variable.")

    async def handle_ws(self, request):
        try:
            self._require_auth(request)
        except web.HTTPUnauthorized:
            return web.Response(status=401)
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.sockets.append(ws)
        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    if msg.data == 'close': await ws.close()
        finally:
            if ws in self.sockets: self.sockets.remove(ws)
        return ws

    async def broadcast(self, data):
        for ws in self.sockets:
            try:
                await ws.send_json(data)
            except: pass

    def _require_auth(self, r):
        h = r.headers.get('Authorization')
        if not h: raise web.HTTPUnauthorized(headers={'WWW-Authenticate': 'Basic'})
        try:
            e = h.split(' ', 1)[1]
            d = base64.b64decode(e).decode('utf-8')
            u, p = d.split(':', 1)
            if u != self.username or p != self.password: raise web.HTTPUnauthorized()
        except: raise web.HTTPUnauthorized()

    async def handle_index(self, r):
        self._require_auth(r)
        html = r'''
        <!DOCTYPE html><html><head><title>Mission Control</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="//unpkg.com/three"></script>
        <script src="//unpkg.com/globe.gl"></script>
        <style>
            body { font-family: 'Courier New', monospace; background: #000; color: #00ff41; overflow: hidden; }
            .card { background: rgba(10, 10, 10, 0.9); border: 1px solid #333; box-shadow: 0 0 10px rgba(0, 255, 65, 0.1); }
            #map { height: 500px; width: 100%; border: 1px solid #00ff41; }
            .scrollbar-hide::-webkit-scrollbar { display: none; }
            .log-entry { border-bottom: 1px solid #111; padding: 2px 0; font-size: 10px; }
            .alert-mode { border: 2px solid red; animation: flash-border 1s infinite; }
            @keyframes flash-border { 0% { border-color: red; } 50% { border-color: transparent; } 100% { border-color: red; } }
        </style></head>
        <body class="p-4 transition-all duration-500" id="main-body">
        <div class="flex justify-between items-center mb-4">
            <h1 class="text-2xl font-bold text-green-500 tracking-tighter">RABBITHOLE // <span class="text-white">NEURAL_GLOBE_v3.1</span></h1>
            <div class="space-x-4">
                <button onclick="simulateTrace()" class="bg-blue-900 hover:bg-blue-700 text-white px-3 py-1 rounded border border-blue-500 text-xs font-bold">SIMULATE TRACE</button>
                <button onclick="toggleLockdown()" class="bg-red-900 hover:bg-red-700 text-white px-3 py-1 rounded border border-red-500 text-xs font-bold animate-pulse">INITIATE LOCKDOWN</button>
            </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 mb-4">
            <div class="lg:col-span-3 card p-0 relative overflow-hidden" style="height: 500px;">
                <div id="map"></div>
                <div class="absolute top-2 right-2 z-10 bg-black/80 p-2 border border-green-500 text-[10px] shadow-[0_0_10px_#00ff00]">
                    <div>SATELLITE: <span class="text-green-400">NEURAL LINK ACTIVE</span></div>
                    <div>STATUS: <span class="text-blue-400" id="map-status">INITIALIZING...</span></div>
                </div>
            </div>
            <div class="grid grid-cols-1 gap-4">
                <div class="card p-4">
                    <h2 class="text-zinc-500 text-[10px] mb-2">GLOBE COMMAND</h2>
                    <div class="flex items-center justify-between mb-2"><span class="text-xs">Real-time Push</span><div class="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_10px_#00ff00]"></div></div>
                    <div class="flex items-center justify-between mb-2"><span class="text-xs">3D Rendering</span><div class="w-2 h-2 bg-blue-500 rounded-full"></div></div>
                    <div class="flex items-center justify-between"><span class="text-xs">Uplink Status</span><div class="w-2 h-2 bg-yellow-500 rounded-full animate-ping"></div></div>
                </div>
                <div class="card p-4 text-center">
                    <h2 class="text-zinc-500 text-[10px]">ACTIVE SESSIONS</h2>
                    <div id="active-count" class="text-4xl font-bold text-red-500 mt-1">0</div>
                </div>
                <div class="card p-4 text-center">
                    <h2 class="text-zinc-500 text-[10px]">THREAT LATENCY</h2>
                    <div id="ai-latency" class="text-3xl font-bold text-blue-500 mt-1">0ms</div>
                </div>
            </div>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-4 gap-4 h-64">
            <div class="card p-2 flex flex-col font-mono text-[10px]">
                <div class="border-b border-zinc-800 pb-1 mb-1 text-zinc-500">->_ RAW_INTERCEPT</div>
                <div id="log-feed" class="flex-1 overflow-y-auto scrollbar-hide"></div>
            </div>
            <div class="card p-2 flex flex-col font-mono text-[10px]">
                <div class="border-b border-zinc-800 pb-1 mb-1 text-blue-500">->_ SHEPHERD_AI</div>
                <div id="shepherd-feed" class="flex-1 overflow-y-auto scrollbar-hide space-y-1"></div>
            </div>
            <div class="card p-2 flex flex-col font-mono text-[10px]">
                <div class="border-b border-zinc-800 pb-1 mb-1 text-orange-500">->_ TARPIT_STATUS</div>
                <div id="tarpit-feed" class="flex-1 overflow-y-auto scrollbar-hide"></div>
            </div>
            <div class="card p-2 flex flex-col font-mono text-[10px]">
                <div class="border-b border-zinc-800 pb-1 mb-1 text-purple-500">->_ ORACLE_INTEL</div>
                <div id="oracle-feed" class="flex-1 overflow-y-auto scrollbar-hide"></div>
            </div>
        </div>

        <script>
            const HOME_LOC = { lat: 37.77, lng: -122.41 }; 
            const globe = Globe()
                .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
                .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
                .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
                .arcColor(() => '#00ff41')
                .arcDashLength(0.4)
                .arcDashGap(4)
                .arcDashAnimateTime(1000)
                .ringColor(() => '#ff4141')
                .ringMaxRadius(5)
                .ringPropagationSpeed(3)
                .ringRepeatPeriod(1000)
                (document.getElementById('map'));

            const arcData = [];
            const ringData = [];
            
            function addHit(lat, lng, ip) {
                const hit = { lat, lng, ip };
                ringData.push(hit);
                arcData.push({
                    startLat: lat, startLng: lng,
                    endLat: HOME_LOC.lat, endLng: HOME_LOC.lng
                });
                
                globe.ringsData(ringData);
                globe.arcsData(arcData);
                
                if (ringData.length > 20) ringData.shift();
                if (arcData.length > 20) arcData.shift();
            }

            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(protocol + '//' + window.location.host + '/ws');
            
            ws.onmessage = (event) => {
                const msg = JSON.parse(event.data);
                if (msg.type === 'attack') {
                    handleAttack(msg.data);
                } else if (msg.type === 'shepherd') {
                    handleShepherd(msg.data);
                } else if (msg.type === 'tarpit') {
                    handleTarpit(msg.data);
                } else if (msg.type === 'oracle') {
                    handleOracle(msg.data);
                }
            };

            function handleAttack(data) {
                const feed = document.getElementById('log-feed');
                const entry = document.createElement('div');
                entry.className = 'log-entry text-zinc-400';
                entry.innerHTML = `<span class="opacity-50">[${data.timestamp}]</span> <b>${data.ip}</b>: ${data.command}`;
                feed.prepend(entry);
                if (feed.childNodes.length > 50) feed.removeChild(feed.lastChild);
                
                if (data.attribution && data.attribution.lat) {
                    addHit(data.attribution.lat, data.attribution.lon, data.ip);
                }
            }

            function handleShepherd(data) {
                const feed = document.getElementById('shepherd-feed');
                const entry = document.createElement('div');
                entry.className = 'border-l border-blue-500 pl-1 mb-1';
                entry.innerHTML = `<div class="flex justify-between text-[8px] opacity-70"><span>${data.ip}</span><span>${data.decision}</span></div>
                                   <div class="text-zinc-500 italic">"${data.command}"</div>
                                   <div class="text-blue-400">-> ${data.response}</div>`;
                feed.prepend(entry);
                if (feed.childNodes.length > 20) feed.removeChild(feed.lastChild);
            }

            function handleTarpit(data) {
                const feed = document.getElementById('tarpit-feed');
                const entry = document.createElement('div');
                entry.className = 'flex justify-between border-b border-zinc-900 pb-1 text-orange-400';
                entry.innerHTML = `<span>${data.ip}</span> <span class="text-zinc-600">[${data.duration}]</span>`;
                feed.prepend(entry);
                if (feed.childNodes.length > 20) feed.removeChild(feed.lastChild);
            }

            function handleOracle(data) {
                const feed = document.getElementById('oracle-feed');
                const entry = document.createElement('div');
                entry.className = 'bg-zinc-900/50 p-1 rounded mb-1 border border-purple-900';
                entry.innerHTML = `<div class="text-purple-400 font-bold uppercase" style="font-size: 8px;">INTEL // ${data.ip}</div>
                                   <div class="text-zinc-400 leading-tight">${data.report.substring(0,80)}...</div>`;
                feed.prepend(entry);
                if (feed.childNodes.length > 10) feed.removeChild(feed.lastChild);
            }

            function simulateTrace() {
                const lat = (Math.random() * 140) - 70;
                const lng = (Math.random() * 360) - 180;
                addHit(lat, lng, "SIM_TARGET");
            }

            async function updateStats() {
                try {
                    const r = await fetch('/api/stats');
                    const d = await r.json();
                    document.getElementById('active-count').innerText = d.active_sessions;
                    document.getElementById('ai-latency').innerText = (d.ai_latency * 1000).toFixed(0) + 'ms';
                    document.getElementById('map-status').innerText = "TRACKING " + arcData.length + " TARGETS";
                } catch(e) {}
            }
            setInterval(updateStats, 2000);
            updateStats();

            function toggleLockdown() {
                document.getElementById('main-body').classList.toggle('alert-mode');
                alert("LOCKDOWN PROTOCOL: OFFLINE MODE ENGAGED (Simulated)");
            }
        </script></body></html>
        """
        return web.Response(text=html, content_type='text/html')

    async def handle_stats(self, r):
        self._require_auth(r)
        map_hits = {}
        for attack in self.the_void.recent_attacks:
            if attack.get('attribution'):
                map_hits[attack['ip']] = attack['attribution']
        active_traces = []
        for ip, session in self.the_void.sessions.items():
            if session.get('trace'):
                active_traces.append({"ip": ip, "attribution": session['trace']})
        return web.json_response({
            "active_sessions": len(self.the_void.sessions),
            "active_traces": active_traces,
            "map_hits": [{"ip": ip, "attribution": attr} for ip, attr in map_hits.items()],
            "recent_logs": list(self.the_void.recent_attacks),
            "reports": list(self.the_void.recent_reports),
            "shepherd_activity": list(self.the_void.shepherd_activity),
            "tarpit_activity": list(self.the_void.tarpit_activity),
            "dossier_count": self._get_dossier_count(),
            "de_anonymized": self.the_void.li.de_anonymized_ips,
            "ai_latency": self.the_void.get_ai_latency()
        })

    def _get_dossier_count(self):
        try:
            with sqlite3.connect(self.the_void.personalities.db_path) as conn: return conn.execute("SELECT COUNT(*) FROM dossiers").fetchone()[0]
        except: return 0

    async def start(self, host='0.0.0.0', port=8888):
        runner = web.AppRunner(self.app); await runner.setup()
        await web.TCPSite(runner, host, port).start()

class RabbitHole:
    def __init__(self, host='0.0.0.0', port=2121):
        self.host, self.port, self.the_void = host, port, TheVoid()

    async def tarpit(self, ip, dk):
        if dk == "none": return
        await asyncio.sleep(random.uniform(1, 3) if dk == "short" else random.uniform(5, 15))

    async def handle_connection(self, r, w):
        addr = w.get_extra_info('peername'); ip = addr[0]
        if ip in ["127.0.0.1", "::1"] or ip.startswith("127."): 
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        if ip in self.the_void.blocked_ips or not self.the_void.register_connection(ip):
            w.close(); await w.wait_closed(); return
        
        loop = asyncio.get_event_loop()
        sandbox = DockerSandbox()
        active_ftp = ACTIVE_SESSIONS.labels(protocol='ftp')._value.get()
        ready = False
        if active_ftp < 5:
            try: ready = await loop.run_in_executor(None, sandbox.create)
            except Exception: ready = False
        
        ACTIVE_SESSIONS.labels(protocol='ftp').inc()
        w.write(b"220 Welcome to RabbitHole FTP\r\n"); await w.drain()
        try:
            while True:
                data = await r.read(1024)
                if not data: break
                cmd = data.decode('utf-8', errors='ignore').strip()
                is_susp, resp, dk = await self.the_void.analyze_command(ip, cmd)
                if is_susp: break
                await self.tarpit(ip, dk)
                if resp: w.write((resp + '\r\n').encode())
                elif ready: w.write(((await loop.run_in_executor(None, sandbox.execute, cmd)) + '\r\n').encode())
                else: w.write(b"Command successful (simulated).\r\n")
                await w.drain()
        except: pass
        finally:
            if ready: await loop.run_in_executor(None, sandbox.destroy)
            ACTIVE_SESSIONS.labels(protocol='ftp').dec()
            self.the_void.unregister_connection(ip); await self.the_void.finalize_session(ip)
            w.close(); await w.wait_closed()

    async def handle_http_connection(self, r, w):
        addr = w.get_extra_info('peername'); ip = addr[0]
        if ip in ["127.0.0.1", "::1"] or ip.startswith("127."): 
            ip = f"{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        headers = {}
        try:
            req_line = await r.readline()
            if not req_line: return
            line = req_line.decode('utf-8').strip()
            while True:
                h = await r.readline()
                if h == b'\r\n' or not h: break
                hp = h.decode('utf-8').split(': ', 1)
                if len(hp) == 2: headers[hp[0].lower()] = hp[1].strip()
            if not self.the_void.register_connection(ip): w.close(); await w.wait_closed(); return
            ACTIVE_SESSIONS.labels(protocol='http').inc()
            is_susp, resp, dk = await self.the_void.analyze_command(ip, line)
            await self.tarpit(ip, dk)
            body = resp if resp else "<html><body>Operational</body></html>"
            w.write(f"HTTP/1.1 200 OK\r\nContent-Length: {len(body)}\r\n\r\n{body}".encode()); await w.drain()
        except: pass
        finally:
            self.the_void.unregister_connection(ip); await self.the_void.finalize_session(ip)
            w.close(); await w.wait_closed(); ACTIVE_SESSIONS.labels(protocol='http').dec()

    async def start(self):
        s = await asyncio.start_server(self.handle_connection, self.host, self.port)
        hs = await asyncio.start_server(self.handle_http_connection, self.host, 8080)
        print(f"[HONEYPOT] FTP:2121 HTTP:8080 active")
        async with s, hs: await asyncio.gather(s.serve_forever(), hs.serve_forever())

async def main():
    start_http_server(8000); DockerSandbox.warmup()
    honeypot = RabbitHole(); gui = CommandCenter(honeypot.the_void) 
    honeypot.the_void.gui = gui 
    await gui.start(); threading.Thread(target=start_ssh_server, args=(honeypot.host, 2222, honeypot.the_void), daemon=True).start()
    await honeypot.start()

if __name__ == '__main__':
    print("Starting RabbitHole v3.1...")
    try: asyncio.run(main())
    except Exception as e:
        print(f"CRITICAL SYSTEM FAILURE: {e}")
        import traceback
        traceback.print_exc()