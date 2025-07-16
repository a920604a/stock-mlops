# backend/src/crud.py
from sqlalchemy.orm import Session
from typing import List, Optional

from . import models, schemas  # Import SQLAlchemy models and Pydantic schemas

# --- CRUD Operations for ModelMetadata ---


def get_model(db: Session, model_id: int) -> Optional[models.ModelMetadata]:
    """
    Retrieve a single model metadata entry by its ID.

    Args:
        db (Session): The database session.
        model_id (int): The ID of the model metadata to retrieve.

    Returns:
        Optional[models.ModelMetadata]: The ModelMetadata object if found, else None.
    """
    return (
        db.query(models.ModelMetadata)
        .filter(models.ModelMetadata.id == model_id)
        .first()
    )


def get_models(
    db: Session, skip: int = 0, limit: int = 100
) -> List[models.ModelMetadata]:
    """
    Retrieve a list of model metadata entries.

    Args:
        db (Session): The database session.
        skip (int): The number of records to skip (for pagination).
        limit (int): The maximum number of records to return.

    Returns:
        List[models.ModelMetadata]: A list of ModelMetadata objects.
    """
    return db.query(models.ModelMetadata).offset(skip).limit(limit).all()


def create_model(
    db: Session, model: schemas.ModelMetadataCreate
) -> models.ModelMetadata:
    """
    Create a new model metadata entry in the database.

    Args:
        db (Session): The database session.
        model (schemas.ModelMetadataCreate): The Pydantic model containing the data for the new entry.

    Returns:
        models.ModelMetadata: The newly created ModelMetadata object.
    """
    # Create a SQLAlchemy model instance from the Pydantic schema data
    db_model = models.ModelMetadata(
        **model.model_dump()
    )  # Use model_dump() for Pydantic v2+
    db.add(db_model)  # Add the new object to the session
    db.commit()  # Commit the transaction to save to the database
    db.refresh(
        db_model
    )  # Refresh the object to get any auto-generated fields (like 'id', 'created_at')
    return db_model


def update_model(
    db: Session, model_id: int, model_update: schemas.ModelMetadataUpdate
) -> Optional[models.ModelMetadata]:
    """
    Update an existing model metadata entry.

    Args:
        db (Session): The database session.
        model_id (int): The ID of the model metadata to update.
        model_update (schemas.ModelMetadataUpdate): The Pydantic model with fields to update.

    Returns:
        Optional[models.ModelMetadata]: The updated ModelMetadata object if found and updated, else None.
    """
    db_model = (
        db.query(models.ModelMetadata)
        .filter(models.ModelMetadata.id == model_id)
        .first()
    )
    if db_model:
        # Iterate over the fields provided in the update schema
        for key, value in model_update.model_dump(
            exclude_unset=True
        ).items():  # exclude_unset=True only updates provided fields
            setattr(db_model, key, value)  # Set the attribute on the SQLAlchemy model
        db.commit()  # Commit the transaction
        db.refresh(db_model)  # Refresh to ensure latest state
    return db_model


def delete_model(db: Session, model_id: int) -> Optional[models.ModelMetadata]:
    """
    Delete a model metadata entry from the database.

    Args:
        db (Session): The database session.
        model_id (int): The ID of the model metadata to delete.

    Returns:
        Optional[models.ModelMetadata]: The deleted ModelMetadata object if found and deleted, else None.
    """
    db_model = (
        db.query(models.ModelMetadata)
        .filter(models.ModelMetadata.id == model_id)
        .first()
    )
    if db_model:
        db.delete(db_model)  # Delete the object from the session
        db.commit()  # Commit the transaction
    return db_model
