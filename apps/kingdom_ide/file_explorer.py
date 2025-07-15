from PySide6.QtWidgets import (
    QTreeView, QFileSystemModel, QDockWidget, 
    QWidget, QVBoxLayout, QMenu, QHeaderView,
    QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDir, Signal, QSettings, QModelIndex
from PySide6.QtGui import QAction
import os
import shutil

class FileExplorer(QDockWidget):
    file_opened = Signal(str)
    file_created = Signal(str)

    def __init__(self, parent=None, root_path=None):
        super().__init__("Explorador de Arquivos", parent)
        
        self._root_path = root_path if root_path else QDir.currentPath()
        print(QDir.currentPath())
        
        self.settings = QSettings("KingdomIDE", "FileExplorer")
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setNameFilters(["*.py", "*.txt", "*.md", "*.json", "*.bat", "*.vbs", "*.gitignore"])
        self.model.setNameFilterDisables(False)
        
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self._root_path))
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        self.tree.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QTreeView.DragDropMode.InternalMove)
        
        self.tree.setHeaderHidden(False)
        self.tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tree.setColumnWidth(0, 300)
        
        layout.addWidget(self.tree)
        self.setWidget(container)
        
        header_state = self.settings.value("header_state")
        if header_state:
            self.tree.header().restoreState(header_state)
        
        self.setup_style()
    
    @property
    def root_path(self):
        return self._root_path
    
    @root_path.setter
    def root_path(self, path):
        if os.path.exists(path):
            self._root_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.refresh_tree()
            
    def setup_connections(self):
        self.tree.doubleClicked.connect(self.on_file_double_clicked)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
    
    def closeEvent(self, event):
        self.settings.setValue("header_state", self.tree.header().saveState())
        super().closeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.tree.indexAt(event.pos())
            if not index.isValid():
                self.tree.clearSelection()
        super().mousePressEvent(event)
    
    def dropEvent(self, event):
        if event.source() == self.tree:
            drag_paths = []
            for index in self.tree.selectedIndexes():
                if index.column() == 0:
                    drag_paths.append(self.model.filePath(index))
            
            drop_index = self.tree.indexAt(event.pos())
            if drop_index.isValid():
                drop_path = self.model.filePath(drop_index)
                if os.path.isfile(drop_path):
                    drop_path = os.path.dirname(drop_path)
            else:
                drop_path = self.model.rootPath()
            
            errors = []
            for src_path in drag_paths:
                try:
                    dst_path = os.path.join(drop_path, os.path.basename(src_path))
                    
                    if os.path.exists(dst_path):
                        confirm = QMessageBox.question(
                            self,
                            "Sobrescrever?",
                            f"{os.path.basename(dst_path)} já existe. Sobrescrever?",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if confirm != QMessageBox.StandardButton.Yes:
                            continue
                    
                    shutil.move(src_path, dst_path)
                except Exception as e:
                    errors.append(f"{os.path.basename(src_path)}: {str(e)}")
            
            if errors:
                QMessageBox.critical(self, "Erro", "Não foi possível mover:\n" + "\n".join(errors))
            
            self.refresh_tree()
            event.acceptProposedAction()
        else:
            super().dropEvent(event)
       
    def setup_style(self):
        self.setStyleSheet("""
            QTreeView {
                background-color: #252526;
                color: #D4D4D4;
                border: 1px solid #1E1E1E;
                alternate-background-color: #2D2D30;
            }
            QTreeView::item:hover {
                background-color: #2A2D2E;
            }
            QTreeView::item:selected {
                background-color: #37373D;
                color: #FFFFFF;
            }
        """)
    
    def on_file_double_clicked(self, index):
        """Abre o arquivo quando double clicked"""
        path = self.model.filePath(index)
        if self.model.isDir(index):
            self.tree.setExpanded(index, not self.tree.isExpanded(index))
        else:
            self.file_opened.emit(path)
    
    def get_selected_path(self):
        indexes = self.tree.selectedIndexes()
        if indexes:
            return self.model.filePath(indexes[0])
        return None
    
    def get_selected_paths(self):
        paths = []
        for index in self.tree.selectedIndexes():
            if index.column() == 0:
                paths.append(self.model.filePath(index))
        return paths
    
    def get_parent_path(self):
        selected = self.get_selected_path()
        if selected:
            if os.path.isdir(selected):
                return selected
            return os.path.dirname(selected)
        return self.model.rootPath()
    
    def show_context_menu(self, position):
        menu = QMenu()
        
        open_action = QAction("Abrir", self)
        open_action.triggered.connect(self.open_selected)
        
        new_file_action = QAction("Novo Arquivo", self)
        new_file_action.triggered.connect(self.create_new_file)
        
        new_folder_action = QAction("Nova Pasta", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        
        rename_action = QAction("Renomear", self)
        rename_action.triggered.connect(self.rename_selected)
        
        delete_action = QAction("Excluir", self)
        delete_action.triggered.connect(self.delete_selected)
        
        menu.addAction(open_action)
        menu.addSeparator()
        menu.addAction(new_file_action)
        menu.addAction(new_folder_action)
        menu.addSeparator()
        menu.addAction(rename_action)
        menu.addAction(delete_action)
        
        menu.exec_(self.tree.viewport().mapToGlobal(position))
    
    def open_selected(self):
        index = self.tree.currentIndex()
        if index.isValid():
            self.on_file_double_clicked(index)
    
    def create_new_file(self):
        parent_dir = self.get_parent_path()
        if not parent_dir:
            return
            
        file_name, ok = QInputDialog.getText(
            self, 
            "Novo Arquivo", 
            "Nome do arquivo:",
            text="novo_arquivo.py"
        )
        
        if ok and file_name:
            if not '.' in file_name:
                file_name += ".py"
                
            full_path = os.path.join(parent_dir, file_name)
            
            if not os.path.exists(full_path):
                try:
                    with open(full_path, 'w') as f:
                        f.write("# Novo arquivo Python\n")
                    self.refresh_tree()
                    self.file_created.emit(full_path)
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível criar o arquivo: {str(e)}")
            else:
                QMessageBox.warning(self, "Aviso", "Um arquivo com esse nome já existe.")
    
    def create_new_folder(self):
        parent_dir = self.get_parent_path()
        if not parent_dir:
            return
            
        folder_name, ok = QInputDialog.getText(
            self, 
            "Nova Pasta", 
            "Nome da pasta:",
            text="nova_pasta"
        )
        
        if ok and folder_name:
            full_path = os.path.join(parent_dir, folder_name)
            
            if not os.path.exists(full_path):
                try:
                    os.makedirs(full_path)
                    self.refresh_tree()
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível criar a pasta: {str(e)}")
            else:
                QMessageBox.warning(self, "Aviso", "Uma pasta com esse nome já existe.")
    
    def rename_selected(self):
        """Renomeia os arquivos ou pastas selecionadas"""
        paths = self.get_selected_paths()
        if not paths:
            return
        
        if len(paths) == 1:
            old_path = paths[0]
            parent_dir = os.path.dirname(old_path)
            current_name = os.path.basename(old_path)
            
            new_name, ok = QInputDialog.getText(
                self, 
                "Renomear", 
                "Novo nome:",
                text=current_name
            )
            
            if ok and new_name and new_name != current_name:
                new_path = os.path.join(parent_dir, new_name)
                
                if not os.path.exists(new_path):
                    try:
                        os.rename(old_path, new_path)
                        self.refresh_tree()
                    except Exception as e:
                        QMessageBox.critical(self, "Erro", f"Não foi possível renomear: {str(e)}")
                else:
                    QMessageBox.warning(self, "Aviso", "Já existe um item com esse nome.")
        else:
            pattern, ok = QInputDialog.getText(
                self, 
                "Renomear Múltiplos", 
                "Padrão de renomeação (use * para manter o nome original):",
                text="*"
            )
            
            if ok and pattern:
                errors = []
                for i, old_path in enumerate(paths):
                    try:
                        parent_dir = os.path.dirname(old_path)
                        current_name = os.path.basename(old_path)
                        ext = os.path.splitext(current_name)[1] if os.path.isfile(old_path) else ""
                        
                        if '*' in pattern:
                            new_name = pattern.replace('*', current_name)
                        else:
                            new_name = f"{pattern}_{i+1}{ext}"
                        
                        new_path = os.path.join(parent_dir, new_name)
                        
                        counter = 1
                        while os.path.exists(new_path):
                            new_name = f"{pattern}_{i+1}_{counter}{ext}"
                            new_path = os.path.join(parent_dir, new_name)
                            counter += 1
                        
                        os.rename(old_path, new_path)
                    except Exception as e:
                        errors.append(f"{current_name}: {str(e)}")
                
                if errors:
                    QMessageBox.critical(self, "Erro", "Não foi possível renomear:\n" + "\n".join(errors))
                
                self.refresh_tree()
    
    def delete_selected(self):
        paths = self.get_selected_paths()
        if not paths:
            return
            
        item_names = ", ".join([os.path.basename(p) for p in paths])
        confirm = QMessageBox.question(
            self,
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir {item_names}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            errors = []
            for path in paths:
                try:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path) 
                except Exception as e:
                    errors.append(f"{os.path.basename(path)}: {str(e)}")
            
            if errors:
                QMessageBox.critical(self, "Erro", "Não foi possível excluir:\n" + "\n".join(errors))
            else:
                self.refresh_tree()
    
    def refresh_tree(self):
        current_index = self.tree.currentIndex()
        root_path = self.model.rootPath()
        
        self.model.setRootPath("")
        self.model.setRootPath(root_path)
        
        if current_index.isValid():
            self.tree.setCurrentIndex(current_index)