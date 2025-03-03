//Maya ASCII 2022 scene
//Name: elasticskin.ma
//Last modified: Wed, Feb 05, 2025 08:53:02 AM
//Codeset: 1252
requires maya "2022";
currentUnit -linear centimeter -angle degree -time ntsc;
fileInfo "application" "maya";
fileInfo "product" "Maya 2022";
fileInfo "version" "2022";
fileInfo "cutIdentifier" "202405021833-753375ecb3";
fileInfo "osv" "Windows 10 Enterprise v2009 (Build: 19045)";
fileInfo "UUID" "5366DEAE-49E4-7C9D-F919-C28CF3312F08";
createNode transform -shared -name "persp";
	rename -uuid "00CB7502-42F4-BB80-1AF8-55ACE1278FE4";
	setAttr ".visibility" no;
	setAttr ".translate" -type "double3" 0.76249707044967552 3.3462793005548273 0.56949959334589995 ;
	setAttr ".rotate" -type "double3" -66.938352729574319 7.8000000000009697 8.0256412165129474e-16 ;
createNode camera -shared -name "perspShape" -parent "persp";
	rename -uuid "5B019699-44CB-5E31-63F7-9699481CE5C2";
	setAttr -keyable off ".visibility" no;
	setAttr ".focalLength" 34.999999999999993;
	setAttr ".centerOfInterest" 3.6012990626088168;
	setAttr ".imageName" -type "string" "persp";
	setAttr ".depthName" -type "string" "persp_depth";
	setAttr ".maskName" -type "string" "persp_mask";
	setAttr ".homeCommand" -type "string" "viewSet -p %camera";
createNode transform -shared -name "top";
	rename -uuid "45F8C1C0-45B7-080E-802B-B38536410451";
	setAttr ".visibility" no;
	setAttr ".translate" -type "double3" 0 1000.1 0 ;
	setAttr ".rotate" -type "double3" -90 0 0 ;
createNode camera -shared -name "topShape" -parent "top";
	rename -uuid "39DFA878-40C2-ED24-580F-A497E93CE269";
	setAttr -keyable off ".visibility" no;
	setAttr ".renderable" no;
	setAttr ".centerOfInterest" 1000.1;
	setAttr ".orthographicWidth" 30;
	setAttr ".imageName" -type "string" "top";
	setAttr ".depthName" -type "string" "top_depth";
	setAttr ".maskName" -type "string" "top_mask";
	setAttr ".homeCommand" -type "string" "viewSet -t %camera";
	setAttr ".orthographic" yes;
createNode transform -shared -name "front";
	rename -uuid "F3AB3AC6-4C13-7FE4-E002-37B6225935DF";
	setAttr ".visibility" no;
	setAttr ".translate" -type "double3" 0 0 1000.1 ;
createNode camera -shared -name "frontShape" -parent "front";
	rename -uuid "E3F52A50-4C06-8F5A-D145-768F823DEB6C";
	setAttr -keyable off ".visibility" no;
	setAttr ".renderable" no;
	setAttr ".centerOfInterest" 1000.1;
	setAttr ".orthographicWidth" 30;
	setAttr ".imageName" -type "string" "front";
	setAttr ".depthName" -type "string" "front_depth";
	setAttr ".maskName" -type "string" "front_mask";
	setAttr ".homeCommand" -type "string" "viewSet -f %camera";
	setAttr ".orthographic" yes;
createNode transform -shared -name "side";
	rename -uuid "7991F044-4CCE-D1BE-C591-A38ACEB455AC";
	setAttr ".visibility" no;
	setAttr ".translate" -type "double3" 1000.1 0 0 ;
	setAttr ".rotate" -type "double3" 0 90 0 ;
createNode camera -shared -name "sideShape" -parent "side";
	rename -uuid "66C18B20-4A18-D412-429C-6D81CEEF77FE";
	setAttr -keyable off ".visibility" no;
	setAttr ".renderable" no;
	setAttr ".centerOfInterest" 1000.1;
	setAttr ".orthographicWidth" 30;
	setAttr ".imageName" -type "string" "side";
	setAttr ".depthName" -type "string" "side_depth";
	setAttr ".maskName" -type "string" "side_mask";
	setAttr ".homeCommand" -type "string" "viewSet -s %camera";
	setAttr ".orthographic" yes;
