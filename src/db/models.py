from __future__ import annotations

import enum
import uuid
from typing import Type, Union
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, RelationshipProperty

from src.db.base import Base

TableType = Union[
    Type["UserTable"], Type["Commodity"], Type["Account"], Type["Transaction"]
]


class UserType(enum.Enum):

    ADMIN = "ADMIN"
    REGULAR_USER = "REGULAR_USER"


class UserStatus(enum.Enum):

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class UserTable(Base):
    __tablename__ = "user_table"
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(36), nullable=False)
    type = Column(
        Enum(UserType),
        default=UserType.REGULAR_USER.name,
        server_default=UserType.REGULAR_USER.name,
        nullable=False,
    )
    status = Column(
        Enum(UserStatus),
        default=UserStatus.INACTIVE.name,
        server_default=UserStatus.INACTIVE.name,
        nullable=False,
    )
    accounts: RelationshipProperty[list[Account]] = relationship(
        "Account", back_populates="user_table"
    )


class Commodity(Base):
    __tablename__ = "commodity"
    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    description = Column(String(500))
    price = Column(Integer, nullable=False)


class Account(Base):
    __tablename__ = "account"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    balance = Column(Integer, default=0, nullable=False)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"))
    user_table: RelationshipProperty[UserTable] = relationship(
        "UserTable", back_populates="accounts"
    )
    transactions: RelationshipProperty[list[Transaction]] = relationship(
        "Transaction", back_populates="account"
    )


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Integer)
    account_id = Column(
        UUID(as_uuid=True), ForeignKey("account.id", ondelete="CASCADE")
    )
    account: RelationshipProperty[Account] = relationship(
        "Account", back_populates="transactions"
    )
