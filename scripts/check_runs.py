# scripts/check_runs.py
import asyncio
from prefect.client import get_client

async def main():
    async with get_client() as client:
        runs = await client.read_flow_runs(limit=100)
        non_scheduled = [r for r in runs if r.state_type != "SCHEDULED"]
        for r in non_scheduled[:15]:
            msg = r.state.message if r.state else ""
            stype = r.state_type if r.state_type else ""
            print(f"Run: {r.name} | State: {stype} | Message: {msg}")

if __name__ == "__main__":
    asyncio.run(main())