createNode transform -name "pPlane1";
	rename -uuid "3610B68F-4F65-6107-A45E-F198DC0F6FED";
	setAttr -lock on ".translateX";
	setAttr -lock on ".translateY";
	setAttr -lock on ".translateZ";
	setAttr -lock on ".rotateX";
	setAttr -lock on ".rotateY";
	setAttr -lock on ".rotateZ";
	setAttr -lock on ".scaleX";
	setAttr -lock on ".scaleY";
	setAttr -lock on ".scaleZ";
createNode mesh -name "pPlaneShape1" -parent "pPlane1";
	rename -uuid "52297135-41A3-2498-2570-B097C5F74FA4";
	setAttr -keyable off ".visibility";
	setAttr ".visibleInReflections" yes;
	setAttr ".visibleInRefractions" yes;
	setAttr ".uvPivot" -type "double2" 0.5 1 ;
	setAttr ".uvSet[0].uvSetName" -type "string" "map1";
	setAttr ".currentUVSet" -type "string" "map1";
	setAttr ".displayColorChannel" -type "string" "Ambient+Diffuse";
	setAttr ".collisionOffsetVelocityMultiplier[0]"  0 1 1;
	setAttr ".collisionDepthVelocityMultiplier[0]"  0 1 1;
	setAttr ".vertexColorSource" 2;
createNode mesh -name "pPlaneShape1Orig" -parent "pPlane1";
	rename -uuid "4BB85D85-4895-86D8-880A-0182EC5AFCBC";
	setAttr -keyable off ".visibility";
	setAttr ".intermediateObject" yes;
	setAttr ".visibleInReflections" yes;
	setAttr ".visibleInRefractions" yes;
	setAttr -size 5 ".componentTags";
	setAttr ".componentTags[0].componentTagName" -type "string" "back";
	setAttr ".componentTags[0].componentTagContents" -type "componentList" 1 "e[3]";
	setAttr ".componentTags[1].componentTagName" -type "string" "front";
	setAttr ".componentTags[1].componentTagContents" -type "componentList" 1 "e[0]";
	setAttr ".componentTags[2].componentTagName" -type "string" "left";
	setAttr ".componentTags[2].componentTagContents" -type "componentList" 1 "e[1]";
	setAttr ".componentTags[3].componentTagName" -type "string" "right";
	setAttr ".componentTags[3].componentTagContents" -type "componentList" 1 "e[2]";
	setAttr ".componentTags[4].componentTagName" -type "string" "rim";
	setAttr ".componentTags[4].componentTagContents" -type "componentList" 1 "e[0:3]";
	setAttr ".uvSet[0].uvSetName" -type "string" "map1";
	setAttr -size 4 ".uvSet[0].uvSetPoints[0:3]" -type "float2" 0 0 1
		 0 0 1 1 1;
	setAttr ".currentUVSet" -type "string" "map1";
	setAttr ".displayColorChannel" -type "string" "Ambient+Diffuse";
	setAttr ".collisionOffsetVelocityMultiplier[0]"  0 1 1;
	setAttr ".collisionDepthVelocityMultiplier[0]"  0 1 1;
	setAttr -size 4 ".pnts[0:3]" -type "float3"  0.5 0 -0.5 0.5 0 -0.5 
		0.5 0 -0.5 0.5 0 -0.5;
	setAttr -size 4 ".vrts[0:3]"  -0.5 0 0.5 0.5 0 0.5 -0.5 0 -0.5 0.5 0 -0.5;
	setAttr -size 5 ".edge[0:4]"  0 1 0 0 2 0 1 3 0 2 3 0 0 3 1;
	setAttr -size 2 -capacityHint 6 ".face[0:1]" -type "polyFaces" 
		f 3 4 -4 -2
		mu 0 3 0 3 2
		f 3 0 2 -5
		mu 0 3 0 1 3;
	setAttr ".creaseData" -type "dataPolyComponent" Index_Data Edge 0 ;
	setAttr ".creaseVertexData" -type "dataPolyComponent" Index_Data Vertex 0 ;
	setAttr ".pinData[0]" -type "dataPolyComponent" Index_Data UV 0 ;
	setAttr ".holeFaceData" -type "dataPolyComponent" Index_Data Face 0 ;
createNode joint -name "joint1";
	rename -uuid "268B1819-45E2-443F-ACAD-4CAE09EDD2F8";
	addAttr -cachedInternally true -shortName "liw" -longName "lockInfluenceWeights" 
		-minValue 0 -maxValue 1 -attributeType "bool";
	setAttr ".useObjectColor" 1;
	setAttr ".minRotLimit" -type "double3" -360 -360 -360 ;
	setAttr ".maxRotLimit" -type "double3" 360 360 360 ;
	setAttr ".bindPose" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr ".radius" 0.1;
