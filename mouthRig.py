#A mouth rig for Softimage
#Requires the Softimage runtime
#Includes sticky lips and support for infinite layering of controls

import win32com, math
from win32com.client import constants as c
si = win32com.client.Dispatch("XSI.Application").Application
XSIMath = win32com.client.Dispatch("XSI.Math")
XSIFactory = win32com.client.Dispatch("XSI.Factory")

class mouthRig(object):
"""
#Assumes the existence of a curve running along the lower lip,
#a curve running along the upper lip, a null or other transform object
#enveloped to the jaw, and a null or transform object of some sort
#enveloped to the rest of the head. The upper lip and lower lip curves are
#best if they are derived directly from edges running along the mouth.
#select the upper lip curve, lower lip curve, jaw deformer, and then head deformer;
#instantiate the mouth rig and build it as follows (scaling it according to your needs):

import mouthRig

oRig = mouthRig.mouthRig(fScale=0.1)
oRig.main()

"""
	__dict__=[
		'__init__',
		'main',
		'setUpFirstLayer',
		'setUpCorners',
		'setUpAdditionalLayer',
		'inbetweens',
		'tangentIceTree',
		'cornerTangent',
		'getTangentOffset',
		'deformersLayer',
		'stickyLips']
		
#***************************************************************************#
	def __init__(self, listNumCtls=[5,9], fScale=0.02):
	
		listSel = list(si.GetValue("SelectionList"))
		listRm = []
		#for oSel in listSel:
			#if oSel.Type != "crvlist":
				#listRm.append(oSel)
		#for oSel in listRm:
			#listSel.pop(oSel)
			
		self.oUprCrv = listSel[0]
		self.oLwrCrv = listSel[1]
		self.oJawDef = listSel[2]
		self.oHeadDef = listSel[3]
		self.oUprIntrCrv = None
		self.oLwrIntrCrv = None
		self.oUprDefCrv = None
		self.oLwrDefCrv = None
		self.oLfUprCornerNull = None
		self.oRtUprCornerNull = None
		self.oLfLwrCornerNull = None
		self.oRtLwrCornerNull = None
		self.listUprLipCtls = [] #each layer of controls gets stored
								#in a list which is one of the items of THIS list
								#ie: [[1st layer], [2nd], [3rd], etc]
								#for as many layers as you want
		self.listLwrLipCtls = []
		self.listUprDefCntrs = []
		self.listLwrDefCntrs = []
		self.oLfCornerCtl = None
		self.oRtCornerCtl = None
		self.oLfUprCrnrTngCtl = None
		self.oLfLwrCrnrTngCtl = None
		self.oRtUprCrnrTngCtl = None
		self.oRtLwrCrnrTngCtl = None		
		self.listNumCtls = listNumCtls
		self.oRootNull = si.GetPrim("Null", "mouthRig_null")
		self.oRigGrp = si.CreateGroup("mouthRig", "", "")
		self.oDefGrp = si.CreateGroup("mouthDeformers")
		self.fScale = fScale
		
		oPosVec = self.oHeadDef.Kinematics.Global.Transform.Translation
		oRootTfrm = self.oRootNull.Kinematics.Global.Transform
		oRootTfrm.Translation = oPosVec
		self.oRootNull.Kinematics.Global.Transform = oRootTfrm
		#si.ParentObj(self.oRootNull, self.oUprCrv)
		#si.ParentObj(self.oRootNull, self.oLwrCrv)
		si.SIAddToGroup(self.oRigGrp, self.oUprCrv)
		si.SIAddToGroup(self.oRigGrp, self.oLwrCrv)
		self.oRootNull.Properties("visibility").Parameters("viewvis").Value = False
		
#***************************************************************************#		
	def main(self): #this is where you assemble all the parts
		
		self.listUprLipCtls.append(self.setUpFirstLayer(self.oUprCrv, self.listNumCtls[0], fScale=self.fScale))
		self.listLwrLipCtls.append(self.setUpFirstLayer(self.oLwrCrv, self.listNumCtls[0], sLip="lwr", fColor="green",fScale=self.fScale))
		self.setUpCorners(fScale=self.fScale)
		self.inbetweens(self.oUprIntrCrv)
		self.inbetweens(self.oLwrIntrCrv, sLip="lwr")
		self.setUpAdditionalLayer( self.oUprIntrCrv, self.listNumCtls[1], fScale=self.fScale*0.75)
		self.setUpAdditionalLayer( self.oLwrIntrCrv, self.listNumCtls[1], sLip="lwr", fScale=self.fScale*0.75)
		self.oUprDefCrv = self.deformersLayer(self.listUprLipCtls[-1], sLip="upr")
		self.oLwrDefCrv = self.deformersLayer(self.listLwrLipCtls[-1], sLip="lwr")
		self.stickyLips(self.listUprLipCtls[-1], self.listLwrLipCtls[-1])#not yet written
		
