
import asyncio
import aiohttp
import ssl
import os
import uuid

HUB_URL = "https://localhost:9443"
AUTH_TOKEN = "6d3574ff21cc17ab6b00405020f2a277"

async def register_node(session, node_id):
    headers = {"Authorization": f"Bearer {AUTH_TOKEN}"}
    params = {"node_id": node_id}
    try:
        # Custom SSL context for self-signed certs
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        
        async with session.get(f"{HUB_URL}/api/blocklist", headers=headers, params=params, ssl=ssl_ctx) as resp:
            if resp.status == 200:
                print(f"Registered node: {node_id}")
            else:
                print(f"Failed to register node {node_id}: {resp.status}")
    except Exception as e:
        print(f"Error registering node {node_id}: {e}")

async def main():
    print("Simulating 19 additional nodes joining the mesh...")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(1, 20):
            node_id = f"RH-NODE-SIM-{uuid.uuid4().hex[:8].upper()}"
            tasks.append(register_node(session, node_id))
        await asyncio.gather(*tasks)
    print("Mesh simulation complete.")

if __name__ == "__main__":
    asyncio.run(main())
