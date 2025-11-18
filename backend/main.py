from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from typing import Any, Dict
from schemas import ContactMessage, NewsletterSubscriber, ConsentEvent
from database import create_document, get_documents, db  # type: ignore

app = FastAPI(title="Commerce Media JV API", version="1.0.0")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test() -> Dict[str, Any]:
    try:
        # quick ping to database (list collections)
        collections = await db.list_collection_names()  # type: ignore
        return {"status": "ok", "db_collections": collections}
    except Exception as e:
        return {"status": "degraded", "error": str(e)}


@app.post("/contact")
async def submit_contact(payload: ContactMessage) -> Dict[str, Any]:
    try:
        doc = payload.dict()
        inserted = await create_document("contactmessage", doc)
        return {
            "success": True,
            "message": "Danke! Wir melden uns zeitnah.",
            "id": str(inserted.get("_id")) if isinstance(inserted, dict) else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern: {e}")


@app.post("/newsletter")
async def newsletter_signup(payload: NewsletterSubscriber) -> Dict[str, Any]:
    try:
        # dedupe by email (best-effort)
        existing = await get_documents("newslettersubscriber", {"email": payload.email}, limit=1)
        if existing:
            return {"success": True, "message": "Diese E-Mail ist bereits angemeldet."}
        inserted = await create_document("newslettersubscriber", payload.dict())
        return {"success": True, "message": "Newsletter erfolgreich abonniert."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Abonnieren: {e}")


@app.post("/consent")
async def consent_event(payload: ConsentEvent) -> Dict[str, Any]:
    try:
        await create_document("consentevent", payload.dict())
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consent konnte nicht gespeichert werden: {e}")