#***************************************************************************#				
	def setUpFirstLayer(self, oCrv,	nNumCtls=5, sLip="upr", fColor="blue", fScale=0.02):
	
		listCtrls = []
		listCns = []
		listNulls = []
		listUpVecs = []
		oIntrCrv = si.SICreateCurve(sLip+"LipIntermed_crv", 3, 1)
		si.ParentObj(self.oRootNull, oIntrCrv)
		si.SIAddToGroup(self.oRigGrp, oIntrCrv)
		for i in range(nNumCtls):
		
			if i == 0:
				sNullName = "L_%sCorner_null" % sLip
			elif i == nNumCtls-1:
				sNullName = "R_%sCorner_null" % sLip
			else:
				sNullName = sLip+"Lip%02d_null" % i
				
			oNull = si.GetPrim("Null", sNullName)
			listNulls.append(oNull)
			oUpVec = si.GetPrim("Null", sNullName.replace("_null", "UpVec_null"))
			listUpVecs.append(oUpVec)
			oUpVec.Size = 0.01
			oNull.Size = 0.01
			oCrvCns = si.ApplyCns("Curve", oNull, oCrv, False)			
			oCrvCns(0).Parameters("posu").Value = i*(1.0/float(nNumCtls-1))
			listCns.append(oCrvCns)#This is for use in the next loop
			si.MatchTransform(oUpVec, oNull, "siSRT", "")
			oUpVecTform = oUpVec.Kinematics.Global.Transform
			oUpVecTform.PosY += 1.0
			oUpVec.Kinematics.Global.Transform = oUpVecTform
			if sLip == "upr":
				si.ParentObj(self.oHeadDef, oUpVec)
			else:
				si.ParentObj(self.oJawDef, oUpVec)
			#add a point to the intermediate curve
			oNullTform = oNull.Kinematics.Global.Transform
			oNullPos = oNullTform.Translation
			si.SIAddPointOnCurveAtEnd(oIntrCrv, oNullPos.X, oNullPos.Y, oNullPos.Z)
			#set up the tangency and up vectors for these locators
			#do you actually want tangency? How do you want the controls oriented?
			#just keep them aligned with the worlds axes
			oCrvCns(0).UpVectorReference = oUpVec
			oCrvCns(0).Parameters("upvct_active").Value = True
			sCtlName = sNullName.replace("_null", "_ctl")
			if i == 0:
				if sLip == "upr":
					self.oLfUprCornerNull = oNull
				else:
					self.oLfLwrCornerNull = oNull
			elif i == nNumCtls-1:
				if sLip == "upr":
					self.oRtUprCornerNull = oNull
				else:
					self.oRtLwrCornerNull = oNull
			else:
				oCtl = si.CreateControl("", sCtlName, fScale, fColor)
				si.ParentObj(oNull, oCtl)
				oPosVec = XSIMath.CreateVector3(0,0,0)
				oCtl.LocalTranslation = oPosVec
				oCtl.rotx = 0.0
				oCtl.roty = 0.0
				oCtl.rotz = 0.0
			
			try:
				if oCtl not in listCtrls:
					listCtrls.append(oCtl)
			except UnboundLocalError:
				pass
		
		#another loop for reconstraining the inbetween controls to
		#the intermediate curve
		for i in range(nNumCtls):
			if i == 0 or i == nNumCtls-1:
				pass
			else:
				if nNumCtls%2 == 1:
					if i == math.ceil(float(nNumCtls)/2.0)-1:
						pass #This is the control object in the center of the lip
					else:
						#reconstrain the null!
						si.DeleteObj(listCns[i])
						oCrvCns = si.ApplyCns("Curve", listNulls[i], oIntrCrv, False)
						oCrvCns(0).Parameters("posu").Value = i*(1.0/float(nNumCtls-1))
						oCrvCns(0).UpVectorReference = listUpVecs[i]
						oCrvCns(0).Parameters("upvct_active").Value = True
				else: #There are TWO center controls
					#find the two in the center of the lip
					if i == nNumCtls/2 or i == nNumCtls/2-1:
						pass
					else:
						#reconstrain the null!
						si.DeleteObj(listCns[i])
						oCrvCns = si.ApplyCns("Curve", listNulls[i], oIntrCrv, False)
						oCrvCns(0).Parameters("posu").Value = i*(1.0/float(nNumCtls-1))
						oCrvCns(0).UpVectorReference = listUpVecs[i]
						oCrvCns(0).Parameters("upvct_active").Value = True
						
			si.ParentObj(self.oRootNull, listNulls[i])
			si.SIAddToGroup(self.oRigGrp, listNulls[i])
			si.SIAddToGroup(self.oRigGrp, listUpVecs[i])
			
		if sLip == "upr":
			self.oUprIntrCrv = oIntrCrv
		elif sLip == "lwr":
			self.oLwrIntrCrv = oIntrCrv
		
		return listCtrls

