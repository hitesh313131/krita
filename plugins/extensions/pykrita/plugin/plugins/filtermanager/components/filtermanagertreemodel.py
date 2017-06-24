from PyQt5.QtCore import QAbstractItemModel, QFile, QIODevice, QModelIndex, Qt
from PyQt5.QtWidgets import QApplication, QTreeView
from filtermanager.components import filtermanagertreeitem
from PyQt5.QtGui import QPixmap


class FilterManagerTreeModel(QAbstractItemModel):

    DATA_COLUMN = 3

    def __init__(self, uiFilterManager, parent=None):
        super(FilterManagerTreeModel, self).__init__(parent)

        self.rootItem = filtermanagertreeitem.FilterManagerTreeItem(("Name", "Type", "Thumbnail"))
        self.uiFilterManager = uiFilterManager
        self._loadTreeModel(self.rootItem)

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.rootItem

        #It's a FilterManagerTreeItem
        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
        return parentItem.childCount()

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()

        if role == Qt.UserRole + 1:
            return item.data(self.DATA_COLUMN)

        if role != Qt.DisplayRole and role != Qt.DecorationRole:
            return None

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def _loadTreeModel(self, parent):
        for document in self.uiFilterManager.documents:
            rootNode = document.rootNode()
            columnData = (document.fileName(),
                          "Document",
                          QPixmap.fromImage(document.thumbnail(30, 30)),
                          rootNode)
            item = filtermanagertreeitem.FilterManagerTreeItem(columnData, parent)
            parent.appendChild(item)

            childNodes = rootNode.childNodes()
            if len(childNodes):
                self._addSubNodes(childNodes[::-1], item)

    def _addSubNodes(self, nodes, parent):
        for node in nodes:
            nodeName = node.name()
            nodeType = node.type()
            columnData = ("Unnamed" if nodeName == '' else nodeName,
                          "Untyped" if nodeType == '' else nodeType,
                          QPixmap.fromImage(node.thumbnail(30, 30)),
                          node)
            item = filtermanagertreeitem.FilterManagerTreeItem(columnData, parent)
            parent.appendChild(item)

            childNodes = node.childNodes()
            if len(childNodes):
                self._addSubNodes(childNodes[::-1], item)