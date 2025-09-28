from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Text, UniqueConstraint
from app.db import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), index=True)
    message: Mapped[str | None] = mapped_column(Text, default=None)

    __table_args__ = (
        UniqueConstraint("email", "message", name="uq_email_message"),
    )
