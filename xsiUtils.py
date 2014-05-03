import win32com, os, math
from win32com.client import constants as c
Application = win32com.client.Dispatch("XSI.Application").Application
XSIMath = win32com.client.Dispatch("XSI.Math")
xsi = Application
lm = xsi.LogMessage

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#get the centroid of a selection of points
#store that position
def averagePoints(oPnts = [], bNull=True, fSize=0.5):
	if oPnts == []:
		oPnts = Application.Selection.Item(0)
	#sParObj = oPnts.Value.split(".pnt")[0]
	#Application.Selection.Clear()
	#Application.SelectObj(sParObj)
	oParObj = oPnts.SubComponent.Parent3DObject
	oParMtx = oParObj.Kinematics.Global.Transform.Matrix4
	oVtxCollection = oPnts
	oPositions = oVtxCollection.PositionArray
	nNumPnts = oVtxCollection.Count

	oSumVec = XSIMath.CreateVector3()
	#for each point, create a vector
	for i in range(nNumPnts):
		#add all of the vectors together
		fX = oPositions[0][i]
		fY = oPositions[1][i]
		fZ = oPositions[2][i]
		oVec = XSIMath.CreateVector3(fX, fY, fZ)
		oVec.MulByMatrix4InPlace(oParMtx)
		oSumVec.AddInPlace(oVec)	
		
	#divide by the total number of vectors
	fScale = 1.0/float(nNumPnts)
	oSumVec.ScaleInPlace(fScale)
	if bNull:
		oNull = Application.GetPrim("Null", "placerNull", "", "")
		oNull.Size = fSize
		Application.SetValue(oNull.Name+".kine.global.posx", oSumVec.X)
		Application.SetValue(oNull.Name+".kine.global.posy", oSumVec.Y)
		Application.SetValue(oNull.Name+".kine.global.posz", oSumVec.Z)
	#print oSumVec.X, oSumVec.Y, oSumVec.Z
	return oSumVec

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Currently only supports creation of a box shaped nurbs curve.
#Additional conditionals can be added for more shape variations.
def createControl(in_sShape="cube", in_sName="UNUSED_ctl", in_fScale=1.0, in_sColor="blue"):
	if in_sShape == "cube":
		oCrv = Application.SICreateCurve(in_sName, 1, 1)
		fVal = 0.5*in_fScale
		#top
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, fVal, (-1)*fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, fVal, (-1)*fVal, False, 0, "")
		#front
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, (-1)*fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, (-1)*fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, fVal, fVal, False, 0, "")
		#back
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, fVal, (-1)*fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, (-1)*fVal, (-1)*fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, (-1)*fVal, (-1)*fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, fVal, (-1)*fVal, False, 0, "")
		#bottom
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, (-1)*fVal, (-1)*fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, fVal, (-1)*fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, (-1)*fVal, fVal, False, 0, "")
		Application.SIAddPointOnCurveAtEnd(in_sName, (-1)*fVal, (-1)*fVal, (-1)*fVal, False, 0, "")
		
	Application.MakeLocal(oCrv.Name+".display")
	if in_sColor.lower() == "blue":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 1.0)
	if in_sColor.lower() == "red":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 0.0)
	if in_sColor.lower() == "green":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 0.0)
	if in_sColor.lower() == "yellow":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 0.0)
	if in_sColor.lower() == "orange":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 0.5)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 0.0)
	if in_sColor.lower() == "purple":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 0.7)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 1.0)
	if in_sColor.lower() == "black":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 0.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 0.0)
	if in_sColor.lower() == "white":
		Application.SetValue(oCrv.Name+".display.wirecolorr", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorg", 1.0)
		Application.SetValue(oCrv.Name+".display.wirecolorb", 1.0)
	
	return oCrv

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#given a selection of edges,
#find their average length and
#set them all to the computed average length
def averageEdgeLengths(bDoIt=True):
	oSel = xsi.Selection.Item(0)
	oObject = oSel.SubComponent.Parent3DObject
	oMtx = oObject.Kinematics.Global.Transform.Matrix4
	oEdges = oSel.SubComponent.ComponentCollection
	oDiff = XSIMath.CreateVector3()
	oCtr = XSIMath.CreateVector3()
	nNumEdges = oEdges.Count
	fAvLen = 0.0
	for oEdge in oEdges:
		oVerts = oEdge.Vertices
		oPos1 = oVerts(0).Position
		oPos2 = oVerts(1).Position
		oDiff.Sub(oPos1, oPos2)
		fLength = oDiff.Length()
		fAvLen+= fLength
		
	fAvLen/=float(nNumEdges)
	for oEdge in oEdges:
		oVerts = oEdge.Vertices
		oPos1 = oVerts(0).Position
		oPos2 = oVerts(1).Position
		oDiff.Sub(oPos2, oPos1)
		oCtr.Scale(0.5, oDiff)
		oCtr.AddInPlace(oPos1)
		oCtr.MulByMatrix4InPlace(oMtx)
		fLength = oDiff.Length()
		fScale = fAvLen/fLength
		oDiff.ScaleInPlace(fScale)
		oDiff.AddInPlace(oPos1)
		oDiff.MulByMatrix4InPlace(oMtx)
		if bDoIt:
			xsi.Translate(oVerts(1), oDiff.X, oDiff.Y, oDiff.Z, c.siAbsolute)
			xsi.Translate(oEdge, oCtr.X, oCtr.Y, oCtr.Z, c.siAbsolute)
			
	return fAvLen

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

def getOffsets(oNull=None, oCube=None, oPosNode=None, bAddToICE=False, bVerbose=True):
	oNull = oNull if oNull else xsi.Selection.Item(0) #offset from the cube
	oCube = oCube if oCube else xsi.Selection.Item(1) #this is the constrainer
	if bAddToICE:
		oPosNode = oPosNode if oPosNode else xsi.Selection.Item(2) #the ice vector node which stores the positional offsets
	
	oNullMtrx = oNull.Kinematics.Global.Transform.Matrix4
	oCubeMtrx = oCube.Kinematics.Global.Transform.Matrix4
	oCubeWldInvMtrx = XSIMath.CreateMatrix4()
	oCubeWldInvMtrx.Invert(oCubeMtrx)
	oOffsetMtrx = XSIMath.CreateMatrix4()
	oOffsetMtrx.Mul(oNullMtrx, oCubeWldInvMtrx)
	oOffsetTfrm = oNull.Kinematics.Global.Transform
	oOffsetTfrm.SetMatrix4(oOffsetMtrx)
	
	if bAddToICE:
		oPosNode.Value_x = oOffsetTfrm.PosX
		oPosNode.Value_y = oOffsetTfrm.PosY
		oPosNode.Value_z = oOffsetTfrm.PosZ
	if bVerbose:
		print oOffsetTfrm.PosX, oOffsetTfrm.PosY, oOffsetTfrm.PosZ
		print oOffsetTfrm.RotX, oOffsetTfrm.RotY, oOffsetTfrm.RotZ

	return oOffsetTfrm

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

def makeBone(oRoot, oEff):
	oSel = xsi.GetValue("SelectionList")
	oRoot = oSel(0)
	oEff = oSel(1)
	oRtPos = oRoot.Kinematics.Global.Transform.Translation
	oEfPos = oEff.Kinematics.Global.Transform.Translation
	oSkel = Application.Create2DSkeleton(oRtPos.X, oRtPos.Y, oRtPos.Z, oEfPos.X, oEfPos.Y, oEfPos.Z, 0,1,0)

	print(oSkel)
	return oSkel

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

def distanceBetween(oObj1=None, oObj2=None, vector=False):
	oObj1 = oObj1 if oObj1 else xsi.Selection.Item(0)
	oObj2 = oObj2 if oObj2 else xsi.Selection.Item(1)

	oVec1 = oObj1.Kinematics.Global.Transform.Translation
	oVec2 = oObj2.Kinematics.Global.Transform.Translation

	oVec1.SubInPlace(oVec2)
	fDist = oVec1.Length()
	print fDist
	
	if vector:
		return oVec1
	else:
		return fDist
	
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#This function doesn't require the Softimage runtime
def findLatest(sDir, sPfx="", sSfx="scn"):
	"Find the most recently created file in a particular directory."
	
	listFiles = [x for x in os.listdir(sDir) if x.split(".")[-1]==sSfx]
	if sPfx != "":
		listFiles = [x for x in listFiles if x.split("_")[0] == sPfx]
	sLatest = ""
	fCtimeInit = 0.0
	for sFile in listFiles:
		oStats =  os.stat(sDir+"\\"+sFile)
		if oStats.st_ctime > fCtimeInit:
			sLatest = sFile
			fCtimeInit = oStats.st_ctime
			
	if sLatest == "":
		return False
	else:
		return sDir+sLatest
	
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Create a straight nurbs curve between two locators
#with numPoints number of CVs.
def curveBetweenLocators(numPoints=7, oNull1=None, oNull2=None):
	nNum = numPoints 
	oNull1 = oNull1 if oNull1 else xsi.Selection.Item(0)
	oNull2 = oNull2 if oNull2 else xsi.Selection.Item(1)

	oVec1 = oNull1.LocalTranslation
	oVec2 = oNull2.LocalTranslation
	oDiffVec = XSIMath.CreateVector3()
	oDiffVec.Sub(oVec1, oVec2)
	fDist = oDiffVec.Length()
	fInc = fDist/(nNum-1)
	#make a vector the same direction as the diff vec
	#but of length fInc
	fMult = 1.0/float(nNum-1 )
	oUnitVec = XSIMath.CreateVector3()
	oUnitVec.Scale(fMult, oDiffVec)
	oCrv = xsi.SICreateCurve("hose_crv", 3)
	oUtilityVec = XSIMath.CreateVector3()
	oUtilityVec2 = XSIMath.CreateVector3(oVec1.X, oVec1.Y, oVec1.Z)
	for i in range(nNum):
		if i != 0:
			oUtilityVec.Scale(float(i), oUnitVec)
			oUtilityVec2.Sub(oVec1, oUtilityVec)
		xsi.SIAddPointOnCurveAtEnd(oCrv, oUtilityVec2.X, oUtilityVec2.Y, oUtilityVec2.Z)
	
	return oCrv

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Match the shape of a destination mesh with that of a source mesh.
#This function opperates based on point index. Meshes with
#different point order will result in unpredictable results.
#Either pass the destination object and source object into
#the function, or select the destination object first and then
#the source object and run the function.
def matchShape(dest=None, src=None):
	#set the construction mode to secondary shape modeling mode
	#select the destination mesh, then select the source mesh
	oDest = dest if dest else xsi.Selection.Item(0)
	oSrc = src if src else xsi.Selection.Item(1)
	sDest = oDest.FullName
	sSrc = oSrc.FullName
	#get the world space matrix for the source object
	oSrcMtrx = oSrc.Kinematics.Global.Transform.Matrix4

	#get the array of points for each mesh
	oDestPnts = oDest.ActivePrimitive.Geometry.Points
	oSrcPnts = oSrc.ActivePrimitive.Geometry.Points

	nNumDest = oDestPnts.Count
	nNumSrc = oSrcPnts.Count
	oDestIdxs = oDestPnts.IndexArray
	oDestPos = oDestPnts.PositionArray
	oSrcIdxs = oSrcPnts.IndexArray
	oSrcPos = oSrcPnts.PositionArray
	lm("Number of Points on Destination Mesh: "+ str(nNumDest))
	lm("Number of Points on Source Mesh: "+ str(nNumSrc))
	#for each point of the destination mesh:
	for i in range(nNumDest):
		#get the source point's worldspace postion
		#listSrcPos = [oSrcPos[0][i], oSrcPos[1][i], oSrcPos[2][i]]
		oSrcVec = XSIMath.CreateVector3(oSrcPos[0][i], oSrcPos[1][i], oSrcPos[2][i])
		oSrcVec.MulByMatrix4InPlace(oSrcMtrx)
		#transform the point by the worldspace matrix of the source object
		#get the corresponding destination point's worldspace position
		nDestIdx = oDestIdxs[i]
		Application.Translate(sDest+".pnt["+str(nDestIdx)+"]", oSrcVec.X, oSrcVec.Y, oSrcVec.Z, "siAbsolute", "siView", "siObj", "siXYZ", "", "", "", "", "", "", "", "", "", 3, "")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Get the length of a given model's geometry.
#Currently assumes that the item has been modeled with
#the length running down the z axis.
def getGeoLength(oModel, sAxis="z"):
	oGeo = oModel.FindChildren("", c.siPolyMeshType)
	fZLast = oGeo(0).ActivePrimitive.Geometry.Points(0).Position.Z
	fZHigh = fZLast
	fZLow = fZLast
	for oPoly in oGeo:
		oPnts = oPoly.ActivePrimitive.Geometry.Points
		for oPnt in oPnts:
			fPosZ = oPnt.Position.Z
			if fPosZ > fZHigh:
				fZHigh = fPosZ
			if fPosZ < fZLow:
				fZLow = fPosZ
			
	fLength = abs(fZHigh-fZLow)

	return (fZLow, fZHigh, fLength)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Propigates instances of a model along the length of a nurbs curve.
#Great for building long, repetetive objects like fences.
#Select the curve then select the model, then run the function.
#You can also optionally pass these arguments in as parameters.
def propigateAlongCurve(curve=None, model=None):
	oCrv = curve if curve else xsi.Selection.Item(0).ActivePrimitive.Geometry.Curves(0)
	oModel = model if model else xsi.Selection.Item(1)

	listInstances = []
	oDiffVec = XSIMath.CreateVector3()
	oGeo = oModel.ActivePrimitive.Geometry
	tLength = getGeoLength(oModel)
	fLength	= tLength[2]
	fHigh = tLength[1]
	fLow = tLength[0]
	fRatio = fHigh/fLength
	fInterval = fLength*0.95
	fStep = 0.01
	fNum = 0.0
	oPosLast = oCrv.EvaluatePositionFromPercentage(fNum)[0]
	while True:
		fNum+=fStep
		if fNum>100:
			break
		oPos = oCrv.EvaluatePositionFromPercentage(fNum)
		oDiffVec.Sub(oPos[0], oPosLast)
		fDist = oDiffVec.Length()
		if fDist < fInterval:
			continue
		else:
			oNull = xsi.GetPrim("Null", "tempNull")
			oNull.LocalTranslation = oPosLast
			oLocPos = XSIMath.CreateVector3(oPos[0].X-oPosLast.X,oPos[0].Y-oPosLast.Y,oPos[0].Z-oPosLast.Z)
			oLocPos.ScaleInPlace(fRatio)
			oLocPos.AddInPlace(oPosLast)
			oInst = xsi.Instantiate(oModel)(0)
			oInst.LocalTranslation = oLocPos
			oCns = xsi.ApplyCns("Direction", oInst, oNull)(0)
			oCns.dirx = 0
			oCns.diry = 0
			oCns.dirz = 1
			oGlobTfrm = oInst.Kinematics.Global.Transform
			oPosLast = oPos[0]
			xsi.DeleteObj(oCns)
			xsi.DeleteObj(oNull)
			oInst.Kinematics.Global.Transform = oGlobTfrm
			listInstances.append(oInst)	

	return listInstances

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Select the control objects for which you want to create mobile pivots.
#Run the function. It assumes that the controllers end with the string "_ctl"
#If this isn't the case, then you MUST pass the parameter to it letting
#it know your naming convention.
def mobilePivot(sfx="_ctl", pivSfx="_pivot_ctl"):
	listPivs = []
	oPosVec = XSIMath.CreateVector3(0,0,0)
	oRot = XSIMath.CreateRotation(0, 0, 0)
	for oCtl in xsi.GetValue("SelectionList"):
		oPiv = xsi.GetPrim("Null", oCtl.Name.replace(sfx, pivSfx))
		xsi.ParentObj(oCtl, oPiv)
		oPiv.LocalTranslation = oPosVec
		oPiv.LocalRotation = oRot
		oPiv.Size = 0.5
		Application.MakeLocal(oPiv.FullName+".display", "siDefaultPropagation")
		Application.SetValue(oPiv.FullName+".display.wirecolorr", 1, "")
		Application.SetValue(oPiv.FullName+".display.wirecolorg", 1, "")
		xsi.SetExpr(oCtl.pposx, oPiv.FullName+".kine.local.posx")
		xsi.SetExpr(oCtl.pposy, oPiv.FullName+".kine.local.posy")
		xsi.SetExpr(oCtl.pposz, oPiv.FullName+".kine.local.posz")
		oProp = oCtl.AddProperty("CustomProperty.Preset", False, "Anim_Prop")
		oProp.AddParameter("mobilePivot", 11, c.siClassifUnknown, 2053, "Mobile Pivot")
		xsi.SetExpr(oPiv.FullName+".visibility.viewvis", oProp.FullName+".mobilePivot")
		listPivs.append(oPiv)

	return listPivs

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#Snap a given item to the nearest point on the surface of
#a given piece of geometry from a given location. Select geometry,
#object from which closest point will be measured, then select
#the item to be snapped; run the function.
def snapItemToMesh(geo=None, point=None, item=None):
	oGeo = geo if geo else Application.Selection(0)
	oPnt = point if point else Application.Selection(1)
	oSlv = item if item else Application.Selection(2)

	fPosX = oPnt.posx.Value
	fPosY = oPnt.posy.Value
	fPosZ = oPnt.posz.Value

	oPntLoc = oGeo.Geometry.GetClosestLocations([fPosX, fPosY, fPosZ])
	oNewPnt = oGeo.Geometry.EvaluatePositions(oPntLoc)
	oSlv.posx = oNewPnt[0][0]
	oSlv.posy = oNewPnt[1][0]
	oSlv.posz = oNewPnt[2][0]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#move pivot of object 1 to the position of object 2
def snapPivot(obj1=None, obj2=None):
	oObj1 = obj1 if obj1 else Application.Selection(0)
	oObj2 = obj2 if obj2 else Application.Selection(1)

	oObj1Space = oObj1.Kinematics.Global.Transform
	oObj2Tform = oObj2.Kinematics.Global.Transform

	oPivTform = XSIMath.MapWorldPoseToObjectSpace(oObj1Space, oObj2Tform)

	oObj1.pposx = oPivTform.PosX
	oObj1.pposy = oPivTform.PosY
	oObj1.pposz = oPivTform.PosZ

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

#create locators and controls and place them evenly along the length of
#the input curve. Assumes that the input curve ends with "_crv"
#If not, then specify a different naming convention.
def tentacleRig(numCtls=3, sfx="_crv"):
	oCrv = Application.Selection(0)

	nNum = numCtls 

	for i in range(nNum):
		oNull = Application.GetPrim("Null")
		oNull.Name = oCrv.Name.replace(sfx, "Def0%s_null" % str(i+1))
		oNull.size = 0.1
		sCtrl = oCrv.Name.replace(sfx, "0%s_ctl" % str(i+1))
		oCns = Application.ApplyCns("curve", oNull, oCrv)(0)
		oCns.posu = 1.0/float(nNum)*i
		oCns.tangent = True
		oCns.upvct_active = True
		fScl = 0.3*1.0/float(i+1)
		oCtrl = createControl(sName=sCtrl, fScale=fScl, sColor="red")
		oPsCns = Application.ApplyCns("Pose", oCtrl, oNull, False)
		Application.DeleteObj(oPsCns)
		Application.DeleteObj(oCns)
		Application.ParentObj(oCtrl, oNull)
		oNull.posx = 0.0
		oNull.posy = 0.0
		oNull.posz = 0.0
		oNull.rotx = 0.0
		oNull.roty = 0.0
		oNull.rotz = 0.0
		
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#

