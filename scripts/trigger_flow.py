# scripts/trigger_flow.py
import asyncio
from prefect.client import get_client

async def main():
    async with get_client() as client:
        dep = await client.read_deployment_by_name("Kafka to Delta Pipeline/kafka-to-delta")
        flow_run = await client.create_flow_run_from_deployment(dep.id)
        print(f"Created flow run: {flow_run.id}")

if __name__ == "__main__":
    asyncio.run(main())
