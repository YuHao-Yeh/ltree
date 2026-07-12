# ltree/core/scanners/filters.py
from __future__ import annotations

from typing import Protocol

from ltree.core.scanners.models import FilterContext


class NodeFilter(Protocol):
    def should_exclude(self, ctx: FilterContext) -> bool: ...


# ----------------------------------------------------------------------
class ForceIncludeFilter:
    def should_exclude(self, ctx: FilterContext) -> bool:
        return False


# ----------------------------------------------------------------------
class GitignoreFilter:
    def should_exclude(self, ctx: FilterContext) -> bool:
        spec = ctx.config.gitignore_spec
        if spec is None:
            return False

        rel = f"{ctx.rel_path}/" if ctx.is_dir else ctx.rel_path

        return spec.match_file(rel)


class RegexFilter:
    def should_exclude(self, ctx: FilterContext) -> bool:
        patterns = ctx.config.regex_exclude_patterns
        if not patterns:
            return False

        return any(r.search(ctx.rel_path) for r in patterns)


class RuleFilter:
    def should_exclude(self, ctx: FilterContext) -> bool:
        return ctx.config.exclude.matches(
            ctx.rel_path,
            ctx.name,
        )


class HiddenFilter:
    def should_exclude(self, ctx: FilterContext) -> bool:
        if ctx.config.show_all:
            return False

        return ctx.name.startswith(".")


# ----------------------------------------------------------------------
class CompositeFilter:
    def __init__(self, filters: list[NodeFilter] | None = None):
        self.filters: list[NodeFilter] = filters or [
            HiddenFilter(),
            RuleFilter(),
            RegexFilter(),
            GitignoreFilter(),
        ]

    def should_exclude(self, ctx: FilterContext) -> bool:
        if ctx.config.include.matches(ctx.rel_path, ctx.name):
            return False

        return any(f.should_exclude(ctx) for f in self.filters)
