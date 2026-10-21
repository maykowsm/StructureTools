import FreeCAD, App, FreeCADGui, Part, os
from PySide import QtWidgets

from .src.tools.msg_error import show_error_message

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")


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
            selection.addProperty('App::PropertyLink', 'SectionMember', 'Structure','Member section')
            selection.addProperty('App::PropertyAngle', 'RotationSection', 'Structure','Member section rotation')
            selection.addProperty('App::PropertyBool', 'TrussMember', 'Structure','Define como membro de treliça').TrussMember = False
        FreeCAD.ActiveDocument.recompute()        

        return

    def IsActive(self):
        
        return True

FreeCADGui.addCommand("member", CommandMember())
