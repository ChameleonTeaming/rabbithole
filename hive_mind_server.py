import logging
import json
import os
import collections
import ssl
import datetime
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [HIVEMIND] %(message)s')
logger = logging.getLogger("HiveMindHub")

# Simulated Database
INCIDENTS_DB = collections.deque(maxlen=100)
NODES = {} # Track active nodes {ip: last_seen}
GLOBAL_BLOCKLIST = set(["103.20.15.1", "45.33.22.11"]) # Example bad IPs
import hmac

SECRET_TOKEN = os.getenv('HIVE_MIND_TOKEN', '6d3574ff21cc17ab6b00405020f2a277')
if SECRET_TOKEN == '6d3574ff21cc17ab6b00405020f2a277':
    logger.warning("Using default HIVE_MIND_TOKEN. Change this for production!")

# Rate Limiting
RATE_LIMITS = collections.defaultdict(list) # ip -> [timestamps]

async def handle_incident(request):
    ip = request.remote
    now = datetime.datetime.now()
    
    # Simple Rate Limit: 10 reports per minute per node
    if ip not in ['127.0.0.1', '::1']:
        RATE_LIMITS[ip] = [t for t in RATE_LIMITS[ip] if (now - t).total_seconds() < 60]
        if len(RATE_LIMITS[ip]) >= 10:
            logger.warning(f"Rate limit exceeded for node {ip}")
            return web.Response(status=429, text="Too Many Requests")
        RATE_LIMITS[ip].append(now)

    try:
        # Verify Auth Token using constant-time comparison
        auth = request.headers.get("Authorization")
        if not auth or not hmac.compare_digest(auth, f"Bearer {SECRET_TOKEN}"):
            logger.warning(f"Unauthorized incident report attempt from {request.remote}")
            return web.Response(status=401, text="Unauthorized")

        data = await request.json()
        node_id = data.get('node_id', 'unknown_node')
        logger.info(f"Received new incident report from {data.get('ip', 'unknown')} via {node_id}")
        
        # Track the node with identity
        NODES[node_id] = {
            "last_seen": datetime.datetime.now().isoformat(),
            "last_ip": request.remote,
            "status": "ACTIVE"
        }
        
        # "Process" the intelligence
        INCIDENTS_DB.append(data)
        
        # Add attacker to global blocklist
        if 'ip' in data:
            GLOBAL_BLOCKLIST.add(data['ip'])
            
        return web.Response(status=201, text="Incident Received")
    except Exception as e:
        logger.error(f"Error processing incident: {e}")
        return web.Response(status=500)

async def handle_blocklist(request):
    # Verify Auth Token using constant-time comparison
    auth = request.headers.get("Authorization")
    if not auth or not hmac.compare_digest(auth, f"Bearer {SECRET_TOKEN}"):
        logger.warning(f"Unauthorized blocklist sync attempt from {request.remote}")
        return web.Response(status=401, text="Unauthorized")

    # Track the node
    node_id = request.query.get('node_id', request.remote)
    NODES[node_id] = {
        "last_seen": datetime.datetime.now().isoformat(),
        "last_ip": request.remote,
        "status": "ACTIVE"
    }

    logger.info(f"Syncing blocklist with sensor {node_id}...")
    return web.json_response(list(GLOBAL_BLOCKLIST))

async def handle_hub_status(request):
    # Public or semi-public status API
    return web.json_response({
        "status": "OPERATIONAL",
        "node_count": len(NODES),
        "nodes": NODES,
        "recent_incidents_count": len(INCIDENTS_DB),
        "blocklist_size": len(GLOBAL_BLOCKLIST)
    })

async def handle_root(request):
    return web.Response(text="Hive Mind Hub: Secure Intelligence Mesh Online")

async def init_app():
    app = web.Application()
    app.add_routes([
        web.get('/', handle_root),
        web.post('/api/incident', handle_incident),
        web.get('/api/blocklist', handle_blocklist),
        web.get('/api/status', handle_hub_status)
    ])
    return app

if __name__ == '__main__':
    print("Initializing Secure Hive Mind Global Intelligence Hub (HTTPS)...")
    try:
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain('cert.pem', 'key.pem')
        web.run_app(init_app(), port=9443, ssl_context=ssl_context)
    except Exception as e:
        print(f"CRITICAL FAILURE: Failed to start Secure Hub: {e}")
        exit(1)