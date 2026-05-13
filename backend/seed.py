"""初始化数据库种子数据"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.department import Department
from app.models.instrument import InstrumentCategory
from app.utils.auth import get_password_hash

def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        # 1. Create admin user
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                name="系统管理员",
                role="admin",
                is_active=True
            )
            db.add(admin)
            print("✅ 管理员账号已创建 (admin/admin123)")
        else:
            print("ℹ️ 管理员账号已存在")
        
        # 2. Create dept head account (大哥)
        boss = db.query(User).filter(User.username == "dage").first()
        if not boss:
            boss = User(
                username="dage",
                password_hash=get_password_hash("dage123"),
                name="胡炯",
                role="system_manager",
                is_active=True
            )
            db.add(boss)
            print("✅ 体系管理员账号已创建 (dage/dage123)")
        
        db.flush()
        
        # 3. Create departments
        root_dept = db.query(Department).filter(Department.name == "工艺质量管理科").first()
        if not root_dept:
            root_dept = Department(name="工艺质量管理科", level=1, manager_id=boss.id, measurer_id=boss.id)
            db.add(root_dept)
            db.flush()
            print(f"✅ 部门已创建: {root_dept.name}")
        
        # 4. Create default instrument categories
        categories = [
            ("长度类", 1),
            ("力学类", 1),
            ("电学类", 1),
            ("热学类", 1),
            ("理化类", 1),
        ]
        for cat_name, level in categories:
            existing = db.query(InstrumentCategory).filter(
                InstrumentCategory.name == cat_name,
                InstrumentCategory.level == level,
                InstrumentCategory.parent_id.is_(None)
            ).first()
            if not existing:
                cat = InstrumentCategory(name=cat_name, level=level)
                db.add(cat)
                print(f"✅ 仪器分类已创建: {cat_name}")
        
        db.commit()
        print("\n🎉 数据库初始化完成！")
        print("   管理员账号: admin / admin123")
        print("   体系管理员: dage / dage123")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 初始化失败: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
