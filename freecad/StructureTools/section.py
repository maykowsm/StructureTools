import FreeCAD, App, FreeCADGui, Part, os, math, copy
from PySide2 import QtWidgets
from PySide2.QtGui import QPixmap

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
# path_ui = str(os.path.dirname(__file__))+'/resources/ui/sectionGui.ui'

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class Section:
    def __init__(self, obj, selection):

        # Define os objetos pré celecionados
        objectSelected = (selection[0].Object, selection[0].SubElementNames[0]) if len(selection) > 0 else ()
            
        
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSub", "ObjectBase", "Base", "Object base").ObjectBase = objectSelected
        
        # Propriedades da seção
        obj.addProperty("App::PropertyFloat", "MomentInertiaY", "SectionProprety", "Inertia in the local Y axis").MomentInertiaY = 0.00
        obj.addProperty("App::PropertyFloat", "MomentInertiaZ", "SectionProprety", "Inertia in the local Z axis").MomentInertiaZ = 0.00
        obj.addProperty("App::PropertyFloat", "MomentInertiaPolar", "SectionProprety", "Polar Moment of Inertia J").MomentInertiaPolar = 0.00
        obj.addProperty("App::PropertyFloat", "ProductInertiaYZ", "SectionProprety", "Product of Inertia").ProductInertiaYZ = 0.00
        obj.addProperty("App::PropertyArea", "AreaSection", "SectionProprety", "Section area").AreaSection = 0.00

        obj.addProperty("App::PropertyBool", "ViewSection", "DrawSection", "Ver a seção no membro").ViewSection = False
        obj.addProperty("App::PropertyBool", "ViewFullSection", "DrawSection", "Ver a seção no membro").ViewFullSection = False
        


    # Faz a rotação da face para que a normal conicida com o vetor passado como argumento
    def rotate(self, face, normal, position = FreeCAD.Vector(0,0,0)):
        normal.normalize()
        try:
            normalface = face.normalAt(0,0)
        except:
            normalface = face.Faces[0].normalAt(0,0)
            

        rotacao = FreeCAD.Rotation(normalface, normal)
        faceRotacionada = face.transformGeometry(FreeCAD.Placement(position,rotacao).toMatrix())
        return faceRotacionada


    def execute(self, obj):
        objects = FreeCAD.ActiveDocument.Objects
        lines = list(filter(lambda object: 'Wire'in object.Name or 'Line' in object.Name, objects))

        # Valida se a seção possui um objeto atribuido e se o desenho da seção está ativo
        if obj.ObjectBase :
            # Captura as propriedaes da face e as adiciona aos seus respectivos campos
            face = obj.ObjectBase[0].getSubObject(obj.ObjectBase[1][0])
            if face.ShapeType == 'Face': # valida se o objeto é uma face

                
                cx, cy, cz = face.CenterOfMass
                A = face.Area
                Iy = face.MatrixOfInertia.A[5]
                Iz = face.MatrixOfInertia.A[0]
                Iyz = face.MatrixOfInertia.A[1] if abs(face.MatrixOfInertia.A[1]) > 1 else 0
                
                #Aplica o teorema de Steiner
                Iy = Iy + A * cx**2
                Iz = Iz + A * cy**2
                Iyz = Iyz + A * cx * cy


                obj.AreaSection = A
                obj.MomentInertiaZ = Iz
                obj.MomentInertiaY = Iy
                obj.ProductInertiaYZ = Iyz
                obj.MomentInertiaPolar = Iy + Iz                   

                # Valida se possuem elementos atribuidos a seção e adiciona a seção no centro do elemento
                listSections = []
                listBar = []
                if len(lines) > 0 and (obj.ViewSection == True or obj.ViewFullSection == True):
                    for line in lines:
                        section = face.copy()
                        if 'SectionMember' in line.PropertiesList: #valida se a linha possui a propriedade
                            if line.SectionMember: #Valida se a propriedade possui valor
                                if line.SectionMember.Name == obj.Name:
                                    rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), 90 + float(line.RotationSection)) #Gira em 90º a seção transversal (Posição padrão)
                                    section.Placement = FreeCAD.Placement(FreeCAD.Vector(0,0,0), rot)

                                    dx = line.Shape.Vertexes[1].Point.x - line.Shape.Vertexes[0].Point.x
                                    dy = line.Shape.Vertexes[1].Point.y - line.Shape.Vertexes[0].Point.y
                                    dz = line.Shape.Vertexes[1].Point.z - line.Shape.Vertexes[0].Point.z

                                    if not(abs(dx) < 1e-2 and abs(dy) < 1e-2): #valida se o elemento não está na vertical

                                        if obj.ViewSection:
                                            section1 = section.copy()
                                            section1 = self.rotate(section1, FreeCAD.Vector(1,0,0)) #Coloca a seção na vertical com a normal no eixo X
                                            section1 = self.rotate(section1, FreeCAD.Vector(dx, dy, 0)) #Coloca a seção na direção da projeção do elemento no plano
                                            section1 = self.rotate(section1, FreeCAD.Vector(dx, dy, dz), line.Shape.CenterOfGravity) #Coloca a seção na direção do elemento e translada  a seção para o centro do elemento                                    
                                            listSections.append(section1.copy())
                                        
                                        # Valida se a barra vai ser visualizada por completo
                                        if obj.ViewFullSection:
                                            section2 = section.copy()
                                            section2 = self.rotate(section2, FreeCAD.Vector(1,0,0)) #Coloca a seção na vertical com a normal no eixo X
                                            section2 = self.rotate(section2, FreeCAD.Vector(dx, dy, 0)) #Coloca a seção na direção da projeção do elemento no plano
                                            section2 = self.rotate(section2, FreeCAD.Vector(dx, dy, dz), line.Shape.Vertexes[0].Point) #Coloca a seção na direção do elemento e translada  a seção para o ponto inicial do elemento                                    

                                            bar = section2.extrude(section2.Faces[0].normalAt(0,0) * (line.Length))
                                            listBar.append(bar)
                                                                    
                                    else:
                                        rot = FreeCAD.Rotation(FreeCAD.Vector(0,0,1), 90 + float(line.RotationSection))
                                        section.Placement = FreeCAD.Placement(line.Shape.CenterOfGravity, rot)
                                        if obj.ViewSection:
                                            listSections.append(section.copy())
                                        
                                        # Valida se a barra vai ser visualizada por completo
                                        if obj.ViewFullSection:
                                            bar1 = section.extrude(section.Faces[0].normalAt(0,0) * (line.Length / 2))
                                            bar2 = section.extrude(section.Faces[0].normalAt(0,0) * (-line.Length / 2))
                                            bar = bar1.fuse([bar2])
                                            bar = bar.removeSplitter()
                                            listBar.append(bar)


                    shape = Part.makeCompound(listSections + listBar)
                    obj.Shape = shape
                else:
                    obj.Shape = Part.Shape()
        

    def onChanged(self,obj,Parameter):
        if Parameter == 'edgeLength':
            self.execute(obj)
    

