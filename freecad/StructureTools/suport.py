import FreeCAD, App, FreeCADGui, Part, os
from PySide6 import QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class Suport:
    def __init__(self, obj, selection):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubList", "ObjectBase", "Base", "Object base")

        obj.addProperty("App::PropertyBool", "FixTranslationX", "Translation", "Nodal loading").FixTranslationX = True
        obj.addProperty("App::PropertyBool", "FixTranslationY", "Translation", "Nodal loading").FixTranslationY = True
        obj.addProperty("App::PropertyBool", "FixTranslationZ", "Translation", "Nodal loading").FixTranslationZ = True

        obj.addProperty("App::PropertyBool", "FixRotationX", "Rotation", "Nodal loading").FixRotationX = True
        obj.addProperty("App::PropertyBool", "FixRotationY", "Rotation", "Nodal loading").FixRotationY = True
        obj.addProperty("App::PropertyBool", "FixRotationZ", "Rotation", "Nodal loading").FixRotationZ = True
        
        obj.addProperty("App::PropertyFloat", "ScaleDraw", "Draw", "Scale from drawing").ScaleDraw = 1
        
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

    # Desenha a forma do cone com a base quadrada
    def makeCone(self, obj, simples = False):
        radiusCone = 100
        heightCone = 200
        lengthPlate = 220
        heigthPlate = 20
        gap = 20
        

        cone = Part.makeCone(radiusCone * obj.ScaleDraw , 0, heightCone * obj.ScaleDraw )
        cone.translate(FreeCAD.Vector(0,0, -heightCone * obj.ScaleDraw))
        box = Part.makeBox(lengthPlate * obj.ScaleDraw, lengthPlate * obj.ScaleDraw, heigthPlate * obj.ScaleDraw) 
        box.translate(FreeCAD.Vector(-lengthPlate/2 * obj.ScaleDraw, -lengthPlate/2 * obj.ScaleDraw, (-heigthPlate - gap - heightCone )* obj.ScaleDraw))
        
        if simples:
            return cone
        else:
            return Part.makeCompound([cone, box])
    
    # Desenha o simbolo do engaste ou restrição de rotação em algum eixo no caso de pinos
    def makebox(self, obj, restricao = False):
        lenghtBox = 220
        heigthBox = 40
        minbox = 50

        if restricao:
            box = Part.makeBox(minbox * obj.ScaleDraw, minbox * obj.ScaleDraw, minbox * obj.ScaleDraw)
            box.translate(FreeCAD.Vector(-minbox/2 * obj.ScaleDraw, -minbox/2 * obj.ScaleDraw, - minbox * obj.ScaleDraw))
        else:
            box = Part.makeBox(lenghtBox * obj.ScaleDraw, lenghtBox * obj.ScaleDraw, heigthBox * obj.ScaleDraw)
            box.translate(FreeCAD.Vector(-lenghtBox/2 * obj.ScaleDraw, -lenghtBox/2 * obj.ScaleDraw, - heigthBox * obj.ScaleDraw))

        return box
    
    def execute(self, obj):        
        subelement = self.getSubelement(obj, obj.ObjectBase[0][1][0])
        
        listSimbols = []
        
        # Caso for um engaste
        if obj.FixTranslationX and obj.FixTranslationY and obj.FixTranslationZ and obj.FixRotationX and obj.FixRotationY and obj.FixRotationZ:
            box = self.makebox(obj)
            listSimbols.append(box)
            
        else:

            # Caso seja um pino   
            if obj.FixTranslationX and obj.FixTranslationY and obj.FixTranslationZ:
                cone = self.makeCone(obj, True)
                listSimbols.append(cone)
                
            else:
                
                if obj.FixTranslationX:
                    cone = self.makeCone(obj)
                    cone.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(0,1,0), 90)
                    listSimbols.append(cone)
                
                if obj.FixTranslationY:
                    cone = self.makeCone(obj)
                    cone.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 90)
                    listSimbols.append(cone)
                
                if obj.FixTranslationZ:
                    cone = self.makeCone(obj)
                    # cone.rotate(FreeCAD.Vector(0,0,0), FreeCAD.Vector(1,0,0), 90)
                    listSimbols.append(cone)
            
            if obj.FixRotationX or obj.FixRotationY or obj.FixRotationZ:
                box = self.makebox(obj, True)
                listSimbols.append(box)

        simbol = Part.makeCompound(listSimbols)
        simbol.translate(subelement.Point)

        obj.Shape = Part.makeCompound(listSimbols)
        obj.Placement.Base = simbol.Placement.Base
        obj.ViewObject.DisplayMode = 'Shaded'
        obj.ViewObject.ShapeAppearance = (FreeCAD.Material(DiffuseColor=(0.00,0.67,0.00),AmbientColor=(0.00,0.00,0.00),SpecularColor=(0.00,0.00,0.00),EmissiveColor=(0.00,0.00,0.00),Shininess=(0.90),Transparency=(0.00),))
        obj.Label = 'Suport'
        
        
       


    def onChanged(self,obj,Parameter):
        if Parameter == 'edgeLength':
            self.execute(obj)
    

