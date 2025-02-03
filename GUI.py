#!/usr/bin/python

# -*- coding: utf-8 -*-

# Module metadata variables
__author__ = "David del Rio Aledo"
__credits__ = ["David del Rio Aledo", "Jesus Vazquez"]
__license__ = "Creative Commons Attribution-NonCommercial-NoDerivs 4.0 Unported License https://creativecommons.org/licenses/by-nc-nd/4.0/"
__version__ = "0.1.0"
__maintainer__ = "David del Rio Aledo"
__email__ = "ddelrioa@cnic.es"
__status__ = "Development"


import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QAction, QPushButton, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QAction, QPushButton, QVBoxLayout, QWidget, QHeaderView, QShortcut
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QAction, QPushButton, QVBoxLayout, QWidget, QHeaderView, QSizePolicy, QFileDialog
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QAction, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QSpacerItem, QMenu, QAction, QToolButton, QApplication, QVBoxLayout, QWidgetAction
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QComboBox, QAction, QPushButton, QHBoxLayout, QVBoxLayout, QWidget, QFileDialog, QSpacerItem, QSizePolicy, QLabel, QLineEdit, QTextEdit,QSplitter, QToolBar, QAction,QTextBrowser, QDialog, QPlainTextEdit, QMessageBox, QGridLayout, QToolTip, QListWidget, QListWidgetItem, QButtonGroup,QCheckBox
from PyQt5.QtGui import QFont, QIcon, QSyntaxHighlighter, QTextCharFormat, QColor, QKeySequence,QTextCursor, QPixmap, QPainter, QBrush, QPainterPath, QBitmap, QKeyEvent
from PyQt5.QtCore import Qt, QRegExp, QProcess, QTimer, QPoint, QRect, pyqtSignal, pyqtProperty, QPropertyAnimation, QRectF, QSize, QTextCodec, QIODevice


from PyQt5.QtGui import QClipboard
from PyQt5.QtCore import Qt,QProcess
import pyautogui

import os
import ast
import shutil
from datetime import datetime
import glob

#########################
###  Project Folder  ####
#########################

project_folder=None
welcome_message_shown=False


#########################
###  Functions names ####
#########################

custom_dir=os.path.join(os.getcwd(),"customfunctions/custom.py")
script_path=os.path.join(os.getcwd(), "fusion_openclose_code.py")

if os.path.exists(custom_dir):

    with open (custom_dir, 'r') as file:
        tree=ast.parse(file.read(), filename=custom_dir)

        function_names=[]

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            docstring=ast.get_docstring(node)
            if docstring is None or '### No readable function ###' not in docstring:
                function_names.append(node.name)

    function_names.insert(0,"")


elif os.path.exists(script_path):

    with open (script_path, 'r') as file:
        tree=ast.parse(file.read(), filename=script_path)

        function_names=[]

        for node in tree.body:
            if isinstance(node, ast.FunctionDef):
                docstring=ast.get_docstring(node)
                if docstring is None or '### No readable function ###' not in docstring:
                    function_names.append(node.name)

        function_names.insert(0,"")

else:
    print('It has not been found the core python code')


