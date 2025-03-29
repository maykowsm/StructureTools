import os
import FreeCADGui as Gui
import FreeCAD as App
import subprocess


translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

try:
	from Pynite import FEModel3D
except:
	print('Instalando dependencias')
	subprocess.check_call(["pip", "install", "PyniteFEA"])

class StructureTools(Gui.Workbench):
	"""
	class which gets initiated at startup of the gui
	"""
	MenuText = translate("Workbench", "StructureTools")
	ToolTip = translate("Workbench", "a simple StructureTools")
	Icon = os.path.join(ICONPATH, "icone.svg")
	toolbox = []

	def GetClassName(self):
		return "Gui::PythonWorkbench"

	def Initialize(self):
		"""
		This function is called at the first activation of the workbench.
		here is the place to import all the commands
		"""
		from freecad.StructureTools import load_distributed
		from freecad.StructureTools import load_nodal
		from freecad.StructureTools import suport
		from freecad.StructureTools import section
		from freecad.StructureTools import material
		from freecad.StructureTools import member
		from freecad.StructureTools import calc
		from freecad.StructureTools import diagram

		
		import DraftTools, SketcherGui, BIMGui
		# NOTE: Context for this commands must be "Workbench"
		self.appendToolbar('DraftDraw', ["Sketcher_NewSketch","Draft_Line", "Draft_Wire", "Draft_ArcTools", "Draft_BSpline"])
		self.appendToolbar('DraftEdit', ["Draft_Move", "Draft_Rotate", "Draft_Clone", "Draft_Offset", "Draft_Trimex", "Draft_Join", "Draft_Split","Draft_Stretch","Draft_Draft2Sketch"])
		self.appendToolbar('DraftSnap', ["Draft_Snap_Lock", "Draft_Snap_Endpoint", "Draft_Snap_Midpoint", "Draft_Snap_Center", "Draft_Snap_Angle", "Draft_Snap_Intersection", "Draft_Snap_Perpendicular", "Draft_Snap_Extension", "Draft_Snap_Parallel", "Draft_Snap_Special", "Draft_Snap_Near", "Draft_Snap_Ortho", "Draft_Snap_Grid", "Draft_Snap_WorkingPlane", "Draft_Snap_Dimensions", "Draft_ToggleGrid"])
		self.appendToolbar('DraftTools', ["Draft_SelectPlane", "Draft_SetStyle"])

		self.appendToolbar('StructureLoad', ["load_distributed","load_nodal"])
		self.appendToolbar('StructureTools', ["member", "suport", "section", "material"])
		self.appendToolbar('StructureResults', ["calc","diagram"])
		self.appendMenu('StructureTools',["load_distributed", "load_nodal","member" ,"suport", "section", "material", "calc", "diagram"])

	def Activated(self):
		'''
		code which should be computed when a user switch to this workbench
		'''
		

		App.Console.PrintMessage(translate(
			"Log",
			"Workbench StructureTools activated.") + "\n")

	def Deactivated(self):
		'''
		code which should be computed when this workbench is deactivated
		'''
		App.Console.PrintMessage(translate(
			"Log",
			"Workbench StructureTools de-activated.") + "\n")


Gui.addWorkbench(StructureTools())
