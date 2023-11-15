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
    kTemplate = [kType, kSide, kIndex, kPrefix, kCore, kSuffix]

    def __str__(self) -> str:
        d = self.to_dict()
        v = [str(d[x]) for x in self.kTemplate if d[x] is not None]
        return self.kSeparator.join(v)

    def clone(self, **kwargs):
        d = self.to_dict()
        d.update(kwargs)
        return NameBuilder(*d)
    
    @classmethod
    def from_name(cls, name: str) -> NameBuilder:
        count = len(cls.kTemplate)
        split = name.split(cls.kSeparator)
        if len(split) != count:
            return cls(core=name)
        
        new_cls = cls()
        new_cls.__dict__.update({cls.kTemplate[i]: split[i] for i in range(count)})
        if new_cls.index is not None:
            new_cls.index = int(new_cls.index)
        
        return new_cls
    
    def mirror(self) -> NameBuilder:
        if self.side and self.side in self.kMirror:
            self.side = self.kMirror[self.side]

    def to_dict(self) -> dict:
        return asdict(self)