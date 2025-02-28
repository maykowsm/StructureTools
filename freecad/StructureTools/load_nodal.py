import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class LoadNodal:
    def __init__(self, obj, selection):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubList", "ObjectBase", "Base", "Object base")
        obj.addProperty("App::PropertyForce", "NodalLoading", "Nodal", "Nodal loading").NodalLoading = 10000000
        obj.addProperty("App::PropertyFloat", "ScaleDraw", "Load", "Scale from drawing").ScaleDraw = 1
        
        obj.addProperty("App::PropertyEnumeration", "GlobalDirection","Load","Global direction load")
        obj.GlobalDirection = ['+X','-X', '+Y','-Y', '+Z','-Z']
        obj.GlobalDirection = '-Z'
        
        print(selection)
        obj.ObjectBase = (selection[0], selection[1])
    
    # Desenha carregamento pontual
    def drawNodeLoad(self, obj, vertex):
        pass
    
    # Retorna o subelemento asociado
    def getSubelement(self, obj, nameSubElement):
        
        if 'Edge' in  nameSubElement:
            index = int(nameSubElement.split('Edge')[1]) - 1
            return obj.ObjectBase[0][0].Shape.Edges[index]
        else:
            index = int(nameSubElement.split('Vertex')[1]) - 1
            return obj.ObjectBase[0][0].Shape.Vertexes[index]

    # Desenha a forma da seta levando em conta a escala informada
    def makeArrow(self, obj, load):
        radiusCone = 5
        heightCone = 20
        heightCylinder = 30
        radiusCylinder = 2

        cone = Part.makeCone(0 ,radiusCone * obj.ScaleDraw * load/1000000, heightCone * obj.ScaleDraw * load/1000000)
        cylinder = Part.makeCylinder(radiusCylinder * obj.ScaleDraw * load/1000000, heightCylinder * obj.ScaleDraw * load/1000000)        
        cylinder.translate(FreeCAD.Vector(0,0, heightCone * obj.ScaleDraw * load/1000000))
        return Part.makeCompound([cone, cylinder])
    
    
    def execute(self, obj):        
        subelement = self.getSubelement(obj, obj.ObjectBase[0][1][0])
        if 'Vertex' in obj.ObjectBase[0][1][0]:
            # Desenha carregamento pontual 
            shape = self.makeArrow(obj, obj.NodalLoading)
            
            match obj.GlobalDirection:
                case '+X':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,1,0), -90)
                case '-X':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,1,0), 90)
                case '+Y':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 90)
                case '-Y':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), -90)
                case '+Z':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 180)
                case '-Z':
                    shape.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 0)
            
            
            shape.translate(subelement.Point)
            obj.ViewObject.ShapeAppearance = (FreeCAD.Material(DiffuseColor=(1.00,0.00,0.00),AmbientColor=(0.33,0.33,0.33),SpecularColor=(0.53,0.53,0.53),EmissiveColor=(0.00,0.00,0.00),Shininess=(0.90),Transparency=(0.00),))
            obj.Label = 'nodal load'

        obj.Placement = shape.Placement
        obj.Shape = shape
        obj.ViewObject.DisplayMode = 'Shaded'
        
        
       


    def onChanged(self,obj,Parameter):
        if Parameter == 'edgeLength':
            self.execute(obj)
    

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
