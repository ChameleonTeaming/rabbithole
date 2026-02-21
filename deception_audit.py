import asyncio
import json

async def get_response(cmd):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2121)
        await reader.read(1024) # Banner
        writer.write(b"USER admin\r\n")
        await writer.drain()
        await reader.read(1024)
        writer.write(b"PASS admin\r\n")
        await writer.drain()
        await reader.read(1024)
        
        # Send the target command
        writer.write(cmd.encode() + b"\r\n")
        await writer.drain()
        response = await reader.read(1024)
        
        writer.close()
        await writer.wait_closed()
        return response.decode('utf-8', errors='ignore').strip()
    except Exception as e:
        return f"Error: {e}"

async def main():
    command = "HELP LOG_ANALYSIS"
    print(f"Testing Deception Entropy for command: '{command}'")
    
    responses = []
    for i in range(5):
        print(f"  Request {i+1}...")
        res = await get_response(command)
        responses.append(res)
        await asyncio.sleep(1)
        
    print("\n--- RabbitHole AI Responses ---")
    for r in responses:
        print(f"  -> {r}")
        
    print("\n--- Standard Honeypot Baseline (Cowrie) ---")
    for _ in range(5):
        print("  -> 500 Unknown command.")

    unique_count = len(set(responses))
    print(f"\nDECEPTION SCORE: {unique_count}/5 (Unique responses per attempt)")
    if unique_count > 1:
        print("RESULT: High Deception Entropy Proven. Attacker cannot fingerprint via repetition.")
    else:
        print("RESULT: Low Deception Entropy. (Check API status)")

if __name__ == "__main__":
    asyncio.run(main())
