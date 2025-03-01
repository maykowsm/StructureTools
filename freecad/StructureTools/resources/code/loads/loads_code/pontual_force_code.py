import FreeCAD, Part
from concretoarmado.utils.rotate import rotate_to_direction
from concretoarmado.utils.make_arrow import make_arrow
from concretoarmado.utils.shape_appearance import set_obj_appear
from concretoarmado.utils.constants import BASE_ARROWS_DIM
from .load_base_class import LoadBaseClass


class PontualForceLoad(LoadBaseClass):
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
        