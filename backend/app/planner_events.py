import json
import os
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

try:
    import redis
except Exception:
    redis = None

from .models import Event


REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")


class EventPublisher:
    def __init__(self):
        self._client = None
        if redis is not None:
            try:
                self._client = redis.from_url(REDIS_URL)
            except Exception:
                self._client = None

    def publish(self, channel: str, message: Dict[str, Any]) -> None:
        if not self._client:
            return
        try:
            payload = json.dumps(message, default=str)
            self._client.publish(channel, payload)
        except Exception:
            # Best-effort - do not raise on publish failure
            return


publisher = EventPublisher()


def append_event(db: Session, aggregate_type: str, aggregate_id: str, event_type: str, payload: Dict[str, Any], created_by: Optional[str] = None) -> Event:
    """Append an event to the events table and publish to Redis.

    Returns the persisted Event instance.
    """
    # Determine next aggregate_version by counting existing events for this aggregate
    # Note: for high-throughput systems consider a different approach (locks or sequence)
    last_version = 0
    try:
        last = db.query(Event).filter(Event.aggregate_type == aggregate_type, Event.aggregate_id == aggregate_id).order_by(Event.aggregate_version.desc()).first()
        if last:
            last_version = last.aggregate_version
    except Exception:
        last_version = 0

    ev = Event(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        event_type=event_type,
        payload=payload,
        created_by=created_by,
        aggregate_version=last_version + 1,
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)

    # publish to redis channel for subscribers
    try:
        channel = f"{aggregate_type}:{aggregate_id}"
        publisher.publish(channel, {
            "event_id": ev.id,
            "aggregate_type": ev.aggregate_type,
            "aggregate_id": ev.aggregate_id,
            "event_type": ev.event_type,
            "payload": ev.payload,
            "created_by": ev.created_by,
            "created_at": ev.created_at.isoformat(),
            "aggregate_version": ev.aggregate_version,
        })
    except Exception:
        # swallow publish errors
        pass

    return ev
