"""Contains models to create the database."""

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

# Base class for each model class
Base = declarative_base()


class Communaute(Base):
    """Model for the communautes table."""

    __tablename__ = "communautes"

    # Fields
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    nom = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)  # Explicitely nullable

    # Relationships
    domaines = relationship("Domaine", back_populates="communaute", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Provide a string representation of the Communaute model."""
        return f"<Communaute(id={self.id}, nom='{self.nom}')>"


class Domaine(Base):
    """Model for the domaines table."""

    __tablename__ = "domaines"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    communaute_id = Column(Integer, ForeignKey("communautes.id"), nullable=False, index=True)

    # Relationships
    communaute = relationship("Communaute", back_populates="domaines")  # Many-to-One
    data_tables = relationship("DataTable", back_populates="domaine", cascade="all, delete-orphan")  # One-to-Many

    def __repr__(self) -> str:
        """Provide a string representation of the Domaine model."""
        return f"<Domaine(id={self.id}, nom='{self.nom}')>"


class DataTable(Base):
    """Model for the data_tables table."""

    __tablename__ = "data_tables"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)  # Text rather than String for flexibility, explicitely nullable
    date_creation = Column(DateTime, default=datetime.now(datetime.UTC))  # type: ignore [reportAttributeAccessIssue]
    date_derniere_modification = Column(
        DateTime,
        default=datetime.now(datetime.UTC),  # type: ignore [reportAttributeAccessIssue]
        onupdate=datetime.now(datetime.UTC),  # type: ignore [reportAttributeAccessIssue]
    )
    domaine_id = Column(String(255), ForeignKey("domaines.id"), nullable=False, index=True)

    # Relationships
    domaine = relationship("Domaine", back_populates="data_tables")  # Many-to-One
    data_colonnes = relationship(
        "DataColonne", back_populates="data_table", cascade="all, delete-orphan"
    )  # One-to-Many

    def __repr__(self) -> str:
        """Provide a string representation of the DataTable model."""
        return f"<DataTable(id={self.id}, nom='{self.nom}')>"


class DataColonne(Base):
    """Model for the data_colonnes table."""

    __tablename__ = "data_colonnes"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)  # Text rather than String for flexibility, explicitely nullable
    data_type = Column(String(50), nullable=True)
    date_creation = Column(DateTime, default=datetime.now(datetime.UTC))  # type: ignore [reportAttributeAccessIssue]
    date_derniere_modification = Column(
        DateTime,
        default=datetime.now(datetime.UTC),  # type: ignore [reportAttributeAccessIssue]
        onupdate=datetime.now(datetime.UTC),  # type: ignore [reportAttributeAccessIssue]
    )
    data_table_id = Column(String(255), ForeignKey("data_tables.id"), nullable=False, index=True)

    # Relationships
    data_table = relationship("DataTable", back_populates="data_colonnes")

    def __repr__(self) -> str:
        """Provide a string representation of the DataColonne model."""
        return f"<DataColonne(id={self.id}, nom='{self.nom}')>"
