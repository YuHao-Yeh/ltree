from dataclasses import dataclass, field


@dataclass(slots=True)
class Stats:
    visible_dirs: int = 0
    visible_files: int = 0
    hidden_dirs: int = 0
    hidden_files: int = 0

    @property
    def total_dirs(self) -> int:
        return self.visible_dirs + self.hidden_dirs

    @property
    def total_files(self) -> int:
        return self.visible_files + self.hidden_files


@dataclass(slots=True)
class TreeNode:
    name: str
    is_dir: bool
    path: str
    size: int = 0
    children: list["TreeNode"] = field(default_factory=list)
    stats: Stats = field(default_factory=Stats)
    is_truncated: bool = False
