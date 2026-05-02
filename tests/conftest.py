"""Shared pytest fixtures for hermes-rtkit tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_plugin_context():
    """Create a mock PluginContext with standard config."""
    ctx = MagicMock()
    ctx.config = {
        "enabled": True,
        "verbose": False,
        "rtk_path": "rtk",
        "exclude_commands": [],
    }
    return ctx


@pytest.fixture
def mock_plugin_context_verbose():
    """Create a mock PluginContext with verbose=True."""
    ctx = MagicMock()
    ctx.config = {
        "enabled": True,
        "verbose": True,
        "rtk_path": "rtk",
        "exclude_commands": [],
    }
    return ctx


@pytest.fixture
def mock_plugin_context_excluded():
    """Create a mock PluginContext with excluded commands."""
    ctx = MagicMock()
    ctx.config = {
        "enabled": True,
        "verbose": False,
        "rtk_path": "rtk",
        "exclude_commands": ["git", "cargo"],
    }
    return ctx


@pytest.fixture
def mock_plugin_context_disabled():
    """Create a mock PluginContext with compression disabled."""
    ctx = MagicMock()
    ctx.config = {
        "enabled": False,
        "verbose": False,
        "rtk_path": "rtk",
        "exclude_commands": [],
    }
    return ctx
