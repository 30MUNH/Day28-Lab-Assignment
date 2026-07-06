# scripts/check_run_details.py
import asyncio
from prefect.client import get_client

async def main():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=15)
        for r in runs:
            print(f"Run: {r.name:25} | State: {r.state_type:10} | Created: {r.created} | Start: {r.start_time}")

if __name__ == "__main__":
    asyncio.run(main())
