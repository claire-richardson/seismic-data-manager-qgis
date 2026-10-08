import os
import csv

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsFeature,
                       QgsField,
                       QgsGeometry,
                       QgsPointXY,
                       QgsProject,
                       QgsVectorLayer)
from qgis.PyQt.QtGui import QIcon, QFont
from qgis.PyQt.QtCore import Qt, QSize, QMetaType
from qgis.PyQt.QtWidgets import (QAction,
                                 QMainWindow,
                                 QPushButton,
                                 QLabel,
                                 QFrame,
                                 QFileDialog,
                                 QWidget,
                                 QVBoxLayout,
                                 QHBoxLayout,
                                 QLineEdit,
                                 QTextEdit,
                                 QTableWidget,
                                 QScrollArea,
                                 QTableWidgetItem,
                                 QComboBox,
                                 QCheckBox,
                                 QMessageBox
                                )

plugin_dir = os.path.dirname(__file__)

# Define the plugin's main window
class SP1ImporterDialog(QMainWindow):
    
    # Define the constructor.
    ## Call the parent QMainWindow class, set its initial attributes.
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SP1 Importer")
        self.initGui()

    # Define the UI initializer
    ## Add widgets here and define their initial attributes
    def initGui(self):
        #############
        # ADD WIDGETS
        #############
        self.window_title = QLabel("SP1 file importer and parser")
        self.window_title.setStyleSheet("font-weight: bold; font-size: 24px;")
        self.window_title_label = QLabel("Developed by Claire Richardson (crricha5@asu.edu)\nOctober 2026")
        self.window_title_label.setStyleSheet("font-size: 16px;")
        
        # Input file selector
        ## Widget: Label for input file selector
        self.input_label = QLabel("Input file: ")
        self.input_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        ## Widget: Push button to browse for input file
        self.input_button = QPushButton("Browse", self)
        ## Widget: Line edit box to display input file name
        self.input_line = QLineEdit(self)
        
        # Output file selector
        ## Widget: Label for output file selector
        self.output_label = QLabel("Output file: ")
        self.output_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        ## Widget: Push button to enter export file name
        self.output_button = QPushButton("Save File", self)
        ## Widget: Line edit box to display input file name
        self.output_line = QLineEdit(self)
        ## Widget: Checkbox for CSV saving
        self.csv_save_checkbox = QCheckBox(text = "Save table as CSV?")
        
        # Header display
        ## Widget: Labels for the header material box
        self.header_label = QLabel("Header content:")
        self.header_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.header_doc_label = QLabel("Use the text box below to review and edit header content if necessary. Any changes made here will be retained in the final output .sp1 file. Note that SEG Specifications require exactly 20 lines of header content, each starting with 'H'.")
        self.header_doc_label.setStyleSheet("font-size: 14px;")
        self.header_doc_label.setWordWrap(True)
        ## Widget: Text box to display the header material
        self.header_text = QTextEdit(self)
        self.header_text.setFont(QFont('Courier'))
        
        # Data preview display
        ## Widget: Labels for the columnized data box
        self.data_columnized_title = QLabel("Data viewer:")
        self.data_columnized_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.data_columnized_label = QLabel("The text box below shows the raw data in the input file for reference.")
        self.data_columnized_label.setStyleSheet("font-size: 14px;")
        self.data_columnized_label.setWordWrap(True)
        ## Widget: Text box to display the data preview
        self.data_columnized_text = QTextEdit(self)
        self.data_columnized_text.setFont(QFont('Courier'))
        
        # Data parser table
        ## Widget: Label for the data parser section
        self.data_parser_title = QLabel("Data parser:")
        self.data_parser_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.data_parser_label = QLabel("Use this table and the text boxes below to provide the column numbers that delineate the data that belong to each header, according to the following:\n  -  For each header, you will need to identify the column numbers where the values start and end. You can do this by simply highlighting the relevant columns and clicking 'Add header and data', or by manually entering the values.\n  -  If the values for a given header include an implicit decimal point, provide the column number of the ones place (i.e., the value that should appear directly to the left of the decimal point).\nNote that not all headers need to be used, however those provided in the dropdown box are the headers listed in the SEG Specification. Besides the introductory/primary header content, which is handled in the top left box above, only the information passed through the parser is retained and used to make the final outputs. Anything unassigned (e.g., whitespace) will be ignored.")
        self.data_parser_label.setWordWrap(True)
        self.data_parser_label.setStyleSheet("font-size: 14px;")
        ## Widget: Push buttons for autoparse
        self.autoparse_button = QPushButton("Auto parse", self)
        ## Widget: Table for parsing input
        self.data_parser_table = QTableWidget()
        ## Widget: Push button to parse and regenerate parse preview
        self.data_parser_button = QPushButton("Add header and data", self)
        
        # Data parser headers
        self.data_parser_headers_label = QLabel("Header:")
        self.data_parser_headers_label.setStyleSheet("font-size: 14px;")
        self.data_parser_headers = QComboBox()
        self.data_parser_headers.addItems(list(seg_header_specs))
        #
        self.data_parser_headers_start_label = QLabel("Start column #:")
        self.data_parser_headers_start_label.setStyleSheet("font-size: 14px;")
        self.data_parser_headers_start_box = QLineEdit(self)
        #
        self.data_parser_headers_end_label = QLabel("End column #:")
        self.data_parser_headers_end_label.setStyleSheet("font-size: 14px;")
        self.data_parser_headers_end_box = QLineEdit(self)
        #
        self.data_parser_headers_decimal_label = QLabel("Decimal column # (ones place):")
        self.data_parser_headers_decimal_label.setStyleSheet("font-size: 14px;")
        self.data_parser_headers_decimal_box = QLineEdit(self)
        
        # Data attribute table
        ## Widget: Table to show the parsed data
        self.data_attribute_table_title = QLabel("Attribute table:")
        self.data_attribute_table_title.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.data_attribute_table_label = QLabel("Use the attribute table below to make sure that everything is processed correctly. If you make a mistake (e.g., assign the wrong header name), you can click on the header to highlight a column and then use the 'Remove column' button to erase it from the table and restart.")
        self.data_attribute_table_label.setStyleSheet("font-size: 14px;")
        self.data_attribute_table = QTableWidget()
        ## Widget: button to remove a column if needed:
        self.remove_column_button = QPushButton("Remove column", self)
        ## Widget: Button for plotting
        self.plotting_button = QPushButton("Add map layer", self)
        
        
        
        
        #######################
        # DEFINE WIDGET SIGNALS
        #######################
        ## signal for when the input file browser button is clicked (activate method/slot .load_input_file)
        self.input_button.clicked.connect(self.load_input_file)
        
        ## signal for when the input file browser button is clicked (activate method/slot .parse_data)
        self.data_parser_button.clicked.connect(self.parse_data)
        
        ## signal for when the remove column button is pushed (activate method/slot .remove_column)
        self.remove_column_button.clicked.connect(self.remove_column)

        ## signal for when the autoparse button is pushed (activate method/slot .autoparse)
        self.autoparse_button.clicked.connect(self.autoparse)

        ## signal for when the add map layer button is pushed (adds a map layer to the QGIS project (activate method/slot .add_map_layer))
        self.plotting_button.clicked.connect(self.add_map_layer)

        ## signal for when the save file button is pushed (activate method/slot .)
        self.output_button.clicked.connect(self.save_new_file)
        
        
        
        
        ##################
        # DESIGN UI LAYOUT
        ##################
        ## Set main vertical layout
        main_layout = QVBoxLayout()
        
        ## Create frames for additional widgets
        self.frame_title = QFrame(self)
        frame_title_layout = QVBoxLayout()
        frame_title_layout.addWidget(self.window_title)
        frame_title_layout.addWidget(self.window_title_label)
        self.frame_title.setLayout(frame_title_layout)
        main_layout.addWidget(self.frame_title)
        
        ## add input file dialog frame
        self.frame_in = QFrame(self)
        frame_in_layout = QHBoxLayout()
        frame_in_layout.addWidget(self.input_label)
        frame_in_layout.addWidget(self.input_line)
        frame_in_layout.addWidget(self.input_button)
        self.frame_in.setLayout(frame_in_layout)
        main_layout.addWidget(self.frame_in)
        
        # frame1: holds preview widgets
        ## define main frame 3 (horizontal layout for preview boxes)
        self.frame1 = QFrame(self)
        frame1_layout = QHBoxLayout()
        #
        ## left frame (header)
        self.frame1_left = QFrame(self)
        frame1_left_layout = QVBoxLayout()
        frame1_left_layout.addWidget(self.header_label)
        frame1_left_layout.addWidget(self.header_doc_label)
        frame1_left_layout.addWidget(self.header_text)
        self.frame1_left.setLayout(frame1_left_layout)
        #
        ## right frame (raw data)
        self.frame1_right = QFrame(self)
        frame1_right_layout = QVBoxLayout()
        frame1_right_layout.addWidget(self.data_columnized_title)
        frame1_right_layout.addWidget(self.data_columnized_label)
        frame1_right_layout.addWidget(self.data_columnized_text)
        self.frame1_right.setLayout(frame1_right_layout)
        #
        ## add everything to the main frame1
        frame1_layout.addWidget(self.frame1_left)
        frame1_layout.addWidget(self.frame1_right)
        self.frame1.setLayout(frame1_layout)
        main_layout.addWidget(self.frame1)
        
        
        # frame_parse_table: holds data parser title
        self.frame_parse_table = QFrame(self)
        frame_parse_table_layout = QVBoxLayout()
        frame_parse_table_layout.addWidget(self.data_parser_title)
        frame_parse_table_layout.addWidget(self.data_parser_label)
        frame_parse_table_layout.addWidget(self.data_parser_table)
        frame_parse_table_layout.addWidget(self.autoparse_button)
        self.frame_parse_table.setLayout(frame_parse_table_layout)
        main_layout.addWidget(self.frame_parse_table)
        
        
        # frame_headers: holds header definition items
        self.frame_headers = QFrame(self)
        frame_headers_layout = QHBoxLayout()
        #
        frame_headers_layout_dropdown = QFrame(self)
        frame_headers_layout_dropdown_layout = QVBoxLayout()
        frame_headers_layout_dropdown_layout.addWidget(self.data_parser_headers_label)
        frame_headers_layout_dropdown_layout.addWidget(self.data_parser_headers)
        frame_headers_layout_dropdown.setLayout(frame_headers_layout_dropdown_layout)
        #
        frame_headers_layout_start = QFrame(self)
        frame_headers_layout_start_layout = QVBoxLayout()
        frame_headers_layout_start_layout.addWidget(self.data_parser_headers_start_label)
        frame_headers_layout_start_layout.addWidget(self.data_parser_headers_start_box)
        frame_headers_layout_start.setLayout(frame_headers_layout_start_layout)
        #
        frame_headers_layout_end = QFrame(self)
        frame_headers_layout_end_layout = QVBoxLayout()
        frame_headers_layout_end_layout.addWidget(self.data_parser_headers_end_label)
        frame_headers_layout_end_layout.addWidget(self.data_parser_headers_end_box)
        frame_headers_layout_end.setLayout(frame_headers_layout_end_layout)
        #
        frame_headers_layout_decimal = QFrame(self)
        frame_headers_layout_decimal_layout = QVBoxLayout()
        frame_headers_layout_decimal_layout.addWidget(self.data_parser_headers_decimal_label)
        frame_headers_layout_decimal_layout.addWidget(self.data_parser_headers_decimal_box)
        frame_headers_layout_decimal.setLayout(frame_headers_layout_decimal_layout)
        #
        frame_headers_layout.addWidget(frame_headers_layout_dropdown)
        frame_headers_layout.addWidget(frame_headers_layout_start)
        frame_headers_layout.addWidget(frame_headers_layout_end)
        frame_headers_layout.addWidget(frame_headers_layout_decimal)
        self.frame_headers.setLayout(frame_headers_layout)
        main_layout.addWidget(self.frame_headers)
        
        
        # frame_attribute_table holds attribute table
        self.frame_attribute_table = QFrame(self)
        frame_attribute_table_layout = QVBoxLayout()
        frame_attribute_table_layout.addWidget(self.data_parser_button, alignment = Qt.AlignLeft)
        frame_attribute_table_layout.addWidget(self.data_attribute_table_title)
        frame_attribute_table_layout.addWidget(self.data_attribute_table)
        frame_attribute_table_layout.addWidget(self.remove_column_button, alignment = Qt.AlignLeft)
        frame_attribute_table_layout.addWidget(self.plotting_button, alignment = Qt.AlignLeft)
        self.frame_attribute_table.setLayout(frame_attribute_table_layout)
        main_layout.addWidget(self.frame_attribute_table)
        
    
    
        # framez: holds input and output file selector/dialog box widgets
        self.frame_out = QFrame(self)
        frame_out_layout = QHBoxLayout()
        frame_out_layout.addWidget(self.output_label)
        frame_out_layout.addWidget(self.output_line)
        frame_out_layout.addWidget(self.output_button)
        frame_out_layout.addWidget(self.csv_save_checkbox)
        self.frame_out.setLayout(frame_out_layout)
        main_layout.addWidget(self.frame_out)
        
        
        
        # Add all frames to the main layout
        container = QWidget()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container)
        container.setLayout(main_layout)
        # self.setCentralWidget(container)
        self.setCentralWidget(scroll_area)
        
    # Define the method/slot for when the input file (fin_button) is clicked (opens dialog box):
    def load_input_file(self):
        # first, grab the file name
        fin = QFileDialog.getOpenFileName(self, "Open File", "", "SP1 files (*.sp1);;All Files (*)")
        
        # if a file is selected (i.e., if the user doesn't hit "cancel") load the input file and do some initial parsing (print header and initial data preview)
        if fin:
            # grab the string of the entire input file path
            input_file_path = fin[0]
            
            # print it in the "input file" text edit line
            self.input_line.setText(input_file_path)

            # read and print the header information to the header text box            
            # open the input .sp1 file and read all lines
            with open(input_file_path, "r") as input_file:
                header_line_no = 0
                input_file_lines = input_file.readlines()
                
                table_data = []
                # loop through each line and parse, print previews accordingly
                for line in input_file_lines:
                    
                    # First, if the line is a header line (i.e., it starts with 'H'), print it in the header preview text box.
                    if line[0] == "H":
                        self.header_text.insertPlainText(f"{header_line_no + 1} {line}")
                        header_line_no += 1

                    # then, print the remaining lines as they are (raw) in the raw data preview text box
                    elif line[0] != "H":
                        self.data_columnized_text.insertPlainText(line)
                        table_data.append(line)

                self.data_parser_table.setRowCount(len(table_data))
                self.data_parser_table.setColumnCount(len(table_data[0]))
                for data_line in range(len(table_data)):
                    for data_item in range(len(table_data[data_line])):
                        self.data_parser_table.setItem(data_line, data_item, QTableWidgetItem((table_data[data_line][data_item])))

                for data_item in range(len(table_data[0])):
                    self.data_parser_table.setColumnWidth(data_item, 1)
                    
                self.data_attribute_table.setRowCount(len(table_data))
                
        else:
            return

    def autoparse(self):
        return
        
    
    def parse_data(self):
        dec = False
        drop = False
        # grab the values for the indices from the text boxes above the attribute box, for the current header
        current_header = self.data_parser_headers.currentText()
        all_header_indices = self.data_parser_table.selectionModel().selectedIndexes()
        header_indices = sorted(set(index.column() for index in all_header_indices))
        
        if len(header_indices) > 0:
            start_idx = header_indices[0] + 1
            end_idx = header_indices[-1] + 1
            self.data_parser_headers_start_box.setText(str(start_idx))
            self.data_parser_headers_end_box.setText(str(end_idx))
        else:
            start_idx = int(self.data_parser_headers_start_box.text())
            end_idx = int(self.data_parser_headers_end_box.text())
        
        # determine whether there will be a decimal point to add, and where its index is
        if self.data_parser_headers_decimal_box.text():
            dec_idx = int(self.data_parser_headers_decimal_box.text())
            dec = True

        # determine whether there are indices to ignore, and where they are
        column_index = self.data_attribute_table.columnCount()

        # scan the input data file to retain just the data, dropping the header content
        data_lines = []
        with open(self.input_line.text(), 'r') as fin:
            input_lines = fin.readlines()
            for line in input_lines:
                if line[0] != 'H':
                    data_lines.append(line)

        # add a column to the attribute table to be populated
        self.data_attribute_table.insertColumn(column_index)

        # parse the data accordingly, and add to the table
        for data_line in range(len(data_lines)):
            raw_val = data_lines[data_line][start_idx - 1:end_idx]
            
            if (current_header == 'Latitude') and ('N' in raw_val) or ('S' in raw_val) or ('E' in raw_val) or ('W' in raw_val):
                drop = True
                drop_idx = []
                for direction in ['N', 'S', 'E', 'W']:
                    if direction in raw_val:
                        drop_idx.append(start_idx + raw_val.index(direction))
            
            # if there is no decimal and nothing to be dropped:
            val = raw_val

            # if there is a decimal point to consider, but nothing to drop:
            if dec == True and drop == False:
                val = f'{data_lines[data_line][start_idx - 1:dec_idx]}.{data_lines[data_line][dec_idx:end_idx]}'

            # if there is not a decimal point, but a value to be dropped:
            elif dec == False and drop == True:
                parts = []
                st = start_idx - 1

                for idx in drop_idx:
                    parts.append(f'{data_lines[data_line][st:idx - 1]}')
                    st = idx

                parts.append(f'{data_lines[0][idx:end_idx]}')

                val = ''.join(parts)

            # if there is both a decimal point to be added and values to be dropped:
            elif dec == True and drop == True:
                # first, add the decimal point
                val_dec = f'{data_lines[data_line][start_idx - 1:dec_idx]}.{data_lines[data_line][dec_idx:end_idx]}'

                # make a modified list of indices to drop, based on the positioning of the decimal point
                mod_idx = []
                for idx in drop_idx:
                    if idx >= dec_idx:
                        mod_idx.append((idx + 1) - start_idx)
                    else:
                        mod_idx.append((idx) - start_idx)

                list_val = list(val_dec)

                itr = 0
                for idx in mod_idx:
                    idx -= itr
                    del list_val[idx]
                    itr += 1

                val = ''.join(list_val)
            
            # handle latitude and longitude assignments
            if (current_header == 'Latitude') and ('S' in raw_val) and ('-' not in raw_val):
                val = f'-{val}'

            if (current_header == 'Longitude') and ('W' in raw_val) and ('-' not in raw_val):
                val = f'-{val}'

            self.data_attribute_table.setItem(data_line, column_index, QTableWidgetItem(val))
        self.data_attribute_table.setHorizontalHeaderItem(column_index, QTableWidgetItem(current_header))

    
    
    
    def remove_column(self):
        self.data_attribute_table.removeColumn(self.data_attribute_table.currentColumn())


    def add_map_layer(self):
        table = self.data_attribute_table
        project = QgsProject.instance()
        layer_crs = project.crs()
        if not layer_crs.isValid():
            QMessageBox.warning(self, "Cannot add map layer", "Set a valid project CRS before plotting positions.")
            return

        column_names = []
        for column in range(table.columnCount()):
            header = table.horizontalHeaderItem(column)
            if header is None or not header.text().strip():
                QMessageBox.warning(self, "Cannot add map layer", "Every attribute column must have a header.")
                return
            column_names.append(header.text())

        column_indices = {name: index for index, name in enumerate(column_names)}
        if {'Latitude', 'Longitude'}.issubset(column_indices):
            x_index = column_indices['Longitude']
            y_index = column_indices['Latitude']
            coordinate_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        else:
            QMessageBox.warning(
                self,
                "Cannot add map layer",
                "The attribute table must contain Latitude and Longitude columns."
            )
            return

        layer = QgsVectorLayer("Point", "SP1 positions", "memory")
        layer.setCrs(layer_crs)
        provider = layer.dataProvider()
        provider.addAttributes([QgsField(name, QMetaType.Type.QString) for name in column_names])
        layer.updateFields()
        coordinate_transform = QgsCoordinateTransform(coordinate_crs, layer_crs, project)

        features = []
        for row in range(table.rowCount()):
            values = []
            for column in range(table.columnCount()):
                item = table.item(row, column)
                values.append(item.text().strip() if item is not None else "")

            try:
                x = float(values[x_index])
                y = float(values[y_index])
            except ValueError:
                continue

            if coordinate_crs.authid() == "EPSG:4326" and not (-180 <= x <= 180 and -90 <= y <= 90):
                continue

            feature = QgsFeature(layer.fields())
            point = coordinate_transform.transform(QgsPointXY(x, y))
            feature.setGeometry(QgsGeometry.fromPointXY(point))
            feature.setAttributes(values)
            features.append(feature)

        if not features:
            QMessageBox.warning(self, "Cannot add map layer", "No rows contain valid coordinates.")
            return

        provider.addFeatures(features)
        layer.updateExtents()
        project.addMapLayer(layer)

        
    def save_new_file(self):
        fout = QFileDialog.getSaveFileName(self, "Save File", "", "SP1 files (*.sp1);;All Files (*)")
        
        output_file_path = fout[0]
        if not output_file_path:
            return
        
        else:
            output_file_stem, _ = os.path.splitext(output_file_path)
            output_file_path_csv = f'{output_file_stem}.csv'
            
            # print it in the "output file" text edit line
            self.output_line.setText(output_file_path)
            
            # make a list to hold CSV data, that will be saved if the CSV data box is checked
            csv_data_list_all = []
            
            # first, write the header info:
            with open(output_file_path, 'w') as output_file:
                output_file.write(self.header_text.toPlainText())
                
                # determine the headers included in the attribute table:
                parsed_headers = []
                # Gather header names
                for col in range(self.data_attribute_table.columnCount()):
                    parsed_headers.append(self.data_attribute_table.horizontalHeaderItem(col).text())
                csv_data_list_all.append(parsed_headers)

                # start looping through the attribute table, row by row
                for row in range(self.data_attribute_table.rowCount()):
                    # for each row, make an empty list of exactly 80 characters, that will be joined as a string and written to the output file
                    data_list = []
                    for i in range(0,80):
                        data_list.append(' ')

                    # also, make an empty list for the CSV
                    csv_data_list = []
                    
                    # now, loop through each column and get the data
                    for parsed_header_idx in range(len(parsed_headers)):
                        parsed_header = parsed_headers[parsed_header_idx]  # get header name
                        item = self.data_attribute_table.item(row, parsed_header_idx)
                        item_value = item.text() if item is not None else ''
                        start_idx = seg_header_specs[parsed_header][0] - 1  # get the starting index from the SEG specs dictionary
                        end_idx = seg_header_specs[parsed_header][1] - 1  # get the ending index from the SEG specs dictionary
                        entry_length = (end_idx - start_idx) + 1
                        csv_data_list.append(item_value)
                        
                        # remove any added decimals, and replace any dropped WESN values
                        if '.' in item_value:
                            item_value = ''.join(item_value.split('.'))
                            
                        if parsed_header == 'Latitude':
                            if '-' in item_value:
                                item_value = f'{item_value.split("-")[-1]}S'
                            else:
                                item_value = f'{item_value}N'
                            
                            if len(item_value) > entry_length:
                                strip = item_value[:entry_length - 1]
                                dir_indicator = item_value[-1]
                                item_value = f'{strip}{dir_indicator}'

                        if parsed_header == 'Longitude':
                            if '-' in item_value:
                                item_value = f'{item_value.split("-")[-1]}W'
                            else:
                                item_value = f'{item_value}E'
                            
                            if len(item_value) > entry_length:
                                strip = item_value[:entry_length - 1]
                                dir_indicator = item_value[-1]
                                item_value = f'{strip}{dir_indicator}'
                        
                        # add the item to the list according to its indices, and length. the `Line name` is left justified, everything else is right justified                            
                        item_length = len(item_value)
                        
                        # find the index locations for the current header info
                        if item_length <= entry_length:
                            # if the header is Line name, it should be left justified
                            if parsed_header == 'Line name':
                                item_indices = list(range(start_idx, (end_idx + 1) - item_length))
                            # otherwise, right justify
                            else:
                                item_indices = list(range((end_idx + 1) - item_length, end_idx + 1))

                        else:
                            item_indices = list(range(start_idx, end_idx + 1))

                        # replace the items in the empty `data_list` with the values at the correct locations
                        for char_idx in range(item_length):
                            char = item_value[char_idx]
                            item_idx = item_indices[char_idx]
                            data_list[item_idx] = char

                    csv_data_list_all.append(csv_data_list)
                    newly_formatted_row = "".join(data_list)
                    output_file.write(f"{newly_formatted_row}\n")
  
    
            if self.csv_save_checkbox.isChecked():
                with open(output_file_path_csv, 'w') as output_file_csv:
                    writer = csv.writer(output_file_csv)
                    for csv_data_row in csv_data_list_all:
                        writer.writerow(csv_data_row)

class SP1Importer:
    def __init__(self, iface):
        self.iface = iface
        self.action = None
        self.dialog = None

    def initGui(self):
        icon = os.path.join(plugin_dir, 'icon.png')
        self.action = QAction(QIcon(icon), 'SP1 Importer', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        if self.action is not None:
            self.iface.removeToolBarIcon(self.action)
            self.action = None
        if self.dialog is not None:
            self.dialog.close()
            self.dialog = None

    def run(self, checked=False):
        if self.dialog is None:
            self.dialog = SP1ImporterDialog(self.iface.mainWindow())
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()

seg_header_specs = {
    'Line name': [2, 17],
    'Shotpoint ID': [18, 25],
    'Reshoot code': [26, 26],
    'Latitude': [27, 35],
    'Longitude': [36, 45],
    'Easting': [46, 53],
    'Northing': [54, 61],
    'Elevation': [62, 66],
    'Year': [67, 68],
    'Day of year': [69, 71],
    'Hours': [72, 73],
    'Minutes': [74, 75],
    'Seconds': [76, 77]
}
