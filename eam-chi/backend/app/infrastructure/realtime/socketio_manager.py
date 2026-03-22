"""
Socket.IO Manager (Infrastructure)
====================================
Re-exports from the existing service for clean layer boundaries.
The actual implementation stays in app.services.socketio_manager
to avoid breaking existing imports.
"""
from app.services.socketio_manager import socket_manager, sio, SocketIOManager

__all__ = ["socket_manager", "sio", "SocketIOManager"]