createNode joint -name "joint2";
	rename -uuid "E681E313-4DBC-1ABF-F972-E28C70743FA6";
	addAttr -cachedInternally true -shortName "liw" -longName "lockInfluenceWeights" 
		-minValue 0 -maxValue 1 -attributeType "bool";
	setAttr ".translate" -type "double3" 0 0 -1 ;
	setAttr ".minRotLimit" -type "double3" -360 -360 -360 ;
	setAttr ".maxRotLimit" -type "double3" 360 360 360 ;
	setAttr ".bindPose" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 -1 1;
	setAttr ".radius" 0.1;
createNode joint -name "joint3";
	rename -uuid "E6B6E68A-4F37-4238-B4D0-F1A1BCBD3107";
	addAttr -cachedInternally true -shortName "liw" -longName "lockInfluenceWeights" 
		-minValue 0 -maxValue 1 -attributeType "bool";
	setAttr ".translate" -type "double3" 1 0 -1 ;
	setAttr ".minRotLimit" -type "double3" -360 -360 -360 ;
	setAttr ".maxRotLimit" -type "double3" 360 360 360 ;
	setAttr ".bindPose" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 1 0 -1 1;
	setAttr ".radius" 0.1;
createNode joint -name "joint4";
	rename -uuid "DC5C036F-4F47-2043-6CEF-F6A97F42439B";
	addAttr -cachedInternally true -shortName "liw" -longName "lockInfluenceWeights" 
		-minValue 0 -maxValue 1 -attributeType "bool";
	setAttr ".translate" -type "double3" 1 0 0 ;
	setAttr ".minRotLimit" -type "double3" -360 -360 -360 ;
	setAttr ".maxRotLimit" -type "double3" 360 360 360 ;
	setAttr ".bindPose" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 1 0 0 1;
	setAttr ".radius" 0.1;
createNode lightLinker -shared -name "lightLinker1";
	rename -uuid "5A33125E-483D-F7C8-C7BA-1C9BB22332E3";
	setAttr -size 3 ".link";
	setAttr -size 3 ".shadowLink";
createNode shapeEditorManager -name "shapeEditorManager";
	rename -uuid "E936BAB1-4F7E-8235-A56A-E9ACDE3787FD";
createNode poseInterpolatorManager -name "poseInterpolatorManager";
	rename -uuid "35A25C0D-4FE0-D441-CE94-CAAB9BB01E18";
createNode displayLayerManager -name "layerManager";
	rename -uuid "00E8A070-47C0-29E3-82D5-59A15E049B9F";
createNode displayLayer -name "defaultLayer";
	rename -uuid "4EB5B6DF-443F-8431-52EB-EBA28AC4C076";
createNode renderLayerManager -name "renderLayerManager";
	rename -uuid "E3E08173-47FF-3305-51D7-0DBC70B0522C";
createNode renderLayer -name "defaultRenderLayer";
	rename -uuid "64760A77-4538-C112-4F3B-DABE7667E0AF";
	setAttr ".global" yes;
createNode skinCluster -name "skinCluster1";
	rename -uuid "A0EB2074-47CE-5CF0-7A09-55B257212986";
	setAttr -size 4 ".weightList";
	setAttr ".weightList[0:3].weights"
		1 0 1
		1 3 1
		1 1 1
		1 2 1;
	setAttr -size 4 ".bindPreMatrix";
	setAttr ".bindPreMatrix[0]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 0 -0 1;
	setAttr ".bindPreMatrix[1]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -0 0 1 1;
	setAttr ".bindPreMatrix[2]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -1 0 1 1;
	setAttr ".bindPreMatrix[3]" -type "matrix" 1 -0 0 -0 -0 1 -0 0 0 -0 1 -0 -1 0 -0 1;
	setAttr ".geomMatrix" -type "matrix" 1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1;
	setAttr -size 4 ".matrix";
	setAttr -size 4 ".dropoff[0:3]"  4 4 4 4;
	setAttr -size 4 ".lockWeights";
	setAttr -size 4 ".lockWeights";
	setAttr ".maintainMaxInfluences" yes;
	setAttr ".maxInfluences" 1;
	setAttr ".useComponentsMatrix" yes;
	setAttr -size 4 ".influenceColor";
	setAttr -size 4 ".influenceColor";
