from PyQt5 import QtWidgets


def resize_window_to_columns(main_widget, table_view, fudgeFactor):
    frameWidth = table_view.frameWidth() * 2
    vertHeaderWidth = table_view.verticalHeader().width()
    horizHeaderWidth = table_view.horizontalHeader().length()
    vertScrollWidth = table_view.style().pixelMetric(QtWidgets.QStyle.PM_ScrollBarExtent)
    fudgeFactor = fudgeFactor
    newWidth = frameWidth + vertHeaderWidth + horizHeaderWidth + vertScrollWidth + fudgeFactor
    if newWidth <= 500:
        main_widget.resize(newWidth, main_widget.height())
    else:
        main_widget.resize(500, main_widget.height())
