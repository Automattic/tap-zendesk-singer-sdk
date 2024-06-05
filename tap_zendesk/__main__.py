"""Zendesk entry point."""

from __future__ import annotations

from tap_zendesk.tap import TapZendesk

TapZendesk.cli()
