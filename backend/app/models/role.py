"""
Role and Permission models for access control
"""
import uuid

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Permission(Base):
    """
    Permission model - fine-grained permissions for role-based access control
    """

    __tablename__ = "permission"
    __table_args__ = (UniqueConstraint("resource", "action", name="uq_permission_resource_action"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    # Resource and Action (e.g., "invoice:create", "product:edit", "report:view")
    resource: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    # Display name and description
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Category for grouping (e.g., "billing", "inventory", "reporting", "admin")
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Relationships
    roles: Mapped[list["Role"]] = relationship(
        "Role", secondary="role_permission", back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"<Permission {self.name}>"


class Role(Base):
    """
    Role model - role definitions for businesses
    Roles are business-scoped (owner can have custom roles)
    """

    __tablename__ = "role"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    business_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("business.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Role metadata
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # If True, role is system-defined (owner, admin, staff) and cannot be edited/deleted
    is_system_role: Mapped[bool] = mapped_column(default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # Relationships
    business: Mapped["Business"] = relationship("Business")
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission", secondary="role_permission", back_populates="roles"
    )
    users: Mapped[list["User"]] = relationship(
        "User", back_populates="custom_role"
    )

    def __repr__(self) -> str:
        return f"<Role {self.name}>"


# Association table for Role-Permission relationship
from sqlalchemy import Table, Column

role_permission = Table(
    "role_permission",
    Base.metadata,
    Column("role_id", ForeignKey("role.id", ondelete="CASCADE"), primary_key=True),
    Column("permission_id", ForeignKey("permission.id", ondelete="CASCADE"), primary_key=True),
)
