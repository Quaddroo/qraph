# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'qraph2.ui'
##
## Created by: Qt User Interface Compiler version 6.2.4
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
    QGridLayout, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpinBox, QStatusBar,
    QTextEdit, QToolButton, QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1101, 644)
        self.save = QAction(MainWindow)
        self.save.setObjectName(u"save")
        self.save_as = QAction(MainWindow)
        self.save_as.setObjectName(u"save_as")
        self.load = QAction(MainWindow)
        self.load.setObjectName(u"load")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout_3 = QGridLayout(self.centralwidget)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.label_2 = QLabel(self.centralwidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setMinimumSize(QSize(0, 25))
        self.label_2.setMaximumSize(QSize(16777215, 30))

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.channel_system = QToolButton(self.centralwidget)
        self.channel_system.setObjectName(u"channel_system")
        sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.channel_system.sizePolicy().hasHeightForWidth())
        self.channel_system.setSizePolicy(sizePolicy1)
        self.channel_system.setMinimumSize(QSize(30, 25))
        self.channel_system.setCheckable(True)

        self.gridLayout.addWidget(self.channel_system, 4, 2, 1, 1)

        self.trend_line = QToolButton(self.centralwidget)
        self.trend_line.setObjectName(u"trend_line")
        sizePolicy1.setHeightForWidth(self.trend_line.sizePolicy().hasHeightForWidth())
        self.trend_line.setSizePolicy(sizePolicy1)
        self.trend_line.setMinimumSize(QSize(30, 25))
        self.trend_line.setCheckable(True)

        self.gridLayout.addWidget(self.trend_line, 4, 0, 1, 1)

        self.horizontal_line = QToolButton(self.centralwidget)
        self.horizontal_line.setObjectName(u"horizontal_line")
        sizePolicy1.setHeightForWidth(self.horizontal_line.sizePolicy().hasHeightForWidth())
        self.horizontal_line.setSizePolicy(sizePolicy1)
        self.horizontal_line.setMinimumSize(QSize(30, 25))
        self.horizontal_line.setCheckable(True)

        self.gridLayout.addWidget(self.horizontal_line, 2, 2, 1, 1)

        self.box = QToolButton(self.centralwidget)
        self.box.setObjectName(u"box")
        sizePolicy1.setHeightForWidth(self.box.sizePolicy().hasHeightForWidth())
        self.box.setSizePolicy(sizePolicy1)
        self.box.setMinimumSize(QSize(30, 25))
        self.box.setCheckable(True)

        self.gridLayout.addWidget(self.box, 5, 0, 1, 1)

        self.vertical_line = QToolButton(self.centralwidget)
        self.vertical_line.setObjectName(u"vertical_line")
        sizePolicy1.setHeightForWidth(self.vertical_line.sizePolicy().hasHeightForWidth())
        self.vertical_line.setSizePolicy(sizePolicy1)
        self.vertical_line.setMinimumSize(QSize(30, 25))
        self.vertical_line.setCheckable(True)

        self.gridLayout.addWidget(self.vertical_line, 2, 0, 1, 1)

        self.group = QToolButton(self.centralwidget)
        self.group.setObjectName(u"group")
        sizePolicy1.setHeightForWidth(self.group.sizePolicy().hasHeightForWidth())
        self.group.setSizePolicy(sizePolicy1)
        self.group.setMinimumSize(QSize(30, 25))
        self.group.setCheckable(True)

        self.gridLayout.addWidget(self.group, 1, 2, 1, 1)

        self.rr_tool = QToolButton(self.centralwidget)
        self.rr_tool.setObjectName(u"rr_tool")
        sizePolicy1.setHeightForWidth(self.rr_tool.sizePolicy().hasHeightForWidth())
        self.rr_tool.setSizePolicy(sizePolicy1)
        self.rr_tool.setMinimumSize(QSize(30, 25))
        self.rr_tool.setCheckable(True)

        self.gridLayout.addWidget(self.rr_tool, 5, 2, 1, 1)


        self.verticalLayout.addLayout(self.gridLayout)

        self.checkBox_3 = QCheckBox(self.centralwidget)
        self.checkBox_3.setObjectName(u"checkBox_3")
        sizePolicy1.setHeightForWidth(self.checkBox_3.sizePolicy().hasHeightForWidth())
        self.checkBox_3.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.checkBox_3)


        self.gridLayout_3.addLayout(self.verticalLayout, 3, 6, 1, 1)

        self.label_4 = QLabel(self.centralwidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.label_4, 6, 2, 1, 1)

        self.connection_state = QLabel(self.centralwidget)
        self.connection_state.setObjectName(u"connection_state")
        sizePolicy2.setHeightForWidth(self.connection_state.sizePolicy().hasHeightForWidth())
        self.connection_state.setSizePolicy(sizePolicy2)

        self.gridLayout_3.addWidget(self.connection_state, 6, 3, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setSizeConstraint(QLayout.SetMaximumSize)
        self.label = QLabel(self.centralwidget)
        self.label.setObjectName(u"label")
        sizePolicy2.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy2)

        self.horizontalLayout_2.addWidget(self.label)

        self.go_to_date = QDateTimeEdit(self.centralwidget)
        self.go_to_date.setObjectName(u"go_to_date")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Maximum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.go_to_date.sizePolicy().hasHeightForWidth())
        self.go_to_date.setSizePolicy(sizePolicy3)

        self.horizontalLayout_2.addWidget(self.go_to_date)


        self.gridLayout_3.addLayout(self.horizontalLayout_2, 6, 0, 1, 2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setSizeConstraint(QLayout.SetMaximumSize)
        self.custom_resample = QTextEdit(self.centralwidget)
        self.custom_resample.setObjectName(u"custom_resample")
        sizePolicy4 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.custom_resample.sizePolicy().hasHeightForWidth())
        self.custom_resample.setSizePolicy(sizePolicy4)
        self.custom_resample.setMinimumSize(QSize(0, 0))
        self.custom_resample.setMaximumSize(QSize(16777215, 40))

        self.horizontalLayout_3.addWidget(self.custom_resample)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.resample_1min = QPushButton(self.centralwidget)
        self.resample_1min.setObjectName(u"resample_1min")
        self.resample_1min.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1min.sizePolicy().hasHeightForWidth())
        self.resample_1min.setSizePolicy(sizePolicy3)
        self.resample_1min.setMinimumSize(QSize(0, 40))
        self.resample_1min.setMaximumSize(QSize(16777215, 40))
        self.resample_1min.setCheckable(True)
        self.resample_1min.setChecked(True)
        self.resample_1min.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1min)

        self.resample_5min = QPushButton(self.centralwidget)
        self.resample_5min.setObjectName(u"resample_5min")
        self.resample_5min.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_5min.sizePolicy().hasHeightForWidth())
        self.resample_5min.setSizePolicy(sizePolicy3)
        self.resample_5min.setMinimumSize(QSize(0, 40))
        self.resample_5min.setMaximumSize(QSize(16777215, 40))
        self.resample_5min.setCheckable(True)
        self.resample_5min.setChecked(False)
        self.resample_5min.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_5min)

        self.resample_15min = QPushButton(self.centralwidget)
        self.resample_15min.setObjectName(u"resample_15min")
        self.resample_15min.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_15min.sizePolicy().hasHeightForWidth())
        self.resample_15min.setSizePolicy(sizePolicy3)
        self.resample_15min.setMinimumSize(QSize(0, 40))
        self.resample_15min.setMaximumSize(QSize(16777215, 40))
        self.resample_15min.setCheckable(True)
        self.resample_15min.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_15min)

        self.resample_1h = QPushButton(self.centralwidget)
        self.resample_1h.setObjectName(u"resample_1h")
        self.resample_1h.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1h.sizePolicy().hasHeightForWidth())
        self.resample_1h.setSizePolicy(sizePolicy3)
        self.resample_1h.setMinimumSize(QSize(0, 40))
        self.resample_1h.setMaximumSize(QSize(16777215, 40))
        self.resample_1h.setCheckable(True)
        self.resample_1h.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1h)

        self.resample_4h = QPushButton(self.centralwidget)
        self.resample_4h.setObjectName(u"resample_4h")
        self.resample_4h.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_4h.sizePolicy().hasHeightForWidth())
        self.resample_4h.setSizePolicy(sizePolicy3)
        self.resample_4h.setMinimumSize(QSize(0, 40))
        self.resample_4h.setMaximumSize(QSize(16777215, 40))
        self.resample_4h.setCheckable(True)
        self.resample_4h.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_4h)

        self.resample_1d = QPushButton(self.centralwidget)
        self.resample_1d.setObjectName(u"resample_1d")
        self.resample_1d.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1d.sizePolicy().hasHeightForWidth())
        self.resample_1d.setSizePolicy(sizePolicy3)
        self.resample_1d.setMinimumSize(QSize(0, 40))
        self.resample_1d.setMaximumSize(QSize(16777215, 40))
        self.resample_1d.setCheckable(True)
        self.resample_1d.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1d)

        self.resample_1w = QPushButton(self.centralwidget)
        self.resample_1w.setObjectName(u"resample_1w")
        self.resample_1w.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1w.sizePolicy().hasHeightForWidth())
        self.resample_1w.setSizePolicy(sizePolicy3)
        self.resample_1w.setMinimumSize(QSize(0, 40))
        self.resample_1w.setMaximumSize(QSize(16777215, 40))
        self.resample_1w.setCheckable(True)
        self.resample_1w.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1w)

        self.resample_1m = QPushButton(self.centralwidget)
        self.resample_1m.setObjectName(u"resample_1m")
        self.resample_1m.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1m.sizePolicy().hasHeightForWidth())
        self.resample_1m.setSizePolicy(sizePolicy3)
        self.resample_1m.setMinimumSize(QSize(0, 40))
        self.resample_1m.setMaximumSize(QSize(16777215, 40))
        self.resample_1m.setCheckable(True)
        self.resample_1m.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1m)

        self.resample_1y = QPushButton(self.centralwidget)
        self.resample_1y.setObjectName(u"resample_1y")
        self.resample_1y.setEnabled(False)
        sizePolicy3.setHeightForWidth(self.resample_1y.sizePolicy().hasHeightForWidth())
        self.resample_1y.setSizePolicy(sizePolicy3)
        self.resample_1y.setMinimumSize(QSize(0, 40))
        self.resample_1y.setMaximumSize(QSize(16777215, 40))
        self.resample_1y.setCheckable(True)
        self.resample_1y.setAutoExclusive(True)

        self.horizontalLayout.addWidget(self.resample_1y)


        self.horizontalLayout_3.addLayout(self.horizontalLayout)


        self.gridLayout_3.addLayout(self.horizontalLayout_3, 0, 1, 1, 5)

        self.instrument = QComboBox(self.centralwidget)
        self.instrument.addItem("")
        self.instrument.setObjectName(u"instrument")
        sizePolicy2.setHeightForWidth(self.instrument.sizePolicy().hasHeightForWidth())
        self.instrument.setSizePolicy(sizePolicy2)
        self.instrument.setMaximumSize(QSize(16777215, 40))

        self.gridLayout_3.addWidget(self.instrument, 0, 0, 1, 1)

        self.auto_resample = QCheckBox(self.centralwidget)
        self.auto_resample.setObjectName(u"auto_resample")
        sizePolicy1.setHeightForWidth(self.auto_resample.sizePolicy().hasHeightForWidth())
        self.auto_resample.setSizePolicy(sizePolicy1)
        self.auto_resample.setMaximumSize(QSize(70, 16777215))
        self.auto_resample.setChecked(True)

        self.gridLayout_3.addWidget(self.auto_resample, 0, 6, 1, 1)

        self.chart_placeholder = QVBoxLayout()
        self.chart_placeholder.setSpacing(9)
        self.chart_placeholder.setObjectName(u"chart_placeholder")
        self.chart_placeholder.setSizeConstraint(QLayout.SetNoConstraint)

        self.gridLayout_3.addLayout(self.chart_placeholder, 1, 0, 4, 6)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setMinimumSize(QSize(0, 25))
        self.label_3.setMaximumSize(QSize(16777215, 30))

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.market_order = QToolButton(self.centralwidget)
        self.market_order.setObjectName(u"market_order")
        self.market_order.setMinimumSize(QSize(30, 25))

        self.gridLayout_2.addWidget(self.market_order, 0, 1, 1, 1)

        self.limit_bracket_order = QToolButton(self.centralwidget)
        self.limit_bracket_order.setObjectName(u"limit_bracket_order")
        self.limit_bracket_order.setMinimumSize(QSize(30, 25))

        self.gridLayout_2.addWidget(self.limit_bracket_order, 1, 0, 1, 1)

        self.stop_bracket_order = QToolButton(self.centralwidget)
        self.stop_bracket_order.setObjectName(u"stop_bracket_order")
        self.stop_bracket_order.setMinimumSize(QSize(30, 25))

        self.gridLayout_2.addWidget(self.stop_bracket_order, 1, 1, 1, 1)

        self.feather_order = QToolButton(self.centralwidget)
        self.feather_order.setObjectName(u"feather_order")
        self.feather_order.setMinimumSize(QSize(30, 25))

        self.gridLayout_2.addWidget(self.feather_order, 2, 0, 1, 1)

        self.exit_all_order = QToolButton(self.centralwidget)
        self.exit_all_order.setObjectName(u"exit_all_order")
        self.exit_all_order.setMinimumSize(QSize(30, 25))

        self.gridLayout_2.addWidget(self.exit_all_order, 2, 1, 1, 1)


        self.gridLayout_3.addLayout(self.gridLayout_2, 1, 6, 1, 1)

        self.right_button = QPushButton(self.centralwidget)
        self.right_button.setObjectName(u"right_button")

        self.gridLayout_3.addWidget(self.right_button, 6, 5, 1, 1)

        self.ta_object_properties = QGridLayout()
        self.ta_object_properties.setObjectName(u"ta_object_properties")
        self.thickness_spinner = QSpinBox(self.centralwidget)
        self.thickness_spinner.setObjectName(u"thickness_spinner")
        sizePolicy5 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.thickness_spinner.sizePolicy().hasHeightForWidth())
        self.thickness_spinner.setSizePolicy(sizePolicy5)
        self.thickness_spinner.setMinimumSize(QSize(30, 25))
        self.thickness_spinner.setMinimum(1)
        self.thickness_spinner.setMaximum(10)

        self.ta_object_properties.addWidget(self.thickness_spinner, 0, 0, 1, 1)

        self.drawing_freq = QLineEdit(self.centralwidget)
        self.drawing_freq.setObjectName(u"drawing_freq")
        sizePolicy5.setHeightForWidth(self.drawing_freq.sizePolicy().hasHeightForWidth())
        self.drawing_freq.setSizePolicy(sizePolicy5)
        self.drawing_freq.setMinimumSize(QSize(0, 0))
        self.drawing_freq.setMaximumSize(QSize(70, 16777215))

        self.ta_object_properties.addWidget(self.drawing_freq, 1, 0, 1, 1)

        self.drawing_metadata = QLineEdit(self.centralwidget)
        self.drawing_metadata.setObjectName(u"drawing_metadata")
        sizePolicy5.setHeightForWidth(self.drawing_metadata.sizePolicy().hasHeightForWidth())
        self.drawing_metadata.setSizePolicy(sizePolicy5)
        self.drawing_metadata.setMaximumSize(QSize(70, 16777215))

        self.ta_object_properties.addWidget(self.drawing_metadata, 2, 0, 1, 1)


        self.gridLayout_3.addLayout(self.ta_object_properties, 2, 6, 1, 1)

        self.left_button = QPushButton(self.centralwidget)
        self.left_button.setObjectName(u"left_button")

        self.gridLayout_3.addWidget(self.left_button, 6, 4, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1101, 20))
        self.menuqraph = QMenu(self.menubar)
        self.menuqraph.setObjectName(u"menuqraph")
        self.menutest = QMenu(self.menubar)
        self.menutest.setObjectName(u"menutest")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuqraph.menuAction())
        self.menubar.addAction(self.menutest.menuAction())
        self.menuqraph.addAction(self.save)
        self.menuqraph.addAction(self.save_as)
        self.menuqraph.addAction(self.load)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.save.setText(QCoreApplication.translate("MainWindow", u"&save", None))
        self.save_as.setText(QCoreApplication.translate("MainWindow", u"sa&ve as", None))
        self.load.setText(QCoreApplication.translate("MainWindow", u"&load", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"TA", None))
        self.channel_system.setText(QCoreApplication.translate("MainWindow", u"//", None))
        self.trend_line.setText(QCoreApplication.translate("MainWindow", u"/", None))
        self.horizontal_line.setText(QCoreApplication.translate("MainWindow", u"_", None))
        self.box.setText(QCoreApplication.translate("MainWindow", u"[]", None))
        self.vertical_line.setText(QCoreApplication.translate("MainWindow", u"|", None))
        self.group.setText(QCoreApplication.translate("MainWindow", u"G", None))
        self.rr_tool.setText(QCoreApplication.translate("MainWindow", u"rr", None))
        self.checkBox_3.setText(QCoreApplication.translate("MainWindow", u"Hide all", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Connection state", None))
        self.connection_state.setText(QCoreApplication.translate("MainWindow", u"Lag", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"GOTO", None))
        self.custom_resample.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Sans Serif'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">1h</p></body></html>", None))
        self.resample_1min.setText(QCoreApplication.translate("MainWindow", u"1", None))
        self.resample_5min.setText(QCoreApplication.translate("MainWindow", u"5", None))
        self.resample_15min.setText(QCoreApplication.translate("MainWindow", u"15", None))
        self.resample_1h.setText(QCoreApplication.translate("MainWindow", u"1h", None))
        self.resample_4h.setText(QCoreApplication.translate("MainWindow", u"4h", None))
        self.resample_1d.setText(QCoreApplication.translate("MainWindow", u"D", None))
        self.resample_1w.setText(QCoreApplication.translate("MainWindow", u"W", None))
        self.resample_1m.setText(QCoreApplication.translate("MainWindow", u"M", None))
        self.resample_1y.setText(QCoreApplication.translate("MainWindow", u"Y", None))
        self.instrument.setItemText(0, QCoreApplication.translate("MainWindow", u"XBTUSDT Bybit", None))

        self.auto_resample.setText(QCoreApplication.translate("MainWindow", u"auto", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Trade", None))
        self.market_order.setText(QCoreApplication.translate("MainWindow", u"M", None))
        self.limit_bracket_order.setText(QCoreApplication.translate("MainWindow", u"=", None))
        self.stop_bracket_order.setText(QCoreApplication.translate("MainWindow", u"/", None))
        self.feather_order.setText(QCoreApplication.translate("MainWindow", u"#", None))
        self.exit_all_order.setText(QCoreApplication.translate("MainWindow", u"!!", None))
        self.right_button.setText(QCoreApplication.translate("MainWindow", u">", None))
        self.left_button.setText(QCoreApplication.translate("MainWindow", u"<", None))
        self.menuqraph.setTitle(QCoreApplication.translate("MainWindow", u"&qraph", None))
        self.menutest.setTitle(QCoreApplication.translate("MainWindow", u"test", None))
    # retranslateUi