class TableWidget(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        #######################
        ###  Crear ventana ####
        #######################

        self.setWindowTitle('Cl-Open')
        self.setGeometry(300, 300, 800, 700)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Layout principal
        self.left_layout = QVBoxLayout()

        # Agregar titulos de los parametros
        self.param_title = QLabel('PARAMETER INPUTS')
        font = QFont()
        font.setBold(True)
        self.param_title.setFont(font)
        self.left_layout.addWidget(self.param_title)

        # Agregar la entrada de parámetros
        self.parameter_input = ParameterInput()
        self.left_layout.addWidget(self.parameter_input)

        # Agregar titulos de la tabla
        self.table_title = QLabel('COLUMN HEADERS TABLE')
        self.table_title.setFont(font)
        self.left_layout.addWidget(self.table_title)

        self.tableWidget = QTableWidget()
        self.tableWidget.setRowCount(1)  # Iniciar con una fila
        self.tableWidget.setColumnCount(3)  # Solo 3 columnas
        self.tableWidget.setHorizontalHeaderLabels(['Open Columns', 'Close Columns', 'Functions'])
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectItems)

        self.loadComboBoxItems()
        self.left_layout.addWidget(self.tableWidget)

        hbox = QHBoxLayout()
        #hbox.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.addRowButton = QPushButton("+")
        self.addRowButton.clicked.connect(self.addRow)
        self.addRowButton.setFixedSize(30, 30)
        hbox.addWidget(self.addRowButton, alignment=Qt.AlignRight)

        hbox.addStretch()

        # Compatibility Selection
        self.loadTableButton = QComboBox()
        defaults_options=['Load Default Table', 'Comet-ProteomeDiscoverer', 'Comet-Comet', 'MSFragger-MSFragger', 'MSFragger-Comet', 'Comet-MSFragger']
        self.loadTableButton.addItems(defaults_options)
        self.loadTableButton.currentIndexChanged.connect(self.loadTable)
        hbox.addWidget(self.loadTableButton)

        self.left_layout.addLayout(hbox)

        # Botón RUN
        self.runButton = QPushButton("RUN")
        self.runButton.clicked.connect(self.run_script)
        self.left_layout.addWidget(self.runButton)

        # Consola de salida con título
        self.console_layout = QVBoxLayout()
        self.console_title = QLabel('STATUS INFORMATION')
        self.console_title.setFont(font)
        self.console_layout.addWidget(self.console_title)

        # Consola de salida
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)

        self.console_layout.addWidget(self.console_output)

        # Splitter para ajustar el tamaño
        splitter = QSplitter(Qt.Horizontal)
        left_widget = QWidget()
        left_widget.setLayout(self.left_layout)
        right_widget = QWidget()
        right_widget.setLayout(self.console_layout)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)

        # Ajuste del tamaño inicial de los widgets en el QSplitter
        splitter.setSizes([100, 2000])
        self.main_layout.addWidget(splitter)


        # Acciones de atajo para copiar y pegar
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.copy)
        self.addAction(copyAction)

        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.triggered.connect(self.paste)
        self.addAction(pasteAction)


        help_text = self.read_help_text()

                # Crear la barra de herramientas
        toolbar = QToolBar("Toolbar")
        # Aplicar estilo personalizado a la barra de herramientas
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #444;
                border: 2px solid #555;
                padding: 0px;
                spacing: 5px;
            }
            QToolButton {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #555;
                border: 1px solid #888;
            }
        """)
        self.addToolBar(toolbar)


        #Crear un main para que se pueda volver al inicio
        main_action=QAction("Home", self)
        main_action.triggered.connect(self.go_to_main_window)
        toolbar.addAction(main_action)

        #Crear un mantein fasta para que se pueda almacenar los fastas
        inport_menu = QMenu("Inport", self)
        inport_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        fasta_action=QAction("Fasta", self)
        fasta_action.triggered.connect(self.mantein_fasta)
        inport_menu.addAction(fasta_action)

        toolbar.addAction(inport_menu.menuAction())

        # Crear herramienta de developer
        developer_action=QAction("Developer", self)
        developer_action.triggered.connect(self.show_developereditor)
        toolbar.addAction(developer_action)


        # Crear accion de ayuda
        help_action = QAction("Help", self)
        help_text = self.read_help_text()
        help_action.triggered.connect(lambda: self.show_help(help_text))
        # Agregar acción a la barra de herramientas
        toolbar.addAction(help_action)

        self.show()



    ####################
    ###  Funcciones ####
    ####################


    def mantein_fasta(self):

        self.fasta_window = Fasta()
        self.fasta_window.show()


    def go_to_main_window(self):

        self.hide()

        self.main_window=ClOpenSearch()
        self.main_window.show()


    def show_developereditor (self):

        self.developer_window=DeveloperEditor()
        self.developer_window.show()


    def show_help(self, help_text):

        help_window = HelpWindow(help_text)
        help_window.exec_()


    def read_help_text(self):

        help_path=os.path.join(os.getcwd(), "Config/Help.txt")
        
        with open(help_path, "r") as file:
            help_text = file.read()

        return help_text


    def log_to_console(self, message):

        self.console_output.append(message)

    def loadComboBoxItems(self):

        #items = ['','num_function', 'xcorr_corr', 'change_modifiedpeptide', 'prev_aa', 'next_aa', 'change_sep', 'count_sep', 'set_fix_mod', 'exp_mz', 'NA_def', 'theorical_mass']
        for row in range(self.tableWidget.rowCount()):
            combo = QComboBox()
            combo.addItems(function_names)
            self.tableWidget.setCellWidget(row, 2, combo)

    def addRow(self):

        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)

        for col in range(self.tableWidget.columnCount()):
            if col == 2:  # Si es la tercera columna
                combo = QComboBox()
                #options = ['', 'num_function', 'xcorr_corr', 'change_modifiedpeptide', 'prev_aa', 'next_aa', 'change_sep', 'count_sep', 'set_fix_mod', 'exp_mz', 'NA_def','theorical_mass']
                combo.addItems(function_names)
                combo.setEditable(True)
                prev_combo = self.tableWidget.cellWidget(row_count - 1, col)  # Obtener el QComboBox de la fila anterior
                if prev_combo:  # Si hay un QComboBox en la fila anterior
                    combo.setCurrentText(prev_combo.currentText())  # Establecer el mismo valor seleccionado
                self.tableWidget.setCellWidget(row_count, col, combo)
            else:
                item = QTableWidgetItem('')
                self.tableWidget.setItem(row_count, col, item)

    def copy(self):

        selection = self.tableWidget.selectedRanges()

        if selection:

            rows = sorted(set(index.row() for range in selection for index in range.topLeft().row() + range.rowCount()))
            columns = sorted(set(index.column() for range in selection for index in range.topLeft().column() + range.columnCount()))
            table = '\t'.join([self.tableWidget.horizontalHeaderItem(column).text() for column in columns]) + '\n'

            for row in rows:

                table += '\t'.join([self.tableWidget.item(row, column).text() for column in columns]) + '\n'

            clipboard = QApplication.clipboard()
            clipboard.setText(table)

    def paste(self):

        clipboard = QApplication.clipboard()
        data = clipboard.text().split('\n')
        rows = len(data)
        columns = len(data[0].split('\t'))

        currentRow = self.tableWidget.currentRow()
        currentColumn = self.tableWidget.currentColumn()

        for i, row in enumerate(data):
            if i + currentRow >= self.tableWidget.rowCount():
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.loadComboBoxItems()  # Asegurar que se creen los ComboBox para la nueva fila

            cells = row.split('\t')
            for j, cell in enumerate(cells):
                if j + currentColumn >= self.tableWidget.columnCount():
                    self.tableWidget.insertColumn(self.tableWidget.columnCount())

                self.tableWidget.setItem(i + currentRow, j + currentColumn, QTableWidgetItem(cell))

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:

            currentRow = self.tableWidget.currentRow()
            currentColumn = self.tableWidget.currentColumn()
            item = self.tableWidget.item(currentRow, currentColumn)

            if item is not None:

                self.tableWidget.editItem(item)

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copy()

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            self.paste()

        else:

            super().keyPressEvent(event)

            if event.key() == Qt.Key_Left:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentColumn > 0:

                    self.tableWidget.setCurrentCell(currentRow, currentColumn - 1)

            elif event.key() == Qt.Key_Right:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentColumn < self.tableWidget.columnCount() - 1:

                    self.tableWidget.setCurrentCell(currentRow, currentColumn + 1)

            elif event.key() == Qt.Key_Up:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentRow > 0:

                    self.tableWidget.setCurrentCell(currentRow - 1, currentColumn)

            elif event.key() == Qt.Key_Down:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentRow < self.tableWidget.rowCount() - 1:

                    self.tableWidget.setCurrentCell(currentRow + 1, currentColumn)

    def saveComboBoxIndices(self):

        self.savedComboBoxIndices = []

        for row in range(self.tableWidget.rowCount()):
            combo = self.tableWidget.cellWidget(row, 2)  # Obtener el QComboBox en la tercera columna
            if combo:
                index = combo.currentIndex()  # Obtener el índice seleccionado
                self.savedComboBoxIndices.append(index)  # Guardar el índice en la lista
            else:
                self.savedComboBoxIndices.append(-1)  # Si no hay QComboBox en la celda, guardar -1 en la lista

    def restoreComboBoxIndices(self):

        for row, index in enumerate(self.savedComboBoxIndices):

            combo = self.tableWidget.cellWidget(row, 2)  # Obtener el QComboBox en la tercera columna

            if combo and index != -1:
                combo.setCurrentIndex(index)  # Restaurar el índice seleccionado en el QComboBox

    def restoreTableItems(self, table):

        for row_num, row_data in enumerate(table):

            row_items = row_data.strip().split('\t')

            for col_num, data in enumerate(row_items):

                item = QTableWidgetItem(data)
                self.tableWidget.setItem(row_num, col_num, item)

    def loadTable(self):

        #file_path, _ = QFileDialog.getOpenFileName(self, 'Open Text File', filter="Text Files (*.txt)")
        #['Load Default Table', 'Comet-ProteomeDiscoverer', 'Comet-Comet', 'MSFragger-MSFragger', 'MSFragger-Comet', 'Comet-MSFragger']

        option = self.loadTableButton.currentText()

        if option == 'Comet-ProteomeDiscoverer':
            file_path = os.path.join(os.getcwd(), "Config/HeadersList.txt")
        elif option == 'Comet-Comet':
            file_path = os.path.join(os.getcwd(), "Config/HeadersList_Comet-Comet.txt")
        else:
            file_path = ''
            self.tableWidget.clearContents()
            self.tableWidget.setRowCount(1)
            self.loadComboBoxItems()

        #file_path=os.path.join(os.getcwd(), "Config/HeadersList.txt")

        if os.path.exists(file_path):

            with open(file_path, 'r') as file:
                lines = file.readlines()[1:]  # Leer todas las líneas excepto la primera (encabezados)
                self.tableWidget.setRowCount(0)

                for row_num, row_data in enumerate(lines):
                    self.tableWidget.insertRow(row_num)
                    row_items = row_data.strip().split('\t')

                    for col_num, data in enumerate(row_items):
                        item = QTableWidgetItem(data)
                        self.tableWidget.setItem(row_num, col_num, item)
            
            # Convertir las celdas vacías en QComboBoxes
            for row in range(self.tableWidget.rowCount()):

                combo = QComboBox()
                #options = ['', 'num_function', 'xcorr_corr', 'change_modifiedpeptide', 'prev_aa', 'next_aa', 'change_sep', 'count_sep', 'set_fix_mod', 'exp_mz', 'NA_def', 'theorical_mass']
                combo.addItems(function_names)
                combo.setEditable(True)

                if not self.tableWidget.item(row, 2) or not self.tableWidget.item(row, 2).text().strip():
                    self.tableWidget.setCellWidget(row, 2, combo)

                else:
                    combo.setCurrentText(self.tableWidget.item(row, 2).text().strip())
                    self.tableWidget.setCellWidget(row, 2, combo)

            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.resizeRowsToContents()


    ### Ejecutar script ###

    def run_script(self):

        # Obtener los parámetros de entrada
        params = self.parameter_input.get_parameters()

        # Crear un archivo temporal para la tabla
        table_path = os.path.join(os.getcwd(), "temp_table.txt")

        with open(table_path, 'w') as file:

            headers = [self.tableWidget.horizontalHeaderItem(i).text() for i in range(self.tableWidget.columnCount())]
            file.write('\t'.join(headers) + '\n')

            for row in range(self.tableWidget.rowCount()):
                row_data = []

                for col in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, col)

                    if col == 2:  # Columna de ComboBox
                        combo = self.tableWidget.cellWidget(row, col)

                        if combo is not None:
                            row_data.append(combo.currentText())

                        else:
                            row_data.append('')

                    else:
                        row_data.append(item.text() if item is not None else '')

                file.write('\t'.join(row_data) + '\n')

        # Crear los argumentos para el script

        print(os.getcwd())

        script_path=os.path.join(os.getcwd(), "fusion_openclose_code.py")

        args = []

        for key, value in zip(['-op', '-cl', '-mdl', '-o', '-pep', '-mod', '-pl', '-c'], params):
            if isinstance(value, str) and value.strip():  # Verificar si el valor no está vacío
                args.append(key)
                args.append(value.strip())

        args = [arg.strip() for arg in args if isinstance(arg, str) and arg.strip()]

        # Agregar el archivo temporal de la tabla como argumento
        args.append('-l')
        args.append(table_path)

        #cmd_line = " ".join([sys.executable, script_path] + args)
        #print(cmd_line)

        print(sys.executable)

        # Ejecutar el script
        process = QProcess(self)

        try:
            process.setProgram('python')
        except:
            try:
                process.setProgram('python3')
            except:
                try:
                    process.setProgram('py')
                except:
                    print('\n\n###       PYTHON NOT FOUND      ###\n\nPlease check if python is installed')


        process.setArguments([script_path] + args)
        process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process))
        process.readyReadStandardError.connect(lambda: self.handle_stderr(process))
        process.start()
        #process.waitForFinished()
        #sys.exit(app.exec_())

    def handle_stdout(self, process):

        data = process.readAllStandardOutput()
        stdout = bytes(data).decode('utf8')
        self.log_to_console(stdout)

    def handle_stderr(self, process):

        data = process.readAllStandardError()
        stderr = bytes(data).decode('utf8')
        self.log_to_console(stderr)


#####################
###  Crear Entry ####
#####################


class ParameterInput(QWidget):

    def __init__(self):

        super().__init__()

        # Crear etiquetas y campos de texto para cada parámetro
        self.param_labels = ['Input file from Open Search:', 'Input file from Close Search (Proteom Discoverer):',
                             'PD Modifications list:', 'Output directory:', 
                             'Peptide list to include from CloseSearch:', 'Modification list to include from CloseSearch:', 
                             'Path to txt file with comparation paths of Open and Close files:', 'Path to custom config.ini file:']
        
        # Valores predefinidos
        config_path=os.path.join(os.getcwd(), "Config/SHIFTS.ini")
        mdl_path=os.path.join(os.getcwd(), "Config/Modifications.xml")
        pathlist_path=os.path.join(os.getcwd(), "Config/path_equivalences.txt")
        pept_list=os.path.join(os.getcwd(), "Config/PepList.txt")
        mod_list=os.path.join(os.getcwd(), "Config/ModList.txt")

        self.param_defaults = ['', '', str(mdl_path), '', str(pept_list), str(mod_list), str(pathlist_path), str(config_path)]

        self.param_lineedits = [QLineEdit(default) for default in self.param_defaults]

        # Configurar el diseño vertical
        layout = QVBoxLayout()

        for label, lineedit in zip(self.param_labels, self.param_lineedits):
            layout.addWidget(QLabel(label))
            layout.addWidget(lineedit)

        self.setLayout(layout)

    def get_parameters(self):

        return [lineedit.text() for lineedit in self.param_lineedits]



############################
###  Crear Help Windows ####
############################


class HelpWindow(QDialog):

    def __init__(self, help_text):

        super().__init__()

        self.setWindowTitle("Help")
        self.setGeometry(300, 300, 400, 300)

        layout = QVBoxLayout(self)
        self.text_browser = QTextBrowser()
        self.text_browser.setPlainText(help_text)
        layout.addWidget(self.text_browser)


##########################
###  Developer Editor ####
##########################


class PythonHighlighter(QSyntaxHighlighter):

    def __init__(self, document):

        super().__init__(document)
        self.highlighting_rules = []

        # Palabras clave de Python en azul
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(0, 190, 255))  # Azul
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]

        for word in keywords:
            pattern = QRegExp(r'\b' + word + r'\b')
            self.highlighting_rules.append((pattern, keyword_format))

        # Nombres de funciones 
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(200, 255, 0))  # Verde lima
        self.highlighting_rules.append((QRegExp(r'\b[A-Za-z0-9_]+(?=\()'), function_format))

        # Cadenas
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(247, 255, 136))  # Amarillo
        self.highlighting_rules.append((QRegExp(r'".*"'), string_format))
        self.highlighting_rules.append((QRegExp(r"'.*'"), string_format))

        # Comentarios
        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(QColor(160, 160, 160))  # Gris
        self.highlighting_rules.append((QRegExp(r'#.*'), single_line_comment_format))

        # Numeros
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(184, 111, 190))  # Morado
        self.highlighting_rules.append((QRegExp(r'\b[0-9]+\b'), number_format))



    def highlightBlock(self, text):

        for pattern, format in self.highlighting_rules:

            expression = QRegExp(pattern)
            index = expression.indexIn(text)

            while index >= 0:

                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)



class DeveloperEditor(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()
        self.scriptinitial=""
        self.process=QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.loaded_script=False
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))
        
    def init_ui(self):

        self.setWindowTitle("Developer Editor")
        self.setGeometry(200, 200, 800, 600)

        # Editor
        editor_title = QLabel("Header transform function Creator [Python]", self)
        editor_title.setAlignment(Qt.AlignCenter)
        editor_title.setStyleSheet("font-weight: bold;")

        # Editor de texto
        self.editor = QPlainTextEdit(self)
        self.highlighter = PythonHighlighter(self.editor.document())

        # Aplicar estilo para fondo negro y texto blanco
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1E1E1E;
                color: #D4D4D4;
                font-family: Consolas;
                font-size: 12pt;
            }
        """)

        # Label consola de salida
        console_title = QLabel("Console output [Python]", self)
        console_title.setAlignment(Qt.AlignCenter)
        console_title.setStyleSheet("font-weight: bold;")

        # Consola de ejecucion
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                color: #000000;
                font-family: Consolas;
                font-size: 12pt;
            }
        """)

        # Botón de guardar
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.save_file)


        # Button reset script
        self.reset_button = QPushButton("Reset Script", self)
        self.reset_button.clicked.connect(self.reset_script)

        # Button load script
        self.load_button = QPushButton("Load Script", self)
        self.load_button.clicked.connect(self.load_script)


        # Boton para ejecutar el script
        self.run_button = QPushButton("Ejecute", self)
        self.run_button.clicked.connect(self.run_script)


        # Layouts
        console_layout  = QVBoxLayout()
        console_layout.addWidget(console_title)
        console_layout.addWidget(self.console)
        console_layout.addWidget(self.run_button)

        editor_layout  = QVBoxLayout()
        editor_layout.addWidget(editor_title)
        editor_layout .addWidget(self.editor)
        editor_layout .addWidget(self.save_button)
        editor_layout.addWidget(self.reset_button)
        editor_layout.addWidget(self.load_button)


        # Splitter to divide the space between console and editor
        splitter = QSplitter(Qt.Horizontal)
        console_container = QWidget()
        console_container.setLayout(console_layout)
        editor_container = QWidget()
        editor_container.setLayout(editor_layout)

        splitter.addWidget(console_container)
        splitter.addWidget(editor_container)

        # Set the splitter initial sizes
        splitter.setSizes([400, 400])

        # Widget central
        self.setCentralWidget(splitter)

        # Atajo de teclado para ejecutar el script
        execute_shortcut = QAction(self)
        execute_shortcut.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_B))
        execute_shortcut.triggered.connect(self.run_script)
        self.addAction(execute_shortcut)


    def reset_script(self):

        custom_dir = os.path.join(os.getcwd(), "customfunctions/custom.py")

        if os.path.exists(custom_dir):

            reply=QMessageBox.warning(self,
                "Reset Script",
                "Are you sure you want to reset the script to default seetings?\nAll added functions will be permanently erased!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No)

            if reply == QMessageBox.Yes:
                shutil.copy(script_path, custom_dir)

                QMessageBox.information(self, "Reset Script", "Custom Script has been reset.")

            else:
                QMessageBox.information(self, "Reset Script", "Reset operation cancelled.")


        else:
            QMessageBox.warning(self, "Reset Script", "Custom Script does not exist.")

    def load_script(self):

        custom_dir = os.path.join(os.getcwd(), "customfunctions/custom.py")

        if os.path.exists(custom_dir):

            with open(custom_dir, 'r') as file:
                lines = file.readlines()

            custom_functions_start = -1
            custom_functions_end = -1

            for i, line in enumerate(lines):

                if '### Custom Functions ###' in line.strip():
                    custom_functions_start = i + 1

                elif '########################' in line.strip():
                    custom_functions_end = i

                    break

            if custom_functions_start == -1 or custom_functions_end == -1:

                QMessageBox.critical(self, "Error", "Custom Functions Markers have not been found.")
                return

            custom_functions_lines = lines[custom_functions_start:custom_functions_end]
            self.editor.setPlainText(''.join(custom_functions_lines))
            self.loaded_script = True

            QMessageBox.information(self, "Load Script", "Custom Functions have been loaded into the editor.")

        else:
            QMessageBox.warning(self, "Load Script", "Custom Script does not exist.")



    def save_file(self):

        if os.path.exists(custom_dir):

            with open (custom_dir, 'r') as file:

                self.scriptinitial=file.readlines()


        elif os.path.exists(script_path):

            with open (script_path, 'r') as file:

                self.scriptinitial=file.readlines()



        custom_functions_start = -1
        custom_functions_end = -1

        # Buscar la posición de inicio y fin de las custom functions
        for i, line in enumerate(self.scriptinitial):
            if '### Custom Functions ###' in line.strip():
                custom_functions_start = i + 1

            elif '########################' in line.strip():
                custom_functions_end = i
                break
        if custom_functions_start == -1 or custom_functions_end == -1:
            QMessageBox.critical(self, "Error", "Custom Functions Markers have not been found")

            return

        # Obtener el contenido del editor
        editor_content = self.editor.toPlainText()

        # Actualizar las líneas
        new_functions_lines = [line + '\n' for line in editor_content.splitlines()]


        if self.loaded_script:

            #Si se cargo un archivo que reescriba el archivo entero
            updated_lines = (
                self.scriptinitial[:custom_functions_start]
                + ['\n']  # Add a newline before new functions
                + new_functions_lines
                + ['\n']  # Add a newline after new functions
                + self.scriptinitial[custom_functions_end:]
            )

        else:

            updated_lines = (
                self.scriptinitial[:custom_functions_end]
                + ['\n'] + new_functions_lines + ['\n']
                + self.scriptinitial[custom_functions_end:]
            )

        save_dir=os.path.join(os.getcwd(),"customfunctions")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if save_dir:

            save_path=os.path.join(save_dir, "custom.py")

            with open(save_path, 'w') as file:
                file.writelines(updated_lines)


        QMessageBox.information(self, "Custom Function Saved", "Custom Functions have been saved successfuly. Restar the program to use the new functions.")


    def run_script(self):

        script_content = self.editor.toPlainText() + "\n" + self.scriptinitial

        with open("temp_script.py", "w") as temp_file:
            temp_file.write(script_content)

        self.console.clear()
        self.process.start("python", ["temp_script.py"])
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)

    def handle_stdout(self):

        data = self.process.readAllStandardOutput()
        stdout = bytes(data).decode("utf8").strip()
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(stdout + "\n")

    def handle_stderr(self):

        data = self.process.readAllStandardError()
        stderr = bytes(data).decode("utf8").strip()
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(stderr + "\n")



#########################
###   Close Search   ####
#########################

class CloseSearch(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()
        self.max_simultaneous_processes = 1  # Define el número máximo de procesos simultáneos
        self.active_processes = 0
        self.process_queue = []


    def init_ui(self):

        global project_folder

        self.setWindowTitle('Cl-Open: Only Close Mode Search')
        self.setGeometry(300, 300, 800, 800)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Layout a la izquierda (file_layout)
        self.file_layout = QVBoxLayout()

        # Boton para seleccionar archivos
        self.select_file_button = QPushButton()
        self.select_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/Folder.png")))
        self.select_file_button.setIconSize(QSize(30, 30))
        self.select_file_button.setFixedSize(30, 30)
        
        self.select_file_button.clicked.connect(self.select_files)
        self.select_file_button.setToolTip("Select File")
        self.select_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.select_file_button)

        # Boton para chequear archivos
        self.check_file_button = QPushButton()
        self.check_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/CheckRaws.png")))
        self.check_file_button.setIconSize(QSize(30, 30))
        self.check_file_button.setFixedSize(30, 30)
        
        self.check_file_button.clicked.connect(self.check_files)
        self.check_file_button.setToolTip("Check Files")
        self.check_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.check_file_button)

        # Boton de RUN
        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/RunIm.jpg")))
        self.run_button.setIconSize(QSize(30, 30))
        self.run_button.setFixedSize(30, 30)
        
        self.run_button.clicked.connect(self.run_Close)
        self.run_button.setToolTip("Run Close Search")
        self.run_button.setToolTipDuration(10000)
        

        # Layout horizontal para los botones
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.select_file_button)
        self.button_layout.addWidget(self.check_file_button)
        self.button_layout.addStretch() 
        self.file_layout.addLayout(self.button_layout)

        self.button_layout.addWidget(self.run_button)


        # Title Raws
        self.raw_title = QLabel("Mass Spectometry Raw Files Selected")
        self.raw_title.setAlignment(Qt.AlignCenter)
        self.raw_title.setStyleSheet("font-weight: bold;")
        self.file_layout.addWidget(self.raw_title)


        # Lista de archivos seleccionados
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection) # Permite seleccion multiple con control y shift
        self.file_layout.addWidget(self.file_list)

        # Botón para eliminar archivos seleccionados
        #self.delete_file_button = QPushButton('Remove')
        #self.delete_file_button.clicked.connect(self.delete_file)
        #self.file_layout.addWidget(self.delete_file_button)

        # Widget para contener el layout de archivos
        file_widget = QWidget()
        file_widget.setLayout(self.file_layout)

        # Layout central (config_layout)
        self.config_layout = QVBoxLayout()

        # Title Select Platform
        self.mode_title = QLabel("Select Search Engine")
        self.mode_title.setAlignment(Qt.AlignLeft)
        self.mode_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.mode_title)

        # Modes Search layaout
        self.comet_button= QPushButton()
        self.comet_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/CometIm.png")))
        self.comet_button.setObjectName("comet_button")
        self.comet_button.setIconSize(QSize(50, 50))
        self.comet_button.setFixedSize(50, 50)
        self.comet_button.setCheckable(True)  # Hacer el boton alternable
        self.comet_button.clicked.connect(self.on_button_clicked)
        self.comet_button.setToolTip("Comet Mode")
        self.comet_button.setToolTipDuration(10000)

        self.fragger_button=QPushButton()
        self.fragger_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/FraggerIm.png")))
        self.fragger_button.setObjectName("fragger_button")
        self.fragger_button.setIconSize(QSize(50, 50))
        self.fragger_button.setFixedSize(50, 50)
        self.fragger_button.setCheckable(True)  # Hacer el boton alternable
        self.fragger_button.clicked.connect(self.on_button_clicked)
        self.fragger_button.setToolTip("MSFragger Mode")
        self.fragger_button.setToolTipDuration(10000)

        # Layout horizontal para los modos
        self.modes_layout = QHBoxLayout()
        self.modes_layout.addWidget(self.comet_button)
        self.modes_layout.addWidget(self.fragger_button)
        self.modes_layout.addStretch() 
        self.config_layout.addLayout(self.modes_layout)

        # Inicializar el QButtonGroup para manejar la exclusividad de los botones
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.comet_button)
        self.button_group.addButton(self.fragger_button)

        ###########





        # Title Fasta
        self.fasta_title = QLabel("Select Fasta")
        self.fasta_title.setAlignment(Qt.AlignLeft)
        self.fasta_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.fasta_title)

        # Fasta Selection
        self.fasta_selection_button = QComboBox()
        fasta_names=self.load_fasta()
        self.fasta_selection_button.addItems(fasta_names)
        self.config_layout.addWidget(self.fasta_selection_button)

        ###########






        # Title Config Params
        self.params_title = QLabel("Configuration Params of Selected Search Engine")
        self.params_title.setAlignment(Qt.AlignLeft)
        self.params_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.params_title)

        # Boton para cargar archivo de configuración
        self.load_config_button = QPushButton()
        self.load_config_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/loadIco.png")))
        self.load_config_button.setObjectName("load_config_button")
        self.load_config_button.setIconSize(QSize(30, 30))
        self.load_config_button.setFixedSize(30, 30)
        self.load_config_button.clicked.connect(self.load_configuration)
        self.load_config_button.setToolTip("Load Configuration")
        self.load_config_button.setToolTipDuration(10000)
        self.modes_layout.addWidget(self.load_config_button)

        # Boton para guardar la configuración
        self.save_config_button = QPushButton()
        self.save_config_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/SaveIco.png")))
        self.save_config_button.setObjectName("save_config_button")
        self.save_config_button.setIconSize(QSize(30, 30))
        self.save_config_button.setFixedSize(30, 30)
        self.save_config_button.clicked.connect(self.save_configuration)
        self.save_config_button.setToolTip("Save Configuration")
        self.save_config_button.setToolTipDuration(10000)
        self.modes_layout.addWidget(self.save_config_button)

        # Área de texto para editar el archivo de configuración
        self.config_text = QTextEdit()
        self.config_layout.addWidget(self.config_text)

        # Widget para contener el layout de configuración
        config_widget = QWidget()
        config_widget.setLayout(self.config_layout)

        # Layout a la derecha (console_layout)
        self.console_layout = QVBoxLayout()

        # Título de la consola
        self.console_title = QLabel('STATUS INFORMATION')
        font = QFont()
        font.setBold(True)
        self.console_title.setFont(font)
        self.console_layout.addWidget(self.console_title)

        # Consola de salida
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_layout.addWidget(self.console_output)


        # Widget para contener el layout de consola
        console_widget = QWidget()
        console_widget.setLayout(self.console_layout)

        # Añadir widgets al main_layout usando splitters
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC; /* Color del manejador */
                border: 1px dotted #707070; /* Borde punteado */
                width: 1px; /* Ancho del manejador */
            }
        """)
        splitter1.addWidget(file_widget)
        splitter1.addWidget(config_widget)
        splitter1.addWidget(console_widget)

        # Ajuste del tamaño inicial de los widgets en el QSplitter
        splitter1.setSizes([200, 400, 200])

        self.main_layout.addWidget(splitter1)



        # Crear la barra de herramientas
        toolbar = QToolBar("Toolbar")
        # Aplicar estilo personalizado a la barra de herramientas
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #444;
                border: 2px solid #555;
                padding: 0px;
                spacing: 5px;
            }
            QToolButton {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #555;
                border: 1px solid #888;
            }
        """)
        self.addToolBar(toolbar)


        #Crear un main para que se pueda volver al inicio
        main_action=QAction("Home", self)
        main_action.triggered.connect(self.go_to_main_window)
        toolbar.addAction(main_action)

        #Crear un mantein fasta para que se pueda almacenar los fastas
        inport_menu = QMenu("Inport", self)
        inport_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        fasta_action=QAction("Fasta", self)
        fasta_action.triggered.connect(self.mantein_fasta)
        inport_menu.addAction(fasta_action)

        toolbar.addAction(inport_menu.menuAction())


        # Crear accion de ayuda
        help_action = QAction("Help", self)
        help_text = self.read_help_text()
        help_action.triggered.connect(lambda: self.show_help(help_text))
        # Agregar acción a la barra de herramientas
        toolbar.addAction(help_action)


        ################
        ### Load log ###
        ################

        if project_folder:

            config_log_path=os.path.join(project_folder, ".clopen")

            #Obtener los logs y ordenarlos por fechas
            subdirs = [d for d in os.listdir(config_log_path) if os.path.isdir(os.path.join(config_log_path, d))]
            subdirs.sort(reverse=True)

            if subdirs:
                config_log=os.path.join(config_log_path, subdirs[0])
                config_file = glob.glob(os.path.join(config_log, "config_params_Closed*"))
                raw_file=glob.glob(os.path.join(config_log, "raw_files_closed*"))
                

                if config_file:

                    with open(config_file[0], 'r') as file:
                        config_text = file.read()
                        self.config_text.setPlainText(config_text)

                        # Desconectar señales
                        self.comet_button.clicked.disconnect(self.on_button_clicked)
                        self.fragger_button.clicked.disconnect(self.on_button_clicked)

                        # Seleccionar el boton sin ejecutar la función

                        if "comet" in config_file[0].lower():
                            self.comet_button.setChecked(True)

                        elif "fragger" in config_file[0].lower():
                            self.fragger_button.setChecked(True)

                        # Volver a conectar señales
                        self.comet_button.clicked.connect(self.on_button_clicked)
                        self.fragger_button.clicked.connect(self.on_button_clicked)


                else:
                    msg = "It cannot loaded the config params log."
                    QMessageBox.warning(self, "Configuration log file not found", msg)


                if raw_file:

                    with open(raw_file[0], 'r') as file:
                        lines=file.readlines()
                        self.file_list.clear()

                        for line in lines:
                            item = QListWidgetItem(line.strip())
                            self.file_list.addItem(item)

                else:
                    msg = "It cannot loaded the raws list log."
                    QMessageBox.warning(self, "Raws list log file not found", msg)



            else:
                msg = "It cannot loaded the log folder."
                QMessageBox.warning(self, "Log folder not found", msg)



        self.show()

    def start_next_process_fragger(self, searchtype):

        if self.active_processes < self.max_simultaneous_processes and self.process_queue:

            script_path, arguments, folder_log_path, index, files_before, program_basename = self.process_queue.pop(0)

            process = QProcess(self)
            process.setProgram("java")
            process.setArguments(arguments)
            # Conectar señales para manejar la salida estándar y error
            process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
            process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
            #### Mover los archivos salida de Fragger a la carpeta resultados ####
            process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename, 'Fragger', searchtype))
            # Iniciar el proceso
            process.start()
            self.active_processes += 1
            # Esperar hasta que el proceso termine
            #process.waitForFinished(-1)

    def start_next_process_comet(self, searchtype):

        if self.active_processes < self.max_simultaneous_processes and self.process_queue:

            script_path, arguments, folder_log_path, index, files_before, program_basename = self.process_queue.pop(0)

            process = QProcess(self)
            process.setProgram(script_path)
            process.setArguments(arguments)
            # Conectar señales para manejar la salida estándar y error
            process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
            process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
            process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename, 'Comet', searchtype))
            process.start()
            self.active_processes += 1


    def load_fasta (self):

        fastas_path = os.path.join(os.getcwd(), "fastas")

        if fastas_path:

            files = []
            for file_name in os.listdir(fastas_path):
                if os.path.isfile(os.path.join(fastas_path, file_name)):
                    files.append(file_name)

        files.insert(0,"")

        return files


    def mantein_fasta(self):

        self.fasta_window = Fasta()
        self.fasta_window.show()


    def go_to_main_window(self):

        self.hide()

        self.main_window=ClOpenSearch()
        self.main_window.show()


    def on_button_clicked(self):

        button = self.sender()

        if button.isChecked():

            self.button_group.setExclusive(True)
            self.button_group.setId(button, 1)

            button_name=button.objectName()

            if button_name=="comet_button":
                config_comet=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(config_comet, 'r') as file:
                    config_text = file.read()
                    self.config_text.setPlainText(config_text)

            if button_name=="fragger_button":

                config_fragger=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/closed_fragger.params")

                with open(config_fragger, 'r') as file:
                    config_text = file.read()
                    self.config_text.setPlainText(config_text)


        else:
            self.button_group.setId(button, 0)



    def run_Close(self):

        global project_folder

        checked_button=self.button_group.checkedButton()

        if checked_button is not None:

            button_name=checked_button.objectName()

        else:
            QMessageBox.critical(self, "No Search Engine Selected", "No Search Engine Selected")



        #### COMET ####

        if button_name=="comet_button":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text.toPlainText().strip()
            params_name="config_params_Closed_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_closed.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Closed-"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_closed.txt")

                else:
                    os.makedirs(config_folder)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_closed.txt")


            

            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        updated_lines.append(f"database_name = {selected_db_path}")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)
                return


            #Antes de ejecutar chequear los archivos
            self.check_files()

            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                folder_project=os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path)
                os.makedirs(folder_project)

            else:
                log_folder=os.path.join(project_folder, "logs")
                clopen_folder=os.path.join(project_folder, ".clopen")
                folder_log_path = os.path.join(log_folder, folder_name)
                clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                os.makedirs(folder_log_path)
                os.makedirs(clopen_folder_log_path)


            #Escribir los logs
            log_params_path = os.path.join(clopen_folder_log_path, params_name)
            log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_closed.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')





            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Iterar y ejecutar cada uno de los archivos
            '''

            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))

                process = QProcess(self)

                arguments = ["-P" + params_path, self.file_list.item(index).text()]
                process.setProgram(script_path)
                process.setArguments(arguments)
                # Conectar señales para manejar la salida estándar y error
                process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
                process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                process.start()
            '''

            #Iterar y ejecutar cada uno de los archivos
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-P" + params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_comet(searchtype='Closed')



        ### MSFRAGGER ###

        if button_name=="fragger_button":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text.toPlainText().strip()
            params_name="config_params_Closed_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_closed.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Closed-"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_closed.txt")

                else:
                    os.makedirs(config_folder)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder,params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_closed.txt")



            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/closed_fragger.params")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        updated_lines.append(f"database_name = {selected_db_path}")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)
                return
                

            #Antes de ejecutar chequear los archivos
            self.check_files()



            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                folder_project=os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path)
                os.makedirs(folder_project)

            else:
                log_folder=os.path.join(project_folder, "logs")
                clopen_folder=os.path.join(project_folder, ".clopen")
                folder_log_path = os.path.join(log_folder, folder_name)
                clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                os.makedirs(folder_log_path)
                os.makedirs(clopen_folder_log_path)


            #Escribir los logs
            log_params_path = os.path.join(clopen_folder_log_path, params_name)
            log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_closed.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')





            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Iterar y ejecutar cada uno de los archivos
            '''
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))

                process = QProcess(self)

                arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]

                process.setProgram("java")
                process.setArguments(arguments)

                # Conectar señales para manejar la salida estándar y error
                process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))

                #### Mover los archivos salida de Fragger a la carpeta resultados ####
                process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                    
                # Iniciar el proceso
                process.start()
                # Esperar hasta que el proceso termine
                #process.waitForFinished(-1)
            '''

            #Iterar y ejecutar cada uno de los archivos
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_fragger(searchtype='Closed')



    def on_process_finished(self, exitCode, exitStatus, index, files_before, program_basename, mode, searchtype):

        self.active_processes -=1
        

        if exitCode == 0:

            # Obtener lista de archivos después de ejecutar fragger
            files_after = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
            
            # Identificar nuevos archivos generados
            new_files = files_after - files_before
            
            # Mover los nuevos archivos a la ubicación deseada
            self.move_output_files(os.path.dirname(self.file_list.item(index).text()), new_files, program_basename, index, searchtype)
            self.move_fastapepindex_files(os.path.join(os.getcwd(), "fastas"), program_basename)

        if mode=="Fragger":

            self.start_next_process_fragger(searchtype='Closed')

        if mode=="Comet":
            self.start_next_process_comet(searchtype='Closed')

    def move_output_files(self, output_directory, new_files, program_basename, index, searchtype):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Closed-"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Closed-"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)
        
        # Mover los archivos generados
        for filename in new_files:

            source_path = os.path.join(output_directory, filename)
            new_filename = f"{os.path.splitext(filename)[0]}_{searchtype}_Search_{index+1}{os.path.splitext(filename)[1]}"
            destination_path = os.path.join(folder_results_path, new_filename)
            
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)

    '''

    def move_output_files(self, output_directory, new_files, program_basename, index, searchtype):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Closed-"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Closed-"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)
        
        # Mover los archivos generados
        for filename in new_files:

            source_path = os.path.join(output_directory, filename)
            destination_path = os.path.join(folder_results_path, filename)
            
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)

    '''


    def move_fastapepindex_files(self, fasta_directory, program_basename):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Closed-"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Closed-"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)

        # Obtener la lista de archivos ".pepindex" en el directorio fuente
        pepindex_files = glob.glob(os.path.join(fasta_directory, "*.pepindex"))

        # Mover cada archivo encontrado al directorio de destino
        for file_path in pepindex_files:

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(folder_results_path, file_name)
            shutil.move(file_path, destination_path)



    def log_to_console(self, message):

        self.console_output.append(message)



    def handle_stdout(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stdout = codec.toUnicode(process.readAllStandardOutput())
        #stdout = process.readAllStandardOutput().data().decode("utf-8")
        self.log_to_console(stdout)
        stdout_file = os.path.join(folder, f"stdout.log")
        with open(stdout_file, 'a') as f:
            f.write(stdout)

    def handle_stderr(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stderr = codec.toUnicode(process.readAllStandardError())
        #stderr = process.readAllStandardError().data().decode("utf-8")
        self.log_to_console(stderr)
        stderr_file = os.path.join(folder, f"stderr.log")
        with open(stderr_file, 'a') as f:
            f.write(stderr)


    def show_help(self, help_text):

        help_window = HelpWindow(help_text)
        help_window.exec_()


    def read_help_text(self):

        help_path=os.path.join(os.getcwd(), "Config/Help.txt")
        
        with open(help_path, "r") as file:
            help_text = file.read()

        return help_text

    def select_files(self):

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()

            for file_path in file_paths:
                item = QListWidgetItem(file_path)
                self.file_list.addItem(item)

    def check_files(self):

        raw_files = []
        no_raw_files=[]

        for index in range(self.file_list.count()):
            file_path = self.file_list.item(index).text()

            if file_path.lower().endswith('.raw') or file_path.lower().endswith('.mzML'):
                raw_files.append(file_path)

            else:
                no_raw_files.append(file_path)
        
        if raw_files and not no_raw_files:
            msg = "All files are .raw or .mzML type files."
            QMessageBox.information(self, "Raw Files Checked", msg)

        elif no_raw_files and not raw_files:
            msg = "Not all files are .raw or .mzML. Do you want to continue?\nThis files are neither .raw nor .mzML:\n"+"\n".join(no_raw_files)
            QMessageBox.warning(self, "Issue find in the files selected", msg)

        else:
            msg = "No raw or mzML file selected"
            QMessageBox.warning(self, "No selection", msg)
        

    def delete_file(self):

        selected_items = self.file_list.selectedItems()

        if selected_items:
            for item in selected_items:
                self.file_list.takeItem(self.file_list.row(item))

    def load_configuration(self):

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'r') as file:
                config_text = file.read()
                self.config_text.setPlainText(config_text)

    def save_configuration(self):

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix('txt')

        if file_dialog.exec_():

            file_path = file_dialog.selectedFiles()[0]
            config_text = self.config_text.toPlainText()

            with open(file_path, 'w') as file:
                file.write(config_text)

    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_Delete:
            self.delete_file()






#########################
###   Open Search   ####
#########################

class OpenSearch(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()
        self.max_simultaneous_processes = 1  # Define el número máximo de procesos simultáneos
        self.active_processes = 0
        self.process_queue = []

    def init_ui(self):

        self.setWindowTitle('Cl-Open: Only Open Mode Search')
        self.setGeometry(300, 300, 800, 800)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Layout a la izquierda (file_layout)
        self.file_layout = QVBoxLayout()

        # Boton para seleccionar archivos
        self.select_file_button = QPushButton()
        self.select_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/Folder.png")))
        self.select_file_button.setIconSize(QSize(30, 30))
        self.select_file_button.setFixedSize(30, 30)
        
        self.select_file_button.clicked.connect(self.select_files)
        self.select_file_button.setToolTip("Select File")
        self.select_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.select_file_button)

        # Boton para chequear archivos
        self.check_file_button = QPushButton()
        self.check_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/CheckRaws.png")))
        self.check_file_button.setIconSize(QSize(30, 30))
        self.check_file_button.setFixedSize(30, 30)
        
        self.check_file_button.clicked.connect(self.check_files)
        self.check_file_button.setToolTip("Check Files")
        self.check_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.check_file_button)

        # Boton de RUN
        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/RunIm.jpg")))
        self.run_button.setIconSize(QSize(30, 30))
        self.run_button.setFixedSize(30, 30)
        
        self.run_button.clicked.connect(self.run_Close)
        self.run_button.setToolTip("Run Close Search")
        self.run_button.setToolTipDuration(10000)
        

        # Layout horizontal para los botones
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.select_file_button)
        self.button_layout.addWidget(self.check_file_button)
        self.button_layout.addStretch() 
        self.file_layout.addLayout(self.button_layout)

        self.button_layout.addWidget(self.run_button)


        # Title Raws
        self.raw_title = QLabel("Mass Spectometry Raw Files Selected")
        self.raw_title.setAlignment(Qt.AlignCenter)
        self.raw_title.setStyleSheet("font-weight: bold;")
        self.file_layout.addWidget(self.raw_title)


        # Lista de archivos seleccionados
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection) # Permite seleccion multiple con control y shift
        self.file_layout.addWidget(self.file_list)

        # Botón para eliminar archivos seleccionados
        #self.delete_file_button = QPushButton('Remove')
        #self.delete_file_button.clicked.connect(self.delete_file)
        #self.file_layout.addWidget(self.delete_file_button)

        # Widget para contener el layout de archivos
        file_widget = QWidget()
        file_widget.setLayout(self.file_layout)

        # Layout central (config_layout)
        self.config_layout = QVBoxLayout()

        # Title Select Platform
        self.mode_title = QLabel("Select Search Engine")
        self.mode_title.setAlignment(Qt.AlignLeft)
        self.mode_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.mode_title)

        # Modes Search layaout
        '''
        self.comet_button= QPushButton()
        self.comet_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/CometIm.png")))
        self.comet_button.setObjectName("comet_button")
        self.comet_button.setIconSize(QSize(50, 50))
        self.comet_button.setFixedSize(50, 50)
        self.comet_button.setCheckable(True)  # Hacer el boton alternable
        self.comet_button.clicked.connect(self.on_button_clicked)
        self.comet_button.setToolTip("Comet Mode")
        self.comet_button.setToolTipDuration(10000)
        '''

        self.fragger_button=QPushButton()
        self.fragger_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/FraggerIm.png")))
        self.fragger_button.setObjectName("fragger_button")
        self.fragger_button.setIconSize(QSize(50, 50))
        self.fragger_button.setFixedSize(50, 50)
        self.fragger_button.setCheckable(True)  # Hacer el boton alternable
        self.fragger_button.clicked.connect(self.on_button_clicked)
        self.fragger_button.setToolTip("MSFragger Mode")
        self.fragger_button.setToolTipDuration(10000)

        # Layout horizontal para los modos
        self.modes_layout = QHBoxLayout()
        #self.modes_layout.addWidget(self.comet_button)
        self.modes_layout.addWidget(self.fragger_button)
        self.modes_layout.addStretch() 
        self.config_layout.addLayout(self.modes_layout)

        # Inicializar el QButtonGroup para manejar la exclusividad de los botones
        self.button_group = QButtonGroup()
        #self.button_group.addButton(self.comet_button)
        self.button_group.addButton(self.fragger_button)

        ###########



        # Title Config Params
        self.params_title = QLabel("Configuration Params of Selected Search Engine")
        self.params_title.setAlignment(Qt.AlignLeft)
        self.params_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.params_title)

        # Boton para cargar archivo de configuración
        self.load_config_button = QPushButton()
        self.load_config_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/loadIco.png")))
        self.load_config_button.setObjectName("load_config_button")
        self.load_config_button.setIconSize(QSize(30, 30))
        self.load_config_button.setFixedSize(30, 30)
        self.load_config_button.clicked.connect(self.load_configuration)
        self.load_config_button.setToolTip("Load Configuration")
        self.load_config_button.setToolTipDuration(10000)
        self.modes_layout.addWidget(self.load_config_button)

        # Boton para guardar la configuración
        self.save_config_button = QPushButton()
        self.save_config_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/SaveIco.png")))
        self.save_config_button.setObjectName("save_config_button")
        self.save_config_button.setIconSize(QSize(30, 30))
        self.save_config_button.setFixedSize(30, 30)
        self.save_config_button.clicked.connect(self.save_configuration)
        self.save_config_button.setToolTip("Save Configuration")
        self.save_config_button.setToolTipDuration(10000)
        self.modes_layout.addWidget(self.save_config_button)

        # Área de texto para editar el archivo de configuración
        self.config_text = QTextEdit()
        self.config_layout.addWidget(self.config_text)

        # Widget para contener el layout de configuración
        config_widget = QWidget()
        config_widget.setLayout(self.config_layout)

        # Layout a la derecha (console_layout)
        self.console_layout = QVBoxLayout()

        # Título de la consola
        self.console_title = QLabel('STATUS INFORMATION')
        font = QFont()
        font.setBold(True)
        self.console_title.setFont(font)
        self.console_layout.addWidget(self.console_title)

        # Consola de salida
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_layout.addWidget(self.console_output)


        # Widget para contener el layout de consola
        console_widget = QWidget()
        console_widget.setLayout(self.console_layout)

        # Añadir widgets al main_layout usando splitters
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC; /* Color del manejador */
                border: 1px dotted #707070; /* Borde punteado */
                width: 1px; /* Ancho del manejador */
            }
        """)
        splitter1.addWidget(file_widget)
        splitter1.addWidget(config_widget)
        splitter1.addWidget(console_widget)

        # Ajuste del tamaño inicial de los widgets en el QSplitter
        splitter1.setSizes([200, 400, 200])

        self.main_layout.addWidget(splitter1)

        


        # Crear la barra de herramientas
        toolbar = QToolBar("Toolbar")
        # Aplicar estilo personalizado a la barra de herramientas
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #444;
                border: 2px solid #555;
                padding: 0px;
                spacing: 5px;
            }
            QToolButton {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #555;
                border: 1px solid #888;
            }
        """)
        self.addToolBar(toolbar)


        #Crear un main para que se pueda volver al inicio
        main_action=QAction("Home", self)
        main_action.triggered.connect(self.go_to_main_window)
        toolbar.addAction(main_action)

        #Crear un mantein fasta para que se pueda almacenar los fastas
        inport_menu = QMenu("Inport", self)
        inport_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        fasta_action=QAction("Fasta", self)
        fasta_action.triggered.connect(self.mantein_fasta)
        inport_menu.addAction(fasta_action)

        toolbar.addAction(inport_menu.menuAction())


        # Crear accion de ayuda
        help_action = QAction("Help", self)
        help_text = self.read_help_text()
        help_action.triggered.connect(lambda: self.show_help(help_text))
        # Agregar acción a la barra de herramientas
        toolbar.addAction(help_action)


        ################
        ### Load log ###
        ################

        if project_folder:

            config_log_path=os.path.join(project_folder, ".clopen")

            #Obtener los logs y ordenarlos por fechas
            subdirs = [d for d in os.listdir(config_log_path) if os.path.isdir(os.path.join(config_log_path, d))]
            subdirs.sort(reverse=True)

            if subdirs:
                config_log=os.path.join(config_log_path, subdirs[0])
                config_file = glob.glob(os.path.join(config_log, "config_params_Open*"))
                raw_file=glob.glob(os.path.join(config_log, "raw_files_open*"))
                

                if config_file:

                    with open(config_file[0], 'r') as file:
                        config_text = file.read()
                        self.config_text.setPlainText(config_text)

                        # Desconectar señales
                        self.comet_button.clicked.disconnect(self.on_button_clicked)
                        self.fragger_button.clicked.disconnect(self.on_button_clicked)

                        # Seleccionar el boton sin ejecutar la función

                        if "comet" in config_file[0].lower():
                            self.comet_button.setChecked(True)

                        elif "fragger" in config_file[0].lower():
                            self.fragger_button.setChecked(True)

                        # Volver a conectar señales
                        self.comet_button.clicked.connect(self.on_button_clicked)
                        self.fragger_button.clicked.connect(self.on_button_clicked)


                else:
                    msg = "It cannot loaded the config params log."
                    QMessageBox.warning(self, "Configuration log file not found", msg)


                if raw_file:

                    with open(raw_file[0], 'r') as file:
                        lines=file.readlines()
                        self.file_list.clear()

                        for line in lines:
                            item = QListWidgetItem(line.strip())
                            self.file_list.addItem(item)

                else:
                    msg = "It cannot loaded the raws list log."
                    QMessageBox.warning(self, "Raws list log file not found", msg)



            else:
                msg = "It cannot loaded the log folder."
                QMessageBox.warning(self, "Log folder not found", msg)


        self.show()


    def on_process_finished(self, exitCode, exitStatus, index, files_before, program_basename, mode, searchtype):

        self.active_processes -=1
        

        if exitCode == 0:

            # Obtener lista de archivos después de ejecutar fragger
            files_after = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
            
            # Identificar nuevos archivos generados
            new_files = files_after - files_before
            
            # Mover los nuevos archivos a la ubicación deseada
            self.move_output_files(os.path.dirname(self.file_list.item(index).text()), new_files, program_basename, index, searchtype)
            self.move_fastapepindex_files(os.path.join(os.getcwd(), "fastas"), program_basename)

        if mode=="Fragger":

            self.start_next_process_fragger()

        if mode=="Comet":
            self.start_next_process_comet()



    def move_output_files(self, output_directory, new_files, program_basename):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Open-"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Open-"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)
        
        # Mover los archivos generados
        for filename in new_files:

            source_path = os.path.join(output_directory, filename)
            destination_path = os.path.join(folder_results_path, filename)
            
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)


    def move_fastapepindex_files(self, fasta_directory, program_basename):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Open-"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Open-"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)

        # Obtener la lista de archivos ".pepindex" en el directorio fuente
        pepindex_files = glob.glob(os.path.join(fasta_directory, "*.pepindex"))

        # Mover cada archivo encontrado al directorio de destino
        for file_path in pepindex_files:

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(folder_results_path, file_name)
            shutil.move(file_path, destination_path)



    def mantein_fasta(self):

        self.fasta_window = Fasta()
        self.fasta_window.show()


    def go_to_main_window(self):

        self.hide()

        self.main_window=ClOpenSearch()
        self.main_window.show()


    def on_button_clicked(self):

        button = self.sender()

        if button.isChecked():

            self.button_group.setExclusive(True)
            self.button_group.setId(button, 1)

            button_name=button.objectName()

            if button_name=="comet_button":
                config_comet=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(config_comet, 'r') as file:
                    config_text = file.read()
                    self.config_text.setPlainText(config_text)

            if button_name=="fragger_button":

                config_fragger=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/open_fragger.params")

                with open(config_fragger, 'r') as file:
                    config_text = file.read()
                    self.config_text.setPlainText(config_text)


        else:
            self.button_group.setId(button, 0)



    def run_Close(self):

        checked_button=self.button_group.checkedButton()

        if checked_button is not None:

            button_name=checked_button.objectName()

        else:
            QMessageBox.critical(self, "No Search Engine Selected", "No Search Engine Selected")
            pass



        #### COMET ####

        if button_name=="comet_button":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text.toPlainText().strip()
            params_name="config_params_Open_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_open.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Open-"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

                else:
                    os.makedirs(config_folder)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder,params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        print(selected_db_path)
                        updated_lines.append(f"database_name = {selected_db_path}\n")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)


            #Antes de ejecutar chequear los archivos
            self.check_files()

            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path)

            else:
                log_folder=os.path.join(project_folder, "logs")
                folder_log_path = os.path.join(log_folder, folder_name)
                os.makedirs(folder_log_path)


            #Escribir los logs
            log_params_path = os.path.join(folder_log_path, params_name)
            log_raw_file_path= os.path.join(folder_log_path, "raw_files_open.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')



            #Iterar y ejecutar cada uno de los archivos

            '''

            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))

                process = QProcess(self)

                arguments = ["-P" + params_path, self.file_list.item(index).text()]
                process.setProgram(script_path)
                process.setArguments(arguments)
                # Conectar señales para manejar la salida estándar y error
                process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
                process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                process.start()

            '''

            #Iterar y ejecutar cada uno de los archivos
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-P" + params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_comet(searchtype='Closed')


        ### MSFRAGGER ###

        if button_name=="fragger_button":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text.toPlainText().strip()
            params_name="config_params_Open_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_open.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Open-"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

                else:
                    os.makedirs(config_folder)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder,params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")


            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/open_fragger.params")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        print(selected_db_path)
                        updated_lines.append(f"database_name = {selected_db_path}\n")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)

            #Antes de ejecutar chequear los archivos
            self.check_files()



            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path)

            else:
                log_folder=os.path.join(project_folder, "logs")
                folder_log_path = os.path.join(log_folder, folder_name)
                os.makedirs(folder_log_path)


            #Escribir los logs
            log_params_path = os.path.join(folder_log_path, params_name)
            log_raw_file_path= os.path.join(folder_log_path, "raw_files_open.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')





            #Iterar y ejecutar cada uno de los archivos
            '''
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                process = QProcess(self)
                arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]
                process.setProgram("java")
                process.setArguments(arguments)
                # Conectar señales para manejar la salida estándar y error
                process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
                #### Mover los archivos salida de Fragger a la carpeta resultados ####
                process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                # Iniciar el proceso
                process.start()
                # Esperar hasta que el proceso termine
                #process.waitForFinished(-1)

            '''

            #Iterar y ejecutar cada uno de los archivos
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_fragger(searchtype='Open')


    def log_to_console(self, message):

        self.console_output.append(message)



    def handle_stdout(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stdout = codec.toUnicode(process.readAllStandardOutput())
        #stdout = process.readAllStandardOutput().data().decode("utf-8")
        self.log_to_console(stdout)
        stdout_file = os.path.join(folder, f"stdout.txt")
        with open(stdout_file, 'a') as f:
            f.write(stdout)

    def handle_stderr(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stderr = codec.toUnicode(process.readAllStandardError())
        #stderr = process.readAllStandardError().data().decode("utf-8")
        self.log_to_console(stderr)
        stderr_file = os.path.join(folder, f"stderr.txt")
        with open(stderr_file, 'a') as f:
            f.write(stderr)


    def show_help(self, help_text):

        help_window = HelpWindow(help_text)
        help_window.exec_()


    def read_help_text(self):

        help_path=os.path.join(os.getcwd(), "Config/Help.txt")
        
        with open(help_path, "r") as file:
            help_text = file.read()

        return help_text

    def select_files(self):

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()

            for file_path in file_paths:
                item = QListWidgetItem(file_path)
                self.file_list.addItem(item)

    def check_files(self):

        raw_files = []
        no_raw_files=[]

        for index in range(self.file_list.count()):
            file_path = self.file_list.item(index).text()

            if file_path.lower().endswith('.raw') or file_path.lower().endswith('.mzML'):
                raw_files.append(file_path)

            else:
                no_raw_files.append(file_path)
        
        if raw_files and not no_raw_files:
            msg = "All files are .raw or .mzML type files."
            QMessageBox.information(self, "Raw Files Checked", msg)

        elif no_raw_files and not raw_files:
            msg = "Not all files are .raw or .mzML. Do you want to continue?\nThis files are neither .raw nor .mzML:\n"+"\n".join(no_raw_files)
            QMessageBox.warning(self, "Issue find in the files selected", msg)

        else:
            msg = "No raw or mzML file selected"
            QMessageBox.warning(self, "No selection", msg)
        

    def delete_file(self):

        selected_items = self.file_list.selectedItems()

        if selected_items:
            for item in selected_items:
                self.file_list.takeItem(self.file_list.row(item))

    def load_configuration(self):

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            with open(file_path, 'r') as file:
                config_text = file.read()
                self.config_text.setPlainText(config_text)

    def save_configuration(self):

        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setDefaultSuffix('txt')

        if file_dialog.exec_():

            file_path = file_dialog.selectedFiles()[0]
            config_text = self.config_text.toPlainText()

            with open(file_path, 'w') as file:
                file.write(config_text)

    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_Delete:
            self.delete_file()







############################
###   Cl-Open Search   ####
############################


class CheckableMenu(QMenu):

    def __init__(self, parent=None):

        super(CheckableMenu, self).__init__(parent)
        self.aboutToHide.connect(self.update_button_text)
    
    def addCheckableAction(self, text):

        action = QWidgetAction(self)
        checkbox = QCheckBox(text)
        action.setDefaultWidget(checkbox)
        self.addAction(action)

        return checkbox
    
    def update_button_text(self):

        parent_button = self.parentWidget()

        if isinstance(parent_button, QToolButton):
            selected_options = [action.defaultWidget().text() for action in self.actions() if action.defaultWidget().isChecked()]

            if selected_options:
                parent_button.setText(', '.join(selected_options))

            else:
                parent_button.setText('Select Options')

class CheckBoxWidget(QWidget):

    def __init__(self, parent=None):

        super().__init__(parent)
        
        self.checkbox = QCheckBox(self)
        layout = QHBoxLayout()
        layout.addWidget(self.checkbox)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)


class ClOpenMode(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init_ui()
        self.max_simultaneous_processes = 1  # Define el número máximo de procesos simultáneos
        self.active_processes = 0
        self.process_queue = []

    def init_ui(self):

        self.setWindowTitle('Cl-Open: Cl-Open Mode Search')
        self.setGeometry(300, 300, 800, 800)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Layout a la izquierda (file_layout)
        self.file_layout = QVBoxLayout()

        # Boton para seleccionar archivos
        self.select_file_button = QPushButton()
        self.select_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/Folder.png")))
        self.select_file_button.setIconSize(QSize(30, 30))
        self.select_file_button.setFixedSize(30, 30)
        
        self.select_file_button.clicked.connect(self.select_files)
        self.select_file_button.setToolTip("Select File")
        self.select_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.select_file_button)

        # Boton para chequear archivos
        self.check_file_button = QPushButton()
        self.check_file_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/CheckRaws.png")))
        self.check_file_button.setIconSize(QSize(30, 30))
        self.check_file_button.setFixedSize(30, 30)
        
        self.check_file_button.clicked.connect(self.check_files)
        self.check_file_button.setToolTip("Check Files")
        self.check_file_button.setToolTipDuration(10000)
        #self.file_layout.addWidget(self.check_file_button)

        # Boton de RUN
        self.run_button = QPushButton()
        self.run_button.setIcon(QIcon(os.path.join(os.getcwd(), "config/RunIm.jpg")))
        self.run_button.setIconSize(QSize(30, 30))
        self.run_button.setFixedSize(30, 30)
        
        self.run_button.clicked.connect(self.run)
        self.run_button.setToolTip("Run Cl-Open Search")
        self.run_button.setToolTipDuration(10000)
        

        # Layout horizontal para los botones
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.select_file_button)
        self.button_layout.addWidget(self.check_file_button)
        self.button_layout.addStretch() 
        self.file_layout.addLayout(self.button_layout)

        self.button_layout.addWidget(self.run_button)


        # Title Raws
        self.raw_title = QLabel("Mass Spectometry Raw Files Selected")
        self.raw_title.setAlignment(Qt.AlignCenter)
        self.raw_title.setStyleSheet("font-weight: bold;")
        self.file_layout.addWidget(self.raw_title)


        # Lista de archivos seleccionados
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.ExtendedSelection) # Permite seleccion multiple con control y shift
        self.file_layout.addWidget(self.file_list)

        # Title CloseMods
        self.raw_title = QLabel("Modifications to considere in Close Search")
        self.raw_title.setAlignment(Qt.AlignCenter)
        self.raw_title.setStyleSheet("font-weight: bold;")
        self.file_layout.addWidget(self.raw_title)

        #Table to select modifications
        self.tableWidget = QTableWidget()
        #self.tableWidget.setRowCount(1)  # Iniciar con una fila
        self.tableWidget.setColumnCount(4)  # Solo 3 columnas
        self.tableWidget.setHorizontalHeaderLabels(['Search Number', 'Modification', 'Position', 'Variable Modification'])
        self.tableWidget.setSelectionBehavior(QTableWidget.SelectItems)

        # Ajustar ancho de columnas
        self.tableWidget.setColumnWidth(0, 100)  # Ajustar ancho de la primera columna
        self.tableWidget.setColumnWidth(1, 150) 
        self.tableWidget.setColumnWidth(2, 100)
        self.tableWidget.setColumnWidth(3, 150)

        self.file_layout.addWidget(self.tableWidget)

        self.addRowButton = QPushButton("+")
        self.addRowButton.clicked.connect(self.addRow)
        self.addRowButton.setFixedSize(30, 30)
        self.file_layout.addWidget(self.addRowButton, alignment=Qt.AlignRight)

        # Tick box para indicar si queremos unir archivos
        self.checkbox_fusionfiles = QCheckBox("Fusion Search Files")
        self.checkbox_fusionfiles.stateChanged.connect(self.update_widget_states)
        self.file_layout.addWidget(self.checkbox_fusionfiles)

        # Compatibility Selection
        self.compatibility_selection_button = QComboBox()
        compatibilities_names=['Select compatibility output', 'Comet', 'MSFragger', 'PTM Workflow']
        self.compatibility_selection_button.addItems(compatibilities_names)
        self.compatibility_selection_button.setEnabled(False)  # Initially disabled
        self.compatibility_selection_button.currentIndexChanged.connect(self.update_widget_states)
        self.file_layout.addWidget(self.compatibility_selection_button)

        # Tick box para indicar si queremos unir archivos
        self.checkbox_ptmwf = QCheckBox("Apply PTM Workflow")
        self.checkbox_ptmwf.setEnabled(False)  # Initially disabled
        self.file_layout.addWidget(self.checkbox_ptmwf)

        # Inicializar la primera fila con widgets personalizados
        self.addRow()

        # Menu contextual
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)


        ###########################


        # Widget para contener el layout de archivos
        file_widget = QWidget()
        file_widget.setLayout(self.file_layout)

        # Layout central (config_layout)
        self.config_layout = QVBoxLayout()


        # Title Fasta
        self.fasta_title = QLabel("Select Fasta")
        self.fasta_title.setAlignment(Qt.AlignLeft)
        self.fasta_title.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.fasta_title)

        # Fasta Selection
        self.fasta_selection_button = QComboBox()
        fasta_names=self.load_fasta()
        self.fasta_selection_button.addItems(fasta_names)
        self.config_layout.addWidget(self.fasta_selection_button)

        ###########


        # Title Select Platform
        self.mode_title_close = QLabel("Select Close Search Engine")
        self.mode_title_close.setAlignment(Qt.AlignLeft)
        self.mode_title_close.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.mode_title_close)

        # Modes Search layaout
        self.comet_button_close= QPushButton()
        self.comet_button_close.setIcon(QIcon(os.path.join(os.getcwd(), "config/CometIm.png")))
        self.comet_button_close.setObjectName("comet_button_close")
        self.comet_button_close.setIconSize(QSize(50, 50))
        self.comet_button_close.setFixedSize(50, 50)
        self.comet_button_close.setCheckable(True)  # Hacer el boton alternable
        self.comet_button_close.clicked.connect(self.on_button_clicked)
        self.comet_button_close.setToolTip("Comet Mode")
        self.comet_button_close.setToolTipDuration(10000)

        self.fragger_button_close=QPushButton()
        self.fragger_button_close.setIcon(QIcon(os.path.join(os.getcwd(), "config/FraggerIm.png")))
        self.fragger_button_close.setObjectName("fragger_button_close")
        self.fragger_button_close.setIconSize(QSize(50, 50))
        self.fragger_button_close.setFixedSize(50, 50)
        self.fragger_button_close.setCheckable(True)  # Hacer el boton alternable
        self.fragger_button_close.clicked.connect(self.on_button_clicked)
        self.fragger_button_close.setToolTip("MSFragger Mode")
        self.fragger_button_close.setToolTipDuration(10000)

        # Layout horizontal para los modos
        self.modes_layout_close = QHBoxLayout()
        self.modes_layout_close.addWidget(self.comet_button_close)
        self.modes_layout_close.addWidget(self.fragger_button_close)
        self.modes_layout_close.addStretch() 
        self.config_layout.addLayout(self.modes_layout_close)

        # Inicializar el QButtonGroup para manejar la exclusividad de los botones
        self.button_group_close = QButtonGroup()
        self.button_group_close.addButton(self.comet_button_close)
        self.button_group_close.addButton(self.fragger_button_close)

        ####



        # Title Config Params
        self.params_title_close = QLabel("Configuration Params of Selected Close Search Engine")
        self.params_title_close.setAlignment(Qt.AlignLeft)
        self.params_title_close.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.params_title_close)

        # Boton para cargar archivo de configuración
        self.load_config_button_close = QPushButton()
        self.load_config_button_close.setIcon(QIcon(os.path.join(os.getcwd(), "config/loadIco.png")))
        self.load_config_button_close.setObjectName("load_config_button_close")
        self.load_config_button_close.setIconSize(QSize(30, 30))
        self.load_config_button_close.setFixedSize(30, 30)
        self.load_config_button_close.clicked.connect(self.load_configuration)
        self.load_config_button_close.setToolTip("Load Configuration")
        self.load_config_button_close.setToolTipDuration(10000)
        self.modes_layout_close.addWidget(self.load_config_button_close)

        # Boton para guardar la configuración
        self.save_config_button_close = QPushButton()
        self.save_config_button_close.setIcon(QIcon(os.path.join(os.getcwd(), "config/SaveIco.png")))
        self.save_config_button_close.setObjectName("save_config_button_close")
        self.save_config_button_close.setIconSize(QSize(30, 30))
        self.save_config_button_close.setFixedSize(30, 30)
        self.save_config_button_close.clicked.connect(self.save_configuration)
        self.save_config_button_close.setToolTip("Save Configuration")
        self.save_config_button_close.setToolTipDuration(10000)
        self.modes_layout_close.addWidget(self.save_config_button_close)

        # Área de texto para editar el archivo de configuración
        self.config_text_close = QTextEdit()
        self.config_layout.addWidget(self.config_text_close)

        # Widget para contener el layout de configuración
        #config_widget = QWidget()
        #config_widget.setLayout(self.config_layout)

        ###############




        # Title Select Platform
        self.mode_title_op = QLabel("Select Open Search Engine")
        self.mode_title_op.setAlignment(Qt.AlignLeft)
        self.mode_title_op.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.mode_title_op)

        # Modes Search layaout
        #self.comet_button_op= QPushButton()
        #self.comet_button_op.setIcon(QIcon(os.path.join(os.getcwd(), "config/CometIm.png")))
        #self.comet_button_op.setObjectName("comet_button_op")
        #self.comet_button_op.setIconSize(QSize(50, 50))
        #self.comet_button_op.setFixedSize(50, 50)
        #self.comet_button_op.setCheckable(True)  # Hacer el boton alternable
        #self.comet_button_op.clicked.connect(self.on_button_clicked)
        #self.comet_button_op.setToolTip("Comet Mode")
        #self.comet_button_op.setToolTipDuration(10000)

        self.fragger_button_op=QPushButton()
        self.fragger_button_op.setIcon(QIcon(os.path.join(os.getcwd(), "config/FraggerIm.png")))
        self.fragger_button_op.setObjectName("fragger_button_op")
        self.fragger_button_op.setIconSize(QSize(50, 50))
        self.fragger_button_op.setFixedSize(50, 50)
        self.fragger_button_op.setCheckable(True)  # Hacer el boton alternable
        self.fragger_button_op.clicked.connect(self.on_button_clicked)
        self.fragger_button_op.setToolTip("MSFragger Mode")
        self.fragger_button_op.setToolTipDuration(10000)

        # Layout horizontal para los modos
        self.modes_layout_op = QHBoxLayout()
        #self.modes_layout_op.addWidget(self.comet_button_op)
        self.modes_layout_op.addWidget(self.fragger_button_op)
        self.modes_layout_op.addStretch() 
        self.config_layout.addLayout(self.modes_layout_op)

        # Inicializar el QButtonGroup para manejar la exclusividad de los botones
        self.button_group_op = QButtonGroup()
        #self.button_group_op.addButton(self.comet_button_op)
        self.button_group_op.addButton(self.fragger_button_op)

        ####



        # Title Config Params
        self.params_title_op = QLabel("Configuration Params of Selected Open Search Engine")
        self.params_title_op.setAlignment(Qt.AlignLeft)
        self.params_title_op.setStyleSheet("font-weight: bold;")
        self.config_layout.addWidget(self.params_title_op)

        # Boton para cargar archivo de configuración
        self.load_config_button_op = QPushButton()
        self.load_config_button_op.setIcon(QIcon(os.path.join(os.getcwd(), "config/loadIco.png")))
        self.load_config_button_op.setObjectName("load_config_button_op")
        self.load_config_button_op.setIconSize(QSize(30, 30))
        self.load_config_button_op.setFixedSize(30, 30)
        self.load_config_button_op.clicked.connect(self.load_configuration)
        self.load_config_button_op.setToolTip("Load Configuration")
        self.load_config_button_op.setToolTipDuration(10000)
        self.modes_layout_op.addWidget(self.load_config_button_op)

        # Boton para guardar la configuración
        self.save_config_button_op = QPushButton()
        self.save_config_button_op.setIcon(QIcon(os.path.join(os.getcwd(), "config/SaveIco.png")))
        self.save_config_button_op.setObjectName("save_config_button_op")
        self.save_config_button_op.setIconSize(QSize(30, 30))
        self.save_config_button_op.setFixedSize(30, 30)
        self.save_config_button_op.clicked.connect(self.save_configuration)
        self.save_config_button_op.setToolTip("Save Configuration")
        self.save_config_button_op.setToolTipDuration(10000)
        self.modes_layout_op.addWidget(self.save_config_button_op)

        # Área de texto para editar el archivo de configuración
        self.config_text_op = QTextEdit()
        self.config_layout.addWidget(self.config_text_op)

        # Widget para contener el layout de configuración
        config_widget = QWidget()
        config_widget.setLayout(self.config_layout)

        ###############3






        # Layout a la derecha (console_layout)
        self.console_layout = QVBoxLayout()

        # Título de la consola
        self.console_title = QLabel('STATUS INFORMATION')
        font = QFont()
        font.setBold(True)
        self.console_title.setFont(font)
        self.console_layout.addWidget(self.console_title)

        # Consola de salida
        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_layout.addWidget(self.console_output)


        # Widget para contener el layout de consola
        console_widget = QWidget()
        console_widget.setLayout(self.console_layout)

        # Añadir widgets al main_layout usando splitters
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.setStyleSheet("""
            QSplitter::handle {
                background-color: #CCCCCC; /* Color del manejador */
                border: 1px dotted #707070; /* Borde punteado */
                width: 1px; /* Ancho del manejador */
            }
        """)
        splitter1.addWidget(file_widget)
        splitter1.addWidget(config_widget)
        splitter1.addWidget(console_widget)

        # Ajuste del tamaño inicial de los widgets en el QSplitter
        splitter1.setSizes([200, 400, 200])

        self.main_layout.addWidget(splitter1)




        # Crear la barra de herramientas
        toolbar = QToolBar("Toolbar")
        # Aplicar estilo personalizado a la barra de herramientas
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #444;
                border: 2px solid #555;
                padding: 0px;
                spacing: 5px;
            }
            QToolButton {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #555;
                border: 1px solid #888;
            }
        """)
        self.addToolBar(toolbar)


        #Crear un main para que se pueda volver al inicio
        main_action=QAction("Home", self)
        main_action.triggered.connect(self.go_to_main_window)
        toolbar.addAction(main_action)

        #Crear un mantein fasta para que se pueda almacenar los fastas
        inport_menu = QMenu("Inport", self)
        inport_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        fasta_action=QAction("Fasta", self)
        fasta_action.triggered.connect(self.mantein_fasta)
        inport_menu.addAction(fasta_action)

        toolbar.addAction(inport_menu.menuAction())


        # Crear accion de ayuda
        help_action = QAction("Help", self)
        help_text = self.read_help_text()
        help_action.triggered.connect(lambda: self.show_help(help_text))
        # Agregar acción a la barra de herramientas
        toolbar.addAction(help_action)

        self.show()


    def update_widget_states(self):
        
        if self.checkbox_fusionfiles.isChecked():
            self.compatibility_selection_button.setEnabled(True)

        else:
            self.compatibility_selection_button.setEnabled(False)
            self.checkbox_ptmwf.setEnabled(False)

        if self.compatibility_selection_button.currentText() == 'PTM Workflow':
            self.checkbox_ptmwf.setEnabled(True)

        else:
            self.checkbox_ptmwf.setEnabled(False)


    def load_fasta (self):

        fastas_path = os.path.join(os.getcwd(), "fastas")

        if fastas_path:

            files = []
            for file_name in os.listdir(fastas_path):
                if os.path.isfile(os.path.join(fastas_path, file_name)):
                    files.append(file_name)

        files.insert(0,"")

        return files

    def showContextMenu(self, position: QPoint):

        context_menu = QMenu(self)

        add_action = QAction("Add Row", self)
        add_action.triggered.connect(self.addRow)
        context_menu.addAction(add_action)

        delete_action = QAction("Delete Row", self)
        delete_action.triggered.connect(self.deleteRow)
        context_menu.addAction(delete_action)

        copy_action = QAction("Coppy", self)
        copy_action.triggered.connect(self.copy)
        context_menu.addAction(copy_action)

        paste_action = QAction("Paste", self)
        paste_action.triggered.connect(self.paste)
        context_menu.addAction(paste_action)

        context_menu.exec_(self.tableWidget.mapToGlobal(position))


    def loadComboBoxItems(self):

        items = ['','N-tern','C-tern','A','C','D','E','F','G','H','I/L','K','M','N','P','Q','R','S','T','V','U','W','Y']

        for row in range(self.tableWidget.rowCount()):
            combo = QComboBox()
            combo.addItems(items)
            self.tableWidget.setCellWidget(row, 2, combo)

    def create_checkbox_widget(self,options, previous_selections=None):

        menu = CheckableMenu(self)
        checkboxes = []

        for option in options:
            checkbox = menu.addCheckableAction(option)
            checkboxes.append(checkbox)
        
        button = QToolButton()
        button.setText('Select Positions')
        button.setMenu(menu)
        button.setPopupMode(QToolButton.InstantPopup)
        
        if previous_selections:
            for checkbox, selected in zip(checkboxes, previous_selections):
                checkbox.setChecked(selected)

        def update_button_text():
            selected_options = [checkbox.text() for checkbox in checkboxes if checkbox.isChecked()]
            if selected_options:
                button.setText(', '.join(selected_options))
            else:
                button.setText('Select Positions')

        # Connect menu aboutToHide to update_button_text
        menu.aboutToHide.connect(update_button_text)
        
        return button, checkboxes


    def addRow(self):

        row_count = self.tableWidget.rowCount()
        self.tableWidget.insertRow(row_count)

        items = ['','Ntern_peptide','Ctern_peptide','Ntern_protein','Ctern_protein','A','C','D','E','F','G','H','I','L','K','M','N','P','Q','R','S','T','V','U','W','Y']
        mods = ['',
            'Acetyl (42.010565)', 
            'Amidated (-0.984016)', 
            'Carbamidomethyl (57.021464)', 
            'Carbamyl (43.005814)', 
            'Carboxymethyl (58.005479)', 
            'Deamidated (0.984016)', 
            'Phospho (79.966331)', 
            'Propionamide (71.037114)', 
            'Gln->pyro-Glu (-17.026549)', 
            'Methyl (14.01565)', 
            'Oxidation (15.994915)', 
            'Dimethyl (28.0313)', 
            'Trimethyl (42.04695)', 
            'Methylthio (45.987721)', 
            'Sulfo (79.956815)', 
            'Palmitoyl (238.229666)', 
            'Trioxidation (47.984744)', 
            'Nitro (44.985078)', 
            'ICAT-C (227.126991)', 
            'ICAT-C:13C(9) (236.157185)', 
            'Nethylmaleimide (125.047679)', 
            'GG (114.042927)', 
            'Formyl (27.994915)', 
            'Dimethyl:2H(6)13C(2) (36.07567)', 
            'Label:13C(6) (6.020129)', 
            'Label:18O(2) (4.008491)', 
            'Dimethyl:2H(4) (32.056407)', 
            'iTRAQ4plex (144.102063)', 
            'Label:18O(1) (2.004246)', 
            'Label:13C(6)15N(2) (8.014199)', 
            'Label:13C(6)15N(4) (10.008269)', 
            'Dioxidation (31.989829)', 
            'Label:2H(4) (4.025107)', 
            'iTRAQ8plex (304.20536)', 
            'TMT6plex (229.162932)', 
            'TMT2plex (225.155833)', 
            'Met-loss (-131.040485)', 
            'Met-loss+Acetyl (-89.02992)', 
            'NEM:2H(5) (130.079062)', 
            'iodoTMT6plex (329.226595)', 
            'TMTpro (304.207146)', 
            'TMTpro_zero (295.189592)', 
            'DSSO Tris (279.07766)', 
            'DSSO Hydrolyzed (176.01433)', 
            'DSSO Amidated (175.03031)', 
            'DSSO (158.00376)', 
            'DSS Tris (259.141973)', 
            'DSS Hydrolyzed (156.078644)', 
            'DSS Amidated (155.09463)', 
            'DSS (138.06808)', 
            'PhoX (209.97181)', 
            'PhoX Amidated (226.99836)', 
            'PhoX Hydrolyzed (227.98237)', 
            'PhoX Tris (331.0457)', 
            'DSBSO (308.03883)', 
            'DSBSO Amidated (325.06538)', 
            'DSBSO Hydrolyzed (326.04939)', 
            'DSBSO Tris (429.11272)', 
            'EDC (-18.01056)']

        for col in range(self.tableWidget.columnCount()):

            if col == 1:  # Si es la segunda columna

                combo = QComboBox()
                combo.addItems(mods)
                combo.setEditable(True)
                prev_combo = self.tableWidget.cellWidget(row_count - 1, col)  # Obtener el QComboBox de la fila anterior

                if prev_combo:  # Si hay un QComboBox en la fila anterior
                    pass
                    #combo.setCurrentText(prev_combo.currentText())  # Establecer el mismo valor seleccionado
                self.tableWidget.setCellWidget(row_count, col, combo)

            elif col == 2:  # Si es la tercera columna

                prev_widget = self.tableWidget.cellWidget(row_count - 1, col)  # Obtener el QComboBox de la fila anterior
                prev_selections = None

                if prev_widget:  # Si hay un QWidget en la fila anterior
                    prev_checkboxes = prev_widget.findChildren(QCheckBox)
                    prev_selections = [checkbox.isChecked() for checkbox in prev_checkboxes]

                checkbox_widget, checkboxes = self.create_checkbox_widget(items, prev_selections)

                self.tableWidget.setCellWidget(row_count, col, checkbox_widget)

            elif col == 3:
                checkbox_widget = CheckBoxWidget()
                self.tableWidget.setCellWidget(row_count, col, checkbox_widget)

            else:
                item = QTableWidgetItem('')
                self.tableWidget.setItem(row_count, col, item)


    def deleteRow(self):
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        for row in reversed(sorted(selected_rows)):
            self.tableWidget.removeRow(row.row())


    def copy(self):

        selection = self.tableWidget.selectedRanges()

        if selection:

            rows = sorted(set(index.row() for range in selection for index in range.topLeft().row() + range.rowCount()))
            columns = sorted(set(index.column() for range in selection for index in range.topLeft().column() + range.columnCount()))
            table = '\t'.join([self.tableWidget.horizontalHeaderItem(column).text() for column in columns]) + '\n'

            for row in rows:

                table += '\t'.join([self.tableWidget.item(row, column).text() for column in columns]) + '\n'

            clipboard = QApplication.clipboard()
            clipboard.setText(table)

    def paste(self):

        clipboard = QApplication.clipboard()
        data = clipboard.text().split('\n')
        rows = len(data)
        columns = len(data[0].split('\t'))

        currentRow = self.tableWidget.currentRow()
        currentColumn = self.tableWidget.currentColumn()

        for i, row in enumerate(data):
            if i + currentRow >= self.tableWidget.rowCount():
                self.tableWidget.insertRow(self.tableWidget.rowCount())
                self.loadComboBoxItems()  # Asegurar que se creen los ComboBox para la nueva fila

            cells = row.split('\t')
            for j, cell in enumerate(cells):
                if j + currentColumn >= self.tableWidget.columnCount():
                    self.tableWidget.insertColumn(self.tableWidget.columnCount())

                self.tableWidget.setItem(i + currentRow, j + currentColumn, QTableWidgetItem(cell))

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:

            currentRow = self.tableWidget.currentRow()
            currentColumn = self.tableWidget.currentColumn()
            item = self.tableWidget.item(currentRow, currentColumn)

            if item is not None:

                self.tableWidget.editItem(item)

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copy()

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            self.paste()

        else:

            super().keyPressEvent(event)

            if event.key() == Qt.Key_Left:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentColumn > 0:

                    self.tableWidget.setCurrentCell(currentRow, currentColumn - 1)

            elif event.key() == Qt.Key_Right:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentColumn < self.tableWidget.columnCount() - 1:

                    self.tableWidget.setCurrentCell(currentRow, currentColumn + 1)

            elif event.key() == Qt.Key_Up:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentRow > 0:

                    self.tableWidget.setCurrentCell(currentRow - 1, currentColumn)

            elif event.key() == Qt.Key_Down:

                currentRow = self.tableWidget.currentRow()
                currentColumn = self.tableWidget.currentColumn()

                if currentRow < self.tableWidget.rowCount() - 1:

                    self.tableWidget.setCurrentCell(currentRow + 1, currentColumn)

    def saveComboBoxIndices(self):

        self.savedComboBoxIndices = []

        for row in range(self.tableWidget.rowCount()):
            combo = self.tableWidget.cellWidget(row, 2)  # Obtener el QComboBox en la tercera columna
            if combo:
                index = combo.currentIndex()  # Obtener el índice seleccionado
                self.savedComboBoxIndices.append(index)  # Guardar el índice en la lista
            else:
                self.savedComboBoxIndices.append(-1)  # Si no hay QComboBox en la celda, guardar -1 en la lista

    def restoreComboBoxIndices(self):

        for row, index in enumerate(self.savedComboBoxIndices):

            combo = self.tableWidget.cellWidget(row, 2)  # Obtener el QComboBox en la tercera columna

            if combo and index != -1:
                combo.setCurrentIndex(index)  # Restaurar el índice seleccionado en el QComboBox

    def restoreTableItems(self, table):

        for row_num, row_data in enumerate(table):

            row_items = row_data.strip().split('\t')

            for col_num, data in enumerate(row_items):

                item = QTableWidgetItem(data)
                self.tableWidget.setItem(row_num, col_num, item)


    def on_button_clicked(self):

        button = self.sender()

        if button.isChecked():

            #button_group.setExclusive(True)
            #button_id = button_group.id(button)
            button_name = button.objectName()

            if button_name == "comet_button_close":
                config_comet = os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(config_comet, 'r') as file:
                    config_text = file.read()
                    self.config_text_close.setPlainText(config_text)

            elif button_name == "fragger_button_close":
                config_fragger = os.path.join(os.getcwd(), "softwares/MSFragger-4.1/closed_fragger.params")

                with open(config_fragger, 'r') as file:
                    config_text = file.read()
                    self.config_text_close.setPlainText(config_text)

            elif button_name == "comet_button_op":
                config_comet = os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(config_comet, 'r') as file:
                    config_text = file.read()
                    self.config_text_op.setPlainText(config_text)

            elif button_name == "fragger_button_op":
                config_fragger = os.path.join(os.getcwd(), "softwares/MSFragger-4.1/open_fragger.params")

                with open(config_fragger, 'r') as file:
                    config_text = file.read()
                    self.config_text_op.setPlainText(config_text)


        else:
            pass
            #self.button_group.setId(button, 0)


    def create_clopen_configurations (self):

        global project_folder

        if not project_folder:

            # Crear un archivo temporal para la tabla
            table_path = os.path.join(os.getcwd(), "mods_table_clopen.txt")

        else:
            config_folder=os.path.join(project_folder, "config/Cl-Open")

            if os.path.exists(config_folder):
                # Crear un archivo temporal para la tabla
                table_path = os.path.join(config_folder, "mods_table_clopen.txt")

            else:
                os.makedirs(config_folder)
                # Crear un archivo temporal para la tabla
                table_path = os.path.join(config_folder, "mods_table_clopen.txt")



        with open(table_path, 'w') as file:

            # Escribir los encabezados
            headers = [self.tableWidget.horizontalHeaderItem(i).text() for i in range(self.tableWidget.columnCount())]
            file.write('\t'.join(headers) + '\n')

            for row in range(self.tableWidget.rowCount()):
                row_data = []

                for col in range(self.tableWidget.columnCount()):
                    item = self.tableWidget.item(row, col)
                    widget = self.tableWidget.cellWidget(row, col)

                    if isinstance(widget, QToolButton):
                        # Si es un QToolButton, obtener el texto del botón
                        row_data.append(widget.text())

                    elif isinstance(widget, CheckBoxWidget):
                        # Si es un CheckBoxWidget, comprobar si el QCheckBox dentro de él está marcado o no
                        row_data.append('Yes' if widget.checkbox.isChecked() else 'No')

                    elif isinstance(widget, QComboBox):

                        if widget is not None:
                            row_data.append(widget.currentText())

                    elif item is not None:
                        # Si es un QTableWidgetItem, obtener el texto del item
                        row_data.append(item.text())

                    else:
                        # Si no hay widget ni item, añadir una cadena vacía
                        row_data.append('')

                # Escribir la fila en el archivo
                file.write('\t'.join(row_data) + '\n')

        return table_path


    def run(self):

        global project_folder

        checked_button_close=self.button_group_close.checkedButton()
        checked_button_op=self.button_group_op.checkedButton()

        if checked_button_close is not None:
            button_name_close=checked_button_close.objectName()

        else:
            QMessageBox.critical(self, "No Closed Search Engine Selected", "No Search Engine Selected")

        if checked_button_op is not None:
            button_name_op=checked_button_op.objectName()

        else:
            QMessageBox.critical(self, "No Open Search Engine Selected", "No Search Engine Selected")

        

        table_path=self.create_clopen_configurations()
        self.check_files()



        ###################################
        #### Different Search Detection ###
        ###################################


        # Crear los argumentos para el script

        args = []

        if os.path.getsize(table_path)==0:

            #### COMET ####

            if button_name_close=="comet_button_close":

                msg = "The modification for Close Serch table is empty.\nIt going to apply only one Closed Search with the modifications indicated in the configuration file"
                QMessageBox.warning(self, "Not fasta selected", msg)

                # Ejecutar el script

                script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]
                params= self.config_text.toPlainText().strip()
                params_name="base_config_params_Cl-Open_Closed_"+program_basename+".new"

                if not project_folder:

                    params_path = os.path.join(os.getcwd(), params_name)
                    raw_file_path= os.path.join(os.getcwd(), "raw_files_Cl-Open.txt")

                else:
                    config_folder=os.path.join(project_folder, "config/Cl-Open/Closed_"+program_basename)

                    if os.path.exists(config_folder):
                        # Crear un archivo temporal para la tabla
                        params_path = os.path.join(config_folder, params_name)
                        raw_file_path= os.path.join(config_folder, "raw_files_Cl-Open.txt")

                    else:
                        os.makedirs(config_folder)
                        # Crear un archivo temporal para la tabla
                        params_path = os.path.join(config_folder, params_name)
                        raw_file_path= os.path.join(config_folder, "raw_files_Cl-Open.txt")

                

                #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

                if not params:
                    msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                    QMessageBox.warning(self, "Not configuration selected", msg)

                    params_default=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                    with open(params_default, 'r') as file:
                        params=file.read()

                with open(params_path, 'w') as file:
                    file.write(params)

                lines=params.split('\n')

                #Cambiar la base de datos por la seleccionada

                if self.fasta_selection_button.currentText() !="":

                    selected_database = self.fasta_selection_button.currentText()
                    path_selected_db=os.path.join(os.getcwd(), "fastas")
                    selected_db_path=os.path.join(path_selected_db, selected_database)

                    updated_lines = []

                    for line in lines:

                        if line.strip().startswith("database_name"):
                            updated_lines.append(f"database_name = {selected_db_path}")
                        else:
                            updated_lines.append(line)

                    params='\n'.join(updated_lines) # Reescribimos los params

                    with open(params_path, 'w') as file:
                        file.write(params)
                
                else:
                    msg = "No fasta selected. Please select a fasta o import some"
                    QMessageBox.critical(self, "Not fasta selected", msg)
                    return

                #Guardar un log

                    # Obtener la fecha y hora actual
                now = datetime.now()
                    # Formatear la fecha y hora como una cadena sin caracteres especiales
                folder_name = now.strftime("%Y%m%d%H%M%S")

                if not project_folder:

                    folder_log_path = os.path.join(os.getcwd(), folder_name)
                    folder_project=os.path.join(os.getcwd(), folder_name)
                    os.makedirs(folder_log_path)
                    os.makedirs(folder_project)

                else:
                    log_folder=os.path.join(project_folder, "logs")
                    clopen_folder=os.path.join(project_folder, ".clopen")
                    folder_log_path = os.path.join(log_folder, folder_name)
                    clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                    os.makedirs(folder_log_path)
                    os.makedirs(clopen_folder_log_path)


                #Escribir los logs
                log_params_path = os.path.join(clopen_folder_log_path, params_name)
                log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_Cl-Open.txt")

                with open(log_params_path, 'w') as file:
                    file.write(params)

                #Guardar un txt de archivos en la carpeta de configuracion
                with open(log_raw_file_path, 'w') as archivo_txt:
                    for index in range(self.file_list.count()):
                        file=self.file_list.item(index).text()
                        archivo_txt.write(file + '\n')


                #Guardar un txt de archivos en la carpeta de configuracion
                with open(raw_file_path, 'w') as archivo_txt:
                    for index in range(self.file_list.count()):
                        file=self.file_list.item(index).text()
                        archivo_txt.write(file + '\n')


                #Iterar y ejecutar cada uno de los archivos

                for index in range (self.file_list.count()):

                    files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))

                    process = QProcess(self)

                    arguments = ["-P" + params_path, self.file_list.item(index).text()]
                    process.setProgram(script_path)
                    process.setArguments(arguments)
                    # Conectar señales para manejar la salida estándar y error
                    process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                    process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
                    process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                    process.start()



            ### MSFRAGGER ###

            if button_name_close=="fragger_button_close":

                # Ejecutar el script

                script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]
                params= self.config_text.toPlainText().strip()
                params_name="base_config_params_Cl-Open_Closed_"+program_basename+".new"

                if not project_folder:

                    params_path = os.path.join(os.getcwd(), params_name)
                    raw_file_path= os.path.join(os.getcwd(), "raw_files_Cl-Open.txt")

                else:
                    config_folder=os.path.join(project_folder, "config/Cl-Open/Closed_"+program_basename)

                    if os.path.exists(config_folder):
                        # Crear un archivo temporal para la tabla
                        params_path = os.path.join(config_folder, params_name)
                        raw_file_path= os.path.join(config_folder, "raw_files_Cl-Open.txt")

                    else:
                        os.makedirs(config_folder)
                        # Crear un archivo temporal para la tabla
                        params_path = os.path.join(config_folder,params_name)
                        raw_file_path= os.path.join(config_folder, "raw_files_Cl-Open.txt")



                #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

                if not params:
                    msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                    QMessageBox.warning(self, "Not configuration selected", msg)

                    params_default=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/closed_fragger.params")

                    with open(params_default, 'r') as file:
                        params=file.read()

                with open(params_path, 'w') as file:
                    file.write(params)

                lines=params.split('\n')

                #Cambiar la base de datos por la seleccionada

                if self.fasta_selection_button.currentText() !="":

                    selected_database = self.fasta_selection_button.currentText()
                    path_selected_db=os.path.join(os.getcwd(), "fastas")
                    selected_db_path=os.path.join(path_selected_db, selected_database)

                    updated_lines = []

                    for line in lines:

                        if line.strip().startswith("database_name"):
                            updated_lines.append(f"database_name = {selected_db_path}")
                        else:
                            updated_lines.append(line)

                    params='\n'.join(updated_lines) # Reescribimos los params

                    with open(params_path, 'w') as file:
                        file.write(params)
                
                else:
                    msg = "No fasta selected. Please select a fasta o import some"
                    QMessageBox.critical(self, "Not fasta selected", msg)
                    return

                #Guardar un log

                    # Obtener la fecha y hora actual
                now = datetime.now()
                    # Formatear la fecha y hora como una cadena sin caracteres especiales
                folder_name = now.strftime("%Y%m%d%H%M%S")

                if not project_folder:

                    folder_log_path = os.path.join(os.getcwd(), folder_name)
                    folder_project=os.path.join(os.getcwd(), folder_name)
                    os.makedirs(folder_log_path)
                    os.makedirs(folder_project)

                else:
                    log_folder=os.path.join(project_folder, "logs")
                    clopen_folder=os.path.join(project_folder, ".clopen")
                    folder_log_path = os.path.join(log_folder, folder_name)
                    clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                    os.makedirs(folder_log_path)
                    os.makedirs(clopen_folder_log_path)


                #Escribir los logs
                log_params_path = os.path.join(clopen_folder_log_path, params_name)
                log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_Cl-Open.txt")

                with open(log_params_path, 'w') as file:
                    file.write(params)

                #Guardar un txt de archivos en la carpeta de configuracion
                with open(log_raw_file_path, 'w') as archivo_txt:
                    for index in range(self.file_list.count()):
                        file=self.file_list.item(index).text()
                        archivo_txt.write(file + '\n')


                #Guardar un txt de archivos en la carpeta de configuracion
                with open(raw_file_path, 'w') as archivo_txt:
                    for index in range(self.file_list.count()):
                        file=self.file_list.item(index).text()
                        archivo_txt.write(file + '\n')


                #Iterar y ejecutar cada uno de los archivos
                for index in range (self.file_list.count()):

                    files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))

                    process = QProcess(self)

                    arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]

                    process.setProgram("java")
                    process.setArguments(arguments)

                    # Conectar señales para manejar la salida estándar y error
                    process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
                    process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))

                    #### Mover los archivos salida de Fragger a la carpeta resultados ####
                    process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename))
                        
                    # Iniciar el proceso
                    process.start()




        ### Si el usuario ha introducido valores en la tabla.
            ### Ejecutar el config creator para crear los distintos archivos de configuracion


        if os.path.getsize(table_path) >0:

            config_script_path=os.path.join(os.getcwd(), "config_clopen_creator.py")

            args.append('-l')
            args.append(table_path)
            args.append('-var')
            args.append('3')


            if button_name_close=="fragger_button_close":

                script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]


            if button_name_close=="comet_button_close":

                script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]


            if not project_folder:

                output_path = os.path.join(os.getcwd(), "config/Cl-Open/Closed_"+program_basename)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_Cl-Open.txt")

            else:
                output_path=os.path.join(project_folder, "config/Cl-Open/Closed_"+program_basename)

                if os.path.exists(output_path):
                    raw_file_path= os.path.join(output_path, "raw_files_Cl-Open.txt")

                else:
                    os.makedirs(output_path)
                    raw_file_path= os.path.join(output_path, "raw_files_Cl-Open.txt")

            args.append('-o')
            args.append(output_path)

            if button_name_close=="comet_button_close":

                script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]
                params= self.config_text_close.toPlainText().strip()
                params_name="config_params_Cl-Open_Closed_"+program_basename+".new"


                args.append('-e')
                args.append('Comet')

                if not project_folder:

                    params_path = os.path.join(os.getcwd(), params_name)
                    with open(params_path, 'w') as file:
                        file.write(params)

                    args.append('-cl')
                    args.append(params_path)

                else:
                    params_path = os.path.join(output_path, params_name)
                    with open(params_path, 'w') as file:
                        file.write(params)

                    args.append('-cl')
                    args.append(params_path)

            if button_name_close=="fragger_button_close":

                # Ejecutar el script

                script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]
                params= self.config_text_close.toPlainText().strip()
                params_name="config_params_Cl-Open_Closed_"+program_basename+".new"

                args.append('-e')
                args.append('Fragger')

                if not project_folder:

                    params_path = os.path.join(os.getcwd(), params_name)
                    with open(params_path, 'w') as file:
                        file.write(params)

                    args.append('-cl')
                    args.append(params_path)

                else:
                    params_path = os.path.join(output_path, params_name)
                    with open(params_path, 'w') as file:
                        file.write(params)

                    args.append('-cl')
                    args.append(params_path)



            #Cambiar la base de datos por la seleccionada

            lines=params.split('\n')

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        updated_lines.append(f"database_name = {selected_db_path}")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)
                return



            print(sys.executable)

            # Ejecutar el script
            process_config = QProcess(self)

            try:
                process_config.setProgram('python')
            except:
                try:
                    process_config.setProgram('python3')
                except:
                    try:
                        process_config.setProgram('py')
                    except:
                        print('\n\n###       PYTHON NOT FOUND      ###\n\nPlease check if python is installed')


                        #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                folder_project=os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path, exist_ok=True)
                os.makedirs(folder_project, exist_ok=True)

            else:
                log_folder=os.path.join(project_folder, "logs")
                clopen_folder=os.path.join(project_folder, ".clopen")
                folder_log_path = os.path.join(log_folder, folder_name)
                clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                os.makedirs(folder_log_path,exist_ok=True)
                os.makedirs(clopen_folder_log_path, exist_ok=True)


            #Escribir los logs
            log_params_path = os.path.join(clopen_folder_log_path, params_name)
            with open(log_params_path, 'w') as file:
                file.write(params)


            process_config.setArguments([config_script_path] + args)
            process_config.readyReadStandardOutput.connect(lambda: self.handle_stdout(process_config,folder_log_path))
            process_config.readyReadStandardError.connect(lambda: self.handle_stderr(process_config,folder_log_path))
            process_config.start()
            process_config.waitForFinished(-1)

            #############################
            ### SERIAL CLOSED SEARCH ####
            #############################

            #Recuperar todos los params que genera el config creator

            params_paths=[]

            for root, _, files in os.walk(output_path):
                for file in files:

                    if 'Cl-Open_Closed' in file:
                        full_path=os.path.join(root,file)
                        params_paths.append(full_path)


            #### COMET ####

            if button_name_close=="comet_button_close":


                # Ejecutar el script

                script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]

                for params_path in params_paths:

                    print(params_path)                    

                    #Guardar un log

                        # Obtener la fecha y hora actual
                    now = datetime.now()
                        # Formatear la fecha y hora como una cadena sin caracteres especiales
                    folder_name = now.strftime("%Y%m%d%H%M%S")

                    if not project_folder:

                        folder_log_path = os.path.join(os.getcwd(), folder_name)
                        folder_project=os.path.join(os.getcwd(), folder_name)
                        os.makedirs(folder_log_path,exist_ok=True)
                        os.makedirs(folder_project,exist_ok=True)

                    else:
                        log_folder=os.path.join(project_folder, "logs")
                        clopen_folder=os.path.join(project_folder, ".clopen")
                        folder_log_path = os.path.join(log_folder, folder_name)
                        clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                        os.makedirs(folder_log_path,exist_ok=True)
                        os.makedirs(clopen_folder_log_path, exist_ok=True)


                    #Escribir los logs
                    log_params_path = os.path.join(clopen_folder_log_path, params_name)
                    log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_Cl-Open.txt")

                    with open(log_params_path, 'w') as file:
                        file.write(params)

                    #Guardar un txt de archivos en la carpeta de configuracion
                    with open(log_raw_file_path, 'w') as archivo_txt:
                        for index in range(self.file_list.count()):
                            file=self.file_list.item(index).text()
                            archivo_txt.write(file + '\n')

                    #Guardar un txt de archivos en la carpeta de configuracion
                    with open(raw_file_path, 'w') as archivo_txt:
                        for index in range(self.file_list.count()):
                            file=self.file_list.item(index).text()
                            archivo_txt.write(file + '\n')


                    #Iterar y ejecutar cada uno de los archivos

                    for index in range (self.file_list.count()):

                        files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                        arguments = ["-P" + params_path, self.file_list.item(index).text()]
                        self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

                    self.start_next_process_comet(searchtype='Closed')




            ### MSFRAGGER ###

            if button_name_close=="fragger_button_close":

                # Ejecutar el script

                script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
                program_basename=os.path.splitext(os.path.basename(script_path))[0]

                for params_path in params_paths:                      

                    #Guardar un log

                        # Obtener la fecha y hora actual
                    now = datetime.now()
                        # Formatear la fecha y hora como una cadena sin caracteres especiales
                    folder_name = now.strftime("%Y%m%d%H%M%S")

                    if not project_folder:

                        folder_log_path = os.path.join(os.getcwd(), folder_name)
                        folder_project=os.path.join(os.getcwd(), folder_name)
                        os.makedirs(folder_log_path, exist_ok=True)
                        os.makedirs(folder_project, exist_ok=True)

                    else:
                        log_folder=os.path.join(project_folder, "logs")
                        clopen_folder=os.path.join(project_folder, ".clopen")
                        folder_log_path = os.path.join(log_folder, folder_name)
                        clopen_folder_log_path = os.path.join(clopen_folder, folder_name)
                        os.makedirs(folder_log_path,exist_ok=True)
                        os.makedirs(clopen_folder_log_path, exist_ok=True)


                    #Escribir los logs
                    log_params_path = os.path.join(clopen_folder_log_path, params_name)
                    log_raw_file_path= os.path.join(clopen_folder_log_path, "raw_files_Cl-Open.txt")

                    with open(log_params_path, 'w') as file:
                        file.write(params)

                    #Guardar un txt de archivos en la carpeta de configuracion
                    with open(log_raw_file_path, 'w') as archivo_txt:
                        for index in range(self.file_list.count()):
                            file=self.file_list.item(index).text()
                            archivo_txt.write(file + '\n')


                    #Guardar un txt de archivos en la carpeta de configuracion
                    with open(raw_file_path, 'w') as archivo_txt:
                        for index in range(self.file_list.count()):
                            file=self.file_list.item(index).text()
                            archivo_txt.write(file + '\n')


                    #Iterar y ejecutar cada uno de los archivos
                    for index in range (self.file_list.count()):

                        files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                        arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]
                        self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

                    self.start_next_process_fragger(searchtype='Closed')




        ####################
        ### OPEN SEARCH ####
        ####################


        #### COMET ####

        if button_name_op=="comet_button_op":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/COMET/comet.win64.exe")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text_op.toPlainText().strip()
            params_name="config_params_Cl-Open_Open_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_open.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Cl-Open/Open_"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

                else:
                    os.makedirs(config_folder,exist_ok=True)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder,params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/COMET/comet.params.new")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        print(selected_db_path)
                        updated_lines.append(f"database_name = {selected_db_path}\n")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)


            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                if os.dir.isdir(folder_name):
                    pass
                else: 
                    os.makedirs(folder_log_path, exist_ok=True)

            else:
                log_folder=os.path.join(project_folder, "logs")
                folder_log_path = os.path.join(log_folder, folder_name)
                if os.dir.isdir(folder_name):
                    pass
                else: 
                    os.makedirs(folder_log_path, exist_ok=True)



            #Escribir los logs
            log_params_path = os.path.join(folder_log_path, params_name)
            log_raw_file_path= os.path.join(folder_log_path, "raw_files_open.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')



            #Iterar y ejecutar cada uno de los archivos

            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-P" + params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_comet(searchtype='Open')


        ### MSFRAGGER ###

        if button_name_op=="fragger_button_op":

            # Ejecutar el script

            script_path=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/MSFragger-4.1.jar")
            program_basename=os.path.splitext(os.path.basename(script_path))[0]
            params= self.config_text_op.toPlainText().strip()
            params_name="config_params_Open_"+program_basename+".new"

            if not project_folder:

                params_path = os.path.join(os.getcwd(), params_name)
                raw_file_path= os.path.join(os.getcwd(), "raw_files_open.txt")

            else:
                config_folder=os.path.join(project_folder, "config/Cl-Open/Open_"+program_basename)

                if os.path.exists(config_folder):
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder, params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")

                else:
                    os.makedirs(config_folder, exist_ok=True)
                    # Crear un archivo temporal para la tabla
                    params_path = os.path.join(config_folder,params_name)
                    raw_file_path= os.path.join(config_folder, "raw_files_open.txt")


            #Comprobar que el usuario a escrito algo en los parametros, sino coger los de por defecto

            if not params:
                msg = "Not configuration selected. Default params are going to apply.\nIf you do not agree, please select a params configuration file."
                QMessageBox.warning(self, "Not configuration selected", msg)

                params_default=os.path.join(os.getcwd(), "softwares/MSFragger-4.1/open_fragger.params")

                with open(params_default, 'r') as file:
                    params=file.read()

            with open(params_path, 'w') as file:
                file.write(params)

            lines=params.split('\n')

            #Cambiar la base de datos por la seleccionada

            if self.fasta_selection_button.currentText() !="":

                selected_database = self.fasta_selection_button.currentText()
                path_selected_db=os.path.join(os.getcwd(), "fastas")
                selected_db_path=os.path.join(path_selected_db, selected_database)

                updated_lines = []

                for line in lines:

                    if line.strip().startswith("database_name"):
                        print(selected_db_path)
                        updated_lines.append(f"database_name = {selected_db_path}\n")
                    else:
                        updated_lines.append(line)

                params='\n'.join(updated_lines) # Reescribimos los params

                with open(params_path, 'w') as file:
                    file.write(params)
            
            else:
                msg = "No fasta selected. Please select a fasta o import some"
                QMessageBox.critical(self, "Not fasta selected", msg)


            #Guardar un log

                # Obtener la fecha y hora actual
            now = datetime.now()
                # Formatear la fecha y hora como una cadena sin caracteres especiales
            folder_name = now.strftime("%Y%m%d%H%M%S")

            if not project_folder:

                folder_log_path = os.path.join(os.getcwd(), folder_name)
                os.makedirs(folder_log_path, exist_ok=True)

            else:
                log_folder=os.path.join(project_folder, "logs")
                folder_log_path = os.path.join(log_folder, folder_name)
                os.makedirs(folder_log_path, exist_ok=True)


            #Escribir los logs
            log_params_path = os.path.join(folder_log_path, params_name)
            log_raw_file_path= os.path.join(folder_log_path, "raw_files_open.txt")

            with open(log_params_path, 'w') as file:
                file.write(params)

            #Guardar un txt de archivos en la carpeta de configuracion
            with open(log_raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')


            #Guardar un txt de archivos en la carpeta de configuracion
            with open(raw_file_path, 'w') as archivo_txt:
                for index in range(self.file_list.count()):
                    file=self.file_list.item(index).text()
                    archivo_txt.write(file + '\n')

            #Iterar y ejecutar cada uno de los archivos
            for index in range (self.file_list.count()):

                files_before = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
                arguments = ["-jar", script_path, params_path, self.file_list.item(index).text()]
                self.process_queue.append((script_path, arguments, folder_log_path, index, files_before, program_basename))

            self.start_next_process_fragger(searchtype='Open')



    def on_process_finished(self, exitCode, exitStatus, index, files_before, program_basename, mode, searchtype):

        self.active_processes -=1
        

        if exitCode == 0:

            # Obtener lista de archivos después de ejecutar fragger
            files_after = set(os.listdir(os.path.dirname(self.file_list.item(index).text())))
            
            # Identificar nuevos archivos generados
            new_files = files_after - files_before
            
            # Mover los nuevos archivos a la ubicación deseada
            self.move_output_files(os.path.dirname(self.file_list.item(index).text()), new_files, program_basename, index, searchtype)
            self.move_fastapepindex_files(os.path.join(os.getcwd(), "fastas"), program_basename)

        if mode=="Fragger":

            self.start_next_process_fragger()

        if mode=="Comet":
            self.start_next_process_comet()



    def move_output_files(self, output_directory, new_files, program_basename, index, searchtype):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Cl-Open/Closed_"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Cl-Open/Closed_"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)
        
        # Mover los archivos generados
        for filename in new_files:

            source_path = os.path.join(output_directory, filename)
            new_filename = f"{os.path.splitext(filename)[0]}_{searchtype}_Search_{index+1}{os.path.splitext(filename)[1]}"
            destination_path = os.path.join(folder_results_path, new_filename)
            
            if os.path.isfile(source_path):
                shutil.move(source_path, destination_path)


    def move_fastapepindex_files(self, fasta_directory, program_basename):

        global project_folder

        # Directorio
        if not project_folder:
            folder_results_path = os.path.join(os.getcwd(), "results/Cl-Open/Closed_"+program_basename)

        else:
            folder_results_path=os.path.join(project_folder, "results/Cl-Open/Closed_"+program_basename)
        
        # Crear el nuevo directorio si no existe
        os.makedirs(folder_results_path, exist_ok=True)

        # Obtener la lista de archivos ".pepindex" en el directorio fuente
        pepindex_files = glob.glob(os.path.join(fasta_directory, "*.pepindex"))

        # Mover cada archivo encontrado al directorio de destino
        for file_path in pepindex_files:

            file_name = os.path.basename(file_path)
            destination_path = os.path.join(folder_results_path, file_name)
            shutil.move(file_path, destination_path)

                

    def start_next_process_fragger(self, searchtype):

        if self.active_processes < self.max_simultaneous_processes and self.process_queue:

            script_path, arguments, folder_log_path, index, files_before, program_basename = self.process_queue.pop(0)

            process = QProcess(self)
            process.setProgram("java")
            process.setArguments(arguments)
            # Conectar señales para manejar la salida estándar y error
            process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
            process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
            #### Mover los archivos salida de Fragger a la carpeta resultados ####
            process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename, 'Fragger', searchtype))
            # Iniciar el proceso
            process.start()
            self.active_processes += 1
            # Esperar hasta que el proceso termine
            #process.waitForFinished(-1)

    def start_next_process_comet(self):

        if self.active_processes < self.max_simultaneous_processes and self.process_queue:

            script_path, arguments, folder_log_path, index, files_before, program_basename = self.process_queue.pop(0)

            process = QProcess(self)
            process.setProgram(script_path)
            process.setArguments(arguments)
            # Conectar señales para manejar la salida estándar y error
            process.readyReadStandardOutput.connect(lambda: self.handle_stdout(process, folder_log_path))
            process.readyReadStandardError.connect(lambda: self.handle_stderr(process, folder_log_path))
            process.finished.connect(lambda exitCode, exitStatus, idx=index, fb=files_before: self.on_process_finished(exitCode, exitStatus, idx, fb, program_basename, 'Comet', searchtype))
            process.start()
            self.active_processes += 1


    def log_to_console(self, message):

        self.console_output.append(message)



    def handle_stdout(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stdout = codec.toUnicode(process.readAllStandardOutput())
        #stdout = process.readAllStandardOutput().data().decode("utf-8")
        self.log_to_console(stdout)
        stdout_file = os.path.join(folder, f"stdout.txt")
        with open(stdout_file, 'a') as f:
            f.write(stdout)

    def handle_stderr(self, process, folder):

        process = self.sender()
        codec = QTextCodec.codecForName("UTF-8")
        stderr = codec.toUnicode(process.readAllStandardError())
        #stderr = process.readAllStandardError().data().decode("utf-8")
        self.log_to_console(stderr)
        stderr_file = os.path.join(folder, f"stderr.txt")
        with open(stderr_file, 'a') as f:
            f.write(stderr)


    def show_help(self, help_text):

        help_window = HelpWindow(help_text)
        help_window.exec_()


    def read_help_text(self):

        help_path=os.path.join(os.getcwd(), "Config/Help.txt")
        
        with open(help_path, "r") as file:
            help_text = file.read()

        return help_text

    def select_files(self):

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            file_paths = file_dialog.selectedFiles()

            for file_path in file_paths:
                item = QListWidgetItem(file_path)
                self.file_list.addItem(item)

    def check_files(self):

        raw_files = []
        no_raw_files=[]

        for index in range(self.file_list.count()):
            file_path = self.file_list.item(index).text()

            if file_path.lower().endswith('.raw'):
                raw_files.append(file_path)

            else:
                no_raw_files.append(file_path)
        
        if raw_files and not no_raw_files:
            msg = "All files are .raw type files."
            QMessageBox.information(self, "Raw Files Checked", msg)

        elif no_raw_files and not raw_files:
            msg = "Not all files are .raw. Do you want to continue?\nThis files are not .raw:\n"+"\n".join(no_raw_files)
            QMessageBox.warning(self, "Issue find in the files selected", msg)

        else:
            msg = "No raw file selected"
            QMessageBox.warning(self, "No selection", msg)
        

    def delete_file(self):

        selected_items = self.file_list.selectedItems()

        if selected_items:
            for item in selected_items:
                self.file_list.takeItem(self.file_list.row(item))

    def load_configuration(self):

        button = self.sender()
        button_name = button.objectName()


        if button_name == "load_config_button_op":

            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFile)

            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]

                with open(file_path, 'r') as file:
                    config_text = file.read()
                    self.config_text_op.setPlainText(config_text)



        elif button_name == "load_config_button_close":

            file_dialog = QFileDialog(self)
            file_dialog.setFileMode(QFileDialog.ExistingFile)

            if file_dialog.exec_():
                file_path = file_dialog.selectedFiles()[0]

                with open(file_path, 'r') as file:
                    config_text = file.read()
                    self.config_text_close.setPlainText(config_text)


        msg = "Configuration File Loaded successfuly"
        QMessageBox.information(self, "Configuration File", msg)


    def save_configuration(self):

        button = self.sender()
        button_name = button.objectName()

        if button_name == "save_config_button_op":

            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setDefaultSuffix('txt')

            if file_dialog.exec_():

                file_path = file_dialog.selectedFiles()[0]
                config_text = self.config_text_op.toPlainText()

                with open(file_path, 'w') as file:
                    file.write(config_text)

        elif button_name == "save_config_button_close":

            file_dialog = QFileDialog(self)
            file_dialog.setAcceptMode(QFileDialog.AcceptSave)
            file_dialog.setDefaultSuffix('txt')

            if file_dialog.exec_():

                file_path = file_dialog.selectedFiles()[0]
                config_text = self.config_text_close.toPlainText()

                with open(file_path, 'w') as file:
                    file.write(config_text)

        msg = "Configuration File saved successfuly"
        QMessageBox.information(self, "Configuration File", msg)

    def keyPressEvent(self, event: QKeyEvent):

        if event.key() == Qt.Key_Delete:
            self.delete_file()

    def mantein_fasta(self):

        self.fasta_window = Fasta()
        self.fasta_window.show()


    def go_to_main_window(self):

        self.hide()

        self.main_window=ClOpenSearch()
        self.main_window.show()






