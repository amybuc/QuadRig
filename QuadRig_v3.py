import sys
import os

from PySide2 import QtCore, QtGui, QtUiTools, QtWidgets
import shiboken2

import maya.cmds as mc
import maya.OpenMayaUI as MayaUI

SCRIPT_LOC = os.path.split("C:/QuadRig/QuadRig_v3.py")[0]

def loadUiWidget (uifilename, parent=None):
	loader = QtUiTools.QUiLoader()
	uifile = QtCore.QFile(uifilename)
	uifile.open(QtCore.QFile.ReadOnly)
	ui = loader.load(uifile, parent)
	uifile.close()
	return ui

class templateUiDemo():
	
	def __init__(self):
		mainUI = SCRIPT_LOC + "/quadrigUI/quadrig_02.ui"
		MayaMain = shiboken2.wrapInstance(long(MayaUI.MQtUtil.mainWindow()), QtWidgets.QWidget)
		
		# main window load / settings
		self.MainWindowUI = loadUiWidget(mainUI, MayaMain)
		self.MainWindowUI.bgLabel.setPixmap(QtGui.QPixmap(SCRIPT_LOC + "/quadrigUI/bgGraphic.png"))
		self.MainWindowUI.lArmBtn.clicked.connect(templateUiDemo.lArmBtn)
		self.MainWindowUI.lLegBtn.clicked.connect(templateUiDemo.lLegBtn)
		self.MainWindowUI.rArmBtn.clicked.connect(templateUiDemo.rArmBtn)
		self.MainWindowUI.rLegBtn.clicked.connect(templateUiDemo.rLegBtn)
		self.MainWindowUI.spineBtn.clicked.connect(templateUiDemo.spineBtn)
		self.MainWindowUI.tailBtn.clicked.connect(templateUiDemo.tailBtn)
		self.MainWindowUI.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
		self.MainWindowUI.show()

	@classmethod
	def lArmBtn(cls):
		templateUiDemo.quadromatic("arm", "left")

	@classmethod
	def lLegBtn(cls):
		templateUiDemo.quadromatic("leg", "left")

	@classmethod
	def rArmBtn(cls):
		templateUiDemo.quadromatic("arm", "right")

	@classmethod
	def rLegBtn(cls):
		templateUiDemo.quadromatic("leg", "right")

	@classmethod
	def spineBtn(cls):
		templateUiDemo.quadromatic("spine", "null")

	@classmethod
	def tailBtn(cls):
		templateUiDemo.quadromatic("tail", "null")

	@classmethod
	def quadromatic(self, function, orientation):

		print function
		print orientation

		listObjs = mc.ls(sl=True)
		selSize = len(listObjs)
		num = 0

		armJNames = ["scap", "shoulder", "elbow", "wrist", "hand"]
		legJNames = ["hip", "knee", "calf", "ankle", "toe"]

		try:
				if orientation == "left":
					orientString = "l_"
				if orientation == "right":
					orientString = "r_" 
		except:
			print "No left or right directive entered"

		if function == "spine":



			print "spine function activated"

			for i in range(0, selSize, 1):
				mc.rename(listObjs[i], "spine" + "% d_jnt" % num)
				num += 1
				
			lastJointNum = selSize-1
			mc.ikHandle(sj="spine_0_jnt",  ee="spine_" + "% d_jnt" % lastJointNum, sol="ikSplineSolver", ccv=True, ns=3, n="spine_ik")

			mc.rename("curve1", "spine_crv")
			mc.select(cl=True)
			mc.joint(n="spineBase_jntCtrl", rad=1.5)
			pointy1 = mc.pointConstraint("spine_0_jnt", "spineBase_jntCtrl")
			mc.delete(pointy1)
			mc.select(cl=True)
			mc.joint(n="spineEnd_jntCtrl", rad=1.5)
			pointy2 = mc.pointConstraint("spine_" + "% d_jnt" % lastJointNum, "spineEnd_jntCtrl")
			mc.delete(pointy2)
			mc.select("spineBase_jntCtrl")
			mc.select("spineEnd_jntCtrl", tgl=True)
			mc.select("spine_crv", tgl=True)
			mc.skinCluster()
			
			upperbodyFrontCtrl = mc.circle(n="upperbodyFront_ctrl", r=4)
			pointy3 = mc.pointConstraint("spineBase_jntCtrl",upperbodyFrontCtrl)
			mc.delete(pointy3)
			mc.select(upperbodyFrontCtrl)
			mc.makeIdentity("upperbodyFront_ctrl", a=True, t=True, r=True, s=True)
			mc.parentConstraint(upperbodyFrontCtrl, "spineBase_jntCtrl")
		   
			upperbodyBackCtrl = mc.circle(n="upperbodyBack_ctrl", r=4)
			pointy4 = mc.pointConstraint("spineEnd_jntCtrl", upperbodyBackCtrl)
			mc.delete(pointy4)
			mc.select(upperbodyBackCtrl)
			mc.makeIdentity("upperbodyBack_ctrl", a=True, t=True, r=True, s=True)
			mc.parentConstraint(upperbodyBackCtrl, "spineEnd_jntCtrl")
			
			upperbodyGroupCtrl = mc.circle(n="upperbody_ctrl")
			mc.select(upperbodyGroupCtrl)
			mc.scale(16, 26, 16)
			mc.select(upperbodyGroupCtrl)
			mc.rotate(90, 0, 0, r=False)
			tempParent = mc.pointConstraint("spineBase_jntCtrl", "spineEnd_jntCtrl", upperbodyGroupCtrl)
			mc.delete(tempParent)
			mc.makeIdentity(upperbodyGroupCtrl, a=True, t=True, r=True, s=True)
			
			mc.parent(upperbodyFrontCtrl, upperbodyGroupCtrl)
			mc.parent(upperbodyBackCtrl, upperbodyGroupCtrl)


		if function == "arm":
			for i in range(0, selSize, 1):
				print armJNames[i]
				mc.rename(listObjs[i],orientString + armJNames[i] + "_jnt")
				num+=1
			
			#Adding some Iks
			mc.ikHandle(sj=orientString + armJNames[0] + "_jnt", ee=orientString + armJNames[2] + "_jnt", sol="ikRPsolver", n=orientString + "upperarm_ik")
			mc.ikHandle(sj=orientString + armJNames[2] + "_jnt", ee=orientString + armJNames[3] + "_jnt", sol="ikSCsolver", n=orientString + "armhock_ik")
			mc.ikHandle(sj=orientString + armJNames[3] + "_jnt", ee=orientString + armJNames[4] + "_jnt", sol="ikSCsolver", n=orientString + "finger_ik")


			#Making some Curves, arranging them

			mc.curve(n=orientString+"hand_ctrl", p=[[0.5, 0.825, -0.75], [0.5, -0.001, -0.75], [-0.5, -0.001, -0.75], [-0.5, -0.001, 0.714], [0.5, -0.001, 0.714], [0.5, 0.546, 0.714], [-0.5, 0.546, 0.714], [-0.5, 0.825, -0.75], [0.5, 0.825, -0.75], [0.5, 0.546, 0.714], [0.5, -0.001, 0.714], [0.5, -0.001, -0.75], [-0.5, -0.001, -0.75], [-0.5, 0.825, -0.75], [-0.5, 0.546, 0.714], [-0.5, -0.001, 0.714]],d=1)
			
			mc.pointConstraint(orientString + armJNames[4] + "_jnt", orientString + armJNames[3] + "_jnt", orientString+"hand_ctrl", n="temp")
			mc.move(0, orientString+"hand_ctrl", y=True, r=False)

			handEndLoc = mc.spaceLocator()
			handStartLoc = mc.spaceLocator()

			mc.matchTransform(handEndLoc, orientString + armJNames[4] + "_jnt")
			mc.matchTransform(handStartLoc, orientString + armJNames[3] + "_jnt")

			handMeasureNode = mc.distanceDimension(handEndLoc, handStartLoc)

			handScaleFactor = mc.getAttr(handMeasureNode + ".distance")

			mc.scale(handScaleFactor, handScaleFactor, handScaleFactor, orientString+"hand_ctrl")
			mc.delete("temp")
			mc.delete(handMeasureNode)
			mc.delete(handEndLoc)
			mc.delete(handStartLoc)

			mc.circle(n=orientString+"handBall_ctrl")
			mc.matchTransform(orientString+"handBall_ctrl", orientString + armJNames[2] + "_jnt", rot=False)
			mc.rotate(-90,0,0, orientString+"handBall_ctrl", r=False)
			mc.makeIdentity(orientString+"hand_ctrl", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString+"handBall_ctrl", a=True, t=True, r=True, s=True)
			
			#Now the Locators, parenting them correctly and then positioning them appropriately
			mc.spaceLocator(n=orientString + "handHindHeelRoll_LOC")
			mc.spaceLocator(n=orientString + "handHindfingerRoll_LOC")
			mc.parent(orientString +"handHindfingerRoll_LOC", orientString +"handHindHeelRoll_LOC")
			mc.spaceLocator(n=orientString + "handHindTipRoll_LOC")
			mc.parent(orientString + "handHindTipRoll_LOC", orientString +"handHindfingerRoll_LOC")
			mc.spaceLocator(n=orientString + "handHindBallRoll_LOC")
			mc.parent(orientString + "handHindBallRoll_LOC", orientString +"handHindfingerRoll_LOC")
			
			mc.matchTransform(orientString + "handHindHeelRoll_LOC", orientString + armJNames[2] + "_jnt", rot=False, scl=False)
			mc.move(0, orientString + "handHindHeelRoll_LOC", y=True, r=False)
			mc.matchTransform(orientString + "handHindfingerRoll_LOC", orientString + armJNames[4] + "_jnt", rot=False, scl=False)
			mc.matchTransform(orientString + "handHindTipRoll_LOC", orientString + armJNames[3] + "_jnt", rot=False, scl=False)
			mc.matchTransform(orientString + "handHindBallRoll_LOC", orientString + armJNames[3] + "_jnt", rot=False, scl=False)
			

			
			#Parenting Everything!
			mc.parent(orientString + "armhock_ik", orientString+"hand_ctrl")
			mc.parent(orientString + "handHindHeelRoll_LOC", orientString+"hand_ctrl")
			mc.parent(orientString + "upperarm_ik", orientString+"handBall_ctrl")
			mc.parent(orientString+"handBall_ctrl", orientString + "handHindTipRoll_LOC")
			mc.parent(orientString + "finger_ik", orientString + "handHindBallRoll_LOC")
			
			mc.makeIdentity(orientString + "handHindHeelRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "handHindfingerRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "handHindTipRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "handHindBallRoll_LOC", a=True, t=True, r=True, s=True)
			
			#Finally, set up new attributes on the hand control and connect them to the locator rotations
			mc.addAttr(orientString+"hand_ctrl", at='float', ln="HeelRoll", h=False, w=True)
			mc.setAttr(orientString+"hand_ctrl.HeelRoll", k=True, typ="float")
			mc.addAttr(orientString+"hand_ctrl", at='float', ln="fingerRoll", h=False, w=True)
			mc.setAttr(orientString+"hand_ctrl.fingerRoll", k=True, typ="float")
			mc.addAttr(orientString+"hand_ctrl", at='float', ln="TipRoll", h=False, w=True)
			mc.setAttr(orientString+"hand_ctrl.TipRoll", k=True, typ="float")
			
			mc.connectAttr(orientString+"hand_ctrl.HeelRoll", orientString + "handHindHeelRoll_LOC.rotateX")
			mc.connectAttr(orientString+"hand_ctrl.fingerRoll", orientString + "handHindfingerRoll_LOC.rotateX")
			mc.connectAttr(orientString+"hand_ctrl.TipRoll", orientString + "handHindBallRoll_LOC.rotateX")

		if function == "leg":
			
			for i in range(0, selSize, 1):
				mc.rename(listObjs[i],orientString + legJNames[i] + "_jnt")
				num+=1
				
		   
			#Adding some Iks
			mc.ikHandle(sj=orientString + legJNames[0] + "_jnt", ee=orientString + legJNames[2] + "_jnt", sol="ikRPsolver", n=orientString + "upperLeg_ik")
			mc.ikHandle(sj=orientString + legJNames[2] + "_jnt", ee=orientString + legJNames[3] + "_jnt", sol="ikSCsolver", n=orientString + "leghock_ik")
			mc.ikHandle(sj=orientString + legJNames[3] + "_jnt", ee=orientString + legJNames[4] + "_jnt", sol="ikSCsolver", n=orientString + "toe_ik")
			
			#Now the Locators, parenting them correctly and then positioning them appropriately
			mc.spaceLocator(n=orientString + "footHindHeelRoll_LOC")
			mc.spaceLocator(n=orientString + "footHindToeRoll_LOC")
			mc.parent(orientString +"footHindToeRoll_LOC", orientString +"footHindHeelRoll_LOC")
			mc.spaceLocator(n=orientString + "footHindTipRoll_LOC")
			mc.parent(orientString + "footHindTipRoll_LOC", orientString +"footHindToeRoll_LOC")
			mc.spaceLocator(n=orientString + "footHindBallRoll_LOC")
			mc.parent(orientString + "footHindBallRoll_LOC", orientString +"footHindToeRoll_LOC")
			
			mc.matchTransform(orientString + "footHindHeelRoll_LOC", orientString + legJNames[2] + "_jnt", rot=False, scl=False)
			mc.move(0, orientString + "footHindHeelRoll_LOC", y=True, r=False)
			mc.matchTransform(orientString + "footHindToeRoll_LOC", orientString + legJNames[4] + "_jnt", rot=False, scl=False)
			mc.matchTransform(orientString + "footHindTipRoll_LOC", orientString + legJNames[3] + "_jnt", rot=False, scl=False)
			mc.matchTransform(orientString + "footHindBallRoll_LOC", orientString + legJNames[3] + "_jnt", rot=False, scl=False)
			
			#Making some Curves, arranging them

			mc.curve(n=orientString+"foot_ctrl", p=[[0.5, 0.825, -0.75], [0.5, -0.001, -0.75], [-0.5, -0.001, -0.75], [-0.5, -0.001, 0.714], [0.5, -0.001, 0.714], [0.5, 0.546, 0.714], [-0.5, 0.546, 0.714], [-0.5, 0.825, -0.75], [0.5, 0.825, -0.75], [0.5, 0.546, 0.714], [0.5, -0.001, 0.714], [0.5, -0.001, -0.75], [-0.5, -0.001, -0.75], [-0.5, 0.825, -0.75], [-0.5, 0.546, 0.714], [-0.5, -0.001, 0.714]],d=1)
			
			mc.pointConstraint(orientString + legJNames[4] + "_jnt", orientString + legJNames[3] + "_jnt", orientString+"foot_ctrl", n="temp")
			mc.move(0, orientString+"foot_ctrl", y=True, r=False)

			footEndLoc = mc.spaceLocator()
			footStartLoc = mc.spaceLocator()

			mc.matchTransform(footEndLoc, orientString + legJNames[4] + "_jnt")
			mc.matchTransform(footStartLoc, orientString + legJNames[3] + "_jnt")

			measureNode = mc.distanceDimension(footEndLoc, footStartLoc)

			scaleFactor = mc.getAttr(measureNode + ".distance")

			mc.scale(scaleFactor, scaleFactor, scaleFactor, orientString+"foot_ctrl")

			mc.delete("temp")
			mc.delete(measureNode)
			mc.delete(footEndLoc)
			mc.delete(footStartLoc)

			mc.rotate(0,0,0, orientString+"foot_ctrl", r=False)
			mc.circle(n=orientString+"footBall_ctrl")
			mc.matchTransform(orientString+"footBall_ctrl", orientString + legJNames[2] + "_jnt", rot=False)
			mc.rotate(-90,0,0, orientString+"footBall_ctrl", r=False)
			mc.makeIdentity(orientString+"footBall_ctrl", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString+"foot_ctrl", a=True, t=True, r=True, s=True)
			
			#Parenting Everything!
			mc.parent(orientString + "leghock_ik", orientString+"foot_ctrl")
			mc.parent(orientString + "footHindHeelRoll_LOC", orientString+"foot_ctrl")
			mc.parent(orientString + "upperLeg_ik", orientString+"footBall_ctrl")
			mc.parent(orientString+"footBall_ctrl", orientString + "footHindTipRoll_LOC")
			mc.parent(orientString + "toe_ik", orientString + "footHindBallRoll_LOC")
			
			mc.makeIdentity(orientString + "footHindHeelRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "footHindToeRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "footHindTipRoll_LOC", a=True, t=True, r=True, s=True)
			mc.makeIdentity(orientString + "footHindBallRoll_LOC", a=True, t=True, r=True, s=True)
			
			#Finally, set up new attributes on the foot control and connect them to the locator rotations
			mc.addAttr(orientString+"foot_ctrl", at='float', ln="HeelRoll", h=False, w=True)
			mc.setAttr(orientString+"foot_ctrl.HeelRoll", k=True, typ="float")
			mc.addAttr(orientString+"foot_ctrl", at='float', ln="ToeRoll", h=False, w=True)
			mc.setAttr(orientString+"foot_ctrl.ToeRoll", k=True, typ="float")
			mc.addAttr(orientString+"foot_ctrl", at='float', ln="TipRoll", h=False, w=True)
			mc.setAttr(orientString+"foot_ctrl.TipRoll", k=True, typ="float")
			
			mc.connectAttr(orientString+"foot_ctrl.HeelRoll", orientString + "footHindHeelRoll_LOC.rotateX")
			mc.connectAttr(orientString+"foot_ctrl.ToeRoll", orientString + "footHindToeRoll_LOC.rotateX")
			mc.connectAttr(orientString+"foot_ctrl.TipRoll", orientString + "footHindBallRoll_LOC.rotateX")

			#Set up a knee controller

			mc.curve(n=orientString+"knee_ctrl", p=[[-1.0, 0.0, 1.0], [1.0, 0.0, 1.0], [0.0, 0.0, -1.0], [-1.0, 0.0, 1.0]],d=1)
			tempPC = mc.pointConstraint(orientString + legJNames[1] + "_jnt", orientString+"knee_ctrl")
			mc.delete(tempPC)
			mc.move(5 * scaleFactor/2, orientString + "knee_ctrl", z=True, r=False)
			mc.poleVectorConstraint( orientString+"knee_ctrl", orientString + "upperLeg_ik")

		if function == "tail":

			#TAIL FUNCTION IS A WORK IN PROGRESS

			for i in range(0, selSize, 1):
				mc.rename(listObjs[i], "tail" + "% d_jnt" % num)
				num += 1

			#for i in range(0, selSize, 1):

				#if i % 2 == 0:
					#mc.circle(n="tail_" + "%d_ctrl" % i)

					#parentLoc = 

					#print "tail" + "% d_jnt" % i
					



				





def runMayaUiDemo():
	"""Command within Maya to run this script"""
	if not (mc.window("demoUI", exists=True)):
		templateUiDemo()
	else:
		sys.stdout.write("tool is already open!\n")


templateUiDemo()