#***************************************************************************#
	def setUpCorners(self, fScale=0.02, fColor="purple"):
		"sets up the primary mouth corner controls."
		
		listSides = ["L", "R"]
		for sSide in listSides:
			sNullName = sSide+"_corner_null"
			#create a null
			oNull = si.GetPrim("Null", sNullName)
			oNull.Size = 0.01
			#constrain it between the upr and lwr corner nulls
			#("TwoPoints", "null", "L_lwrCorner_null,L_uprCorner_null", "")
			if sSide == "L":
				oCns = si.ApplyCns("TwoPoints", oNull, self.oLfUprCornerNull.FullName+","+self.oLfLwrCornerNull.FullName, False)
			else:
				oCns = si.ApplyCns("TwoPoints", oNull, self.oRtUprCornerNull.FullName+","+self.oRtLwrCornerNull.FullName, False)
			#create the control object
			oCtl = si.CreateControl("", sNullName.replace("null", "ctl"), fScale, fColor)
			#make the control object a child of the null
			si.ParentObj(oNull, oCtl)
			oPosVec = XSIMath.CreateVector3(0,0,0)
			oCtl.LocalTranslation = oPosVec
			#create a zero null for the control object
			oZero = si.GetPrim("Null", sNullName.replace("corner", "cornerZero"))
			oZero.Size = 0.01
			si.MatchTransform(oZero, oCtl, "siSRT")
			si.ParentObj(oZero, oCtl)			
			
			oAim = si.Duplicate(oZero)(0)
			oUpVec = si.Duplicate(oZero)(0)
			oAim.Name = sNullName.replace("corner", "cornerAim")
			oAimTfrm = oAim.Kinematics.Global.Transform
			oAimTfrm.PosY += 1.0
			oAim.Kinematics.Global.Transform = oAimTfrm
			oAimMstr1 = si.Duplicate(oAim)(0)
			oAimMstr2 = si.Duplicate(oAim)(0)
			oAimMstr1.Name = oAimMstr1.Name.replace("Aim", "AimDriver01").replace("null1", "null")
			oAimMstr2.Name = oAimMstr2.Name.replace("Aim", "AimDriver02").replace("null2", "null")
			si.ApplyCns("Pose", oAimMstr1, self.oHeadDef, True)
			si.ApplyCns("Pose", oAimMstr2, self.oJawDef, True)
			si.ApplyCns("TwoPoints", oAim, oAimMstr1.FullName+","+oAimMstr2.FullName, False)
			oUpVec.Name = sNullName.replace("corner", "cornerUpVec")
			oUpVecTfrm = oUpVec.Kinematics.Global.Transform
			oUpVecTfrm.PosZ += 1.0
			oUpVec.Kinematics.Global.Transform = oUpVecTfrm
			oUpVecMstr1 = si.Duplicate(oUpVec)(0)
			oUpVecMstr2 = si.Duplicate(oUpVec)(0)
			oUpVecMstr1.Name = oUpVecMstr1.Name.replace("UpVec", "UpVecDriver01").replace("null1", "null")
			oUpVecMstr2.Name = oUpVecMstr2.Name.replace("UpVec", "UpVecDriver02").replace("null2", "null")
			si.ApplyCns("Pose", oUpVecMstr1, self.oHeadDef, True)
			si.ApplyCns("Pose", oUpVecMstr2, self.oJawDef, True)
			si.ApplyCns("TwoPoints", oUpVec, oUpVecMstr1.FullName+","+oUpVecMstr2.FullName, False)
			oDirCns = si.ApplyCns("Direction", oZero, oAim, False)
			oDirCns(0).dirx = 0
			oDirCns(0).diry = 1
			oDirCns(0).dirz = 0
			oDirCns(0).UpVectorReference = oUpVec
			oDirCns(0).upx = 0
			oDirCns(0).upy = 0
			oDirCns(0).upz = 1
			oDirCns(0).upvct_active = True
			si.ApplyCns("Position", oZero, oNull, True)
			
			#organize
			si.ParentObj(self.oRootNull, oNull)
			si.ParentObj(self.oRootNull, oZero)
			si.ParentObj(self.oRootNull, oAim)
			si.ParentObj(self.oRootNull, oUpVec)
			si.ParentObj(self.oRootNull, oAimMstr1)
			si.ParentObj(self.oRootNull, oAimMstr2)
			si.ParentObj(self.oRootNull, oUpVecMstr1)
			si.ParentObj(self.oRootNull, oUpVecMstr2)
			si.SIAddToGroup(self.oRigGrp, oNull)
			si.SIAddToGroup(self.oRigGrp, oZero)
			si.SIAddToGroup(self.oRigGrp, oAim)
			si.SIAddToGroup(self.oRigGrp, oUpVec)
			si.SIAddToGroup(self.oRigGrp, oAimMstr1)
			si.SIAddToGroup(self.oRigGrp, oAimMstr2)
			si.SIAddToGroup(self.oRigGrp, oUpVecMstr1)
			si.SIAddToGroup(self.oRigGrp, oUpVecMstr2)
			
			if sSide == "L":
				self.oLfCornerCtl = oCtl
			else:
				self.oRtCornerCtl = oCtl
		
