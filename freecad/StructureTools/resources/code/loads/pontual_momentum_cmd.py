import FreeCAD, FreeCADGui
from freecad.StructureTools.resources.code.base_cmd_class.cmd_base_class import _Command_Class_Model
from freecad.StructureTools.resources.code.loads.loads_code.pontual_momentum_code import PontualMomentumLoad
from freecad.StructureTools.resources.code.loads.loads_code.view_provider_load import ViewProviderMomentumLoad
# from .structure_codes.pontual_momentum_code import PontualMomentumLoad

class PontualMomentumLoadCmd(_Command_Class_Model):
	"""Cria Carga distribuida para elemento selecionado"""

	_cmd_name = 'Momento Pontual'
	_cmd_tip = 'Coloca carga de Momento Pontual no Elemento ou nó!'
	_icon_name = "load_momentum.svg" #TODO corrigir com icone correto
	_accel = "m,l"

	def Activated(self):
		try:
			selections = list(FreeCADGui.Selection.getSelectionEx())        
			for selection in selections:
				for subSelectionname in selection.SubElementNames:

					doc = FreeCAD.ActiveDocument
					obj = doc.addObject("Part::FeaturePython", "Load")

					PontualMomentumLoad(obj,(selection.Object, subSelectionname))
					ViewProviderMomentumLoad(obj.ViewObject)
			
			FreeCAD.ActiveDocument.recompute()
		except:
			print("Seleciona um ponto ou uma barra para adicionar um carregamento.")
		return
    
	def IsActive(self):
		return super().IsActive()
	
# FreeCADGui.addCommand("pontual_momentum_load", PontualMomentumLoadCmd())

