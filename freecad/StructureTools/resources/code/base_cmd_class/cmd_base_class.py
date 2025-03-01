import FreeCADGui as Gui
import FreeCAD as App
from pathlib import Path
import os
import PySide #type: ignore
from PySide import QtCore, QtGui#type: ignore

#doc: https://wiki.freecad.org/Command#

class _Command_Class_Model():
    """Classe Base para os Comandos da Workbench"""
    
    _cmd_name = 'Nome Comando'
    _cmd_tip = 'Descriçao/Dicas'
    _icon_name = "icone.svg"
    _accel = "Shift+S"
    # _dir = Path.cwd() / 'resources' 
    print(Path(__file__).parent.parent.parent)
    _dir =  Path(__file__).parent.parent.parent


    def get_doc_name(self) -> str:
        """Pegar Nome do Documento"""
        self.doc_name = App.ActiveDocument.Name # type: ignore
        return self.doc_name
        
    # def get_selection(self):
    #     """Pegar Objeto Selecionado"""
    #     self.get_doc_name()
    #     obj_selection = Gui.Selection.getSelection()
    #     #TODO PENDENTE
    #     print(self.doc_name, obj_selection)

    # #TODO PENDENTE
    # def get_select_all(self):
    #     """Selecionar Todos os Objetos do Documento Ativo"""
    #     #busca objetos por determinado filtro
    #     # objs = App.ActiveDocument.findObjects("Part::Feature") # type: ignore
    #     objs = App.ActiveDocument.findObjects() # type: ignore
    #     for obj in objs:
    #         Gui.Selection.addSelection(self.get_doc_name(), obj.Name)
             
    def GetResources(self):
        """Ícone e Informações do Comando"""

        MenuText = QtCore.QT_TRANSLATE_NOOP(
            self.__class__.__name__,
            self._cmd_name)
        
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            self.__class__.__name__,
            self._cmd_tip)
        
        pixmap = self._dir / 'icons' /  self._icon_name
        return {
            'Pixmap': pixmap.as_posix(),
            'MenuText': MenuText,
            'ToolTip': ToolTip,
            "Accel"   : self._accel # a default shortcut (optional)
            }

    def Activated(self):
        """Do something here"""
        return

    def IsActive(self):
        """Here you can define if the command must be active or not (greyed) if certain conditions
        are met or not. This function is optional."""

        # The command will be active if there is an active document
        return not App.ActiveDocument is None
    
    @classmethod
    def add_cmd(cls):
        """Adicionar Comando ao Gui"""
        Gui.addCommand(cls.__name__, cls())

    def show_error_message(self,msg):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setIcon(QtWidgets.QMessageBox.Critical)  # Ícone de erro
        msg_box.setWindowTitle("Erro")
        msg_box.setText(msg)
        msg_box.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msg_box.exec_()
