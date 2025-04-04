# -*- coding: utf-8 -*-
import sys
import requests
import os
import pandas as pd
from dotenv import load_dotenv
import pyvista as pv
import numpy as np
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import (QSplitter, QHeaderView, QAbstractItemView, QMessageBox,
                             QLineEdit, QPushButton, QVBoxLayout, QWidget, QFrame,
                             QGroupBox, QHBoxLayout, QLabel, QTableWidget)
from pyvistaqt import QtInteractor
import traceback

# --- GraphDB Configuration and Credentials ---
load_dotenv()
username = os.getenv('username')
password = os.getenv('password')
graphdb_url = "http://localhost:7200"
repo_name = "defect"
endpoint = f"{graphdb_url}/repositories/{repo_name}"
graphdb_auth = (username, password) if username and password else None

# --- Constants and Setup ---
stl_file = "airfoil.stl"
VISUALIZATION_SCALE_FACTOR = 19.0809 # Converts 'inch' inputs to meters for plotting

# Coordinates of the reference spheres (METERS)
reference_spheres = {
    "top_front":    (-14.5649, -3.372,    66.8014),
    "bottom_front": (-15.3724,  0.108056, 17.3466),
    "top_back":     ( 21.6716,  5.41146,  66.6593),
    "bottom_back":  ( 22.2777,  0.75596,  17.4064),
}
datum_pos_fixed = np.array(reference_spheres["top_front"]) # Top Front sphere center (meters)
vec_down_fixed = np.array(reference_spheres["bottom_front"]) - datum_pos_fixed
unit_vec_down_fixed = vec_down_fixed / np.linalg.norm(vec_down_fixed)

# --- Helper Functions (clean_uri, safe_float_convert, get_defect_info) ---
# ... (Keep these functions exactly as they were) ...
def clean_uri(uri):
    if not isinstance(uri, str): return None
    if '#' in uri: return uri.split('#')[-1]
    elif '/' in uri: return uri.split('/')[-1]
    else: return uri
def safe_float_convert(value, default=0.0):
    if value is None or value == '': return default
    try: return float(value)
    except (ValueError, TypeError): print(f"Warning: Could not convert '{value}' to float."); return default
