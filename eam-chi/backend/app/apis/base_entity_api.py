"""Backward-compatible re-export. Canonical location: application/services/base_entity_api.py"""
from app.application.services.base_entity_api import BaseEntityAPI, Context  # noqa: F401

__all__ = ["BaseEntityAPI", "Context"]
