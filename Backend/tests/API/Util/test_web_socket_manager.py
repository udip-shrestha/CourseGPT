import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, call

from API.Util.web_socket_manager import WebSocketManager


def fake_ws():
    ws = MagicMock()
    ws.send_json = AsyncMock()
    ws.accept = AsyncMock()
    ws.receive_text = AsyncMock()
    return ws


def test_subscribe_and_unsubscribe():
    mgr = WebSocketManager()
    ws = fake_ws()

    mgr.subscribe("topic1", ws)
    assert mgr.topics["topic1"] == [ws]

    mgr.unsubscribe("topic1", ws)
    assert mgr.topics["topic1"] == []


def test_publish_sends_json_to_all():
    mgr = WebSocketManager()
    ws1 = fake_ws()
    ws2 = fake_ws()

    mgr.subscribe("topic", ws1)
    mgr.subscribe("topic", ws2)

    message = {"text": "hello"}

    mgr.publish("topic", message)

    ws1.send_json.assert_awaited_once_with(message)
    ws2.send_json.assert_awaited_once_with(message)


def test_publish_removes_dead_websockets():
    mgr = WebSocketManager()

    alive_ws = fake_ws()
    dead_ws = fake_ws()
    dead_ws.send_json.side_effect = Exception("network failure")

    mgr.subscribe("chat", alive_ws)
    mgr.subscribe("chat", dead_ws)

    mgr.publish("chat", {"msg": "ping"})

    # Alive socket should work
    alive_ws.send_json.assert_awaited_once()

    # Dead socket send_json should have been called but raised
    dead_ws.send_json.assert_awaited_once()

    # Dead socket removed from subscribers
    assert mgr.topics["chat"] == [alive_ws]


@pytest.mark.asyncio
async def test_handle_subscription_lifecycle():
    mgr = WebSocketManager()
    ws = fake_ws()

    # Simulate one message then disconnect
    ws.receive_text.side_effect = [
        "hello world",
        Exception("disconnect")
    ]

    await mgr.handle_subscription("updates", ws)

    # Accept should be called
    ws.accept.assert_awaited_once()

    # Subscribe should register the socket
    # but after disconnect, ws should be removed
    assert "updates" in mgr.topics
    assert ws not in mgr.topics["updates"]

    # First receive_text should have been awaited
    ws.receive_text.assert_awaited()


@pytest.mark.asyncio
async def test_handle_subscription_disconnect_cleanup():
    mgr = WebSocketManager()
    ws = fake_ws()

    from fastapi import WebSocketDisconnect

    ws.receive_text.side_effect = WebSocketDisconnect()

    await mgr.handle_subscription("chat-room", ws)

    ws.accept.assert_awaited_once()
    assert ws not in mgr.topics["chat-room"]
