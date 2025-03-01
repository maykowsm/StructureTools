import FreeCAD, FreeCADGui
from freecad.StructureTools.resources.code.base_cmd_class.cmd_base_class import _Command_Class_Model
from freecad.StructureTools.resources.code.loads.loads_code.pontual_force_code import PontualForceLoad
from freecad.StructureTools.resources.code.loads.loads_code.view_provider_load import ViewProviderPontualLoad

class PontualForceLoadCmd(_Command_Class_Model):
	"""Cria Carga distribuida para elemento selecionado"""

	_cmd_name = 'Pontual'
	_cmd_tip = 'Coloca carga Pontual no Elemento ou nó!'
	_icon_name = "load_nodal.svg"
	_accel = "p,l"

	def Activated(self):
		try:
			selections = list(FreeCADGui.Selection.getSelectionEx())        
			for selection in selections:
				for subSelectionname in selection.SubElementNames:

					doc = FreeCAD.ActiveDocument
					obj = doc.addObject("Part::FeaturePython", "Load")

					objLoad = PontualForceLoad(obj,(selection.Object, subSelectionname))
					ViewProviderPontualLoad(obj.ViewObject)
			
			FreeCAD.ActiveDocument.recompute()
		except:
			print("Seleciona um ponto para adicionar um carregamento.")
			self.show_error_message("Seleciona um ponto para adicionar um carregamento.")

		return
    
	def IsActive(self):
		return super().IsActive()
	
# FreeCADGui.addCommand("pontual_force_load", PontualForceLoadCmd())