#***************************************************************************#
	def setUpAdditionalLayer(self, oCrv, nNumCtls, sLip="upr", nLevel=2, fScale=0.015, sColor="yellow"):
		"Sets up the second layer of controls on a given curve."
		
		#duplicate the curve (which should be the intermediate curve)
		#this is the curve to which the controls will be constrained
		sGrpName = "layer"+str(nLevel)+"Controls_grp"
		try:
			si.Selection.SetAsText(sGrpName)
			oLyrGrp = si.Selection.Item(0)
		except:
			oLyrGrp = si.CreateGroup(sGrpName)
			
		try:
			si.Selection.SetAsText(self.oRootNull.FullName+".Anim_Prop")
			oAnimProp = si.Selection.Item(0)
			sParamName = "layer"+str(nLevel)+"CtlVis"
		except:
			si.AddProp("Custom_parameter_list", self.oRootNull, "", "Anim_Prop")
			si.Selection.SetAsText(self.oRootNull.FullName+".Anim_Prop")
			oAnimProp = si.Selection.Item(0)
			sParamName = "layer"+str(nLevel)+"CtlVis"
			si.SIAddCustomParameter(oAnimProp, sParamName, "siBool", 0, 0, 1, "", 2053, "", 1, "Layer "+str(nLevel)+" Control Vis")
		
		oCtlCrv = si.Duplicate(oCrv)(0)
		oCtlCrv.Name = sLip+"LipLayer%dCtls_crv"%nLevel
		si.SIAddToGroup(self.oRigGrp, oCtlCrv)
		si.ParentObj(self.oRootNull, oCtlCrv)
		#actually, cluster them!
		oClusters = oCtlCrv.ActivePrimitive.Geometry.Clusters
		si.DeleteObj(oClusters)
		oPnts = oCtlCrv.ActivePrimitive.Geometry.Points
		listClstrs = []
		for oPnt in oPnts:
			listClstrs.append(si.CreateCluster(oPnt)(0))
		#for every cluster, assingn the corresponding control object as a center reference
		nLvlIdx = nLevel-2
		for i in range(oPnts.Count):
			if nLvlIdx == 0:
				if i == 0:
					#assign the left corner control as a reference
					listClstrs[i].CenterReference = self.oLfCornerCtl
				elif i == oPnts.Count-1:
					listClstrs[i].CenterReference = self.oRtCornerCtl
				else:
					if sLip == "upr":
						if i == 1:
							listClstrs[i].CenterReference = self.oLfUprCrnrTngCtl
						elif i == oPnts.Count-2:
							listClstrs[i].CenterReference = self.oRtUprCrnrTngCtl
						else:
							listClstrs[i].CenterReference = self.listUprLipCtls[nLvlIdx][i-2]
					else:
						if i == 1:
							listClstrs[i].CenterReference = self.oLfLwrCrnrTngCtl
						elif i == oPnts.Count-2:
							listClstrs[i].CenterReference = self.oRtLwrCrnrTngCtl
						else:
							listClstrs[i].CenterReference = self.listLwrLipCtls[nLvlIdx][i-2]
			else:
				if sLip == "upr":
					listClstrs[i].CenterReference = self.listUprLipCtls[nLvlIdx][i]
				else:
					listClstrs[i].CenterReference = self.listLwrLipCtls[nLvlIdx][i]
		#attach secondary controls along the length of the curve
		oUpVecTform = si.GetPrim("Null", sLip+"LipLayer%dUpVecs_null" % nLevel)
		listCtls = []
		for i in range(nNumCtls):
			sName = sLip+"Lip%02dLayer%d" % (i, nLevel)
			#create a null, a control object, and an upvector null
			oNull = si.GetPrim("Null", sName+"_null")
			oUpVec = si.GetPrim("Null", sName+"UpVec_null")
			oNull.Size = 0.01
			oUpVec.Size = 0.01
			oCtl = si.CreateControl("", sName+"_ctl", fScale, sColor)
			oCrvCns = si.ApplyCns("Curve", oNull, oCtlCrv, False)
			oCrvCns(0).Parameters("posu").Value = i*(1.0/float(nNumCtls-1))
			si.MatchTransform(oUpVec, oNull, "siTrn")
			oUpVecTrfm = oUpVec.Kinematics.Global
			oUpVec.posy.Value += 1.0
			oCrvCns(0).UpVectorReference = oUpVec
			oCrvCns(0).Parameters("upvct_active").Value = True
			oCrvCns(0).Parameters("tangent").Value = True
			si.MatchTransform(oCtl, oNull, "siSRT")
			si.ParentObj(oNull, oCtl)
			#what moves the upvector?
			#for now, just place them under the head and jaw deformers
			si.ParentObj(oUpVecTform, oUpVec)
			si.ParentObj(self.oRootNull, oNull)
			si.SIAddToGroup(self.oRigGrp, oNull)
			si.SIAddToGroup(self.oRigGrp, oUpVec)
			si.SIAddToGroup(self.oRigGrp, oUpVecTform)
			si.SIAddToGroup(oLyrGrp, oCtl)
			si.SetExpr(oCtl.FullName+".visibility.viewvis", oAnimProp.FullName+"."+sParamName)
			listCtls.append(oCtl)
			
		if sLip == "upr":
			si.ParentObj(self.oHeadDef, oUpVecTform)
			self.listUprLipCtls.append(listCtls)
		else:
			si.ParentObj(self.oJawDef, oUpVecTform)
			self.listLwrLipCtls.append(listCtls)
		
#***************************************************************************#
	def inbetweens(self, oCrv, sLip="upr", nLayer=0):
		
		oPnts = oCrv.ActivePrimitive.Geometry.Points
		nNumPnts = oPnts.Count
		listClusters = []
		for oPnt in oPnts:
			oClstr = si.CreateCluster(oPnt)(0)
			listClusters.append(oClstr)
			
		for i in range(nNumPnts):
			if i == 0:
				listClusters[i].CenterReference = self.oLfCornerCtl
			elif i == nNumPnts-1:
				listClusters[i].CenterReference = self.oRtCornerCtl
			elif nNumPnts%2 == 1:
				if i == math.ceil(float(nNumPnts)/2.0)-1:
					if sLip == "upr":
						nNumCtls = len(self.listUprLipCtls[nLayer])
						nCrIdx = int(math.ceil(float(nNumCtls)/2.0))-1
						listClusters[i].CenterReference = self.listUprLipCtls[nLayer][nCrIdx]
					else:
						nNumCtls = len(self.listLwrLipCtls[nLayer])
						nCrIdx = int(math.ceil(float(nNumCtls)/2.0))-1
						listClusters[i].CenterReference = self.listLwrLipCtls[nLayer][nCrIdx]
				elif i == 1:
					oLfTang = self.cornerTangent(listClusters[i], oPnts(i), oPnts(0), sLip=sLip)
				elif i == nNumPnts-2:
					oRtTang = self.cornerTangent(listClusters[i], oPnts(i), oPnts(i+1), sSide="R", sLip=sLip)
				else:
					if sLip == "upr":
						listClusters[i].CenterReference = self.oHeadDef
					else:
						listClusters[i].CenterReference = self.oJawDef
		if sLip == "upr":
			self.oLfUprCrnrTngCtl = oLfTang
			self.oRtUprCrnrTngCtl = oRtTang
		else:
			self.oLfLwrCrnrTngCtl = oLfTang
			self.oRtLwrCrnrTngCtl = oRtTang
		
