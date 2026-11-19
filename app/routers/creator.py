import re
import random
import string
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.database import get_db
from app.models.db import CampaignRecord
from app.services.keitaro import KeitaroClient

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def slugify(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "campaign"


class CreateCampaignIn(BaseModel):
    name: str
    country_code: str
    offer_id: int
    domain_id: Optional[int] = None
    group_id: Optional[int] = None
    traffic_source_id: Optional[int] = None


@router.get("/creator", response_class=HTMLResponse)
def creator_page(request: Request):
    return templates.TemplateResponse(request, "creator.html", {"request": request})


@router.get("/api/keitaro/domains")
def api_domains():
    return KeitaroClient().list_domains()


@router.get("/api/keitaro/groups")
def api_groups(type: str = "campaigns"):
    return KeitaroClient().list_groups(type)


@router.get("/api/keitaro/sources")
def api_sources():
    return KeitaroClient().list_traffic_sources()


@router.get("/api/keitaro/offers")
def api_offers():
    return KeitaroClient().list_offers()


@router.post("/api/creator/create")
def create_campaign(payload: CreateCampaignIn, db: Session = Depends(get_db)):
    payload.country_code = payload.country_code.upper().strip()
    kt = KeitaroClient()
    # check for duplicate campaign name
    try:
        existing = kt.list_campaigns()
        if any(c.get("name") == payload.name for c in existing):
            raise HTTPException(status_code=400, detail="Название кампании не может повторяться")
    except HTTPException:
        raise
    except Exception:
        pass
    domain_id = payload.domain_id or kt.ensure_domain()
    group_id = payload.group_id or kt.ensure_group()
    ts_id = payload.traffic_source_id or kt.ensure_traffic_source()
    if domain_id is None:
        raise HTTPException(status_code=400, detail="В Keitaro нет доступных доменов")
    if ts_id is None:
        raise HTTPException(status_code=400, detail="В Keitaro нет доступных источников трафика")

    alias = slugify(payload.name) + "-" + "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
    try:
        campaign = kt.create_campaign({
            "name": payload.name,
            "alias": alias,
            "type": "position",
            "state": "active",
            "domain_id": domain_id,
            "group_id": group_id,
            "traffic_source_id": ts_id,
        })
    except RuntimeError as e:
        if "already used" in str(e).lower() or "422" in str(e):
            raise HTTPException(status_code=400, detail="Название кампании не может повторяться")
        raise
    cid = campaign["id"]

    # Stream 1: country -> Google (try 'country' filter, fallback to 'geo' for older Keitaro)
    redirect_action = kt.pick_redirect_action() or "redirect"
    stream1_payload = {
        "campaign_id": cid,
        "type": "regular",
        "name": f"Google ({payload.country_code})",
        "action_type": redirect_action,
        "schema": "redirect",
        "action_payload": "https://www.google.com/",
        "position": 1,
        "state": "active",
        "filters": [{"name": "country", "mode": "accept", "payload": [payload.country_code]}],
    }
    try:
        kt.create_stream(stream1_payload)
    except RuntimeError:
        stream1_payload["filters"] = [{"name": "geo", "mode": "accept", "payload": [payload.country_code]}]
        kt.create_stream(stream1_payload)

    # Stream 2: offer
    landing_action = kt.pick_landing_action() or "show_landing_page"
    kt.create_stream({
        "campaign_id": cid,
        "type": "default",
        "name": "Offer",
        "action_type": landing_action,
        "schema": "landings",
        "position": 2,
        "state": "active",
        "offers": [{"offer_id": payload.offer_id, "share": 100}],
    })

    rec = CampaignRecord(
        name=payload.name,
        country_code=payload.country_code,
        offer_id=payload.offer_id,
        keitaro_campaign_id=cid,
        domain_id=domain_id,
        group_id=group_id,
        traffic_source_id=ts_id,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {"ok": True, "campaign": campaign, "local_id": rec.id}