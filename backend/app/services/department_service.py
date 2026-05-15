from app.services.base import BaseCRUDService
from app.models.department import Department


class DepartmentService(BaseCRUDService):
    def __init__(self):
        super().__init__(Department, "部门")

    def list_tree(self, db):
        """返回完整部门树"""
        all_depts = db.query(Department).all()

        def build_tree(parent_id):
            children = [d for d in all_depts if d.parent_id == parent_id]
            return [{"id": d.id, "name": d.name, "parent_id": d.parent_id,
                     "level": d.level, "manager_id": d.manager_id,
                     "measurer_id": d.measurer_id,
                     "children": build_tree(d.id)} for d in children]

        return build_tree(None)
