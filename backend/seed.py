"""初始化种子数据 v2"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app.models import User, Department, InstrumentCategory
from app.config import settings
from app.utils.auth import hash_password

db = SessionLocal()
try:
    if not db.query(User).filter(User.username == "admin").first():
        db.add(User(username="admin", password_hash=hash_password(settings.ADMIN_PASSWORD or "admin123"),
                     name="系统管理员", role="admin", is_active=True))
        print("admin created")
    if not db.query(User).filter(User.username == "dage").first():
        db.add(User(username="dage", password_hash=hash_password(settings.SYSTEM_MANAGER_PASSWORD or "dage123"),
                     name="胡炯", role="system_manager", is_active=True))
        print("dage created")
    db.flush()
    dage = db.query(User).filter(User.username == "dage").first()
    if not db.query(Department).filter(Department.name == "工艺质量管理科").first():
        db.add(Department(name="工艺质量管理科", level=1, manager_id=dage.id if dage else None,
                          measurer_id=dage.id if dage else None))
        print("department created")
    db.flush()
    qc_dept = db.query(Department).filter(Department.name == "工艺质量管理科").first()
    # Assign dage to QC department
    if dage and not dage.department_id:
        dage.department_id = qc_dept.id
    for cat_name in ["长度类", "力学类", "电学类", "热学类", "理化类"]:
        if not db.query(InstrumentCategory).filter(InstrumentCategory.name == cat_name, InstrumentCategory.parent_id.is_(None)).first():
            db.add(InstrumentCategory(name=cat_name, level=1))
    db.commit()
    print("Seed completed.")
except Exception as e:
    db.rollback()
    print(f"Seed error: {e}")
finally:
    db.close()
