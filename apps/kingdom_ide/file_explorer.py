from PySide6.QtWidgets import (
    QTreeView, QFileSystemModel, QDockWidget, 
    QWidget, QVBoxLayout, QMenu, QHeaderView,
    QInputDialog, QMessageBox
)
from PySide6.QtCore import Qt, QDir, Signal, QSettings, QModelIndex, QSortFilterProxyModel
from PySide6.QtGui import QAction
import os
import shutil

class FileSystemFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hidden_folders = ["__pycache__", ".git", ".idea", "venv", "env", "node_modules"]
    
    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        name = self.sourceModel().fileName(index)
        
        if self.sourceModel().isDir(index) and name in self.hidden_folders:
            return False
            
        return True
    
    def lessThan(self, left, right):
        left_is_dir = self.sourceModel().isDir(left)
        right_is_dir = self.sourceModel().isDir(right)
        
        if left_is_dir and not right_is_dir:
            return True
        if not left_is_dir and right_is_dir:
            return False
            
        return left.data().lower() < right.data().lower()

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
    
    def add_hidden_folder(self, folder_name):
        if folder_name not in self.proxy_model.hidden_folders:
            self.proxy_model.hidden_folders.append(folder_name)
            self.proxy_model.invalidateFilter()

    def remove_hidden_folder(self, folder_name):
        if folder_name in self.proxy_model.hidden_folders:
            self.proxy_model.hidden_folders.remove(folder_name)
            self.proxy_model.invalidateFilter()
        
    def setup_ui(self):
        container = QWidget()
        layout = QVBoxLayout()
        container.setLayout(layout)
        
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.model.setNameFilters(["*.py", "*.txt", "*.md", "*.json", "*.bat", "*.vbs", "*.gitignore"])
        self.model.setNameFilterDisables(False)
        
        self.proxy_model = FileSystemFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        
        self.tree = QTreeView()
        self.tree.setModel(self.proxy_model)
        self.tree.setRootIndex(self.proxy_model.mapFromSource(self.model.index(self._root_path)))
        self.tree.setAnimated(True)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
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
    
    def on_file_double_clicked(self, index):
        if not index.isValid():
            return
            
        source_index = self.proxy_model.mapToSource(index)
        path = self.model.filePath(source_index)
        
        if self.model.isDir(source_index):
            self.tree.setExpanded(index, not self.tree.isExpanded(index))
        else:
            self.file_opened.emit(path)
            
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
    
    def get_selected_path(self):
        indexes = self.tree.selectedIndexes()
        if indexes:
            source_index = self.proxy_model.mapToSource(indexes[0])
            return self.model.filePath(source_index)
        return None

    def refresh_tree(self):
        current_path = self.get_selected_path()
        root_path = self.model.rootPath()
        
        self.model.setRootPath("")
        self.model.setRootPath(root_path)
        
        if current_path:
            source_index = self.model.index(current_path)
            proxy_index = self.proxy_model.mapFromSource(source_index)
            self.tree.setCurrentIndex(proxy_index)
    
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
        index = self.tree.indexAt(position)
        
        if index.isValid():
            source_index = self.proxy_model.mapToSource(index)
            path = self.model.filePath(source_index)
            
            if self.model.isDir(source_index):
                folder_name = os.path.basename(path)
                
                if folder_name in self.proxy_model.hidden_folders:
                    show_action = QAction(f"Mostrar '{folder_name}'", self)
                    show_action.triggered.connect(lambda: self.remove_hidden_folder(folder_name))
                    menu.addAction(show_action)
                else:
                    hide_action = QAction(f"Ocultar '{folder_name}'", self)
                    hide_action.triggered.connect(lambda: self.add_hidden_folder(folder_name))
                    menu.addAction(hide_action)
                
                menu.addSeparator()
        
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
        try:
            indexes = self.tree.selectedIndexes()
            if not indexes:
                return
                
            source_index = self.proxy_model.mapToSource(indexes[0])
            old_path = self.model.filePath(source_index)
            
            if not os.path.exists(old_path):
                QMessageBox.warning(self, "Aviso", "O item selecionado não existe mais.")
                self.refresh_tree()
                return

            current_name = os.path.basename(old_path)
            new_name, ok = QInputDialog.getText(
                self, "Renomear", "Novo nome:", text=current_name
            )
            
            if ok and new_name and new_name != current_name:
                new_path = os.path.join(os.path.dirname(old_path), new_name)
                
                if os.path.exists(new_path):
                    QMessageBox.warning(self, "Aviso", "Já existe um item com esse nome.")
                    return
                    
                self.proxy_model.setDynamicSortFilter(False)
                
                try:
                    os.rename(old_path, new_path)
                    self.model.setRootPath(self.model.rootPath())
                except Exception as e:
                    QMessageBox.critical(self, "Erro", f"Não foi possível renomear: {str(e)}")
                finally:
                    self.proxy_model.setDynamicSortFilter(True)
                    self.refresh_tree()
                    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")

    def delete_selected(self):
        try:
            indexes = self.tree.selectedIndexes()
            if not indexes:
                return
                
            paths = []
            for index in indexes:
                if index.column() == 0:
                    source_index = self.proxy_model.mapToSource(index)
                    path = self.model.filePath(source_index)
                    if os.path.exists(path):
                        paths.append(path)
            
            if not paths:
                return
                
            confirm = QMessageBox.question(
                self, "Confirmar Exclusão", 
                f"Tem certeza que deseja excluir {len(paths)} itens?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.proxy_model.setDynamicSortFilter(False)
                
                errors = []
                for path in paths:
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path)
                        else:
                            os.remove(path)
                    except Exception as e:
                        errors.append(f"{os.path.basename(path)}: {str(e)}")
                
                self.model.setRootPath(self.model.rootPath())
                
                if errors:
                    QMessageBox.critical(self, "Erro", "Não foi possível excluir:\n" + "\n".join(errors))
                
                self.proxy_model.setDynamicSortFilter(True)
                self.refresh_tree()
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro inesperado: {str(e)}")
    
    def refresh_tree(self):
        try:
            expanded_paths = []
            root = self.model.rootPath()
            
            def collect_expanded(index):
                if self.tree.isExpanded(index):
                    source_index = self.proxy_model.mapToSource(index)
                    path = self.model.filePath(source_index)
                    expanded_paths.append(path)

                    for i in range(self.proxy_model.rowCount(index)):
                        child_index = self.proxy_model.index(i, 0, index)
                        collect_expanded(child_index)
            
            root_index = self.proxy_model.mapFromSource(self.model.index(root))
            if root_index.isValid():
                collect_expanded(root_index)
            
            current_index = self.tree.currentIndex()
            current_path = None
            if current_index.isValid():
                source_index = self.proxy_model.mapToSource(current_index)
                current_path = self.model.filePath(source_index)
            
            self.model.setRootPath("")
            self.model.setRootPath(root)
            
            def restore_expansion(index):
                source_index = self.proxy_model.mapToSource(index)
                path = self.model.filePath(source_index)
                if path in expanded_paths:
                    self.tree.setExpanded(index, True)
                for i in range(self.proxy_model.rowCount(index)):
                    child_index = self.proxy_model.index(i, 0, index)
                    restore_expansion(child_index)
            
            if root_index.isValid():
                restore_expansion(root_index)
            
            if current_path:
                source_index = self.model.index(current_path)
                if source_index.isValid():
                    proxy_index = self.proxy_model.mapFromSource(source_index)
                    self.tree.setCurrentIndex(proxy_index)
                    self.tree.scrollTo(proxy_index)
                    
        except Exception as e:
            print(f"Erro ao atualizar árvore: {str(e)}")