import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.shared.database import get_db
from app.models import Pet, Student

router = APIRouter(prefix="/pets", tags=["Pets"])

@router.get("/")
def get_all_pets(db: Session = Depends(get_db)):
    return db.query(Pet).all()

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_pet(pet_in: dict, db: Session = Depends(get_db)):
    student_exists = db.query(Student).filter(Student.id == pet_in["student_id"]).first()
    if not student_exists:
        raise HTTPException(status_code=404, detail="El estudiante asignado no existe")
    
    try:
        new_pet = Pet(
            id=str(uuid.uuid4()),
            student_id=pet_in["student_id"],
            name=pet_in["name"],
            species=pet_in["species"],
            age=pet_in["age"],
            created_at=datetime.utcnow()
        )
        db.add(new_pet)
        db.commit()
        db.refresh(new_pet)
        return new_pet
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando mascota: {str(e)}")

@router.delete("/{pet_id}")
def delete_pet(pet_id: str, db: Session = Depends(get_db)):
    pet = db.query(Pet).filter(Pet.id == pet_id).first()
    if not pet:
        raise HTTPException(status_code=404, detail="Mascota no encontrada")
    try:
        db.delete(pet)
        db.commit()
        return {"message": "Mascota eliminada exitosamente"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error en la transacción al eliminar mascota")