######################
###  Main Window  ####
######################

class Fasta(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Layout principal
        layout = QVBoxLayout()


        # Etiqueta y campo para la ruta del proyecto
        project_path_layout = QHBoxLayout()
        self.ruta_proyecto_label = QLabel("<b>Path:")
        self.ruta_proyecto_input = QLineEdit(self)
        self.ruta_proyecto_input.setFixedHeight(25)
        self.ruta_proyecto_input.setStyleSheet("""
            QLineEdit {
                border-radius: 5px;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 255, 40%);
            }
        """)
        layout.addWidget(self.ruta_proyecto_label)
        project_path_layout.addWidget(self.ruta_proyecto_input)

        # Boton para seleccionar la ruta
        self.seleccionar_ruta_btn = QPushButton("Browser", self)
        self.seleccionar_ruta_btn.clicked.connect(self.seleccionar_ruta)
        self.seleccionar_ruta_btn.setFixedSize(70, 25)
        self.seleccionar_ruta_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 100%);
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 1px solid rgba(0, 0, 255, 40%);
                border-radius: 5px;
                font-weight: bold;
            }
            """
        )
        project_path_layout.addWidget(self.seleccionar_ruta_btn)
        layout.addLayout(project_path_layout)

        # Boton para crear el proyecto
        self.crear_proyecto_btn = QPushButton("Submit", self)
        self.crear_proyecto_btn.clicked.connect(self.cargar_proyecto)
        self.crear_proyecto_btn.setFixedSize(70, 30)
        self.crear_proyecto_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 60%);
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: 1 px solid rgba(0, 255, 0, 100%);
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 80%);
                font-weight: bold;
            }
            """
        )

        #Añadir un espacio para separar el boton
        layout.addSpacing(15)
        layout.addWidget(self.crear_proyecto_btn)
        layout.addSpacing(15)

        self.setLayout(layout)
        self.setWindowTitle("Inport Fasta File")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))
        self.setFixedSize(400, 130)
        #self.setGeometry(100, 100, 400, 200)


    def seleccionar_ruta(self):

        # Filtro de archivos para solo permitir archivos fasta
        options = QFileDialog.Options()
        file_filter = "Fasta Files (*.fasta);;All Files (*)"
        
        # Mostrar el diálogo de selección de archivos
        ruta, _ = QFileDialog.getOpenFileName(self, "Select Fasta File", "", file_filter, options=options)

        if ruta:
            self.ruta_proyecto_input.setText(ruta)


    def cargar_proyecto(self):

        ruta_fasta = self.ruta_proyecto_input.text().strip()
        nombre_fasta=os.path.basename(ruta_fasta)
        file_extension = os.path.splitext(ruta_fasta)[1][1:]

        if not ruta_fasta:

            QMessageBox.critical(self, "Error", "Fasta file path not detected. Plese check the path")

            return

        elif file_extension !="fasta":

            QMessageBox.critical(self, "Error", "Selected file is not fasta file. Plese check the path")

            return

        else:
            fasta_folder=os.path.join(os.getcwd(), "fastas")
            fasta_name=os.path.join(fasta_folder,nombre_fasta)
            shutil.copy(ruta_fasta, fasta_name)
            QMessageBox.information(self, "Import Fasta File", f"The fasta '{nombre_fasta}' has been imported.")
            self.close()