class ViewProviderSuport:
    def __init__(self, obj):
        obj.Proxy = self
    

    def getIcon(self):
        return """
/* XPM */
static char * suport_xpm[] = {
"32 32 148 2",
"  	c None",
". 	c #000B00",
"+ 	c #001600",
"@ 	c #000900",
"# 	c #008800",
"$ 	c #0E950E",
"% 	c #000A00",
"& 	c #005300",
"* 	c #00AB00",
"= 	c #44CE50",
"- 	c #005200",
"; 	c #001900",
"> 	c #00A800",
", 	c #4ACA65",
"' 	c #2EC431",
") 	c #001A00",
"! 	c #008D00",
"~ 	c #38BD58",
"{ 	c #58D66E",
"] 	c #119A11",
"^ 	c #000700",
"/ 	c #005900",
"( 	c #28B449",
"_ 	c #4CC96F",
": 	c #4FD55A",
"< 	c #015801",
"[ 	c #001F00",
"} 	c #00A900",
"| 	c #1CAE38",
"1 	c #3DBC66",
"2 	c #55D172",
"3 	c #31C632",
"4 	c #001D00",
"5 	c #000800",
"6 	c #008F00",
"7 	c #11AB27",
"8 	c #2FB358",
"9 	c #46C26B",
"0 	c #5BD86F",
"a 	c #119F11",
"b 	c #005E00",
"c 	c #08AA15",
"d 	c #21AD47",
"e 	c #37B861",
"f 	c #4FCA70",
"g 	c #51D75A",
"h 	c #015D01",
"i 	c #002100",
"j 	c #01AA04",
"k 	c #14A931",
"l 	c #29B052",
"m 	c #3FBE67",
"n 	c #58D372",
"o 	c #33C934",
"p 	c #002300",
"q 	c #009300",
"r 	c #09A917",
"s 	c #1CAB3E",
"t 	c #31B45B",
"u 	c #48C56D",
"v 	c #5EDB71",
"w 	c #13A313",
"x 	c #006400",
"y 	c #0FA927",
"z 	c #23AD4A",
"A 	c #39BA63",
"B 	c #51CD71",
"C 	c #54D95B",
"D 	c #016301",
"E 	c #002700",
"F 	c #00AA00",
"G 	c #04AA0B",
"H 	c #16AA35",
"I 	c #2BB154",
"J 	c #42C069",
"K 	c #5AD673",
"L 	c #36CB36",
"M 	c #002800",
"N 	c #009700",
"O 	c #0BA91C",
"P 	c #1EAC42",
"Q 	c #33B55D",
"R 	c #4AC76E",
"S 	c #61DD71",
"T 	c #14A514",
"U 	c #006900",
"V 	c #11A92B",
"W 	c #25AF4D",
"X 	c #3BBA64",
"Y 	c #54CF71",
"Z 	c #58DD5D",
"` 	c #026902",
" .	c #002C00",
"..	c #06AA10",
"+.	c #18AA39",
"@.	c #2DB357",
"#.	c #44C16A",
"$.	c #5DD873",
"%.	c #37CC37",
"&.	c #002B00",
"*.	c #009800",
"=.	c #0CA920",
"-.	c #20AD45",
";.	c #35B75F",
">.	c #4DC96F",
",.	c #65E171",
"'.	c #14A914",
").	c #006E00",
"!.	c #01AB03",
"~.	c #13A92F",
"{.	c #27B050",
"].	c #3EBC66",
"^.	c #56D172",
"/.	c #5CE05D",
"(.	c #026E02",
"_.	c #002F00",
":.	c #08AA14",
"<.	c #1AAA3C",
"[.	c #2FB459",
"}.	c #46C36C",
"|.	c #60DB74",
"1.	c #39CE39",
"2.	c #003200",
"3.	c #009C00",
"4.	c #0EA924",
"5.	c #22AD48",
"6.	c #38B861",
"7.	c #4FCB70",
"8.	c #67E572",
"9.	c #17AE17",
"0.	c #000C00",
"a.	c #007200",
"b.	c #02AB06",
"c.	c #13AA2D",
"d.	c #29B050",
"e.	c #40BE68",
"f.	c #59D473",
"g.	c #5DE35D",
"h.	c #027802",
"i.	c #009400",
"j.	c #059609",
"k.	c #0F9D17",
"l.	c #1FAA24",
"m.	c #0E9F0E",
"n.	c #001200",
"o.	c #000D00",
"p.	c #000600",
"q.	c #00A000",
"                              . .                               ",
"                              + +                               ",
"                            @ # $ @                             ",
"                          % & * = - .                           ",
"                          ; > * , ' )                           ",
"                        @ ! * * ~ { ] ^                         ",
"                      % / * * * ( _ : < .                       ",
"                      [ } * * * | 1 2 3 4                       ",
"                    5 6 * * * * 7 8 9 0 a ^                     ",
"                  . b * * * * * c d e f g h %                   ",
"                  i } * * * * * j k l m n o p                   ",
"                5 q * * * * * * * r s t u v w 5                 ",
"              % x * * * * * * * * * y z A B C D %               ",
"              E F * * * * * * * * * G H I J K L M               ",
"            @ N * * * * * * * * * * * O P Q R S T 5             ",
"          % U * * * * * * * * * * * * * V W X Y Z ` %           ",
"           .* * * * * * * * * * * * * * ..+.@.#.$.%.&.          ",
"        @ *.* * * * * * * * * * * * * * * =.-.;.>.,.'.@         ",
"      % ).* * * * * * * * * * * * * * * * !.~.{.].^./.(.@       ",
"    5 _.* * * * * * * * * * * * * * * * * * :.<.[.}.|.1.2.5     ",
"    % 3.* * * * * * * * * * * * * * * * * * * 4.5.6.7.8.9.0.    ",
"  . a.* * * * * * * * * * * * * * * * * * * * b.c.d.e.f.g.h.@   ",
"^ M i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.q j.k.l.m.E 5 ",
"% n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.n.% ",
"                                                                ",
"% o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.o.% ",
"p.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.i.p.",
"p.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.q.p.",
"5 % % % % % % % % % % % % % % % % % % % % % % % % % % % % % % 5 ",
"                                                                ",
"                                                                ",
"                                                                "};
        """


class CommandSuport():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/suport.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+S", # a default shortcut (optional)
                "MenuText": "Suport",
                "ToolTip" : "Adds suport to the structure"}

    def Activated(self):

        try:
            selections = list(FreeCADGui.Selection.getSelectionEx())        
            for selection in selections:
                for subSelectionname in selection.SubElementNames:
                    if not 'Edge' in subSelectionname:
                        doc = FreeCAD.ActiveDocument
                        obj = doc.addObject("Part::FeaturePython", "Suport")

                        objSuport = Suport(obj,(selection.Object, subSelectionname))
                        ViewProviderSuport(obj.ViewObject)
                    else:
                        show_error_message("Seleciona um nó para adicionar um suporte.")
            
            FreeCAD.ActiveDocument.recompute()
        except:
            show_error_message("Seleciona um nó para adicionar um suporte.")
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("suport", CommandSuport())
