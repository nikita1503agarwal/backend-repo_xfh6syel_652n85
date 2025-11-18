import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from typing import Any

from database import db, create_document, get_documents
from schemas import ContactMessage, NewsletterSubscriber, ConsentEvent

app = FastAPI(title="JV Commerce Media API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = os.getenv("DATABASE_NAME") or "❌ Not Set"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response

@app.post("/contact")
async def submit_contact(payload: ContactMessage):
    try:
        doc_id = create_document('contactmessage', payload)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/newsletter")
async def subscribe_newsletter(payload: NewsletterSubscriber):
    try:
        # dedupe by email
        existing = get_documents('newslettersubscriber', {"email": payload.email}, limit=1)
        if existing:
            return {"ok": True, "duplicate": True}
        doc_id = create_document('newslettersubscriber', payload)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/consent")
async def log_consent(event: ConsentEvent, request: Request):
    try:
        # enrich
        user_agent = request.headers.get('user-agent')
        event.user_agent = user_agent
        doc_id = create_document('consentevent', event)
        return {"ok": True, "id": doc_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.exception_handler(422)
async def validation_exception_handler(request: Request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "ok": False,
            "error": "Validation error",
            "details": exc.errors() if hasattr(exc, 'errors') else str(exc)
        },
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
