"""Contains models to create the database."""

from datetime import datetime, timezone

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
    description = Column(Text, nullable=True)

    # Relationships - One-to-Many: Many domains may belong to one community
    domains = relationship("Domaine", back_populates="community", cascade="all, delete-orphan")

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
    # 1. Many-to-One: Many domains may belong to one community
    community = relationship("Communaute", back_populates="domains")
    # 2. One-to-Many: One domain may have many data_tables
    data_tables = relationship("DataTable", back_populates="domain", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Provide a string representation of the Domaine model."""
        return f"<Domaine(id={self.id}, nom='{self.nom}')>"


class DataTable(Base):
    """Model for the data_tables table."""

    __tablename__ = "data_tables"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    date_creation = Column(DateTime, default=datetime.now(timezone.utc))  # type: ignore [reportAttributeAccessIssue]
    date_derniere_modification = Column(
        DateTime,
        default=datetime.now(timezone.utc),  # type: ignore [reportAttributeAccessIssue]
        onupdate=datetime.now(timezone.utc),  # type: ignore [reportAttributeAccessIssue]
    )
    domaine_id = Column(String(255), ForeignKey("domaines.id"), nullable=False, index=True)

    # Relationships
    # 1. Many-to-One: Many data_tables may belong to one domain
    domain = relationship("Domaine", back_populates="data_tables")
    # 2. One-to-Many: One data_table may have many data_columns
    data_columns = relationship("DataColonne", back_populates="data_table", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Provide a string representation of the DataTable model."""
        return f"<DataTable(id={self.id}, nom='{self.nom}')>"


class DataColonne(Base):
    """Model for the data_colonnes table."""

    __tablename__ = "data_colonnes"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    data_type = Column(String(50), nullable=True)

    date_creation = Column(DateTime, default=datetime.now(timezone.utc))  # type: ignore [reportAttributeAccessIssue]
    date_derniere_modification = Column(
        DateTime,
        default=datetime.now(timezone.utc),  # type: ignore [reportAttributeAccessIssue]
        onupdate=datetime.now(timezone.utc),  # type: ignore [reportAttributeAccessIssue]
    )
    code_set_id = Column(String(255), ForeignKey("code_sets.id"), nullable=True, index=True)
    data_table_id = Column(String(255), ForeignKey("data_tables.id"), nullable=False, index=True)

    # Relationships
    # 1. Many-to-One: Many data_columns may belong to one data_table
    data_table = relationship("DataTable", back_populates="data_columns")
    # 2. Many-to-One: Many data_columns may have one code_set
    code_set = relationship("CodeSet", back_populates="data_columns")

    def __repr__(self) -> str:
        """Provide a string representation of the DataColonne model."""
        return f"<DataColonne(id={self.id}, nom='{self.nom}')>"


class CodeSet(Base):
    """Model for the code_sets table."""

    __tablename__ = "code_sets"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Relationships
    # 1. One-to-Many: One code_set may target many data_columns
    data_columns = relationship("DataColonne", back_populates="code_set", cascade="all, delete-orphan")
    # 2. One-to-Many: One code set corresponds to many code_values
    code_values = relationship("CodeValue", back_populates="code_set", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        """Provide a string representation of the CodeSet model."""
        return f"<CodeSet(id={self.id}, nom='{self.nom}')>"


class CodeValue(Base):
    """Model for the code_values table."""

    __tablename__ = "code_values"

    # Fields
    id = Column(String(255), primary_key=True, index=True)
    nom = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    code = Column(String(255), nullable=True)
    code_set_id = Column(String(255), ForeignKey("code_sets.id"), nullable=False, index=True)

    # Relationships - Many-to-One: Many code values correspond to one code set
    code_set = relationship("CodeSet", back_populates="code_values")

    def __repr__(self) -> str:
        """Provide a string representation of the CodeValue model."""
        return f"<CodeValue(id={self.id}, nom='{self.nom}', code='{self.code}')>"
