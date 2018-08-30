from PyQt5.QtWidgets import QDialog, QTableView, QVBoxLayout, \
     QPushButton, QHBoxLayout, QComboBox, QLabel, QApplication, QStyle, QFontDialog
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QSize
from PyQt5.QtGui import QPixmap

from utils import resize_window_to_columns

_PLANT_IMAGE_SCALE_FACTORS = ['1', '2', '3', '4', '5', '6', '7']
_VIEW_MINIMUM_HEIGHT = 500


class PhotoViewe(QDialog):
    def __init__(self, model, parent=None):
        QDialog.__init__(self, parent=parent)

        self.setMinimumHeight(_VIEW_MINIMUM_HEIGHT)

        self.model = model
        self.font = None

        layout = QVBoxLayout(self)

        close_button = QPushButton('Go back to table view')
        scale_label = QLabel('Scale the image')
        photo_scale_button = QComboBox(self)
        photo_scale_button.insertItems(0, _PLANT_IMAGE_SCALE_FACTORS)
        font_size_button = QPushButton('Font')
        font_size_button.clicked.connect(self.font_dialog)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(close_button)

        buttons_layout.addStretch()

        buttons_layout.addWidget(scale_label)
        buttons_layout.addWidget(photo_scale_button)

        buttons_layout.addStretch()

        buttons_layout.addWidget(font_size_button)

        layout.addLayout(buttons_layout)

        close_button.clicked.connect(self._close)
        photo_scale_button.currentIndexChanged[str].connect(self._change_pixmap_factor)

        scale_factor = int(photo_scale_button.currentText())
        self.model.scale = scale_factor

        self.view = QTableView()
        self.view.setModel(self.model)
        self.font = self.view.property('font')

        self._hide_info_columns(self.model.image_column)

        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()

        #resize_window_to_columns(self, self.view, fudgeFactor=0)

        #self.view.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.view)

    def _close(self):
        self.close()

    def _change_pixmap_factor(self, scale_factor):
        self.model._set_scale_pixmap_factor(float(scale_factor))
        self.model.dataChanged.emit(QModelIndex(), QModelIndex())
        self.view.resizeRowsToContents()
        self.view.resizeColumnsToContents()

    def _hide_info_columns(self, image_column_index):
        for index in range(image_column_index):
            self.view.setColumnHidden(index, True)

    def font_dialog(self):

        self.font, valid = QFontDialog.getFont(self.font)
        if valid:
            self.view.setFont(self.font)
            self.view.resizeRowsToContents()




#class PhotoVieweModel(QAbstractTableModel):
    #def __init__(self, data, parent=None):
        #QAbstractTableModel.__init__(self, parent)

        #self.images_records = data
        #self.scale = 1

    #def rowCount(self, parent=QModelIndex()):
        #return len(self.images_records)

    #def columnCount(self, parent=QModelIndex()):
        #return 1

    #def data(self, index, role=Qt.DisplayRole):
        #if not index.isValid():
            #return None

        #record = self.images_records[index.row()]

        #if role == Qt.DisplayRole:
            #return 'plant name: {}'.format(record.name)

        #if role == Qt.DecorationRole:
            #path = record.path
            #pixmap = QPixmap(path)
            #return _scaled_pixmap(pixmap, self.scale)

        #if role == Qt.TextAlignmentRole:
            #return Qt.AlignTop

        #return None

    #def _set_scale_pixmap_factor(self, scale_factor):
        #self.scale = scale_factor


#def _scaled_pixmap(pixmap, scale):
    #width = pixmap.width()
    #height = pixmap.height()
    #scaled_pixmap = pixmap.scaled(width * scale, height * scale,
                            #Qt.KeepAspectRatio, Qt.SmoothTransformation)

    #return scaled_pixmap


if __name__ == '__main__':
    from sys import argv, exit
    from table import TableModel, _get_image_paths_names

    app = QApplication(argv)
    model = TableModel()
    image_data = _get_image_paths_names(model)
    view = PhotoViewe(image_data)
    view.show()
    exit(app.exec_())
