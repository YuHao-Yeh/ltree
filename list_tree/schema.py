from dataclasses import dataclass

@dataclass
class Stats:
    visible_dirs: int = 0
    visible_files: int = 0
    hidden_dirs: int = 0
    hidden_files: int = 0