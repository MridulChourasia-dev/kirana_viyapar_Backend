-- Clear and re-insert correct migration records
TRUNCATE TABLE alembic_version;
INSERT INTO alembic_version (version_num) VALUES ('000_create_core_tables');
INSERT INTO alembic_version (version_num) VALUES ('001_add_erp_models');
INSERT INTO alembic_version (version_num) VALUES ('002_add_audit_notifications');
INSERT INTO alembic_version (version_num) VALUES ('003_add_customer_address_fields');
INSERT INTO alembic_version (version_num) VALUES ('004_fix_product_schema');
INSERT INTO alembic_version (version_num) VALUES ('005_drop_product_unit_enum');
