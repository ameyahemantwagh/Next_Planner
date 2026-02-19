from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime

from .database import get_db
from .auth import get_current_user
from . import models
from .planner_events import append_event

router = APIRouter(prefix="/api/planner", tags=["planner"])


class CreatePlanRequest(BaseModel):
    name: str
    container_type: str
    container_id: str
    visibility: Optional[str] = "private"


class CreateBucketRequest(BaseModel):
    title: str


class CreateTaskRequest(BaseModel):
    title: str
    bucket_id: Optional[str]
    description: Optional[str] = None


@router.post("/plans", status_code=status.HTTP_201_CREATED)
def create_plan(payload: CreatePlanRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = models.Plan(name=payload.name, container_type=payload.container_type, container_id=payload.container_id, visibility=payload.visibility, owner_id=current_user.id)
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Add creator as member
    m = models.Membership(plan_id=plan.id, user_id=current_user.id, role="owner")
    db.add(m)
    db.commit()

    append_event(db, "plan", plan.id, "plan.created", {"name": plan.name}, created_by=current_user.id)
    return {"id": plan.id, "name": plan.name}


@router.get("/plans/{plan_id}/snapshot")
def plan_snapshot(plan_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Authorization: ensure membership
    mem = db.query(models.Membership).filter(models.Membership.plan_id == plan_id, models.Membership.user_id == current_user.id).first()
    if not mem and plan.visibility != "public":
        raise HTTPException(status_code=403, detail="Not a member of this plan")

    buckets = db.query(models.Bucket).filter(models.Bucket.plan_id == plan_id).order_by(models.Bucket.created_at).all()
    tasks = db.query(models.Task).filter(models.Task.plan_id == plan_id).all()

    return {
        "plan": {"id": plan.id, "name": plan.name, "visibility": plan.visibility, "version": plan.version},
        "buckets": [{"id": b.id, "title": b.title, "order_hint": b.order_hint} for b in buckets],
        "tasks": [{"id": t.id, "title": t.title, "bucket_id": t.bucket_id, "order_hint": t.order_hint, "percent_complete": t.percent_complete} for t in tasks],
    }


@router.post("/plans/{plan_id}/buckets", status_code=status.HTTP_201_CREATED)
def create_bucket(plan_id: str, payload: CreateBucketRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Authorization: only members can create buckets
    mem = db.query(models.Membership).filter(models.Membership.plan_id == plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member of this plan")

    # crude order_hint using epoch ms
    order_hint = str(int(datetime.utcnow().timestamp() * 1000))
    bucket = models.Bucket(plan_id=plan_id, title=payload.title, order_hint=order_hint)
    db.add(bucket)
    db.commit()
    db.refresh(bucket)

    append_event(db, "bucket", bucket.id, "bucket.created", {"title": bucket.title}, created_by=current_user.id)
    return {"id": bucket.id, "title": bucket.title, "order_hint": bucket.order_hint}


@router.patch("/buckets/{bucket_id}")
def patch_bucket(bucket_id: str, payload: CreateBucketRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bucket = db.query(models.Bucket).filter(models.Bucket.id == bucket_id).first()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    # membership check
    mem = db.query(models.Membership).filter(models.Membership.plan_id == bucket.plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member")
    bucket.title = payload.title
    db.commit()
    append_event(db, "bucket", bucket.id, "bucket.updated", {"title": bucket.title}, created_by=current_user.id)
    return {"id": bucket.id, "title": bucket.title}


@router.delete("/buckets/{bucket_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bucket(bucket_id: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    bucket = db.query(models.Bucket).filter(models.Bucket.id == bucket_id).first()
    if not bucket:
        raise HTTPException(status_code=404, detail="Bucket not found")
    mem = db.query(models.Membership).filter(models.Membership.plan_id == bucket.plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member")
    db.delete(bucket)
    db.commit()
    append_event(db, "bucket", bucket.id, "bucket.deleted", {}, created_by=current_user.id)
    return None


@router.post("/plans/{plan_id}/tasks", status_code=status.HTTP_201_CREATED)
def create_task(plan_id: str, payload: CreateTaskRequest, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    mem = db.query(models.Membership).filter(models.Membership.plan_id == plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member")

    order_hint = str(int(datetime.utcnow().timestamp() * 1000))
    task = models.Task(plan_id=plan_id, bucket_id=payload.bucket_id, title=payload.title, description=payload.description, order_hint=order_hint, created_by=current_user.id)
    db.add(task)
    db.commit()
    db.refresh(task)

    append_event(db, "task", task.id, "task.created", {"title": task.title, "bucket_id": task.bucket_id}, created_by=current_user.id)
    return {"id": task.id, "title": task.title, "bucket_id": task.bucket_id, "order_hint": task.order_hint}


@router.patch("/tasks/{task_id}")
def patch_task(task_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    mem = db.query(models.Membership).filter(models.Membership.plan_id == task.plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member")
    # Apply allowed updates
    allowed = ["title", "description", "percent_complete", "labels", "assignments"]
    changed = {}
    for k in allowed:
        if k in payload:
            setattr(task, k, payload[k])
            changed[k] = payload[k]
    task.version = (task.version or 0) + 1
    db.commit()
    append_event(db, "task", task.id, "task.updated", changed, created_by=current_user.id)
    return {"id": task.id, "version": task.version}


@router.patch("/tasks/{task_id}/move")
def move_task(task_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    mem = db.query(models.Membership).filter(models.Membership.plan_id == task.plan_id, models.Membership.user_id == current_user.id).first()
    if not mem:
        raise HTTPException(status_code=403, detail="Not a member")

    target_bucket = payload.get("target_bucket_id")
    before = payload.get("before_task_id")
    after = payload.get("after_task_id")

    # For now, simple behaviour: set bucket and assign epoch-based order_hint
    if target_bucket:
        task.bucket_id = target_bucket
    task.order_hint = str(int(datetime.utcnow().timestamp() * 1000))
    task.version = (task.version or 0) + 1
    db.commit()
    append_event(db, "task", task.id, "task.moved", {"target_bucket_id": task.bucket_id, "order_hint": task.order_hint, "before": before, "after": after}, created_by=current_user.id)
    return {"id": task.id, "bucket_id": task.bucket_id, "order_hint": task.order_hint}


@router.post("/tasks/{task_id}/comments", status_code=status.HTTP_201_CREATED)
def add_comment(task_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    comment = models.Comment(task_id=task_id, user_id=current_user.id, body=payload.get("body", ""))
    db.add(comment)
    db.commit()
    db.refresh(comment)
    append_event(db, "task", task_id, "comment.created", {"comment_id": comment.id, "body": comment.body}, created_by=current_user.id)
    return {"id": comment.id, "body": comment.body}


@router.post("/plans/{plan_id}/members", status_code=status.HTTP_201_CREATED)
def add_member(plan_id: str, payload: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    plan = db.query(models.Plan).filter(models.Plan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    # Only owner may add members (simple rule)
    owner_mem = db.query(models.Membership).filter(models.Membership.plan_id == plan_id, models.Membership.user_id == current_user.id, models.Membership.role == "owner").first()
    if not owner_mem:
        raise HTTPException(status_code=403, detail="Only owners can add members")
    user_id = payload.get("user_id")
    role = payload.get("role", "member")
    m = models.Membership(plan_id=plan_id, user_id=user_id, role=role)
    db.add(m)
    db.commit()
    append_event(db, "plan", plan_id, "membership.added", {"user_id": user_id, "role": role}, created_by=current_user.id)
    return {"id": m.id, "user_id": user_id, "role": role}