createNode dagPose -name "bindPose1";
	rename -uuid "56E04043-476E-9E75-69B5-EB8A1E7071DD";
	setAttr -size 4 ".worldMatrix";
	setAttr -size 4 ".xformMatrix";
	setAttr ".xformMatrix[0]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xformMatrix[1]" -type "matrix" "xform" 1 1 1 0 0 0 0 0 0 -1 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xformMatrix[2]" -type "matrix" "xform" 1 1 1 0 0 0 0 1 0 -1 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr ".xformMatrix[3]" -type "matrix" "xform" 1 1 1 0 0 0 0 1 0 0 0 0 0 0
		 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 1 1 1 1 yes;
	setAttr -size 4 ".members";
	setAttr -size 4 ".parents";
	setAttr ".bindPose" yes;
createNode script -name "sceneConfigurationScriptNode";
	rename -uuid "1D8C761C-4BAF-D34B-454B-8383B2A52248";
	setAttr ".before" -type "string" "playbackOptions -min 1 -max 120 -ast 1 -aet 200 ";
	setAttr ".scriptType" 6;
createNode polyTweakUV -name "polyTweakUV1";
	rename -uuid "0B90BA4B-481B-A832-33F2-668D5425756B";
	setAttr ".useOldPolyArchitecture" yes;
	setAttr -size 3 ".uvTweak";
	setAttr ".uvTweak[2]" -type "float2" 0 5.9604645e-08 ;
	setAttr ".uvTweak[3]" -type "float2" 0 5.9604645e-08 ;
createNode lambert -name "lambert2";
	rename -uuid "D7A27742-43F1-5FB6-A9B8-68AED48A35D4";
createNode shadingEngine -name "lambert2SG";
	rename -uuid "0B96DB5D-4B34-20B0-D117-25AA9690F3B6";
	setAttr ".isHistoricallyInteresting" 0;
	setAttr ".renderableOnlySet" yes;
createNode materialInfo -name "materialInfo1";
	rename -uuid "BDB5E054-4D21-8221-8A00-298A737CC8C9";
createNode checker -name "checker1";
	rename -uuid "7CEB694C-4B3B-8B85-75F2-A783097C30F8";
createNode place2dTexture -name "place2dTexture1";
	rename -uuid "11C94AD9-4FA5-7E6D-4CCE-F6B7A4F25BFB";
	setAttr ".repeatUV" -type "float2" 4 4 ;
select -noExpand :time1;
	setAttr ".outTime" 1;
	setAttr ".unwarpedTime" 1;
select -noExpand :hardwareRenderingGlobals;
	setAttr ".objectTypeFilterNameArray" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
	setAttr ".objectTypeFilterValueArray" -type "Int32Array" 22 0 1 1
		 1 1 1 1 1 1 0 0 0 0 0 0
		 0 0 0 0 0 0 0 ;
select -noExpand :renderPartition;
	setAttr -size 3 ".sets";
select -noExpand :renderGlobalsList1;
select -noExpand :defaultShaderList1;
	setAttr -size 6 ".shaders";
select -noExpand :postProcessList1;
	setAttr -size 2 ".postProcesses";
select -noExpand :defaultRenderUtilityList1;
select -noExpand :defaultRenderingList1;
select -noExpand :defaultTextureList1;
select -noExpand :initialShadingGroup;
	setAttr ".renderableOnlySet" yes;
select -noExpand :initialParticleSE;
	setAttr ".renderableOnlySet" yes;
select -noExpand :defaultRenderGlobals;
	addAttr -cachedInternally true -hidden true -shortName "dss" -longName "defaultSurfaceShader" 
		-dataType "string";
	setAttr ".startFrame" 1;
	setAttr ".endFrame" 10;
	setAttr ".defaultSurfaceShader" -type "string" "lambert1";
select -noExpand :defaultResolution;
	setAttr ".pixelAspect" 1;
select -noExpand :defaultColorMgtGlobals;
	setAttr ".cmEnabled" no;
	setAttr ".configFileEnabled" yes;
	setAttr ".configFilePath" -type "string" "<MAYA_RESOURCES>/OCIO-configs/Maya2022-default/config.ocio";
	setAttr ".viewTransformName" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".viewName" -type "string" "ACES 1.0 SDR-video";
	setAttr ".displayName" -type "string" "sRGB";
	setAttr ".workingSpaceName" -type "string" "ACEScg";
	setAttr ".outputTransformName" -type "string" "ACES 1.0 SDR-video (sRGB)";
	setAttr ".playblastOutputTransformName" -type "string" "ACES 1.0 SDR-video (sRGB)";
