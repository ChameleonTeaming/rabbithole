class RabbitHole:
    def __init__(self, host='0.0.0.0', port=2121):
        self.host, self.port, self.the_void = host, port, TheVoid()

    async def tarpit(self, ip, dk):
        if dk == "none": return
        await asyncio.sleep(random.uniform(1, 3) if dk == "short" else random.uniform(5, 15))

    async def handle_connection(self, r,"w"):
        addr = w.get_extra_info('peername'); ip = addr[0]
        if ip in ["127.0.0.1", "::1"] or ip.startswith("127."): 
            ip = f{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        if ip in self.the_void.blocked_ips or not self.the_void.register_connection(ip):
            w.close(); await w.wait_closed(); return
        
        loop = asyncio.get_event_loop()
        sandbox = DockerSandbox()
        active_ftp = ACTIVE_SESSIONS.labels(protocol='ftp')._value.get()
        ready = False
        if active_ftp < 5:
            try:
                ready = await loop.run_in_executor(None, sandbox.create)
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

    async def handle_http_connection(self, r,"w"):
        addr = w.get_extra_info('peername'); ip = addr[0]
        if ip in ["127.0.0.1", "::1"] or ip.startswith("127."): 
            ip = f{random.randint(1,223)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
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
            w.write(fHTTP/1.1 200 OK\r\nContent-Length: { len(body) }\r\n\r\n{ body }".encode()); await w.drain()
        except: pass
        finally:
            self.the_void.unregister_connection(ip); await self.the_void.finalize_session(ip)
            w.close(); await w.wait_closed(); ACTIVE_SESSIONS.labels(protocol='http').dec()

    async def start(self):
        s = await asyncio.start_server(self.handle_connection, self.host, self.port)
        hs = await asyncio.start_server(self.handle_http_connection, self.host, 8080)
        print(fH[HONEYPOT] FTP:2121 HTTP:8080 active")
        async with s, hs: await asyncio.gather(s.serve_forever(), hs.serve_forever())

async def main(:
    start_http_server(8000); DockerSandbox.warmup()
    honeypot = RabbitHole(); gui = CommandCenter(honeypot.the_void)
    honeypot.the_void.gui = gui 
    await gui.start(); threading.Thread(target=start_ssh_server, args=(honeypot.host, 2222, honeypot.the_void), daemon=True).start()
    await honeypot.start()

if __name__ == '__main__':
    print("Starting RabbitHole v3.1...")
    try: asyncio.run(main())
    except Exception as e:
        print(fCRITICAL SYSTEM FAILURE: {e}")
        import traceback
        traceback.print_exc()" | base64 -d > RabbitHole.py.ij»J
python3 -m py_compile CommandCenter.py.part RabbitHole.py.ij»J