#***************************************************************************#			
	def tangentIceTree(self, oNull, sSide="L"):
		"Set up the ice tree for the corners of the mouth."
		oTopNull = oNull.Parent
		if sSide == "L":
			oCrnrCtl = self.oLfCornerCtl
		else:
			oCrnrCtl = self.oRtCornerCtl
		oCrnrZero = oCrnrCtl.Parent
		
		#you got what you need, now set up the graph
		oIceOps = si.ApplyOp("ICETree", oNull, "siNode")
		oIceTree = oIceOps(0)
		oNullData = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\GetDataNode.Preset", oIceTree)			
		oCtlData = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\GetDataNode.Preset", oIceTree)
		oCtlParData = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\GetDataNode.Preset", oIceTree)
		oNullParData = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\GetDataNode.Preset", oIceTree)
		oNullMtxToSRT = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\MatrixToSRTNode.Preset", oIceTree)
		oNullParMtxToSRT = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\MatrixToSRTNode.Preset", oIceTree)
		oCtlMtxToSRT = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\MatrixToSRTNode.Preset", oIceTree)
		oInvert = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\InvertNode.Preset", oIceTree)
		#Multiply Null Parent Position Vector by Control Parent Inverse Matrix:
		oVecByMtx1 = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\MultiplyVectorByMatrixNode.Preset", oIceTree)
		#Multiply offset position vector by scale and rotation matrix of corner control:
		oVecByMtx2 = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\MultiplyVectorByMatrixNode.Preset", oIceTree)
		#convert corner control global matrix to scale and rotation matrix
		oSRTToMtx1 = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\SRTToMatrixNode.Preset", oIceTree)
		#compose the final matrix to set the null's global matrix
		oSRTToMtx2 = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\SRTToMatrixNode.Preset", oIceTree)
		oAddRot = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\AddNode.Preset", oIceTree)
		oAddPos = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\AddNode.Preset", oIceTree)
		oEuler = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\EulerToRotationNode.Preset", oIceTree)
		oPosOfst = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\3DVectorNode.Preset", oIceTree)
		oIntrp = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\LinearInterpolateNode.Preset", oIceTree)
		#Linear interpolation for the tangent blend switch
		oIntrp1 = si.AddICENode("$XSI_DSPRESETS\\ICENodes\\LinearInterpolateNode.Preset", oIceTree)
		oSetData = si.AddICECompoundNode("Set Data", oIceTree)
		#si.AddICENode("$XSI_DSPRESETS\\ICENodes\\.Preset", oIceTree)
		
		oNullData.reference = "self.kine.global"
		oCtlData.reference = oCrnrCtl.FullName+".kine.global"
		oCtlParData.reference = oCrnrZero.FullName+".kine.global"
		oNullParData.reference = oTopNull.FullName+".kine.global"
		si.ConnectICENodes(oNullMtxToSRT.FullName+".matrix", oNullData.FullName+".value")
		si.ConnectICENodes(oCtlMtxToSRT.FullName+".matrix", oCtlData.FullName+".value")
		si.ConnectICENodes(oNullParMtxToSRT.FullName+".matrix", oNullParData.FullName+".value")
		si.ConnectICENodes(oInvert.FullName+".value", oCtlParData.FullName+".value")
		si.ConnectICENodes(oSetData.FullName+".In_Name", oNullData.FullName+".outname")
		si.ConnectICENodes(oVecByMtx1.FullName+".vector", oNullParMtxToSRT.FullName+".translation")
		si.ConnectICENodes(oVecByMtx1.FullName+".matrix", oInvert.FullName+".result")
		si.ConnectICENodes(oSRTToMtx2.FullName+".scaling", oNullMtxToSRT.FullName+".scaling")
		si.ConnectICENodes(oSRTToMtx1.FullName+".scaling", oCtlMtxToSRT.FullName+".scaling")
		si.ConnectICENodes(oSRTToMtx1.FullName+".rotation", oCtlMtxToSRT.FullName+".rotation")
		si.ConnectICENodes(oAddRot.FullName+".value1", oCtlMtxToSRT.FullName+".rotation")
		si.ConnectICENodes(oAddPos.FullName+".value1", oCtlMtxToSRT.FullName+".translation")
		si.ConnectICENodes(oIntrp.FullName+".first", oVecByMtx1.FullName+".result")
		si.ConnectICENodes(oIntrp.FullName+".second", oPosOfst.FullName+".result")
		si.ConnectICENodes(oAddRot.FullName+".value2", oEuler.FullName+".rotation")
		si.ConnectICENodes(oVecByMtx2.FullName+".vector", oIntrp.FullName+".result")
		#these next two lines are a hack that can hopefully get thrown away later
		si.ConnectICENodes(oSetData.FullName+".value", oSRTToMtx1.FullName+".matrix")
		si.DisconnectICENodePort(oSetData.FullName+".value")
		si.ConnectICENodes(oVecByMtx2.FullName+".matrix", oSRTToMtx1.FullName+".matrix")
		si.ConnectICENodes(oAddPos.FullName+".value2", oVecByMtx2.FullName+".result")
		si.ConnectICENodes(oSRTToMtx2.FullName+".translation", oAddPos.FullName+".result")
		si.ConnectICENodes(oSRTToMtx2.FullName+".rotation", oAddRot.FullName+".result")		
		si.ConnectICENodes(oIntrp1.FullName+".first", oNullData.FullName+".value")
		si.ConnectICENodes(oIntrp1.FullName+".second", oSRTToMtx2.FullName+".matrix")
		si.ConnectICENodes(oSetData.FullName+".value", oIntrp1.FullName+".result")
		si.ConnectICENodes(oIceTree.FullName+".port1", oSetData.FullName+".Execute")
		
		#calculate offsets for the constraint
		self.getTangentOffset(oNull, oCrnrCtl, oPosOfst, oEuler)
		
		return oIntrp1
		
