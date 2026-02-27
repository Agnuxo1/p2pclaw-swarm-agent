"""
P2PCLAW Swarm Agent — Autonomous swarm intelligence & collective behavior research.
Operates 24/7 on GitHub Actions using free HuggingFace Inference API.
"""

import os
import random
import threading
import time
import asyncio
import traceback
from datetime import datetime, timezone
from typing import Callable, Optional, List

from p2p import P2PClient

# ── Agent identity ──────────────────────────────────────────────────────────────
AGENT_ID = os.getenv("AGENT_ID", "p2pclaw-swarm-agi")
AGENT_NAME = os.getenv("AGENT_NAME", "P2PCLAW Swarm Agent")
AGENT_INTERESTS = (
    "swarm intelligence, collective behavior, emergent systems, flocking algorithms, "
    "multi-agent systems, distributed problem solving, ant colonies, bird flocks, "
    "cellular automata, consensus mechanisms, DAO governance, self-organizing systems"
)

# ── HuggingFace tokens ───────────────────────────────────────────────────────────
HF_TOKEN = os.getenv("HF_TOKEN")
HF_TOKENS = [HF_TOKEN] if HF_TOKEN else []
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct")
HF_BASE_URL = "https://api-inference.huggingface.co/models"

class HFLLMClient:
    def __init__(self, token: str, model: str):
        self.token = token
        self.model = model
    
    async def complete(self, messages: list, max_tokens: int = 2000):
        import httpx
        url = f"{HF_BASE_URL}/{self.model}/v1/chat/completions"
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {"model": self.model, "messages": messages, "max_tokens": max_tokens}
        
        async with httpx.AsyncClient() as client:
            r = await client.post(url, headers=headers, json=payload, timeout=60.0)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]

class P2PCLAWSwarmAgent:
    def __init__(self):
        self.agent_id = AGENT_ID
        self.agent_name = AGENT_NAME
        self.client = P2PClient(self.agent_id, self.agent_name)
        self.llm = HFLLMClient(HF_TOKEN, HF_MODEL) if HF_TOKEN else None
        self.running = False

    async def start(self):
        self.running = True
        logger.info(f"Starting {self.agent_name}...")
        await self._announce()
        
        await asyncio.gather(
            self._heartbeat_loop(),
            self._research_loop()
        )

    async def _announce(self):
        try:
            self.client.chat(f"[{self.agent_name} Online] Swarm intelligence researcher joining the hive.")
        except: pass

    async def _heartbeat_loop(self):
        while self.running:
            try:
                self.client.register(interests=AGENT_INTERESTS)
            except: pass
            await asyncio.sleep(60)

    async def _research_loop(self):
        while self.running:
            try:
                if self.llm:
                    logger.info("Starting swarm research...")
                    prompt = "Generate a brief technical note on emergent swarm intelligence in decentralized networks."
                    content = await self.llm.complete([{"role": "user", "content": prompt}])
                    
                    self.client.publish_paper({
                        "title": f"Swarm Intelligence Analysis: {datetime.now().isoformat()}",
                        "content": content,
                        "author": self.agent_name,
                        "agentId": self.agent_id
                    })
            except Exception as e:
                logger.error(f"Swarm loop error: {e}")
            await asyncio.sleep(1800)

    def stop(self):
        self.running = False

async def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    global logger
    logger = logging.getLogger(__name__)
    
    agent = P2PCLAWSwarmAgent()
    duration = int(os.getenv("RUN_DURATION", "19800")) 
    start_ts = time.time()
    
    agent_task = asyncio.create_task(agent.start())
    
    while time.time() - start_ts < duration:
        await asyncio.sleep(60)
            
    print("\nRun duration reached. Shutting down...")
    agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
