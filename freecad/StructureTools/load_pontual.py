import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets
from .utils_func import rotate_to_direction, make_arrow, set_obj_appear, BASE_ARROWS_DIM
from .load_base_class import LoadBaseClass

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class LoadNodal(LoadBaseClass):
    def __init__(self, obj, selection):
        super().__init__(obj, selection)
        obj.addProperty("App::PropertyForce", "NodalLoading", "Pontual", "Nodal loading").NodalLoading = 0
        obj.addProperty("App::PropertyLength", "NodalLoadingAt", "Pontual", "Nodal loading At (distance from start)").NodalLoadingAt = 0

    def execute(self, obj):        
        subelement = self.getSubelement(obj, obj.ObjectBase[0][1][0])
        if obj.NodalLoading == 0:
            obj.NodalLoading = self.base_value

        shape = make_arrow(obj.NodalLoading,**BASE_ARROWS_DIM, scale=obj.ScaleDraw)
        rotate_to_direction(obj.GlobalDirection, shape)
        shape.translate(subelement.Vertexes[0].Point)
        set_obj_appear(obj,1)
        
        if 'Edge' in obj.ObjectBase[0][1][0]:
            if obj.NodalLoadingAt > subelement.Length:
                obj.NodalLoadingAt = 0

            for coordinades in self.get_arrow_coordinades(0,subelement, obj.NodalLoadingAt):

                shape.translate(coordinades)
                obj.Label = 'Pontual load'

        else:
            obj.NodalLoadingAt = 0
            obj.Label = 'Nodal load'

        obj.Placement = shape.Placement
        obj.Shape = shape
        obj.ViewObject.DisplayMode = 'Shaded'
    

class ViewProviderLoadNodal:
    def __init__(self, obj):
        obj.Proxy = self
    

    def getIcon(self):
        return """
              /* XPM */
static char * load_nodal_xpm[] = {
"32 32 36 1",
" 	c None",
".	c #110101",
"+	c #220303",
"@	c #1C0303",
"#	c #190303",
"$	c #200303",
"%	c #FF1919",
"&	c #DC1616",
"*	c #1A0303",
"=	c #1D0303",
"-	c #190202",
";	c #DE1616",
">	c #100101",
",	c #160202",
"'	c #D11414",
")	c #DD1616",
"!	c #E61717",
"~	c #790C0C",
"{	c #E71717",
"]	c #E91717",
"^	c #180202",
"/	c #5D0A0A",
"(	c #5D0909",
"_	c #1B0202",
":	c #D51515",
"<	c #D81515",
"[	c #1A0202",
"}	c #420707",
"|	c #420606",
"1	c #C31313",
"2	c #C61313",
"3	c #2D0404",
"4	c #FE1919",
"5	c #2E0404",
"6	c #A91010",
"7	c #210303",
"             .+++@#             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"             $%%%&$             ",
"          *==-%%%;>==*          ",
"          ,')!%%%%;)',          ",
"           ~%%%%%%%%~           ",
"           -{%%%%%%]^           ",
"            /%%%%%%(            ",
"            _:%%%%<[            ",
"             }%%%%|             ",
"             #1%%2@             ",
"              34%5              ",
"              ^66*              ",
"               77               ",
"                                "};
        """


class CommandLoadNodal():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/load_nodal.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+N", # a default shortcut (optional)
                "MenuText": "Nodal load",
                "ToolTip" : "Adds loads to the structure"}

    def Activated(self):
        try:
            selections = list(FreeCADGui.Selection.getSelectionEx())        
            for selection in selections:
                for subSelectionname in selection.SubElementNames:

                    doc = FreeCAD.ActiveDocument
                    obj = doc.addObject("Part::FeaturePython", "Load_Nodal")

                    objLoad = LoadNodal(obj,(selection.Object, subSelectionname))
                    ViewProviderLoadNodal(obj.ViewObject)
            
            FreeCAD.ActiveDocument.recompute()
        except:
            show_error_message("Seleciona um ponto ou uma barra para adicionar um carregamento.")
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

FreeCADGui.addCommand("load_nodal", CommandLoadNodal())