def get_defect_info(target_defect_id: str, endpoint: str, auth: tuple = None) -> pd.DataFrame | None:
    if not target_defect_id: print("Error: No target defect ID provided."); return None
    query = f"""
    PREFIX :    <http://api.stardog.com/>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT
      ?defect ?defectID ?airfoil ?airfoilPartNum ?defectRegion ?regionPart
      ?index1Val ?index1DatumPart ?index2Val ?index2DatumPart ?depthVal ?lengthVal
      ?blendProc ?blendParticipant ?blendDepth ?blendLength ?blendFlatLen
      ?blendFillet ?blendPropFactor ?blendLoc ?blendNodeComp
    WHERE {{
      # Core Defect Identification
      ?defect rdf:type :Airfoil_Defect .
      # Link Defect to its ID via Information Entities
      ?defectICE rdf:type :Designative_Information_Content_Entity ;
                 :designates ?defect ; :generically_depends_on ?defectIBE .
      ?defectIBE :has_text_value ?defectID .

      # Filter by the specific Defect ID provided
      FILTER (?defectID = "{target_defect_id}") # The user's ID goes here!

      # Optional details about the defect and associated blend processes
      OPTIONAL {{ ?defect :inheres_in ?defectRegion . ?airfoil :has_continuant_part ?defectRegion . }}
      OPTIONAL {{ ?defectRegion :has_continuant_part ?regionPart . }}
      OPTIONAL {{ ?partNumICE rdf:type :Part_Number ; :designates ?airfoil ; :generically_depends_on ?partNumIBE . ?partNumIBE :has_text_value ?airfoilPartNum . }}
      OPTIONAL {{ ?index1MICE rdf:type :Defect_Index1_Distance_to_Datum ; :describes ?defect ; :generically_depends_on ?index1IBE . ?index1IBE :has_decimal_value ?index1Val . OPTIONAL {{ ?index1MICE :measured_from_part ?index1DatumPart . }} }}
      OPTIONAL {{ ?index2MICE rdf:type :Defect_Index2_Distance_to_Datum ; :describes ?defect ; :generically_depends_on ?index2IBE . ?index2IBE :has_decimal_value ?index2Val . OPTIONAL {{ ?index2MICE :measured_from_part ?index2DatumPart . }} }}
      OPTIONAL {{ ?depthMICE rdf:type :Defect_Depth ; :describes ?defect ; :generically_depends_on ?depthIBE . ?depthIBE :has_decimal_value ?depthVal . }}
      OPTIONAL {{ ?lengthMICE rdf:type :Defect_Length ; :describes ?defect ; :generically_depends_on ?lengthIBE . ?lengthIBE :has_decimal_value ?lengthVal . }}
      OPTIONAL {{
        ?blendProc rdf:type :Blend_on_Edge_Process ; :is_about ?defect .
        OPTIONAL {{ ?blendProc :has_participant ?blendParticipant . }}
        OPTIONAL {{ ?blendDepthMICE rdf:type :Blend_On_Edge_Depth_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendDepthIBE . ?blendDepthIBE :has_decimal_value ?blendDepth . }}
        OPTIONAL {{ ?blendLengthMICE rdf:type :Blend_On_Edge_Length_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendLengthIBE . ?blendLengthIBE :has_decimal_value ?blendLength . }}
        OPTIONAL {{ ?blendFlatLenMICE rdf:type :Blend_On_Edge_Flat_Length_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendFlatLenIBE . ?blendFlatLenIBE :has_decimal_value ?blendFlatLen . }}
        OPTIONAL {{ ?blendFilletMICE rdf:type :Blend_On_Edge_Fillet_Radius_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendFilletIBE . ?blendFilletIBE :has_decimal_value ?blendFillet . }}
        OPTIONAL {{ ?blendPropMICE rdf:type :Blend_On_Edge_Proportional_Factor_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendPropIBE . ?blendPropIBE :has_decimal_value ?blendPropFactor . }}
        OPTIONAL {{ ?blendLocMICE rdf:type :Blend_On_Edge_Location_Measurement ; :describes ?blendProc ; :generically_depends_on ?blendLocIBE . ?blendLocIBE :has_decimal_value ?blendLoc . }}
        OPTIONAL {{ ?blendNodeCompMICE rdf:type :Blend_On_Edge_Node_Component ; :describes ?blendProc ; :generically_depends_on ?blendNodeCompIBE . ?blendNodeCompIBE :has_text_value ?blendNodeComp . }}
      }}
    }} ORDER BY ?defect ?blendProc
    """
    # <<< --- END OF SPARQL QUERY --- >>>
    headers = {"Accept": "application/sparql-results+json"}; post_data = {"query": query}
    try: response = requests.post(endpoint, data=post_data, headers=headers, auth=auth); response.raise_for_status()
    except requests.exceptions.RequestException as e: print(f"Error connecting to GraphDB: {e}"); return None
    try:
        results = response.json(); data = []
        bindings = results.get("results", {}).get("bindings", [])
        if not bindings: print(f"No defect found with ID: {target_defect_id}"); return pd.DataFrame()
        for result in bindings:
            row = { "Defect": clean_uri(result.get("defect", {}).get("value")), "Defect ID": result.get("defectID", {}).get("value", ""), "Airfoil": clean_uri(result.get("airfoil", {}).get("value")), "Airfoil Part Num": result.get("airfoilPartNum", {}).get("value", ""), "Defect Region": clean_uri(result.get("defectRegion", {}).get("value")), "Region Part": clean_uri(result.get("regionPart", {}).get("value", "")), "Index1 Val": result.get("index1Val", {}).get("value", ""), "Index1 Datum Part": clean_uri(result.get("index1DatumPart", {}).get("value", "")), "Index2 Val": result.get("index2Val", {}).get("value", ""), "Index2 Datum Part": clean_uri(result.get("index2DatumPart", {}).get("value", "")), "Depth Val": result.get("depthVal", {}).get("value", ""), "Length Val": result.get("lengthVal", {}).get("value", ""), "Blend Process": clean_uri(result.get("blendProc", {}).get("value", "")), "Blend Participant": clean_uri(result.get("blendParticipant", {}).get("value", "")), "Blend Depth": result.get("blendDepth", {}).get("value", ""), "Blend Length": result.get("blendLength", {}).get("value", ""), "Blend Flat Len": result.get("blendFlatLen", {}).get("value", ""), "Blend Fillet": result.get("blendFillet", {}).get("value", ""), "Blend Prop Factor": result.get("blendPropFactor", {}).get("value", ""), "Blend Loc": result.get("blendLoc", {}).get("value", ""), "Blend Node Comp": result.get("blendNodeComp", {}).get("value", "") }
            data.append(row)
        return pd.DataFrame(data)
    except Exception as e: print(f"Error processing results: {e}"); return None

