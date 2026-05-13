from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.workflow import Workflow, WorkflowNode
from app.models.user import User
from app.schemas import (
    WorkflowCreate, WorkflowUpdate, WorkflowResponse,
    WorkflowNodeCreate, WorkflowNodeUpdate, WorkflowNodeResponse
)
from app.utils.auth import get_current_user, require_role

router = APIRouter()

# === Workflow CRUD ===

@router.get("/", response_model=List[WorkflowResponse])
def list_workflows(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    initiator_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Workflow)
    if type:
        query = query.filter(Workflow.type == type)
    if status:
        query = query.filter(Workflow.status == status)
    if initiator_id:
        query = query.filter(Workflow.initiator_id == initiator_id)
    return query.all()

@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="审批流不存在")
    return wf

@router.post("/", response_model=WorkflowResponse)
def create_workflow(
    wf: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_wf = Workflow(**wf.model_dump())
    db.add(db_wf)
    db.commit()
    db.refresh(db_wf)
    return db_wf

@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    wf: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not db_wf:
        raise HTTPException(status_code=404, detail="审批流不存在")
    for key, value in wf.model_dump(exclude_unset=True).items():
        setattr(db_wf, key, value)
    db.commit()
    db.refresh(db_wf)
    return db_wf

@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="审批流不存在")
    db.query(WorkflowNode).filter(WorkflowNode.workflow_id == workflow_id).delete()
    db.delete(wf)
    db.commit()
    return {"message": "删除成功"}

# === Workflow Node CRUD ===

@router.get("/{workflow_id}/nodes", response_model=List[WorkflowNodeResponse])
def list_nodes(workflow_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WorkflowNode).filter(
        WorkflowNode.workflow_id == workflow_id
    ).order_by(WorkflowNode.step_order).all()

@router.post("/{workflow_id}/nodes", response_model=WorkflowNodeResponse)
def create_node(
    workflow_id: int,
    node: WorkflowNodeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "system_manager"]))
):
    db_node = WorkflowNode(workflow_id=workflow_id, **node.model_dump(exclude={"workflow_id"}))
    db.add(db_node)
    db.commit()
    db.refresh(db_node)
    return db_node

@router.put("/{workflow_id}/nodes/{node_id}", response_model=WorkflowNodeResponse)
def update_node(
    workflow_id: int,
    node_id: int,
    node: WorkflowNodeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from datetime import date
    db_node = db.query(WorkflowNode).filter(
        WorkflowNode.id == node_id,
        WorkflowNode.workflow_id == workflow_id
    ).first()
    if not db_node:
        raise HTTPException(status_code=404, detail="审批节点不存在")
    for key, value in node.model_dump(exclude_unset=True).items():
        setattr(db_node, key, value)
    if node.status in ("approved", "rejected"):
        db_node.operated_at = date.today()
    db.commit()
    db.refresh(db_node)
    return db_node
