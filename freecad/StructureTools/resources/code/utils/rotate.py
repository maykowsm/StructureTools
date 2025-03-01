import FreeCAD

def str_dir_to_vet(direction:str):
        y_vet = FreeCAD.Vector(0,1,0)
        x_vet = FreeCAD.Vector(1,0,0)
        z_vet = FreeCAD.Vector(0,0,1)
        vet_map = {
            '+X':x_vet,
            '-X':-x_vet,
            '+Y':y_vet,
            '-Y':-y_vet,
            '+Z':z_vet,
            '-Z':z_vet,
            }
        return vet_map.get(direction)

def rotate_to_direction(direction:str, obj):
    """
    Rotaciona um objeto fornecido na direção desejada.
    Direções Suportadas:
    '+X','-X','+Y','-Y','+Z','-Z'
    """
    null_vet = FreeCAD.Vector(0,0,0)
    y_vet = str_dir_to_vet('+Y')
    x_vet = str_dir_to_vet('+X')
    rotate_map = {
        '+X':(null_vet,y_vet, -90),
        '-X':(null_vet,y_vet, 90),
        '+Y':(null_vet,x_vet, 90),
        '-Y':(null_vet,x_vet, -90),
        '+Z':(null_vet,x_vet, 180),
        '-Z':(null_vet,x_vet, 0),
        }
    if direction not in rotate_map.keys():
        print("Invalid Direction!")
        return
    obj.rotate(*rotate_map.get(direction))

