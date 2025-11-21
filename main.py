import os
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Partner, Update

app = FastAPI(title="H2Ok API", version="0.1.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _seed_tyumen_lifemart():
    """Return a list of 11 LifeMart (ЖизньМарт) partner dicts in Tyumen."""
    base = [
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, центр",
            "latitude": 57.15303,
            "longitude": 65.53433,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Заречный",
            "latitude": 57.1605,
            "longitude": 65.5255,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Восточный",
            "latitude": 57.1482,
            "longitude": 65.5968,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Дом обороны",
            "latitude": 57.1675,
            "longitude": 65.6072,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Тура",
            "latitude": 57.1352,
            "longitude": 65.5209,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Мыс",
            "latitude": 57.2050,
            "longitude": 65.5975,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Тюменская слобода",
            "latitude": 57.1105,
            "longitude": 65.5701,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Лесобаза",
            "latitude": 57.1077,
            "longitude": 65.4859,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Плеханово",
            "latitude": 57.1189,
            "longitude": 65.6505,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Антипино",
            "latitude": 57.0903,
            "longitude": 65.6697,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
        {
            "name": "ЖизньМарт",
            "address": "Тюмень, Тарманы",
            "latitude": 57.1516,
            "longitude": 65.4334,
            "category": "shop",
            "open_hours": "08:00-22:00",
            "has_cold": True,
            "has_hot": False,
            "access_type": "free",
            "is_new": True,
        },
    ]
    return base


@app.get("/")
def read_root():
    return {"message": "H2Ok backend is running"}


@app.get("/api/partners")
def list_partners(
    category: Optional[str] = Query(None, description="Filter by category"),
    has_hot: Optional[bool] = Query(None, description="Hot water available"),
    has_cold: Optional[bool] = Query(None, description="Cold water available"),
    is_new: Optional[bool] = Query(None, description="Highlight new partners"),
    q: Optional[str] = Query(None, description="Text search by name/address"),
):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")

    # Auto-seed Tyumen LifeMart if collection is empty
    try:
        if db["partner"].count_documents({}) == 0:
            seed = _seed_tyumen_lifemart()
            if seed:
                db["partner"].insert_many(seed)
    except Exception:
        pass

    filt = {}
    if category:
        filt["category"] = category
    if has_hot is not None:
        filt["has_hot"] = has_hot
    if has_cold is not None:
        filt["has_cold"] = has_cold
    if is_new is not None:
        filt["is_new"] = is_new
    if q:
        filt["$or"] = [
            {"name": {"$regex": q, "$options": "i"}},
            {"address": {"$regex": q, "$options": "i"}},
        ]

    docs = get_documents("partner", filt)
    # Convert ObjectId
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    return {"items": docs, "count": len(docs)}


@app.get("/api/partners/{partner_id}")
def get_partner(partner_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    doc = db["partner"].find_one({"_id": ObjectId(partner_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Partner not found")
    doc["id"] = str(doc["_id"]) 
    doc.pop("_id", None)
    return doc


@app.post("/api/partners", status_code=201)
def create_partner(partner: Partner):
    partner_id = create_document("partner", partner)
    return {"id": partner_id}


@app.post("/api/partners/bulk", status_code=201)
def create_partners_bulk(partners: List[Partner]):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    to_insert = [p.model_dump() for p in partners]
    res = db["partner"].insert_many(to_insert)
    return {"inserted": len(res.inserted_ids), "ids": [str(x) for x in res.inserted_ids]}


@app.get("/api/updates")
def list_updates(limit: int = 20):
    docs = get_documents("update", {}, limit=limit)
    for d in docs:
        d["id"] = str(d.get("_id"))
        d.pop("_id", None)
    # Sort newest first if timestamps present
    docs = sorted(docs, key=lambda x: x.get("created_at", 0), reverse=True)
    return {"items": docs, "count": len(docs)}


@app.post("/api/updates", status_code=201)
def create_update(update: Update):
    update_id = create_document("update", update)
    return {"id": update_id}


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
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