select -noExpand :hardwareRenderGlobals;
	setAttr ".colorTextureResolution" 256;
	setAttr ".bumpTextureResolution" 512;
connectAttr "polyTweakUV1.output" "pPlaneShape1.inMesh";
connectAttr "polyTweakUV1.uvTweak[0]" "pPlaneShape1.uvSet[0].uvSetTweakLocation"
		;
relationship "link" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "link" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialShadingGroup.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" ":initialParticleSE.message" ":defaultLightSet.message";
relationship "shadowLink" ":lightLinker1" "lambert2SG.message" ":defaultLightSet.message";
connectAttr "layerManager.displayLayerId[0]" "defaultLayer.identification";
connectAttr "renderLayerManager.renderLayerId[0]" "defaultRenderLayer.identification"
		;
connectAttr "pPlaneShape1Orig.worldMesh" "skinCluster1.input[0].inputGeometry";
connectAttr "pPlaneShape1Orig.outMesh" "skinCluster1.originalGeometry[0]";
connectAttr "bindPose1.message" "skinCluster1.bindPose";
connectAttr "joint1.worldMatrix" "skinCluster1.matrix[0]";
connectAttr "joint2.worldMatrix" "skinCluster1.matrix[1]";
connectAttr "joint3.worldMatrix" "skinCluster1.matrix[2]";
connectAttr "joint4.worldMatrix" "skinCluster1.matrix[3]";
connectAttr "joint1.lockInfluenceWeights" "skinCluster1.lockWeights[0]";
connectAttr "joint2.lockInfluenceWeights" "skinCluster1.lockWeights[1]";
connectAttr "joint3.lockInfluenceWeights" "skinCluster1.lockWeights[2]";
connectAttr "joint4.lockInfluenceWeights" "skinCluster1.lockWeights[3]";
connectAttr "joint1.objectColorRGB" "skinCluster1.influenceColor[0]";
connectAttr "joint2.objectColorRGB" "skinCluster1.influenceColor[1]";
connectAttr "joint3.objectColorRGB" "skinCluster1.influenceColor[2]";
connectAttr "joint4.objectColorRGB" "skinCluster1.influenceColor[3]";
connectAttr "joint1.message" "bindPose1.members[0]";
connectAttr "joint2.message" "bindPose1.members[1]";
connectAttr "joint3.message" "bindPose1.members[2]";
connectAttr "joint4.message" "bindPose1.members[3]";
connectAttr "bindPose1.world" "bindPose1.parents[0]";
connectAttr "bindPose1.world" "bindPose1.parents[1]";
connectAttr "bindPose1.world" "bindPose1.parents[2]";
connectAttr "bindPose1.world" "bindPose1.parents[3]";
connectAttr "joint1.bindPose" "bindPose1.worldMatrix[0]";
connectAttr "joint2.bindPose" "bindPose1.worldMatrix[1]";
connectAttr "joint3.bindPose" "bindPose1.worldMatrix[2]";
connectAttr "joint4.bindPose" "bindPose1.worldMatrix[3]";
connectAttr "skinCluster1.outputGeometry[0]" "polyTweakUV1.inputPolymesh";
connectAttr "checker1.outColor" "lambert2.color";
connectAttr "lambert2.outColor" "lambert2SG.surfaceShader";
connectAttr "pPlaneShape1.instObjGroups" "lambert2SG.dagSetMembers" -nextAvailable
		;
connectAttr "lambert2SG.message" "materialInfo1.shadingGroup";
connectAttr "lambert2.message" "materialInfo1.material";
connectAttr "checker1.message" "materialInfo1.texture" -nextAvailable;
connectAttr "place2dTexture1.outUV" "checker1.uvCoord";
connectAttr "place2dTexture1.outUvFilterSize" "checker1.uvFilterSize";
connectAttr "lambert2SG.partition" ":renderPartition.sets" -nextAvailable;
connectAttr "lambert2.message" ":defaultShaderList1.shaders" -nextAvailable;
connectAttr "place2dTexture1.message" ":defaultRenderUtilityList1.utilities" -nextAvailable
		;
connectAttr "defaultRenderLayer.message" ":defaultRenderingList1.rendering" -nextAvailable
		;
connectAttr "checker1.message" ":defaultTextureList1.textures" -nextAvailable;
// End of elasticskin.ma
