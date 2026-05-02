"""Shared pytest fixtures for hermes-rtkit tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


def _make_ctx(config_dict):
    """Create a mock PluginContext whose register() uses load_config()."""
    ctx = MagicMock()
    # ctx.config is NOT set here — register() reads from load_config() instead
    return ctx


@pytest.fixture
def mock_plugin_context():
    """Create a mock PluginContext with standard config."""
    cfg = {
        "plugins": {
            "hermes-rtkit": {
                "enabled": True,
                "verbose": False,
                "rtk_path": "rtk",
                "exclude_commands": [],
            }
        }
    }
    ctx = MagicMock()
    with patch("hermes_rtkit.plugin.load_config", return_value=cfg):
        yield ctx


@pytest.fixture
def mock_plugin_context_verbose():
    """Create a mock PluginContext with verbose=True."""
    cfg = {
        "plugins": {
            "hermes-rtkit": {
                "enabled": True,
                "verbose": True,
                "rtk_path": "rtk",
                "exclude_commands": [],
            }
        }
    }
    ctx = MagicMock()
    with patch("hermes_rtkit.plugin.load_config", return_value=cfg):
        yield ctx


@pytest.fixture
def mock_plugin_context_excluded():
    """Create a mock PluginContext with excluded commands."""
    cfg = {
        "plugins": {
            "hermes-rtkit": {
                "enabled": True,
                "verbose": False,
                "rtk_path": "rtk",
                "exclude_commands": ["git", "cargo"],
            }
        }
    }
    ctx = MagicMock()
    with patch("hermes_rtkit.plugin.load_config", return_value=cfg):
        yield ctx


@pytest.fixture
def mock_plugin_context_disabled():
    """Create a mock PluginContext with compression disabled."""
    cfg = {
        "plugins": {
            "hermes-rtkit": {
                "enabled": False,
                "verbose": False,
                "rtk_path": "rtk",
                "exclude_commands": [],
            }
        }
    }
    ctx = MagicMock()
    with patch("hermes_rtkit.plugin.load_config", return_value=cfg):
        yield ctx
