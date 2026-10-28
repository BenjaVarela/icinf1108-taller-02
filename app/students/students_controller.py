import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.shared.database import get_db
from app.models import Student

router = APIRouter(prefix="/students", tags=["Students"])

@router.get("/")
def get_all_students(db: Session = Depends(get_db)):
    return db.query(Student).all()

@router.get("/{student_id}")
def get_student_by_id(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return student

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_student(student_in: dict, db: Session = Depends(get_db)):
    try:
        new_student = Student(
            id=str(uuid.uuid4()),
            username=student_in["username"],
            email=student_in["email"],
            name=student_in["name"],
            age=student_in["age"],
            created_at=datetime.utcnow()
        )
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creando estudiante: {str(e)}")

@router.delete("/{student_id}")
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    try:
        db.delete(student)
        db.commit()
        return {"message": "Estudiante eliminado exitosamente"}
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error en la transacción al eliminar")