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


class LoadDistributed:
    def __init__(self, obj, selection):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubList", "ObjectBase", "Base", "Object base")
        obj.addProperty("App::PropertyForce", "InitialLoading", "Distributed", "Initial loading (load per unit length)").InitialLoading = 10000000
        obj.addProperty("App::PropertyForce", "FinalLoading", "Distributed", "Final loading (load per unit length)").FinalLoading = 10000000
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
        if 'Edge' in obj.ObjectBase[0][1][0]:
            k = 1000000
            nArrow = int(k * (subelement.Length**(1/1.8))/(obj.ScaleDraw * ((obj.InitialLoading + obj.FinalLoading) / 2))) #calcula o numero de setas com base na distancia do menbro, escala do desenho e media das forças de inicio e fim
            
            

            FEend = obj.FinalLoading / obj.InitialLoading #fator de escala entre as forças 'end' e 'start'
            distEndStart = subelement.Length

            # Gera a lista de pontos 
            pInit = subelement.Vertexes[0].Point
            dist = subelement.Length / nArrow
            distx = (subelement.Vertexes[1].Point.x - subelement.Vertexes[0].Point.x) / nArrow #Calcula a distancia entre cada seta no eixo x
            disty = (subelement.Vertexes[1].Point.y - subelement.Vertexes[0].Point.y) / nArrow #Calcula a distancia entre cada seta no eixo y
            distz = (subelement.Vertexes[1].Point.z - subelement.Vertexes[0].Point.z) / nArrow #Calcula a distancia entre cada seta no eixo z
            listPoints = []
            for i in range(nArrow + 1):
                x = distx * i 
                y = disty * i 
                z = distz * i 
                listPoints.append(FreeCAD.Vector(x,y,z))

            # gera a lista de setas já em suas devidas escalas e nas devidas distancia posicionadas sobre o eixo X
            listArrow = []            
            for i in range(nArrow + 1):
                arrowCopy = self.makeArrow(obj, obj.InitialLoading)
                listArrow.append(arrowCopy)
                Fe = ((dist * i * (FEend - 1)) / distEndStart)  + 1 #calculo do fator de escala               
                
                match obj.GlobalDirection:
                    case '+X':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,1,0), -90)
                    case '-X':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,1,0), 90)
                    case '+Y':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 90)
                    case '-Y':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), -90)
                    case '+Z':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 180)
                    case '-Z':
                        arrowCopy.rotate(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,0,0), 0)
                
                arrowCopy.scale(Fe)
                arrowCopy.translate(listPoints[i])
                listArrow.append(arrowCopy)

            shape = Part.makeCompound(listArrow)
            shape.translate(subelement.Vertexes[0].Point)
            obj.ViewObject.ShapeAppearance = (FreeCAD.Material(DiffuseColor=(0.00,0.00,1.00),AmbientColor=(0.33,0.33,0.33),SpecularColor=(0.53,0.53,0.53),EmissiveColor=(0.00,0.00,0.00),Shininess=(0.90),Transparency=(0.00),))
            obj.Label = 'distributed load'


        obj.Placement = shape.Placement
        obj.Shape = shape
        obj.ViewObject.DisplayMode = 'Shaded'
        
        
       


    def onChanged(self,obj,Parameter):
        if Parameter == 'edgeLength':
            self.execute(obj)
    

class ViewProviderLoadDistributed:
    def __init__(self, obj):
        obj.Proxy = self
    

    def getIcon(self):
        return """
               /* XPM */
static char * load_distributed_xpm[] = {
"32 32 8 1",
" 	c None",
".	c #1966FF",
"+	c #1866FF",
"@	c #1A66FF",
"#	c #1A67FF",
"$	c #1965FF",
"%	c #1A65FF",
"&	c #1967FF",
"                                ",
"                                ",
"                                ",
"  ...........................+  ",
"  ............................  ",
"  ............................  ",
"  ...@        #..@        @...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  ...$         ...        $...  ",
"  %...        &..&        %..@  ",
"$......$    #.......    $......#",
" ......      ......$     ...... ",
" +.....      &.....      ...... ",
"  ....$       ....$      $....  ",
"  @...        ....        ....  ",
"  $..+        #..@        ...#  ",
"   ..          ...         ..   ",
"   ..          ..          ..   ",
"   $$           +          $.   ",
"                                "};
        """


class CommandLoadDistributed():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/load_distributed.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+L", # a default shortcut (optional)
                "MenuText": "Distributed Load",
                "ToolTip" : "Adds loads to the structure"}

    def Activated(self):
        try:
            selections = list(FreeCADGui.Selection.getSelectionEx())        
            for selection in selections:
                for subSelectionname in selection.SubElementNames:

                    doc = FreeCAD.ActiveDocument
                    obj = doc.addObject("Part::FeaturePython", "Load_Distributed")

                    objLoad = LoadDistributed(obj,(selection.Object, subSelectionname))
                    ViewProviderLoadDistributed(obj.ViewObject)
            
            FreeCAD.ActiveDocument.recompute()
        except:
            show_error_message("Seleciona um ponto ou uma barra para adicionar um carregamento.")
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

FreeCADGui.addCommand("load_distributed", CommandLoadDistributed())
