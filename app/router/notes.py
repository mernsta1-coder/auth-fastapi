from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database.database import get_db
from app.models.notes import Note

router = APIRouter(prefix="/notes", tags=["notes"])

bearer_scheme = HTTPBearer()


# CREATE NOTE
@router.post("/", summary="Create note")
def create_note(
    title: str,
    content: str,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    user_payload = getattr(request.state, "user", None)

    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user_payload.get("sub")

    note = Note(
        title=title,
        content=content,
        user_id=user_id
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return {"message": "Note created", "note": note}


# GET ALL NOTES
@router.get("/", summary="Get notes")
def get_notes(
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    user_payload = getattr(request.state, "user", None)

    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user_payload.get("sub")

    notes = db.query(Note).filter(Note.user_id == user_id).all()

    return notes


# GET SINGLE NOTE
@router.get("/{note_id}", summary="Get single note")
def get_note(
    note_id: int,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    user_payload = getattr(request.state, "user", None)

    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user_payload.get("sub")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    return note


# UPDATE NOTE
@router.put("/{note_id}", summary="Update note")
def update_note(
    note_id: int,
    title: str,
    content: str,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    user_payload = getattr(request.state, "user", None)

    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user_payload.get("sub")

    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    note.title = title
    note.content = content

    db.commit()
    db.refresh(note)

    return {"message": "Note updated", "note": note}


# DELETE NOTE
@router.delete("/{note_id}", summary="Delete note")
def delete_note(
    note_id: int,
    request: Request,
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    user_payload = getattr(request.state, "user", None)

    if not user_payload:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_id = user_payload.get("sub")
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()

    return {"message": "Note deleted"}