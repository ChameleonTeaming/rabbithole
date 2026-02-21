import asyncio
import time
import random

async def simulate_bot(bot_id):
    try:
        # Randomize protocol
        port = 2121
        reader, writer = await asyncio.open_connection('127.0.0.1', port)
        await reader.read(1024)
        
        # Varied bot behaviors
        behavior = random.choice(["brute", "recon", "malware"])
        
        if behavior == "brute":
            cmds = [b"USER admin\r\n", b"PASS password\r\n", b"USER root\r\n", b"PASS 123456\r\n"]
        elif behavior == "recon":
            cmds = [b"USER guest\r\n", b"SYST\r\n", b"PWD\r\n", b"LIST\r\n"]
        else:
            cmds = [b"USER root\r\n", b"PASS root\r\n", b"CWD /tmp\r\n", b"STOR exploit.sh\r\n"]
            
        for cmd in cmds:
            writer.write(cmd)
            await writer.drain()
            await reader.read(1024)
            await asyncio.sleep(random.uniform(0.01, 0.05))
            
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def main():
    while True:
        total_bots = 250
        batch_size = 25
        print(f"Starting Botnet Surge: {total_bots} bots in batches of {batch_size}...")
        
        start_time = time.time()
        success = 0
        
        for i in range(0, total_bots, batch_size):
            tasks = [simulate_bot(j) for j in range(i, i + batch_size)]
            results = await asyncio.gather(*tasks)
            success += sum(1 for r in results if r)
            print(f"  Batch {i//batch_size + 1} complete. Total successes: {success}")
            
        end_time = time.time()
        print(f"\nSURGE COMPLETE.")
        print(f"Success Rate: {success}/{total_bots}")
        print(f"Duration: {end_time - start_time:.2f}s")
        print(f"Throughput: {total_bots/(end_time - start_time):.2f} bots/sec")
        print("Cooling down for 5 seconds before next wave...")
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
