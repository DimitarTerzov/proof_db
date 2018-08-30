from collections import namedtuple

from PyQt5.QtWidgets import QApplication, QTableView, QWidget, QVBoxLayout, \
     QTextEdit, QLabel, QDialog, QMainWindow, QPushButton, QStyle, QGridLayout, \
     QLineEdit, QHeaderView, QAbstractScrollArea, QCheckBox, QHBoxLayout, QFontDialog
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt5.QtGui import QPixmap
from PyQt5 import QtSql

from database import get_db_data, update_db
from photo_view_dialog_3 import PhotoViewe
from utils import resize_window_to_columns


_PATH_TO_DB = 'C:/sqlite/usda.db'
_DB_TABLE = 'usda'
_PLANT_FOLDER = 'C:\sqlite\proof_db\plant_folder'
_PLANTS_MAPPING = {
    0: 'aloevera.jpg',
    1: 'artichoke.jpg',
    2: 'bamboo.jpg',
    3: 'bananatree.jpg',
    4: 'cactus.jpg',
    5: 'clover.jpg',
    6: 'coastlineplant.jpg',
    7: 'convolvulus.jpg',
    8: 'daisy.jpg',
    9: 'daylily.jpg'
}


class MySqlModel(QtSql.QSqlQueryModel):
    def __init__(self, headers, parent=None):
        QtSql.QSqlQueryModel.__init__(self, parent)

        self.scale = None
        self.headers = headers
        self.column_count = len(self.headers) + 2
        self.image_column = self.column_count - 2
        self.info_column = self.column_count - 1

    def columnCount(self, parent=QModelIndex()):
        return self.column_count

    def data(self, index, role=Qt.DisplayRole):

        column = index.column()
        if role == Qt.TextAlignmentRole and column != self.info_column:
            return Qt.AlignCenter

        if role == Qt.DecorationRole and column == self.image_column:
            model = index.model()

            # hardcoded image path just to show something
            plant = _PLANTS_MAPPING[index.row() % 10]
            pixmap_path = '{}/{}'.format(_PLANT_FOLDER, plant)
            pixmap = QPixmap(pixmap_path)
            return _scaled_pixmap(pixmap, self.scale)

        if role == Qt.DisplayRole and column == self.info_column:
            return self._info_data(index)

        return QtSql.QSqlQueryModel.data(self, index, role)

    def _set_scale_pixmap_factor(self, scale_factor):
        self.scale = scale_factor

    def _info_data(self, index):
        #model = index.model()
        info = ''
        for i in range(len(self.headers)):
            info += '{}: {}\n'.format(self.headers[i],
                                      self.index(index.row(), i).data())
        return info


def _scaled_pixmap(pixmap, scale):
    width = pixmap.width()
    height = pixmap.height()
    scaled_pixmap = pixmap.scaled(width * scale, height * scale,
                            Qt.KeepAspectRatio, Qt.SmoothTransformation)

    return scaled_pixmap


