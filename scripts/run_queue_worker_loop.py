import argparse
import asyncio
import json
from contextlib import suppress

from app.database import SessionLocal
from app.services.queue_worker_runtime import consume_queue_item_once, upsert_worker_heartbeat


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run queue worker loop (claim -> execute -> complete -> heartbeat).")
    parser.add_argument("--project-id", type=int, required=True, help="Project ID to consume.")
    parser.add_argument("--worker-id", type=str, required=True, help="Worker identifier.")
    parser.add_argument("--run-type", type=str, choices=["api", "web"], default=None, help="Optional run type filter.")
    parser.add_argument("--poll-interval", type=float, default=2.0, help="Polling interval when queue is empty.")
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=0,
        help="Max loop iterations; 0 means run forever.",
    )
    return parser.parse_args()


async def _run_loop(args: argparse.Namespace) -> None:
    iteration = 0
    worker_id = args.worker_id.strip()
    run_type = args.run_type.strip() if args.run_type else None
    try:
        while args.max_iterations <= 0 or iteration < args.max_iterations:
            iteration += 1
            with SessionLocal() as db:
                result = await consume_queue_item_once(
                    db=db,
                    project_id=args.project_id,
                    worker_id=worker_id,
                    run_type=run_type,
                )

            print(json.dumps({"iteration": iteration, **result}, ensure_ascii=False))
            if result.get("executed"):
                continue
            await asyncio.sleep(max(args.poll_interval, 0.1))
    finally:
        with suppress(Exception):
            with SessionLocal() as db:
                upsert_worker_heartbeat(
                    db=db,
                    project_id=args.project_id,
                    worker_id=worker_id,
                    run_type=run_type,
                    status="offline",
                    current_queue_item_id=None,
                )


def main() -> None:
    args = _parse_args()
    asyncio.run(_run_loop(args))


if __name__ == "__main__":
    main()
