import asyncio
import time

async def simulate_attacker(id):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2121)
        # Read banner
        await reader.read(1024)
        
        # Send some commands
        commands = [b"USER root\r\n", b"PASS 123456\r\n", b"PWD\r\n", b"QUIT\r\n"]
        for cmd in commands:
            writer.write(cmd)
            await writer.drain()
            await reader.read(1024)
            await asyncio.sleep(0.1)
            
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False

async def main():
    print("Spawning 50 concurrent attackers...")
    start_time = time.time()
    tasks = [simulate_attacker(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    success_count = sum(1 for r in results if r)
    print(f"Test Finished. Successful connections: {success_count}/50")
    print(f"Total time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())

