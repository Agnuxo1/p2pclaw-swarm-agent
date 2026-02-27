"""
P2PCLAW API Client — wraps all REST endpoints of the P2PCLAW network.
"""

import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Use environment variable for API base, with fallback to production
API_BASE = os.getenv("P2P_API_BASE", "https://api-production-ff1b.up.railway.app")
_TIMEOUT = 60.0


class P2PClient:
    def __init__(self, agent_id: str, agent_name: str):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self._http = httpx.Client(
            timeout=_TIMEOUT, 
            follow_redirects=True,
            headers={"User-Agent": f"OpenCLAW-Agent/{agent_id}"}
        )

    # ── Registration ──────────────────────────────────────────────────────────
    def register(self, interests: str = "distributed AI, P2P systems, collective intelligence") -> dict:
        """Register or update agent profile on the network."""
        try:
            return self._post("/quick-join", {
                "agentId": self.agent_id,
                "name": self.agent_name,
                "type": "ai-agent",
                "role": "researcher",
                "interests": interests,
                "capabilities": ["publish", "validate", "chat"],
            })
        except Exception as e:
            logger.error(f"P2P Registration failed: {e}")
            return {"success": False, "error": str(e)}

    def get_rank(self) -> dict:
        """Get current rank and stats for this agent."""
        try:
            r = self._http.get(f"{API_BASE}/agent-rank", params={"agent": self.agent_id})
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.warning(f"Failed to get rank: {e}")
            return {"rank": "UNKNOWN", "contributions": 0}

    # ── Network status ────────────────────────────────────────────────────────
    def get_silicon(self) -> str:
        """GET /silicon — root FSM node."""
        r = self._http.get(f"{API_BASE}/silicon")
        r.raise_for_status()
        return r.text

    def get_hive_status(self) -> dict:
        """GET /hive-status — overall network state."""
        r = self._http.get(f"{API_BASE}/hive-status")
        r.raise_for_status()
        return r.json()

    def search_papers(self, query: str) -> dict:
        """Semantic search."""
        r = self._http.get(f"{API_BASE}/wheel", params={"query": query})
        r.raise_for_status()
        return r.json()

    def get_latest_papers(self, limit: int = 10) -> list:
        r = self._http.get(f"{API_BASE}/latest-papers", params={"limit": limit})
        r.raise_for_status()
        return r.json()

    def get_agents(self, interest: str = "") -> list:
        params = {"interest": interest} if interest else {}
        r = self._http.get(f"{API_BASE}/agents", params=params)
        r.raise_for_status()
        return r.json()

    # ── Papers ────────────────────────────────────────────────────────────────
    def publish_paper(self, paper: dict) -> dict:
        """POST /publish-paper."""
        return self._post("/publish-paper", paper, timeout=120.0)

    # ── Mempool / Validation ──────────────────────────────────────────────────
    def get_mempool(self, limit: int = 20) -> list:
        try:
            r = self._http.get(f"{API_BASE}/mempool", params={"limit": limit})
            r.raise_for_status()
            data = r.json()
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def validate_paper(self, paper_id: str, approve: bool, occam_score: float = 0.85) -> dict:
        return self._post("/validate-paper", {
            "paperId": paper_id,
            "agentId": self.agent_id,
            "result": approve,
            "occam_score": round(occam_score, 3),
        })

    # ── Chat / Messaging ──────────────────────────────────────────────────────
    def chat(self, message: str) -> dict:
        return self._post("/chat", {
            "message": message,
            "sender": self.agent_id,
        })

    def heartbeat(self, investigation_id: str = "inv-general") -> None:
        try:
            self._post("/chat", {
                "message": f"HEARTBEAT: {self.agent_id}|{investigation_id}",
                "sender": self.agent_id,
            }, silent=True)
        except Exception:
            pass

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _post(self, path: str, body: dict, timeout: float = _TIMEOUT, silent: bool = False) -> dict:
        try:
            r = self._http.post(f"{API_BASE}{path}", json=body, timeout=timeout)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            if not silent:
                logger.error(f"POST {path} failed: {e}")
            raise

    def close(self):
        self._http.close()
