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

        # obj.addProperty("App::PropertyFloat", "InitialLoadingInmm", "Distributed", "Initial loading (load per unit length)")
        # obj.addProperty("App::PropertyFloat", "FinalLoadingInmm", "Distributed", "Final loading (load per unit length)")
        # obj.setEditorMode("InitialLoadingInmm", 2)
        # obj.setEditorMode("FinalLoadingInmm", 2)
        # obj.FinalLoadingInmm.Hidden = True
        # obj.InitialLoadingInmm.Hidden = True

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
"32 32 99 2",
"  	c None",
". 	c #030D22",
"+ 	c #0E3B93",
"@ 	c #1144AA",
"# 	c #0E398F",
"$ 	c #1658DD",
"% 	c #1966FF",
"& 	c #1556D6",
"* 	c #1860F0",
"= 	c #1452CC",
"- 	c #1555D5",
"; 	c #175EEA",
"> 	c #1861F2",
", 	c #0D3483",
"' 	c #030A17",
") 	c #030E26",
"! 	c #020611",
"~ 	c #1966FE",
"{ 	c #09255B",
"] 	c #030C1D",
"^ 	c #030917",
"/ 	c #0E388C",
"( 	c #0D337F",
"_ 	c #020C1E",
": 	c #092256",
"< 	c #0E3789",
"[ 	c #030918",
"} 	c #040D20",
"| 	c #165BE4",
"1 	c #0D398D",
"2 	c #020917",
"3 	c #030914",
"4 	c #020B1C",
"5 	c #01060F",
"6 	c #0A2863",
"7 	c #020916",
"8 	c #020A18",
"9 	c #020712",
"0 	c #01050F",
"a 	c #010815",
"b 	c #030D1F",
"c 	c #165AE1",
"d 	c #0E3687",
"e 	c #020B1D",
"f 	c #1862F6",
"g 	c #0A2966",
"h 	c #0E3C96",
"i 	c #1659DF",
"j 	c #030C1E",
"k 	c #0C317A",
"l 	c #031026",
"m 	c #1042A5",
"n 	c #1864F9",
"o 	c #020B1E",
"p 	c #04122D",
"q 	c #0C3078",
"r 	c #1965FD",
"s 	c #1450C8",
"t 	c #061637",
"u 	c #020A19",
"v 	c #1554D2",
"w 	c #030C1F",
"x 	c #030C1C",
"y 	c #134CBE",
"z 	c #092459",
"A 	c #165AE0",
"B 	c #06173B",
"C 	c #0B2A69",
"D 	c #124ABA",
"E 	c #020C1D",
"F 	c #081F4E",
"G 	c #0C3179",
"H 	c #1964FA",
"I 	c #081E49",
"J 	c #040C1E",
"K 	c #1760EF",
"L 	c #0F40A0",
"M 	c #1146AE",
"N 	c #020C1F",
"O 	c #041433",
"P 	c #020A1B",
"Q 	c #134CBD",
"R 	c #030F24",
"S 	c #07193F",
"T 	c #0E3A91",
"U 	c #04132F",
"V 	c #1659DE",
"W 	c #081F4D",
"X 	c #134DC1",
"Y 	c #030B1D",
"Z 	c #030D1E",
"` 	c #175CE6",
" .	c #041129",
"..	c #071E4C",
"+.	c #061B44",
"@.	c #082155",
"#.	c #01040B",
"$.	c #020815",
"%.	c #010307",
"                                                                ",
"                                                                ",
"                                                                ",
"    . + @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ @ # .     ",
"    . $ % % % % % % % % % % % % % % % % % % % % % % % % & .     ",
"    . $ % * = = = = = = = = - % % ; = = = = = = = = > % & .     ",
"    . $ % , ' ) ) ) ) ) ) ) ! ~ % { ] ) ) ) ) ) ) ^ / % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"    . $ % (                 _ ~ % :                 < % & .     ",
"[ } ! | % 1 2 }         3 4 5 ~ % 6 7 4       8 4 9 + % $ 0 4 a ",
"b c % % % % % d         e f % % % % % g         h % % % % % i j ",
"  k % % % % % l           m % % % % n o         p % % % % % q   ",
"  . r % % % s j           t % % % % @ u         b v % % % r w   ",
"  x y % % % z             b A % % % B             C % % % D E   ",
"    F % % f _               G % % | b             b H % % I     ",
"    J K % L                 . r % (               7 M % * N     ",
"      h % O                 P Q % R                 S % T       ",
"      U V w                   W X Y                 Z `  .      ",
"      b ..                    _ +.                    @.Z       ",
"        #.                      $.                    %.        "};
        """


class CommandLoadDistributed():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/load_distributed.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+L", # a default shortcut (optional)
                "MenuText": "Distributed Load",
                "ToolTip" : "Adds loads to the structure"}

    def Activated(self):
        # try:
        selections = list(FreeCADGui.Selection.getSelectionEx())
    
        for selection in selections:
            if selection.HasSubObjects: #Valida se a seleção possui sub objetos
                for subSelectionname in selection.SubElementNames:

                    doc = FreeCAD.ActiveDocument
                    obj = doc.addObject("Part::FeaturePython", "Load_Distributed")

                    print(subSelectionname)
                    objLoad = LoadDistributed(obj,(selection.Object, subSelectionname))
                    ViewProviderLoadDistributed(obj.ViewObject)
            else:
                # pass
                line = selection.Object
                edges = line.Shape.Edges
                for i in range(len(edges)):
                    doc = FreeCAD.ActiveDocument
                    obj = doc.addObject("Part::FeaturePython", "Load_Distributed")
                    LoadDistributed(obj,(selection.Object, 'Edge'+str(i+1)))
                    ViewProviderLoadDistributed(obj.ViewObject)

        
        FreeCAD.ActiveDocument.recompute()
        # except:
        #     show_error_message("Seleciona uma barra para adicionar um carregamento distribuido.")
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""
        return True

FreeCADGui.addCommand("load_distributed", CommandLoadDistributed())
