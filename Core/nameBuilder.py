from __future__ import annotations

from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class NameBuilder:
    
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
    kTemplates = [kTemplateFull, kTemplate, kUntypedTemplate]

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
        split = name.split(cls.kSeparator)
        split_count = len(split)

        template = None
        count = 0
        for t in cls.kTemplates:
            tc = len(t)
            if split_count == tc:
                template = t
                count = tc
                break

        if not template:
            return cls(core=name)
        
        new_cls = cls()
        new_cls.__dict__.update({template[i]: split[i] for i in range(count)})
        if new_cls.index is not None:
            new_cls.index = int(new_cls.index)
        
        return new_cls
    
    def mirror(self) -> NameBuilder:
        if self.side and self.side in self.kMirror:
            self.side = self.kMirror[self.side]

    def to_dict(self) -> dict:
        return asdict(self)