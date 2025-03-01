import FreeCAD, Part
from concretoarmado.utils.rotate import rotate_to_direction
from functools import lru_cache

@lru_cache(maxsize=2)
def make_arrow_point(base_radius, height, scale = 1):
    """Cria um cone de acordo com as medidas enviadas.
    Possue um cache para as duas primeiras chamadas.
    base_radius - raio base em mm
    heights - height em mm
    scala -  fator de escala
    """
    return Part.makeCone(0 ,base_radius * scale , height * scale )

def make_arrow(height_arrow, radius_cylinder = 2, base_radius_cone=12, height_cone=30, scale=1):
    """Cria uma seta de acordo com as medidas enviadas.
    """
    height_cylinder = (height_arrow/1000000) * 30
    cone = make_arrow_point(base_radius_cone, height_cone, scale)
    cylinder = Part.makeCylinder(radius_cylinder * scale , abs(height_cylinder) * scale )        
    cylinder.translate(FreeCAD.Vector(0,0, height_cone * scale ))
    shape = Part.makeCompound([cone, cylinder])
    if height_arrow < 0:
        rotate_to_direction('+Z',shape)
    return shape

def make_momentum_arrow(height_arrow, radius_cylinder = 2, base_radius_cone=12, height_cone=30, scale=1):
    height_cylinder = (height_arrow/1000000) * 30
    cone = make_arrow_point(base_radius_cone, height_cone, scale)
    cone2 = cone.copy()
    cone2.translate(FreeCAD.Vector(0,0, height_cone * scale ))

    cylinder = Part.makeCylinder(radius_cylinder * scale , abs(height_cylinder) * scale )        
    cylinder.translate(FreeCAD.Vector(0,0, height_cone * 2 * scale ))
    shape = Part.makeCompound([cone,cone2, cylinder])
    if height_arrow < 0:
        rotate_to_direction('+Z',shape)
    return shape