# coding=ascii

try:
    from PySide2 import QtCore, QtWidgets
except:
    from PySide6 import QtCore, QtWidgets


class GroupWidget(QtWidgets.QWidget):

    kBaseHeaderColor = [253, 147, 0]

    def __init__(self, title, expanded: bool = True,
                 header_color: list = kBaseHeaderColor, parent=None):
        super().__init__(parent)

        self._layout = QtWidgets.QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._layout.setAlignment(QtCore.Qt.AlignTop)

        self._init_header(title)
        self._init_widget()

        self.set_header_color(header_color)
        self.set_expanded(expanded)
    
    def _init_header(self, title: str):

        self._header = QtWidgets.QFrame()
        self._header.setObjectName("HeaderWidget")
        self._header.setFixedHeight(20)
        self._layout.addWidget(self._header)

        self._header_layout = QtWidgets.QHBoxLayout(self._header)
        self._header_layout.setSpacing(2)
        self._header_layout.setContentsMargins(0, 0, 0, 0)
        self._header_layout.setAlignment(QtCore.Qt.AlignLeft)

        self._expand = QtWidgets.QToolButton()
        self._expand.setArrowType(QtCore.Qt.RightArrow)
        self._expand.setStyleSheet("QToolButton { border: none; }")
        self._expand.clicked.connect(self.__on_expand_clicked)
        self._header_layout.addWidget(self._expand)

        self._title = QtWidgets.QLabel(title)
        self._title.setObjectName("HeaderLabel")
        self._title.setStyleSheet("font: bold;")
        self._header_layout.addWidget(self._title)

        # self._header_layout.addStretch()
    
    def _init_widget(self):

        self._widget = QtWidgets.QWidget(self)
        self._widget.setObjectName("GroupWidget")
        self._layout.addWidget(self._widget)

        layout = QtWidgets.QVBoxLayout(self._widget)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignTop)

    def set_expanded(self, expanded):
        self._expand.setArrowType(QtCore.Qt.DownArrow if expanded else QtCore.Qt.RightArrow)
        self._widget.setVisible(expanded)
        self._widget.updateGeometry()

        layout = self._widget.layout()
        if layout:
            layout.update()
            layout.activate()
        
        self.updateGeometry()
        self._header_layout.update()
        self._header_layout.activate()

    def set_header_color(self, color: list = None):
        if color:
            self._header.setStyleSheet(
                """
                #HeaderWidget {{
                    padding-left: 4px;
                    border-radius: 3px;
                    background-color: rgb({0}, {1}, {2});
                }}
                """.format(*color)
            )
            self._title.setStyleSheet("#HeaderLabel { color: rgb(64, 64, 64); font: bold;}")
        else:
            self._header.setStyleSheet("")
            self._title.setStyleSheet("font: bold;")

    def __on_expand_clicked(self):
        self._expanded = self._expand.arrowType() == QtCore.Qt.RightArrow
        self.set_expanded(self._expanded)

    def add_widget(self, widget: QtWidgets.QWidget):
        self._widget.layout().addWidget(widget)
    
    def add_layout(self, layout: QtWidgets.QLayout):
        self._widget.layout().addLayout(layout)
  