class ViewProviderSection:
    def __init__(self, obj):
        obj.Proxy = self
    
    # def setupContextMenu(self, obj, menu):
    #     # Adiciona uma opção ao menu de contexto do objeto
    #     action = QtWidgets.QAction("Edit Section", menu)
    #     action.triggered.connect(lambda: self.editSection(obj))
    #     menu.addAction(action)
    
    # def editSection(self, obj):
    #     # Função executada ao clicar no menu de contexto
    #     FreeCAD.Console.PrintMessage(f"Objeto {obj.Object.Name} foi clicado!\n")
    #     janela = EditSectionGui(obj)
    #     FreeCADGui.Control.showDialog(janela)

    def getIcon(self):
        return """/* XPM */
static char * profile_xpm[] = {
"32 32 213 2",
"  	c None",
". 	c #060B17",
"+ 	c #09101D",
"@ 	c #0B1222",
"# 	c #0C1222",
"$ 	c #0C1422",
"% 	c #0D1422",
"& 	c #0D1522",
"* 	c #0E1522",
"= 	c #0F1522",
"- 	c #0F1622",
"; 	c #101622",
"> 	c #101722",
", 	c #111722",
"' 	c #121722",
") 	c #121822",
"! 	c #141822",
"~ 	c #141922",
"{ 	c #151922",
"] 	c #161A22",
"^ 	c #171A22",
"/ 	c #171B22",
"( 	c #14171D",
"_ 	c #101316",
": 	c #08101E",
"< 	c #4075E1",
"[ 	c #4C88FF",
"} 	c #518CFF",
"| 	c #568FFF",
"1 	c #5B92FF",
"2 	c #6095FF",
"3 	c #6599FF",
"4 	c #6A9CFF",
"5 	c #6F9FFF",
"6 	c #73A2FF",
"7 	c #78A6FF",
"8 	c #7DA9FF",
"9 	c #82ACFF",
"0 	c #87AFFF",
"a 	c #8CB3FF",
"b 	c #91B6FF",
"c 	c #95B9FF",
"d 	c #9ABDFF",
"e 	c #9FC0FF",
"f 	c #A4C3FF",
"g 	c #A9C6FF",
"h 	c #97B0DE",
"i 	c #15181E",
"j 	c #070E1E",
"k 	c #3972E1",
"l 	c #4684FF",
"m 	c #4B87FF",
"n 	c #4F8AFF",
"o 	c #548EFF",
"p 	c #5991FF",
"q 	c #5E94FF",
"r 	c #6397FF",
"s 	c #689BFF",
"t 	c #6D9EFF",
"u 	c #72A1FF",
"v 	c #76A4FF",
"w 	c #7BA8FF",
"x 	c #80ABFF",
"y 	c #85AEFF",
"z 	c #8AB1FF",
"A 	c #8FB5FF",
"B 	c #94B8FF",
"C 	c #98BBFF",
"D 	c #9DBFFF",
"E 	c #A2C2FF",
"F 	c #91ACDE",
"G 	c #336DE1",
"H 	c #3F7FFF",
"I 	c #4483FF",
"J 	c #4986FF",
"K 	c #4E89FF",
"L 	c #528CFF",
"M 	c #5790FF",
"N 	c #5C93FF",
"O 	c #6196FF",
"P 	c #6699FF",
"Q 	c #6B9DFF",
"R 	c #70A0FF",
"S 	c #75A3FF",
"T 	c #79A6FF",
"U 	c #7EAAFF",
"V 	c #83ADFF",
"W 	c #88B0FF",
"X 	c #8DB3FF",
"Y 	c #92B7FF",
"Z 	c #97BAFF",
"` 	c #9BBDFF",
" .	c #8BA8DE",
"..	c #14181E",
"+.	c #050E1E",
"@.	c #2D6AE1",
"#.	c #387BFF",
"$.	c #3D7EFF",
"%.	c #4281FF",
"&.	c #4785FF",
"*.	c #518BFF",
"=.	c #558EFF",
"-.	c #5A92FF",
";.	c #5F95FF",
">.	c #6498FF",
",.	c #699BFF",
"'.	c #6E9FFF",
").	c #78A5FF",
"!.	c #7CA8FF",
"~.	c #81ACFF",
"{.	c #86AFFF",
"].	c #8BB2FF",
"^.	c #90B5FF",
"/.	c #86A4DE",
"(.	c #12161E",
"_.	c #050D1E",
":.	c #2865E1",
"<.	c #3276FF",
"[.	c #367AFF",
"}.	c #3B7DFF",
"|.	c #4080FF",
"1.	c #4583FF",
"2.	c #4A87FF",
"3.	c #548DFF",
"4.	c #5890FF",
"5.	c #5D94FF",
"6.	c #6297FF",
"7.	c #679AFF",
"8.	c #6C9DFF",
"9.	c #71A1FF",
"0.	c #7BA7FF",
"a.	c #7FAAFF",
"b.	c #84AEFF",
"c.	c #89B1FF",
"d.	c #8EB4FF",
"e.	c #80A0DE",
"f.	c #030A19",
"g.	c #030B1A",
"h.	c #040C1B",
"i.	c #060C1B",
"j.	c #060D1B",
"k.	c #070D1B",
"l.	c #050A13",
"m.	c #355FB1",
"n.	c #578FFF",
"o.	c #6096FF",
"p.	c #4568AE",
"q.	c #080C13",
"r.	c #0C111B",
"s.	c #0C121B",
"t.	c #0D121B",
"u.	c #0F131B",
"v.	c #0E121A",
"w.	c #0D1219",
"x.	c #2C53A0",
"y.	c #508BFF",
"z.	c #5A91FF",
"A.	c #3A5B9D",
"B.	c #2850A0",
"C.	c #538DFF",
"D.	c #36599D",
"E.	c #244DA0",
"F.	c #4282FF",
"G.	c #32569D",
"H.	c #1F4BA0",
"I.	c #377AFF",
"J.	c #3C7DFF",
"K.	c #4584FF",
"L.	c #2E539D",
"M.	c #1B48A0",
"N.	c #3075FF",
"O.	c #3579FF",
"P.	c #3A7CFF",
"Q.	c #29509D",
"R.	c #1745A0",
"S.	c #2971FF",
"T.	c #2E74FF",
"U.	c #3377FF",
"V.	c #264E9D",
"W.	c #1342A0",
"X.	c #236CFF",
"Y.	c #2770FF",
"Z.	c #2C73FF",
"`.	c #3176FF",
" +	c #214A9D",
".+	c #1040A0",
"++	c #1C68FF",
"@+	c #216BFF",
"#+	c #266EFF",
"$+	c #2A72FF",
"%+	c #1D489D",
"&+	c #1966FF",
"*+	c #1A67FF",
"=+	c #1F6AFF",
"-+	c #246DFF",
";+	c #19459D",
">+	c #1D69FF",
",+	c #15429D",
"'+	c #113F9D",
")+	c #0F3F9D",
"!+	c #020A19",
"~+	c #020A1A",
"{+	c #020B1B",
"]+	c #020813",
"^+	c #1147B1",
"/+	c #1146AE",
"(+	c #030C1E",
"_+	c #165AE1",
":+	c #1659DE",
"<+	c #010915",
"[+	c #030C1D",
"}+	c #030D22",
"|+	c #010916",
"        . + @ # $ % & * = - ; > , ' ) ! ~ { { ] ^ / ( _         ",
"        : < [ } | 1 2 3 4 5 6 7 8 9 0 a b c d e f g h i         ",
"        j k l m n o p q r s t u v w x y z A B C D E F i         ",
"        j G H I J K L M N O P Q R S T U V W X Y Z `  ...        ",
"        +.@.#.$.%.&.[ *.=.-.;.>.,.'.6 ).!.~.{.].^.c /.(.        ",
"        _.:.<.[.}.|.1.2.n 3.4.5.6.7.8.9.v 0.a.b.c.d.e.(.        ",
"        f.g.h.i.i.j.k.k.l.m.L n.1 o.p.q.r.r.s.t.t.u.v.w.        ",
"                          x.m y.=.z.A.                          ",
"                          B.I J K C.D.                          ",
"                          E.$.F.&.[ G.                          ",
"                          H.I.J.|.K.L.                          ",
"                          M.N.O.P.H Q.                          ",
"                          R.S.T.U.#.V.                          ",
"                          W.X.Y.Z.`. +                          ",
"                          .+++@+#+$+%+                          ",
"                          .+&+*+=+-+;+                          ",
"                          .+&+&+&+>+,+                          ",
"                          .+&+&+&+&+'+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"                          .+&+&+&+&+)+                          ",
"        !+~+{+{+{+{+{+{+]+^+&+&+&+&+/+]+{+{+{+{+{+{+~+!+        ",
"        (+_+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+:+(+        ",
"        (+_+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+:+(+        ",
"        (+_+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+:+(+        ",
"        (+_+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+:+(+        ",
"        (+_+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+&+:+(+        ",
"        <+[+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+}+[+|+        "};
        """