class LoadProject(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Layout principal
        layout = QVBoxLayout()


        # Etiqueta y campo para la ruta del proyecto
        project_path_layout = QHBoxLayout()
        self.ruta_proyecto_label = QLabel("<b>Path:")
        self.ruta_proyecto_input = QLineEdit(self)
        self.ruta_proyecto_input.setFixedHeight(25)
        self.ruta_proyecto_input.setStyleSheet("""
            QLineEdit {
                border-radius: 5px;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 255, 40%);
            }
        """)
        layout.addWidget(self.ruta_proyecto_label)
        project_path_layout.addWidget(self.ruta_proyecto_input)

        # Boton para seleccionar la ruta
        self.seleccionar_ruta_btn = QPushButton("Browser", self)
        self.seleccionar_ruta_btn.clicked.connect(self.seleccionar_ruta)
        self.seleccionar_ruta_btn.setFixedSize(70, 25)
        self.seleccionar_ruta_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 100%);
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 1px solid rgba(0, 0, 255, 40%);
                border-radius: 5px;
                font-weight: bold;
            }
            """
        )
        project_path_layout.addWidget(self.seleccionar_ruta_btn)
        layout.addLayout(project_path_layout)

        # Boton para crear el proyecto
        self.crear_proyecto_btn = QPushButton("Submit", self)
        self.crear_proyecto_btn.clicked.connect(self.cargar_proyecto)
        self.crear_proyecto_btn.setFixedSize(70, 30)
        self.crear_proyecto_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 60%);
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: 1 px solid rgba(0, 255, 0, 100%);
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 80%);
                font-weight: bold;
            }
            """
        )

        #Añadir un espacio para separar el boton
        layout.addSpacing(15)
        layout.addWidget(self.crear_proyecto_btn)
        layout.addSpacing(15)

        self.setLayout(layout)
        self.setWindowTitle("Load Project")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))
        self.setFixedSize(400, 130)
        #self.setGeometry(100, 100, 400, 200)


    def seleccionar_ruta(self):

        ruta = QFileDialog.getExistingDirectory(self, "Select Directory")

        if ruta:
            self.ruta_proyecto_input.setText(ruta)


    def cargar_proyecto(self):

        global project_folder

        ruta_proyecto = self.ruta_proyecto_input.text().strip()
        nombre_proyecto=os.path.basename(ruta_proyecto)

        if not ruta_proyecto:

            QMessageBox.warning(self, "Error", "Project Path not detected. Plese insert project name and path")

            return

        else:
            project_folder=ruta_proyecto
            QMessageBox.information(self, "Load Project ", f"The project '{nombre_proyecto}' has been loaded.")
            self.close()




