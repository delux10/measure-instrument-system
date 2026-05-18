"""审计日志工具"""
from app.models import AuditLog

def log(db, user_id: int, action: str, target_type: str, target_id: int = None,
        changes: dict = None, summary: str = None):
    entry = AuditLog(
        user_id=user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        changes=changes,
        summary=summary,
    )
    db.add(entry)
    db.flush()
    return entry
