from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from app.database import get_db
from app.models.db import OfferChangeLog
from app.services.keitaro import KeitaroClient

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


class OfferActionIn(BaseModel):
    offer_id: int


def _stream_update_payload(stream: dict, new_offers: list) -> dict:
    landings = []
    for l in stream.get("landings") or []:
        landings.append({
            "landing_id": l.get("landing_id") or l.get("id"),
            "share": l.get("share", 100),
            "state": l.get("state", "active"),
        })
    # remove None landing_id
    landings = [x for x in landings if x.get("landing_id") is not None]

    offers = []
    for o in new_offers:
        offers.append({
            "offer_id": o.get("offer_id") if isinstance(o, dict) else o,
            "share": o.get("share", 100) if isinstance(o, dict) else 100,
            "state": o.get("state", "active") if isinstance(o, dict) else "active",
        })

    payload = {
        "campaign_id": stream.get("campaign_id"),
        "type": stream.get("type", "regular"),
        "name": stream.get("name"),
        "action_type": stream.get("action_type"),
        "schema": stream.get("schema"),
        "state": stream.get("state", "active"),
        "position": stream.get("position"),
        "weight": stream.get("weight"),
        "collect_clicks": stream.get("collect_clicks", False),
        "filter_or": stream.get("filter_or", False),
        "filters": stream.get("filters") or [],
        "landings": landings,
        "offers": offers,
    }
    # remove None values for optional
    for k in ["position", "weight"]:
        if payload.get(k) is None:
            payload.pop(k, None)
    return payload


@router.get("/editor", response_class=HTMLResponse)
def editor_page(request: Request):
    return templates.TemplateResponse("editor.html", {"request": request})


@router.get("/api/editor/campaigns")
def editor_campaigns():
    return KeitaroClient().list_campaigns()


@router.get("/api/editor/campaigns/{campaign_id}/streams")
def editor_streams(campaign_id: int):
    return KeitaroClient().list_streams(campaign_id)


@router.get("/api/editor/offers")
def editor_offers():
    return KeitaroClient().list_offers()


@router.get("/api/editor/streams/{stream_id}")
def editor_stream(stream_id: int):
    return KeitaroClient().get_stream(stream_id)


@router.post("/api/editor/streams/{stream_id}/offers/add")
def add_offer(stream_id: int, payload: OfferActionIn, db: Session = Depends(get_db)):
    kt = KeitaroClient()
    stream = kt.get_stream(stream_id)
    offers = list(stream.get("offers") or [])
    # check duplicate
    if any((o.get("offer_id") == payload.offer_id) for o in offers):
        raise HTTPException(status_code=400, detail="Offer already attached to this stream")
    offers.append({"offer_id": payload.offer_id, "share": 100, "state": "active"})
    new_payload = _stream_update_payload(stream, offers)
    updated = kt.update_stream(stream_id, new_payload)

    log = OfferChangeLog(campaign_id=stream.get("campaign_id"), stream_id=stream_id,
                         offer_id=payload.offer_id, action="add")
    db.add(log)
    db.commit()
    return {"ok": True, "stream": updated}


@router.post("/api/editor/streams/{stream_id}/offers/remove")
def remove_offer(stream_id: int, payload: OfferActionIn, db: Session = Depends(get_db)):
    kt = KeitaroClient()
    stream = kt.get_stream(stream_id)
    offers = [o for o in (stream.get("offers") or []) if o.get("offer_id") != payload.offer_id]
    if len(offers) == len(stream.get("offers") or []):
        raise HTTPException(status_code=400, detail="Offer not found on this stream")
    new_payload = _stream_update_payload(stream, offers)
    updated = kt.update_stream(stream_id, new_payload)

    log = OfferChangeLog(campaign_id=stream.get("campaign_id"), stream_id=stream_id,
                         offer_id=payload.offer_id, action="remove")
    db.add(log)
    db.commit()
    return {"ok": True, "stream": updated}