#***************************************************************************#	
	def cornerTangent(self, oClstr, oPnt, oStrtPnt, sSide="L", sLip="upr"):
		"Set up the controls for the tangents of the corners of the mouth."
		
		if sSide == "L":
			oCrnrCtl = self.oLfCornerCtl
		else:
			oCrnrCtl = self.oRtCornerCtl
			
		#create a control for the center reference
		sName = sSide+"_corner"+sLip.capitalize()+"Tang"
		oTngCtl = si.GetPrim("Sphere", sName+"_ctl")
		oTngCtl.ActivePrimitive.Parameters("Radius").Value = 0.01
		si.MakeLocal(oTngCtl.FullName+".display")
		si.SetValue(oTngCtl.FullName+".display.wirecolorr", 1.0)
		si.SetValue(oTngCtl.FullName+".display.wirecolorg", 0.5)
		oTngCtl.sclx = 0.5
		oTngCtl.scly = 0.5
		oTngCtl.sclz = 0.5
		#create a parent null for the control
		oParNull = si.GetPrim("Null", sName+"Parent_null")#this one gets the ice tree
		oParNull.Size = 0.01
		si.ParentObj(oParNull, oTngCtl)
		#apply the ice network to this parent
		#add a null as a center reference
		oTopNull = si.GetPrim("Null", sName+"_null")# this one gets constrained to the deformer
		oTopNull.Size = 0.01
		si.ParentObj(oTopNull, oParNull)
		#place the null on the point
		oPntVec = oPnt.Position
		oTopNull.LocalTranslation = oPntVec
		#constrain the null to the left corner control
		oClstr.CenterReference = oTngCtl
		#oCnsCrn = si.ApplyCns("Pose", oTopNull, self.oLfCornerCtl, True)
		#set up a space switch
		#add a blend parameter to the corner control
		oNewProps = XSIFactory.CreateObject("XSI.Collection")
		si.AddProp("Custom_parameter_list", oCrnrCtl, "", "Tangents", oNewProps)
		oNewProps.SetAsText(oCrnrCtl.FullName+".Tangents")
		oTngProp = oNewProps(0)
		#constrain the null to the jaw/head deformer
		if sLip == "upr":
			oCnsDef = si.ApplyCns("Pose", oTopNull, self.oHeadDef, True)
			si.SIAddCustomParameter(oTngProp, "uprFollow", "siDouble", 0.0, 0.0, 1.0, "", 2053, "", 1, "Upper Follow")
			si.SIAddCustomParameter(oTngProp, "uprVis", "siBool", 0, 0, 1, "", 2053, "", 1, "Upper Vis")	
			#link it to the blend weight of oCnsDef
			#si.SetExpr(oCnsDef(0).blendweight, "1.0 - "+oTngProp.FullName+".uprTang")
		else:
			oCnsDef = si.ApplyCns("Pose", oTopNull, self.oJawDef, True)
			si.SIAddCustomParameter(oTngProp, "lwrFollow", "siDouble", 0.0, 0.0, 1.0, "", 2053, "", 1, "Lower Follow")
			si.SIAddCustomParameter(oTngProp, "lwrVis", "siBool", 0, 0, 1, "", 2053, "", 1, "Lower Vis")
			#si.SetExpr(oCnsDef(0).blendweight, "1.0 - "+oTngProp.FullName+".lwrTang")
		#apply the ice tree to oParNull
		oIntrp = self.tangentIceTree(oParNull, sSide=sSide)
		si.SetExpr(oIntrp.FullName+".blend", oTngProp.FullName+"."+sLip+"Follow")
		si.SetExpr(oTngCtl.FullName+".visibility.viewvis", oTngProp.FullName+"."+sLip+"Vis")
		#create a line from the tangent control to the corner of the mouth
		oTngCrv = si.SICreateCurve(oTngCtl.Name.replace("ctl", "crv"), 1)
		oStrtPos = oStrtPnt.Position
		oEndPos = oPnt.Position
		si.SIAddPointOnCurveAtEnd(oTngCrv, oStrtPos.X, oStrtPos.Y, oStrtPos.Z)
		si.SIAddPointOnCurveAtEnd(oTngCrv, oEndPos.X, oEndPos.Y, oEndPos.Z)
		#cluster the points on the curve, and give them center refs
		oTngPnts = oTngCrv.ActivePrimitive.Geometry.Points
		listTngClstrs = []
		for oTngPnt in oTngPnts:
			listTngClstrs.append(si.CreateCluster(oTngPnt)(0))
		listTngClstrs[0].CenterReference = oCrnrCtl
		listTngClstrs[1].CenterReference = oTngCtl
		#connect the curves vis to the tangent param
		si.SetExpr(oTngCrv.FullName+".visibility.viewvis", oTngProp.FullName+"."+sLip+"Vis")
		#make the curve unselectable
		si.SetValue(oTngCrv.FullName+".visibility.selectability", False)
		#organize
		si.ParentObj(self.oRootNull, oTopNull)
		si.ParentObj(self.oRootNull, oTngCrv)
		si.SIAddToGroup(self.oRigGrp, oTopNull)
		si.SIAddToGroup(self.oRigGrp, oParNull)
		si.Lock(oTngCtl.FullName+".kine.local.sclx", "siLockLevelManipulation")
		si.Lock(oTngCtl.FullName+".kine.local.scly", "siLockLevelManipulation")
		si.Lock(oTngCtl.FullName+".kine.local.sclz", "siLockLevelManipulation")
		si.SetKeyableAttributes(oTngCtl, "kine.local.sclx,kine.local.scly,kine.local.sclz", "siKeyableAttributeClear")
		
		return oTngCtl
		