class Widget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.setGeometry(100, 150, 1200, 600)

        self.Columns = '*'
        self.font = None
        self.HeaderList = None
        self.left_padding = 0
        self.right_padding = 0
        self.search_field_spacing = 5

        self.createDB()
        self.getHeaders()

        layout = QVBoxLayout(self)

        buttons_layout = QHBoxLayout()
        show_plant_view = QPushButton('Plant photo with details')
        font_button = QPushButton('Font')
        buttons_layout.addWidget(show_plant_view)
        buttons_layout.addWidget(font_button)

        layout.addLayout(buttons_layout)

        show_plant_view.clicked.connect(self._show_photo_view)
        font_button.clicked.connect(self.font_dialog)

        self.model = MySqlModel(self.HeaderList)
        self.SearchQuery = "select {} from {}".format(self.Columns, _DB_TABLE)
        self.model.setQuery(self.SearchQuery, self.DB)

        self.view = QTableView(self)
        self.view.setMinimumHeight(325)
        self.font = self.view.property('font')
        self.view.setModel(self.model)

        self.view.setColumnHidden(self.model.image_column, True)
        self.view.setColumnHidden(self.model.info_column, True)

        horizontal_header = self.view.horizontalHeader()
        for i in range(len(horizontal_header)):
            horizontal_header.setSectionResizeMode(i, QHeaderView.Stretch)

        self.search_layout = QHBoxLayout()
        self.search_layout.insertSpacing(0, self.left_padding)
        self.SearchFieldsGrid = QGridLayout()
        self.makeSearchFieldsGrid()
        self.search_layout.addLayout(self.SearchFieldsGrid)
        self.search_layout.insertSpacing(-1, self.right_padding)
        layout.addLayout(self.search_layout)

        #self.view.horizontalHeader().setStretchLastSection(True)
        #self.view.resizeColumnsToContents()
        #self.view.horizontalHeader().ResizeMode(QHeaderView.Interactive)

        layout.addWidget(self.view)

        self.view.resizeRowsToContents()
        self.view_vertical_header = self.view.verticalHeader()
        self.view_vertical_header.geometriesChanged.connect(self._align_search_layout)

    def createDB(self):
        # binding to an existing database

        self.DB = QtSql.QSqlDatabase.addDatabase('QSQLITE')

        self.DB.setDatabaseName(_PATH_TO_DB)
        self.DB.open()

    def getHeaders(self):
        # getting a list of Headers
        self.query = QtSql.QSqlQuery(db = self.DB)
        self.query.exec_("PRAGMA table_info({})".format(_DB_TABLE))

        # filling the list of headings
        self.HeaderList = []
        while self.query.next():
            self.HeaderList.append(self.query.value(1))

        # create a query parameter dictionary
        self.paramsDict = {x: ['', '', ''] for x in self.HeaderList}
        self.paramsDict[''] = ["{} {} '%{}%'", '', '']

    def makeSearchFieldsGrid(self):
        self.SearchFieldsGrid.setSpacing(self.search_field_spacing)

        self.clearLayout(self.SearchFieldsGrid)

        self.cb = QCheckBox(self)
        self.cb.stateChanged.connect(self.changeQuery)
        self.SearchFieldsGrid.addWidget(self.cb, 1, 0)

        n = len(self.HeaderList)
        qwidth = [self.view.columnWidth(i) for i in range(n)]
        self.qles = [None for i in range(n)]

        for i in range(n):
            self.qles[i] = QLineEdit(self)
            self.qles[i].setObjectName(self.HeaderList[i])
            self.qles[i].textChanged[str].connect(self.setSearchQuery)
            label = QLabel(self.HeaderList[i])

            self.SearchFieldsGrid.addWidget(label, 0, i + 1, alignment=Qt.AlignCenter)
            self.SearchFieldsGrid.addWidget(self.qles[i], 1, i + 1)

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget() is not None:
                child.widget().deleteLater()
            elif child.layout() is not None:
                clearLayout(child.layout())

    # remembering the status of the switch after pressing and updating the table
    def changeQuery(self, state):

        self.state = state
        self.setSearchQuery('')

    def setSearchQuery(self, text):
        # switch handling
        try:
            if self.state == Qt.Checked:
                self.paramsDict[''] = ["{0} {1} '% {2}%' or {0} {1} '{2}%'", '', '']
            else:
                self.paramsDict[''] = ["{} {} '%{}%'", '', '']
        except:
            self.paramsDict[''] = ["{} {} '%{}%'", '', '']
        # processing of more and less characters
        if text != '':
            if text[0] == '<':
                matching = '<'
                queryString = "{} {} {}"
                text = text[1:]
            elif text[0] == '>':
                matching = '>'
                queryString = "{} {} {}"
                text = text[1:]
            else:
                queryString = self.paramsDict[''][0]
                matching = 'like'
        else:
            queryString, matching, text = self.paramsDict['']

        # filling in the query parameters dictionary
        self.paramsDict[self.sender().objectName()] = [queryString, matching, text]
        paramList = []
        # assembling query parameters into a list
        for name, value in self.paramsDict.items():
            if len(value) == 3:
                queryString, matching, text = value
                if queryString.find('%') != -1:
                    queryString = self.paramsDict[''][0]
                if text != '':
                    paramList.append(queryString.format(name, matching, text))

        # assembling query parameters into a string
        if len(paramList) == 0:
            params = ''
        elif len(paramList) == 1:
            params = 'where {}'.format(paramList[0])
        else:
            params = 'where {}'.format(" and ".join(paramList))
        # assembling the query and updating the table according to it

        self.Columns = '*' if self.Columns == '' else self.Columns
        self.searchQuery = "select {} from {} {}".format(self.Columns, _DB_TABLE, params)
        self.model.setQuery(self.searchQuery, self.DB)

        self.view.resizeRowsToContents()

        #header = self.view.horizontalHeader()
        #for i in range(len(header)):
            #header.setSectionResizeMode(i, QHeaderView.Stretch)

    def font_dialog(self):

        self.font, valid = QFontDialog.getFont(self.font)
        if valid:
            self.view.setFont(self.font)
            self.view.resizeRowsToContents()
            for i in self.qles:
                i.setFont(self.font)

    def _align_search_layout(self):
        vertical_header_width = self.view_vertical_header.width()
        checkbox_width = self.cb.width()
        self.left_padding = vertical_header_width - checkbox_width - self.search_field_spacing
        vertical_scrollbar_width = self.view.verticalScrollBar().width()
        self.right_padding = vertical_scrollbar_width

        left_spacer = self.search_layout.itemAt(0)
        left_spacer.changeSize(self.left_padding, 10)

        right_spacer = self.search_layout.itemAt(2)
        right_spacer.changeSize(self.right_padding, 10)

        self.search_layout.invalidate()

    def _show_photo_view(self):
        #image_data = _get_image_paths_names(self.model)
        viewer = PhotoViewe(self.model, self)
        viewer.show()


def _get_image_paths_names(model):

    Record = namedtuple('ImageData', ['path', 'name'])

    image_data = []
    for row in range(model.rowCount()):
        image_name = model.index(row, 2).data()
        image_directory = model.index(row, 1).data()
        path = '{}\\{}.jpg'.format(image_directory, image_name)

        record = Record(path, image_name)
        image_data.append(record)

    return image_data


if __name__=="__main__":
    from sys import argv, exit

    app = QApplication(argv)
    widget = Widget()
    widget.show()
    exit(app.exec_())
