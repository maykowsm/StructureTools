import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets
from .utils_func import rotate_to_direction, make_momentum_arrow, set_obj_appear, BASE_ARROWS_DIM
from .load_base_class import LoadBaseClass

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class LoadMomentum(LoadBaseClass):
    def __init__(self, obj, selection):
        super().__init__(obj, selection)
        obj.addProperty("App::PropertyForce", "NodalLoading", "Momentum", "Nodal loading").NodalLoading = 0
        obj.addProperty("App::PropertyLength", "NodalLoadingAt", "Momentum", "Nodal loading At (distance from start)").NodalLoadingAt = 0

    def execute(self, obj):        
        subelement = self.getSubelement(obj, obj.ObjectBase[0][1][0])
        if obj.NodalLoading == 0:
            obj.NodalLoading = self.base_value

        shape = make_momentum_arrow(obj.NodalLoading,**BASE_ARROWS_DIM, scale=obj.ScaleDraw)
        rotate_to_direction(obj.GlobalDirection, shape)
        shape.translate(subelement.Vertexes[0].Point)
        set_obj_appear(obj,2)
        
        if 'Edge' in obj.ObjectBase[0][1][0]:
            if obj.NodalLoadingAt > subelement.Length:
                obj.NodalLoadingAt = 0

            for coordinades in self.get_arrow_coordinades(0,subelement, obj.NodalLoadingAt):

                shape.translate(coordinades)
                obj.Label = 'Momentum Load'

        else:
            obj.NodalLoadingAt = 0
            obj.Label = 'Momentum load'

        obj.Placement = shape.Placement
        obj.Shape = shape
        obj.ViewObject.DisplayMode = 'Shaded'
    

class ViewProviderLoadMomentum:
    def __init__(self, obj):
        obj.Proxy = self
    

    def getIcon(self):
        return """/* XPM */
static char * load_momentum_2_xpm[] = {
"18 16 60 1",
" 	c None",
".	c #000F00",
"+	c #001000",
"@	c #003A00",
"#	c #000E00",
"$	c #001300",
"%	c #005301",
"&	c #008401",
"*	c #008901",
"=	c #006B01",
"-	c #002A00",
";	c #001100",
">	c #00C801",
",	c #007301",
"'	c #000900",
")	c #003500",
"!	c #00BC01",
"~	c #006801",
"{	c #002F00",
"]	c #002100",
"^	c #003F00",
"/	c #009201",
"(	c #00A101",
"_	c #001A00",
":	c #009801",
"<	c #00B101",
"[	c #001D00",
"}	c #000C00",
"|	c #003400",
"1	c #00B601",
"2	c #001E00",
"3	c #008301",
"4	c #002E00",
"5	c #00AF01",
"6	c #008001",
"7	c #007E01",
"8	c #004700",
"9	c #001C00",
"0	c #002900",
"a	c #009101",
"b	c #001200",
"c	c #001500",
"d	c #00B501",
"e	c #009001",
"f	c #004500",
"g	c #002D00",
"h	c #001400",
"i	c #002600",
"j	c #003200",
"k	c #001F00",
"l	c #002000",
"m	c #00AE01",
"n	c #008201",
"o	c #001700",
"p	c #001900",
"q	c #008A01",
"r	c #00A601",
"s	c #003900",
"t	c #009D01",
"u	c #007B01",
"        .+        ",
" .@#  $%&*=-+     ",
" ;>,')!~{]^/(_    ",
" ;>>:<[}   +|12   ",
" ;>>>3}      45+  ",
" ;>>>>6.     .78  ",
" +&&&&&9      0ab ",
"  +++++       c1b ",
"              cd; ",
"              -eb ",
"             #6f  ",
"             g5+  ",
"    hi.    .j1k   ",
"    lmnjop|qr[    ",
"     +s7ttu|.     ",
"       #hh}       "};
 """


class CommandLoadMomentum():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/load_momentum.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+M", # a default shortcut (optional)
                "MenuText": "Momentum load",
                "ToolTip" : "Adds momentum loads to the structure"}

    def Activated(self):
        try:
            selections = list(FreeCADGui.Selection.getSelectionEx())        
            for selection in selections:
                for subSelectionname in selection.SubElementNames:

                    doc = FreeCAD.ActiveDocument
                    obj = doc.addObject("Part::FeaturePython", "Load_Nodal")

                    objLoad = LoadMomentum(obj,(selection.Object, subSelectionname))
                    ViewProviderLoadMomentum(obj.ViewObject)
            
            FreeCAD.ActiveDocument.recompute()
        except:
            show_error_message("Seleciona um ponto ou uma barra para adicionar um carregamento.")
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

FreeCADGui.addCommand("load_momentum", CommandLoadMomentum())
