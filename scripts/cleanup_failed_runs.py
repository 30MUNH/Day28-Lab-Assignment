# scripts/cleanup_failed_runs.py
import asyncio
from prefect.client import get_client

async def main():
    async with get_client() as client:
        runs = await client.read_flow_runs()
        deleted_count = 0
        for r in runs:
            if r.state_type.name == "FAILED" or r.state_type == "FAILED":
                try:
                    await client.delete_flow_run(r.id)
                    print(f"Deleted failed flow run: {r.name} ({r.id})")
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {r.name}: {e}")
        print(f"Cleanup complete. Deleted {deleted_count} failed runs.")

if __name__ == "__main__":
    asyncio.run(main())
