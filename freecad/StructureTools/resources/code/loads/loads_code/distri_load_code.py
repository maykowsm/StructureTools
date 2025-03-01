import Part
from freecad.StructureTools.resources.code.utils.rotate import rotate_to_direction
from freecad.StructureTools.resources.code.utils.make_arrow import make_arrow
from freecad.StructureTools.resources.code.utils.shape_appearance import set_obj_appear
from freecad.StructureTools.resources.code.utils.constants import BASE_ARROWS_DIM
from .load_base_class import LoadBaseClass


class DistLoad(LoadBaseClass):
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
        