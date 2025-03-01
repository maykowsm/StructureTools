import os
import FreeCADGui as Gui
import FreeCAD as App

translate=App.Qt.translate
QT_TRANSLATE_NOOP=App.Qt.QT_TRANSLATE_NOOP

ICONPATH = os.path.join(os.path.dirname(__file__), "resources")
TRANSLATIONSPATH = os.path.join(os.path.dirname(__file__), "resources", "translations")

# Add translations path
Gui.addLanguagePath(TRANSLATIONSPATH)
Gui.updateLocale()

class StructureTools(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """
    MenuText = translate("Workbench", "StructureTools")
    ToolTip = translate("Workbench", "a simple StructureTools")
    Icon = os.path.join(ICONPATH, "icone.svg")
    toolbox = []

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        from freecad.StructureTools import suport
        from freecad.StructureTools import profile
        from freecad.StructureTools import material
        from freecad.StructureTools import member

        ###add load tools ###
        from freecad.StructureTools.resources.code import loads
        self.add_cmds_to_toolbar(loads)

        # NOTE: Context for this commands must be "Workbench"
        self.appendToolbar('StructureTools', ["member", "suport", "profile", "material"])
        # self.appendMenu('StructureTools',["load_distributed", "load_nodal","member" ,"suport", "profile", "material"])

        import DraftTools
        #add Draft Snap
        self.appendToolbar('Draft Snap', [
            'Draft_Snap_Lock','Draft_Snap_Endpoint',
            'Draft_Snap_Midpoint',
            'Draft_Snap_Center',
            'Draft_Snap_Angle',
            'Draft_Snap_Intersection',
            'Draft_Snap_Perpendicular',
            'Draft_Snap_Extension',
            'Draft_Snap_Parallel',
            'Draft_Snap_Special',
            'Draft_Snap_Near',
            'Draft_Snap_Ortho',
            'Draft_Snap_Grid',
            'Draft_Snap_WorkingPlane',
            'Draft_Snap_Dimensions',
            'Draft_ToggleGrid'])



    def Activated(self):
        '''
        code which should be computed when a user switch to this workbench
        '''

        App.Console.PrintMessage(translate(
            "Log",
            "Workbench StructureTools activated.") + "\n")

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        App.Console.PrintMessage(translate(
            "Log",
            "Workbench StructureTools de-activated.") + "\n")
        
    def add_cmds_to_toolbar(self, module_name):
        """Add commands from module to the toolbar"""
        for cmd in module_name.cmd_list:
            cmd.add_cmd()
            self.appendToolbar(module_name.group_name, [cmd.__name__])
            #o original:
            #     self.appendToolbar(
            #         str(QtCore.QT_TRANSLATE_NOOP(group_name, group_name)), [cmd.__name__])

    def add_cmds_to_menu(self, module_name):
        """Add commands from module to the Menu Bar"""
        for cmd in module_name.cmd_list:
            cmd.add_cmd()
            self.appendMenu(module_name.group_name, [cmd.__name__])
            #o original:
            #     self.appendMenu(
            #         str(QtCore.QT_TRANSLATE_NOOP(group_name, group_name)), [cmd.__name__])


Gui.addWorkbench(StructureTools())
