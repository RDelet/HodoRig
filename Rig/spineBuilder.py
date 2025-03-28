"""!@Brief FK builder.
           Select joints and launch this code

from HodoRig.Core import constants as cst
from HodoRig.Rig.module import Module
from HodoRig.Rig.spineBuilder import SpineBuilder
from HodoRig.Nodes.node import Node


# ------------------------------------------
# Without Module
# ------------------------------------------

sources = Node.selected(node_type="joint")
spine_builder = SpineBuilder("L_0_Hodor", sources)
spine_builder.build()

# ------------------------------------------
# With Module
# ------------------------------------------

# Create Module
sources = Node.selected(node_type="joint")
module = Module("L_0_Hodor", sources)
module._name

# Create Fk
fk_builder = SpineBuilder()
fk_builder._settings.set(cst.kShapeScale, 300.0)
module.add_builder(fk_builder)

# Build Module
module.build()
"""

from __future__ import annotations
from typing import Optional, List

from maya import cmds

from ..Core import constants as cst
from ..Core.nameBuilder import NameBuilder
from ..Core.settings import Setting
from ..Core.context import KeepSelection
from ..Helpers.color import Color
from ..Nodes.curve import Curve
from ..Nodes.node import Node
from .rigBuilder import RigBuilder
from .manipulatorBuilder import ManipulatorBuilder


class SpineBuilder(RigBuilder):

    def __init__(self, name: Optional[str | NameBuilder] = NameBuilder(),
                 sources: Optional[List[Node]]= []):
        super().__init__(name, sources)

        self._ikh = None
        self._eff = None
        # Settings
        self._shape_dir = None
        self._shape_scale = None
        # ToDo: Add more settings

    def _init_settings(self):
        self._settings.add(Setting(cst.kShapeDirection, 0))
        self._settings.add(Setting(cst.kShapeScale, 10.0))

    def _get_settings(self):
        self._shape_dir = self._settings.value(cst.kShapeDirection)
        self._shape_scale = self._settings.value(cst.kShapeScale)
    
    def _build(self, *args, **kwargs):
        super()._build(*args, **kwargs)

        points = [jnt.position() for jnt in self._sources]
        self._build_manipulators()
        self._build_attribute()
        curve = self._build_curve(points)
        self._skin_curve(curve)
        self._create_handle(curve)
        self._add_stretch(curve, points)
    
    def _build_manipulators(self):

        spine_manip = ManipulatorBuilder("spine")
        spine_manip.build(self._parent_grp, shape="circle",
                          shape_dir=self._shape_dir,
                          scale=self._shape_scale, color=cst.kYellow)
        spine_manip.reset.snap(self._sources[0])
        self._manipulators.append(spine_manip.node)

        hips_manip = ManipulatorBuilder("hips")
        hips_manip.build(spine_manip.node, shape="circle",
                         shape_dir=self._shape_dir,
                         scale=self._shape_scale * 0.75, color=cst.kYellow)
        self._manipulators.append(hips_manip.node)
        
        chest_manip = ManipulatorBuilder("chest")
        chest_manip.build(spine_manip.node, shape="circle",
                          shape_dir=self._shape_dir,
                          scale=self._shape_scale, color=cst.kYellow)
        chest_manip.reset.snap(self._sources[-1])
        self._manipulators.append(chest_manip.node)
    
    def _build_attribute(self):
        root_manipulator = self._manipulators[0]
        root_manipulator.add_settings_attribute("spineSettings")
        root_manipulator.add_attribute(cst.kStretch, cst.kFloat, keyable=True, min=0.0, max=1.0)
        proxy_attr = f"{root_manipulator}.{cst.kStretch}"
        for manipulator in self._manipulators[1:]:
            manipulator.add_settings_attribute("spineSettings")
            manipulator.add_attribute(cst.kStretch, cst.kFloat,
                                      keyable=True, min=0.0, max=1.0, proxy=proxy_attr)
    
    def _build_curve(self, points: List) -> Curve:
        curve = Curve.create_from_points(f"NC_{self.name}", points)
        transform = curve.parent
        transform.set_attribute(cst.kInheritsTransform, False)

        return curve
        # ToDo: Reshape 0 to 1 ?
    
    def _skin_curve(self, curve: Curve):
        jnts = []
        for manipulator in self._manipulators[1:]:
            jnt = Node.create(cst.kJoint, f"SK_{manipulator.short_name}", parent=manipulator)
            jnts.append(jnt)
        
        with KeepSelection():
            cmds.select(jnts)
            cmds.skinCluster(jnts, curve.name, toSelectedBones=True, skinMethod=0)[0]
    
    def _create_handle(self, curve: Curve):
        ikh, eff = cmds.ikHandle(startJoint=self._sources[0], endEffector=self._sources[-1],
                                 curve=curve.name, solver=cst.kIkSplineSolver,
                                 createCurve=False, parentCurve=False)
        self._eff = Node.get(eff)
        self._eff.rename(f"EFF_{self.name}")
        self._ikh = Node.get(ikh)
        self._eff.rename(f"IKH_{self.name}")

        self._ikh.set_attribute(cst.kVisibility, False)
        self._ikh.set_attribute(cst.kDTwistControlEnable, 1)
        self._ikh.set_attribute(cst.kDWorldUpType, 4)
        self._ikh.set_attribute(cst.kDForwardAxis, 2)
        self._ikh.set_attribute(cst.kDWorldUpAxis, 6)
        self._ikh.set_attribute(cst.kDWorldUpVector, [1, 0, 0])
        self._ikh.set_attribute(cst.kDWorldUpVectorEnd, [1, 0, 0])
        self._manipulators[1].connect_to(f"{cst.kWorldMatrix}[0]", f"{self._ikh}.{cst.kDWorldUpMatrix}")
        self._manipulators[-1].connect_to(f"{cst.kWorldMatrix}[0]", f"{self._ikh}.{cst.kDWorldUpMatrixEnd}")

    def _add_stretch(self, curve: Curve, points: List):
        prev_poci = None
        for i, (jnt, point) in enumerate(zip(self._sources, points)):
            parameter = curve.param_at_point(point)
            poci = curve.create_poci(parameter, f"POCI_{jnt.short_name}")
            if i == 0:
                prev_poci = poci
                continue

            jnt_dir = (jnt.position() - self._sources[i - 1].position())
            distance = jnt_dir.length()
            jnt_dir.normalize()

            db = Node.create(cst.kDistanceBetween, f"DB_{jnt.short_name}")
            prev_poci.connect_to(cst.kPosition, f"{db}.{cst.kPoint1}")
            poci.connect_to(cst.kPosition, f"{db}.{cst.kPoint2}")

            bta = Node.create(cst.kBlendTwoAttr, f"BTA_{jnt.short_name}")
            bta.set_attribute(f"{cst.kInput}[0]", distance)
            db.connect_to(cst.kDistance, f"{bta}.{cst.kInput}[1]")
            self._manipulators[0].connect_to(cst.kStretch, f"{bta}.{cst.kAttributesBlender}")

            md = Node.create(cst.kMultiplyDivide, f"MD_{jnt.short_name}")
            bta.connect_to(cst.kOutput, f"{md}.{cst.kInput1X}")
            bta.connect_to(cst.kOutput, f"{md}.{cst.kInput1Y}")
            bta.connect_to(cst.kOutput, f"{md}.{cst.kInput1Z}")
            md.set_attribute(cst.kInput2, [jnt_dir.x, jnt_dir.y, jnt_dir.z])
            md.connect_to(cst.kOutput, f"{jnt}.{cst.kTranslate}")

            prev_poci = poci
