# HodoRig
Auto rig for maya

# Build Exemple

## Create Module
The module is a class that allows you to serialize a builder suite in json (ToDo)

```python
from HodoRig.Rig.module import Module
from HodoRig.Nodes.node import Node

sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)
```

## Create Builder
A builder is a class used to separate construction processes (pre_build, build, post_build).
In rig they allow you to build setup elements like fk, ik, footRoll, etc.

```python
from HodoRig.Rig.ikBuilder import IKBuilder

ik_builder = IKBuilder()
module.add_builder(ik_builder)
```

When you add a builder to a module, it automatically takes the module sources as well as the name to which it adds the name of the builder class.
Exemple:
- Module -> M_0_Hodor
- Builder -> M_0_HodorIK

## Build Module

```python
module.build()
```

# Ik / FK blend exemple
It is possible to add builders to an another builder. I call it sub builders.
This allows, for example, to add an FK and IK builder to a blend builder. The builder blend will allow you to go from one to the other through an attribute.

```python
from HodoRig.Rig.module import Module
from HodoRig.Rig.fkBuilder import FKBuilder
from HodoRig.Rig.ikBuilder import IKBuilder
from HodoRig.Rig.blendBuilder import BlendBuilder
from HodoRig.Nodes.node import Node

# Create Module
sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)

# Create blender
blend_builder = BlendBuilder()
blend_builder._settings.set("blendName", "ikFkBlend")
module.add_builder(blend_builder)

# Create Ik
ik_builder = IKBuilder()
blend_builder.add_children(ik_builder)

# Create Fk
fk_builder = FKBuilder()
fk_builder._settings.set("shapeScale", 1.0)
blend_builder.add_children(fk_builder)

# Build Module
module.build()
```

# Builder only exemple
However, it is possible to use the builder without a module

```python
from HodoRig.Rig.ikBuilder import IKBuilder
from HodoRig.Nodes.node import Node

sources = Node.selected(node_type="joint")
ik_builder = IKBuilder("L_0_Hodor", sources)
ik_builder.build()
```