##############################################################################
#                                PyQt Main Window
##############################################################################

class MainWindow(QtWidgets.QMainWindow):
    # --- __init__ method remains the same ---
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Airfoil Defect Visualization")
        self.setGeometry(100, 100, 1400, 900)
        self.defect_data = None
        self.defect_actors = []
        self._initialize_defect_params()
        # UI Layout
        main_widget = QWidget(); self.setCentralWidget(main_widget); main_layout = QHBoxLayout(main_widget)
        self.splitter = QSplitter(QtCore.Qt.Horizontal); main_layout.addWidget(self.splitter)
        # Plotter frame
        plotter_frame = QFrame(); plotter_frame.setFrameShape(QFrame.StyledPanel); plotter_layout = QVBoxLayout(plotter_frame)
        plotter_layout.setContentsMargins(0,0,0,0); self.plotter = QtInteractor(plotter_frame, auto_update=False)
        plotter_layout.addWidget(self.plotter.interactor); self.splitter.addWidget(plotter_frame)
        # Controls frame
        controls_widget = QWidget(); controls_layout = QVBoxLayout(controls_widget); self.splitter.addWidget(controls_widget)
        # Input Group
        input_group = QGroupBox("Load Defect"); input_layout = QHBoxLayout(input_group)
        self.defect_id_input = QLineEdit(); self.defect_id_input.setPlaceholderText("Enter Defect ID")
        self.load_button = QPushButton("Load & Visualize"); self.load_button.clicked.connect(self.load_and_update_defect)
        input_layout.addWidget(QLabel("Defect ID:")); input_layout.addWidget(self.defect_id_input); input_layout.addWidget(self.load_button)
        controls_layout.addWidget(input_group)
        # View Buttons
        view_buttons_group = QGroupBox("Camera Views"); view_buttons_layout = QVBoxLayout(view_buttons_group)
        btn_iso = QPushButton("Isometric View"); btn_xy = QPushButton("XY View"); btn_yz = QPushButton("YZ View"); btn_xz = QPushButton("XZ View")
        btn_iso.clicked.connect(self.set_iso_view); btn_xy.clicked.connect(self.set_xy_view); btn_yz.clicked.connect(self.set_yz_view); btn_xz.clicked.connect(self.set_xz_view)
        view_buttons_layout.addWidget(btn_iso); view_buttons_layout.addWidget(btn_xy); view_buttons_layout.addWidget(btn_yz); view_buttons_layout.addWidget(btn_xz)
        controls_layout.addWidget(view_buttons_group)
        # Index/Depth Table
        self.index_depth_table_group = QGroupBox("Defect Location Parameters"); index_depth_table_layout = QVBoxLayout(self.index_depth_table_group)
        self.index_depth_table = QTableWidget(); index_depth_table_layout.addWidget(self.index_depth_table); controls_layout.addWidget(self.index_depth_table_group)
        # Blend Table
        self.blend_table_group = QGroupBox("Blend Parameters"); blend_table_layout = QVBoxLayout(self.blend_table_group)
        self.blend_table = QTableWidget(); blend_table_layout.addWidget(self.blend_table); controls_layout.addWidget(self.blend_table_group)
        controls_layout.addStretch()
        self.splitter.setSizes([900, 400]); self.splitter.setStretchFactor(0, 1); self.splitter.setStretchFactor(1, 0)
        self._setup_base_plot(); self._update_display()


    # --- _initialize_defect_params remains the same ---
    def _initialize_defect_params(self):
        self.airfoil_part_num = "N/A"; self.defect_id_loaded = "N/A"; self.defect_title = "Blend Info"
        self.indexVal1_input = 0.0; self.indexVal2_input = 0.0; self.depthVal_input = 0.0
        self.blend_fillet_radius = 0.0; self.blend_depth = 0.0; self.blend_length = 0.0
        self.blend_flat_length = 0.0; self.blend_proportional_factor = 0.0; self.blend_location = 0.0
        self.blend_node_component = ""
        self.pos_red1, self.pos_red2, self.pos_red3 = [datum_pos_fixed] * 3
        self.short_label = "Index 1: N/A in"; self.far_label = "Index 2: N/A in"; self.depth_label = "Depth: N/A in"
        self.arrow_depth_start, self.arrow_depth_end = [datum_pos_fixed] * 2
        self.line1_start, self.line1_end = [datum_pos_fixed] * 2
        self.line2_start, self.line2_end = [datum_pos_fixed] * 2
        self.txt_pos_v1, self.txt_pos_v2, self.txt_pos_depth = [datum_pos_fixed] * 3


    # --- load_and_update_defect remains the same ---
    def load_and_update_defect(self):
        target_id = self.defect_id_input.text().strip()
        if not target_id: QMessageBox.warning(self, "Input Error", "Please enter a Defect ID."); return
        print(f"Querying for Defect ID: {target_id}...")
        app_instance = QtWidgets.QApplication.instance();
        if app_instance: app_instance.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.defect_data = None
        try:
            defect_df = get_defect_info(target_id, endpoint, graphdb_auth)
            if defect_df is None: QMessageBox.critical(self, "Query Error", "Failed to query GraphDB."); self._initialize_defect_params()
            elif defect_df.empty: QMessageBox.information(self, "Not Found", f"No data found for Defect ID: {target_id}"); self._initialize_defect_params()
            else:
                self.defect_data = defect_df.iloc[0].to_dict(); print("Defect data loaded successfully.")
                self.airfoil_part_num = self.defect_data.get("Airfoil Part Num", "N/A")
                self.defect_id_loaded = self.defect_data.get("Defect ID", "N/A")
                self.indexVal1_input = safe_float_convert(self.defect_data.get("Index1 Val"))
                self.indexVal2_input = safe_float_convert(self.defect_data.get("Index2 Val"))
                self.depthVal_input = safe_float_convert(self.defect_data.get("Depth Val"))
                self.blend_fillet_radius = safe_float_convert(self.defect_data.get("Blend Fillet"))
                self.blend_depth = safe_float_convert(self.defect_data.get("Blend Depth"))
                self.blend_length = safe_float_convert(self.defect_data.get("Blend Length"))
                self.blend_flat_length = safe_float_convert(self.defect_data.get("Blend Flat Len"))
                self.blend_proportional_factor = safe_float_convert(self.defect_data.get("Blend Prop Factor"))
                self.blend_location = safe_float_convert(self.defect_data.get("Blend Loc"))
                self.blend_node_component = self.defect_data.get("Blend Node Comp", "")
        except Exception as e: print(f"Error loading/processing data: {e}\n{traceback.format_exc()}"); QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}"); self._initialize_defect_params()
        finally:
            if app_instance: app_instance.restoreOverrideCursor()
        self._update_display()


    def _calculate_visualization_data(self):
        """ Calculates positions (in meters) and labels (in display units). """
        datum_pos = datum_pos_fixed       # meters
        unit_vec_down = unit_vec_down_fixed # unit vector

        # --- Calculate distances in METERS for plotting ---
        index1_dist_m = self.indexVal1_input * VISUALIZATION_SCALE_FACTOR
        index2_dist_m = self.indexVal2_input * VISUALIZATION_SCALE_FACTOR
        depth_dist_m = self.depthVal_input * VISUALIZATION_SCALE_FACTOR

        # --- Calculate positions in METERS ---
        self.pos_red1 = datum_pos + unit_vec_down * index1_dist_m
        self.pos_red2 = datum_pos + unit_vec_down * index2_dist_m
        mid_z = (self.pos_red1[2] + self.pos_red2[2]) / 2.0
        self.pos_red3 = np.array([datum_pos[0] + depth_dist_m, datum_pos[1], mid_z])

        # --- Prepare labels using the ORIGINAL input/display values ---
        self.short_label = f"Index 1 = {self.indexVal1_input:.3f} in"
        self.far_label = f"Index 2 = {self.indexVal2_input:.3f} in"
        self.depth_label = f"Depth = {self.depthVal_input:.3f} in"

        # --- Calculate line/arrow coordinates in METERS ---
        self.arrow_depth_start = np.array([datum_pos[0], datum_pos[1], mid_z])
        self.arrow_depth_end = self.pos_red3

        # Define offsets (in meters) - adjust magnitude if needed
        offset_1 = np.array([-5.0, 0.0, 0.0]) # Increased offset magnitude slightly
        offset_2 = np.array([-10.0, 0.0, 0.0])# Increased offset magnitude slightly

        # <<< MODIFIED Line End Points >>>
        # Start at the offset defect position
        self.line1_start = self.pos_red1 + offset_1
        # End at the offset DATUM position
        self.line1_end   = datum_pos + offset_1 # Connects back to datum (offset)

        # Start at the offset defect position
        self.line2_start = self.pos_red2 + offset_2
        # End at the offset DATUM position
        self.line2_end   = datum_pos + offset_2 # Connects back to datum (offset)
        # <<< END MODIFICATION >>>

        # Calculate text label positions (midpoints of the NEW lines) - in meters
        self.txt_pos_v1 = (self.line1_start + self.line1_end) / 2
        self.txt_pos_v2 = (self.line2_start + self.line2_end) / 2
        self.txt_pos_depth = (self.arrow_depth_start + self.arrow_depth_end) / 2


    def _setup_base_plot(self):
        """ Sets up the static parts of the plot: mesh, reference spheres, axes. """
        self.plotter.clear()
        self.plotter.enable_anti_aliasing('fxaa')
        try:
            self.airfoil_mesh = pv.read(stl_file)
            # <<< MODIFIED: Set opacity to 1.0 for solid view >>>
            self.plotter.add_mesh(self.airfoil_mesh, color="lightgray", opacity=1.0)
            # <<< END MODIFICATION >>>
        except FileNotFoundError:
             QMessageBox.critical(self, "File Error", f"Cannot find STL file: {stl_file}")
             self.airfoil_mesh = pv.Sphere(); self.plotter.add_mesh(self.airfoil_mesh, color="red") # Placeholder

        # Reference Spheres
        for label, center in reference_spheres.items():
            sphere = pv.Sphere(radius=0.3, center=center); self.plotter.add_mesh(sphere, color="yellow", opacity=1.0, name=f"ref_{label}")
            self.plotter.add_point_labels([center + np.array([0,0,0.5])], [label.replace("_", " ").title()], font_size=10, text_color="white", point_color="yellow", shape=None, always_visible=False, name=f"ref_label_{label}")

        self.plotter.add_axes(interactive=True)
        self.set_iso_view()


    # --- _update_plot remains the same (uses calculated points/labels) ---
    def _update_plot(self):
        """ Clears previous defect actors and adds new ones based on current data. """
        for actor in self.defect_actors:
            try: self.plotter.remove_actor(actor, render=False)
            except Exception: pass
        self.defect_actors.clear()
        if self.defect_data is not None:
            try:
                # Defect Spheres
                sphere1 = pv.Sphere(radius=0.6, center=self.pos_red1); sphere2 = pv.Sphere(radius=0.6, center=self.pos_red2); sphere3 = pv.Sphere(radius=0.6, center=self.pos_red3)
                self.defect_actors.append(self.plotter.add_mesh(sphere1, color="red", name="defect_sphere1", render=False))
                self.defect_actors.append(self.plotter.add_mesh(sphere2, color="red", name="defect_sphere2", render=False))
                self.defect_actors.append(self.plotter.add_mesh(sphere3, color="red", name="defect_sphere3", render=False))
                # Measurement Lines
                line_v1 = pv.Line(self.line1_start, self.line1_end); line_v2 = pv.Line(self.line2_start, self.line2_end); line_depth = pv.Line(self.arrow_depth_start, self.arrow_depth_end)
                self.defect_actors.append(self.plotter.add_mesh(line_v1, color="cyan", line_width=5, name="line_index1", render=False))
                self.defect_actors.append(self.plotter.add_mesh(line_v2, color="lime", line_width=5, name="line_index2", render=False))
                self.defect_actors.append(self.plotter.add_mesh(line_depth, color="magenta", line_width=5, name="line_depth", render=False))
                # Measurement Labels
                label_actor1 = self.plotter.add_point_labels([self.txt_pos_v1], [self.short_label], font_size=12, text_color="cyan", shape=None, always_visible=True, name="label_index1", render=False)
                if label_actor1: self.defect_actors.append(label_actor1)
                label_actor2 = self.plotter.add_point_labels([self.txt_pos_v2], [self.far_label], font_size=12, text_color="lime", shape=None, always_visible=True, name="label_index2", render=False)
                if label_actor2: self.defect_actors.append(label_actor2)
                label_actor3 = self.plotter.add_point_labels([self.txt_pos_depth], [self.depth_label], font_size=12, text_color="magenta", shape=None, always_visible=True, name="label_depth", render=False)
                if label_actor3: self.defect_actors.append(label_actor3)
            except Exception as e: print(f"Error adding defect viz actors: {e}\n{traceback.format_exc()}"); self.defect_actors.clear() # Clear list on error
        print(f"Rendering plot. {len(self.defect_actors)} defect actors present.")
        self.plotter.render()


    # --- Table Update Methods (_update_index_depth_table, _update_blend_table) remain the same ---
    def _update_index_depth_table(self):
        table = self.index_depth_table; table.clearContents()
        title = f"Airfoil: {self.airfoil_part_num} | Defect ID: {self.defect_id_loaded}"; self.index_depth_table_group.setTitle(title)
        data = { "Index 1": f"{self.indexVal1_input:.3f}", "Index 2": f"{self.indexVal2_input:.3f}", "Depth": f"{self.depthVal_input:.3f}" }
        table.setColumnCount(2); table.setRowCount(len(data)); table.setHorizontalHeaderLabels(["Location Parameter", "Value (in)"])
        header = table.horizontalHeader(); header.setSectionResizeMode(0, QHeaderView.Stretch); header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        font = header.font(); font.setBold(True); header.setFont(font); header.setStyleSheet("QHeaderView::section { background-color: #E8E8E8; padding: 4px; border: 1px solid #C0C0C0; }")
        row = 0
        for key, value in data.items():
            param_item = QtWidgets.QTableWidgetItem(key); value_item = QtWidgets.QTableWidgetItem(value)
            value_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            param_item.setFlags(param_item.flags() ^ QtCore.Qt.ItemIsEditable); value_item.setFlags(value_item.flags() ^ QtCore.Qt.ItemIsEditable)
            table.setItem(row, 0, param_item); table.setItem(row, 1, value_item); row += 1
        table.verticalHeader().setVisible(False); table.resizeRowsToContents(); table.setAlternatingRowColors(True)

    def _update_blend_table(self):
        table = self.blend_table; table.clearContents(); self.blend_table_group.setTitle("Blend Parameters")
        params_with_units = ["Fillet Radius", "Blend Depth", "Blend Length", "Flat Length", "Location"]
        data = { "Fillet Radius": f"{self.blend_fillet_radius:.3f}", "Blend Depth": f"{self.blend_depth:.3f}", "Blend Length": f"{self.blend_length:.3f}", "Flat Length": f"{self.blend_flat_length:.3f}", "Proportional Factor": f"{self.blend_proportional_factor:.3f}", "Location": f"{self.blend_location:.3f}", "Node Component": f"{self.blend_node_component}" }
        table.setColumnCount(2); table.setRowCount(len(data)); table.setHorizontalHeaderLabels(["Blend Parameter", "Value"])
        header = table.horizontalHeader(); header.setSectionResizeMode(0, QHeaderView.Stretch); header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        font = header.font(); font.setBold(True); header.setFont(font); header.setStyleSheet("QHeaderView::section { background-color: #E8E8E8; padding: 4px; border: 1px solid #C0C0C0; }")
        row = 0
        for key, value in data.items():
            param_item = QtWidgets.QTableWidgetItem(key); value_text = f"{value} in" if key in params_with_units else value
            if key == "Node Component" and not self.blend_node_component: value_text = "N/A"
            value_item = QtWidgets.QTableWidgetItem(value_text); value_item.setTextAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            param_item.setFlags(param_item.flags() ^ QtCore.Qt.ItemIsEditable); value_item.setFlags(value_item.flags() ^ QtCore.Qt.ItemIsEditable)
            table.setItem(row, 0, param_item); table.setItem(row, 1, value_item); row += 1
        table.verticalHeader().setVisible(False); table.resizeRowsToContents(); table.setAlternatingRowColors(True)


    # --- _update_display remains the same ---
    def _update_display(self):
        print("Updating display...")
        self._calculate_visualization_data()
        self._update_plot()
        self._update_index_depth_table()
        self._update_blend_table()
        print("Display update complete.")


    # --- Camera View Slot Methods (Remain the same) ---
    def set_iso_view(self): self.plotter.camera_position = 'iso'; self.plotter.reset_camera(); self.plotter.render()
    def set_xy_view(self): self.plotter.view_xy(); self.plotter.reset_camera(); self.plotter.render()
    def set_yz_view(self): self.plotter.view_yz(); self.plotter.reset_camera(); self.plotter.render()
    def set_xz_view(self): self.plotter.view_xz(); self.plotter.reset_camera(); self.plotter.render()

    # Override closeEvent
    def closeEvent(self, event):
        print("Closing plotter...") 
        try: self.plotter.close() 
        except Exception as e: print(f"Error closing plotter: {e}")
        super().closeEvent(event)

##############################################################################
#                                Run Application
##############################################################################
if __name__ == "__main__":
    if not graphdb_auth: print("Warning: GraphDB username/password not found in .env.")
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