class NewProject(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):

        # Layout principal
        layout = QVBoxLayout()

        # Etiqueta y campo para el nombre del proyecto
        self.nombre_proyecto_label = QLabel("<b>Project Name:")
        self.nombre_proyecto_input = QLineEdit(self)
        self.nombre_proyecto_input.setFixedHeight(25)
        self.nombre_proyecto_input.setStyleSheet("""
            QLineEdit {
                border-radius: 5px;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 255, 40%);
            }
        """)
        layout.addWidget(self.nombre_proyecto_label)
        layout.addWidget(self.nombre_proyecto_input)
        layout.addSpacing(10)

        # Etiqueta y campo para la ruta del proyecto
        project_path_layout = QHBoxLayout()
        self.ruta_proyecto_label = QLabel("<b>Path:")
        self.ruta_proyecto_input = QLineEdit(self)
        self.ruta_proyecto_input.setFixedHeight(25)
        self.ruta_proyecto_input.setStyleSheet("""
            QLineEdit {
                border-radius: 5px;
                padding: 2px;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 255, 40%);
            }
        """)
        layout.addWidget(self.ruta_proyecto_label)
        project_path_layout.addWidget(self.ruta_proyecto_input)

        # Boton para seleccionar la ruta
        self.seleccionar_ruta_btn = QPushButton("Browser", self)
        self.seleccionar_ruta_btn.clicked.connect(self.seleccionar_ruta)
        self.seleccionar_ruta_btn.setFixedSize(70, 25)
        self.seleccionar_ruta_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 100%);
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 1px solid rgba(0, 0, 255, 40%);
                border-radius: 5px;
                font-weight: bold;
            }
            """
        )
        project_path_layout.addWidget(self.seleccionar_ruta_btn)
        layout.addLayout(project_path_layout)

        # Boton para crear el proyecto
        self.crear_proyecto_btn = QPushButton("Submit", self)
        self.crear_proyecto_btn.clicked.connect(self.crear_proyecto)
        self.crear_proyecto_btn.setFixedSize(70, 30)
        self.crear_proyecto_btn.setStyleSheet(
            """
            QPushButton {
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 60%);
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                border-color: 1 px solid rgba(0, 255, 0, 100%);
                border-radius: 5px;
                background-color: rgba(0, 0, 0, 80%);
                font-weight: bold;
            }
            """
        )

        #Añadir un espacio para separar el boton
        layout.addSpacing(15)
        layout.addWidget(self.crear_proyecto_btn)
        layout.addSpacing(15)

        self.setLayout(layout)
        self.setWindowTitle("New Project")
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))
        self.setFixedSize(400, 160)
        #self.setGeometry(100, 100, 400, 200)


    def seleccionar_ruta(self):

        ruta = QFileDialog.getExistingDirectory(self, "Select Directory")

        if ruta:
            self.ruta_proyecto_input.setText(ruta)

    def crear_proyecto(self):

        global project_folder

        nombre_proyecto = self.nombre_proyecto_input.text().strip()
        ruta_proyecto = self.ruta_proyecto_input.text().strip()

        if not nombre_proyecto or not ruta_proyecto:

            QMessageBox.warning(self, "Error", "Project Name or Path not detected. Plese insert project name and path")

            return

        ruta_completa = os.path.join(ruta_proyecto, nombre_proyecto)

        try:
            os.makedirs(ruta_completa)
            self.crear_estructura_carpetas(ruta_completa)
            project_folder=ruta_completa
            QMessageBox.information(self, "Create New ", f"The project '{nombre_proyecto}' has been created in {ruta_completa}.")
            self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"It cannot create the project: {str(e)}")

    def crear_estructura_carpetas(self, ruta_completa):

        carpetas = [".clopen", "logs", "config", "results", "stats"]

        for carpeta in carpetas:
            os.makedirs(os.path.join(ruta_completa, carpeta))


class HoverButton(QPushButton):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setMouseTracking(True)

    def enterEvent(self, event):
        self.setStyleSheet("""
            QPushButton {
                border-radius: 30px;
                background-color: rgba(0, 0, 0, 0%);
                border: 1px solid rgba(0, 200, 255, 40%);
            }
            QPushButton:hover {
                background-color: rgba(0, 200, 255, 40%);
            }
        """)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("""
            QPushButton {
                border-radius: 30px;
                background-color: rgba(0, 0, 0, 0%);
                border: none;
            }
        """)
        super().leaveEvent(event)



class ClOpenSearch(QMainWindow):

    def __init__(self):


        super().__init__()
        self.init_ui()


    def init_ui(self):

        global welcome_message_shown

        self.setWindowTitle('Cl-Open')
        self.setFixedSize(600, 650)
        self.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout() #Layout principal en vertical
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        grid_layout = QGridLayout() #Layout para los botones
        grid_layout.setHorizontalSpacing(100)  # Espacio horizontal entre los botones
        grid_layout.setVerticalSpacing(100)    # Espacio vertical entre los botones

        #Put the title
        self.param_title = QLabel("SELECT THE MODE")
        font = QFont("Arial", 24, QFont.Bold)
        self.param_title.setFont(font)
        self.param_title.setAlignment(Qt.AlignCenter)  # Centrar el título horizontalmente
        self.param_title.setToolTip("To start select one of the possibles modes")
        self.param_title.setToolTipDuration(5000)
        main_layout.addWidget(self.param_title,alignment=Qt.AlignTop)


        # Crear botones
        im_path=os.path.join(os.getcwd(), "Config") #Ruta a las imagenes de los modos

        self.button1 = HoverButton()
        self.set_button_properties(self.button1,os.path.join(im_path, "image1.png"), "<b>Open Search strategy Mode</b><br><br>Apply normal OpenSearch to identify postranslational modifications")
        self.button1.clicked.connect(self.open_function)
        grid_layout.addWidget(self.button1,0,0)

        self.button2 = HoverButton()
        self.set_button_properties(self.button2,os.path.join(im_path, "image2.png"), "<b>Close Search strategy Mode</b><br><br>Apply normal CloseSearch to identify postranslational modifications")
        self.button2.clicked.connect(self.close_function)
        grid_layout.addWidget(self.button2,0,1)

        self.button3 = HoverButton()
        self.set_button_properties(self.button3,os.path.join(im_path, "image3.png"), "<b>Cl-Open Search strategy Mode</b><br><br>Apply diferent CloseSearchs to improve OpenSearch output")
        self.button3.clicked.connect(self.clopen_function)
        grid_layout.addWidget(self.button3,1,0)

        self.button4 = HoverButton()
        self.set_button_properties(self.button4,os.path.join(im_path, "image4.png"), "<b>Cl-Open toolkit to fusion search files<b>")
        self.button4.clicked.connect(self.open_table_widget)
        grid_layout.addWidget(self.button4,1,1)

        # Centrar los botones en la ventana principal
        grid_layout.setAlignment(Qt.AlignCenter)

        main_layout.addLayout (grid_layout)
        self.central_widget.setLayout(main_layout)

        # Establecer estilo del tooltip
        self.setStyleSheet(
            """
            QToolTip {
                color: black;
                background-color: white;
                border: 2px solid black;
                font-size: 12pt;
                font-family: 'SansSerif';
                min-width: 400px;
            }
            """
        )

        # Crear la barra de herramientas
        toolbar = QToolBar("Toolbar")
        # Aplicar estilo personalizado a la barra de herramientas
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #444;
                border: 2px solid #555;
                padding: 0px;
                spacing: 5px;
            }
            QToolButton {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 50px;
            }
            QToolButton:hover {
                background-color: #555;
                border: 1px solid #888;
            }
        """)
        self.addToolBar(toolbar)


        #Crear un main para que se pueda volver al inicio
        main_action=QAction("Home", self)
        main_action.triggered.connect(self.go_to_main_window)
        toolbar.addAction(main_action)

        #Crear uun QMenu para los projectos
        project_menu = QMenu("Project", self)
        project_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        # Crear accion de crear un nuevo projecto y cargarlo
        NewProject_action = QAction("New Project", self)
        NewProject_action.triggered.connect(self.open_new_project_window)

        LoadProject_action=QAction("Load Project", self)
        LoadProject_action.triggered.connect(self.load_project)

        # Incorporarlos al menu de projecto y incorporar el menu a la toolbar
        project_menu.addAction(NewProject_action)
        project_menu.addAction(LoadProject_action)
        project_button=toolbar.addAction(project_menu.menuAction())

        #Crear un mantein fasta para que se pueda almacenar los fastas
        inport_menu = QMenu("Inport", self)
        inport_menu.setStyleSheet("""
            QMenu  {
                background-color: #444;
                border: 2px solid #555;
                padding: 3px;
                spacing: 5px;
            }
            QMenu::item {
                color: #fff;
                background-color: #444;
                border: none;
                padding: 0px;
                border-radius: 2px;
                min-height: 25px;
                min-width: 120px;
            }
            QMenu::item:selected {
                background-color: #555;
                border: 1px solid #888;
            }
        """)

        fasta_action=QAction("Fasta", self)
        fasta_action.triggered.connect(self.mantein_fasta)
        inport_menu.addAction(fasta_action)

        toolbar.addAction(inport_menu.menuAction())


        # Crear acción para iniciar el tutorial
        tutorial_action = QAction("Tutorial", self)
        tutorial_action.triggered.connect(self.start_tutorial)
        toolbar.addAction(tutorial_action)

        # Crear accion de ayuda
        help_action = QAction("Help", self)
        help_text = self.read_help_text()
        help_action.triggered.connect(lambda: self.show_help(help_text))
        # Agregar acción a la barra de herramientas
        toolbar.addAction(help_action)



        if not welcome_message_shown:
            # Mensaje de inicio
            msg_box=QMessageBox()
            #QMessageBox.information(self, "Welcome to Cl-Open", "<b>Welcome to Cl-Open programm!</b><br><br>This program make Open and Close Search of raw data of mass spectrometry, compare and improve the output results.<br><br><b>Click to start!</b>")
            # Configurar el icono personalizado
            mes_ico = os.path.join(os.getcwd(), "config/Ico.png")
            icon_pixmap = QPixmap(mes_ico)
            icon_pixmap = icon_pixmap.scaledToWidth(100)
            msg_box.setIconPixmap(icon_pixmap)

            msg_box.setText("<b>Welcome to Cl-Open programm!</b><br><br>This program make Open and Close Search of raw data of mass spectrometry, compare and improve the output results.<br><br><b>Click to start!</b>")
            msg_box.setWindowTitle("Welcome to Cl-Open")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setWindowIcon(QIcon(os.path.join(os.getcwd(), "config/Ico.png")))

            result = msg_box.exec()

            # Marcar el mensaje de bienvenida como mostrado
            welcome_message_shown = True

            self.open_new_project_window()

            self.show()
            

        else:
            self.show()


    def mantein_fasta(self):

        self.fasta_window = Fasta()
        self.fasta_window.show()


    def go_to_main_window(self):

        self.hide()

        self.main_window=ClOpenSearch()
        self.main_window.show()

    def open_new_project_window(self):

        self.new_project_window = NewProject()
        self.new_project_window.show()

    def load_project(self):

        self.load_project_window = LoadProject()
        self.load_project_window.show()


    def set_button_properties(self, button, icon_path, tooltip_text):

        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(193, 193, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Aplicar máscara de recorte redondeada
        rounded_pixmap = QPixmap(pixmap.size())
        rounded_pixmap.fill(Qt.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(Qt.white)
        painter.drawRoundedRect(pixmap.rect(), 30, 30)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

        button.setIcon(QIcon(rounded_pixmap))
        button.setIconSize(button.size())
        button.setFixedSize(200, 200)
        button.setToolTip(tooltip_text)
        button.setToolTipDuration(5000)

        # Eliminar el borde predeterminado y establecer el foco en false
        button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 0px;
            }
        """)
        button.setFocusPolicy(Qt.NoFocus)
        

    def open_table_widget(self):

        self.table_widget = TableWidget()
        self.table_widget.show()
        self.hide()

    def close_function (self):

        self.table_widget = CloseSearch()
        self.table_widget.show()
        self.hide()

    def open_function (self):

        self.table_widget = OpenSearch()
        self.table_widget.show()
        self.hide()

    def clopen_function (self):

        self.table_widget = ClOpenMode()
        self.table_widget.show()
        self.hide()

    def show_help(self, help_text):

        help_window = HelpWindow(help_text)
        help_window.exec_()

    def read_help_text(self):

        help_path=os.path.join(os.getcwd(), "Config/Help.txt")
        
        with open(help_path, "r") as file:
            help_text = file.read()

        return help_text

    def start_tutorial(self):

        self.steps = [
            (self.show_tooltip, (self.param_title, "To start select one of the possibles modes")),
            (self.show_tooltip, (self.button1, "")),
            (self.show_tooltip, (self.button2, "")),
            (self.show_tooltip, (self.button3, "")),
            (self.show_tooltip, (self.button4, "")),
        ]
        self.current_step = 0
        self.run_next_step()

    def run_next_step(self):

        if self.current_step < len(self.steps):
            function, args = self.steps[self.current_step]
            function(*args)
            self.current_step += 1
            QTimer.singleShot(2000, self.run_next_step)  # Espera 2 segundos entre pasos

    def show_tooltip(self, widget, text):

        pos = widget.mapToGlobal(widget.rect().center())
        pyautogui.moveTo(pos.x(), pos.y(), duration=0.5)
        QToolTip.showText(pos, text, widget)



###############
###  Main  ####
###############



if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = ClOpenSearch()
    #ex = TableWidget()
    #window.show()
    sys.exit(app.exec_())
    
    #sys.exit(app.exec_())