import asyncio
import logging
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List


logger = logging.getLogger(__name__)


class WebSocketManager:

    def __init__(self):
        # Maps: topic -> list of WebSockets
        self.topics: Dict[str, List[WebSocket]] = {}
        logger.info("[WSManager] Initialized WebSocketManager")

    def subscribe(self, topic: str, websocket: WebSocket):
        """Subscribe a WebSocket to a given topic string."""
        self.topics.setdefault(topic, []).append(websocket)
        logger.info(f"[WSManager] Subscribed WS id={id(websocket)} to topic='{topic}'. Total subscribers on topic: {len(self.topics[topic])}")

    def unsubscribe(self, topic: str, websocket: WebSocket):
        """Unsubscribe WebSocket from a given topic."""
        if topic in self.topics and websocket in self.topics[topic]:
            self.topics[topic].remove(websocket)
            logger.info(f"[WSManager] Unsubscribed WS id={id(websocket)} from topic='{topic}'. Remaining subscribers: {len(self.topics[topic])}")
        else:
            logger.warning(f"[WSManager] Attempted to unsubscribe WS id={id(websocket)} from topic='{topic}', but it was not found.")

    def publish(self, topic: str, message: dict):
        """Publish a JSON message to all subscribers of a topic."""
        subscribers = list(self.topics.get(topic, []))  # snapshot
        if not subscribers:
            return

        dead_ws = []  # collect failed sockets

        async def _publish_to_websocket(ws: WebSocket, message: dict):
            try:
                await ws.send_json(message)
            except:
                dead_ws.append(ws)
  
        async def _broadcast(): 
            await asyncio.gather(*(_publish_to_websocket(ws, message) for ws in subscribers), return_exceptions=True)

             # Now safely clean up dead websockets *after* broadcasting
            if dead_ws:
                alive_list = self.topics.get(topic, [])
                for ws in dead_ws:
                    if ws in alive_list:
                        alive_list.remove(ws)

        logger.info(f"[WSManager] Publishing to topic='{topic}' subscriber_count={len(subscribers)} message={message}")
        asyncio.run(_broadcast())

    async def handle_subscription(self, topic: str, websocket: WebSocket):
        """
        Accept, subscribe, keep alive, auto-unsubscribe on disconnect.
        """
        logger.info(f"[WSManager] New subscription request ws_id={id(websocket)} topic='{topic}'")
   
        await websocket.accept()
        self.subscribe(topic, websocket)

        try:
            while True:
                data = await websocket.receive_text()
                logger.info(f"[WSManager] Received message on ws_id={id(websocket)} topic='{topic}' data='{data}' (ignored)")
        except WebSocketDisconnect:
            logger.info(f"[WSManager] WSDisconnect ws_id={id(websocket)} topic='{topic}'")
        except Exception as e:
            logger.error(f"[WSManager] Error on ws_id={id(websocket)} topic='{topic}': {e}")
        finally:
            self.unsubscribe(topic, websocket)
            logger.info(f"[WSManager] Cleanup complete ws_id={id(websocket)} topic='{topic}'")
