import FreeCAD, FreeCADGui
from freecad.StructureTools.resources.code.base_cmd_class.cmd_base_class import _Command_Class_Model
from freecad.StructureTools.resources.code.loads.loads_code.distri_load_code import DistLoad
# from .structure_codes.pontual_force_code import PontualForceLoad
from freecad.StructureTools.resources.code.loads.loads_code.view_provider_load import ViewProviderDistLoad
# from .structure_codes.pontual_momentum_code import PontualMomentumLoad

class DistLoadCmd(_Command_Class_Model):
	"""Cria Carga distribuida para elemento selecionado"""

	_cmd_name = 'Carga Distribuida'
	_cmd_tip = 'Coloca carga Distribuida no Elemento (quanto uma linha for selecionada )'
	_icon_name = "load_distributed.svg"
	_accel = "d,l"

	def Activated(self):
		try:
			selections = list(FreeCADGui.Selection.getSelectionEx())        
			for selection in selections:
				for subSelectionname in selection.SubElementNames:

					doc = FreeCAD.ActiveDocument
					obj = doc.addObject("Part::FeaturePython", "Load")

					DistLoad(obj,(selection.Object, subSelectionname))
					ViewProviderDistLoad(obj.ViewObject)
			
			FreeCAD.ActiveDocument.recompute()
		except:
			print("Seleciona um ponto ou uma barra para adicionar um carregamento.")
			#TODO: Msg de erro nao aparece quando nao há elementos selecionados
			self.show_error_message("Seleciona um ponto ou uma barra para adicionar um carregamento.")
		return
    
	def IsActive(self):
		return super().IsActive()
	
# FreeCADGui.addCommand("load_distributed", DistLoadCmd())

