import httpx
from typing import Any, Dict, List, Optional
from app.config import settings


class KeitaroClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        self.base_url = (base_url or settings.keitaro_url).rstrip("/")
        self.api_key = api_key or settings.keitaro_api_key

    @property
    def admin_base(self) -> str:
        return f"{self.base_url}/admin_api/v1"

    def _headers(self) -> Dict[str, str]:
        return {"Api-Key": self.api_key, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.admin_base}{path}"
        with httpx.Client(timeout=30.0) as client:
            resp = client.request(method, url, headers=self._headers(), **kwargs)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Keitaro API {method} {path} -> {resp.status_code}: {resp.text}")
        try:
            return resp.json()
        except Exception:
            return {"status": "ok", "code": resp.status_code}

    # --- Campaigns ---
    def list_campaigns(self) -> List[Dict]:
        return self._request("GET", "/campaigns")

    def get_campaign(self, campaign_id: int) -> Dict:
        return self._request("GET", f"/campaigns/{campaign_id}")

    def create_campaign(self, data: Dict) -> Dict:
        return self._request("POST", "/campaigns", json=data)

    def update_campaign(self, campaign_id: int, data: Dict) -> Dict:
        return self._request("PUT", f"/campaigns/{campaign_id}", json=data)

    def delete_campaign(self, campaign_id: int) -> Any:
        return self._request("DELETE", f"/campaigns/{campaign_id}")

    def list_streams(self, campaign_id: int) -> List[Dict]:
        return self._request("GET", f"/campaigns/{campaign_id}/streams")

    def get_stream(self, stream_id: int) -> Dict:
        return self._request("GET", f"/streams/{stream_id}")

    def create_stream(self, data: Dict) -> Dict:
        return self._request("POST", "/streams", json=data)

    def update_stream(self, stream_id: int, data: Dict) -> Dict:
        # Keitaro uses POST for stream updates
        return self._request("POST", f"/streams/{stream_id}", json=data)

    def delete_stream(self, stream_id: int) -> Any:
        return self._request("DELETE", f"/streams/{stream_id}")

    # --- Offers ---
    def list_offers(self) -> List[Dict]:
        return self._request("GET", "/offers")

    def get_offer(self, offer_id: int) -> Dict:
        return self._request("GET", f"/offers/{offer_id}")

    # --- Domains ---
    def list_domains(self) -> List[Dict]:
        return self._request("GET", "/domains")

    # --- Groups ---
    def list_groups(self, type_: str = "campaigns") -> List[Dict]:
        return self._request("GET", f"/groups?type={type_}")

    def create_group(self, data: Dict) -> Dict:
        return self._request("POST", "/groups", json=data)

    # --- Traffic sources ---
    def list_traffic_sources(self) -> List[Dict]:
        return self._request("GET", "/traffic_sources")

    # --- Discovery ---
    def list_stream_schemas(self) -> List[Dict]:
        return self._request("GET", "/stream_schemas")

    def list_stream_types(self) -> List[Dict]:
        return self._request("GET", "/stream_types")

    def list_stream_actions(self) -> List[Dict]:
        return self._request("GET", "/streams_actions")

    # --- helpers ---
    def pick_redirect_action(self) -> Optional[str]:
        try:
            actions = self.list_stream_actions()
        except Exception:
            return None
        # prefer an action whose type/key/name mentions redirect
        for a in actions:
            hay = " ".join(str(a.get(k, "")) for k in ("key", "name", "type", "description")).lower()
            if "redirect" in hay:
                return a.get("key")
        return actions[0].get("key") if actions else None

    def pick_landing_action(self) -> Optional[str]:
        try:
            actions = self.list_stream_actions()
        except Exception:
            return None
        for a in actions:
            hay = " ".join(str(a.get(k, "")) for k in ("key", "name", "type", "description")).lower()
            if "landing" in hay:
                return a.get("key")
        return actions[0].get("key") if actions else None

    def ensure_group(self, name: str = "test_group", type_: str = "campaigns") -> int:
        groups = self.list_groups(type_)
        for g in groups:
            if g.get("name") == name:
                return g["id"]
        # create
        created = self.create_group({"name": name, "position": 1, "type": type_})
        return created["id"]

    def ensure_domain(self) -> Optional[int]:
        domains = self.list_domains()
        active = [d for d in domains if d.get("state") in (None, "active")]
        if active:
            return active[0]["id"]
        return domains[0]["id"] if domains else None

    def ensure_traffic_source(self) -> Optional[int]:
        sources = self.list_traffic_sources()
        if sources:
            return sources[0]["id"]
        return None


client = KeitaroClient()