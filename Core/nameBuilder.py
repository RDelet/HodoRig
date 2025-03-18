from __future__ import annotations

import re

from typing import Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class NameBuilder:
    
    rgx_clean_path = re.compile(r'[^|:\/\\]+$')

    type: Optional[str] = None
    side: Optional[str] = None
    index: Optional[int] = None
    prefix: Optional[str] = None
    core: Optional[str] = None
    suffix: Optional[str] = None
    
    kType = 'type'
    kSide = 'side'
    kIndex = 'index'
    kPrefix = 'prefix'
    kCore = 'core'
    kSuffix = 'suffix'
    
    kMirror = {'L': 'R', 'M': 'M', 'R': 'L'}
    kSeparator = "_"
    kTemplateFull = [kType, kSide, kIndex, kPrefix, kCore, kSuffix]
    kTemplate = [kType, kSide, kIndex, kCore]
    kUntypedTemplate = [kSide, kIndex, kCore]
    kSimple = [kCore, kSide]
    kTemplates = [kTemplateFull, kTemplate, kUntypedTemplate, kSimple]

    def __str__(self) -> str:
        d = self.to_dict()
        v = [str(d[x]) for x in self.kTemplate if d[x] is not None]
        return self.kSeparator.join(v)

    def clone(self, **kwargs):
        d = self.to_dict()
        d.update(kwargs)
        return NameBuilder(**d)

    @classmethod
    def from_name(cls, name: str) -> NameBuilder:
        match  = cls.rgx_clean_path.search(name)
        name = match.group(0) if match else name
        
        split = name.split(cls.kSeparator)
        split_count = len(split)

        for t in cls.kTemplates:
            if split_count != len(t):
                continue

            if cls.kIndex in t:
                index_id = t.index(cls.kIndex)
                if not split_count[index_id].isnumeric():
                    continue
                split_count[index_id] = int(split_count[index_id])

            return cls(**{t[i]: split[i] for i in range(len(t))})

        return cls(core=name)
    
    def mirror(self) -> NameBuilder:
        if self.side and self.side in self.kMirror:
            self.side = self.kMirror[self.side]

    def to_dict(self) -> dict:
        return asdict(self)