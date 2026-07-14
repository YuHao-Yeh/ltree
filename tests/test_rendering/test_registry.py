# tests/test_rendering/test_registry.py
from __future__ import annotations

import pytest

from ltree.rendering.base import BaseRenderer
from ltree.rendering.registry import (
    BUILTIN_RENDERERS,
    RendererRegistry,
    registry,
)


# ======================================================================= #
# Mocks & Dummies for Testing
# ======================================================================= #
class DummyRenderer(BaseRenderer):
    name = "dummy"
    aliases = ["dum", "dm"]

    def render(self, node, output_file) -> None:
        pass


class BadNameRenderer(BaseRenderer):
    name = ""
    aliases = []

    def render(self, node, output_file) -> None:
        pass


class DuplicateNameRenderer(BaseRenderer):
    name = "dummy"
    aliases = []

    def render(self, node, output_file) -> None:
        pass


class DuplicateAliasRenderer(BaseRenderer):
    name = "unique_name"
    aliases = ["dum"]

    def render(self, node, output_file) -> None:
        pass


# ======================================================================= #
# Tests: RendererRegistry
# ======================================================================= #
def test_registry_registration_success():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    assert reg.get("dummy") is DummyRenderer
    assert reg.get("dum") is DummyRenderer
    assert reg.get("dm") is DummyRenderer


def test_registry_register_missing_name():
    reg = RendererRegistry()
    with pytest.raises(ValueError) as exc_info:
        reg.register(BadNameRenderer)

    assert "BadNameRenderer has no renderer name." in str(exc_info.value)


def test_registry_register_duplicate_name():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    with pytest.raises(ValueError) as exc_info:
        reg.register(DuplicateNameRenderer)

    assert "Renderer 'dummy' already registered." in str(exc_info.value)


def test_registry_register_duplicate_alias():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    with pytest.raises(ValueError) as exc_info:
        reg.register(DuplicateAliasRenderer)

    assert "Alias 'dum' already registered." in str(exc_info.value)


def test_registry_unregister_existing():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    assert "dummy" in reg
    assert "dum" in reg

    reg.unregister("dummy")

    assert "dummy" not in reg
    assert "dum" not in reg
    assert reg.get("dummy") is None
    assert reg.get("dum") is None


def test_registry_unregister_by_alias():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    reg.unregister("dum")

    assert "dummy" not in reg
    assert "dum" not in reg


def test_registry_unregister_non_existing():
    reg = RendererRegistry()
    assert reg.unregister("non_existent") is None


def test_registry_get_fallback():
    reg = RendererRegistry()
    assert reg.get("non_existent") is None


def test_registry_names_sorting():
    reg = RendererRegistry()

    class RendererB(BaseRenderer):
        name = "b_renderer"
        aliases = ["beta"]

        def render(self, node, output_file):
            pass

    class RendererA(BaseRenderer):
        name = "a_renderer"
        aliases = ["alpha"]

        def render(self, node, output_file):
            pass

    reg.register(RendererB)
    reg.register(RendererA)

    assert reg.names() == ["a_renderer", "b_renderer"]


def test_registry_keys_sorting():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    # DummyRenderer.name = "dummy", aliases = ["dum", "dm"]
    assert reg.keys() == ["dm", "dum", "dummy"]


def test_registry_contains():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    assert "dummy" in reg
    assert "dum" in reg
    assert "non_existent" not in reg


def test_registry_iterator():
    reg = RendererRegistry()
    reg.register(DummyRenderer)

    yielded_renderers = list(reg)
    assert len(yielded_renderers) == 1
    assert yielded_renderers[0] is DummyRenderer


# ======================================================================= #
# Tests: Built-in Registry
# ======================================================================= #
def test_global_builtin_registry_populated():
    assert len(registry.names()) == len(BUILTIN_RENDERERS)

    for renderer in BUILTIN_RENDERERS:
        assert renderer.name in registry
        assert registry.get(renderer.name) is renderer