# class EditSectionGui():
#     def __init__(self, obj):
#         self.obj = obj
#         self.form = FreeCADGui.PySideUic.loadUi(path_ui)

#         #Define a função do botão ok        
#         self.form.btn_ok.clicked.connect(self.accept)

#         self.form.comboBox.textActivated.connect(self.changeImage)

#         # self.form.image.pixmap = str(os.path.dirname(__file__))+'/resources/ui/img/sectionRetangle.svg'
#         pixmap = QPixmap(str(os.path.dirname(__file__))+'/resources/ui/img/sectionI.svg')
#         self.form.image.setPixmap(pixmap)
    
#     def changeImage(self, selection):
#         match selection:
#             case 'Rectangle Section':
#                 pixmap = QPixmap(str(os.path.dirname(__file__))+'/resources/ui/img/sectionRetangle.svg')

#             case 'Circular Section':
#                 pixmap = QPixmap(str(os.path.dirname(__file__))+'/resources/ui/img/sectionI.svg')
            
#             case 'W Section':
#                 pixmap = QPixmap(str(os.path.dirname(__file__))+'/resources/ui/img/sectionI.svg')

#         self.form.image.setPixmap(pixmap)
    
#     def accept(self):
#         print('botao ok clicado')



class CommandProfile():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/section.svg"), # the name of a svg file available in the resources
                "Accel"   : "S+C", # a default shortcut (optional)
                "MenuText": "Section",
                "ToolTip" : "Adds section to structure member"}

    def Activated(self):
        selections = list(FreeCADGui.Selection.getSelectionEx())
        
        doc = FreeCAD.ActiveDocument
        obj = doc.addObject("Part::FeaturePython", "Section")

        Section(obj, selections)
        ViewProviderSection(obj.ViewObject)
        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("section", CommandProfile())
