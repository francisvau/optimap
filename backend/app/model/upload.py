from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model.base import Base


class Upload(Base):
    __tablename__ = "uploads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_filename: Mapped[str] = mapped_column(String, nullable=False)
    generated_filename: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    file_extension: Mapped[str] = mapped_column(String, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    # The user that uploaded the file.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    user = relationship("User", back_populates="uploads")

    def __repr__(self) -> str:
        """Return a string representation of the Upload object."""
        return f"<Upload {self.original_filename} ({self.generated_filename})>"
