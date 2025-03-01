import FreeCAD

def set_obj_appear(obj, option=0):
    """
    obj - > shape freecad
    option - > int
    0 to blue
    1 to red
    """
    if option == 0:
        material = {
                    'DiffuseColor':(0.00,0.00,1.00),
                    'AmbientColor':(0.33,0.33,0.33),
                    'SpecularColor':(0.53,0.53,0.53),
                    'EmissiveColor':(0.00,0.00,0.00),
                    'Shininess':(0.90),
                    'Transparency':(0.00),
                    }
    if option == 1:
        material = {
                    'DiffuseColor':(1.00,0.00,0.00),
                    'AmbientColor':(0.33,0.33,0.33),
                    'SpecularColor':(0.53,0.53,0.53),
                    'EmissiveColor':(0.00,0.00,0.00),
                    'Shininess':(0.90),
                    'Transparency':(0.00),
                    }
    if option == 2:
        material = {
                    'DiffuseColor':(0.00,1.00,0.00),
                    'AmbientColor':(0.33,0.33,0.33),
                    'SpecularColor':(0.53,0.53,0.53),
                    'EmissiveColor':(0.00,0.00,0.00),
                    'Shininess':(0.90),
                    'Transparency':(0.00),
                    }
        
    obj.ViewObject.ShapeAppearance = (
                FreeCAD.Material(**material))
