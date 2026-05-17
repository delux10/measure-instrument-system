"""initial

Revision ID: 05d39e86f1a6
Revises:
Create Date: 2026-05-17 11:17:33.761125

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05d39e86f1a6'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Phase 1: Create all tables without foreign key constraints ===

    op.create_table('calibration_agencies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('qualification', sa.String(length=500), nullable=True),
    sa.Column('contact', sa.String(length=100), nullable=True),
    sa.Column('phone', sa.String(length=50), nullable=True),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('service_range', sa.String(length=500), nullable=True),
    sa.Column('cooperation_end', sa.Date(), nullable=True),
    sa.Column('remark', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calibration_agencies_id', 'calibration_agencies', ['id'])

    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('manager_id', sa.Integer(), nullable=True),
    sa.Column('measurer_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_departments_id', 'departments', ['id'])

    op.create_table('instrument_categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('level', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_instrument_categories_id', 'instrument_categories', ['id'])

    op.create_table('supervision_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('category', sa.Enum('DEPARTMENT', 'CENTRAL', name='supervisiontype'), nullable=True),
    sa.Column('department_type', sa.String(length=100), nullable=True),
    sa.Column('version', sa.String(length=20), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supervision_templates_id', 'supervision_templates', ['id'])

    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('password_hash', sa.String(length=200), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('role', sa.String(length=20), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_id', 'users', ['id'])

    op.create_table('calibration_contracts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_no', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.Column('agency_id', sa.Integer(), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('contract_date', sa.Date(), nullable=True),
    sa.Column('start_date', sa.Date(), nullable=True),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('total_amount', sa.Float(), nullable=True),
    sa.Column('payment_terms', sa.String(length=500), nullable=True),
    sa.Column('invoice_title', sa.String(length=200), nullable=True),
    sa.Column('tax_id', sa.String(length=50), nullable=True),
    sa.Column('invoice_type', sa.String(length=20), nullable=True),
    sa.Column('tax_rate', sa.Float(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'EXECUTING', 'COMPLETED', 'ARCHIVED', name='contractstatus'), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('contract_no')
    )
    op.create_index('ix_calibration_contracts_id', 'calibration_contracts', ['id'])

    op.create_table('instruments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('code', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('model', sa.String(length=200), nullable=True),
    sa.Column('serial_no', sa.String(length=200), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.Column('range_value', sa.String(length=100), nullable=True),
    sa.Column('accuracy', sa.String(length=100), nullable=True),
    sa.Column('scale_interval', sa.String(length=50), nullable=True),
    sa.Column('manufacture_date', sa.Date(), nullable=True),
    sa.Column('manufacturer', sa.String(length=200), nullable=True),
    sa.Column('purchase_date', sa.Date(), nullable=True),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('keeper', sa.String(length=50), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('cal_agency', sa.String(length=200), nullable=True),
    sa.Column('certificate_no', sa.String(length=100), nullable=True),
    sa.Column('cert_confirmed', sa.String(length=50), nullable=True),
    sa.Column('metrology_characteristic', sa.String(length=200), nullable=True),
    sa.Column('status', sa.Enum('IN_USE', 'IDLE', 'REPAIR', 'SCRAPPED', 'CALIBRATING', 'STOPPED', name='instrumentstatus'), nullable=True),
    sa.Column('photo', sa.String(length=500), nullable=True),
    sa.Column('calibration_cycle', sa.Integer(), nullable=True),
    sa.Column('last_cal_date', sa.Date(), nullable=True),
    sa.Column('next_cal_date', sa.Date(), nullable=True),
    sa.Column('cal_method', sa.String(length=50), nullable=True),
    sa.Column('last_cal_cost', sa.Float(), nullable=True),
    sa.Column('remark', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    op.create_index('ix_instruments_id', 'instruments', ['id'])

    op.create_table('supervision_plans',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('DEPARTMENT', 'CENTRAL', name='supervisiontype', create_type=False), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('plan_date', sa.Date(), nullable=True),
    sa.Column('executor_id', sa.Integer(), nullable=True),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('DRAFT', 'IN_PROGRESS', 'COMPLETED', name='planstatus'), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supervision_plans_id', 'supervision_plans', ['id'])

    op.create_table('supervision_template_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('template_id', sa.Integer(), nullable=False),
    sa.Column('item_name', sa.String(length=500), nullable=False),
    sa.Column('standard', sa.Text(), nullable=True),
    sa.Column('score_standard', sa.String(length=100), nullable=True),
    sa.Column('sort_order', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supervision_template_items_id', 'supervision_template_items', ['id'])

    op.create_table('workflows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('PURCHASE', 'SCRAP', 'TRANSFER', name='workflowtype'), nullable=False),
    sa.Column('status', sa.Enum('DRAFT', 'PENDING', 'APPROVED', 'REJECTED', name='workflowstatus'), nullable=True),
    sa.Column('initiator_id', sa.Integer(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('form_data', sa.Text(), nullable=True),
    sa.Column('electronic_sign', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflows_id', 'workflows', ['id'])

    op.create_table('borrow_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('from_department', sa.Integer(), nullable=True),
    sa.Column('to_department', sa.Integer(), nullable=True),
    sa.Column('borrower', sa.String(length=50), nullable=True),
    sa.Column('expected_return_date', sa.Date(), nullable=True),
    sa.Column('actual_return_date', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('BORROWED', 'RETURNED', name='borrowstatus'), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_borrow_records_id', 'borrow_records', ['id'])

    op.create_table('contract_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_id', sa.Integer(), nullable=False),
    sa.Column('instrument_name', sa.String(length=200), nullable=False),
    sa.Column('specification', sa.String(length=200), nullable=True),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('unit_price', sa.Float(), nullable=True),
    sa.Column('amount', sa.Float(), nullable=True),
    sa.Column('remark', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contract_items_id', 'contract_items', ['id'])

    op.create_table('contract_versions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_id', sa.Integer(), nullable=False),
    sa.Column('version_no', sa.String(length=20), nullable=False),
    sa.Column('version_label', sa.String(length=200), nullable=True),
    sa.Column('file_path', sa.String(length=500), nullable=True),
    sa.Column('file_size', sa.Integer(), nullable=True),
    sa.Column('file_hash', sa.String(length=100), nullable=True),
    sa.Column('uploader_id', sa.Integer(), nullable=True),
    sa.Column('is_current', sa.Integer(), nullable=True),
    sa.Column('remark', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_contract_versions_id', 'contract_versions', ['id'])

    op.create_table('repair_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('fault_description', sa.Text(), nullable=True),
    sa.Column('repair_content', sa.Text(), nullable=True),
    sa.Column('cost', sa.Float(), nullable=True),
    sa.Column('repair_party', sa.String(length=200), nullable=True),
    sa.Column('repair_date', sa.Date(), nullable=True),
    sa.Column('operator', sa.String(length=50), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_repair_records_id', 'repair_records', ['id'])

    op.create_table('supervision_executions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=True),
    sa.Column('template_id', sa.Integer(), nullable=True),
    sa.Column('executor_id', sa.Integer(), nullable=True),
    sa.Column('target_department_id', sa.Integer(), nullable=True),
    sa.Column('execution_date', sa.Date(), nullable=True),
    sa.Column('status', sa.Enum('IN_PROGRESS', 'COMPLETED', 'APPROVED', 'REJECTED', name='execstatus'), nullable=True),
    sa.Column('overall_result', sa.String(length=20), nullable=True),
    sa.Column('reviewer_id', sa.Integer(), nullable=True),
    sa.Column('review_opinion', sa.Text(), nullable=True),
    sa.Column('review_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supervision_executions_id', 'supervision_executions', ['id'])

    op.create_table('workflow_nodes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('workflow_id', sa.Integer(), nullable=False),
    sa.Column('step_order', sa.Integer(), nullable=True),
    sa.Column('approver_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='nodestatus'), nullable=True),
    sa.Column('opinion', sa.Text(), nullable=True),
    sa.Column('sign_image', sa.String(length=500), nullable=True),
    sa.Column('operated_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_workflow_nodes_id', 'workflow_nodes', ['id'])

    op.create_table('calibration_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('instrument_id', sa.Integer(), nullable=False),
    sa.Column('plan_date', sa.Date(), nullable=True),
    sa.Column('actual_date', sa.Date(), nullable=True),
    sa.Column('agency_id', sa.Integer(), nullable=True),
    sa.Column('result', sa.Enum('PASS', 'FAIL', 'ADJUST', name='calresult'), nullable=True),
    sa.Column('certificate_no', sa.String(length=100), nullable=True),
    sa.Column('cost', sa.Float(), nullable=True),
    sa.Column('contract_id', sa.Integer(), nullable=True),
    sa.Column('contract_item_id', sa.Integer(), nullable=True),
    sa.Column('operator', sa.String(length=50), nullable=True),
    sa.Column('remark', sa.String(length=500), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calibration_records_id', 'calibration_records', ['id'])

    op.create_table('execution_records',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_item_id', sa.Integer(), nullable=True),
    sa.Column('instrument_id', sa.Integer(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('agency_id', sa.Integer(), nullable=True),
    sa.Column('actual_date', sa.Date(), nullable=True),
    sa.Column('actual_quantity', sa.Integer(), nullable=True),
    sa.Column('actual_unit_price', sa.Float(), nullable=True),
    sa.Column('actual_amount', sa.Float(), nullable=True),
    sa.Column('result', sa.String(length=20), nullable=True),
    sa.Column('certificate_no', sa.String(length=100), nullable=True),
    sa.Column('invoice_no', sa.String(length=100), nullable=True),
    sa.Column('invoice_date', sa.Date(), nullable=True),
    sa.Column('payment_status', sa.Enum('UNPAID', 'PARTIAL', 'PAID', name='paymentstatus'), nullable=True),
    sa.Column('payment_amount', sa.Float(), nullable=True),
    sa.Column('payment_date', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_execution_records_id', 'execution_records', ['id'])

    op.create_table('supervision_check_items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('execution_id', sa.Integer(), nullable=False),
    sa.Column('template_item_id', sa.Integer(), nullable=True),
    sa.Column('result', sa.Enum('PASS', 'FAIL', 'NA', name='checkresult'), nullable=True),
    sa.Column('opinion', sa.Text(), nullable=True),
    sa.Column('evidence_path', sa.String(length=500), nullable=True),
    sa.Column('inspector_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_supervision_check_items_id', 'supervision_check_items', ['id'])

    op.create_table('certificates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('calibration_record_id', sa.Integer(), nullable=False),
    sa.Column('file_path', sa.String(length=500), nullable=False),
    sa.Column('file_type', sa.String(length=20), nullable=True),
    sa.Column('valid_from', sa.Date(), nullable=True),
    sa.Column('valid_until', sa.Date(), nullable=True),
    sa.Column('uploader', sa.String(length=50), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_certificates_id', 'certificates', ['id'])

    op.create_table('non_conformities',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('supervision_execution_id', sa.Integer(), nullable=True),
    sa.Column('check_item_id', sa.Integer(), nullable=True),
    sa.Column('ncr_no', sa.String(length=50), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('severity', sa.Enum('GENERAL', 'SERIOUS', name='severity'), nullable=True),
    sa.Column('status', sa.Enum('ISSUED', 'RECEIVED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'CLOSED', name='ncrstatus'), nullable=True),
    sa.Column('issued_by', sa.Integer(), nullable=True),
    sa.Column('issued_date', sa.Date(), nullable=True),
    sa.Column('corrective_action', sa.Text(), nullable=True),
    sa.Column('corrective_evidence', sa.String(length=500), nullable=True),
    sa.Column('responsible_person', sa.Integer(), nullable=True),
    sa.Column('deadline', sa.Date(), nullable=True),
    sa.Column('verified_by', sa.Integer(), nullable=True),
    sa.Column('verified_date', sa.Date(), nullable=True),
    sa.Column('verification_result', sa.String(length=200), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ncr_no')
    )
    op.create_index('ix_non_conformities_id', 'non_conformities', ['id'])

    op.create_table('reconciliation_diffs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('contract_id', sa.Integer(), nullable=False),
    sa.Column('execution_record_id', sa.Integer(), nullable=True),
    sa.Column('diff_type', sa.Enum('NAME', 'QUANTITY', 'PRICE', 'AMOUNT', 'AGENCY', 'DEPARTMENT', name='difftype'), nullable=False),
    sa.Column('contract_value', sa.String(length=200), nullable=True),
    sa.Column('actual_value', sa.String(length=200), nullable=True),
    sa.Column('diff_value', sa.String(length=200), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'ADJUSTED', name='diffstatus'), nullable=True),
    sa.Column('remark', sa.Text(), nullable=True),
    sa.Column('confirmed_by', sa.Integer(), nullable=True),
    sa.Column('confirmed_at', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reconciliation_diffs_id', 'reconciliation_diffs', ['id'])

    # === Phase 2: Add all foreign key constraints ===

    # departments self-referencing + FK to users
    op.create_foreign_key(None, 'departments', 'departments', ['parent_id'], ['id'])
    op.create_foreign_key(None, 'departments', 'users', ['manager_id'], ['id'])
    op.create_foreign_key(None, 'departments', 'users', ['measurer_id'], ['id'])

    # users -> departments
    op.create_foreign_key(None, 'users', 'departments', ['department_id'], ['id'])

    # instrument_categories self-referencing
    op.create_foreign_key(None, 'instrument_categories', 'instrument_categories', ['parent_id'], ['id'])

    # calibration_contracts
    op.create_foreign_key(None, 'calibration_contracts', 'calibration_agencies', ['agency_id'], ['id'])
    op.create_foreign_key(None, 'calibration_contracts', 'departments', ['department_id'], ['id'])

    # instruments
    op.create_foreign_key(None, 'instruments', 'instrument_categories', ['category_id'], ['id'])
    op.create_foreign_key(None, 'instruments', 'departments', ['department_id'], ['id'])

    # supervision_plans
    op.create_foreign_key(None, 'supervision_plans', 'departments', ['department_id'], ['id'])
    op.create_foreign_key(None, 'supervision_plans', 'users', ['executor_id'], ['id'])
    op.create_foreign_key(None, 'supervision_plans', 'supervision_templates', ['template_id'], ['id'])

    # supervision_template_items
    op.create_foreign_key(None, 'supervision_template_items', 'supervision_templates', ['template_id'], ['id'])

    # workflows
    op.create_foreign_key(None, 'workflows', 'departments', ['department_id'], ['id'])
    op.create_foreign_key(None, 'workflows', 'users', ['initiator_id'], ['id'])

    # borrow_records
    op.create_foreign_key(None, 'borrow_records', 'instruments', ['instrument_id'], ['id'])
    op.create_foreign_key(None, 'borrow_records', 'departments', ['from_department'], ['id'])
    op.create_foreign_key(None, 'borrow_records', 'departments', ['to_department'], ['id'])

    # contract_items
    op.create_foreign_key(None, 'contract_items', 'calibration_contracts', ['contract_id'], ['id'])

    # contract_versions
    op.create_foreign_key(None, 'contract_versions', 'calibration_contracts', ['contract_id'], ['id'])
    op.create_foreign_key(None, 'contract_versions', 'users', ['uploader_id'], ['id'])

    # repair_records
    op.create_foreign_key(None, 'repair_records', 'instruments', ['instrument_id'], ['id'])

    # supervision_executions
    op.create_foreign_key(None, 'supervision_executions', 'users', ['executor_id'], ['id'])
    op.create_foreign_key(None, 'supervision_executions', 'supervision_plans', ['plan_id'], ['id'])
    op.create_foreign_key(None, 'supervision_executions', 'users', ['reviewer_id'], ['id'])
    op.create_foreign_key(None, 'supervision_executions', 'departments', ['target_department_id'], ['id'])
    op.create_foreign_key(None, 'supervision_executions', 'supervision_templates', ['template_id'], ['id'])

    # workflow_nodes
    op.create_foreign_key(None, 'workflow_nodes', 'users', ['approver_id'], ['id'])
    op.create_foreign_key(None, 'workflow_nodes', 'workflows', ['workflow_id'], ['id'])

    # calibration_records
    op.create_foreign_key(None, 'calibration_records', 'calibration_agencies', ['agency_id'], ['id'])
    op.create_foreign_key(None, 'calibration_records', 'calibration_contracts', ['contract_id'], ['id'])
    op.create_foreign_key(None, 'calibration_records', 'contract_items', ['contract_item_id'], ['id'])
    op.create_foreign_key(None, 'calibration_records', 'instruments', ['instrument_id'], ['id'])

    # execution_records
    op.create_foreign_key(None, 'execution_records', 'calibration_agencies', ['agency_id'], ['id'])
    op.create_foreign_key(None, 'execution_records', 'contract_items', ['contract_item_id'], ['id'])
    op.create_foreign_key(None, 'execution_records', 'departments', ['department_id'], ['id'])
    op.create_foreign_key(None, 'execution_records', 'instruments', ['instrument_id'], ['id'])

    # supervision_check_items
    op.create_foreign_key(None, 'supervision_check_items', 'supervision_executions', ['execution_id'], ['id'])
    op.create_foreign_key(None, 'supervision_check_items', 'users', ['inspector_id'], ['id'])
    op.create_foreign_key(None, 'supervision_check_items', 'supervision_template_items', ['template_item_id'], ['id'])

    # certificates
    op.create_foreign_key(None, 'certificates', 'calibration_records', ['calibration_record_id'], ['id'])

    # non_conformities
    op.create_foreign_key(None, 'non_conformities', 'supervision_check_items', ['check_item_id'], ['id'])
    op.create_foreign_key(None, 'non_conformities', 'departments', ['department_id'], ['id'])
    op.create_foreign_key(None, 'non_conformities', 'users', ['issued_by'], ['id'])
    op.create_foreign_key(None, 'non_conformities', 'users', ['responsible_person'], ['id'])
    op.create_foreign_key(None, 'non_conformities', 'supervision_executions', ['supervision_execution_id'], ['id'])
    op.create_foreign_key(None, 'non_conformities', 'users', ['verified_by'], ['id'])

    # reconciliation_diffs
    op.create_foreign_key(None, 'reconciliation_diffs', 'users', ['confirmed_by'], ['id'])
    op.create_foreign_key(None, 'reconciliation_diffs', 'calibration_contracts', ['contract_id'], ['id'])
    op.create_foreign_key(None, 'reconciliation_diffs', 'execution_records', ['execution_record_id'], ['id'])


def downgrade() -> None:
    op.drop_index('ix_reconciliation_diffs_id', table_name='reconciliation_diffs')
    op.drop_table('reconciliation_diffs')
    op.drop_index('ix_non_conformities_id', table_name='non_conformities')
    op.drop_table('non_conformities')
    op.drop_index('ix_certificates_id', table_name='certificates')
    op.drop_table('certificates')
    op.drop_index('ix_supervision_check_items_id', table_name='supervision_check_items')
    op.drop_table('supervision_check_items')
    op.drop_index('ix_execution_records_id', table_name='execution_records')
    op.drop_table('execution_records')
    op.drop_index('ix_calibration_records_id', table_name='calibration_records')
    op.drop_table('calibration_records')
    op.drop_index('ix_workflow_nodes_id', table_name='workflow_nodes')
    op.drop_table('workflow_nodes')
    op.drop_index('ix_supervision_executions_id', table_name='supervision_executions')
    op.drop_table('supervision_executions')
    op.drop_index('ix_repair_records_id', table_name='repair_records')
    op.drop_table('repair_records')
    op.drop_index('ix_contract_versions_id', table_name='contract_versions')
    op.drop_table('contract_versions')
    op.drop_index('ix_contract_items_id', table_name='contract_items')
    op.drop_table('contract_items')
    op.drop_index('ix_borrow_records_id', table_name='borrow_records')
    op.drop_table('borrow_records')
    op.drop_index('ix_workflows_id', table_name='workflows')
    op.drop_table('workflows')
    op.drop_index('ix_supervision_template_items_id', table_name='supervision_template_items')
    op.drop_table('supervision_template_items')
    op.drop_index('ix_supervision_plans_id', table_name='supervision_plans')
    op.drop_table('supervision_plans')
    op.drop_index('ix_instruments_id', table_name='instruments')
    op.drop_table('instruments')
    op.drop_index('ix_calibration_contracts_id', table_name='calibration_contracts')
    op.drop_table('calibration_contracts')
    op.drop_index('ix_users_id', table_name='users')
    op.drop_table('users')
    op.drop_index('ix_supervision_templates_id', table_name='supervision_templates')
    op.drop_table('supervision_templates')
    op.drop_index('ix_instrument_categories_id', table_name='instrument_categories')
    op.drop_table('instrument_categories')
    op.drop_index('ix_departments_id', table_name='departments')
    op.drop_table('departments')
    op.drop_index('ix_calibration_agencies_id', table_name='calibration_agencies')
    op.drop_table('calibration_agencies')
