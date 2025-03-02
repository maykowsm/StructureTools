import FreeCAD, App, FreeCADGui, Part, os
from PySide2 import QtWidgets

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")

def show_error_message(msg):
    msg_box = QtWidgets.QMessageBox()
    msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
    msg_box.setWindowTitle("Erro")
    msg_box.setText(msg)
    msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg_box.exec_()




class CommandMember():
    """My new command"""

    def GetResources(self):
        return {"Pixmap"  : os.path.join(ICONPATH, "icons/member.svg"), # the name of a svg file available in the resources
                "Accel"   : "Shift+D", # a default shortcut (optional)
                "MenuText": "Define Member",
                "ToolTip" : "Defines the members of the structure"}

    def Activated(self):
        selections = FreeCADGui.Selection.getSelection()
        selection = list(filter(lambda element: 'Wire' in element.Name or 'Line' in element.Name, selections ))
             
        for selection in selections:
            selection.addProperty('App::PropertyLink', 'MaterialMember', 'Structure','Member material')
            selection.addProperty('App::PropertyLink', 'ProfileMember', 'Structure','Member profile')

        FreeCAD.ActiveDocument.recompute()        
        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("member", CommandMember())
