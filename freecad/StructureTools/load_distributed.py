import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets
from .load_base_class import LoadBaseClass
from .utils_func import rotate_to_direction, make_arrow, set_obj_appear, BASE_ARROWS_DIM

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()


class LoadDistributed(LoadBaseClass):
    def __init__(self, obj, selection):
        super().__init__(obj, selection)

        obj.addProperty("App::PropertyForce", "InitialLoading", "Distributed", "Initial loading (load per unit length)").InitialLoading = 10000000
        obj.addProperty("App::PropertyLength","InitialLoadAt","Distributed","Initial Load At(distance from start)").InitialLoadAt= 0
        obj.addProperty("App::PropertyForce", "FinalLoading", "Distributed", "Final loading (load per unit length)").FinalLoading = 10000000
        obj.addProperty("App::PropertyLength","FinalLoadAt","Distributed","Initial Load At(distance from start)")
    
    
    
    def execute(self, obj):        
        subelement = self.getSubelement(obj, obj.ObjectBase[0][1][0])
        if 'Edge' not in obj.ObjectBase[0][1][0]:
            return
        
        if obj.FinalLoadAt <= obj.InitialLoadAt or obj.InitialLoadAt > subelement.Length:
            obj.FinalLoadAt = subelement.Length
            obj.InitialLoadAt = 0
        
        if not (obj.FinalLoading != 0 or obj.InitialLoading != 0):
            obj.FinalLoading = self.base_value
            
        
        #calcula o numero de setas com base no tamanho padrao da seta
        n_arrow = int( (obj.FinalLoadAt-obj.InitialLoadAt) / (obj.ScaleDraw * self.dist_bet_arrows) )
        dist_bet_arrows = (obj.FinalLoadAt-obj.InitialLoadAt)/n_arrow #recalcula distancias
        if n_arrow < 3:
            n_arrow = 3
        
        # gera a lista de setas já em suas devidas escalas e nas devidas distancia posicionadas sobre o eixo X
        list_of_arrows = []            
        escala = (obj.FinalLoading- obj.InitialLoading)/n_arrow
        load = obj.InitialLoading

        for coordinades in self.get_arrow_coordinades(n_arrow,subelement, obj.InitialLoadAt, dist_bet_arrows):
            
            if load.Value == 0:
                load = load + escala
                continue
            arrow = make_arrow(load.Value,**BASE_ARROWS_DIM, scale=obj.ScaleDraw)
            load = load + escala
            
            rotate_to_direction(obj.GlobalDirection, arrow)
                            
            arrow.translate(coordinades)
            list_of_arrows.append(arrow)

        shape = Part.makeCompound(list_of_arrows)
        shape.translate(subelement.Vertexes[0].Point)
        set_obj_appear(obj)
        obj.Label = 'Distributed load'

        obj.Placement = shape.Placement
        obj.Shape = shape
        obj.ViewObject.DisplayMode = 'Shaded'



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
