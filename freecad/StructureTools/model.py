import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  #Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()



# Mapeia os nós da estrutura, (inverte o eixo y e z para adequação as coordenadas do sover)
def mapNodes(elements):
    # Varre todos os elementos de linha e adiciona seus vertices à tabela de nodes
    listNodes = []
    for element in elements:
        for edge in element.Shape.Edges:
            for vertex in edge.Vertexes:
                node = [vertex.Point.x, vertex.Point.z, vertex.Point.y]
                if not node in listNodes:
                    listNodes.append(node)

    return listNodes


# Mapeia os membros da estrutura 
def mapMembers(elements, listNodes):

    listMembers = []
    for element in elements:
        for edge in element.Shape.Edges:
            listIndexVertex = []
            for vertex in edge.Vertexes:
                node = [round(vertex.Point.x,2),round(vertex.Point.z,2), round(vertex.Point.y,2)]
                index = listNodes.index(node)
                listIndexVertex.append(index + 1)

            listMembers.append([listIndexVertex[0], listIndexVertex[1]])
            # sheetMembers.set('A'+str(int(line)), str(listIndexVertex[0]))
            # sheetMembers.set('B'+str(int(line)), str(listIndexVertex[1]))

class CommandModel():

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/member.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+B", # a default shortcut (optional)
                "MenuText": "Define Member",
                "ToolTip" : "Defines the members of the structure"}
    
    def Activated(self):
        selections = FreeCADGui.Selection.getSelection()    
        nodes = mapNodes(selections)
        members = mapMembers(selections)

        print(nodes)
        print(members)
           

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("model", CommandModel())