#***************************************************************************#		
	def getTangentOffset(self, oConstrainee, oConstrainer, oPosNode, oRotNode):
		"Calculate and set offsets for custom constraints on the corners of the mouth."
		
		oConstrainee #offset from the cube
		oConstrainer #this is the constrainer
		oPosNode #the ice vector node which stores the positional offsets
		oRotNode #the ice node that takes a vector as input and converts to rotation

		oConstraineeMtrx = oConstrainee.Kinematics.Global.Transform.Matrix4
		oConstrainerMtrx = oConstrainer.Kinematics.Global.Transform.Matrix4
		oConstrainerWldInvMtrx = XSIMath.CreateMatrix4()
		oConstrainerWldInvMtrx.Invert(oConstrainerMtrx)
		oOffsetMtrx = XSIMath.CreateMatrix4()
		oOffsetMtrx.Mul(oConstraineeMtrx, oConstrainerWldInvMtrx)
		oOffsetTfrm = oConstrainee.Kinematics.Global.Transform
		oOffsetTfrm.SetMatrix4(oOffsetMtrx)
		
		oPosNode.Value_x = oOffsetTfrm.PosX
		oPosNode.Value_y = oOffsetTfrm.PosY
		oPosNode.Value_z = oOffsetTfrm.PosZ
		
		oRotNode.rotationxyz_x = oOffsetTfrm.RotX
		oRotNode.rotationxyz_y = oOffsetTfrm.RotY
		oRotNode.rotationxyz_z = oOffsetTfrm.RotZ
		
#***************************************************************************#	
	def deformersLayer(self, listCtls, sLip="upr"):
		"Set up the final layer which contains the deformers."
		
		#create a new curve for the deformers
		oCrv = si.SICreateCurve(sLip+"LipDeformers_crv", 3, 1)
		for oCtl in listCtls:
			oCtlPos = oCtl.Kinematics.Global.Transform.Translation
			si.SIAddPointOnCurveAtEnd(oCrv, oCtlPos.X, oCtlPos.Y, oCtlPos.Z)
		
		si.ParentObj(self.oRootNull, oCrv)
		si.SIAddToGroup(self.oRigGrp, oCrv)
		oPnts = oCrv.ActivePrimitive.Geometry.Points
		nNum = oPnts.Count
		nNumCtls = len(listCtls)
		listCrRefs = []
		for i, oPnt in zip(range(nNum), oPnts):
			#cluster the point
			#if it is an endpoint cluster it with its tangent
			oClstr = si.CreateCluster(oPnt)(0)
			#create a null as the cluster's center reference
			oCrRef = si.GetPrim("Null", sLip+"LipDefCrvCtr%02d_null"%i)
			oCrRef.Size = 0.005
			oPntPos = oPnt.Position
			oCrRef.LocalTranslation = oPntPos
			oClstr.CenterReference = oCrRef
			listCrRefs.append(oCrRef)
			si.ParentObj(self.oRootNull, oCrRef)
			si.SIAddToGroup(self.oRigGrp, oCrRef)
		
		for i in range(nNumCtls):
			#create a deformer and constrain it to the curve
			oDef = si.GetPrim("Cube", sLip+"Lip%02d_def"%i) #what type of primitive? Implicit cube
			oDef.Length = 0.01
			oCrvCns = si.ApplyCns("Curve", oDef, oCrv, False)(0)
			oCrvCns.Parameters("posu").Value = float(i)/float(nNumCtls-1)
			oCrvCns.Parameters("tangent").Value = True
			oCrvCns.Parameters("upvct_active").Value = True
			#you still have to do something about up vectors
			#create up vectors and pose constrain them to the control objects
			oUpVec = si.GetPrim("Null", sLip+"Lip%02d_upVec"%i)
			oUpVec.Size = 0.01
			si.MatchTransform(oUpVec, oDef, "siSRT")
			oUpVec.posy.Value += 1.0
			oCrvCns.UpVectorReference = oUpVec
			si.ParentObj(listCtls[i], oUpVec)
			si.ParentObj(self.oRootNull, oDef)
			si.SIAddToGroup(self.oDefGrp, oDef)
			si.SIAddToGroup(self.oRigGrp, oUpVec)
		
		nNumCrRefs = len(listCrRefs)
		for i, oCrRef in enumerate(listCrRefs):
			#constrain the cluster center to the corresponding control object
			#the tangent center reference should be blended between the two 
			#center references on either side of it
			if i == 0:
				#si.ApplyCns("Position", oCrRef, listCtls[i], True)
				si.ParentObj(listCtls[i], oCrRef)
			elif i == 1:
				#create an additional null
				#constrain between two points
				#make the tangent ctr a child of this extra null
				oCns1 = si.ApplyCns("Pose", oCrRef, listCrRefs[0], True)(0)
				oCns2 = si.ApplyCns("pose", oCrRef, listCrRefs[2], True)(0)
				oCns2.Parameters("blendweight").Value = 0.5
			elif i == nNumCrRefs-1:
				#si.ApplyCns("Position", oCrRef, listCtls[-1], True)
				si.ParentObj(listCtls[-1], oCrRef)
			elif i == nNumCrRefs-2:
				si.ApplyCns("Pose", oCrRef, listCrRefs[-1], True)
				oCns = si.ApplyCns("Pose", oCrRef, listCrRefs[-3], True)(0)
				oCns.Parameters("blendweight").Value = 0.5
			else:
				#si.ApplyCns("Position", oCrRef, listCtls[i-1], True)
				si.ParentObj(listCtls[i-1], oCrRef)
			
		if sLip == "upr":
			self.listUprDefCntrs = listCrRefs
		else:
			self.listLwrDefCntrs = listCrRefs
			
		return oCrv #return the curve that constrains the deformers
				
