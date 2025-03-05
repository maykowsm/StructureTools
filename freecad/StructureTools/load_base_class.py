import FreeCAD, Part
from .utils_func import rotate_to_direction, make_arrow, set_obj_appear, DIST_BET_ARROWS



class LoadBaseClass:
    def __init__(self, obj, selection):
        obj.Proxy = self
        obj.addProperty("App::PropertyLinkSubList", "ObjectBase", "Base", "Object base")
        obj.addProperty("App::PropertyFloat", "ScaleDraw", "Load", "Scale from drawing").ScaleDraw = 1
        obj.addProperty("App::PropertyEnumeration", "GlobalDirection","Load","Global direction load")

        obj.ObjectBase = (selection[0], selection[1])
        obj.GlobalDirection = ['+X','-X', '+Y','-Y', '+Z','-Z']
        obj.GlobalDirection = '-Z'

        self.dist_bet_arrows = DIST_BET_ARROWS
        self.base_value = 10000000

    # Retorna o subelemento asociado
    def getSubelement(self, obj, nameSubElement):
        if 'Edge' in  nameSubElement:
            index = int(nameSubElement.split('Edge')[1]) - 1
            return obj.ObjectBase[0][0].Shape.Edges[index]
        else:
            index = int(nameSubElement.split('Vertex')[1]) - 1
            return obj.ObjectBase[0][0].Shape.Vertexes[index]

        
    def get_arrow_coordinades(self,n_arrow,subelement, start_at=0,dist_bet_arrows=0):
        """Retorna com as coodenadas das setas distribuidas ao longo de um elemento de acordo com o elemento e o numero de setas
        n_arrow -> numero de setas
        subelement -> subelemento
        """
        vertex = subelement.Vertexes
        start_vet = FreeCAD.Vector(vertex[0].Point.x,vertex[0].Point.y,vertex[0].Point.z)
        final_vet = FreeCAD.Vector(vertex[1].Point.x,vertex[1].Point.y,vertex[1].Point.z)
        uni_vet = (final_vet-start_vet)/subelement.Length
        for i in range(n_arrow + 1):
            yield uni_vet * start_at + i * uni_vet * dist_bet_arrows
            
    
    def execute(self, obj):        
        pass
        
        
    def onChanged(self,obj,Parameter):
        if Parameter == 'edgeLength':
            self.execute(obj)
    