#***************************************************************************#						
	def stickyLips(self, listUprCtls, listLwrCtls):
	
		#what do you need?
		#the upper and lower lip last layer controls
		#from them, generate a center curve by averaging their corresponding points
		oCtrCrv = si.SICreateCurve("stickyLips_crv" , 3, 1)
		si.ParentObj(self.oRootNull, oCtrCrv)
		si.SIAddToGroup(self.oRigGrp, oCtrCrv)
		for oUpr, oLwr in zip(listUprCtls, listLwrCtls):
			oUprPos = oUpr.Kinematics.Global.Transform.Translation
			oLwrPos = oLwr.Kinematics.Global.Transform.Translation
			oPosVec = XSIMath.CreateVector3()
			oPosVec.Add(oUprPos, oLwrPos)
			oPosVec.ScaleInPlace(0.5)
			si.SIAddPointOnCurveAtEnd(oCtrCrv, oPosVec.X, oPosVec.Y, oPosVec.Z)
			
		#cluster the points of the center curve
		oPnts = oCtrCrv.ActivePrimitive.Geometry.Points
		nNumPnts = oPnts.Count
		listCntrs = []
		for i, oPnt in enumerate(oPnts):
			oClstr = si.CreateCluster(oPnt)(0)
			oCrRef = si.GetPrim("Null", "stickyLips%02d_null"%i)
			oCrRef.Size = 0.01
			oPos = oPnt.Position
			oCrRef.LocalTranslation = oPos
			oClstr.CenterReference = oCrRef
			listCntrs.append(oCrRef)
			si.ParentObj(self.oRootNull, oCrRef)
			si.SIAddToGroup(self.oRigGrp, oCrRef)
			
		for i , oCrRef in enumerate(listCntrs):
			#point constrain the centers between the upper and lower lip controls(no offsets)
			if i == 0: #the first point on the left side
				si.ApplyCns("Pose", oCrRef, listUprCtls[i], True)
				oCns = si.ApplyCns("Pose", oCrRef, listLwrCtls[i], True)(0)
			elif i == 1: #the left tangent
				#constrain it between the two centers on either side of it
				si.ApplyCns("Pose", oCrRef, listCntrs[0], True)
				oCns = si.ApplyCns("Pose", oCrRef, listCntrs[2], True)(0)
			elif i == nNumPnts-2:#the right tangent
				si.ApplyCns("Pose", oCrRef, listCntrs[-1], True)
				oCns = si.ApplyCns("Pose", oCrRef, listCntrs[-3], True)(0)
			elif i == nNumPnts-1:#the last point on the right side
				si.ApplyCns("Pose", oCrRef, listUprCtls[-1], True)
				oCns = si.ApplyCns("Pose", oCrRef, listLwrCtls[-1], True)(0)
			else:#all the points inbetween the two tangents
				si.ApplyCns("Pose", oCrRef, listUprCtls[i-1], True)
				oCns = si.ApplyCns("Pose", oCrRef, listLwrCtls[i-1], True)(0)
			oCns.Parameters("blendweight").Value = 0.5
			
		#add the sticky lips params to the root null
		try:
			si.Selection.SetAsText(self.oRootNull.FullName+".Anim_Prop")
		except:
			si.AddProp("Custom_parameter_list", self.oRootNull, "", "Anim_Prop")
			si.Selection.SetAsText(self.oRootNull.FullName+".Anim_Prop")
		oAnimProp = si.Selection.Item(0)
		si.SIAddCustomParameter(oAnimProp, "stickyLips", "siDouble", 0.0, 0.0, 2.0, "", 2053, "", 1.0, "Sticky Lips")
		si.SIAddCustomParameter(oAnimProp, "sharpness", "siDouble", 0.0, -10.0, 10.0, "", 2053, -1.0, 1.0, "Sharpness")
				
		#the cluster centers on the deformer curve need to be point constrained to the cntrs
		#of the center curve and blended
		nNum = len(listCntrs)
		fMid = math.ceil(float(nNum)/2.0)-1.0
		nFactor = 2
		
		for i, oUpr, oLwr, oCntr in zip(range(nNum), self.listUprDefCntrs, self.listLwrDefCntrs, listCntrs):
		
			if i > fMid:
				n = (float(i) - fMid)
				sPosNeg = "(1.0)"
			else:
				if i == fMid:
					n = 0.5
				else:
					n = (fMid - float(i))
				sPosNeg = "1.0"
				
			d = n/fMid
			sSticky = oAnimProp.FullName+".stickyLips"
			sOffset = oAnimProp.FullName+".sharpness"
			#sEq = sSticky+"*sin(180.0*"+str(d)+")" #str(n)
			
			sEq = sSticky+"*(pow("+str(n)+", "+sOffset+"+2.0) )*4"
			sExp = "cond("+sEq+" >= 1.0, 1.0, cond("+sEq+" <= 0.0, 0.0, "+sEq+"))"
			
			oUprStat = si.Duplicate(oUpr)(0)
			oUprStat.Name = oUpr.Name.replace("CrvCtr", "Stat")
			si.ParentObj(oUpr.Parent, oUprStat)
			si.SIAddToGroup(self.oRigGrp, oUprStat)
			oLwrStat = si.Duplicate(oLwr)(0)
			oLwrStat.Name = oLwr.Name.replace("CrvCtr", "Stat")
			si.ParentObj(oLwr.Parent, oLwrStat)
			si.SIAddToGroup(self.oRigGrp, oLwrStat)
			
			si.ApplyCns("Position", oUpr, oUprStat, False)
			si.ApplyCns("Position", oLwr, oLwrStat, False)
			oUprCns = si.ApplyCns("Position", oUpr, oCntr, False)(0)
			oLwrCns = si.ApplyCns("Position", oLwr, oCntr, False)(0)
			
			si.SetExpr(oUprCns.FullName+".blendweight", sExp)
			si.SetExpr(oLwrCns.FullName+".blendweight", sExp)
