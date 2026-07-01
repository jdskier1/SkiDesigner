# Program for Designing Ski/Snowboards
# Written by JD Ritchey, starting 3.1.2026
  
import sys
import math
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsItem, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QFileDialog, QSlider, QLabel, QDoubleSpinBox, QDialog, QDialogButtonBox, QFormLayout, QComboBox, QColorDialog, QGroupBox, QMenuBar, QMessageBox, QAbstractSpinBox, QSizePolicy, QTextEdit, QCheckBox, QScrollArea, QFrame, QToolButton, QButtonGroup, QSplitter
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPainterPath, QPainterPathStroker, QFont, QPolygonF, QImage, QAction, QLinearGradient, QRadialGradient, QTransform, QTransform, QPdfWriter, QPageSize, QTextOption
from PySide6.QtCore import Qt, QRectF, QPointF, QSize, QDateTime, QMarginsF, QTimer, QLineF
import json
import xml.etree.ElementTree as ET
from pathlib import Path
try:
    from shapely.geometry import Polygon, MultiPolygon
    from shapely.geometry import JOIN_STYLE
    SHAPELY_AVAILABLE = True
except Exception:
    Polygon = None
    MultiPolygon = tuple
    JOIN_STYLE = None
    SHAPELY_AVAILABLE = False
# =========================
# Settings
# =========================
GRID_SPACING_CM = 1.0
PIXELS_PER_CM = 10.0
PIXELS_PER_MM = PIXELS_PER_CM / 10.0

BUILD_SHEET_NOTE_FIELDS = [
    ("upper_reinforcement", "Upper Reinforcement"),
    ("lower_reinforcement", "Lower Reinforcement"),
    ("core_wood_type", "Core Type"),
    ("sidewall_type", "Sidewall"),
    ("tip_tail_filler_type", "Tip/Tail Filler"),
    ("base_type", "Base Info"),
    ("topsheet_type", "Topsheet Info"),
    ("additional_notes", "Additional Notes"),
]

def default_build_sheet_notes():
    return {key: "" for key, _label in BUILD_SHEET_NOTE_FIELDS}

def get_default_shape_presets():
    return {
        "All Mountain Ski": {
            "edge": [
                {"pos": (0, 750), "in": (-25, 750), "out": (25, 750)},
                {"pos": (61, 650), "in": (61, 750), "out": (61, 550)},
                {"pos": (50, -90), "in": (50, 170), "out": (50, -350)},
                {"pos": (67, -820), "in": (67, -600), "out": (67, -980)},
                {"pos": (0, -1000), "in": (30, -1000), "out": (-30, -1000)},
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},
                {"pos": (-750, 500), "in": (-750, 550), "out": (-750, 450)},
                {"pos": (-740, 180), "in": (-740, 260), "out": (-740, 60)},
                {"pos": (-740, -400), "in": (-740, -300), "out": (-740, -500)},
                {"pos": (-750, -700), "in": (-750, -550), "out": (-750, -750)},
                {"pos": (-750, -1000), "in": (-750, -940), "out": (-750, -1060)},
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 800)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-450, 700)},
                {"pos": (-450, 560),  "in": (-450, 590), "out": (-450, 520)},
                {"pos": (-440, -90),  "in": (-440, 260), "out": (-440, -420)},
                {"pos": (-450, -780), "in": (-450, -740), "out": (-450, -820)},
                {"pos": (-400, -1000),"in": (-450, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },

        "Park Ski": {
            "edge": [
                {"pos": (0, 750), "in": (-48, 750), "out": (20, 750)},
                {"pos": (61, 650), "in": (60, 750), "out": (60, 450)},
                {"pos": (46, -100), "in": (47, 250), "out": (47, -450)},
                {"pos": (63, -820), "in": (63, -720), "out": (63, -920)},
                {"pos": (0, -1000), "in": (50, -1000), "out": (-50, -1000)},
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},
                {"pos": (-750, 560), "in": (-750, 620), "out": (-750, 470)},
                {"pos": (-740, 180), "in": (-740, 200), "out": (-740, 160)},
                {"pos": (-740, -350), "in": (-740, -250), "out": (-740, -450)},
                {"pos": (-750, -800), "in": (-750, -700), "out": (-750, -920)},
                {"pos": (-750, -1000), "in": (-750, -940), "out": (-750, -1060)},
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 790)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-442, 708)},
                {"pos": (-445, 650),  "in": (-445, 675), "out": (-445, 650)},
                {"pos": (-434, -90),  "in": (-434, 220), "out": (-434, -360)},
                {"pos": (-445, -820), "in": (-445, -720), "out": (-445, -920)},
                {"pos": (-400, -1000),"in": (-442, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },
        
        "Carving Ski": {
            "edge": [
                {"pos": (0, 750), "in": (-25, 750), "out": (25, 750)},
                {"pos": (53, 650), "in": (56, 750), "out": (50, 550)},
                {"pos": (38.3, -30), "in": (38.3, 230.2), "out": (38.3, -289.8)},
                {"pos": (60, -820), "in": (60, -667.4), "out": (68, -972.6)},
                {"pos": (0, -1000), "in": (30, -1000), "out": (-30, -1000)},
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},
                {"pos": (-750, 500), "in": (-750, 550), "out": (-750, 450)},
                {"pos": (-740, 180), "in": (-740, 260), "out": (-740, 60)},
                {"pos": (-740, -400), "in": (-740, -300), "out": (-740, -500)},
                {"pos": (-750, -700), "in": (-750, -550), "out": (-750, -750)},
                {"pos": (-750, -1000), "in": (-750, -940), "out": (-750, -1060)},
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 800)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-450, 700)},
                {"pos": (-450, 560),  "in": (-450, 590), "out": (-450, 520)},
                {"pos": (-440, -90),  "in": (-440, 260), "out": (-440, -420)},
                {"pos": (-450, -780), "in": (-450, -740), "out": (-450, -820)},
                {"pos": (-400, -1000),"in": (-450, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },
        
        "Powder Ski": {
            "edge": [
                {"pos": (0, 750), "in": (-50, 750), "out": (50, 750)},              #Tail
                {"pos": (65, 650), "in": (65, 715), "out": (65, 585)},
                {"pos": (55, -60), "in": (55, 70), "out": (55, -250)},
                {"pos": (70, -750), "in": (70, -570), "out": (70, -930)},
                {"pos": (0, -1000), "in": (40, -1000), "out": (-40, -1000)},        #Tip
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},
                {"pos": (-750, 560), "in": (-750, 620), "out": (-750, 470)},
                {"pos": (-743, 180), "in": (-743, 260), "out": (-743, 60)},
                {"pos": (-743, -420), "in": (-743, -320), "out": (-743, -560)},
                {"pos": (-750, -780), "in": (-750, -700), "out": (-750, -860)},
                {"pos": (-750, -1000), "in": (-750, -950), "out": (-750, -1050)},
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 790)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-440, 712)},
                {"pos": (-444, 560),  "in": (-444, 590), "out": (-444, 520)},
                {"pos": (-450, -69),  "in": (-450, 180), "out": (-450, -300)},
                {"pos": (-444, -735), "in": (-444, -635), "out": (-444, -835)},
                {"pos": (-400, -1000),"in": (-425, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },
        
        "Powder Board": {
            "edge": [
                {"pos": (0, 675), "in": (-100, 675), "out": (100, 675)},        #Tail
                {"pos": (145, 630), "in": (145, 725), "out": (145, 535)},
                {"pos": (140, -75), "in": (140, 130), "out": (140, -280)},
                {"pos": (160, -710), "in": (160, -575), "out": (160, -844)},
                {"pos": (0, -1000), "in": (100, -1000), "out": (-100, -1000)},    #Tip
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},
                {"pos": (-750, 500), "in": (-750, 550), "out": (-750, 450)},
                {"pos": (-740, 180), "in": (-740, 260), "out": (-740, 60)},
                {"pos": (-740, -400), "in": (-740, -300), "out": (-740, -500)},
                {"pos": (-750, -700), "in": (-750, -550), "out": (-750, -750)},
                {"pos": (-750, -1000), "in": (-750, -940), "out": (-750, -1060)},
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 790)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-440, 712)},
                {"pos": (-444, 560),  "in": (-444, 590), "out": (-444, 520)},
                {"pos": (-438, -70),  "in": (-438, 180), "out": (-438, -300)},
                {"pos": (-448, -760), "in": (-448, -720), "out": (-448, -800)},
                {"pos": (-400, -1000),"in": (-442, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },

        "Caving Board": {
            "edge": [
                {"pos": (0, 750), "in": (-100, 750), "out": (100, 750)},              #Tail
                {"pos": (148, 600), "in": (148, 665), "out": (148, 535)},
                {"pos": (130, -80), "in": (130, 320), "out": (130, -500)},
                {"pos": (154, -805), "in": (154, -735), "out": (154, -875)},
                {"pos": (0, -1000), "in": (85, -1000), "out": (-85, -1000)},        #Tip
            ],
            "core": [
                {"pos": (-750, 750), "in": (-750, 800), "out": (-750, 700)},        #Tail
                {"pos": (-750, 500), "in": (-750, 550), "out": (-750, 450)},
                {"pos": (-740, 180), "in": (-740, 260), "out": (-740, 60)},
                {"pos": (-740, -400), "in": (-740, -300), "out": (-740, -500)},
                {"pos": (-750, -700), "in": (-750, -550), "out": (-750, -750)},
                {"pos": (-750, -1000), "in": (-750, -940), "out": (-750, -1060)},   #Tip
            ],
            "camber": [
                {"pos": (-400, 800),  "in": (-410, 800), "out": (-400, 790)},
                {"pos": (-400, 750),  "in": (-400, 760), "out": (-440, 712)},
                {"pos": (-444, 560),  "in": (-444, 590), "out": (-444, 520)},
                {"pos": (-438, -70),  "in": (-438, 180), "out": (-438, -300)},
                {"pos": (-448, -760), "in": (-448, -720), "out": (-448, -800)},
                {"pos": (-400, -1000),"in": (-442, -950), "out": (-400, -1010)},
                {"pos": (-400, -1050),"in": (-400, -1040), "out": (-410, -1050)},
            ],
        },
    }

def format_preset_data_text(preset_name):
    presets = get_default_shape_presets()
    preset = presets.get(preset_name, {})
    if not preset:
        return "No preset data available."

    lines = [f"{preset_name} preset data"]
    for section_name in ("edge", "core", "camber"):
        entries = preset.get(section_name, [])
        lines.append(f"\n{section_name.title()}:")
        for idx, entry in enumerate(entries, start=1):
            pos = entry.get("pos", (0, 0))
            hin = entry.get("in", (0, 0))
            hout = entry.get("out", (0, 0))
            lines.append(
                f"  P{idx}: pos={pos}  in={hin}  out={hout}"
            )
    return "\n".join(lines)

# =========================
# Control Point Class
# =========================
class ControlPointMid:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y() + 150)
        self.handle_out = QPointF(pos.x(), pos.y() - 150)
        self.locked = True
        self.selected = False
#        self.lock_direction = "vertical"
        self.lock_direction = None
class ControlPointTip:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x() + 60, pos.y())
        self.handle_out = QPointF(pos.x() - 60, pos.y())
        self.locked = True
        self.selected = False      
        self.lock_direction = "horizontal"
class ControlPointTail:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x() - 50, pos.y())
        self.handle_out = QPointF(pos.x() + 50, pos.y())
        self.locked = True
        self.selected = False
        self.lock_direction = "horizontal"
class ControlPointCoreThickness:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y()+50)
        self.handle_out = QPointF(pos.x(), pos.y()-50)
        self.locked = True
        self.selected = False
        self.lock_direction = None
class ControlPointCoreCamber1:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y()+30)
        self.handle_out = QPointF(pos.x(), pos.y()-30)
        self.locked = True
        self.selected = False      
        self.lock_direction = None
class ControlPointCoreCamber2:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y()+10)
        self.handle_out = QPointF(pos.x()-10, pos.y())
        self.locked = True
        self.selected = False      
        self.lock_direction = None
class ControlPointCoreCamber3:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x()-10, pos.y())
        self.handle_out = QPointF(pos.x(), pos.y()-10)
        self.locked = True
        self.selected = False      
        self.lock_direction = None
class ControlPointCoreCamber4:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y()+400)
        self.handle_out = QPointF(pos.x(), pos.y()-400)
        self.locked = True
        self.selected = False      
        self.lock_direction = None
class SeamControlPoint:
    def __init__(self, pos: QPointF, handle_in: QPointF | None = None, handle_out: QPointF | None = None):
        self.pos = QPointF(pos)
        self.handle_in = QPointF(handle_in) if handle_in is not None else QPointF(pos.x() - 12.0, pos.y())
        self.handle_out = QPointF(handle_out) if handle_out is not None else QPointF(pos.x() + 12.0, pos.y())
        self.locked = False
        self.selected = False
        self.lock_direction = None
class ControlPointCoreCamberUL1:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x(), pos.y()+10)
        self.handle_out = QPointF(pos.x()-50, pos.y()-50)
        self.locked = False
        self.selected = False        
        self.lock_direction = None
class ControlPointCoreCamberUL2:
    def __init__(self, pos: QPointF):
        self.pos = pos
        self.handle_in = QPointF(pos.x()-50, pos.y()+50)
        self.handle_out = QPointF(pos.x(), pos.y()-10)
        self.locked = False
        self.selected = False        
        self.lock_direction = None
class CosmeticPoint:
    def __init__(self, pos: QPointF):
        self.pos = QPointF(pos)
        self.selected = False
        self.uid = None

# =========================
# Ski Shape Item (INITIALIZATIONS)
# =========================
class SkiShape(QGraphicsItem):
    def __init__(self):
        super().__init__()
        self.points = [                             #Initial Ski Shape Points
            ControlPointTail(QPointF(0, 750)),      #Tail of Ski
            ControlPointMid(QPointF(50, 600)),
            ControlPointMid(QPointF(40, -90)),        #Center of ski, binding setback
            ControlPointMid(QPointF(60, -800)),
            ControlPointTip(QPointF(0, -1000)),     #Tip of Ski
        ]
        self.left_points = self._make_mirrored_edge_points(self.points)
        self.outline_mode = "symmetric"
        self.core_thickness_points = [              #Initial core thickness points
            ControlPointCoreThickness(QPointF(100, 750)),
            ControlPointCoreThickness(QPointF(100, 600)),
            ControlPointCoreThickness(QPointF(115, 200)),
            ControlPointCoreThickness(QPointF(115, -400)),
            ControlPointCoreThickness(QPointF(100, -800)),
            ControlPointCoreThickness(QPointF(100, -1000)),
        ] 
        self.camber_thickness_points = [              #Initial camber shape points
            ControlPointCoreCamber3(QPointF(-300, 800)),
            ControlPointCoreCamberUL1(QPointF(-300, 750)),          #Tail
            ControlPointCoreCamber1(QPointF(-350, 600)),
            ControlPointCoreCamber4(QPointF(-335, -90)),
            ControlPointCoreCamber1(QPointF(-350, -800)),
            ControlPointCoreCamberUL2(QPointF(-300, -1000)),        #Tip
            ControlPointCoreCamber2(QPointF(-300, -1050)),
        ]
        self.cosmetic_points = []
        self.undo_stack = []
        self.redo_stack = []        
        self.move_core_shape(-100)
        self.move_camber_shape(-100)
        self.show_points = False
        self.show_dimensions = False
        self.show_global_coordinates = False
        self.dragging_point = None
        self.drag_type = None
        self.selected_seam_handle = None
        self.show_sidecut_circle = False      
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable, True)
        self.show_3d = False
        self.show_ski_snowboard = False
        self.second_3d_base_to_base = False
        self.second_3d_base_separation_cm = self.get_default_second_3d_base_separation_cm()
        self.restoring_state = False
        self.view_x_scale = 10
        self.view_x_offset = 600
        self.view_y_scale = 10
        self.view_y_offset = 0
        self.view_x_offset2 = 1000
        self.view_y_offset2 = 0
        self.rot_x = 0
        self.rot_y = 0
        self.rot_z = 0
        self.render_3d_mode = "shaded"
        self.ski_color = QColor(180, 40, 40)
        self.background_3d_color = QColor(46, 50, 58, 210)
        self.show_3d_background = True
        self.background_3d_width_px = 750.0
        self.background_3d_height_px = 2000.0
        self.upper_mold_offset_mm = 40.0
        self.mold_hole_count = 4
        self.mold_hole_diameter_mm = 20.0
        self.light_azimuth_deg = -90
        self.light_elevation_deg = -30.0
        self.light_brightness = 1.0
        self.top_graphic_path = ""
        self.base_graphic_path = ""
        self.top_graphic_image = None
        self.base_graphic_image = None
        self.top_graphic_offset_x_px = 0.0
        self.top_graphic_offset_y_px = 0.0
        self.top_graphic_scale_x = 1.0
        self.top_graphic_scale_y = 1.0
        self.base_graphic_offset_x_px = 0.0
        self.base_graphic_offset_y_px = 0.0
        self.base_graphic_scale_x = 1.0
        self.base_graphic_scale_y = 1.0
        self.build_sheet_notes = default_build_sheet_notes()

        # Stiffness plot / sandwich-composite tuning
        self.lower_reinforcement_factor = 1.0
        self.wood_core_stiffness_factor = 1.0
        self.upper_reinforcement_factor = 1.0

        # 3D projection offsets
        self.offset_x = 1275
        self.offset_y = 0

        # Layup view settings
        self.edge_thickness_px = 2.3
        self.sidewall_thickness_px = 7.0
        self.left_sidewall_thickness_px = self.sidewall_thickness_px
        self.edge_inlay_tip_trim_px = 55.0
        self.edge_inlay_tail_trim_px = 55.0
        self.base_edge_corner_min_radius_px = 0.0
        self.include_splitboard_inside_edge = True
        self.minimum_core_thickness_px = 5.0
        self.tip_spacer_length_px = 120.0
        self.tail_spacer_length_px = 120.0
        self.seam_depth_px = 18.0
        self.seam_point_count = 1
        self.seam_point_count = self._normalize_seam_point_count(self.seam_point_count)
        self.tip_seam_point_count = 1
        self.tail_seam_point_count = 1
        self.tip_seam_center = self._build_default_seam_center_point()
        self.tail_seam_center = self._build_default_seam_center_point()
        self.tip_seam_points = self._build_default_seam_points()
        self.tail_seam_points = self._build_default_seam_points()
        self.seam_inner_x_frac = 0.34
        self.seam_inner_y_frac = 1.00
        self.seam_outer_x_frac = 0.72
        self.seam_outer_y_frac = -0.32
        self.seam_lobes = 3  # legacy save-file compatibility
        self.seam_tension = 0.55  # legacy save-file compatibility

        self.show_base_shape = False
        self.show_edge_inlay_shape = False
        self.show_core_shape = False
        self.show_sidewall_shape = False
        self.show_tip_tail_spacers = False
        self.show_sidewall_spacer_shell = False

        self._cache = {}
        self._face_orientation_cache = {}
        self._outline_span_cache = {}
        self._cached_3d_draw_faces_key = None
        self._cached_3d_draw_faces = None
        self.owner_window = None
        self._next_point_uid = 1
        self.relative_point_locks = []
        self.point_circles = []
        self.point_dimensions = []
        self.multi_select_order = []
        self.profile_insert_key = None
        self.left_edge_insert_key = False
        self.selection_box_active = False
        self.selection_box_origin = None
        self.selection_box_current = None
        self.selection_box_additive = False
        self.selection_box_toggle = False
        self.selection_box_zoom = False
        self.zoom_box_key = False
        self.hover_point_uid = None
        self.setAcceptHoverEvents(True)
        self._ensure_point_ids()
        self.model_center_length_cm = 12.5
        self.low_res_3d_edit_mode = True
        self.interaction_3d_active = False
        self._cached_3d_background_center_x = None
        self.low_res_mesh_samples = 24
        self.preview_mesh_samples = 72
        self.full_res_mesh_samples = 120
        self.apply_design_constraints()
    def apply_shape_preset(self, preset_name):
        presets = get_default_shape_presets()
        if preset_name not in presets:
            return

        preset = presets[preset_name]

        self.load_point_set(self.points, preset["edge"])
        self.left_points = self._make_mirrored_edge_points(self.points)
        self.load_point_set(self.core_thickness_points, preset["core"])
        self.load_point_set(self.camber_thickness_points, preset["camber"])

        self.apply_design_constraints()
        self.update()
    def load_point_set(self, target_points, preset_data):
        for p, data in zip(target_points, preset_data):
            p.pos = QPointF(*data["pos"])
            p.handle_in = QPointF(*data["in"])
            p.handle_out = QPointF(*data["out"])
            p.selected = False
            p.locked = data.get("locked", p.locked)
            if hasattr(p, "lock_direction") and "lock_direction" in data:
                p.lock_direction = data["lock_direction"]
    def _clone_edge_point(self, point, mirror_x=False):
        pos = QPointF(point.pos)
        handle_in = QPointF(point.handle_in)
        handle_out = QPointF(point.handle_out)
        if mirror_x:
            pos.setX(-pos.x())
            handle_in.setX(-handle_in.x())
            handle_out.setX(-handle_out.x())
        clone = point.__class__(pos)
        clone.handle_in = handle_in
        clone.handle_out = handle_out
        clone.locked = getattr(point, "locked", False)
        clone.lock_direction = getattr(point, "lock_direction", None)
        clone.uid = None
        clone.selected = False
        return clone
    def _make_mirrored_edge_points(self, points):
        return [self._clone_edge_point(p, mirror_x=True) for p in points]
    def _ensure_left_points(self):
        if not hasattr(self, "left_points") or not self.left_points:
            self.left_points = self._make_mirrored_edge_points(self.points)
    def set_outline_mode(self, mode):
        mode = str(mode).lower()
        if mode not in {"symmetric", "snowboard", "splitboard", "asymmetric"}:
            mode = "symmetric"
        previous_mode = getattr(self, "outline_mode", "symmetric")
        if mode == "asymmetric" and previous_mode != "asymmetric":
            self.left_points = self._make_mirrored_edge_points(self.points)
        self.outline_mode = mode
        self._cache.clear()
        self.update()
    def shift_point_y(self, p, dy):
        p.pos.setY(p.pos.y() + dy)
        p.handle_in.setY(p.handle_in.y() + dy)
        p.handle_out.setY(p.handle_out.y() + dy)
    def set_point_x(self, p, new_x, move_handles=True):
        dx = new_x - p.pos.x()
        p.pos.setX(new_x)
        if move_handles:
            p.handle_in.setX(p.handle_in.x() + dx)
            p.handle_out.setX(p.handle_out.x() + dx)
    def _shift_point_x(self, p, dx):
        if abs(dx) < 1e-9 or p is None:
            return
        p.pos.setX(p.pos.x() + dx)
        if hasattr(p, "handle_in"):
            p.handle_in.setX(p.handle_in.x() + dx)
        if hasattr(p, "handle_out"):
            p.handle_out.setX(p.handle_out.x() + dx)
    def _shift_point_y(self, p, dy):
        if abs(dy) < 1e-9 or p is None:
            return
        p.pos.setY(p.pos.y() + dy)
        if hasattr(p, "handle_in"):
            p.handle_in.setY(p.handle_in.y() + dy)
        if hasattr(p, "handle_out"):
            p.handle_out.setY(p.handle_out.y() + dy)
    def _iter_regular_point_groups(self):
        groups = [self.points]
        if getattr(self, "outline_mode", "symmetric") == "asymmetric":
            self._ensure_left_points()
            groups.append(self.left_points)
        groups.extend([self.core_thickness_points, self.camber_thickness_points])
        return tuple(groups)
    def _iter_regular_points(self):
        for group in self._iter_regular_point_groups():
            for p in group:
                yield p
    def _iter_selectable_points(self):
        for p in self._iter_regular_points():
            yield p
        for p in self.cosmetic_points:
            yield p
    def _get_selected_cosmetic_points(self):
        return [p for p in self.cosmetic_points if getattr(p, "selected", False)]
    def _get_selected_circle_points(self):
        cosmetic = self._get_selected_cosmetic_points()
        if cosmetic:
            return cosmetic
        return [p for p in self._iter_selectable_points() if getattr(p, "selected", False)]
    def _ensure_point_ids(self):
        next_uid = max(1, int(getattr(self, "_next_point_uid", 1)))
        for p in self._iter_selectable_points():
            uid = getattr(p, "uid", None)
            if uid is None:
                p.uid = next_uid
                next_uid += 1
            else:
                try:
                    uid = int(uid)
                except Exception:
                    uid = next_uid
                    next_uid += 1
                p.uid = uid
                next_uid = max(next_uid, uid + 1)
        self._next_point_uid = next_uid
    def _assign_point_uid(self, p):
        self._ensure_point_ids()
        p.uid = int(self._next_point_uid)
        self._next_point_uid += 1
    def _get_point_by_uid(self, uid):
        for p in self._iter_selectable_points():
            if getattr(p, "uid", None) == uid:
                return p
        return None
    def _get_selected_regular_points(self):
        return [p for p in self._iter_selectable_points() if getattr(p, "selected", False)]
    def _clear_regular_point_selection(self):
        for p in self._iter_selectable_points():
            p.selected = False
            if hasattr(p, "selected_handle_kind"):
                p.selected_handle_kind = None
        self.multi_select_order = []
    def _sync_multi_select_order(self):
        selected_ids = {getattr(p, "uid", None) for p in self._get_selected_regular_points()}
        self.multi_select_order = [uid for uid in self.multi_select_order if uid in selected_ids]
        for p in self._get_selected_regular_points():
            uid = getattr(p, "uid", None)
            if uid is not None and uid not in self.multi_select_order:
                self.multi_select_order.append(uid)
        while len(self.multi_select_order) > 3:
            uid = self.multi_select_order.pop(0)
            point = self._get_point_by_uid(uid)
            if point is not None:
                point.selected = False
    def _select_regular_point(self, point, additive=False):
        if point is None:
            return
        self._ensure_point_ids()
        if not additive:
            self._clear_regular_point_selection()
            point.selected = True
            point.selected_handle_kind = None
            self.multi_select_order = [point.uid]
            return
        uid = getattr(point, "uid", None)
        if uid is None:
            self._assign_point_uid(point)
            uid = point.uid
        if point.selected:
            point.selected = False
            point.selected_handle_kind = None
            self.multi_select_order = [existing for existing in self.multi_select_order if existing != uid]
            return
        point.selected = True
        point.selected_handle_kind = None
        self.multi_select_order = [existing for existing in self.multi_select_order if existing != uid]
        self.multi_select_order.append(uid)
        while len(self.multi_select_order) > 3:
            removed_uid = self.multi_select_order.pop(0)
            removed_point = self._get_point_by_uid(removed_uid)
            if removed_point is not None:
                removed_point.selected = False
    def _prune_relative_point_locks(self):
        self._ensure_point_ids()
        valid_ids = {getattr(p, "uid", None) for p in self._iter_selectable_points()}
        cleaned = []
        seen = set()
        for entry in getattr(self, "relative_point_locks", []):
            if not isinstance(entry, dict):
                continue
            axis = entry.get("axis")
            a_uid = entry.get("a")
            b_uid = entry.get("b")
            if axis not in ("vertical", "horizontal"):
                continue
            if a_uid not in valid_ids or b_uid not in valid_ids or a_uid == b_uid:
                continue
            key = tuple(sorted((int(a_uid), int(b_uid))))
            if key in seen:
                continue
            seen.add(key)
            cleaned.append({"a": int(a_uid), "b": int(b_uid), "axis": axis})
        self.relative_point_locks = cleaned
    def _set_relative_point_lock(self, point_a, point_b, axis):
        if point_a is None or point_b is None or point_a is point_b:
            return False
        self._ensure_point_ids()
        a_uid = getattr(point_a, "uid", None)
        b_uid = getattr(point_b, "uid", None)
        if a_uid is None:
            self._assign_point_uid(point_a)
            a_uid = point_a.uid
        if b_uid is None:
            self._assign_point_uid(point_b)
            b_uid = point_b.uid

        pair_ids = {int(a_uid), int(b_uid)}
        axis = "vertical" if axis == "vertical" else "horizontal"
        existing_same_axis = False
        new_entries = []
        for entry in self.relative_point_locks:
            entry_ids = {int(entry.get("a")), int(entry.get("b"))} if entry.get("a") is not None and entry.get("b") is not None else set()
            if entry_ids == pair_ids:
                if entry.get("axis") == axis:
                    existing_same_axis = True
                continue
            if a_uid in entry_ids or b_uid in entry_ids:
                continue
            new_entries.append(entry)

        if not existing_same_axis:
            new_entries.append({"a": int(a_uid), "b": int(b_uid), "axis": axis})

        self.relative_point_locks = new_entries
        self._prune_relative_point_locks()
        return not existing_same_axis
    def _circle_from_points(self, p1, p2, p3):
        x1, y1 = p1.x(), p1.y()
        x2, y2 = p2.x(), p2.y()
        x3, y3 = p3.x(), p3.y()
        d = 2.0 * (x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2))
        if abs(d) < 1e-9:
            return None
        ux = ((x1 * x1 + y1 * y1) * (y2 - y3) + (x2 * x2 + y2 * y2) * (y3 - y1) + (x3 * x3 + y3 * y3) * (y1 - y2)) / d
        uy = ((x1 * x1 + y1 * y1) * (x3 - x2) + (x2 * x2 + y2 * y2) * (x1 - x3) + (x3 * x3 + y3 * y3) * (x2 - x1)) / d
        center = QPointF(ux, uy)
        radius = math.hypot(x1 - ux, y1 - uy)
        if radius <= 1e-9 or not math.isfinite(radius):
            return None
        return center, radius
    def _prune_point_circles(self):
        self._ensure_point_ids()
        valid_ids = {getattr(p, "uid", None) for p in self._iter_selectable_points()}
        cleaned = []
        seen = set()
        for entry in getattr(self, "point_circles", []):
            if not isinstance(entry, dict):
                continue
            ids = entry.get("points")
            if not isinstance(ids, (list, tuple)) or len(ids) != 3:
                continue
            try:
                ids = tuple(sorted(int(v) for v in ids))
            except Exception:
                continue
            if len(set(ids)) != 3:
                continue
            if any(v not in valid_ids for v in ids):
                continue
            if ids in seen:
                continue
            seen.add(ids)
            cleaned.append({"points": list(ids)})
        self.point_circles = cleaned
    def _toggle_point_circle(self, points):
        if len(points) != 3:
            return False
        self._ensure_point_ids()
        ids = []
        for p in points:
            uid = getattr(p, "uid", None)
            if uid is None:
                self._assign_point_uid(p)
                uid = p.uid
            ids.append(int(uid))
        key = tuple(sorted(ids))
        self._prune_point_circles()
        existing = {tuple(sorted(int(v) for v in entry.get("points", []))) for entry in self.point_circles}
        if key in existing:
            self.point_circles = [entry for entry in self.point_circles if tuple(sorted(int(v) for v in entry.get("points", []))) != key]
            return False
        self.point_circles.append({"points": list(key)})
        self._prune_point_circles()
        return True
    def _get_circle_entries(self):
        self._prune_point_circles()
        entries = []
        for entry in self.point_circles:
            pts = [self._get_point_by_uid(uid) for uid in entry.get("points", [])]
            if any(p is None for p in pts):
                continue
            circle = self._circle_from_points(pts[0].pos, pts[1].pos, pts[2].pos)
            if circle is None:
                continue
            center, radius = circle
            entries.append((pts, center, radius))
        return entries
    def _distance_between_points(self, point_a, point_b):
        if point_a is None or point_b is None:
            return 0.0
        return math.hypot(point_b.pos.x() - point_a.pos.x(), point_b.pos.y() - point_a.pos.y())
    def _prune_point_dimensions(self):
        self._ensure_point_ids()
        valid_ids = {getattr(p, "uid", None) for p in self._iter_selectable_points()}
        cleaned = []
        seen = set()
        for entry in getattr(self, "point_dimensions", []):
            if not isinstance(entry, dict):
                continue
            ids = entry.get("points")
            if not isinstance(ids, (list, tuple)) or len(ids) != 2:
                continue
            try:
                ids = tuple(sorted(int(v) for v in ids))
                distance_px = float(entry.get("distance_px", 0.0))
            except Exception:
                continue
            if len(set(ids)) != 2:
                continue
            if any(v not in valid_ids for v in ids):
                continue
            if distance_px <= 1e-9 or not math.isfinite(distance_px):
                continue
            if ids in seen:
                continue
            seen.add(ids)
            cleaned.append({"points": list(ids), "distance_px": distance_px})
        self.point_dimensions = cleaned
    def _toggle_point_dimension(self, points):
        if len(points) != 2:
            return False
        self._ensure_point_ids()
        ids = []
        for p in points:
            uid = getattr(p, "uid", None)
            if uid is None:
                self._assign_point_uid(p)
                uid = p.uid
            ids.append(int(uid))
        key = tuple(sorted(ids))
        distance_px = self._distance_between_points(points[0], points[1])
        self._prune_point_dimensions()
        existing = {tuple(sorted(int(v) for v in entry.get("points", []))) for entry in self.point_dimensions}
        if key in existing:
            self.point_dimensions = [entry for entry in self.point_dimensions if tuple(sorted(int(v) for v in entry.get("points", []))) != key]
            return False
        self.point_dimensions.append({"points": list(key), "distance_px": distance_px})
        self._prune_point_dimensions()
        return True
    def _get_dimension_entries(self):
        self._prune_point_dimensions()
        entries = []
        for entry in self.point_dimensions:
            pts = [self._get_point_by_uid(uid) for uid in entry.get("points", [])]
            if any(p is None for p in pts):
                continue
            distance_px = float(entry.get("distance_px", self._distance_between_points(pts[0], pts[1])))
            entries.append((pts[0], pts[1], distance_px))
        return entries
    def _move_point_by_delta(self, point, delta):
        if point is None:
            return
        if isinstance(point, CosmeticPoint):
            point.pos = QPointF(point.pos + delta)
            return
        point.pos += delta
        point.handle_in += delta
        point.handle_out += delta
    def _set_regular_handle_from_pos(self, point, handle_kind, pos):
        if point is None or handle_kind not in ("handle_in", "handle_out"):
            return False
        pos = QPointF(pos)
        if handle_kind == "handle_in":
            point.handle_in = pos
            if point.locked:
                dx = point.pos.x() - pos.x()
                dy = point.pos.y() - pos.y()
                point.handle_out = QPointF(point.pos.x() + dx, point.pos.y() + dy)
            if point.lock_direction == "vertical":
                dy = point.pos.y() - pos.y()
                point.handle_out = QPointF(point.pos.x(), point.pos.y() + dy)
                point.handle_in = QPointF(point.pos.x(), point.pos.y() - dy)
            if point.lock_direction == "horizontal":
                dx = point.pos.x() - pos.x()
                point.handle_out = QPointF(point.pos.x() + dx, point.pos.y())
                point.handle_in = QPointF(point.pos.x() - dx, point.pos.y())
            return True

        point.handle_out = pos
        if point.locked:
            dx = point.pos.x() - pos.x()
            dy = point.pos.y() - pos.y()
            point.handle_in = QPointF(point.pos.x() + dx, point.pos.y() + dy)
        if point.lock_direction == "vertical":
            dy = point.pos.y() - pos.y()
            point.handle_out = QPointF(point.pos.x(), point.pos.y() - dy)
            point.handle_in = QPointF(point.pos.x(), point.pos.y() + dy)
        if point.lock_direction == "horizontal":
            dx = point.pos.x() - pos.x()
            point.handle_out = QPointF(point.pos.x() - dx, point.pos.y())
            point.handle_in = QPointF(point.pos.x() + dx, point.pos.y())
        return True
    def _nudge_selected_seam_handle(self, delta):
        if not self.selected_seam_handle:
            return False
        seam_name, index, kind = self.selected_seam_handle
        points = self.tip_seam_points if seam_name == "tip" else self.tail_seam_points
        if index == -1:
            point = self.tip_seam_center if seam_name == "tip" else self.tail_seam_center
        elif 0 <= index < len(points):
            point = points[index]
        else:
            return False
        if kind == "center_point":
            world_pos = self._seam_local_to_world(seam_name, point.pos) + delta
        elif kind == "center_handle_in":
            world_pos = self._seam_local_to_world(seam_name, point.handle_in) + delta
        elif kind == "center_handle_out":
            world_pos = self._seam_local_to_world(seam_name, point.handle_out) + delta
        elif kind == "point":
            world_pos = self._seam_local_to_world(seam_name, point.pos) + delta
        elif kind == "handle_in":
            world_pos = self._seam_local_to_world(seam_name, point.handle_in) + delta
        elif kind == "handle_out":
            world_pos = self._seam_local_to_world(seam_name, point.handle_out) + delta
        else:
            return False
        self._set_seam_handle_from_pos(seam_name, kind, index, world_pos)
        return True
    def _nudge_selected_points(self, delta):
        selected_points = self._get_selected_regular_points()
        moved = False
        if not selected_points and self._nudge_selected_seam_handle(delta):
            return True
        if not selected_points:
            return False
        for point in selected_points:
            point_delta = QPointF(delta)
            handle_kind = getattr(point, "selected_handle_kind", None)
            if handle_kind == "handle_in" and hasattr(point, "handle_in"):
                self._set_regular_handle_from_pos(point, "handle_in", point.handle_in + point_delta)
            elif handle_kind == "handle_out" and hasattr(point, "handle_out"):
                self._set_regular_handle_from_pos(point, "handle_out", point.handle_out + point_delta)
            else:
                if point in (self.points[0], self.points[-1]):
                    point_delta.setX(0.0)
                self._move_point_by_delta(point, point_delta)
            moved = True
        if self._nudge_selected_seam_handle(delta):
            moved = True
        if not moved:
            return False
        previous_dragging_point = self.dragging_point
        self.dragging_point = selected_points[0]
        self.apply_design_constraints()
        self.dragging_point = previous_dragging_point
        self._cache.clear()
        self.update()
        owner = getattr(self, "owner_window", None)
        if owner is not None and hasattr(owner, "refresh_cnc_after_shape_edit"):
            owner.refresh_cnc_after_shape_edit()
        return True
    def _apply_point_distance_locks(self, preferred_uid=None):
        self._prune_point_dimensions()
        for entry in self.point_dimensions:
            point_a = self._get_point_by_uid(entry["points"][0])
            point_b = self._get_point_by_uid(entry["points"][1])
            if point_a is None or point_b is None:
                continue
            if preferred_uid == getattr(point_b, "uid", None):
                leader, follower = point_b, point_a
            else:
                leader, follower = point_a, point_b
            dx = follower.pos.x() - leader.pos.x()
            dy = follower.pos.y() - leader.pos.y()
            current = math.hypot(dx, dy)
            target = float(entry.get("distance_px", current))
            if target <= 1e-9 or not math.isfinite(target):
                continue
            if current <= 1e-9:
                ux, uy = 1.0, 0.0
            else:
                ux, uy = dx / current, dy / current
            desired = QPointF(leader.pos.x() + ux * target, leader.pos.y() + uy * target)
            delta = desired - follower.pos
            if abs(delta.x()) > 1e-9 or abs(delta.y()) > 1e-9:
                self._move_point_by_delta(follower, delta)
    def _apply_relative_point_locks(self, preferred_uid=None):
        self._prune_relative_point_locks()
        for entry in self.relative_point_locks:
            point_a = self._get_point_by_uid(entry["a"])
            point_b = self._get_point_by_uid(entry["b"])
            if point_a is None or point_b is None:
                continue
            if preferred_uid == getattr(point_b, "uid", None):
                leader, follower = point_b, point_a
            else:
                leader, follower = point_a, point_b
            if entry["axis"] == "vertical":
                self._shift_point_x(follower, leader.pos.x() - follower.pos.x())
            elif entry["axis"] == "horizontal":
                self._shift_point_y(follower, leader.pos.y() - follower.pos.y())
    def _current_full_outline_polygon_cm_uncached(self, samples=900):
        right_path = self.build_edge_path()
        left_path = self.build_inner_or_left_edge_path()
        samples = max(80, int(samples))
        right = [
            (-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM)
            for p in (right_path.pointAtPercent(i / samples) for i in range(samples + 1))
        ]
        left = [
            (-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM)
            for p in (left_path.pointAtPercent(i / samples) for i in range(samples + 1))
        ]
        pts = self._dedupe_polygon_points(right + left)
        if len(pts) >= 3 and self._polygon_signed_area_xy(pts) < 0.0:
            pts.reverse()
        return pts
    def _current_outline_has_dovetail(self, outline):
        if len(outline) < 3:
            return False
        xs = [p[0] for p in outline]
        min_x = min(xs)
        max_x = max(xs)
        if max_x - min_x <= 1e-6:
            return False
        stations = self._dovetail_scan_stations(outline, min_x, max_x, 220)
        return any(len(self._station_spans_from_outline(outline, x_cm)) > 1 for x_cm in stations)
    def _current_dovetail_length_y_bounds(self):
        key = self._cache_key("dovetail_length_y_bounds")
        if key in self._cache:
            return self._cache[key]
        outline = self._current_full_outline_polygon_cm_uncached()
        xs = [p[0] for p in outline]
        if not xs:
            self._cache[key] = None
            return None
        min_x = min(xs)
        max_x = max(xs)
        if not self._current_outline_has_dovetail(outline):
            endpoint_tail_x = -float(self.points[0].pos.y()) / PIXELS_PER_CM
            endpoint_tip_x = -float(self.points[-1].pos.y()) / PIXELS_PER_CM
            endpoint_min_x = min(endpoint_tail_x, endpoint_tip_x)
            endpoint_max_x = max(endpoint_tail_x, endpoint_tip_x)
            if min_x >= endpoint_min_x - 0.05 and max_x <= endpoint_max_x + 0.05:
                self._cache[key] = None
                return None
        bounds = (-min_x * PIXELS_PER_CM, -max_x * PIXELS_PER_CM)
        self._cache[key] = bounds
        return bounds
    def apply_design_constraints(self):
        if len(self.points) < 2:
            return

        # Align core thickness to the full base/outline length when a dovetail
        # exists, so the 3D thickness profile reaches the split tip/tail ends.
        if len(self.core_thickness_points) >= 2:
            tail_y = self.points[0].pos.y()
            tip_y = self.points[-1].pos.y()
            dovetail_bounds = self._current_dovetail_length_y_bounds()
            if dovetail_bounds is not None:
                tail_y, tip_y = dovetail_bounds
            self.core_thickness_points[0].pos.setY(tail_y)
            self.core_thickness_points[-1].pos.setY(tip_y)

        # Keep the camber profile taller than the ski using the second point in from each end.
        if len(self.camber_thickness_points) >= 4:
            ski_tail_y = self.points[0].pos.y()
            ski_tip_y = self.points[-1].pos.y()
            bottom = self.camber_thickness_points[1]
            top = self.camber_thickness_points[-2]

            min_extra = 0

            if bottom.pos.y() <= ski_tail_y:
                self.shift_point_y(bottom, (ski_tail_y - bottom.pos.y()) + min_extra)

            if top.pos.y() >= ski_tip_y:
                self.shift_point_y(top, (ski_tip_y - top.pos.y()) - min_extra)

            ski_length = ski_tail_y - ski_tip_y
            camber_length = bottom.pos.y() - top.pos.y()
            if camber_length <= ski_length:
                grow = ((ski_length - camber_length) / 2.0) + min_extra
                self.shift_point_y(bottom, grow)
                self.shift_point_y(top, -grow)

        # Keep the camber end caps outside their adjacent profile points.
        if len(self.camber_thickness_points) >= 2:
            endpoint_gap = 1.0
            lower_end = self.camber_thickness_points[0]
            lower_adjacent = self.camber_thickness_points[1]
            upper_end = self.camber_thickness_points[-1]
            upper_adjacent = self.camber_thickness_points[-2]

            if lower_end.pos.y() <= lower_adjacent.pos.y() + endpoint_gap:
                self.shift_point_y(lower_end, (lower_adjacent.pos.y() + endpoint_gap) - lower_end.pos.y())

            if upper_end.pos.y() >= upper_adjacent.pos.y() - endpoint_gap:
                self.shift_point_y(upper_end, (upper_adjacent.pos.y() - endpoint_gap) - upper_end.pos.y())

        preferred_uid = getattr(self.dragging_point, 'uid', None)
        self._apply_relative_point_locks(preferred_uid)
        self._apply_point_distance_locks(preferred_uid)
    def _scale_points_xy(self, points, center_x, center_y, factor):
        for p in points:
            p.pos.setX(center_x + (p.pos.x() - center_x) * factor)
            p.pos.setY(center_y + (p.pos.y() - center_y) * factor)
            p.handle_in.setX(center_x + (p.handle_in.x() - center_x) * factor)
            p.handle_in.setY(center_y + (p.handle_in.y() - center_y) * factor)
            p.handle_out.setX(center_x + (p.handle_out.x() - center_x) * factor)
            p.handle_out.setY(center_y + (p.handle_out.y() - center_y) * factor)
    def _points_center_x(self, points):
        if not points:
            return 0.0
        xs = [p.pos.x() for p in points]
        return (min(xs) + max(xs)) / 2.0
    def set_overall_length_cm(self, length_cm):
        if length_cm <= 0 or len(self.points) < 2:
            return
        tail_y = self.points[0].pos.y()
        tip_y = self.points[-1].pos.y()
        current_length_px = tail_y - tip_y
        target_length_px = length_cm * PIXELS_PER_CM
        if current_length_px <= 0:
            return
        factor = target_length_px / current_length_px
        if abs(factor - 1.0) < 1e-9:
            return

        center_y = (tail_y + tip_y) / 2.0
        self._scale_points_xy(self.points, self._points_center_x(self.points), center_y, factor)
        self._scale_points_xy(self.core_thickness_points, self._points_center_x(self.core_thickness_points), center_y, factor)
        self._scale_points_xy(self.camber_thickness_points, self._points_center_x(self.camber_thickness_points), center_y, factor)

        #self.edge_thickness_px *= factor
        #self.sidewall_thickness_px *= factor
        self.edge_inlay_tip_trim_px *= factor
        self.edge_inlay_tail_trim_px *= factor
        self.base_edge_corner_min_radius_px *= factor
        self.tip_spacer_length_px *= factor
        self.tail_spacer_length_px *= factor
        self.seam_depth_px *= factor
        self._scale_seam_points([self.tip_seam_center], factor)
        self._scale_seam_points([self.tail_seam_center], factor)
        self._scale_seam_points(self.tip_seam_points, factor)
        self._scale_seam_points(self.tail_seam_points, factor)

        self._prune_relative_point_locks()
        self._prune_point_circles()
        for entry in self.point_dimensions:
            if isinstance(entry, dict) and "distance_px" in entry:
                entry["distance_px"] = float(entry["distance_px"])
            self._prune_point_dimensions()
        self.apply_design_constraints()
        self._cache.clear()
        self.prepareGeometryChange()
        self.update()
    def get_length(self):
        if len(self.points) < 2:
            return 0.0
        tail_y = self.points[0].pos.y()
        tip_y = self.points[-1].pos.y()
        return abs(tail_y - tip_y) / PIXELS_PER_CM
    def get_startup_values(self):
        return {
            "overall_length_cm": self.get_length(),
            #"edge_thickness_px": self.edge_thickness_px,
            #"sidewall_thickness_px": self.sidewall_thickness_px,
            #"edge_inlay_tip_trim_px": self.edge_inlay_tip_trim_px,
            "edge_inlay_tail_trim_px": self.edge_inlay_tail_trim_px,
            "tip_spacer_length_px": self.tip_spacer_length_px,
            "tail_spacer_length_px": self.tail_spacer_length_px,
        }
    def apply_startup_values(self, values):
        if not values:
            return
        overall_length_cm = float(values.get("overall_length_cm", self.get_length()))
        self.edge_thickness_px = float(values.get("edge_thickness_px", self.edge_thickness_px))
        self.sidewall_thickness_px = float(values.get("sidewall_thickness_px", self.sidewall_thickness_px))
        self.left_sidewall_thickness_px = float(values.get("left_sidewall_thickness_px", getattr(self, "left_sidewall_thickness_px", self.sidewall_thickness_px)))
        self.edge_inlay_tip_trim_px = float(values.get("edge_inlay_tip_trim_px", self.edge_inlay_tip_trim_px))
        self.edge_inlay_tail_trim_px = float(values.get("edge_inlay_tail_trim_px", self.edge_inlay_tail_trim_px))
        self.base_edge_corner_min_radius_px = float(values.get("base_edge_corner_min_radius_px", values.get("edge_inlay_min_radius_px", self.base_edge_corner_min_radius_px)))
        self.tip_spacer_length_px = float(values.get("tip_spacer_length_px", self.tip_spacer_length_px))
        self.tail_spacer_length_px = float(values.get("tail_spacer_length_px", self.tail_spacer_length_px))
        self.set_overall_length_cm(overall_length_cm)
        self.apply_design_constraints()
        self._cache.clear()
        self.prepareGeometryChange()
        self.update()
    def get_core_trim_boundaries_y(self, include_dovetail_bounds=False):
        tail_y = self.points[0].pos.y()
        tip_y = self.points[-1].pos.y()
        if include_dovetail_bounds:
            dovetail_bounds = self._current_dovetail_length_y_bounds()
            if dovetail_bounds is not None:
                tail_y, tip_y = dovetail_bounds
        core_tip_start_y = tip_y + max(0.0, self.tip_spacer_length_px)
        core_tail_end_y = tail_y - max(0.0, self.tail_spacer_length_px)
        if core_tail_end_y < core_tip_start_y:
            mid_y = (tail_y + tip_y) / 2.0
            core_tip_start_y = mid_y
            core_tail_end_y = mid_y
        return tip_y, tail_y, core_tip_start_y, core_tail_end_y
    def get_core_profile_left_x(self):
        if len(self.core_thickness_points) < 2:
            return 0.0
        return min(p.pos.x() for p in self.core_thickness_points) - max(1.0, float(getattr(self, "minimum_core_thickness_px", 5.0)))

    def boundingRect(self):
        return QRectF(-3000, -4000, 5000, 8000)
    # Build ski right edge path
    def build_edge_path(self):
        path = QPainterPath()
        if len(self.points) < 2:
            return path
        path.moveTo(self.points[0].pos)
        for i in range(len(self.points) - 1):
            p0 = self.points[i]
            p1 = self.points[i + 1]
            path.cubicTo(
                p0.handle_out,
                p1.handle_in,
                p1.pos
            )
        return path
    # Build mirrored left edge path
    def build_mirrored_edge_path(self):

        path = QPainterPath()

        last = self.points[-1]
        path.moveTo(QPointF(-last.pos.x(), last.pos.y()))

        for i in range(len(self.points) - 1, 0, -1):

            p0 = self.points[i]
            p1 = self.points[i - 1]

            path.cubicTo(
                QPointF(-p0.handle_in.x(), p0.handle_in.y()),
                QPointF(-p1.handle_out.x(), p1.handle_out.y()),
                QPointF(-p1.pos.x(), p1.pos.y())
            )

        return path
    def build_centerline_edge_path(self):
        path = QPainterPath()
        if len(self.points) < 2:
            return path
        last = self.points[-1]
        first = self.points[0]
        path.moveTo(QPointF(0.0, last.pos.y()))
        path.lineTo(QPointF(0.0, first.pos.y()))
        return path
    def build_asymmetric_left_edge_path(self):
        self._ensure_left_points()
        path = QPainterPath()
        if len(self.left_points) < 2:
            return self.build_mirrored_edge_path()
        last = self.left_points[-1]
        path.moveTo(last.pos)
        for i in range(len(self.left_points) - 1, 0, -1):
            p0 = self.left_points[i]
            p1 = self.left_points[i - 1]
            path.cubicTo(
                p0.handle_in,
                p1.handle_out,
                p1.pos
            )
        return path
    def build_inner_or_left_edge_path(self):
        mode = getattr(self, "outline_mode", "symmetric")
        if mode == "splitboard":
            return self.build_centerline_edge_path()
        if mode == "asymmetric":
            return self.build_asymmetric_left_edge_path()
        return self.build_mirrored_edge_path()
    # Full ski shape
    def build_full_shape(self):

        full = QPainterPath()
        full.addPath(self.build_edge_path())
        full.connectPath(self.build_inner_or_left_edge_path())
        full.closeSubpath()

        return full
    # Second Ski 
    def get_leftmost_x(self):

        return self.build_full_shape().boundingRect().left()
    def build_second_ski_shape(self, gap_px=10.0):
        path = self.build_full_shape()
        if path.isEmpty():
            return path
        bounds = path.boundingRect()
        transform = QTransform()
        if getattr(self, "outline_mode", "symmetric") == "snowboard":
            transform.translate(2.0 * bounds.right() + float(gap_px), 0.0)
        else:
            transform.translate(2.0 * bounds.left() - float(gap_px), 0.0)
        transform.scale(-1.0, 1.0)
        return transform.map(path)
    def build_second_ski(self):
        leftmost_x = min([-p.x() for p in pts])  # mirrored side
        second_ski_offset = leftmost_x - 30
    # Core Thickness Shape     
    def build_core_curve(self):

        path = QPainterPath()

        if len(self.core_thickness_points) < 2:
            return path

        path.moveTo(self.core_thickness_points[0].pos)

        for i in range(len(self.core_thickness_points)-1):

            p1 = self.core_thickness_points[i]
            p2 = self.core_thickness_points[i+1]

            path.cubicTo(
                p1.handle_out,
                p2.handle_in,
                p2.pos
            )
        return path
    def move_core_shape(self, dx):
        for p in self.core_thickness_points:
            p.pos.setX(p.pos.x() + dx)
            p.handle_in.setX(p.handle_in.x() + dx)
            p.handle_out.setX(p.handle_out.x() + dx)
    # Camber Thickness Shape     
    def build_camber_curve(self):
        path = QPainterPath()
        if len(self.camber_thickness_points) < 2:
            return path
        path.moveTo(self.camber_thickness_points[0].pos)
        for i in range(len(self.camber_thickness_points)-1):
            p1 = self.camber_thickness_points[i]
            p2 = self.camber_thickness_points[i+1]
            path.cubicTo(
                p1.handle_out,
                p2.handle_in,
                p2.pos
            )
        return path
    def get_upper_mold_flat_x(self):
        offset_pts = self._upper_mold_offset_curve_points()
        if not offset_pts:
            return 0.0
        mold_width_px = 40.0 * PIXELS_PER_MM
        return max(pt.x() for pt in offset_pts) + mold_width_px
    def _upper_mold_offset_curve_points(self, samples=240):
        curve = self.build_camber_curve()
        if curve.isEmpty():
            return []
        gap_px = max(0.0, float(getattr(self, "upper_mold_offset_mm", 40.0))) * PIXELS_PER_MM
        source = [curve.pointAtPercent(i / max(1, samples)) for i in range(samples + 1)]
        if len(source) < 2:
            return source
        offset_pts = []
        for i, pt in enumerate(source):
            if i == 0:
                prev_pt = pt
                next_pt = source[i + 1]
            elif i == len(source) - 1:
                prev_pt = source[i - 1]
                next_pt = pt
            else:
                prev_pt = source[i - 1]
                next_pt = source[i + 1]
            dx = next_pt.x() - prev_pt.x()
            dy = next_pt.y() - prev_pt.y()
            length = math.hypot(dx, dy)
            if length <= 1e-9:
                nx, ny = 1.0, 0.0
            else:
                nx = -dy / length
                ny = dx / length
                if nx < 0.0:
                    nx = -nx
                    ny = -ny
            offset_pts.append(QPointF(pt.x() + nx * gap_px, pt.y() + ny * gap_px))
        return offset_pts
    def build_upper_mold_path(self):
        if len(self.camber_thickness_points) < 2:
            return QPainterPath()
        offset_pts = self._upper_mold_offset_curve_points()
        if not offset_pts:
            return QPainterPath()
        flat_x = self.get_upper_mold_flat_x()
        path = QPainterPath()
        path.moveTo(offset_pts[0])
        for pt in offset_pts[1:]:
            path.lineTo(pt)
        path.lineTo(QPointF(flat_x, offset_pts[-1].y()))
        path.lineTo(QPointF(flat_x, offset_pts[0].y()))
        path.closeSubpath()
        return path
    def _mold_hole_centers(self, upper=False):
        count = max(1, min(10, int(getattr(self, "mold_hole_count", 4))))
        curve = self.build_camber_curve()
        if curve.isEmpty():
            return []
        flat_x = self.get_upper_mold_flat_x() if upper else min(p.pos.x() for p in self.camber_thickness_points) - 50
        centers = []
        for i in range(count):
            t = (i + 1.0) / (count + 1.0)
            if upper:
                offset_pts = self._upper_mold_offset_curve_points()
                if not offset_pts:
                    continue
                curve_pt = offset_pts[min(len(offset_pts) - 1, max(0, int(round(t * (len(offset_pts) - 1)))))]
            else:
                curve_pt = curve.pointAtPercent(t)
            centers.append(QPointF((curve_pt.x() + flat_x) * 0.5, curve_pt.y()))
        return centers
    def draw_mold_holes(self, painter, include_upper=True):
        diameter_px = max(1.0, float(getattr(self, "mold_hole_diameter_mm", 20.0)) * PIXELS_PER_MM)
        radius = diameter_px * 0.5
        painter.save()
        painter.setPen(QPen(QColor(88, 54, 28), 1.4))
        painter.setBrush(QBrush(QColor(28, 22, 18, 230)))
        mold_sides = (False, True) if include_upper else (False,)
        for upper in mold_sides:
            for center in self._mold_hole_centers(upper=upper):
                painter.drawEllipse(center, radius, radius)
        painter.restore()
    def move_camber_shape(self, dx):
        for p in self.camber_thickness_points:
            p.pos.setX(p.pos.x() + dx)
            p.handle_in.setX(p.handle_in.x() + dx)
            p.handle_out.setX(p.handle_out.x() + dx)
    def load_top_graphic(self, filename):
        image = QImage(filename)
        if image.isNull():
            return False
        self.top_graphic_path = filename
        self.top_graphic_image = image
        self.update()
        return True
    def load_base_graphic(self, filename):
        image = QImage(filename)
        if image.isNull():
            return False
        self.base_graphic_path = filename
        self.base_graphic_image = image
        self.update()
        return True
    def _get_2d_graphic_settings(self, graphic_kind):
        if str(graphic_kind).lower() == "base":
            return (
                float(getattr(self, "base_graphic_offset_x_px", 0.0)),
                float(getattr(self, "base_graphic_offset_y_px", 0.0)),
                max(0.01, float(getattr(self, "base_graphic_scale_x", getattr(self, "base_graphic_scale", 1.0)))),
                max(0.01, float(getattr(self, "base_graphic_scale_y", getattr(self, "base_graphic_scale", 1.0)))),
            )
        return (
            float(getattr(self, "top_graphic_offset_x_px", 0.0)),
            float(getattr(self, "top_graphic_offset_y_px", 0.0)),
            max(0.01, float(getattr(self, "top_graphic_scale_x", getattr(self, "top_graphic_scale", 1.0)))),
            max(0.01, float(getattr(self, "top_graphic_scale_y", getattr(self, "top_graphic_scale", 1.0)))),
        )

    def _draw_graphic_clipped(self, painter, clip_path, image, graphic_kind="top"):
        if image is None or image.isNull():
            return
        bounds = clip_path.boundingRect()
        if bounds.isEmpty():
            return
        offset_x_px, offset_y_px, scale_x, scale_y = self._get_2d_graphic_settings(graphic_kind)
        scaled_w = bounds.width() * scale_x
        scaled_h = bounds.height() * scale_y
        target = QRectF(
            bounds.center().x() - scaled_w / 2.0 + offset_x_px,
            bounds.center().y() - scaled_h / 2.0 + offset_y_px,
            scaled_w,
            scaled_h,
        )
        painter.save()
        painter.setClipPath(clip_path)
        painter.drawImage(target, image)
        painter.restore()

    # Save / Load
    def serialize(self):

        def pack(points):
            arr = []
            for p in points:
                entry = {
                    "pos": (p.pos.x(), p.pos.y()),
                    "type": p.__class__.__name__,
                    "uid": getattr(p, "uid", None),
                    "selected": bool(getattr(p, "selected", False)),
                }
                if hasattr(p, "handle_in"):
                    entry["handle_in"] = (p.handle_in.x(), p.handle_in.y())
                if hasattr(p, "handle_out"):
                    entry["handle_out"] = (p.handle_out.x(), p.handle_out.y())
                if hasattr(p, "locked"):
                    entry["locked"] = p.locked
                arr.append(entry)
            return arr

        return {
            "edge": pack(self.points),
            "left_edge": pack(getattr(self, "left_points", [])),
            "core": pack(self.core_thickness_points),
            "camber": pack(self.camber_thickness_points),
            "cosmetic": pack(self.cosmetic_points),
            "layup": {
                "outline_mode": getattr(self, "outline_mode", "symmetric"),
                "edge_thickness_px": self.edge_thickness_px,
                "sidewall_thickness_px": self.sidewall_thickness_px,
                "left_sidewall_thickness_px": getattr(self, "left_sidewall_thickness_px", self.sidewall_thickness_px),
                "edge_inlay_tip_trim_px": self.edge_inlay_tip_trim_px,
                "edge_inlay_tail_trim_px": self.edge_inlay_tail_trim_px,
                "base_edge_corner_min_radius_px": getattr(self, "base_edge_corner_min_radius_px", 0.0),
                "include_splitboard_inside_edge": bool(getattr(self, "include_splitboard_inside_edge", True)),
                "minimum_core_thickness_px": self.minimum_core_thickness_px,
                "tip_spacer_length_px": self.tip_spacer_length_px,
                "tail_spacer_length_px": self.tail_spacer_length_px,
                "seam_depth_px": self.seam_depth_px,
                "seam_point_count": self.seam_point_count,
                "tip_seam_point_count": getattr(self, "tip_seam_point_count", self.seam_point_count),
                "tail_seam_point_count": getattr(self, "tail_seam_point_count", self.seam_point_count),
                "seam_inner_x_frac": self.seam_inner_x_frac,
                "seam_inner_y_frac": self.seam_inner_y_frac,
                "seam_outer_x_frac": self.seam_outer_x_frac,
                "seam_outer_y_frac": self.seam_outer_y_frac,
                "tip_seam_center": self._serialize_seam_point(self.tip_seam_center),
                "tail_seam_center": self._serialize_seam_point(self.tail_seam_center),
                "tip_seam_points": self._serialize_seam_points(self.tip_seam_points),
                "tail_seam_points": self._serialize_seam_points(self.tail_seam_points),
                "seam_lobes": self.seam_lobes,
                "seam_tension": self.seam_tension,
                "show_base_shape": self.show_base_shape,
                "show_edge_inlay_shape": self.show_edge_inlay_shape,
                "show_core_shape": self.show_core_shape,
                "show_sidewall_shape": self.show_sidewall_shape,
                "show_tip_tail_spacers": self.show_tip_tail_spacers,
                "show_sidewall_spacer_shell": self.show_sidewall_spacer_shell,
                "ski_color_rgb": (self.ski_color.red(), self.ski_color.green(), self.ski_color.blue()),
                "render_3d_mode": getattr(self, "render_3d_mode", "shaded"),
                "second_3d_base_separation_cm": float(getattr(self, "second_3d_base_separation_cm", 7.5)),
                "background_3d_color_rgba": (self.background_3d_color.red(), self.background_3d_color.green(), self.background_3d_color.blue(), self.background_3d_color.alpha()),
                "show_3d_background": bool(getattr(self, "show_3d_background", True)),
                "background_3d_width_px": self.background_3d_width_px,
                "background_3d_height_px": self.background_3d_height_px,
                "upper_mold_offset_mm": float(getattr(self, "upper_mold_offset_mm", 40.0)),
                "mold_hole_count": int(getattr(self, "mold_hole_count", 4)),
                "mold_hole_diameter_mm": float(getattr(self, "mold_hole_diameter_mm", 20.0)),
                "light_azimuth_deg": self.light_azimuth_deg,
                "light_elevation_deg": self.light_elevation_deg,
                "light_brightness": self.light_brightness,
                "top_graphic_path": self.top_graphic_path,
                "base_graphic_path": self.base_graphic_path,
                "top_graphic_offset_x_px": float(getattr(self, "top_graphic_offset_x_px", 0.0)),
                "top_graphic_offset_y_px": float(getattr(self, "top_graphic_offset_y_px", 0.0)),
                "top_graphic_scale_x": float(getattr(self, "top_graphic_scale_x", getattr(self, "top_graphic_scale", 1.0))),
                "top_graphic_scale_y": float(getattr(self, "top_graphic_scale_y", getattr(self, "top_graphic_scale", 1.0))),
                "base_graphic_offset_x_px": float(getattr(self, "base_graphic_offset_x_px", 0.0)),
                "base_graphic_offset_y_px": float(getattr(self, "base_graphic_offset_y_px", 0.0)),
                "base_graphic_scale_x": float(getattr(self, "base_graphic_scale_x", getattr(self, "base_graphic_scale", 1.0))),
                "base_graphic_scale_y": float(getattr(self, "base_graphic_scale_y", getattr(self, "base_graphic_scale", 1.0))),
                "lower_reinforcement_factor": self.lower_reinforcement_factor,
                "wood_core_stiffness_factor": self.wood_core_stiffness_factor,
                "upper_reinforcement_factor": self.upper_reinforcement_factor,
                "second_3d_base_to_base": bool(getattr(self, "second_3d_base_to_base", False)),
            },
            "relative_point_locks": list(self.relative_point_locks),
            "point_circles": list(self.point_circles),
            "point_dimensions": list(self.point_dimensions),
            "build_sheet_notes": dict(getattr(self, "build_sheet_notes", default_build_sheet_notes())),
        }
    def deserialize(self, data):

        def unpack(entries, target):

            target.clear()

            for entry in entries:

                pos = QPointF(*entry["pos"])

                if entry["type"] == "ControlPointTip":
                    p = ControlPointTip(pos)
                elif entry["type"] == "ControlPointTail":
                    p = ControlPointTail(pos)
                elif entry["type"] == "ControlPointCoreThickness":
                    p = ControlPointCoreThickness(pos)
                elif entry["type"] == "CosmeticPoint":
                    p = CosmeticPoint(pos)
                else:
                    p = ControlPointMid(pos)

                if hasattr(p, "handle_in") and "handle_in" in entry:
                    p.handle_in = QPointF(*entry["handle_in"])
                if hasattr(p, "handle_out") and "handle_out" in entry:
                    p.handle_out = QPointF(*entry["handle_out"])
                if hasattr(p, "locked") and "locked" in entry:
                    p.locked = entry["locked"]
                p.selected = bool(entry.get("selected", False))
                p.uid = entry.get("uid")

                target.append(p)

        unpack(data["edge"], self.points)
        unpack(data.get("left_edge", []), self.left_points)
        if not self.left_points:
            self.left_points = self._make_mirrored_edge_points(self.points)
        unpack(data["core"], self.core_thickness_points)
        unpack(data["camber"], self.camber_thickness_points)
        unpack(data.get("cosmetic", []), self.cosmetic_points)
        self._ensure_point_ids()
        self.relative_point_locks = list(data.get("relative_point_locks", []))
        self.point_circles = list(data.get("point_circles", []))
        self.point_dimensions = list(data.get("point_dimensions", []))
        notes = default_build_sheet_notes()
        saved_notes = data.get("build_sheet_notes", {})
        if isinstance(saved_notes, dict):
            for key in notes:
                notes[key] = str(saved_notes.get(key, notes[key]))
        self.build_sheet_notes = notes
        self._prune_relative_point_locks()
        self._prune_point_circles()
        self._prune_point_dimensions()
        for entry in self.point_dimensions:
            if isinstance(entry, dict) and "distance_px" in entry:
                entry["distance_px"] = float(entry["distance_px"])
        self._prune_point_dimensions()
        self.multi_select_order = []

        layup = data.get("layup", {})
        self.edge_thickness_px = float(layup.get("edge_thickness_px", self.edge_thickness_px))
        self.sidewall_thickness_px = float(layup.get("sidewall_thickness_px", self.sidewall_thickness_px))
        self.left_sidewall_thickness_px = float(layup.get("left_sidewall_thickness_px", getattr(self, "left_sidewall_thickness_px", self.sidewall_thickness_px)))
        self.edge_inlay_tip_trim_px = float(layup.get("edge_inlay_tip_trim_px", self.edge_inlay_tip_trim_px))
        self.edge_inlay_tail_trim_px = float(layup.get("edge_inlay_tail_trim_px", self.edge_inlay_tail_trim_px))
        self.base_edge_corner_min_radius_px = float(layup.get("base_edge_corner_min_radius_px", layup.get("edge_inlay_min_radius_px", getattr(self, "base_edge_corner_min_radius_px", 0.0))))
        self.include_splitboard_inside_edge = bool(layup.get("include_splitboard_inside_edge", getattr(self, "include_splitboard_inside_edge", True)))
        self.minimum_core_thickness_px = float(layup.get("minimum_core_thickness_px", getattr(self, "minimum_core_thickness_px", 5.0)))
        self.tip_spacer_length_px = float(layup.get("tip_spacer_length_px", self.tip_spacer_length_px))
        self.tail_spacer_length_px = float(layup.get("tail_spacer_length_px", self.tail_spacer_length_px))
        self.seam_depth_px = float(layup.get("seam_depth_px", self.seam_depth_px))
        self.seam_point_count = self._normalize_seam_point_count(
            layup.get("seam_point_count", getattr(self, "seam_point_count", 3))
        )
        self.tip_seam_point_count = self._normalize_seam_point_count(layup.get("tip_seam_point_count", self.seam_point_count))
        self.tail_seam_point_count = self._normalize_seam_point_count(layup.get("tail_seam_point_count", self.seam_point_count))
        self.seam_inner_x_frac = float(layup.get("seam_inner_x_frac", getattr(self, "seam_inner_x_frac", 0.34)))
        self.seam_inner_y_frac = float(layup.get("seam_inner_y_frac", getattr(self, "seam_inner_y_frac", 1.0)))
        self.seam_outer_x_frac = float(layup.get("seam_outer_x_frac", getattr(self, "seam_outer_x_frac", 0.72)))
        self.seam_outer_y_frac = float(layup.get("seam_outer_y_frac", getattr(self, "seam_outer_y_frac", -0.32)))
        self.tip_seam_center = self._deserialize_one_seam_point(layup.get("tip_seam_center"), self._build_default_seam_center_point())
        self.tail_seam_center = self._deserialize_one_seam_point(layup.get("tail_seam_center"), self._build_default_seam_center_point())
        self.tip_seam_points = self._deserialize_seam_points(layup.get("tip_seam_points"), self._build_default_seam_points())
        self.tail_seam_points = self._deserialize_seam_points(layup.get("tail_seam_points"), self._build_default_seam_points())
        self.seam_lobes = int(round(float(layup.get("seam_lobes", self.seam_lobes))))
        self.seam_tension = float(layup.get("seam_tension", self.seam_tension))
        self.show_base_shape = bool(layup.get("show_base_shape", self.show_base_shape))
        self.show_edge_inlay_shape = bool(layup.get("show_edge_inlay_shape", self.show_edge_inlay_shape))
        self.show_core_shape = bool(layup.get("show_core_shape", self.show_core_shape))
        self.show_sidewall_shape = bool(layup.get("show_sidewall_shape", self.show_sidewall_shape))
        self.show_tip_tail_spacers = bool(layup.get("show_tip_tail_spacers", self.show_tip_tail_spacers))
        self.show_sidewall_spacer_shell = bool(layup.get("show_sidewall_spacer_shell", self.show_sidewall_spacer_shell))
        self.outline_mode = str(layup.get("outline_mode", getattr(self, "outline_mode", "symmetric"))).lower()
        if self.outline_mode not in {"symmetric", "snowboard", "splitboard", "asymmetric"}:
            self.outline_mode = "symmetric"
        if self.outline_mode == "asymmetric":
            self._ensure_left_points()
        color_rgb = layup.get("ski_color_rgb", (self.ski_color.red(), self.ski_color.green(), self.ski_color.blue()))
        if isinstance(color_rgb, (list, tuple)) and len(color_rgb) >= 3:
            self.ski_color = QColor(int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]))
        self.render_3d_mode = str(layup.get("render_3d_mode", getattr(self, "render_3d_mode", "shaded")))
        if self.render_3d_mode not in {"shaded", "shaded_edges", "wireframe", "graphic"}:
            self.render_3d_mode = "shaded"
        self.second_3d_base_separation_cm = float(layup.get("second_3d_base_separation_cm", getattr(self, "second_3d_base_separation_cm", 7.5)))
        bg_color_rgba = layup.get("background_3d_color_rgba", (self.background_3d_color.red(), self.background_3d_color.green(), self.background_3d_color.blue(), self.background_3d_color.alpha()))
        if isinstance(bg_color_rgba, (list, tuple)) and len(bg_color_rgba) >= 3:
            alpha = int(bg_color_rgba[3]) if len(bg_color_rgba) >= 4 else self.background_3d_color.alpha()
            self.background_3d_color = QColor(int(bg_color_rgba[0]), int(bg_color_rgba[1]), int(bg_color_rgba[2]), alpha)
        self.show_3d_background = bool(layup.get("show_3d_background", getattr(self, "show_3d_background", True)))
        self.background_3d_width_px = float(layup.get("background_3d_width_px", getattr(self, "background_3d_width_px", 760.0)))
        self.background_3d_height_px = float(layup.get("background_3d_height_px", getattr(self, "background_3d_height_px", 1280.0)))
        self.upper_mold_offset_mm = float(layup.get("upper_mold_offset_mm", getattr(self, "upper_mold_offset_mm", 40.0)))
        self.mold_hole_count = max(1, min(10, int(layup.get("mold_hole_count", getattr(self, "mold_hole_count", 4)))))
        self.mold_hole_diameter_mm = float(layup.get("mold_hole_diameter_mm", getattr(self, "mold_hole_diameter_mm", 20.0)))
        self.light_azimuth_deg = float(layup.get("light_azimuth_deg", self.light_azimuth_deg))
        self.light_elevation_deg = float(layup.get("light_elevation_deg", self.light_elevation_deg))
        self.light_brightness = float(layup.get("light_brightness", self.light_brightness))
        self.lower_reinforcement_factor = float(layup.get("lower_reinforcement_factor", getattr(self, "lower_reinforcement_factor", 1.0)))
        self.wood_core_stiffness_factor = float(layup.get("wood_core_stiffness_factor", getattr(self, "wood_core_stiffness_factor", 1.0)))
        self.upper_reinforcement_factor = float(layup.get("upper_reinforcement_factor", getattr(self, "upper_reinforcement_factor", 1.0)))
        self.second_3d_base_to_base = bool(layup.get("second_3d_base_to_base", getattr(self, "second_3d_base_to_base", False)))
        self.top_graphic_offset_x_px = float(layup.get("top_graphic_offset_x_px", getattr(self, "top_graphic_offset_x_px", 0.0)))
        self.top_graphic_offset_y_px = float(layup.get("top_graphic_offset_y_px", getattr(self, "top_graphic_offset_y_px", 0.0)))
        legacy_top_scale = max(0.01, float(layup.get("top_graphic_scale", 1.0)))
        self.top_graphic_scale_x = max(0.01, float(layup.get("top_graphic_scale_x", getattr(self, "top_graphic_scale_x", legacy_top_scale))))
        self.top_graphic_scale_y = max(0.01, float(layup.get("top_graphic_scale_y", getattr(self, "top_graphic_scale_y", legacy_top_scale))))
        self.base_graphic_offset_x_px = float(layup.get("base_graphic_offset_x_px", getattr(self, "base_graphic_offset_x_px", 0.0)))
        self.base_graphic_offset_y_px = float(layup.get("base_graphic_offset_y_px", getattr(self, "base_graphic_offset_y_px", 0.0)))
        legacy_base_scale = max(0.01, float(layup.get("base_graphic_scale", 1.0)))
        self.base_graphic_scale_x = max(0.01, float(layup.get("base_graphic_scale_x", getattr(self, "base_graphic_scale_x", legacy_base_scale))))
        self.base_graphic_scale_y = max(0.01, float(layup.get("base_graphic_scale_y", getattr(self, "base_graphic_scale_y", legacy_base_scale))))
        top_graphic_path = layup.get("top_graphic_path", self.top_graphic_path)
        base_graphic_path = layup.get("base_graphic_path", self.base_graphic_path)
        self.top_graphic_path = ""
        self.base_graphic_path = ""
        self.top_graphic_image = None
        self.base_graphic_image = None
        if top_graphic_path:
            self.load_top_graphic(top_graphic_path)
        if base_graphic_path:
            self.load_base_graphic(base_graphic_path)

        self.apply_design_constraints()
        self._cache.clear()
        self.prepareGeometryChange()
        self.update()
    # Export Helpers
    def get_outline_points_cm1(self, samples=1000):
        pts = []
        edge = self.build_edge_path()
        mirrored = self.build_inner_or_left_edge_path()
        for i in range(samples + 1):
            p = edge.pointAtPercent(i / samples)
            pts.append((p.x()/PIXELS_PER_CM, -p.y()/PIXELS_PER_CM))
        for i in range(samples + 1):
            p = mirrored.pointAtPercent(i / samples)
            pts.append((p.x()/PIXELS_PER_CM, -p.y()/PIXELS_PER_CM))
        return pts
    def get_outline_points_cm(self, samples=1000):
        pts = []
        edge = self.build_edge_path()
        for i in range(samples + 1):
            p = edge.pointAtPercent(i / samples)
            # length_cm, half_width_cm
            pts.append((-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM))
        return pts
        pts = []
        edge = self.build_edge_path()
        for i in range(samples + 1):
            p = edge.pointAtPercent(i / samples)
            pts.append((p.x()/PIXELS_PER_CM, -p.y()/PIXELS_PER_CM))
        return pts
    def get_half_outline_points_cm(self, samples=1000):
        key = self._cache_key("half_outline_cm", samples)
        if key not in self._cache:
            self._cache[key] = [(-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM) for p in self.sample_edge(samples)]
        return self._cache[key]
    def get_camber_thickness_points_cm(self, samples=1000):
        key = self._cache_key("camber_cm", samples)
        if key not in self._cache:
            pts = []
            edge = self.build_camber_curve()
            if len(self.camber_thickness_points) < 2:
                return []

            # Use the true endpoint baseline of the camber profile rather than
            # the 2D drawing offset. This keeps the 3D mesh from inflating into
            # a "taco shell" when the side-view profile is moved around on screen.
            baseline_x = (
                self.camber_thickness_points[0].pos.x()
                + self.camber_thickness_points[-1].pos.x()
            ) / 2.0

            for i in range(samples + 1):
                p = edge.pointAtPercent(i / samples)
                length_cm = -p.y() / PIXELS_PER_CM
                camber_cm = (p.x() - baseline_x) / PIXELS_PER_CM
                pts.append((length_cm, camber_cm))
            self._cache[key] = pts
        return self._cache[key]
    def get_default_second_3d_base_separation_cm(self):
        if not self.camber_thickness_points:
            return 7.5
        xs = [float(p.pos.x()) for p in self.camber_thickness_points]
        if not xs:
            return 7.5
        span_px = max(xs) - min(xs)
        return max(0.1, 0.5 * span_px / PIXELS_PER_CM)
    def get_second_3d_side_by_side_offset_cm(self, faces=None):
        spacing_cm = float(getattr(self, "second_3d_base_separation_cm", self.get_default_second_3d_base_separation_cm()))
        min_y = 0.0
        if faces:
            ys = []
            for face in faces:
                for vertex in face:
                    ys.append(float(vertex[1]))
            if ys:
                min_y = min(ys)
        return (2.0 * min_y) - spacing_cm

    def path_to_points_cm(self, path, precision_scale=1.0):
        shapes = []
        precision_scale = max(1.0, float(precision_scale))
        transform = QTransform()
        if precision_scale > 1.0:
            transform.scale(precision_scale, precision_scale)
        for poly in path.toSubpathPolygons(transform):
            pts = [
                (-(pt.y() / precision_scale) / PIXELS_PER_CM, (pt.x() / precision_scale) / PIXELS_PER_CM)
                for pt in poly
            ]
            if len(pts) >= 2 and pts[0] == pts[-1]:
                pts = pts[:-1]
            if pts:
                shapes.append(pts)
        return shapes
    def path_to_fill_points_cm(self, path, precision_scale=1.0):
        precision_scale = max(1.0, float(precision_scale))
        transform = QTransform()
        if precision_scale > 1.0:
            transform.scale(precision_scale, precision_scale)
        poly = path.toFillPolygon(transform)
        pts = [
            (-(pt.y() / precision_scale) / PIXELS_PER_CM, (pt.x() / precision_scale) / PIXELS_PER_CM)
            for pt in poly
        ]
        if len(pts) >= 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        return pts
    def _clip_polygon_by_length_cm(self, points_cm, boundary_x_cm, keep_greater=True, eps=1e-6):
        pts = [(float(x), float(y)) for x, y in points_cm]
        if len(pts) < 3:
            return []

        boundary_x_cm = float(boundary_x_cm)

        def inside(pt):
            if keep_greater:
                return pt[0] >= boundary_x_cm - eps
            return pt[0] <= boundary_x_cm + eps

        def intersect(a, b):
            ax, ay = a
            bx, by = b
            dx = bx - ax
            if abs(dx) <= eps:
                return (boundary_x_cm, ay)
            t = (boundary_x_cm - ax) / dx
            t = max(0.0, min(1.0, t))
            return (boundary_x_cm, ay + (by - ay) * t)

        clipped = []
        prev = pts[-1]
        prev_inside = inside(prev)
        for curr in pts:
            curr_inside = inside(curr)
            if curr_inside:
                if not prev_inside:
                    clipped.append(intersect(prev, curr))
                clipped.append(curr)
            elif prev_inside:
                clipped.append(intersect(prev, curr))
            prev = curr
            prev_inside = curr_inside

        clipped = self._dedupe_polygon_points(clipped, eps=1e-5)
        if len(clipped) >= 3 and self._polygon_signed_area_xy(clipped) < 0.0:
            clipped.reverse()
        return clipped
    def build_dovetail_spacer_export_points_cm(self, spacer_name, samples=1400):
        dovetail_bounds = self._current_dovetail_length_y_bounds()
        if dovetail_bounds is None:
            return []
        outline = self._current_full_outline_polygon_cm_uncached(samples=max(300, int(samples)))
        if len(outline) < 3:
            return []

        tip_y, tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
        if spacer_name == "tip_spacer":
            seam_x = -float(core_tip_start_y) / PIXELS_PER_CM
            pts = self._clip_polygon_by_length_cm(outline, seam_x, keep_greater=True)
        elif spacer_name == "tail_spacer":
            seam_x = -float(core_tail_end_y) / PIXELS_PER_CM
            pts = self._clip_polygon_by_length_cm(outline, seam_x, keep_greater=False)
        else:
            return []

        if len(pts) < 3 or abs(self._polygon_signed_area_xy(pts)) <= 1e-6:
            return []
        return pts
    def _path_from_points_cm(self, points_cm):
        pts = [
            QPointF(float(y_cm) * PIXELS_PER_CM, -float(x_cm) * PIXELS_PER_CM)
            for x_cm, y_cm in points_cm
        ]
        return self._polygon_path(pts)
    def sampled_curve_to_points_cm(self, path, samples=2000):
        pts = []
        if path.isEmpty():
            return pts
        for i in range(samples + 1):
            p = path.pointAtPercent(i / samples)
            pts.append((-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM))
        return pts
    def build_core_profile_export_points_cm(self, samples=2000):
        if len(self.core_thickness_points) < 2:
            return []
        flat_x = self.get_core_profile_left_x()
        curve_pts = self.sampled_curve_to_points_cm(self.build_core_curve(), samples=samples)
        if not curve_pts:
            return []
        start_y = self.core_thickness_points[0].pos.y()
        end_y = self.core_thickness_points[-1].pos.y()
        flat_start = (-start_y / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        flat_end = (-end_y / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        return [flat_start] + curve_pts + [flat_end]
    def build_camber_profile_export_points_cm(self, samples=2000):
        if len(self.camber_thickness_points) < 2:
            return []
        flat_x = min(p.pos.x() for p in self.camber_thickness_points) - 50
        curve_pts = self.sampled_curve_to_points_cm(self.build_camber_curve(), samples=samples)
        if not curve_pts:
            return []
        start_y = self.camber_thickness_points[0].pos.y()
        end_y = self.camber_thickness_points[-1].pos.y()
        flat_start = (-start_y / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        flat_end = (-end_y / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        # Include the straight left-side segment explicitly so the CNC on-line path,
        # previews, and exports all carry the full closed camber profile.
        return [flat_start] + curve_pts + [flat_end, flat_start]
    def build_upper_mold_export_points_cm(self, samples=2000):
        if len(self.camber_thickness_points) < 2:
            return []
        offset_pts = self._upper_mold_offset_curve_points(samples=samples)
        if not offset_pts:
            return []
        flat_x = self.get_upper_mold_flat_x()
        curve_pts = [(-pt.y() / PIXELS_PER_CM, pt.x() / PIXELS_PER_CM) for pt in offset_pts]
        flat_end = (-offset_pts[-1].y() / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        flat_start = (-offset_pts[0].y() / PIXELS_PER_CM, flat_x / PIXELS_PER_CM)
        return curve_pts + [flat_end, flat_start, curve_pts[0]]
    def _build_strip_piece_paths(self, start_y, end_y, outer_inset_px, inner_inset_px, samples=2000):
        if end_y < start_y:
            start_y, end_y = end_y, start_y
        if isinstance(inner_inset_px, (tuple, list)):
            inner_left_inset = float(inner_inset_px[0])
            inner_right_inset = float(inner_inset_px[1] if len(inner_inset_px) > 1 else inner_inset_px[0])
        else:
            inner_left_inset = float(inner_inset_px)
            inner_right_inset = float(inner_inset_px)
        right_samples = self._sorted_outline_side_samples("right", samples)
        left_samples = self._sorted_outline_side_samples("left", samples)
        outer_right = self._outline_side_between(right_samples, start_y, end_y, "right", inset_px=outer_inset_px)
        inner_right = self._outline_side_between(right_samples, start_y, end_y, "right", inset_px=inner_right_inset)
        outer_left = self._outline_side_between(left_samples, start_y, end_y, "left", inset_px=outer_inset_px)
        inner_left = self._outline_side_between(left_samples, start_y, end_y, "left", inset_px=inner_left_inset)
        outer_left, outer_right = self._clamp_outline_sides(outer_left, outer_right)
        inner_left, inner_right = self._clamp_outline_sides(inner_left, inner_right)
        if len(outer_right) < 2 or len(inner_right) < 2 or len(outer_left) < 2 or len(inner_left) < 2:
            return []

        right_polygon = outer_right + list(reversed(inner_right))
        left_polygon = outer_left + list(reversed(inner_left))

        paths = []
        for polygon in (right_polygon, left_polygon):
            path = self._polygon_path(polygon)
            if not path.isEmpty():
                paths.append(path)
        return paths
    def _append_export_path(self, shapes, name, shape_path, closed=True, split_subpaths=False):
        if split_subpaths:
            subpaths = self.path_to_points_cm(shape_path)
            for idx, pts in enumerate(subpaths, start=1):
                if pts:
                    layer_name = f"{name}_{idx}"
                    shapes.append({"name": layer_name, "layer": layer_name, "closed": closed, "points": pts})
            return

        shape_pts = self.path_to_fill_points_cm(shape_path)
        if shape_pts:
            shapes.append({"name": name, "layer": name, "closed": closed, "points": shape_pts})
    def get_export_shapes(self, samples=5000, include_all=True):
        shapes = []

        outline_pts = self.path_to_fill_points_cm(self.build_full_shape())
        if outline_pts:
            shapes.append({"name": "ski_outline", "layer": "ski_outline", "closed": True, "points": outline_pts})
        if bool(getattr(self, "show_ski_snowboard", False)):
            left_ski_pts = self.path_to_fill_points_cm(self.build_second_ski_shape())
            if left_ski_pts:
                shapes.append({"name": "left_ski_outline", "layer": "left_ski_outline", "closed": True, "points": left_ski_pts})

        core_profile_pts = self.build_core_profile_export_points_cm(samples=2000)
        if core_profile_pts:
            shapes.append({"name": "core_profile", "layer": "core_profile", "closed": True, "points": core_profile_pts})

        camber_profile_pts = self.build_camber_profile_export_points_cm(samples=2000)
        if camber_profile_pts:
            shapes.append({"name": "camber_profile", "layer": "camber_profile", "closed": True, "points": camber_profile_pts})

        upper_mold_pts = self.build_upper_mold_export_points_cm(samples=2000)
        if upper_mold_pts:
            shapes.append({"name": "upper_mold", "layer": "upper_mold", "closed": True, "points": upper_mold_pts})

        export_candidates = [
            (True if include_all else self.show_base_shape, "base_material", self.build_base_material_path(samples), False),
            (True if include_all else self.show_core_shape, "core_footprint", self.build_core_footprint_path(samples), False),
            (True if include_all else self.show_tip_tail_spacers, "tip_spacer", self.build_tip_spacer_path(samples), False),
            (True if include_all else self.show_tip_tail_spacers, "tail_spacer", self.build_tail_spacer_path(samples), False),
            (True if include_all else self.show_sidewall_spacer_shell, "sidewall_spacer_shell", self.build_sidewall_spacer_shell_path(samples), False),
        ]

        for enabled, name, shape_path, split_subpaths in export_candidates:
            if not enabled:
                continue
            self._append_export_path(shapes, name, shape_path, closed=True, split_subpaths=split_subpaths)

        if True if include_all else self.show_edge_inlay_shape:
            tip_y = self.points[-1].pos.y() + max(0.0, self.edge_inlay_tip_trim_px)
            tail_y = self.points[0].pos.y() - max(0.0, self.edge_inlay_tail_trim_px)
            for idx, piece_path in enumerate(self._build_strip_piece_paths(tip_y, tail_y, 0.0, self.edge_thickness_px, samples=samples), start=1):
                self._append_export_path(shapes, f"edge_inlay_{idx}", piece_path, closed=True, split_subpaths=False)

        if True if include_all else self.show_sidewall_shape:
            tip_y = self.points[-1].pos.y() + max(0.0, self.tip_spacer_length_px)
            tail_y = self.points[0].pos.y() - max(0.0, self.tail_spacer_length_px)
            inner_inset = self._sidewall_inner_insets_px()
            for idx, piece_path in enumerate(self._build_strip_piece_paths(tip_y, tail_y, 0.0, inner_inset, samples=samples), start=1):
                self._append_export_path(shapes, f"sidewall_{idx}", piece_path, closed=True, split_subpaths=False)

        return shapes
    def export_svg(self, filename):

        shapes = self.get_export_shapes(include_all=True)
        all_pts = [pt for shape in shapes for pt in shape["points"]]
        if not all_pts:
            return

        minx = min(p[0] for p in all_pts)
        maxx = max(p[0] for p in all_pts)
        miny = min(p[1] for p in all_pts)
        maxy = max(p[1] for p in all_pts)

        width = maxx - minx
        height = maxy - miny

        svg = ET.Element("svg", {
            "xmlns": "http://www.w3.org/2000/svg",
            "version": "1.1",
            "width": f"{width}cm",
            "height": f"{height}cm",
            "viewBox": f"{minx} {miny} {width} {height}"
        })

        for shape in shapes:
            pts = shape["points"]
            if not pts:
                continue
            d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
            if shape["closed"]:
                d += " Z"
            layer = ET.SubElement(svg, "g", {
                "id": shape.get("layer", shape["name"])
            })
            ET.SubElement(layer, "path", {
                "id": shape["name"],
                "d": d,
                "fill": "none",
                "stroke": "black",
                "stroke-width": "0.1"
            })

        tree = ET.ElementTree(svg)
        tree.write(filename)
    def export_dxf(self, filename):

        shapes = self.get_export_shapes(include_all=True)
        if not shapes:
            return

        scale = 10.0
        layer_names = [shape.get("layer", shape["name"]).upper() for shape in shapes]

        def write_lwpolyline(f, layer_name, pts, closed):
            if len(pts) < 2:
                return
            f.write("0\nLWPOLYLINE\n")
            f.write(f"8\n{layer_name}\n")
            f.write(f"90\n{len(pts)}\n")
            f.write(f"70\n{1 if closed else 0}\n")
            for x, y in pts:
                f.write(f"10\n{x * scale:.6f}\n20\n{y * scale:.6f}\n")

        with open(filename, "w") as f:
            f.write("0\nSECTION\n2\nHEADER\n")
            f.write("9\n$ACADVER\n1\nAC1015\n")
            f.write("9\n$INSUNITS\n70\n4\n")
            f.write("0\nENDSEC\n")

            f.write("0\nSECTION\n2\nTABLES\n")
            f.write("0\nTABLE\n2\nLAYER\n70\n{}\n".format(len(layer_names) + 1))
            f.write("0\nLAYER\n2\n0\n70\n0\n62\n7\n6\nCONTINUOUS\n")
            for layer_name in layer_names:
                f.write(f"0\nLAYER\n2\n{layer_name}\n70\n0\n62\n7\n6\nCONTINUOUS\n")
            f.write("0\nENDTAB\n0\nENDSEC\n")

            f.write("0\nSECTION\n2\nENTITIES\n")
            for shape in shapes:
                write_lwpolyline(f, shape.get("layer", shape["name"]).upper(), shape["points"], shape["closed"])
            f.write("0\nENDSEC\n0\nEOF\n")
    # Dimensions
    def _begin_dimension_layout(self):
        self._dimension_label_rects = []
        self._dimension_line_rects = []

    def _register_dimension_segment(self, a, b, margin=2.0):
        if not hasattr(self, "_dimension_line_rects"):
            self._begin_dimension_layout()
        rect = QRectF(a, b).normalized().adjusted(-margin, -margin, margin, margin)
        self._dimension_line_rects.append(rect)

    def _dimension_text_rect(self, painter, pos, text, pad=3.0):
        metrics = painter.fontMetrics()
        return QRectF(
            pos.x() - pad,
            pos.y() - metrics.ascent() - pad,
            metrics.horizontalAdvance(text) + pad * 2.0,
            metrics.height() + pad * 2.0,
        )

    def _dimension_rect_collision_score(self, rect):
        score = 0
        for existing in getattr(self, "_dimension_label_rects", []):
            if rect.intersects(existing):
                score += 100
        for line_rect in getattr(self, "_dimension_line_rects", []):
            if rect.intersects(line_rect):
                score += 1
        return score

    def _place_dimension_label(self, painter, preferred_pos, text, orientation="vertical"):
        if not hasattr(self, "_dimension_label_rects"):
            self._begin_dimension_layout()

        if orientation == "horizontal":
            shifts = [
                QPointF(0.0, 0.0), QPointF(0.0, -16.0), QPointF(0.0, 16.0),
                QPointF(-28.0, -16.0), QPointF(28.0, -16.0),
                QPointF(-28.0, 16.0), QPointF(28.0, 16.0),
                QPointF(-56.0, -28.0), QPointF(56.0, -28.0),
                QPointF(-56.0, 28.0), QPointF(56.0, 28.0),
            ]
        else:
            shifts = [
                QPointF(0.0, 0.0), QPointF(14.0, 0.0), QPointF(-48.0, 0.0),
                QPointF(14.0, -16.0), QPointF(14.0, 16.0),
                QPointF(-48.0, -16.0), QPointF(-48.0, 16.0),
                QPointF(28.0, -30.0), QPointF(28.0, 30.0),
                QPointF(-72.0, -30.0), QPointF(-72.0, 30.0),
            ]

        best_pos = preferred_pos
        best_rect = self._dimension_text_rect(painter, preferred_pos, text)
        best_score = self._dimension_rect_collision_score(best_rect)

        for shift in shifts:
            candidate = QPointF(preferred_pos.x() + shift.x(), preferred_pos.y() + shift.y())
            rect = self._dimension_text_rect(painter, candidate, text)
            score = self._dimension_rect_collision_score(rect)
            if score < best_score:
                best_pos = candidate
                best_rect = rect
                best_score = score
                if score == 0:
                    break

        self._dimension_label_rects.append(best_rect)
        return best_pos, best_rect

    def _draw_dimension_label(self, painter, preferred_pos, text, orientation="vertical"):
        label_pos, rect = self._place_dimension_label(painter, preferred_pos, text, orientation)
        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(20, 24, 30, 185)))
        painter.drawRoundedRect(rect, 3, 3)
        painter.restore()
        painter.drawText(label_pos, text)

    def _right_side_dimension_offset_cm(self, p1, p2, padding_px=42.0, stack_padding_px=52.0, min_offset_cm=9.5):
        anchor_x = max(float(p1.x()), float(p2.x()))
        try:
            base_path = self.build_base_material_path(samples=600)
        except Exception:
            base_path = QPainterPath()
        if base_path.isEmpty():
            base_path = self.build_full_shape()
        if base_path.isEmpty():
            return min_offset_cm
        target_x = base_path.boundingRect().right() + float(padding_px)
        other_dim_x = None

        def include_dimension_line_x(point_a, point_b, offset_cm):
            nonlocal other_dim_x
            line_x = max(float(point_a.x()), float(point_b.x())) + float(offset_cm) * PIXELS_PER_CM
            other_dim_x = line_x if other_dim_x is None else max(other_dim_x, line_x)

        def point_at(points, index):
            resolved = index if index >= 0 else len(points) + index
            if 0 <= resolved < len(points):
                return points[resolved]
            return None

        if len(self.points) >= 5:
            include_dimension_line_x(self.points[1].pos, self.points[-2].pos, 7)
            include_dimension_line_x(self.points[0].pos, self.points[1].pos, 7)
            include_dimension_line_x(self.points[-1].pos, self.points[-2].pos, 7)
            y_center = (self.points[-1].pos.y() + self.points[0].pos.y()) / 2.0
            include_dimension_line_x(QPointF(0.0, y_center), self.points[2].pos, 3)

        camber_dims = [(1, -2, 8), (1, 2, 3), (2, 3, 4), (3, 4, 4), (4, 5, 3)]
        for idx_a, idx_b, offset_cm in camber_dims:
            point_a = point_at(self.camber_thickness_points, idx_a)
            point_b = point_at(self.camber_thickness_points, idx_b)
            if point_a is not None and point_b is not None:
                include_dimension_line_x(point_a.pos, point_b.pos, offset_cm)

        core_pts = self.core_thickness_points
        for i in range(max(0, len(core_pts) - 1)):
            include_dimension_line_x(core_pts[i].pos, core_pts[i + 1].pos, 4)

        if other_dim_x is not None:
            target_x = max(target_x, other_dim_x + float(stack_padding_px))
        offset_px = max(float(min_offset_cm) * PIXELS_PER_CM, target_x - anchor_x)
        return offset_px / PIXELS_PER_CM

    def draw_vertical_dimension_line2(self,painter,p1,p2,offset_cm=0,text_offset_px=6,arrow_size_px=8):
        """
        Draws a vertical dimension between two QPointF positions
        """
        # Convert offset to pixels
        offset_px = offset_cm * PIXELS_PER_CM
        # Ensure p1 is bottom and p2 is top
        if p1.y() < p2.y():
            p1, p2 = p2, p1
        # Dimension line X position
        x_dim = max(p1.x(), p2.x()) + offset_px
        # Extension line endpoints
        ext1 = QPointF(x_dim, p1.y())
        ext2 = QPointF(x_dim, p2.y())
        # Draw extension lines
        painter.drawLine(p1, ext1)
        painter.drawLine(p2, ext2)
        self._register_dimension_segment(p1, ext1)
        self._register_dimension_segment(p2, ext2)
        # Draw main dimension line
        painter.drawLine(ext1, ext2)
        self._register_dimension_segment(ext1, ext2)
        # Calculate height
        height_px = abs(p1.y() - p2.y())
        height_cm = height_px / PIXELS_PER_CM
        # Arrow drawing helper
        def draw_arrow(base, direction):

            dx, dy = direction

            left = QPointF(
                base.x() - dx * arrow_size_px + dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px - dx * arrow_size_px * 0.5)

            right = QPointF(
                base.x() - dx * arrow_size_px - dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px + dx * arrow_size_px * 0.5)

            painter.drawLine(base, left)
            painter.drawLine(base, right)
    def draw_vertical_dimension_line(self, painter,p1,p2,offset_cm=2.0,text_offset_px=6,arrow_size_px=10):
        """
        Draws a vertical dimension between two QPointF positions
        """
        # Convert offset to pixels
        offset_px = offset_cm * PIXELS_PER_CM

        # Ensure p1 is bottom and p2 is top
        if p1.y() < p2.y():
            p1, p2 = p2, p1

        # Dimension line X position
        x_dim = max(p1.x(), p2.x()) + offset_px

        # Extension line endpoints
        ext1 = QPointF(x_dim, p1.y())
        ext2 = QPointF(x_dim, p2.y())

        # Draw extension lines
        painter.drawLine(p1, ext1)
        painter.drawLine(p2, ext2)
        self._register_dimension_segment(p1, ext1)
        self._register_dimension_segment(p2, ext2)

        # Draw main dimension line
        painter.drawLine(ext1, ext2)
        self._register_dimension_segment(ext1, ext2)

        # Calculate height
        height_px = abs(p1.y() - p2.y())
        height_cm = height_px / PIXELS_PER_CM

        # Arrow drawing helper
        def draw_arrow(base, direction):

            dx, dy = direction

            left = QPointF(
                base.x() - dx * arrow_size_px + dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px - dx * arrow_size_px * 0.5)

            right = QPointF(
                base.x() - dx * arrow_size_px - dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px + dx * arrow_size_px * 0.5)

            painter.drawLine(base, left)
            painter.drawLine(base, right)

        # Draw arrows
        draw_arrow(ext1, (0, 1))
        draw_arrow(ext2, (0, -1))

        # Draw text centered
        mid_y = (ext1.y() + ext2.y()) / 2

        text_point = QPointF(
            x_dim + text_offset_px,
            mid_y)
        self._draw_dimension_label(painter, text_point, f"{height_cm:.1f} cm", "vertical")
    def draw_horizontal_dimension_line(self, painter, p1, p2, offset_cm=2.0, text_offset_px_v=6, text_offset_px_h=6, arrow_size_px=5):
        """
        Draws a horizontal dimension between two QPointF positions
        """
        offset_px = offset_cm * PIXELS_PER_CM

        # Ensure p1 is left and p2 is right
        if p1.x() > p2.x():
            p1, p2 = p2, p1

        # Dimension line Y position
        y_dim = min(p1.y(), p2.y()) - offset_px

        # Extension line endpoints
        ext1 = QPointF(p1.x(), y_dim)
        ext2 = QPointF(p2.x(), y_dim)

        # Draw extension lines
        painter.drawLine(p1, ext1)
        painter.drawLine(p2, ext2)
        self._register_dimension_segment(p1, ext1)
        self._register_dimension_segment(p2, ext2)

        # Draw main dimension line
        painter.drawLine(ext1, ext2)
        self._register_dimension_segment(ext1, ext2)

        # Calculate width
        width_px = abs(p2.x() - p1.x())
        width_mm = width_px / PIXELS_PER_CM * 10.0

        def draw_arrow(base, direction):
            dx, dy = direction

            left = QPointF(
                base.x() - dx * arrow_size_px + dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px - dx * arrow_size_px * 0.5
            )

            right = QPointF(
                base.x() - dx * arrow_size_px - dy * arrow_size_px * 0.5,
                base.y() - dy * arrow_size_px + dx * arrow_size_px * 0.5
            )

            painter.drawLine(base, left)
            painter.drawLine(base, right)

        # Arrows point 
        draw_arrow(ext1, (-1, 0))
        draw_arrow(ext2, (1, 0))

        # Centered text
        mid_x = (ext1.x() + ext2.x()) / 2.0
        text_point = QPointF(mid_x + text_offset_px_h, y_dim + text_offset_px_v)
        self._draw_dimension_label(painter, text_point, f"{width_mm:.0f} mm", "horizontal")
    # Sidecut Circle
    def _sidecut_circle_geometry(self, points):
        if len(points) < 4:
            return None

        A = points[1].pos
        B = points[2].pos
        C = points[3].pos

        ax, ay = A.x(), A.y()
        bx, by = B.x(), B.y()
        cx, cy = C.x(), C.y()

        d = 2 * (ax*(by-cy) + bx*(cy-ay) + cx*(ay-by))
        if abs(d) < 0.001:
            return None

        ux = ((ax*ax+ay*ay)*(by-cy) +
              (bx*bx+by*by)*(cy-ay) +
              (cx*cx+cy*cy)*(ay-by)) / d
        uy = ((ax*ax+ay*ay)*(cx-bx) +
              (bx*bx+by*by)*(ax-cx) +
              (cx*cx+cy*cy)*(bx-ax)) / d

        center = QPointF(ux, uy)
        radius = math.hypot(ax-ux, ay-uy)
        ski_true_center = QPointF(0, (points[0].pos.y() + points[-1].pos.y()) / 2)
        ski_turn_center = QPointF(points[2].pos.x(), points[2].pos.y())
        return center, radius, ski_true_center, ski_turn_center, QPointF(B)

    def _map_sidecut_circle_geometry(self, geometry, transform):
        if geometry is None:
            return None
        center, radius, ski_true_center, ski_turn_center, label_point = geometry
        return (
            transform.map(center),
            radius,
            transform.map(ski_true_center),
            transform.map(ski_turn_center),
            transform.map(label_point),
        )

    def _second_ski_transform(self, gap_px=10.0):
        path = self.build_full_shape()
        bounds = path.boundingRect()
        transform = QTransform()
        if getattr(self, "outline_mode", "symmetric") == "snowboard":
            transform.translate(2.0 * bounds.right() + float(gap_px), 0.0)
        else:
            transform.translate(2.0 * bounds.left() - float(gap_px), 0.0)
        transform.scale(-1.0, 1.0)
        return transform

    def _draw_sidecut_circle_geometry(self, painter, geometry):
        if geometry is None:
            return
        center, radius, ski_true_center, ski_turn_center, label_point = geometry

        vx1 = ski_true_center.x() - center.x()
        vy1 = ski_true_center.y() - center.y()
        vx2 = ski_turn_center.x() - center.x()
        vy2 = ski_turn_center.y() - center.y()
        mag1 = math.hypot(vx1, vy1)
        mag2 = math.hypot(vx2, vy2)
        if mag1 > 1e-9 and mag2 > 1e-9:
            cross = vx1 * vy2 - vy1 * vx2
            dot = vx1 * vx2 + vy1 * vy2
            angle_deg = math.degrees(math.atan2(cross, dot))
        else:
            angle_deg = 0.0

        painter.setPen(QPen(QColor(255,255,255), 1))
        painter.drawText(QPointF(label_point.x() + 20, label_point.y() + 15), f"{angle_deg:.2f}°")

        painter.setPen(QPen(QColor(255,255,0,200), 2, Qt.PenStyle.DashLine))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, radius, radius)

        painter.setPen(QPen(QColor(0,0,200), 2, Qt.PenStyle.DashLine))
        painter.drawLine(center, ski_true_center)

        painter.setPen(QPen(QColor(0,200,0), 2, Qt.PenStyle.DashLine))
        painter.drawLine(center, ski_turn_center)

    def _draw_sidecut_circle_with_copies(self, painter, geometry, draw_opposite_side=False):
        if geometry is None:
            return
        mode = getattr(self, "outline_mode", "symmetric")
        geometries = [geometry]
        mirror = None
        if draw_opposite_side:
            mirror = QTransform()
            mirror.scale(-1.0, 1.0)
            geometries.append(self._map_sidecut_circle_geometry(geometry, mirror))
        if self.show_ski_snowboard and mode not in {"snowboard", "splitboard"}:
            second_transform = self._second_ski_transform()
            if mode == "symmetric":
                mirror = mirror or QTransform()
                mirror.scale(-1.0, 1.0)
                second_source = self._map_sidecut_circle_geometry(geometry, mirror)
                geometries.append(self._map_sidecut_circle_geometry(second_source, second_transform))
            else:
                geometries.extend([
                    self._map_sidecut_circle_geometry(item, second_transform)
                    for item in list(geometries)
                ])
        for item in geometries:
            self._draw_sidecut_circle_geometry(painter, item)

    def draw_sidecut_circle(self, painter):
        self._draw_sidecut_circle_with_copies(
            painter,
            self._sidecut_circle_geometry(self.points),
            draw_opposite_side=False,
        )
        if getattr(self, "outline_mode", "symmetric") == "asymmetric":
            self._ensure_left_points()
            self._draw_sidecut_circle_with_copies(
                painter,
                self._sidecut_circle_geometry(self.left_points),
                draw_opposite_side=False,
            )
    def _points_signature(self, points):
        sig = []
        for p in points:
            if hasattr(p, "handle_in") and hasattr(p, "handle_out"):
                sig.append((
                    round(p.pos.x(), 3), round(p.pos.y(), 3),
                    round(p.handle_in.x(), 3), round(p.handle_in.y(), 3),
                    round(p.handle_out.x(), 3), round(p.handle_out.y(), 3)
                ))
            else:
                sig.append((round(p.pos.x(), 3), round(p.pos.y(), 3)))
        return tuple(sig)
    def _cache_key(self, name, *extra):
        return (
            name,
            getattr(self, "outline_mode", "symmetric"),
            self._points_signature(self.points),
            self._points_signature(getattr(self, "left_points", [])),
            self._points_signature(self.core_thickness_points),
            self._points_signature(self.camber_thickness_points),
            self._points_signature(self.cosmetic_points),
            round(self.edge_thickness_px, 3),
            round(self.sidewall_thickness_px, 3),
            round(getattr(self, "left_sidewall_thickness_px", self.sidewall_thickness_px), 3),
            round(self.edge_inlay_tip_trim_px, 3),
            round(self.edge_inlay_tail_trim_px, 3),
            round(getattr(self, "base_edge_corner_min_radius_px", 0.0), 3),
            bool(getattr(self, "include_splitboard_inside_edge", True)),
            round(self.tip_spacer_length_px, 3),
            round(self.tail_spacer_length_px, 3),
            round(self.seam_depth_px, 3),
            int(getattr(self, "tip_seam_point_count", getattr(self, "seam_point_count", 3))),
            int(getattr(self, "tail_seam_point_count", getattr(self, "seam_point_count", 3))),
            round(getattr(self, "seam_inner_x_frac", 0.34), 4),
            round(getattr(self, "seam_inner_y_frac", 1.0), 4),
            round(getattr(self, "seam_outer_x_frac", 0.72), 4),
            round(getattr(self, "seam_outer_y_frac", -0.32), 4),
            self._points_signature([self.tip_seam_center]),
            self._points_signature([self.tail_seam_center]),
            int(self.seam_lobes),
            round(self.seam_tension, 3),
        ) + extra
    def _shape_path_from_samples(self, samples, inset_px=0.0, tip_trim_px=0.0, tail_trim_px=0.0):
        tail_y = self.points[0].pos.y()
        tip_y = self.points[-1].pos.y()
        start_y = tip_y + max(0.0, tip_trim_px)
        end_y = tail_y - max(0.0, tail_trim_px)

        filtered = []
        for p in samples:
            if start_y <= p.y() <= end_y:
                half_width = max(0.0, p.x() - inset_px)
                filtered.append(QPointF(half_width, p.y()))

        path = QPainterPath()
        if len(filtered) < 2:
            return path

        poly = QPolygonF(filtered + [QPointF(-p.x(), p.y()) for p in reversed(filtered)])
        path.addPolygon(poly)
        path.closeSubpath()
        return path
    def _rounded_polygon_path(self, pts, radius_px=0.0, should_round=None):
        radius = max(0.0, float(radius_px))
        clean_pts = [QPointF(p) for p in pts]
        while len(clean_pts) > 1 and QLineF(clean_pts[0], clean_pts[-1]).length() < 1e-6:
            clean_pts.pop()
        if len(clean_pts) < 3 or radius <= 1e-9:
            return self._polygon_path(clean_pts)

        rounded = []
        straight_tolerance = math.radians(12.0)
        min_angle = math.radians(20.0)
        count = len(clean_pts)
        for i, curr in enumerate(clean_pts):
            prev_pt = clean_pts[(i - 1) % count]
            next_pt = clean_pts[(i + 1) % count]
            prev_len = QLineF(curr, prev_pt).length()
            next_len = QLineF(curr, next_pt).length()
            if prev_len < 1e-6 or next_len < 1e-6:
                rounded.append((curr, None))
                continue

            v_prev_x = (prev_pt.x() - curr.x()) / prev_len
            v_prev_y = (prev_pt.y() - curr.y()) / prev_len
            v_next_x = (next_pt.x() - curr.x()) / next_len
            v_next_y = (next_pt.y() - curr.y()) / next_len
            dot = max(-1.0, min(1.0, v_prev_x * v_next_x + v_prev_y * v_next_y))
            angle = math.acos(dot)
            if angle <= min_angle or abs(math.pi - angle) <= straight_tolerance:
                rounded.append((curr, None))
                continue
            if should_round is not None and not should_round(curr, prev_pt, next_pt, i):
                rounded.append((curr, None))
                continue

            offset = min(radius, prev_len * 0.45, next_len * 0.45)
            if offset <= 1e-6:
                rounded.append((curr, None))
                continue
            before = QPointF(curr.x() + v_prev_x * offset, curr.y() + v_prev_y * offset)
            after = QPointF(curr.x() + v_next_x * offset, curr.y() + v_next_y * offset)
            rounded.append((before, (curr, after)))

        path = QPainterPath()
        first_point = rounded[0][0]
        path.moveTo(first_point)
        for point, curve in rounded[1:]:
            path.lineTo(point)
            if curve is not None:
                control, end = curve
                path.quadTo(control, end)
        point, curve = rounded[0]
        path.lineTo(point)
        if curve is not None:
            control, end = curve
            path.quadTo(control, end)
        path.closeSubpath()
        return path
    def _round_closed_path_corners(self, path, radius_px=0.0, should_round=None):
        radius = max(0.0, float(radius_px))
        if radius <= 1e-9 or path.isEmpty():
            return path
        rounded_path = QPainterPath()
        for poly in path.toSubpathPolygons():
            pts = [QPointF(p) for p in poly]
            subpath = self._rounded_polygon_path(pts, radius, should_round=should_round)
            if not subpath.isEmpty():
                rounded_path.addPath(subpath)
        return rounded_path
    def _round_base_edge_cutout_corners_path(self, path, tip_trim_y, tail_trim_y):
        radius = max(0.0, float(getattr(self, "base_edge_corner_min_radius_px", 0.0)))
        if radius <= 1e-9 or path.isEmpty():
            return path

        trim_ys = (float(tip_trim_y), float(tail_trim_y))
        y_tol = max(0.25, radius * 0.05)
        def should_round(curr, _prev_pt, _next_pt, _idx):
            return any(abs(curr.y() - trim_y) <= y_tol for trim_y in trim_ys)

        return self._round_closed_path_corners(path, radius, should_round=should_round)
    def _sample_path_points(self, path, samples=2000):
        pts = []
        samples = max(2, int(samples))
        if path.isEmpty():
            return pts
        for i in range(samples + 1):
            pt = path.pointAtPercent(i / samples)
            pts.append(QPointF(pt.x(), pt.y()))
        return pts
    def _sorted_outline_side_samples(self, side, samples=2000):
        key = self._cache_key("outline_side_samples", str(side), samples)
        if key in self._cache:
            return self._cache[key]
        path = self.build_inner_or_left_edge_path() if side == "left" else self.build_edge_path()
        pts = sorted(self._sample_path_points(path, samples), key=lambda p: p.y())
        deduped = []
        for p in pts:
            if deduped and abs(deduped[-1].y() - p.y()) < 1e-6:
                if side == "right":
                    if p.x() > deduped[-1].x():
                        deduped[-1] = p
                else:
                    if p.x() < deduped[-1].x():
                        deduped[-1] = p
            else:
                deduped.append(p)
        self._cache[key] = deduped
        return deduped
    def _outline_x_at_y(self, samples_sorted, y, side, inset_px=0.0):
        if not samples_sorted:
            return 0.0
        if y <= samples_sorted[0].y():
            x = samples_sorted[0].x()
        elif y >= samples_sorted[-1].y():
            x = samples_sorted[-1].x()
        else:
            x = samples_sorted[-1].x()
            for p0, p1 in zip(samples_sorted, samples_sorted[1:]):
                y0 = p0.y()
                y1 = p1.y()
                if y0 <= y <= y1:
                    if abs(y1 - y0) < 1e-9:
                        x = p0.x()
                    else:
                        t = (y - y0) / (y1 - y0)
                        x = p0.x() + (p1.x() - p0.x()) * t
                    break
        if side == "left":
            return x + max(0.0, float(inset_px))
        return x - max(0.0, float(inset_px))
    def _outline_side_between(self, samples_sorted, y0, y1, side, inset_px=0.0):
        if y1 < y0:
            y0, y1 = y1, y0
        pts = [QPointF(self._outline_x_at_y(samples_sorted, y0, side, inset_px), y0)]
        for p in samples_sorted:
            if y0 < p.y() < y1:
                pts.append(QPointF(self._outline_x_at_y(samples_sorted, p.y(), side, inset_px), p.y()))
        pts.append(QPointF(self._outline_x_at_y(samples_sorted, y1, side, inset_px), y1))
        return pts
    def _clamp_outline_pair(self, left_pt, right_pt):
        if left_pt.x() <= right_pt.x():
            return left_pt, right_pt
        mid_x = 0.5 * (left_pt.x() + right_pt.x())
        y = 0.5 * (left_pt.y() + right_pt.y())
        return QPointF(mid_x, y), QPointF(mid_x, y)
    def _clamp_outline_sides(self, left, right):
        count = min(len(left), len(right))
        for i in range(count):
            left[i], right[i] = self._clamp_outline_pair(left[i], right[i])
        return left, right
    def _shape_path_from_current_outline(self, samples=2000, inset_px=0.0, tip_trim_px=0.0, tail_trim_px=0.0, left_inset_px=None, right_inset_px=None):
        if len(self.points) < 2:
            return QPainterPath()
        if left_inset_px is None:
            left_inset_px = inset_px
        if right_inset_px is None:
            right_inset_px = inset_px
        if (
            abs(float(left_inset_px)) < 1e-9
            and abs(float(right_inset_px)) < 1e-9
            and abs(float(tip_trim_px)) < 1e-9
            and abs(float(tail_trim_px)) < 1e-9
        ):
            return self.build_full_shape()
        tail_y = self.points[0].pos.y()
        tip_y = self.points[-1].pos.y()
        start_y = tip_y + max(0.0, tip_trim_px)
        end_y = tail_y - max(0.0, tail_trim_px)
        if end_y < start_y:
            return QPainterPath()

        right_samples = self._sorted_outline_side_samples("right", samples)
        left_samples = self._sorted_outline_side_samples("left", samples)
        right = self._outline_side_between(right_samples, start_y, end_y, "right", inset_px=right_inset_px)
        left = self._outline_side_between(left_samples, start_y, end_y, "left", inset_px=left_inset_px)
        left, right = self._clamp_outline_sides(left, right)
        if len(right) < 2 or len(left) < 2:
            return QPainterPath()
        return self._polygon_path(right + list(reversed(left)))
    def _shape_path_from_current_outline_between(self, y_start, y_end, samples=2000, inset_px=0.0, left_inset_px=None, right_inset_px=None):
        if len(self.points) < 2:
            return QPainterPath()
        if left_inset_px is None:
            left_inset_px = inset_px
        if right_inset_px is None:
            right_inset_px = inset_px
        if y_end < y_start:
            y_start, y_end = y_end, y_start
        right_samples = self._sorted_outline_side_samples("right", samples)
        left_samples = self._sorted_outline_side_samples("left", samples)
        right = self._outline_side_between(right_samples, y_start, y_end, "right", inset_px=right_inset_px)
        left = self._outline_side_between(left_samples, y_start, y_end, "left", inset_px=left_inset_px)
        left, right = self._clamp_outline_sides(left, right)
        if len(right) < 2 or len(left) < 2:
            return QPainterPath()
        return self._polygon_path(right + list(reversed(left)))
    def _polygon_path(self, pts):
        path = QPainterPath()
        if len(pts) < 3:
            return path
        poly = QPolygonF(pts)
        path.addPolygon(poly)
        path.closeSubpath()
        return path
    def _sample_cubic_bezier(self, p0, p1, p2, p3, samples):
        pts = []
        samples = max(2, int(samples))
        for i in range(samples + 1):
            t = i / samples
            omt = 1.0 - t
            x = (omt ** 3) * p0.x() + 3 * (omt ** 2) * t * p1.x() + 3 * omt * (t ** 2) * p2.x() + (t ** 3) * p3.x()
            y = (omt ** 3) * p0.y() + 3 * (omt ** 2) * t * p1.y() + 3 * omt * (t ** 2) * p2.y() + (t ** 3) * p3.y()
            pts.append(QPointF(x, y))
        return pts
    def _sorted_edge_samples(self, samples=2000):
        key = self._cache_key("sorted_edge_samples", samples)
        if key not in self._cache:
            self._cache[key] = sorted(self.sample_edge(samples), key=lambda p: p.y())
        return self._cache[key]
    def _half_width_at_y(self, samples_sorted, y, inset_px=0.0):
        if not samples_sorted:
            return 0.0
        if y <= samples_sorted[0].y():
            return max(0.0, samples_sorted[0].x() - inset_px)
        if y >= samples_sorted[-1].y():
            return max(0.0, samples_sorted[-1].x() - inset_px)
        for p0, p1 in zip(samples_sorted, samples_sorted[1:]):
            y0 = p0.y()
            y1 = p1.y()
            if y0 <= y <= y1:
                if abs(y1 - y0) < 1e-9:
                    x = max(p0.x(), p1.x())
                else:
                    t = (y - y0) / (y1 - y0)
                    x = p0.x() + (p1.x() - p0.x()) * t
                return max(0.0, x - inset_px)
        return max(0.0, samples_sorted[-1].x() - inset_px)
    def _half_outline_between(self, samples_sorted, y0, y1, inset_px=0.0):
        pts = [QPointF(self._half_width_at_y(samples_sorted, y0, inset_px), y0)]
        for p in samples_sorted:
            if y0 < p.y() < y1:
                pts.append(QPointF(max(0.0, p.x() - inset_px), p.y()))
        pts.append(QPointF(self._half_width_at_y(samples_sorted, y1, inset_px), y1))
        return pts
    def _sample_spline_through_points(self, anchors, samples_per_seg=14):
        anchors = [QPointF(p.x(), p.y()) for p in anchors]
        if len(anchors) < 2:
            return anchors
        pts = []
        samples_per_seg = max(4, int(samples_per_seg))
        for i in range(len(anchors) - 1):
            p0 = anchors[i - 1] if i > 0 else anchors[i]
            p1 = anchors[i]
            p2 = anchors[i + 1]
            p3 = anchors[i + 2] if i + 2 < len(anchors) else anchors[i + 1]
            c1 = QPointF(p1.x() + (p2.x() - p0.x()) / 6.0, p1.y() + (p2.y() - p0.y()) / 6.0)
            c2 = QPointF(p2.x() - (p3.x() - p1.x()) / 6.0, p2.y() - (p3.y() - p1.y()) / 6.0)
            seg = self._sample_cubic_bezier(p1, c1, c2, p2, samples_per_seg)
            if pts:
                seg = seg[1:]
            pts.extend(seg)
        return pts
    def _build_default_seam_center_point(self):
        return SeamControlPoint(QPointF(0.0, 0.0), QPointF(-14.0, 0.0), QPointF(14.0, 0.0))
    def _serialize_seam_point(self, point):
        if point is None:
            return None
        return {
            "pos": (point.pos.x(), point.pos.y()),
            "handle_in": (point.handle_in.x(), point.handle_in.y()),
            "handle_out": (point.handle_out.x(), point.handle_out.y()),
            "locked": bool(getattr(point, "locked", False)),
            "lock_direction": getattr(point, "lock_direction", None),
        }
    def _deserialize_one_seam_point(self, entry, fallback=None):
        if not entry:
            if fallback is not None:
                p = SeamControlPoint(fallback.pos, fallback.handle_in, fallback.handle_out)
                p.locked = bool(getattr(fallback, "locked", False))
                p.lock_direction = getattr(fallback, "lock_direction", None)
                return p
            return self._build_default_seam_center_point()
        pos = QPointF(*entry.get("pos", (0.0, 0.0)))
        handle_in = QPointF(*entry.get("handle_in", (pos.x() - 12.0, pos.y())))
        handle_out = QPointF(*entry.get("handle_out", (pos.x() + 12.0, pos.y())))
        p = SeamControlPoint(pos, handle_in, handle_out)
        p.locked = bool(entry.get("locked", getattr(p, "locked", False)))
        p.lock_direction = entry.get("lock_direction", getattr(p, "lock_direction", None))
        return p
    def _build_default_seam_points(self):
        return [
            SeamControlPoint(QPointF(22.0, 22.0), QPointF(8.0, 30.0), QPointF(34.0, 8.0)),
            SeamControlPoint(QPointF(48.0, -8.0), QPointF(36.0, -20.0), QPointF(64.0, -2.0)),
        ]
    def _normalize_seam_point_count(self, value):
        try:
            value = int(round(float(value)))
        except Exception:
            value = 3
        return max(0, min(3, value))
    def _get_seam_point_count(self, seam_name):
        if seam_name == "tip":
            value = getattr(self, "tip_seam_point_count", getattr(self, "seam_point_count", 3))
        else:
            value = getattr(self, "tail_seam_point_count", getattr(self, "seam_point_count", 3))
        return self._normalize_seam_point_count(value)
    def _active_seam_points(self, seam_name):
        pts = self.tip_seam_points if seam_name == "tip" else self.tail_seam_points
        count = max(0, min(len(pts), self._get_seam_point_count(seam_name) - 1))
        return pts[:count]
    def _serialize_seam_points(self, points):
        arr = []
        for p in points:
            arr.append({
                "pos": (p.pos.x(), p.pos.y()),
                "handle_in": (p.handle_in.x(), p.handle_in.y()),
                "handle_out": (p.handle_out.x(), p.handle_out.y()),
                "locked": bool(getattr(p, "locked", False)),
                "lock_direction": getattr(p, "lock_direction", None),
            })
        return arr
    def _deserialize_seam_points(self, entries, fallback=None):
        pts = []
        for entry in entries or []:
            pos = QPointF(*entry.get("pos", (0.0, 0.0)))
            handle_in = QPointF(*entry.get("handle_in", (pos.x() - 12.0, pos.y())))
            handle_out = QPointF(*entry.get("handle_out", (pos.x() + 12.0, pos.y())))
            p = SeamControlPoint(pos, handle_in, handle_out)
            p.locked = bool(entry.get("locked", getattr(p, "locked", False)))
            p.lock_direction = entry.get("lock_direction", getattr(p, "lock_direction", None))
            pts.append(p)
        if not pts:
            pts = self._build_default_seam_points()
        if fallback is not None:
            while len(pts) < len(fallback):
                src = fallback[len(pts)]
                p = SeamControlPoint(src.pos, src.handle_in, src.handle_out)
                p.locked = bool(getattr(src, "locked", False))
                p.lock_direction = getattr(src, "lock_direction", None)
                pts.append(p)
        return pts
    def _scale_seam_points(self, points, factor):
        for p in points:
            p.pos = QPointF(p.pos.x() * factor, p.pos.y() * factor)
            p.handle_in = QPointF(p.handle_in.x() * factor, p.handle_in.y() * factor)
            p.handle_out = QPointF(p.handle_out.x() * factor, p.handle_out.y() * factor)
    def _splitboard_seam_origin_world(self, seam_name, samples=500):
        if getattr(self, "outline_mode", "symmetric") != "splitboard":
            return None
        _tip_y, _tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
        seam_y = core_tip_start_y if seam_name == "tip" else core_tail_end_y
        left_inner_inset, _right_inner_inset = self._sidewall_inner_insets_px()
        left_samples = self._sorted_outline_side_samples("left", samples)
        inner_x = self._outline_x_at_y(left_samples, seam_y, "left", inset_px=left_inner_inset)
        return QPointF(max(0.0, float(inner_x)), float(seam_y))
    def _seam_origin_world(self, seam_name):
        data = self._get_seam_editor_data(seam_name)
        split_origin = self._splitboard_seam_origin_world(seam_name)
        if split_origin is not None:
            return split_origin
        return QPointF(0.0, data["y"])
    def _seam_center_local_for_display(self, seam_name):
        center_point = self.tip_seam_center if seam_name == "tip" else self.tail_seam_center
        if getattr(self, "outline_mode", "symmetric") != "splitboard":
            return center_point
        snapped = SeamControlPoint(
            QPointF(0.0, 0.0),
            QPointF(center_point.handle_in.x() - center_point.pos.x(), center_point.handle_in.y() - center_point.pos.y()),
            QPointF(center_point.handle_out.x() - center_point.pos.x(), center_point.handle_out.y() - center_point.pos.y()),
        )
        snapped.locked = getattr(center_point, "locked", False)
        snapped.lock_direction = getattr(center_point, "lock_direction", None)
        return snapped
    def _seam_local_to_world(self, seam_name, pt):
        data = self._get_seam_editor_data(seam_name)
        origin = self._seam_origin_world(seam_name)
        return QPointF(origin.x() + pt.x(), origin.y() + data["direction"] * pt.y())
    def _seam_world_to_local(self, seam_name, pt):
        data = self._get_seam_editor_data(seam_name)
        origin = self._seam_origin_world(seam_name)
        return QPointF(pt.x() - origin.x(), data["direction"] * (pt.y() - origin.y()))
    def _sample_cubic_chain(self, seam_points, end_x, center_point=None, samples_per_seg=18, flat_len=0.0):
        start_pos = QPointF(center_point.pos) if center_point is not None else QPointF(0.0, 0.0)
        path = QPainterPath(start_pos)
        end_x = float(end_x)
        flat_len = max(0.0, min(abs(end_x) * 0.35, float(flat_len)))
        curve_end_x = end_x - flat_len if end_x >= 0.0 else end_x + flat_len
        if not seam_points:
            start_out = QPointF(center_point.handle_out) if center_point is not None else QPointF(end_x * 0.35, 0.0)
            edge_in = QPointF(curve_end_x - max(10.0, abs(curve_end_x) * 0.22), 0.0)
            total_samples = max(24, int(samples_per_seg))
            path.cubicTo(start_out, edge_in, QPointF(curve_end_x, 0.0))
            pts = [path.pointAtPercent(i / total_samples) for i in range(total_samples + 1)]
            if flat_len > 1e-6:
                pts.append(QPointF(end_x, 0.0))
            return pts
        first = seam_points[0]
        start_out = QPointF(center_point.handle_out) if center_point is not None else QPointF(first.pos.x() * 0.35, first.pos.y() * 0.35)
        path.cubicTo(start_out, first.handle_in, first.pos)
        for i in range(len(seam_points) - 1):
            a = seam_points[i]
            b = seam_points[i + 1]
            path.cubicTo(a.handle_out, b.handle_in, b.pos)
        last = seam_points[-1]
        edge_in = QPointF(curve_end_x - max(10.0, abs(curve_end_x) * 0.22), 0.0)
        path.cubicTo(last.handle_out, edge_in, QPointF(curve_end_x, 0.0))
        pts = []
        total_segments = len(seam_points) + 1
        total_samples = max(24, samples_per_seg * total_segments)
        for i in range(total_samples + 1):
            pts.append(path.pointAtPercent(i / total_samples))
        if flat_len > 1e-6:
            pts.append(QPointF(end_x, 0.0))
        return pts
    def _sample_seam_center_to_side(self, y, center_x, side_x, direction, seam_name=None, samples_per_seg=18):
        seam_name = seam_name or ("tip" if direction < 0 else "tail")
        side_width = float(side_x) - float(center_x)
        if abs(side_width) <= 1e-6:
            return [QPointF(center_x, y)]
        sign = 1.0 if side_width >= 0.0 else -1.0
        width = abs(side_width)
        seam_count = self._get_seam_point_count(seam_name)
        if seam_count <= 0:
            return [QPointF(center_x, y), QPointF(side_x, y)]
        center_src = self.tip_seam_center if seam_name == "tip" else self.tail_seam_center
        splitboard_snap = getattr(self, "outline_mode", "symmetric") == "splitboard" and center_x >= -1e-6
        if splitboard_snap:
            center_pos = QPointF(0.0, 0.0)
            center_handle_in = QPointF(
                sign * (center_src.handle_in.x() - center_src.pos.x()),
                direction * (center_src.handle_in.y() - center_src.pos.y()),
            )
            center_handle_out = QPointF(
                sign * (center_src.handle_out.x() - center_src.pos.x()),
                direction * (center_src.handle_out.y() - center_src.pos.y()),
            )
        else:
            center_pos = QPointF(0.0, direction * center_src.pos.y())
            center_handle_in = QPointF(sign * center_src.handle_in.x(), direction * center_src.handle_in.y())
            center_handle_out = QPointF(sign * center_src.handle_out.x(), direction * center_src.handle_out.y())
        center_point = SeamControlPoint(
            center_pos,
            center_handle_in,
            center_handle_out,
        )
        side_points = []
        for p in self._active_seam_points(seam_name):
            side_points.append(
                SeamControlPoint(
                    QPointF(sign * p.pos.x(), direction * p.pos.y()),
                    QPointF(sign * p.handle_in.x(), direction * p.handle_in.y()),
                    QPointF(sign * p.handle_out.x(), direction * p.handle_out.y()),
                )
            )
        flat_len = min(14.0, max(5.0, width * 0.18))
        local = self._sample_cubic_chain(side_points, sign * width, center_point=center_point, samples_per_seg=samples_per_seg, flat_len=flat_len)
        return [QPointF(center_x + p.x(), y + p.y()) for p in local]
    def _sample_puzzle_seam(self, y, half_width, direction, seam_name=None, samples_per_seg=18):
        half_width = float(half_width)
        if half_width <= 0.0:
            return [QPointF(0.0, y)]
        right = self._sample_seam_center_to_side(y, 0.0, half_width, direction, seam_name=seam_name, samples_per_seg=samples_per_seg)
        left = [QPointF(-p.x(), p.y()) for p in reversed(right[1:])]
        return left + right
    def _sample_puzzle_seam_between(self, y, left_x, right_x, direction, seam_name=None, samples_per_seg=18):
        left_x = float(left_x)
        right_x = float(right_x)
        if right_x < left_x:
            left_x, right_x = right_x, left_x
        width = right_x - left_x
        if width <= 1e-6:
            return [QPointF(left_x, y)]
        if left_x >= -1e-6:
            return self._sample_seam_center_to_side(y, left_x, right_x, direction, seam_name=seam_name, samples_per_seg=samples_per_seg)
        if right_x <= 1e-6:
            return list(reversed(self._sample_seam_center_to_side(y, right_x, left_x, direction, seam_name=seam_name, samples_per_seg=samples_per_seg)))
        center_x = 0.5 * (left_x + right_x)
        half_width = 0.5 * width
        pts = self._sample_puzzle_seam(y, half_width, direction, seam_name=seam_name, samples_per_seg=samples_per_seg)
        return [QPointF(center_x + p.x(), p.y()) for p in pts]
    def _sidewall_thickness_for_side(self, side):
        if side == "left" and getattr(self, "outline_mode", "symmetric") == "splitboard":
            return float(getattr(self, "left_sidewall_thickness_px", self.sidewall_thickness_px))
        return float(self.sidewall_thickness_px)
    def _sidewall_inner_insets_px(self):
        return (
            float(self.edge_thickness_px) + self._sidewall_thickness_for_side("left"),
            float(self.edge_thickness_px) + self._sidewall_thickness_for_side("right"),
        )
    def _get_seam_editor_data(self, seam_name, samples=2000):
        tip_y, tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
        samples_sorted = self._sorted_edge_samples(samples)
        inset_px = self.edge_thickness_px + self.sidewall_thickness_px
        if seam_name == "tip":
            seam_y = core_tip_start_y
            direction = -1
        else:
            seam_y = core_tail_end_y
            direction = 1
        half_width = self._half_width_at_y(samples_sorted, seam_y, inset_px=inset_px)
        half_width = max(1.0, float(half_width))
        return {
            "name": seam_name,
            "y": seam_y,
            "direction": direction,
            "half_width": half_width,
            "point_count": self._get_seam_point_count(seam_name),
            "center_point": self.tip_seam_center if seam_name == "tip" else self.tail_seam_center,
            "points": self._active_seam_points(seam_name),
        }
    def get_seam_editor_handles(self):
        handles = []
        for seam_name in ("tip", "tail"):
            seam_count = self._get_seam_point_count(seam_name)
            center_point = self._seam_center_local_for_display(seam_name)
            if seam_count >= 1:
                handles.append({"seam": seam_name, "kind": "center_point", "index": -1, "pos": self._seam_local_to_world(seam_name, center_point.pos)})
                handles.append({"seam": seam_name, "kind": "center_handle_in", "index": -1, "pos": self._seam_local_to_world(seam_name, center_point.handle_in)})
                handles.append({"seam": seam_name, "kind": "center_handle_out", "index": -1, "pos": self._seam_local_to_world(seam_name, center_point.handle_out)})
            for idx, p in enumerate(self._active_seam_points(seam_name)):
                handles.append({"seam": seam_name, "kind": "point", "index": idx, "pos": self._seam_local_to_world(seam_name, p.pos)})
                handles.append({"seam": seam_name, "kind": "handle_in", "index": idx, "pos": self._seam_local_to_world(seam_name, p.handle_in)})
                handles.append({"seam": seam_name, "kind": "handle_out", "index": idx, "pos": self._seam_local_to_world(seam_name, p.handle_out)})
        return handles
    def _draw_seam_editor(self, painter):
        show_editor = self.show_core_shape or self.show_tip_tail_spacers
        if not show_editor or self.show_3d:
            return
        label_pen = QPen(QColor(255, 220, 120), 1)
        line_pen = QPen(QColor(255, 220, 120, 180), 1, Qt.PenStyle.DashLine)
        tangent_pen = QPen(QColor(180, 235, 255, 170), 1, Qt.PenStyle.DashLine)
        center_brush = QBrush(QColor(255, 255, 255, 130))
        painter.save()
        for seam_name in ("tip", "tail"):
            seam_count = self._get_seam_point_count(seam_name)
            data = self._get_seam_editor_data(seam_name)
            seam_y = data["y"]
            half_width = data["half_width"]
            center_point = self._seam_center_local_for_display(seam_name)
            center_local = center_point.pos
            center = self._seam_local_to_world(seam_name, center_local)
            center_in = self._seam_local_to_world(seam_name, center_point.handle_in)
            center_out = self._seam_local_to_world(seam_name, center_point.handle_out)
            painter.setPen(line_pen)
            painter.drawLine(QPointF(-half_width, seam_y), QPointF(half_width, seam_y))
            painter.setPen(QPen(QColor(255, 255, 255, 90), 1, Qt.PenStyle.DotLine))
            painter.drawLine(QPointF(0.0, seam_y - 35.0), QPointF(0.0, seam_y + 35.0))
            center_selected = self.selected_seam_handle and self.selected_seam_handle[0] == seam_name and self.selected_seam_handle[2] == "center_point"
            center_selected_kind = self.selected_seam_handle[2] if (self.selected_seam_handle and self.selected_seam_handle[0] == seam_name and self.selected_seam_handle[1] == -1) else None

            if seam_count >= 1:
                painter.setPen(tangent_pen)
                painter.drawLine(center, center_in)
                painter.drawLine(center, center_out)

                center_handle_pen = QPen(QColor(120, 230, 255), 1)
                center_handle_brush = QBrush(QColor(120, 230, 255))
                if center_selected_kind == "center_handle_in":
                    center_handle_pen = QPen(QColor(255, 0, 0, 220), 2)
                    center_handle_brush = QBrush(QColor(255, 160, 160))
                painter.setPen(center_handle_pen)
                painter.setBrush(center_handle_brush)
                painter.drawRect(QRectF(center_in.x() - 4.0, center_in.y() - 4.0, 8.0, 8.0))

                center_handle_pen = QPen(QColor(120, 230, 255), 1)
                center_handle_brush = QBrush(QColor(120, 230, 255))
                if center_selected_kind == "center_handle_out":
                    center_handle_pen = QPen(QColor(255, 0, 0, 220), 2)
                    center_handle_brush = QBrush(QColor(255, 160, 160))
                painter.setPen(center_handle_pen)
                painter.setBrush(center_handle_brush)
                painter.drawRect(QRectF(center_out.x() - 4.0, center_out.y() - 4.0, 8.0, 8.0))
            for idx, p in enumerate(data["points"]):
                wpos = self._seam_local_to_world(seam_name, p.pos)
                win = self._seam_local_to_world(seam_name, p.handle_in)
                wout = self._seam_local_to_world(seam_name, p.handle_out)

                painter.setPen(tangent_pen)
                painter.drawLine(wpos, win)
                painter.drawLine(wpos, wout)

                selected_kind = None
                if self.selected_seam_handle and self.selected_seam_handle[0] == seam_name and self.selected_seam_handle[1] == idx:
                    selected_kind = self.selected_seam_handle[2]

                if p.selected:
                    painter.setPen(QPen(QColor(255, 0, 0, 200), 3))
                    painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
                    painter.drawEllipse(wpos, 10, 10)

                if p.locked:
                    if p.lock_direction == "vertical":
                        point_pen = QPen(QColor(255, 0, 255, 200), 1)
                        point_brush = QBrush(QColor(255, 0, 255, 200))
                    elif p.lock_direction == "horizontal":
                        point_pen = QPen(QColor(0, 255, 255, 200), 1)
                        point_brush = QBrush(QColor(0, 255, 255, 200))
                    else:
                        point_pen = QPen(QColor(255, 255, 255, 200), 1)
                        point_brush = QBrush(QColor(255, 255, 255, 200))
                else:
                    point_pen = QPen(QColor(100, 100, 100, 200), 1)
                    point_brush = QBrush(QColor(100, 100, 100, 200))

                handle_pen = QPen(QColor(120, 230, 255), 1)
                handle_brush = QBrush(QColor(120, 230, 255))
                if selected_kind == "handle_in":
                    handle_pen = QPen(QColor(255, 0, 0, 220), 2)
                    handle_brush = QBrush(QColor(255, 160, 160))
                painter.setPen(handle_pen)
                painter.setBrush(handle_brush)
                painter.drawRect(QRectF(win.x() - 4.0, win.y() - 4.0, 8.0, 8.0))

                handle_pen = QPen(QColor(120, 230, 255), 1)
                handle_brush = QBrush(QColor(120, 230, 255))
                if selected_kind == "handle_out":
                    handle_pen = QPen(QColor(255, 0, 0, 220), 2)
                    handle_brush = QBrush(QColor(255, 160, 160))
                painter.setPen(handle_pen)
                painter.setBrush(handle_brush)
                painter.drawRect(QRectF(wout.x() - 4.0, wout.y() - 4.0, 8.0, 8.0))

                painter.setPen(line_pen)
                painter.drawLine(center, wpos)
                painter.drawLine(center, QPointF(-wpos.x(), wpos.y()))
                painter.setPen(point_pen)
                painter.setBrush(point_brush)
                painter.drawEllipse(wpos, 7, 7)
                painter.drawEllipse(QPointF(-wpos.x(), wpos.y()), 5, 5)

                painter.setPen(tangent_pen)
                painter.drawLine(QPointF(-wpos.x(), wpos.y()), QPointF(-win.x(), win.y()))
                painter.drawLine(QPointF(-wpos.x(), wpos.y()), QPointF(-wout.x(), wout.y()))
                painter.setPen(QPen(QColor(120, 230, 255), 1))
                painter.setBrush(QBrush(QColor(120, 230, 255)))
                painter.drawRect(QRectF(-win.x() - 4.0, win.y() - 4.0, 8.0, 8.0))
                painter.drawRect(QRectF(-wout.x() - 4.0, wout.y() - 4.0, 8.0, 8.0))
            if center_point.locked:
                if center_point.lock_direction == "vertical":
                    center_point_pen = QPen(QColor(255, 0, 255, 200), 1)
                    center_point_brush = QBrush(QColor(255, 0, 255, 200))
                elif center_point.lock_direction == "horizontal":
                    center_point_pen = QPen(QColor(0, 255, 255, 200), 1)
                    center_point_brush = QBrush(QColor(0, 255, 255, 200))
                else:
                    center_point_pen = QPen(QColor(255, 255, 255, 200), 1)
                    center_point_brush = QBrush(QColor(255, 255, 255, 200))
            else:
                center_point_pen = QPen(QColor(100, 100, 100, 200), 1)
                center_point_brush = QBrush(QColor(100, 100, 100, 200))
            if seam_count >= 1:
                if center_selected:
                    painter.setPen(QPen(QColor(255, 0, 0, 200), 3))
                    painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
                    painter.drawEllipse(center, 10, 10)
                painter.setBrush(center_point_brush)
                painter.setPen(center_point_pen)
                painter.drawEllipse(center, 6, 6)
            painter.setPen(label_pen)
            #painter.drawText(QPointF(half_width + 12.0, seam_y - 6.0), f"{seam_name.title()} seam")
        painter.restore()
    def _set_seam_handle_from_pos(self, seam_name, kind, index, pos):
        points = self.tip_seam_points if seam_name == "tip" else self.tail_seam_points
        local = self._seam_world_to_local(seam_name, pos)
        if kind == "center_point":
            center_point = self.tip_seam_center if seam_name == "tip" else self.tail_seam_center
            if getattr(self, "outline_mode", "symmetric") == "splitboard":
                center_point.pos = QPointF(0.0, 0.0)
                self._cache.clear()
                self.update()
                return
            delta = QPointF(0.0, local.y() - center_point.pos.y())
            center_point.pos = QPointF(0.0, local.y())
            center_point.handle_in += delta
            center_point.handle_out += delta
            self.seam_depth_px = max([2.0] + [abs(p.pos.y()) for p in [self.tip_seam_center, self.tail_seam_center] + self.tip_seam_points + self.tail_seam_points])
            self._cache.clear()
            if self.owner_window is not None:
                self.owner_window.sync_seam_editor_widgets()
            self.update()
            return
        elif kind in ("center_handle_in", "center_handle_out"):
            center_point = self.tip_seam_center if seam_name == "tip" else self.tail_seam_center
            if getattr(self, "outline_mode", "symmetric") == "splitboard":
                center_point.pos = QPointF(0.0, 0.0)
            if kind == "center_handle_in":
                center_point.handle_in = QPointF(local)
                if center_point.locked:
                    dx = center_point.pos.x() - local.x()
                    dy = center_point.pos.y() - local.y()
                    center_point.handle_out = QPointF(center_point.pos.x() + dx, center_point.pos.y() + dy)
                if center_point.lock_direction == "vertical":
                    dy = center_point.pos.y() - local.y()
                    center_point.handle_out = QPointF(center_point.pos.x(), center_point.pos.y() + dy)
                    center_point.handle_in = QPointF(center_point.pos.x(), center_point.pos.y() - dy)
                elif center_point.lock_direction == "horizontal":
                    dx = center_point.pos.x() - local.x()
                    center_point.handle_out = QPointF(center_point.pos.x() + dx, center_point.pos.y())
                    center_point.handle_in = QPointF(center_point.pos.x() - dx, center_point.pos.y())
            else:
                center_point.handle_out = QPointF(local)
                if center_point.locked:
                    dx = center_point.pos.x() - local.x()
                    dy = center_point.pos.y() - local.y()
                    center_point.handle_in = QPointF(center_point.pos.x() + dx, center_point.pos.y() + dy)
                if center_point.lock_direction == "vertical":
                    dy = center_point.pos.y() - local.y()
                    center_point.handle_out = QPointF(center_point.pos.x(), center_point.pos.y() - dy)
                    center_point.handle_in = QPointF(center_point.pos.x(), center_point.pos.y() + dy)
                elif center_point.lock_direction == "horizontal":
                    dx = center_point.pos.x() - local.x()
                    center_point.handle_out = QPointF(center_point.pos.x() - dx, center_point.pos.y())
                    center_point.handle_in = QPointF(center_point.pos.x() + dx, center_point.pos.y())
            self._cache.clear()
            if self.owner_window is not None:
                self.owner_window.sync_seam_editor_widgets()
            self.update()
            return
        if index < 0 or index >= len(points):
            return
        target = points[index]
        if kind == "point":
            delta = local - target.pos
            target.pos = QPointF(local)
            target.handle_in += delta
            target.handle_out += delta
        elif kind == "handle_in":
            target.handle_in = QPointF(local)
            if target.locked:
                dx = target.pos.x() - local.x()
                dy = target.pos.y() - local.y()
                target.handle_out = QPointF(target.pos.x() + dx, target.pos.y() + dy)
            if target.lock_direction == "vertical":
                dy = target.pos.y() - local.y()
                target.handle_out = QPointF(target.pos.x(), target.pos.y() + dy)
                target.handle_in = QPointF(target.pos.x(), target.pos.y() - dy)
            elif target.lock_direction == "horizontal":
                dx = target.pos.x() - local.x()
                target.handle_out = QPointF(target.pos.x() + dx, target.pos.y())
                target.handle_in = QPointF(target.pos.x() - dx, target.pos.y())
        elif kind == "handle_out":
            target.handle_out = QPointF(local)
            if target.locked:
                dx = target.pos.x() - local.x()
                dy = target.pos.y() - local.y()
                target.handle_in = QPointF(target.pos.x() + dx, target.pos.y() + dy)
            if target.lock_direction == "vertical":
                dy = target.pos.y() - local.y()
                target.handle_out = QPointF(target.pos.x(), target.pos.y() - dy)
                target.handle_in = QPointF(target.pos.x(), target.pos.y() + dy)
            elif target.lock_direction == "horizontal":
                dx = target.pos.x() - local.x()
                target.handle_out = QPointF(target.pos.x() - dx, target.pos.y())
                target.handle_in = QPointF(target.pos.x() + dx, target.pos.y())
        self.seam_depth_px = max([2.0] + [abs(p.pos.y()) for p in [self.tip_seam_center, self.tail_seam_center] + self.tip_seam_points + self.tail_seam_points])
        self._cache.clear()
        if self.owner_window is not None:
            self.owner_window.sync_seam_editor_widgets()
        self.update()
    def _build_region_path(self, y_start, y_end, inset_px=0.0, top_seam=False, top_direction=-1, bottom_seam=False, bottom_direction=1, samples=2000, left_inset_px=None, right_inset_px=None):
        if y_end < y_start:
            y_start, y_end = y_end, y_start
            top_seam, bottom_seam = bottom_seam, top_seam
            top_direction, bottom_direction = bottom_direction, top_direction
        if left_inset_px is None:
            left_inset_px = inset_px
        if right_inset_px is None:
            right_inset_px = inset_px

        right_samples = self._sorted_outline_side_samples("right", samples)
        left_samples = self._sorted_outline_side_samples("left", samples)
        right = self._outline_side_between(right_samples, y_start, y_end, "right", inset_px=right_inset_px)
        left = self._outline_side_between(left_samples, y_start, y_end, "left", inset_px=left_inset_px)
        left, right = self._clamp_outline_sides(left, right)
        if len(right) < 2 or len(left) < 2:
            return QPainterPath()

        top = self._sample_puzzle_seam_between(y_start, left[0].x(), right[0].x(), top_direction, "tip" if top_direction < 0 else "tail") if top_seam else [left[0], right[0]]
        bottom_lr = self._sample_puzzle_seam_between(y_end, left[-1].x(), right[-1].x(), bottom_direction, "tip" if bottom_direction < 0 else "tail") if bottom_seam else [left[-1], right[-1]]
        bottom = list(reversed(bottom_lr))

        polygon = list(top)
        polygon.extend(right[1:])
        polygon.extend(bottom[1:])
        polygon.extend(reversed(left[1:-1]))
        return self._polygon_path(polygon)
    def _path_segment_between_y(self, path, y0, y1, samples=2000, reverse=False):
        raw = self._sample_path_points(path, max(120, int(samples)))
        if reverse:
            raw = list(reversed(raw))
        if len(raw) < 2:
            return raw
        low = min(float(y0), float(y1))
        high = max(float(y0), float(y1))

        def inside(pt):
            return low - 1e-6 <= pt.y() <= high + 1e-6

        def interpolate_at_y(a, b, y):
            dy = b.y() - a.y()
            if abs(dy) <= 1e-9:
                return QPointF(a)
            t = (float(y) - a.y()) / dy
            t = max(0.0, min(1.0, t))
            return QPointF(a.x() + (b.x() - a.x()) * t, float(y))

        def append_unique(target, pt, eps=1e-6):
            if not target or abs(target[-1].x() - pt.x()) > eps or abs(target[-1].y() - pt.y()) > eps:
                target.append(QPointF(pt))

        pts = []
        if inside(raw[0]):
            append_unique(pts, raw[0])
        for a, b in zip(raw, raw[1:]):
            ay = a.y()
            by = b.y()
            crossings = []
            for boundary_y in (low, high):
                if (ay - boundary_y) * (by - boundary_y) < 0.0:
                    t = (boundary_y - ay) / (by - ay)
                    crossings.append((t, boundary_y))
            for _t, boundary_y in sorted(crossings):
                append_unique(pts, interpolate_at_y(a, b, boundary_y))
            if inside(b):
                append_unique(pts, b)
        return pts
    def _build_spacer_region_path(self, y_start, y_end, seam_at_top=False, seam_direction=1, seam_inset_px=0.0, samples=2000, left_seam_inset_px=None, right_seam_inset_px=None):
        if y_end < y_start:
            y_start, y_end = y_end, y_start
            seam_at_top = not seam_at_top
        if left_seam_inset_px is None:
            left_seam_inset_px = seam_inset_px
        if right_seam_inset_px is None:
            right_seam_inset_px = seam_inset_px

        right_samples = self._sorted_outline_side_samples("right", samples)
        left_samples = self._sorted_outline_side_samples("left", samples)

        eps = 1e-6
        def append_unique(target, pts, eps=1e-6):
            for pt in pts:
                if not target or abs(target[-1].x() - pt.x()) > eps or abs(target[-1].y() - pt.y()) > eps:
                    target.append(QPointF(pt))

        if seam_at_top:
            seam_y = y_start
            inner_l = QPointF(self._outline_x_at_y(left_samples, seam_y, "left", inset_px=left_seam_inset_px), seam_y)
            inner_r = QPointF(self._outline_x_at_y(right_samples, seam_y, "right", inset_px=right_seam_inset_px), seam_y)
            inner_l, inner_r = self._clamp_outline_pair(inner_l, inner_r)
            seam_lr = self._sample_puzzle_seam_between(seam_y, inner_l.x(), inner_r.x(), seam_direction)
            right_outer = self._path_segment_between_y(self.build_edge_path(), seam_y, y_end, samples=samples, reverse=True)
            left_outer = self._path_segment_between_y(self.build_inner_or_left_edge_path(), seam_y, y_end, samples=samples, reverse=False)
            if len(right_outer) < 2 or len(left_outer) < 2 or not seam_lr:
                return QPainterPath()
            polygon = []
            append_unique(polygon, seam_lr)
            if right_outer and math.hypot(right_outer[0].x() - inner_r.x(), right_outer[0].y() - inner_r.y()) > eps:
                append_unique(polygon, [right_outer[0]])
            append_unique(polygon, right_outer[1:])
            append_unique(polygon, reversed(left_outer))
            return self._polygon_path(polygon)
        else:
            seam_y = y_end
            inner_l = QPointF(self._outline_x_at_y(left_samples, seam_y, "left", inset_px=left_seam_inset_px), seam_y)
            inner_r = QPointF(self._outline_x_at_y(right_samples, seam_y, "right", inset_px=right_seam_inset_px), seam_y)
            inner_l, inner_r = self._clamp_outline_pair(inner_l, inner_r)
            seam_lr = self._sample_puzzle_seam_between(seam_y, inner_l.x(), inner_r.x(), seam_direction)
            right_tip_to_seam = self._path_segment_between_y(self.build_edge_path(), y_start, seam_y, samples=samples, reverse=True)
            left_tip_to_seam = self._path_segment_between_y(self.build_inner_or_left_edge_path(), y_start, seam_y, samples=samples, reverse=False)
            if len(right_tip_to_seam) < 2 or len(left_tip_to_seam) < 2 or not seam_lr:
                return QPainterPath()
            polygon = []
            append_unique(polygon, seam_lr)
            append_unique(polygon, reversed(right_tip_to_seam))
            append_unique(polygon, left_tip_to_seam)
            return self._polygon_path(polygon)
    def _build_sidewall_between_path(self, y_start, y_end, samples=2000):
        left_inner_inset, right_inner_inset = self._sidewall_inner_insets_px()
        outer = self._shape_path_from_current_outline_between(
            y_start,
            y_end,
            samples=samples,
            left_inset_px=0.0,
            right_inset_px=0.0,
        )
        inner = self._shape_path_from_current_outline_between(
            y_start,
            y_end,
            samples=samples,
            left_inset_px=left_inner_inset,
            right_inset_px=right_inner_inset,
        )
        return outer.subtracted(inner)
    def _base_material_side_trace(self, path, side, samples, tip_trim_y, tail_trim_y, reverse=False, centerline=False):
        raw = self._sample_path_points(path, max(120, int(samples)))
        if reverse:
            raw = list(reversed(raw))
        if not raw:
            return []

        tip_trim_y = float(tip_trim_y)
        tail_trim_y = float(tail_trim_y)
        edge_thickness = max(0.0, float(getattr(self, "edge_thickness_px", 0.0)))

        def in_edge_zone(y):
            return tip_trim_y <= float(y) <= tail_trim_y

        def point_for_state(pt, inside_edge_zone):
            if centerline or not inside_edge_zone or edge_thickness <= 1e-9:
                return QPointF(pt)
            if side == "left":
                return QPointF(pt.x() + edge_thickness, pt.y())
            return QPointF(pt.x() - edge_thickness, pt.y())

        def interpolate_at_y(a, b, y):
            dy = b.y() - a.y()
            if abs(dy) <= 1e-9:
                return QPointF(a)
            t = (float(y) - a.y()) / dy
            t = max(0.0, min(1.0, t))
            return QPointF(a.x() + (b.x() - a.x()) * t, float(y))

        def append_unique(target, pt, eps=1e-6):
            if not target or abs(target[-1].x() - pt.x()) > eps or abs(target[-1].y() - pt.y()) > eps:
                target.append(QPointF(pt))

        def raw_point_at_y(y):
            y = float(y)
            for p0, p1 in zip(raw, raw[1:]):
                y0 = p0.y()
                y1 = p1.y()
                if min(y0, y1) - 1e-6 <= y <= max(y0, y1) + 1e-6:
                    if abs(y1 - y0) <= 1e-9:
                        return QPointF(p0)
                    t = (y - y0) / (y1 - y0)
                    t = max(0.0, min(1.0, t))
                    return QPointF(p0.x() + (p1.x() - p0.x()) * t, y)
            return QPointF(min(raw, key=lambda p: abs(p.y() - y)))

        def cubic_point(p0, p1, p2, p3, t):
            omt = 1.0 - t
            return QPointF(
                (omt ** 3) * p0.x() + 3.0 * (omt ** 2) * t * p1.x() + 3.0 * omt * (t ** 2) * p2.x() + (t ** 3) * p3.x(),
                (omt ** 3) * p0.y() + 3.0 * (omt ** 2) * t * p1.y() + 3.0 * omt * (t ** 2) * p2.y() + (t ** 3) * p3.y(),
            )

        def pop_after_y(target, y_limit, y_direction):
            if not target:
                return
            if y_direction > 0:
                while len(target) > 1 and target[-1].y() > y_limit:
                    target.pop()
            else:
                while len(target) > 1 and target[-1].y() < y_limit:
                    target.pop()

        radius = max(0.0, float(getattr(self, "base_edge_corner_min_radius_px", 0.0)))
        transition_radius = 0.0
        if radius > 1e-9 and not centerline and edge_thickness > 1e-9 and tail_trim_y > tip_trim_y:
            transition_radius = min(radius, (tail_trim_y - tip_trim_y) * 0.45)

        traced = []
        state = in_edge_zone(raw[0].y())
        append_unique(traced, point_for_state(raw[0], state))
        skip_until_y = None
        skip_direction = 0
        for a, b in zip(raw, raw[1:]):
            state = in_edge_zone(a.y())
            crossings = []
            ay = a.y()
            by = b.y()
            for boundary_y in (tip_trim_y, tail_trim_y):
                if (ay - boundary_y) * (by - boundary_y) < 0.0:
                    t = (boundary_y - ay) / (by - ay)
                    crossings.append((t, boundary_y))
            for _t, boundary_y in sorted(crossings):
                pt = interpolate_at_y(a, b, boundary_y)
                new_state = not state
                y_direction = 1 if by >= ay else -1
                if transition_radius > 1e-9:
                    before_y = max(min(raw[0].y(), raw[-1].y()), min(max(raw[0].y(), raw[-1].y()), boundary_y - y_direction * transition_radius))
                    after_y = max(min(raw[0].y(), raw[-1].y()), min(max(raw[0].y(), raw[-1].y()), boundary_y + y_direction * transition_radius))
                    start_pt = point_for_state(raw_point_at_y(before_y), state)
                    end_pt = point_for_state(raw_point_at_y(after_y), new_state)
                    control_1 = point_for_state(pt, state)
                    control_2 = point_for_state(pt, new_state)
                    pop_after_y(traced, before_y, y_direction)
                    append_unique(traced, start_pt)
                    for step in range(1, 11):
                        append_unique(traced, cubic_point(start_pt, control_1, control_2, end_pt, step / 10.0))
                    skip_until_y = after_y
                    skip_direction = y_direction
                else:
                    append_unique(traced, point_for_state(pt, state))
                    append_unique(traced, point_for_state(pt, new_state))
                    skip_until_y = None
                    skip_direction = 0
                state = new_state
            if skip_until_y is not None:
                if (skip_direction > 0 and b.y() < skip_until_y) or (skip_direction < 0 and b.y() > skip_until_y):
                    continue
                skip_until_y = None
                skip_direction = 0
            append_unique(traced, point_for_state(b, in_edge_zone(b.y())))
        return traced
    # Derived Shapes
    def build_base_material_path(self, samples=2000):
        key = self._cache_key("base_path", samples)
        if key not in self._cache:
            if getattr(self, "outline_mode", "symmetric") == "splitboard":
                self._cache[key] = self._build_splitboard_base_material_path(samples)
                return self._cache[key]
            tail_y = self.points[0].pos.y()
            tip_y = self.points[-1].pos.y()
            dovetail_bounds = self._current_dovetail_length_y_bounds()
            if dovetail_bounds is not None:
                tail_y, tip_y = dovetail_bounds
            tip_trim_y = max(tip_y, min(tail_y, self.points[-1].pos.y() + max(0.0, self.edge_inlay_tip_trim_px)))
            tail_trim_y = max(tip_y, min(tail_y, self.points[0].pos.y() - max(0.0, self.edge_inlay_tail_trim_px)))
            if tail_trim_y < tip_trim_y:
                mid_y = 0.5 * (tip_trim_y + tail_trim_y)
                tip_trim_y = mid_y
                tail_trim_y = mid_y

            polygon = []
            polygon.extend(self._base_material_side_trace(self.build_edge_path(), "right", samples, tip_trim_y, tail_trim_y, reverse=True))
            polygon.extend(self._base_material_side_trace(self.build_inner_or_left_edge_path(), "left", samples, tip_trim_y, tail_trim_y, reverse=True))
            self._cache[key] = self._polygon_path(polygon)
        return self._cache[key]
    def _build_splitboard_base_material_path(self, samples=2000):
        if len(self.points) < 2:
            return QPainterPath()

        tip_y = self.points[-1].pos.y()
        tail_y = self.points[0].pos.y()
        centerline_tip_y = tip_y
        centerline_tail_y = tail_y
        dovetail_bounds = self._current_dovetail_length_y_bounds()
        if dovetail_bounds is not None:
            tail_y, tip_y = dovetail_bounds
        tip_trim_y = max(tip_y, min(tail_y, self.points[-1].pos.y() + max(0.0, self.edge_inlay_tip_trim_px)))
        tail_trim_y = max(tip_y, min(tail_y, self.points[0].pos.y() - max(0.0, self.edge_inlay_tail_trim_px)))
        if tail_trim_y < tip_trim_y:
            mid_y = 0.5 * (tip_trim_y + tail_trim_y)
            tip_trim_y = mid_y
            tail_trim_y = mid_y

        polygon = []
        polygon.extend(self._base_material_side_trace(self.build_edge_path(), "right", samples, tip_trim_y, tail_trim_y, reverse=True))
        if bool(getattr(self, "include_splitboard_inside_edge", True)):
            centerline_path = QPainterPath()
            centerline_path.moveTo(QPointF(0.0, centerline_tail_y))
            centerline_path.lineTo(QPointF(0.0, centerline_tip_y))
            polygon.extend(self._base_material_side_trace(centerline_path, "left", samples, tip_trim_y, tail_trim_y))
        else:
            # The split seam itself ends at the editable outline endpoints. The
            # outer edge can pass beyond those endpoints in a dovetail, but extending
            # the centerline to the dovetail extrema creates a small exterior
            # vertical toolpath segment at the split seam.
            polygon.extend([QPointF(0.0, centerline_tail_y), QPointF(0.0, centerline_tip_y)])
        return self._polygon_path(polygon)
    def _mirror_path_to_second_ski(self, path, gap_px=10.0):
        if path.isEmpty():
            return path
        outline = self.build_full_shape()
        bounds = outline.boundingRect() if not outline.isEmpty() else path.boundingRect()
        transform = QTransform()
        if getattr(self, "outline_mode", "symmetric") == "snowboard":
            transform.translate(2.0 * bounds.right() + float(gap_px) + 100.0, 0.0)
        else:
            transform.translate(2.0 * bounds.left() - float(gap_px), 0.0)
        transform.scale(-1.0, 1.0)
        return transform.map(path)
    def build_left_base_material_path(self, samples=2000):
        key = self._cache_key("left_base_path", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_base_material_path(samples))
        return self._cache[key]
    def build_both_base_material_paths(self, samples=2000):
        key = self._cache_key("both_base_paths", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_base_material_path(samples))
            path.addPath(self.build_left_base_material_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_left_tip_spacer_path(self, samples=2000):
        key = self._cache_key("left_tip_spacer", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_tip_spacer_path(samples))
        return self._cache[key]
    def build_both_tip_spacer_paths(self, samples=2000):
        key = self._cache_key("both_tip_spacers", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_tip_spacer_path(samples))
            path.addPath(self.build_left_tip_spacer_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_left_tail_spacer_path(self, samples=2000):
        key = self._cache_key("left_tail_spacer", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_tail_spacer_path(samples))
        return self._cache[key]
    def build_both_tail_spacer_paths(self, samples=2000):
        key = self._cache_key("both_tail_spacers", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_tail_spacer_path(samples))
            path.addPath(self.build_left_tail_spacer_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def _build_core_spacer_seam_path(self, seam_name, samples=2000):
        seam_name = "tip" if seam_name == "tip" else "tail"
        key = self._cache_key(f"{seam_name}_core_spacer_seam", samples)
        if key not in self._cache:
            _tip_y, _tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
            seam_y = core_tip_start_y if seam_name == "tip" else core_tail_end_y
            direction = -1 if seam_name == "tip" else 1
            left_inset_px, right_inset_px = self._sidewall_inner_insets_px()
            left_samples = self._sorted_outline_side_samples("left", samples)
            right_samples = self._sorted_outline_side_samples("right", samples)
            inner_l = QPointF(self._outline_x_at_y(left_samples, seam_y, "left", inset_px=left_inset_px), seam_y)
            inner_r = QPointF(self._outline_x_at_y(right_samples, seam_y, "right", inset_px=right_inset_px), seam_y)
            inner_l, inner_r = self._clamp_outline_pair(inner_l, inner_r)
            pts = self._sample_puzzle_seam_between(seam_y, inner_l.x(), inner_r.x(), direction, seam_name=seam_name, samples_per_seg=24)
            path = QPainterPath()
            if pts:
                path.moveTo(pts[0])
                for pt in pts[1:]:
                    path.lineTo(pt)
            self._cache[key] = path
        return self._cache[key]
    def build_tip_core_seam_path(self, samples=2000):
        return self._build_core_spacer_seam_path("tip", samples=samples)
    def build_tail_core_seam_path(self, samples=2000):
        return self._build_core_spacer_seam_path("tail", samples=samples)
    def build_left_tip_core_seam_path(self, samples=2000):
        key = self._cache_key("left_tip_core_seam", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_tip_core_seam_path(samples))
        return self._cache[key]
    def build_left_tail_core_seam_path(self, samples=2000):
        key = self._cache_key("left_tail_core_seam", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_tail_core_seam_path(samples))
        return self._cache[key]
    def build_both_tip_core_seam_paths(self, samples=2000):
        key = self._cache_key("both_tip_core_seams", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_tip_core_seam_path(samples))
            path.addPath(self.build_left_tip_core_seam_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_both_tail_core_seam_paths(self, samples=2000):
        key = self._cache_key("both_tail_core_seams", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_tail_core_seam_path(samples))
            path.addPath(self.build_left_tail_core_seam_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_left_sidewall_spacer_shell_path(self, samples=2000):
        key = self._cache_key("left_sidewall_spacer_shell", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_sidewall_spacer_shell_path(samples))
        return self._cache[key]
    def build_both_sidewall_spacer_shell_paths(self, samples=2000):
        key = self._cache_key("both_sidewall_spacer_shells", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_sidewall_spacer_shell_path(samples))
            path.addPath(self.build_left_sidewall_spacer_shell_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_core_footprint_path(self, samples=2000):
        key = self._cache_key("core_footprint", samples)
        if key not in self._cache:
            tip_y, tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
            left_inset_px, right_inset_px = self._sidewall_inner_insets_px()
            self._cache[key] = self._build_region_path(
                core_tip_start_y,
                core_tail_end_y,
                left_inset_px=left_inset_px,
                right_inset_px=right_inset_px,
                top_seam=True,
                top_direction=-1,
                bottom_seam=True,
                bottom_direction=1,
                samples=samples,
            )
        return self._cache[key]
    def build_left_core_footprint_path(self, samples=2000):
        key = self._cache_key("left_core_footprint", samples)
        if key not in self._cache:
            self._cache[key] = self._mirror_path_to_second_ski(self.build_core_footprint_path(samples))
        return self._cache[key]
    def build_both_core_footprint_paths(self, samples=2000):
        key = self._cache_key("both_core_footprints", samples)
        if key not in self._cache:
            path = QPainterPath()
            path.addPath(self.build_core_footprint_path(samples))
            path.addPath(self.build_left_core_footprint_path(samples))
            self._cache[key] = path
        return self._cache[key]
    def build_edge_inlay_path(self, samples=2000):
        key = self._cache_key("edge_inlay", samples)
        if key not in self._cache:
            outer = self._shape_path_from_current_outline(
                samples,
                inset_px=0,
                tip_trim_px=self.edge_inlay_tip_trim_px,
                tail_trim_px=self.edge_inlay_tail_trim_px,
            )
            inner = self._shape_path_from_current_outline(
                samples,
                inset_px=self.edge_thickness_px,
                tip_trim_px=self.edge_inlay_tip_trim_px,
                tail_trim_px=self.edge_inlay_tail_trim_px,
            )
            self._cache[key] = outer.subtracted(inner)
        return self._cache[key]
    def build_sidewall_path(self, samples=2000):
        key = self._cache_key("sidewall", samples)
        if key not in self._cache:
            _tip_y, _tail_y, core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
            self._cache[key] = self._build_sidewall_between_path(core_tip_start_y, core_tail_end_y, samples=samples)
        return self._cache[key]
    def build_tip_spacer_path(self, samples=2000):
        key = self._cache_key("tip_spacer", samples)
        if key not in self._cache:
            tip_y, tail_y, _core_tip_start_y, _core_tail_end_y = self.get_core_trim_boundaries_y(include_dovetail_bounds=True)
            _base_tip_y, _base_tail_y, core_tip_start_y, _core_tail_end_y = self.get_core_trim_boundaries_y()
            left_seam_inset_px, right_seam_inset_px = self._sidewall_inner_insets_px()
            self._cache[key] = self._build_spacer_region_path(
                tip_y,
                core_tip_start_y,
                seam_at_top=False,
                seam_direction=-1,
                left_seam_inset_px=left_seam_inset_px,
                right_seam_inset_px=right_seam_inset_px,
                samples=samples,
            )
        return self._cache[key]
    def build_tail_spacer_path(self, samples=2000):
        key = self._cache_key("tail_spacer", samples)
        if key not in self._cache:
            tip_y, tail_y, _core_tip_start_y, _core_tail_end_y = self.get_core_trim_boundaries_y(include_dovetail_bounds=True)
            _base_tip_y, _base_tail_y, _core_tip_start_y, core_tail_end_y = self.get_core_trim_boundaries_y()
            left_seam_inset_px, right_seam_inset_px = self._sidewall_inner_insets_px()
            self._cache[key] = self._build_spacer_region_path(
                core_tail_end_y,
                tail_y,
                seam_at_top=True,
                seam_direction=1,
                left_seam_inset_px=left_seam_inset_px,
                right_seam_inset_px=right_seam_inset_px,
                samples=samples,
            )
        return self._cache[key]
    def build_sidewall_spacer_shell_path(self, samples=2000):
        key = self._cache_key("sidewall_spacer_shell", samples)
        if key not in self._cache:
            core = self.build_core_footprint_path(samples)

            # Shell is the non-core construction perimeter: sidewalls plus
            # tip/tail spacers. Subtract core last so splitboard/asymmetric
            # side-specific insets leave both sidewall cutouts intact.
            shell = self.build_sidewall_path(samples)
            shell = shell.united(self.build_tip_spacer_path(samples))
            shell = shell.united(self.build_tail_spacer_path(samples))
            self._cache[key] = shell.subtracted(core).simplified()
        return self._cache[key]
    # Measurement functions
    def sample_edge(self, samples=1000):
        key = self._cache_key("sample_edge", samples)
        if key not in self._cache:
            path = self.build_edge_path()
            pts = []
            for i in range(samples + 1):
                percent = i / samples
                pt = path.pointAtPercent(percent)
                pts.append(QPointF(pt.x(), pt.y()))
            self._cache[key] = pts
        return self._cache[key]
    def width_at_y(self, y):

        pts = self.sample_edge()

        closest = min(pts, key=lambda p: abs(p.y() - y))
        return abs(closest.x()) * 2 / PIXELS_PER_CM
    def get_tip_width(self):

        pts = [p for p in self.sample_edge() if p.y() < 0]
        if not pts:
            pts = self.sample_edge()
        pt = max(pts, key=lambda p: abs(p.x()))
        return 10*abs(pt.x()) * 2 / PIXELS_PER_CM
    def get_tail_width(self):
        pts = [p for p in self.sample_edge() if p.y() > 0]
        if not pts:
            pts = self.sample_edge()
        pt = max(pts, key=lambda p: abs(p.x()))
        return 10*abs(pt.x()) * 2 / PIXELS_PER_CM
    def get_waist_width(self):

        pts = self.sample_edge()
        if not pts:
            return 0.0

        tip_pts = [p for p in pts if p.y() < 0]
        tail_pts = [p for p in pts if p.y() > 0]
        if not tip_pts or not tail_pts:
            pt = min(pts, key=lambda p: abs(p.x()))
            return 10*abs(pt.x()) * 2 / PIXELS_PER_CM

        tip = max(tip_pts, key=lambda p: abs(p.x()))
        tail = max(tail_pts, key=lambda p: abs(p.x()))

        y_min = min(tip.y(), tail.y())
        y_max = max(tip.y(), tail.y())
        mid_pts = [p for p in pts if y_min <= p.y() <= y_max]
        if not mid_pts:
            mid_pts = pts

        pt = min(mid_pts, key=lambda p: abs(p.x()))
        return 10*abs(pt.x()) * 2 / PIXELS_PER_CM
    def get_effective_edge(self):

        pts = self.sample_edge()

        length = 0

        for i in range(len(pts) - 1):
            dx = pts[i+1].x() - pts[i].x()
            dy = pts[i+1].y() - pts[i].y()
            length += math.hypot(dx, dy)

        return length / PIXELS_PER_CM
    def get_turning_radius(self):
        return self.get_turning_radius_for_points(self.points)

    def get_turning_radius_for_points(self, points):
        if len(points) < 4:
            return 0.0

        # Match the turning-radius visualizer exactly by using the same
        # three control points that define the displayed sidecut circle.
        A = points[1].pos
        B = points[2].pos
        C = points[3].pos

        return self.circle_radius(A, B, C)
    def circle_radius(self, A, B, C):
        ax, ay = A.x(), A.y()
        bx, by = B.x(), B.y()
        cx, cy = C.x(), C.y()

        d = 2*(ax*(by-cy)+bx*(cy-ay)+cx*(ay-by))

        if abs(d) < 0.001:
            return 0

        ux = ((ax*ax+ay*ay)*(by-cy)+(bx*bx+by*by)*(cy-ay)+(cx*cx+cy*cy)*(ay-by))/d
        uy = ((ax*ax+ay*ay)*(cx-bx)+(bx*bx+by*by)*(ax-cx)+(cx*cx+cy*cy)*(bx-ax))/d

        r = math.hypot(ax-ux, ay-uy)

        return r / PIXELS_PER_CM
    # 3D Maths

        pts = self.get_camber_thickness_points_cm()

        if not pts:
            return 0

        closest = pts[0]

        for p in pts:
            if abs(p[0] - x) < abs(closest[0] - x):
                closest = p

        return closest[1]
    def get_camber_at_length(self, length_cm):

        pts = self.get_camber_thickness_points_cm()

        if not pts:
            return 0.0

        return self._interp_profile_at_length(length_cm, pts)

        if not outline:
            return 0

        closest = outline[0]

        for p in outline:
            if abs(p[0] - x) < abs(closest[0] - x):
                closest = p

        # outline width is stored in Y
        return abs(closest[1]) * 2
    def get_width_at_length(self, length_cm, outline):

        if not outline:
            return 0.0

        half_width_cm = max(0.0, self._interp_profile_at_length(length_cm, outline))
        return half_width_cm * 2.0

        outline = self.get_outline_points_cm()
        if not outline:
            return []

        faces = []

        length_min = min(p[0] for p in outline)
        length_max = max(p[0] for p in outline)

        slices = 120

        prev = None

        for i in range(slices + 1):

            x = length_min + (length_max - length_min) * i / slices

            width = self.get_width_at_x(x, outline)
            camber = self.get_camber_at_x(x)
            thickness = self.get_thickness_at_x(x)

            half_w = width / 2

            TL = (x, -half_w, camber + thickness)
            TR = (x,  half_w, camber + thickness)

            BL = (x, -half_w, camber)
            BR = (x,  half_w, camber)

            if prev:

                pTL, pTR, pBL, pBR = prev

                faces.append([pTL, pTR, TR, TL])  # top
                faces.append([pBL, pBR, BR, BL])  # base
                faces.append([pTL, TL, BL, pBL])  # left wall
                faces.append([pTR, TR, BR, pBR])  # right wall

            prev = (TL, TR, BL, BR)

        return faces
    def get_ski_length(self):
        if len(self.points) < 2:
            return 0.0

        ys = [p.pos.y() for p in self.points]
        top_y = min(ys)
        bottom_y = max(ys)

        return (bottom_y - top_y) / PIXELS_PER_CM
    def get_camber_curve_length(self, start_index=1, end_index=5, samples_per_segment=80):
        """
        Returns curved path length in cm along the camber curve from
        control point index start_index to end_index, inclusive.

        For your current 6-point camber setup:
        points 2-6 in human terms = indices 1..5 in Python
        """
        pts = self.camber_thickness_points

        if len(pts) < 2:
            return 0.0

        start_index = max(0, start_index)
        end_index = min(len(pts) - 1, end_index)

        if end_index <= start_index:
            return 0.0

        def cubic_point(p0, c1, c2, p1, t):
            mt = 1.0 - t
            x = (
                mt**3 * p0.x()
                + 3 * mt**2 * t * c1.x()
                + 3 * mt * t**2 * c2.x()
                + t**3 * p1.x()
            )
            y = (
                mt**3 * p0.y()
                + 3 * mt**2 * t * c1.y()
                + 3 * mt * t**2 * c2.y()
                + t**3 * p1.y()
            )
            return QPointF(x, y)

        total_px = 0.0

        for i in range(start_index, end_index):
            p0 = pts[i].pos
            c1 = pts[i].handle_out
            c2 = pts[i + 1].handle_in
            p1 = pts[i + 1].pos

            prev = p0
            for s in range(1, samples_per_segment + 1):
                t = s / samples_per_segment
                curr = cubic_point(p0, c1, c2, p1, t)
                total_px += math.hypot(curr.x() - prev.x(), curr.y() - prev.y())
                prev = curr

        return total_px / PIXELS_PER_CM

    def get_main_shape_centerline_y(self):
        if len(self.points) < 2:
            return 0.0
        return (self.points[0].pos.y() + self.points[-1].pos.y()) / 2.0

    def _integrate_full_width_area_cm2(self, y_min_px=None, y_max_px=None, samples=4000):
        pts = self.sample_edge(samples)
        if len(pts) < 2:
            return 0.0

        rows = sorted((float(p.y()), abs(float(p.x())) * 2.0 / PIXELS_PER_CM) for p in pts)
        if len(rows) < 2:
            return 0.0

        if y_min_px is None:
            y_min_px = rows[0][0]
        if y_max_px is None:
            y_max_px = rows[-1][0]
        y_min_px = float(min(y_min_px, y_max_px))
        y_max_px = float(max(y_min_px, y_max_px))

        def width_at(y_px):
            if y_px <= rows[0][0]:
                return rows[0][1]
            if y_px >= rows[-1][0]:
                return rows[-1][1]
            lo = 0
            hi = len(rows) - 1
            while hi - lo > 1:
                mid = (lo + hi) // 2
                if rows[mid][0] <= y_px:
                    lo = mid
                else:
                    hi = mid
            y0, w0 = rows[lo]
            y1, w1 = rows[hi]
            if abs(y1 - y0) <= 1e-9:
                return max(w0, w1)
            t = (y_px - y0) / (y1 - y0)
            return w0 + (w1 - w0) * t

        clipped = [(y_px, width_cm) for y_px, width_cm in rows if y_min_px <= y_px <= y_max_px]
        clipped.insert(0, (y_min_px, width_at(y_min_px)))
        clipped.append((y_max_px, width_at(y_max_px)))
        clipped.sort(key=lambda item: item[0])

        merged = []
        for y_px, width_cm in clipped:
            if merged and abs(y_px - merged[-1][0]) <= 1e-9:
                merged[-1] = (y_px, max(width_cm, merged[-1][1]))
            else:
                merged.append((y_px, width_cm))

        area_cm2 = 0.0
        for (y0, w0), (y1, w1) in zip(merged, merged[1:]):
            dy_cm = abs(y1 - y0) / PIXELS_PER_CM
            area_cm2 += 0.5 * (w0 + w1) * dy_cm
        return area_cm2

    def get_main_shape_area_above_centerline_cm2(self, samples=4000):
        if len(self.points) < 2:
            return 0.0
        center_y = self.get_main_shape_centerline_y()
        top_y = min(self.points[0].pos.y(), self.points[-1].pos.y())
        return self._integrate_full_width_area_cm2(top_y, center_y, samples=samples)

    def get_main_shape_area_behind_centerline_cm2(self, samples=4000):
        if len(self.points) < 2:
            return 0.0
        center_y = self.get_main_shape_centerline_y()
        bottom_y = max(self.points[0].pos.y(), self.points[-1].pos.y())
        return self._integrate_full_width_area_cm2(center_y, bottom_y, samples=samples)

    def get_boot_center_y(self):
        if len(self.points) >= 3:
            return float(self.points[2].pos.y())
        return self.get_main_shape_centerline_y()

    def get_main_shape_area_above_boot_center_cm2(self, samples=4000):
        if len(self.points) < 2:
            return 0.0
        boot_center_y = self.get_boot_center_y()
        top_y = min(self.points[0].pos.y(), self.points[-1].pos.y())
        return self._integrate_full_width_area_cm2(top_y, boot_center_y, samples=samples)

    def get_main_shape_area_below_boot_center_cm2(self, samples=4000):
        if len(self.points) < 2:
            return 0.0
        boot_center_y = self.get_boot_center_y()
        bottom_y = max(self.points[0].pos.y(), self.points[-1].pos.y())
        return self._integrate_full_width_area_cm2(boot_center_y, bottom_y, samples=samples)

    # 3D Graphic Stuff
    def _polygon_signed_area_xy(self, poly):
        if len(poly) < 3:
            return 0.0
        area = 0.0
        for i in range(len(poly)):
            x0, y0 = poly[i][0], poly[i][1]
            x1, y1 = poly[(i + 1) % len(poly)][0], poly[(i + 1) % len(poly)][1]
            area += x0 * y1 - x1 * y0
        return 0.5 * area
    def _dedupe_polygon_points(self, pts, eps=1e-5):
        if not pts:
            return []
        out = []
        for p in pts:
            if not out or math.hypot(p[0] - out[-1][0], p[1] - out[-1][1]) > eps:
                out.append(p)
        if len(out) > 1 and math.hypot(out[0][0] - out[-1][0], out[0][1] - out[-1][1]) <= eps:
            out.pop()
        return out
    def get_full_outline_polygon_cm(self, samples=720):
        key = self._cache_key("full_outline_polygon_cm", samples)
        if key not in self._cache:
            # Sample the actual right and mirrored-left edge paths in their
            # native travel order so the closed perimeter follows the ski
            # boundary continuously: tail -> tip on the right side, then
            # tip -> tail on the left side. This avoids introducing a bad
            # wraparound segment from the tail to a point near the tip when
            # the shape has a dovetail or other reverse-curved ends.
            right_path = self.build_edge_path()
            left_path = self.build_inner_or_left_edge_path()

            right = [
                (-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM)
                for p in (right_path.pointAtPercent(i / samples) for i in range(samples + 1))
            ]
            left = [
                (-p.y() / PIXELS_PER_CM, p.x() / PIXELS_PER_CM)
                for p in (left_path.pointAtPercent(i / samples) for i in range(samples + 1))
            ]

            pts = self._dedupe_polygon_points(right + left)

            if len(pts) < 3:
                self._cache[key] = pts
                return self._cache[key]

            # Collapse only runs of consecutive centerline points at the same
            # end. Keep tip and tail centerline vertices separate so a split
            # end cannot get shortcut by over-aggressive deduping.
            cleaned = []
            for p in pts:
                if (
                    cleaned
                    and abs(p[1]) <= 1e-6
                    and abs(cleaned[-1][1]) <= 1e-6
                    and abs(p[0] - cleaned[-1][0]) <= 0.05
                ):
                    cleaned[-1] = p
                else:
                    cleaned.append(p)
            pts = self._dedupe_polygon_points(cleaned)

            if len(pts) >= 3 and self._polygon_signed_area_xy(pts) < 0.0:
                pts.reverse()
            self._cache[key] = pts
        return self._cache[key]
    def _point_in_triangle_2d(self, p, a, b, c, eps=1e-10):
        px, py = p
        ax, ay = a
        bx, by = b
        cx, cy = c

        v0x, v0y = cx - ax, cy - ay
        v1x, v1y = bx - ax, by - ay
        v2x, v2y = px - ax, py - ay

        dot00 = v0x * v0x + v0y * v0y
        dot01 = v0x * v1x + v0y * v1y
        dot02 = v0x * v2x + v0y * v2y
        dot11 = v1x * v1x + v1y * v1y
        dot12 = v1x * v2x + v1y * v2y

        denom = dot00 * dot11 - dot01 * dot01
        if abs(denom) <= eps:
            return False
        inv = 1.0 / denom
        u = (dot11 * dot02 - dot01 * dot12) * inv
        v = (dot00 * dot12 - dot01 * dot02) * inv
        return u >= -eps and v >= -eps and (u + v) <= 1.0 + eps
    def _triangulate_polygon_ear_clip(self, poly):
        if len(poly) < 3:
            return []

        area = self._polygon_signed_area_xy(poly)
        if area < 0.0:
            poly = list(reversed(poly))
            index_map = list(reversed(range(len(poly))))
        else:
            poly = list(poly)
            index_map = list(range(len(poly)))

        remaining = list(range(len(poly)))
        triangles = []
        guard = 0
        max_guard = max(1000, len(poly) * len(poly) * 2)

        def cross_z(a, b, c):
            return ((b[0] - a[0]) * (c[1] - a[1])) - ((b[1] - a[1]) * (c[0] - a[0]))

        while len(remaining) > 3 and guard < max_guard:
            ear_found = False
            n = len(remaining)
            for i in range(n):
                i_prev = remaining[(i - 1) % n]
                i_curr = remaining[i]
                i_next = remaining[(i + 1) % n]
                a = poly[i_prev]
                b = poly[i_curr]
                c = poly[i_next]

                if cross_z(a, b, c) <= 1e-10:
                    continue

                blocked = False
                for j in remaining:
                    if j in (i_prev, i_curr, i_next):
                        continue
                    if self._point_in_triangle_2d(poly[j], a, b, c):
                        blocked = True
                        break
                if blocked:
                    continue

                triangles.append((index_map[i_prev], index_map[i_curr], index_map[i_next]))
                del remaining[i]
                ear_found = True
                break

            if not ear_found:
                break
            guard += 1

        if len(remaining) == 3:
            triangles.append((index_map[remaining[0]], index_map[remaining[1]], index_map[remaining[2]]))

        return triangles
    def _station_spans_from_outline(self, outline, x_cm, eps=1e-6):
        if len(outline) < 3:
            return []

        hits = []
        n = len(outline)
        for i in range(n):
            x0, y0 = outline[i]
            x1, y1 = outline[(i + 1) % n]
            dx = x1 - x0

            if abs(dx) <= eps:
                if abs(x_cm - x0) <= eps:
                    hits.extend([y0, y1])
                continue

            if x_cm < min(x0, x1) - eps or x_cm > max(x0, x1) + eps:
                continue

            t = (x_cm - x0) / dx
            if -eps <= t <= 1.0 + eps:
                t = max(0.0, min(1.0, t))
                y = y0 + (y1 - y0) * t
                hits.append(y)

        if not hits:
            return []

        hits.sort()
        dedup = []
        for y in hits:
            if not dedup or abs(y - dedup[-1]) > 1e-4:
                dedup.append(y)

        spans = []
        i = 0
        while i + 1 < len(dedup):
            y0 = dedup[i]
            y1 = dedup[i + 1]
            if y1 - y0 > 1e-4:
                spans.append((y0, y1))
            i += 2

        spans.sort(key=lambda s: 0.5 * (s[0] + s[1]))
        return spans

    def _build_span_ring_cm(self, x_cm, y0_cm, y1_cm):
        camber_cm = self.get_camber_at_length(x_cm)
        thickness_cm = self.get_thickness_at_length(x_cm)
        top_z = camber_cm + thickness_cm
        base_z = camber_cm
        return (
            (x_cm, y0_cm, top_z),
            (x_cm, y1_cm, top_z),
            (x_cm, y1_cm, base_z),
            (x_cm, y0_cm, base_z),
        )

    def _endpoint_collapse_y_for_span(self, outline, x_cm, y0_cm, y1_cm):
        if not outline:
            return 0.5 * (float(y0_cm) + float(y1_cm))
        x_cm = float(x_cm)
        y_mid = 0.5 * (float(y0_cm) + float(y1_cm))
        y_low = min(float(y0_cm), float(y1_cm))
        y_high = max(float(y0_cm), float(y1_cm))
        x_span = max((max(p[0] for p in outline) - min(p[0] for p in outline)), 1e-6)
        endpoint_tol = max(x_span * 1e-5, 0.002)
        y_margin = max((y_high - y_low) * 0.35, 0.03)
        candidates = [
            p for p in outline
            if abs(float(p[0]) - x_cm) <= endpoint_tol and y_low - y_margin <= float(p[1]) <= y_high + y_margin
        ]
        if not candidates:
            candidates = [p for p in outline if abs(float(p[0]) - x_cm) <= endpoint_tol]
        if not candidates:
            candidates = sorted(outline, key=lambda p: (abs(float(p[0]) - x_cm), abs(float(p[1]) - y_mid)))[:8]
        return float(min(candidates, key=lambda p: abs(float(p[1]) - y_mid))[1])

    def _span_ring_to_standard_order(self, ring):
        if ring is None:
            return None
        # Dovetail rings use (TL, TR, BR, BL); standard slices use (TL, TR, BL, BR).
        return (ring[0], ring[1], ring[3], ring[2])

    def _build_boundary_single_ring_cm(self, outline, x_cm):
        if len(outline) < 3:
            return None

        min_x = min(p[0] for p in outline)
        max_x = max(p[0] for p in outline)
        if max_x - min_x <= 1e-9:
            return None

        x_cm = max(min_x, min(max_x, x_cm))

        # At a dovetail/body seam there can be multiple spans at the exact seam
        # station. For handing off to the standard one-ring body mesher, use the
        # full outer envelope at that SAME station instead of shifting inward to
        # a different x position. That keeps the dovetail patch and body mesh on
        # the same seam plane and avoids small corner wedges getting left open on
        # one mirrored side.
        spans = self._station_spans_from_outline(outline, x_cm)
        if spans:
            y0 = min(s[0] for s in spans)
            y1 = max(s[1] for s in spans)
            if y1 - y0 > 1e-6:
                return self._build_span_ring_cm(x_cm, y0, y1)

        # Fallback: look slightly inward only if the exact seam station has no
        # usable span data.
        midpoint = 0.5 * (min_x + max_x)
        inward_sign = 1.0 if x_cm <= midpoint else -1.0
        offsets = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5]
        for off in offsets:
            candidate_x = max(min_x, min(max_x, x_cm + inward_sign * off))
            spans = self._station_spans_from_outline(outline, candidate_x)
            if not spans:
                continue
            y0 = min(s[0] for s in spans)
            y1 = max(s[1] for s in spans)
            if y1 - y0 > 1e-6:
                return self._build_span_ring_cm(candidate_x, y0, y1)

        return None


    def _append_bridge_faces(self, faces, prev_ring, curr_ring):
        a0, a1, a2, a3 = prev_ring
        b0, b1, b2, b3 = curr_ring

        faces.append([a0, b0, b1, a1])
        faces.append([a3, a2, b2, b3])
        faces.append([a0, a3, b3, b0])
        faces.append([a1, b1, b2, a2])

    def _append_dovetail_gap_wall_faces(self, faces, prev_spans, curr_spans):
        if not prev_spans or not curr_spans:
            return
        prev_ordered = sorted(
            [span for span in prev_spans if len(span) >= 3 and not self._ring_is_collapsed_width(span[2])],
            key=lambda span: float(span[0]),
        )
        curr_ordered = sorted(
            [span for span in curr_spans if len(span) >= 3 and not self._ring_is_collapsed_width(span[2])],
            key=lambda span: float(span[0]),
        )
        pair_count = min(len(prev_ordered), len(curr_ordered))
        if pair_count < 2:
            return
        double_sided = getattr(self, "outline_mode", "symmetric") == "splitboard"

        def append_wall(face):
            faces.append(face)
            if double_sided:
                faces.append(list(reversed(face)))

        for i in range(pair_count - 1):
            prev_lower = prev_ordered[i][2]
            prev_upper = prev_ordered[i + 1][2]
            curr_lower = curr_ordered[i][2]
            curr_upper = curr_ordered[i + 1][2]

            # Ring order in dovetail patches is TL, TR, BR, BL. These two
            # faces are the vertical side walls of the open notch between
            # adjacent spans, running from topsheet to base.
            append_wall([prev_lower[1], curr_lower[1], curr_lower[2], prev_lower[2]])
            append_wall([prev_upper[0], prev_upper[3], curr_upper[3], curr_upper[0]])

    def _append_outline_boundary_wall_faces(self, faces, outline, x_start_cm, x_end_cm, double_sided=False):
        if len(outline) < 3 or x_end_cm - x_start_cm <= 1e-6:
            return

        x0_bound = float(min(x_start_cm, x_end_cm))
        x1_bound = float(max(x_start_cm, x_end_cm))

        def interp(a, b, t):
            ax, ay = a
            bx, by = b
            return (ax + (bx - ax) * t, ay + (by - ay) * t)

        def add_wall(a, b):
            ax, ay = a
            bx, by = b
            if math.hypot(bx - ax, by - ay) <= 1e-7:
                return
            top_a = float(self.get_camber_at_length(ax)) + float(self.get_thickness_at_length(ax))
            base_a = float(self.get_camber_at_length(ax))
            top_b = float(self.get_camber_at_length(bx)) + float(self.get_thickness_at_length(bx))
            base_b = float(self.get_camber_at_length(bx))
            face = [
                (ax, ay, top_a),
                (bx, by, top_b),
                (bx, by, base_b),
                (ax, ay, base_a),
            ]
            faces.append(face)
            if double_sided:
                faces.append(list(reversed(face)))

        count = len(outline)
        for i in range(count):
            a = outline[i]
            b = outline[(i + 1) % count]
            ax, ay = float(a[0]), float(a[1])
            bx, by = float(b[0]), float(b[1])
            seg_min = min(ax, bx)
            seg_max = max(ax, bx)
            if seg_max < x0_bound - 1e-6 or seg_min > x1_bound + 1e-6:
                continue

            if abs(bx - ax) <= 1e-9:
                if x0_bound - 1e-6 <= ax <= x1_bound + 1e-6:
                    add_wall((ax, ay), (bx, by))
                continue

            t0 = max(0.0, min(1.0, (x0_bound - ax) / (bx - ax)))
            t1 = max(0.0, min(1.0, (x1_bound - ax) / (bx - ax)))
            t_low = min(t0, t1)
            t_high = max(t0, t1)
            start = interp((ax, ay), (bx, by), t_low)
            end = interp((ax, ay), (bx, by), t_high)
            add_wall(start, end)

    def _append_station_cap(self, faces, ring, at_start):
        if self._ring_is_collapsed_width(ring):
            return
        v0, v1, v2, v3 = ring
        if at_start:
            faces.append([v0, v1, v2, v3])
        else:
            faces.append([v0, v3, v2, v1])

    def _append_collapsed_endpoint_valley_fill(self, faces, collapsed_spans, at_start):
        # Do not skin across adjacent collapsed dovetail endpoint spans. Those
        # spans are the separate forked tips/tails of the dovetail; adding a
        # face between them creates a stray sheet across the open notch.
        return

    def _ring_is_collapsed_width(self, ring, tol=1e-6):
        if ring is None or len(ring) != 4:
            return False
        top_left, top_right, base_left, base_right = ring
        top_width = math.dist(top_left, top_right)
        base_width = math.dist(base_left, base_right)
        return top_width <= tol and base_width <= tol

    def _append_taper_bridge_faces(self, faces, collapsed_ring, full_ring, collapsed_is_prev=True):
        if collapsed_ring is None or full_ring is None:
            return False
        if len(collapsed_ring) != 4 or len(full_ring) != 4:
            return False

        cTL, cTR, cBL, cBR = collapsed_ring
        fTL, fTR, fBL, fBR = full_ring
        apex_top = ((cTL[0] + cTR[0]) * 0.5, (cTL[1] + cTR[1]) * 0.5, (cTL[2] + cTR[2]) * 0.5)
        apex_base = ((cBL[0] + cBR[0]) * 0.5, (cBL[1] + cBR[1]) * 0.5, (cBL[2] + cBR[2]) * 0.5)

        if collapsed_is_prev:
            faces.append([apex_top, fTL, fTR])
            faces.append([apex_base, fBR, fBL])
            faces.append([apex_top, apex_base, fBL, fTL])
            faces.append([apex_top, fTR, fBR, apex_base])
        else:
            faces.append([fTL, apex_top, fTR])
            faces.append([fBL, fBR, apex_base])
            faces.append([fTL, fBL, apex_base, apex_top])
            faces.append([apex_top, apex_base, fBR, fTR])
        return True

    def _append_dovetail_taper_bridge_faces(self, faces, collapsed_ring, full_ring, collapsed_is_prev=True):
        if collapsed_ring is None or full_ring is None:
            return False
        if len(collapsed_ring) != 4 or len(full_ring) != 4:
            return False

        # Dovetail patch rings use TL, TR, BR, BL. The standard taper helper is
        # for TL, TR, BL, BR rings, so using it here swaps the vertical notch
        # walls and can leave the topsheet-to-base side surfaces missing.
        cTL, cTR, cBR, cBL = collapsed_ring
        fTL, fTR, fBR, fBL = full_ring
        apex_top = ((cTL[0] + cTR[0]) * 0.5, (cTL[1] + cTR[1]) * 0.5, (cTL[2] + cTR[2]) * 0.5)
        apex_base = ((cBL[0] + cBR[0]) * 0.5, (cBL[1] + cBR[1]) * 0.5, (cBL[2] + cBR[2]) * 0.5)

        if collapsed_is_prev:
            faces.append([apex_top, fTL, fTR])
            faces.append([apex_base, fBR, fBL])
            faces.append([apex_top, apex_base, fBL, fTL])
            faces.append([apex_top, fTR, fBR, apex_base])
        else:
            faces.append([fTL, apex_top, fTR])
            faces.append([fBL, fBR, apex_base])
            faces.append([fTL, fBL, apex_base, apex_top])
            faces.append([apex_top, apex_base, fBR, fTR])
        return True

    def _split_single_span_for_transition(self, single_span, reference_spans):
        if single_span is None or not reference_spans or len(reference_spans) < 2:
            return None

        y0, y1, ring = single_span[:3]
        ordered_reference = sorted(
            [span for span in reference_spans if span is not None and span[1] - span[0] > 1e-6],
            key=lambda span: span[0],
        )
        if len(ordered_reference) != len(reference_spans):
            return None

        x_cm = ring[0][0]
        split_spans = []
        margin = 1e-5
        for span in ordered_reference:
            if span is None:
                return None
            sy0, sy1, _ = span[:3]
            clipped_y0 = max(float(y0), float(sy0))
            clipped_y1 = min(float(y1), float(sy1))
            if clipped_y1 - clipped_y0 <= margin:
                return None
            split_spans.append((clipped_y0, clipped_y1, self._build_span_ring_cm(x_cm, clipped_y0, clipped_y1)))

        return split_spans

    def _append_transition_spans(self, faces, prev_spans, curr_spans):
        # Handle 2-span <-> 1-span seam transitions without creating station-plane
        # caps in the middle of the ski. Those temporary caps were useful for
        # closing tiny slivers, but they also create overlapping interior
        # surfaces that can show through in the 3D preview.
        if len(prev_spans) == 2 and len(curr_spans) == 1:
            split_curr = self._split_single_span_for_transition(curr_spans[0], prev_spans)
            if split_curr is not None:
                for pi in range(2):
                    self._append_bridge_faces(faces, prev_spans[pi][2], split_curr[pi][2])
                return True

        if len(prev_spans) == 1 and len(curr_spans) == 2:
            split_prev = self._split_single_span_for_transition(prev_spans[0], curr_spans)
            if split_prev is not None:
                for pi in range(2):
                    self._append_bridge_faces(faces, split_prev[pi][2], curr_spans[pi][2])
                return True

        return False


    def _build_gap_ring_cm(self, x_cm, y0_cm, y1_cm):
        if y1_cm - y0_cm <= 1e-6:
            return None
        return self._build_span_ring_cm(x_cm, y0_cm, y1_cm)

    def _append_explicit_seam_stitch(self, faces, seam_spans, body_ring, seam_is_start):
        if not seam_spans or body_ring is None:
            return

        ordered = sorted(
            [(float(y0), float(y1), ring) for (y0, y1, ring) in seam_spans if (y1 - y0) > 1e-6],
            key=lambda entry: entry[0],
        )
        if len(ordered) < 2:
            return

        x_cm = float(body_ring[0][0])
        top_z = float(body_ring[0][2])
        base_z = float(body_ring[2][2])
        double_sided = getattr(self, "outline_mode", "symmetric") == "splitboard"

        def append_wall(face):
            faces.append(face)
            if double_sided:
                faces.append(list(reversed(face)))

        for left, right in zip(ordered, ordered[1:]):
            gap_y0 = float(left[1])
            gap_y1 = float(right[0])
            if gap_y1 - gap_y0 <= 1e-6:
                continue
            # This is the vertical notch wall at the dovetail/body handoff. It
            # connects topsheet to base; the endpoint cross-tip fill remains
            # disabled in _append_collapsed_endpoint_valley_fill().
            if seam_is_start:
                append_wall([
                    (x_cm, gap_y0, top_z),
                    (x_cm, gap_y1, top_z),
                    (x_cm, gap_y1, base_z),
                    (x_cm, gap_y0, base_z),
                ])
            else:
                append_wall([
                    (x_cm, gap_y0, top_z),
                    (x_cm, gap_y0, base_z),
                    (x_cm, gap_y1, base_z),
                    (x_cm, gap_y1, top_z),
                ])

    def _face_crosses_dovetail_gap(self, face, outline, eps=1e-5):
        if len(face) < 3 or len(outline) < 3:
            return False
        xs = [float(p[0]) for p in face]
        ys = [float(p[1]) for p in face]
        zs = [float(p[2]) for p in face]
        if max(xs) - min(xs) > 0.002:
            return False
        if max(zs) - min(zs) > 0.002:
            return False
        y_min = min(ys)
        y_max = max(ys)
        if y_max - y_min <= eps:
            return False

        x_cm = sum(xs) / len(xs)
        spans = self._station_spans_from_outline(outline, x_cm)
        if len(spans) < 2:
            return False
        ordered = sorted(spans, key=lambda span: span[0])
        for left, right in zip(ordered, ordered[1:]):
            gap_y0 = float(left[1])
            gap_y1 = float(right[0])
            if gap_y1 - gap_y0 <= eps:
                continue
            if y_min < gap_y0 + eps and y_max > gap_y1 - eps:
                return True
        return False

    def _dedupe_and_drop_degenerate_faces(self, faces, area_tol=1e-7, dovetail_outline=None):
        if not faces:
            return faces

        cleaned = []
        seen = set()
        preserve_splitboard_wall_winding = (
            getattr(self, "outline_mode", "symmetric") == "splitboard"
            and dovetail_outline is not None
        )
        for face in faces:
            if len(face) < 3:
                continue
            xs = [float(p[0]) for p in face]
            ys = [float(p[1]) for p in face]
            zs = [float(p[2]) for p in face]
            span_x = max(xs) - min(xs)
            span_y = max(ys) - min(ys)
            span_z = max(zs) - min(zs)
            keep_winding = preserve_splitboard_wall_winding and span_z > 0.02
            face_key = tuple(self._point_key(p) for p in face) if keep_winding else tuple(sorted(self._point_key(p) for p in face))
            if face_key in seen:
                continue
            seen.add(face_key)

            if max(span_x, span_y, span_z) <= area_tol:
                continue
            if dovetail_outline is not None and self._face_crosses_dovetail_gap(face, dovetail_outline):
                continue
            cleaned.append(face)
        return cleaned

    def _point_key(self, p, ndigits=6):
        return (round(float(p[0]), ndigits), round(float(p[1]), ndigits), round(float(p[2]), ndigits))

    def _edge_key(self, a, b):
        ka = self._point_key(a)
        kb = self._point_key(b)
        return (ka, kb) if ka <= kb else (kb, ka)

    def _polygon_perimeter(self, pts):
        if len(pts) < 2:
            return 0.0
        total = 0.0
        for i in range(len(pts)):
            x0, y0, z0 = pts[i]
            x1, y1, z1 = pts[(i + 1) % len(pts)]
            total += math.dist((x0, y0, z0), (x1, y1, z1))
        return total

    def _order_boundary_loop(self, component_keys, adjacency, key_to_point):
        if not component_keys:
            return []

        start = min(component_keys, key=lambda k: (key_to_point[k][0], key_to_point[k][1], key_to_point[k][2]))
        ordered = [start]
        prev = None
        curr = start

        for _ in range(len(component_keys) + 2):
            neighbors = list(adjacency.get(curr, ()))
            if not neighbors:
                break
            next_key = None
            for cand in neighbors:
                if cand != prev:
                    next_key = cand
                    break
            if next_key is None:
                next_key = neighbors[0]
            if next_key == start:
                break
            if next_key in ordered:
                break
            ordered.append(next_key)
            prev, curr = curr, next_key

        if len(ordered) >= 3:
            return [key_to_point[k] for k in ordered]
        return []

    def _repair_small_boundary_holes(self, faces, seam_xs=None, x_tol=0.08, max_edges=8, max_perimeter=2.5):
        if not faces:
            return faces

        edge_counts = {}
        edge_dirs = {}
        key_to_point = {}
        for face in faces:
            if len(face) < 3:
                continue
            n = len(face)
            for i in range(n):
                a = face[i]
                b = face[(i + 1) % n]
                ka = self._point_key(a)
                kb = self._point_key(b)
                key_to_point.setdefault(ka, a)
                key_to_point.setdefault(kb, b)
                ek = self._edge_key(a, b)
                edge_counts[ek] = edge_counts.get(ek, 0) + 1
                edge_dirs.setdefault(ek, (ka, kb))

        boundary_edges = []
        for ek, count in edge_counts.items():
            if count == 1:
                ka, kb = edge_dirs[ek]
                boundary_edges.append((ka, kb))

        if not boundary_edges:
            return faces

        adjacency = {}
        for ka, kb in boundary_edges:
            adjacency.setdefault(ka, set()).add(kb)
            adjacency.setdefault(kb, set()).add(ka)

        visited = set()
        repaired = list(faces)
        seam_xs = [sx for sx in (seam_xs or []) if sx is not None]

        for start in list(adjacency.keys()):
            if start in visited:
                continue
            stack = [start]
            component = set()
            while stack:
                k = stack.pop()
                if k in component:
                    continue
                component.add(k)
                visited.add(k)
                stack.extend(adjacency.get(k, ()))

            if len(component) < 3 or len(component) > max_edges:
                continue
            if any(len(adjacency.get(k, ())) != 2 for k in component):
                continue

            loop = self._order_boundary_loop(component, adjacency, key_to_point)
            if len(loop) < 3:
                continue

            xs = [p[0] for p in loop]
            if seam_xs and not any(abs(x - sx) <= x_tol for x in xs for sx in seam_xs):
                continue

            perimeter = self._polygon_perimeter(loop)
            if perimeter > max_perimeter:
                continue

            cx = sum(p[0] for p in loop) / len(loop)
            cy = sum(p[1] for p in loop) / len(loop)
            cz = sum(p[2] for p in loop) / len(loop)
            centroid = (cx, cy, cz)
            for i in range(len(loop)):
                repaired.append([loop[i], loop[(i + 1) % len(loop)], centroid])

        return repaired

    def _order_boundary_chain(self, component_keys, adjacency, key_to_point):
        if not component_keys:
            return []

        endpoints = [k for k in component_keys if len(adjacency.get(k, ())) == 1]
        if endpoints:
            start = min(endpoints, key=lambda k: (key_to_point[k][0], key_to_point[k][1], key_to_point[k][2]))
        else:
            start = min(component_keys, key=lambda k: (key_to_point[k][0], key_to_point[k][1], key_to_point[k][2]))

        ordered = [start]
        prev = None
        curr = start
        seen = {start}
        for _ in range(len(component_keys) + 2):
            neighbors = list(adjacency.get(curr, ()))
            next_key = None
            for cand in neighbors:
                if cand != prev and cand not in seen:
                    next_key = cand
                    break
            if next_key is None:
                for cand in neighbors:
                    if cand != prev:
                        next_key = cand
                        break
            if next_key is None or next_key in seen:
                break
            ordered.append(next_key)
            seen.add(next_key)
            prev, curr = curr, next_key

        if len(ordered) >= 2:
            return [key_to_point[k] for k in ordered]
        return []

    def _repair_small_boundary_chains(self, faces, seam_xs=None, x_tol=0.12, max_edges=6, max_span=1.5):
        if not faces:
            return faces

        edge_counts = {}
        edge_dirs = {}
        key_to_point = {}
        for face in faces:
            if len(face) < 3:
                continue
            n = len(face)
            for i in range(n):
                a = face[i]
                b = face[(i + 1) % n]
                ka = self._point_key(a)
                kb = self._point_key(b)
                key_to_point.setdefault(ka, a)
                key_to_point.setdefault(kb, b)
                ek = self._edge_key(a, b)
                edge_counts[ek] = edge_counts.get(ek, 0) + 1
                edge_dirs.setdefault(ek, (ka, kb))

        boundary_edges = []
        for ek, count in edge_counts.items():
            if count == 1:
                ka, kb = edge_dirs[ek]
                boundary_edges.append((ka, kb))

        if not boundary_edges:
            return faces

        seam_xs = [float(sx) for sx in (seam_xs or []) if sx is not None]
        if not seam_xs:
            return faces

        adjacency = {}
        for ka, kb in boundary_edges:
            pa = key_to_point[ka]
            pb = key_to_point[kb]
            if not any(abs(pa[0] - sx) <= x_tol or abs(pb[0] - sx) <= x_tol for sx in seam_xs):
                continue
            adjacency.setdefault(ka, set()).add(kb)
            adjacency.setdefault(kb, set()).add(ka)

        if not adjacency:
            return faces

        repaired = list(faces)
        visited = set()
        for start in list(adjacency.keys()):
            if start in visited:
                continue

            stack = [start]
            component = set()
            while stack:
                k = stack.pop()
                if k in component:
                    continue
                component.add(k)
                visited.add(k)
                stack.extend(adjacency.get(k, ()))

            if len(component) < 2 or len(component) > max_edges + 1:
                continue

            degrees = [len(adjacency.get(k, ())) for k in component]
            endpoint_count = sum(1 for d in degrees if d == 1)
            if endpoint_count not in (0, 2):
                continue

            chain = self._order_boundary_chain(component, adjacency, key_to_point)
            if len(chain) < 2:
                continue

            xs = [p[0] for p in chain]
            ys = [p[1] for p in chain]
            zs = [p[2] for p in chain]
            nearest_seam = min(seam_xs, key=lambda sx: min(abs(x - sx) for x in xs))
            if min(abs(x - nearest_seam) for x in xs) > x_tol:
                continue

            span = max(max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
            if span > max_span:
                continue

            centroid = (nearest_seam, sum(ys) / len(ys), sum(zs) / len(zs))
            for i in range(len(chain) - 1):
                tri = [chain[i], chain[i + 1], centroid]
                repaired.append(tri)

        return repaired

    def _prune_interior_station_caps(self, faces, interior_xs=None, x_tol=0.05, area_tol=1e-7):
        if not faces:
            return faces

        interior_xs = [float(x) for x in (interior_xs or []) if x is not None]
        if not interior_xs:
            return faces

        cleaned = []
        seen = set()
        for face in faces:
            if len(face) < 3:
                continue

            # Drop exact duplicate faces regardless of winding.
            face_key = tuple(sorted(self._point_key(p) for p in face))
            if face_key in seen:
                continue
            seen.add(face_key)

            xs = [float(p[0]) for p in face]
            ys = [float(p[1]) for p in face]
            zs = [float(p[2]) for p in face]

            # Drop tiny degenerate faces.
            span_x = max(xs) - min(xs)
            span_y = max(ys) - min(ys)
            span_z = max(zs) - min(zs)
            if max(span_x, span_y, span_z) <= area_tol:
                continue

            # Only prune broad station-plane caps on the interior seam planes.
            # Keep small repair triangles, since those are what close the tiny
            # sliver that appears at the dovetail/body handoff.
            if span_x <= x_tol:
                cx = sum(xs) / len(xs)
                if any(abs(cx - sx) <= x_tol for sx in interior_xs):
                    is_broad_cap = (len(face) >= 4) or (span_y > x_tol * 4.0 and span_z > x_tol * 4.0)
                    if is_broad_cap:
                        continue

            cleaned.append(face)

        return cleaned

    def _match_station_spans(self, prev_spans, curr_spans):
        # prev_spans / curr_spans entries are (y0, y1, ring)
        matches = []
        unmatched_prev = list(range(len(prev_spans)))
        unmatched_curr = list(range(len(curr_spans)))

        candidates = []
        for i, prev_span in enumerate(prev_spans):
            py0, py1, _ = prev_span[:3]
            pc = 0.5 * (py0 + py1)
            pw = py1 - py0
            for j, curr_span in enumerate(curr_spans):
                cy0, cy1, _ = curr_span[:3]
                cc = 0.5 * (cy0 + cy1)
                cw = cy1 - cy0
                overlap = min(py1, cy1) - max(py0, cy0)
                center_dist = abs(pc - cc)
                width_scale = max(pw, cw, 1e-6)
                candidates.append((-(max(0.0, overlap)), center_dist / width_scale, center_dist, i, j))

        used_prev = set()
        used_curr = set()
        for _neg_overlap, _norm_dist, center_dist, i, j in sorted(candidates):
            if i in used_prev or j in used_curr:
                continue
            py0, py1, _ = prev_spans[i][:3]
            cy0, cy1, _ = curr_spans[j][:3]
            overlap = min(py1, cy1) - max(py0, cy0)
            width_scale = max(py1 - py0, cy1 - cy0, 1e-6)
            if overlap <= 1e-4 and center_dist > max(0.35 * width_scale, 0.08):
                continue
            matches.append((i, j))
            used_prev.add(i)
            used_curr.add(j)

        unmatched_prev = [i for i in unmatched_prev if i not in used_prev]
        unmatched_curr = [j for j in unmatched_curr if j not in used_curr]
        return matches, unmatched_prev, unmatched_curr

    def _dovetail_scan_stations(self, outline, min_x, max_x, station_count):
        length = max_x - min_x
        if length <= 1e-6:
            return []

        stations = {
            min_x + length * i / max(1, station_count - 1)
            for i in range(max(2, int(station_count)))
        }

        # Very shallow dovetails can occupy less than one uniform station step.
        # Add adaptive samples between nearby outline vertices at both ends so
        # the split is still detected as soon as it is just past flat.
        end_zone = max(length * 0.18, 18.0)
        near_end_xs = sorted({
            float(x)
            for x, _y in outline
            if x <= min_x + end_zone or x >= max_x - end_zone
        })
        for a, b in zip(near_end_xs[:-1], near_end_xs[1:]):
            if b - a <= 1e-6:
                continue
            stations.add((a + b) * 0.5)

        eps = max(length * 1e-7, 1e-5)
        return sorted(x for x in stations if min_x + eps <= x <= max_x - eps)

    def _scan_outline_stations(self, station_count=360, outline_samples=1200):
        outline = self.get_full_outline_polygon_cm(outline_samples)
        if len(outline) < 3:
            return [], [], [], 0.0, 0.0

        xs = [p[0] for p in outline]
        min_x = min(xs)
        max_x = max(xs)
        if max_x - min_x <= 1e-6:
            return outline, [], [], min_x, max_x

        stations = self._dovetail_scan_stations(outline, min_x, max_x, station_count)
        spans_by_station = [self._station_spans_from_outline(outline, x_cm) for x_cm in stations]
        return outline, stations, spans_by_station, min_x, max_x

    def _find_dovetail_zone_end_from_start(self, stations, spans_by_station, min_run=1):
        multi = [i for i, spans in enumerate(spans_by_station) if len(spans) > 1]
        if not multi:
            return None
        run_start = multi[0]
        run_end = run_start
        while run_end + 1 < len(spans_by_station) and len(spans_by_station[run_end + 1]) > 1:
            run_end += 1
        if run_end - run_start + 1 < min_run:
            return None
        for i in range(run_end + 1, len(spans_by_station)):
            if len(spans_by_station[i]) == 1:
                return stations[i]
        return None

    def _find_dovetail_zone_start_from_end(self, stations, spans_by_station, min_run=1):
        multi = [i for i, spans in enumerate(spans_by_station) if len(spans) > 1]
        if not multi:
            return None
        run_end = multi[-1]
        run_start = run_end
        while run_start - 1 >= 0 and len(spans_by_station[run_start - 1]) > 1:
            run_start -= 1
        if run_end - run_start + 1 < min_run:
            return None
        for i in range(run_start - 1, -1, -1):
            if len(spans_by_station[i]) == 1:
                return stations[i]
        return None

    def _get_dovetail_zone_bounds(self, station_count=360, outline_samples=1200):
        outline, stations, spans_by_station, min_x, max_x = self._scan_outline_stations(
            station_count=station_count,
            outline_samples=outline_samples,
        )
        if len(outline) < 3 or not stations:
            return {
                "outline": outline,
                "min_x": min_x,
                "max_x": max_x,
                "tip_end_x": None,
                "tail_start_x": None,
            }

        tip_end_x = self._find_dovetail_zone_end_from_start(stations, spans_by_station)
        tail_start_x = self._find_dovetail_zone_start_from_end(stations, spans_by_station)

        tol = max((max_x - min_x) / max(1, station_count - 1) * 1.5, 0.05)
        if tip_end_x is not None and tip_end_x >= max_x - tol:
            tip_end_x = None
        if tail_start_x is not None and tail_start_x <= min_x + tol:
            tail_start_x = None
        if tip_end_x is not None and tail_start_x is not None and tip_end_x >= tail_start_x - tol:
            tip_end_x = None
            tail_start_x = None

        return {
            "outline": outline,
            "min_x": min_x,
            "max_x": max_x,
            "tip_end_x": tip_end_x,
            "tail_start_x": tail_start_x,
        }

    def has_dovetail(self, station_count=360, outline_samples=1200):
        bounds = self._get_dovetail_zone_bounds(
            station_count=station_count,
            outline_samples=outline_samples,
        )
        return bounds["tip_end_x"] is not None or bounds["tail_start_x"] is not None

    def _build_standard_mesh_range(self, x_start_cm, x_end_cm, num_samples=500, cap_start=True, cap_end=True, leading_ring=None, trailing_ring=None):
        if x_end_cm - x_start_cm <= 1e-6:
            return []

        faces = []
        outline = self.get_full_outline_polygon_cm(max(720, num_samples * 3))
        if not outline:
            return []
        outline_min_x = min(p[0] for p in outline)
        outline_max_x = max(p[0] for p in outline)
        endpoint_tol = max((outline_max_x - outline_min_x) * 1e-7, 1e-5)
        range_len = max(x_end_cm - x_start_cm, 1e-6)
        endpoint_probe = max(range_len / max(num_samples * 4, 80), 0.002)

        sections = []
        for i in range(num_samples + 1):
            t = i / max(1, num_samples)
            length_cm = x_start_cm + (x_end_cm - x_start_cm) * t
            spans = self._station_spans_from_outline(outline, length_cm)
            endpoint_ring = None
            if not spans:
                at_outline_start = cap_start and abs(length_cm - outline_min_x) <= endpoint_tol and length_cm + endpoint_probe < x_end_cm
                at_outline_end = cap_end and abs(length_cm - outline_max_x) <= endpoint_tol and length_cm - endpoint_probe > x_start_cm
                if at_outline_start or at_outline_end:
                    probe_x = length_cm + endpoint_probe if at_outline_start else length_cm - endpoint_probe
                    probe_spans = self._station_spans_from_outline(outline, probe_x)
                    if probe_spans:
                        y0_probe = min(span[0] for span in probe_spans)
                        y1_probe = max(span[1] for span in probe_spans)
                        endpoint_y = self._endpoint_collapse_y_for_span(outline, length_cm, y0_probe, y1_probe)
                        endpoint_ring = self._span_ring_to_standard_order(self._build_span_ring_cm(length_cm, endpoint_y, endpoint_y))
                if endpoint_ring is not None:
                    sections.append(endpoint_ring)
                    continue
            if not spans:
                continue
            y0 = min(span[0] for span in spans)
            y1 = max(span[1] for span in spans)
            ring = self._span_ring_to_standard_order(self._build_span_ring_cm(length_cm, y0, y1))
            if ring is not None:
                sections.append(ring)

        if not sections:
            return faces

        if leading_ring is not None:
            sections[0] = leading_ring
        if trailing_ring is not None:
            sections[-1] = trailing_ring

        for i in range(1, len(sections)):
            prev_ring = sections[i - 1]
            curr_ring = sections[i]
            pTL, pTR, pBL, pBR = prev_ring
            TL, TR, BL, BR = curr_ring

            prev_collapsed = self._ring_is_collapsed_width(prev_ring)
            curr_collapsed = self._ring_is_collapsed_width(curr_ring)
            if prev_collapsed and not curr_collapsed:
                self._append_taper_bridge_faces(faces, prev_ring, curr_ring, collapsed_is_prev=True)
                continue
            if curr_collapsed and not prev_collapsed:
                self._append_taper_bridge_faces(faces, curr_ring, prev_ring, collapsed_is_prev=False)
                continue

            faces.append([pTL, TL, TR, pTR])
            faces.append([pBL, pBR, BR, BL])
            faces.append([pTL, pBL, BL, TL])
            faces.append([pTR, TR, BR, pBR])

        TL, TR, BL, BR = sections[0]
        if cap_start:
            faces.append([TL, TR, BR, BL])
        TL, TR, BL, BR = sections[-1]
        if cap_end:
            faces.append([TL, BL, BR, TR])
        return faces

    def build_ski_mesh_standard(self, num_samples=500):
        key = self._cache_key("ski_mesh_standard", int(num_samples))
        if key in self._cache:
            return self._cache[key]

        outline = self.get_full_outline_polygon_cm(max(720, num_samples * 3))
        if not outline:
            return []

        length_min = min(p[0] for p in outline)
        length_max = max(p[0] for p in outline)
        faces = self._build_standard_mesh_range(
            length_min,
            length_max,
            num_samples=int(num_samples),
            cap_start=True,
            cap_end=True,
        )
        self._cache[key] = faces
        return faces

    def _build_dovetail_patch_range(self, outline, x_start_cm, x_end_cm, num_samples=220, cap_start=True, cap_end=True, return_seam_rings=False):
        if len(outline) < 3 or x_end_cm - x_start_cm <= 1e-6:
            if return_seam_rings:
                return [], None, None
            return []

        faces = []
        prev_spans = None
        first_primary_ring = None
        last_primary_ring = None
        span_count = max(2, int(num_samples))
        total_len = x_end_cm - x_start_cm
        eps = max(total_len / max(50, span_count * 8), 0.002)

        for i in range(span_count + 1):
            t = i / max(1, span_count)
            x_station = x_start_cm + total_len * t
            x_eval = x_station
            collapse_to_endpoint = False
            if i == 0 and cap_start and x_station + eps < x_end_cm:
                x_eval = x_station + eps
                collapse_to_endpoint = True
            elif i == span_count and cap_end and x_station - eps > x_start_cm:
                x_eval = x_station - eps
                collapse_to_endpoint = True

            spans_xy = self._station_spans_from_outline(outline, x_eval)
            curr_spans = []
            for y0, y1 in spans_xy:
                if (y1 - y0) <= 1e-4:
                    continue
                if collapse_to_endpoint:
                    endpoint_y = self._endpoint_collapse_y_for_span(outline, x_station, y0, y1)
                    curr_spans.append((endpoint_y, endpoint_y, self._build_span_ring_cm(x_station, endpoint_y, endpoint_y), True))
                else:
                    curr_spans.append((y0, y1, self._build_span_ring_cm(x_station, y0, y1), False))

            if curr_spans:
                primary = max(
                    curr_spans,
                    key=lambda entry: ((entry[1] - entry[0]), -abs(0.5 * (entry[0] + entry[1]))),
                )[2]
                if first_primary_ring is None:
                    first_primary_ring = primary
                last_primary_ring = primary

            if not curr_spans:
                if prev_spans:
                    for span in prev_spans:
                        self._append_station_cap(faces, span[2], at_start=False)
                    prev_spans = None
                continue

            if prev_spans is None:
                if cap_start and i == 0:
                    self._append_collapsed_endpoint_valley_fill(faces, curr_spans, at_start=True)
                    for span in curr_spans:
                        if not (bool(span[3]) if len(span) > 3 else False):
                            self._append_station_cap(faces, span[2], at_start=True)
                prev_spans = curr_spans
                continue

            if self._append_transition_spans(faces, prev_spans, curr_spans):
                self._append_dovetail_gap_wall_faces(faces, prev_spans, curr_spans)
                prev_spans = curr_spans
                continue

            matches, unmatched_prev, unmatched_curr = self._match_station_spans(prev_spans, curr_spans)
            for pi, cj in matches:
                prev_ring = prev_spans[pi][2]
                curr_ring = curr_spans[cj][2]
                prev_collapsed = self._ring_is_collapsed_width(prev_ring)
                curr_collapsed = self._ring_is_collapsed_width(curr_ring)
                if prev_collapsed and not curr_collapsed:
                    self._append_dovetail_taper_bridge_faces(faces, prev_ring, curr_ring, collapsed_is_prev=True)
                elif curr_collapsed and not prev_collapsed:
                    self._append_dovetail_taper_bridge_faces(faces, curr_ring, prev_ring, collapsed_is_prev=False)
                else:
                    self._append_bridge_faces(faces, prev_ring, curr_ring)
            for pi in unmatched_prev:
                self._append_station_cap(faces, prev_spans[pi][2], at_start=False)
            for cj in unmatched_curr:
                self._append_station_cap(faces, curr_spans[cj][2], at_start=True)
            self._append_dovetail_gap_wall_faces(faces, prev_spans, curr_spans)
            prev_spans = curr_spans

        if prev_spans and cap_end:
            self._append_collapsed_endpoint_valley_fill(faces, prev_spans, at_start=False)
            for span in prev_spans:
                if not (bool(span[3]) if len(span) > 3 else False):
                    self._append_station_cap(faces, span[2], at_start=False)

        if return_seam_rings:
            return faces, first_primary_ring, last_primary_ring
        return faces

    def build_ski_mesh_dovetail(self, num_samples=260):
        key = self._cache_key("ski_mesh_dovetail", int(num_samples))
        if key in self._cache:
            return self._cache[key]

        bounds = self._get_dovetail_zone_bounds(
            station_count=max(360, int(num_samples) * 2),
            outline_samples=max(1200, int(num_samples) * 6),
        )
        outline = bounds["outline"]
        min_x = bounds["min_x"]
        max_x = bounds["max_x"]
        tip_end_x = bounds["tip_end_x"]
        tail_start_x = bounds["tail_start_x"]

        if len(outline) < 3 or max_x - min_x <= 1e-6:
            return []
        if tip_end_x is None and tail_start_x is None:
            faces = self._build_standard_mesh_range(min_x, max_x, num_samples=max(400, int(num_samples) * 2))
            self._cache[key] = faces
            return faces

        transition_pad = max((max_x - min_x) / max(160, int(num_samples) * 3), 0.35)
        if tip_end_x is not None:
            tip_end_x = min(tip_end_x + transition_pad, max_x)
        if tail_start_x is not None:
            tail_start_x = max(tail_start_x - transition_pad, min_x)
        if tip_end_x is not None and tail_start_x is not None and tip_end_x >= tail_start_x - transition_pad:
            tip_end_x = None
            tail_start_x = None

        faces = []
        body_start = tip_end_x if tip_end_x is not None else min_x
        body_end = tail_start_x if tail_start_x is not None else max_x

        leading_ring = None
        trailing_ring = None
        tail_faces = []
        tip_seam_spans = None
        tail_seam_spans = None
        dovetail_sample_floor = 120
        dovetail_sample_scale = 1.35

        if tip_end_x is not None and tip_end_x > min_x + 1e-6:
            tip_faces, _tip_start_ring, tip_end_ring = self._build_dovetail_patch_range(
                outline,
                min_x,
                tip_end_x,
                num_samples=max(
                    dovetail_sample_floor,
                    int(num_samples * dovetail_sample_scale * (tip_end_x - min_x) / max(max_x - min_x, 1e-6)),
                ),
                cap_start=True,
                cap_end=False,
                return_seam_rings=True,
            )
            faces.extend(tip_faces)
            tip_seam_spans_xy = self._station_spans_from_outline(outline, body_start)
            tip_seam_spans = [
                (y0, y1, self._build_span_ring_cm(body_start, y0, y1))
                for (y0, y1) in tip_seam_spans_xy
                if (y1 - y0) > 1e-4
            ]
            leading_ring = self._span_ring_to_standard_order(self._build_boundary_single_ring_cm(outline, body_start))
            if leading_ring is None:
                leading_ring = self._span_ring_to_standard_order(tip_end_ring)

        if tail_start_x is not None and max_x > tail_start_x + 1e-6:
            tail_faces, tail_start_ring, _tail_end_ring = self._build_dovetail_patch_range(
                outline,
                tail_start_x,
                max_x,
                num_samples=max(
                    dovetail_sample_floor,
                    int(num_samples * dovetail_sample_scale * (max_x - tail_start_x) / max(max_x - min_x, 1e-6)),
                ),
                cap_start=False,
                cap_end=True,
                return_seam_rings=True,
            )
            tail_seam_spans_xy = self._station_spans_from_outline(outline, body_end)
            tail_seam_spans = [
                (y0, y1, self._build_span_ring_cm(body_end, y0, y1))
                for (y0, y1) in tail_seam_spans_xy
                if (y1 - y0) > 1e-4
            ]
            trailing_ring = self._span_ring_to_standard_order(self._build_boundary_single_ring_cm(outline, body_end))
            if trailing_ring is None:
                trailing_ring = self._span_ring_to_standard_order(tail_start_ring)

        if body_end > body_start + 1e-6:
            faces.extend(
                self._build_standard_mesh_range(
                    body_start,
                    body_end,
                    num_samples=max(220, int(num_samples * 1.5)),
                    cap_start=(tip_end_x is None),
                    cap_end=(tail_start_x is None),
                    leading_ring=leading_ring,
                    trailing_ring=trailing_ring,
                )
            )

        if tail_start_x is not None and max_x > tail_start_x + 1e-6:
            faces.extend(tail_faces)

        double_sided_splitboard_walls = getattr(self, "outline_mode", "symmetric") == "splitboard"
        if tip_end_x is not None and tip_end_x > min_x + 1e-6:
            self._append_outline_boundary_wall_faces(
                faces,
                outline,
                min_x,
                tip_end_x,
                double_sided=double_sided_splitboard_walls,
            )
        if tail_start_x is not None and max_x > tail_start_x + 1e-6:
            self._append_outline_boundary_wall_faces(
                faces,
                outline,
                tail_start_x,
                max_x,
                double_sided=double_sided_splitboard_walls,
            )

        if tip_seam_spans and leading_ring is not None:
            self._append_explicit_seam_stitch(faces, tip_seam_spans, leading_ring, seam_is_start=True)
        if tail_seam_spans and trailing_ring is not None:
            self._append_explicit_seam_stitch(faces, tail_seam_spans, trailing_ring, seam_is_start=False)

        faces = self._dedupe_and_drop_degenerate_faces(faces, dovetail_outline=outline)

        self._cache[key] = faces
        return faces

    def build_ski_mesh(self, num_samples=120, force_samples=False):
        requested_samples = int(num_samples)
        if force_samples:
            requested_samples = max(16, requested_samples)
        elif getattr(self, "interaction_3d_active", False) and getattr(self, "low_res_3d_edit_mode", True):
            requested_samples = min(requested_samples, int(getattr(self, "low_res_mesh_samples", 32)))
        else:
            requested_samples = max(requested_samples, int(getattr(self, "full_res_mesh_samples", 120)))

        key = self._cache_key("ski_mesh_dispatch", requested_samples, bool(force_samples))
        if key in self._cache:
            return self._cache[key]

        bounds = self._get_dovetail_zone_bounds(
            station_count=max(180, int(requested_samples) * 2),
            outline_samples=max(600, int(requested_samples) * 6),
        )
        if bounds["tip_end_x"] is None and bounds["tail_start_x"] is None:
            if force_samples:
                faces = self.build_ski_mesh_standard(max(80, int(requested_samples) * 2))
            else:
                faces = self.build_ski_mesh_standard(max(180, int(requested_samples) * 3))
        else:
            if force_samples:
                faces = self.build_ski_mesh_dovetail(max(72, int(requested_samples * 1.5)))
            else:
                faces = self.build_ski_mesh_dovetail(max(120, int(requested_samples) * 2))

        self._cache[key] = faces
        return faces

    def rotate_point(self, p):
        x, y, z = p

        ax = self.rot_x
        ay = self.rot_y
        az = self.rot_z

        # X axis (tilt / pitch)
        y2 = y * math.cos(ax) - z * math.sin(ax)
        z2 = y * math.sin(ax) + z * math.cos(ax)
        x2 = x

        # Y axis (spin / yaw)
        x3 = x2 * math.cos(ay) + z2 * math.sin(ay)
        z3 = -x2 * math.sin(ay) + z2 * math.cos(ay)
        y3 = y2

        # Z axis (roll)
        x4 = x3 * math.cos(az) - y3 * math.sin(az)
        y4 = x3 * math.sin(az) + y3 * math.cos(az)
        z4 = z3

        return (x4, y4, z4)
    def project(self, x, y=None, z=None):
        # allow tuple input
        if y is None and z is None:
            x, y, z = x

        scale = float(getattr(self, "project_scale", 7.5))  # scale 3d rendering
        x = float(x) - float(getattr(self, "model_center_length_cm", 12.5))

        # simple trimetric projection
        px = (x - y) * 0.866
        py = (x + y) * 0.5 - z

        sx = px * scale + self.offset_x
        sy = py * scale + self.offset_y

        return QPointF(sx, sy)

    def get_projected_3d_model_bounds(self, samples=80):
        if not getattr(self, "show_3d", False):
            return QRectF()
        try:
            faces = self.build_ski_mesh(samples)
        except Exception:
            return QRectF()
        projected = []
        seen = set()
        duplicate_offset_cm = self.get_second_3d_side_by_side_offset_cm(faces) if self.show_ski_snowboard else None
        base_to_base = bool(getattr(self, "second_3d_base_to_base", False))
        base_sep_cm = float(getattr(self, "second_3d_base_separation_cm", 7.5))

        def add_vertex(vertex):
            key = tuple(round(float(v), 4) for v in vertex)
            if key in seen:
                return None
            seen.add(key)
            pt = self.project(self.rotate_point(vertex))
            projected.append(pt)
            return pt

        for face in faces:
            for vertex in face:
                pt = add_vertex(vertex)
                if duplicate_offset_cm is not None:
                    if base_to_base:
                        add_vertex((vertex[0], -vertex[1], base_sep_cm - vertex[2]))
                    else:
                        add_vertex((vertex[0], -vertex[1] + duplicate_offset_cm, vertex[2]))

        if not projected:
            return QRectF()
        min_x = min(pt.x() for pt in projected)
        max_x = max(pt.x() for pt in projected)
        min_y = min(pt.y() for pt in projected)
        max_y = max(pt.y() for pt in projected)
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)

    def update_3d_background_center_cache(self):
        center_x = float(getattr(self, "offset_x", 1000.0))
        model_bounds = self.get_projected_3d_model_bounds()
        if not model_bounds.isNull():
            center_x = model_bounds.center().x()
        self._cached_3d_background_center_x = center_x
        return center_x

    def _get_3d_background_center_x(self):
        if getattr(self, "interaction_3d_active", False):
            cached = getattr(self, "_cached_3d_background_center_x", None)
            if cached is not None:
                return float(cached)
        return self.update_3d_background_center_cache()

    def get_3d_background_rect(self, max_width=None):
        if not getattr(self, "show_3d", False) or not getattr(self, "show_3d_background", True):
            return QRectF()

        center_x = self._get_3d_background_center_x()
        center_y = float(getattr(self, "offset_y", 0.0))

        base_to_base = bool(getattr(self, "second_3d_base_to_base", False))

        width = float(getattr(self, "background_3d_width_px", 760.0))
        height = float(getattr(self, "background_3d_height_px", 1280.0))
        if self.show_ski_snowboard and not base_to_base:
            width = max(width, 980.0)
        if max_width is not None:
            width = min(width, max(1.0, float(max_width)))

        return QRectF(center_x - width * 0.5, center_y - height * 0.5-100, width, height)

    def _get_3d_graphic_bounds_cm(self):
        outline = self._current_full_outline_polygon_cm_uncached()
        if not outline:
            return (-100.0, 100.0, -10.0, 10.0)
        xs = [float(p[0]) for p in outline]
        ys = [float(p[1]) for p in outline]
        if not xs or not ys:
            return (-100.0, 100.0, -10.0, 10.0)
        min_y = min(ys)
        max_y = max(ys)
        if max_y - min_y < 1.0:
            center_y = 0.5 * (min_y + max_y)
            min_y = center_y - 0.5
            max_y = center_y + 0.5
        return (min(xs), max(xs), min_y, max_y)

    def _classify_3d_surface_face(self, face):
        if len(face) < 3:
            return None

        xs = [float(p[0]) for p in face]
        zs = [float(p[2]) for p in face]
        avg_x = sum(xs) / float(len(xs))
        avg_z = sum(zs) / float(len(zs))
        z_span = max(zs) - min(zs)

        camber_z = float(self.get_camber_at_length(avg_x))
        thickness_z = max(0.01, float(self.get_thickness_at_length(avg_x)))
        top_z = camber_z + thickness_z
        bottom_z = camber_z

        # Horizontal skin faces keep nearly the same Z across the polygon.
        # Side faces span most of the ski thickness, so reject those first.
        if z_span <= max(0.02, thickness_z * 0.45):
            return "top" if abs(avg_z - top_z) <= abs(avg_z - bottom_z) else "bottom"

        # Fallback for steeper tip/tail areas: keep only faces whose normals are
        # still dominated by Z, then classify by which skin height they are closer to.
        nx, ny, nz = self._normalize_vec3(self._face_normal(face))
        if abs(nz) >= max(abs(nx), abs(ny)) * 0.65:
            return "top" if abs(avg_z - top_z) <= abs(avg_z - bottom_z) else "bottom"
        return None

    def _draw_3d_graphic_face(self, painter, face, pts, image):
        if image is None or image.isNull() or len(face) < 3 or len(pts) < 3:
            return
        self._draw_3d_graphic_mapped_face(painter, face, pts, image, self._classify_3d_surface_face(face) or "top")

    def _face_uv_to_image_point(self, vertex, image, face_kind, bounds_cm=None):
        if image is None or image.isNull():
            return QPointF()
        if bounds_cm is None:
            bounds_cm = self._get_3d_graphic_bounds_cm()
        min_len, max_len, min_half_w, max_half_w = bounds_cm
        span_len = max(1e-6, float(max_len) - float(min_len))
        span_w = max(1e-6, float(max_half_w) - float(min_half_w))

        u = (float(vertex[0]) - float(min_len)) / span_len
        v = (float(vertex[1]) - float(min_half_w)) / span_w
        u = max(0.0, min(1.0, u))
        v = max(0.0, min(1.0, v))

        # 3D graphic orientation is controlled here through UV remapping.
        # Top graphic: rotate 180 degrees.
        if face_kind == "top":
            u, v = 1.0 - v, u
        # Bottom graphic: rotate 270 degrees so the base artwork lines up on the 3D ski.
        elif face_kind == "bottom":
            u, v = 1.0 - v, u

        return QPointF(u * float(image.width()), (1.0 - v) * float(image.height()))

    def _make_affine_transform(self, src_tri, dst_tri):
        if len(src_tri) != 3 or len(dst_tri) != 3:
            return None

        x1, y1 = float(src_tri[0].x()), float(src_tri[0].y())
        x2, y2 = float(src_tri[1].x()), float(src_tri[1].y())
        x3, y3 = float(src_tri[2].x()), float(src_tri[2].y())
        X1, Y1 = float(dst_tri[0].x()), float(dst_tri[0].y())
        X2, Y2 = float(dst_tri[1].x()), float(dst_tri[1].y())
        X3, Y3 = float(dst_tri[2].x()), float(dst_tri[2].y())

        det = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
        if abs(det) < 1e-9:
            return None

        a = (X1 * (y2 - y3) + X2 * (y3 - y1) + X3 * (y1 - y2)) / det
        b = (X1 * (x3 - x2) + X2 * (x1 - x3) + X3 * (x2 - x1)) / det
        c = (X1 * (x2 * y3 - x3 * y2) + X2 * (x3 * y1 - x1 * y3) + X3 * (x1 * y2 - x2 * y1)) / det
        d = (Y1 * (y2 - y3) + Y2 * (y3 - y1) + Y3 * (y1 - y2)) / det
        e = (Y1 * (x3 - x2) + Y2 * (x1 - x3) + Y3 * (x2 - x1)) / det
        f = (Y1 * (x2 * y3 - x3 * y2) + Y2 * (x3 * y1 - x1 * y3) + Y3 * (x1 * y2 - x2 * y1)) / det
        return QTransform(a, d, b, e, c, f)

    def _draw_3d_graphic_triangle(self, painter, src_tri, dst_tri, image):
        if image is None or image.isNull() or len(src_tri) != 3 or len(dst_tri) != 3:
            return
        dst_poly = QPolygonF(dst_tri)
        dst_rect = dst_poly.boundingRect()
        if dst_rect.width() < 0.25 or dst_rect.height() < 0.25:
            return
        transform = self._make_affine_transform(src_tri, dst_tri)
        if transform is None:
            return
        clip_path = QPainterPath()
        clip_path.addPolygon(dst_poly)
        painter.save()
        try:
            painter.setClipPath(clip_path, Qt.ClipOperation.IntersectClip)
            painter.setTransform(transform, True)
            painter.drawImage(QPointF(0.0, 0.0), image)
        finally:
            painter.restore()

    def _draw_3d_graphic_mapped_face(self, painter, face, pts, image, face_kind, bounds_cm=None, uv_face=None):
        if uv_face is None:
            uv_face = face
        if image is None or image.isNull() or len(face) < 3 or len(pts) < 3 or len(uv_face) < 3:
            return
        if bounds_cm is None:
            bounds_cm = self._get_3d_graphic_bounds_cm()

        src_pts = [self._face_uv_to_image_point(v, image, face_kind, bounds_cm) for v in uv_face]
        if len(src_pts) != len(pts):
            return

        # Triangle fan mapping keeps the artwork locked to the rotated mesh
        # instead of stretching a screen-aligned image across the projected bounds.
        for i in range(1, min(len(src_pts), len(pts)) - 1):
            src_tri = [src_pts[0], src_pts[i], src_pts[i + 1]]
            dst_tri = [pts[0], pts[i], pts[i + 1]]
            self._draw_3d_graphic_triangle(painter, src_tri, dst_tri, image)

    def _draw_3d_graphic_overlay(self, painter, draw_faces, face_kind, image):
        if image is None or image.isNull() or not draw_faces:
            return
        bounds_cm = self._get_3d_graphic_bounds_cm()
        for item in draw_faces:
            _depth, face, _rotated, pts = item[:4]
            uv_face = item[4] if len(item) > 4 else face
            kind = self._classify_3d_surface_face(uv_face)
            if kind != face_kind or len(face) < 3 or len(pts) < 3:
                continue
            self._draw_3d_graphic_mapped_face(painter, face, pts, image, face_kind, bounds_cm=bounds_cm, uv_face=uv_face)

    def _face_normal(self, face):
        if len(face) < 3:
            return (0.0, 0.0, 0.0)
        p0, p1, p2 = face[0], face[1], face[2]
        e1x = p1[0] - p0[0]
        e1y = p1[1] - p0[1]
        e1z = p1[2] - p0[2]
        e2x = p2[0] - p0[0]
        e2y = p2[1] - p0[1]
        e2z = p2[2] - p0[2]
        nx = e1y * e2z - e1z * e2y
        ny = e1z * e2x - e1x * e2z
        nz = e1x * e2y - e1y * e2x
        return (nx, ny, nz)
    def _face_centroid(self, face):
        if not face:
            return (0.0, 0.0, 0.0)
        inv = 1.0 / float(len(face))
        return (
            sum(p[0] for p in face) * inv,
            sum(p[1] for p in face) * inv,
            sum(p[2] for p in face) * inv,
        )
    def _orient_face_outward(self, face):
        if len(face) < 3:
            return list(face)
        oriented = list(face)
        cx, cy, cz = self._face_centroid(oriented)
        center_z = float(self.get_camber_at_length(cx)) + 0.5 * max(0.0, float(self.get_thickness_at_length(cx)))
        if getattr(self, "outline_mode", "symmetric") == "splitboard":
            zs = [float(p[2]) for p in oriented]
            ys = [float(p[1]) for p in oriented]
            z_span = max(zs) - min(zs)
            y_abs = max(abs(y) for y in ys) if ys else abs(cy)
            if z_span > 0.02 and y_abs <= 0.03:
                # Splitboard centerline wall faces live on y=0, so using cy as
                # the outward vector makes their winding ambiguous. Treat the
                # split seam as the left boundary of the editable right half.
                outward = (0.0, -1.0, cz - center_z)
            else:
                outward = (0.0, cy, cz - center_z)
        else:
            outward = (0.0, cy, cz - center_z)
        nx, ny, nz = self._face_normal(oriented)
        if (nx * outward[0] + ny * outward[1] + nz * outward[2]) < 0.0:
            oriented.reverse()
        return oriented

    def _orient_face_outward_base_to_base(self, face, base_sep_cm):
        if len(face) < 3:
            return list(face)
        oriented = list(face)
        cx, cy, cz = self._face_centroid(oriented)
        center_z = float(self.get_camber_at_length(cx)) + 0.5 * max(0.0, float(self.get_thickness_at_length(cx)))
        transformed_center_z = float(base_sep_cm) - center_z
        outward = (0.0, cy, cz - transformed_center_z)
        nx, ny, nz = self._face_normal(oriented)
        if (nx * outward[0] + ny * outward[1] + nz * outward[2]) < 0.0:
            oriented.reverse()
        return oriented
    def _normalize_vec3(self, v):
        x, y, z = v
        length = math.sqrt(x * x + y * y + z * z)
        if length < 1e-9:
            return (0.0, 0.0, 0.0)
        return (x / length, y / length, z / length)
    def _trimetric_view_dir(self):
        return self._normalize_vec3((1.0, 1.0, 1.0))
    def _face_visible(self, face):
        nx, ny, nz = self._face_normal(face)
        vx, vy, vz = self._trimetric_view_dir()
        return (nx * vx + ny * vy + nz * vz) < 0.0
    def _is_dovetail_preview_wall_face(self, face, bounds=None):
        if len(face) < 3:
            return False
        xs = [float(p[0]) for p in face]
        zs = [float(p[2]) for p in face]
        if max(zs) - min(zs) <= 0.02:
            return False

        if bounds is None:
            bounds = self._get_dovetail_zone_bounds(
                station_count=max(180, int(getattr(self, "full_res_mesh_samples", 120)) * 2),
                outline_samples=max(600, int(getattr(self, "full_res_mesh_samples", 120)) * 6),
            )
        min_x = bounds.get("min_x")
        max_x = bounds.get("max_x")
        tip_end_x = bounds.get("tip_end_x")
        tail_start_x = bounds.get("tail_start_x")
        if min_x is None or max_x is None:
            return False

        cx = sum(xs) / float(len(xs))
        tol = max((float(max_x) - float(min_x)) * 0.01, 0.15)
        in_tip = tip_end_x is not None and float(min_x) - tol <= cx <= float(tip_end_x) + tol
        in_tail = tail_start_x is not None and float(tail_start_x) - tol <= cx <= float(max_x) + tol
        if not (in_tip or in_tail):
            return False

        # Require at least one matching XY pair with different Z. That targets
        # true top-to-base wall faces and avoids making broad skin faces double-sided.
        pts = [(round(float(p[0]), 5), round(float(p[1]), 5), float(p[2])) for p in face]
        for i, a in enumerate(pts):
            for b in pts[i + 1:]:
                if a[0] == b[0] and a[1] == b[1] and abs(a[2] - b[2]) > 0.02:
                    return True
        if getattr(self, "outline_mode", "symmetric") == "splitboard":
            # Splitboard dovetails are half-outlines with a centerline boundary,
            # so their vertical wall quads are not always represented as exact
            # repeated XY pairs after the station mesh is stitched. If the face
            # spans thickness and its normal is mostly horizontal, it is one of
            # the topsheet-to-base walls that should stay visible in preview.
            nx, ny, nz = self._normalize_vec3(self._face_normal(face))
            if abs(nz) <= max(abs(nx), abs(ny)) * 0.45:
                return True
        return False
    def _face_depth(self, face):
        vx, vy, vz = self._trimetric_view_dir()
        cx = sum(p[0] for p in face) / len(face)
        cy = sum(p[1] for p in face) / len(face)
        cz = sum(p[2] for p in face) / len(face)
        return cx * vx + cy * vy + cz * vz
    def _interp_profile_at_length(self, length_cm, pts):
        if not pts:
            return 0.0

        pts = sorted(pts, key=lambda p: p[0])

        if length_cm <= pts[0][0]:
            return pts[0][1]
        if length_cm >= pts[-1][0]:
            return pts[-1][1]

        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            if x0 <= length_cm <= x1:
                if abs(x1 - x0) < 1e-9:
                    return y0
                t = (length_cm - x0) / (x1 - x0)
                return y0 + (y1 - y0) * t

        return pts[-1][1]
    def get_thickness_at_x1(self, x):
        pts = []
        path = self.build_core_curve()
        for i in range(300):
            p = path.pointAtPercent(i/299)
            pts.append((p.x()/PIXELS_PER_CM, -p.y()/PIXELS_PER_CM))
        if not pts:
            return 1
        closest = pts[0]
        for p in pts:
            if abs(p[0]-x) < abs(closest[0]-x):
                closest = p
        return abs(closest[1])
    def get_thickness_profile_cm(self, samples=300):
        key = self._cache_key("thickness_cm", samples)
        if key not in self._cache:
            if len(self.core_thickness_points) < 2:
                return []

            path = self.build_core_curve()

            # Measure thickness from the same offset baseline line used by the
            # 2D core-thickness sketch fill, not from the average X of the end
            # points. That way the 3D ski includes the full thickness implied by
            # the offset line and does not collapse too thin near the tip/tail.
            baseline_x = self.get_core_profile_left_x()

            pts = []
            for i in range(samples):
                p = path.pointAtPercent(i / (samples - 1))
                sample_length = -p.y() / PIXELS_PER_CM
                thickness_cm = (p.x() - baseline_x) / PIXELS_PER_CM
                pts.append((sample_length, thickness_cm))
            self._cache[key] = pts
        return self._cache[key]
    def get_thickness_at_length(self, length_cm):
        pts = self.get_thickness_profile_cm()
        if not pts:
            return 1.0
        return max(0.0, self._interp_profile_at_length(length_cm, pts))
    def get_sandwich_stiffness_profile(self, samples=180):
        """
        Returns [(length_cm, stiffness_value), ...] using a simple sandwich
        composite flexural-rigidity model based on local ski width and the
        core-thickness sketch. Values are relative units intended for shape
        comparison inside the design tool.
        """
        samples = max(8, int(samples))
        lower_factor = max(0.01, float(getattr(self, 'lower_reinforcement_factor', 10.0)))
        core_factor = max(0.01, float(getattr(self, 'wood_core_stiffness_factor', 1.0)))
        upper_factor = max(0.01, float(getattr(self, 'upper_reinforcement_factor', 10.0)))
        cache_key = (
            'sandwich_stiffness_profile',
            samples,
            round(lower_factor, 6),
            round(core_factor, 6),
            round(upper_factor, 6),
        )
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        outline = self.get_half_outline_points_cm(max(400, samples * 3))
        thickness_profile = self.get_thickness_profile_cm(max(220, samples * 2))
        if not outline or not thickness_profile:
            self._cache[cache_key] = []
            return []

        length_min = max(min(p[0] for p in outline), min(p[0] for p in thickness_profile))
        length_max = min(max(p[0] for p in outline), max(p[0] for p in thickness_profile))
        if length_max <= length_min:
            self._cache[cache_key] = []
            return []

        # Simple ski sandwich assumptions:
        # - reinforcement skins are thin relative to the core
        # - factors act like relative modulus multipliers
        # - output is relative EI, useful for comparing stiffness distribution
        skin_thickness_cm = 0.06  # ~0.6 mm effective skin per side

        profile = []
        for i in range(samples):
            t = i / max(1, samples - 1)
            length_cm = length_min + (length_max - length_min) * t
            width_cm = max(0.05, self.get_width_at_length(length_cm, outline))
            core_thickness_cm = max(0.02, self.get_thickness_at_length(length_cm))

            core_I = width_cm * (core_thickness_cm ** 3) / 12.0
            neutral_offset_cm = (core_thickness_cm + skin_thickness_cm) / 2.0

            lower_skin_I = (width_cm * (skin_thickness_cm ** 3) / 12.0) + (width_cm * skin_thickness_cm * (neutral_offset_cm ** 2))
            upper_skin_I = (width_cm * (skin_thickness_cm ** 3) / 12.0) + (width_cm * skin_thickness_cm * (neutral_offset_cm ** 2))

            stiffness_value = (
                core_factor * core_I
                + lower_factor * lower_skin_I
                + upper_factor * upper_skin_I
            )
            profile.append((length_cm, stiffness_value))
        self._cache[cache_key] = profile
        return profile

    def draw_stiffness_plot(self, painter):
        profile = self.get_sandwich_stiffness_profile()
        if len(profile) < 2:
            return

        values = [v for _, v in profile]
        max_value = max(values)
        if max_value <= 1e-9:
            return

        box_left = -1230.0
        box_top = -1030.0
        box_width = 235.0
        box_height = 1800.0
        pad = 18.0

        outer = QRectF(box_left, box_top, box_width, box_height)
        inner = QRectF(box_left + pad, box_top + pad + 24.0, box_width - 2.0 * pad, box_height - 2.0 * pad - 40.0)

        painter.save()
        painter.setPen(QPen(QColor(210, 210, 210, 180), 1))
        painter.setBrush(QBrush(QColor(20, 20, 24, 170)))
        painter.drawRoundedRect(outer, 12, 12)

        painter.setPen(QPen(QColor(235, 235, 235), 1))
        painter.setFont(QFont('Arial', 20))
        painter.drawText(QRectF(box_left + 10.0, box_top + 6.0, box_width - 20.0, 20.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'Stiffness Plot')

        painter.setPen(QPen(QColor(90, 90, 95, 160), 1, Qt.PenStyle.DashLine))
        for frac in (0.25, 0.5, 0.75):
            y = inner.top() + inner.height() * frac
            painter.drawLine(QPointF(inner.left(), y), QPointF(inner.right(), y))

        painter.setPen(QPen(QColor(160, 160, 160, 180), 1))
        painter.drawLine(QPointF(inner.left(), inner.top()), QPointF(inner.left(), inner.bottom()))
        painter.drawLine(QPointF(inner.left(), inner.bottom()), QPointF(inner.right(), inner.bottom()))

        path = QPainterPath()
        fill_path = QPainterPath()
        first = True
        for length_cm, value in profile:
            value_norm = value / max_value
            x = inner.left() + value_norm * inner.width()
            y = inner.bottom() - ((length_cm - profile[0][0]) / max(1e-9, (profile[-1][0] - profile[0][0]))) * inner.height()
            pt = QPointF(x, y)
            if first:
                path.moveTo(pt)
                fill_path.moveTo(QPointF(inner.left(), y))
                fill_path.lineTo(pt)
                first = False
            else:
                path.lineTo(pt)
                fill_path.lineTo(pt)

        fill_path.lineTo(QPointF(inner.left(), inner.bottom()))
        fill_path.closeSubpath()

        painter.setBrush(QBrush(QColor(80, 150, 255, 55)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(fill_path)

        painter.setPen(QPen(QColor(110, 185, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)

        painter.setPen(QPen(QColor(230, 230, 230), 1))
        painter.setFont(QFont('Arial', 18))
        painter.drawText(QRectF(inner.left(), box_top + box_height - 18.0, inner.width(), 14.0), Qt.AlignmentFlag.AlignCenter, 'relative EI')
        painter.save()
        painter.translate(box_left + 8.0, inner.center().y())
        painter.rotate(-90)
        painter.drawText(QRectF(-inner.height() / 2.0, -10.0, inner.height(), 14.0), Qt.AlignmentFlag.AlignCenter, 'ski length')
        painter.restore()

        painter.drawText(QRectF(inner.left(), inner.top() - 22.0, inner.width(), 18.0), Qt.AlignmentFlag.AlignRight, f'max {max_value:.1f}')
        painter.restore()

    # =========================
    # ====Paint Section!!!=====
    # =========================
    def _build_projected_3d_outline_polylines(self, duplicate_shift_px=None, samples=240):
        outline = self.get_half_outline_points_cm(samples)
        if not outline:
            return []

        top_right = []
        top_left = []
        bottom_right = []
        bottom_left = []
        for length_cm, half_width_cm in outline:
            thickness_cm = max(0.0, self.get_thickness_at_length(length_cm))
            camber_cm = self.get_camber_at_length(length_cm)
            top_z = camber_cm + thickness_cm
            bottom_z = camber_cm

            tr_rot = self.rotate_point((length_cm, half_width_cm, top_z))
            tl_rot = self.rotate_point((length_cm, -half_width_cm, top_z))
            br_rot = self.rotate_point((length_cm, half_width_cm, bottom_z))
            bl_rot = self.rotate_point((length_cm, -half_width_cm, bottom_z))

            top_right.append((tr_rot, self.project(tr_rot)))
            top_left.append((tl_rot, self.project(tl_rot)))
            bottom_right.append((br_rot, self.project(br_rot)))
            bottom_left.append((bl_rot, self.project(bl_rot)))

        polylines = [top_right, top_left, bottom_right, bottom_left]
        if duplicate_shift_px is not None:
            shifted = []
            for poly in polylines:
                shifted.append([(rot, QPointF(pt.x() + duplicate_shift_px, pt.y())) for rot, pt in poly])
            polylines.extend(shifted)
        return polylines

    def _point_depth(self, p):
        vx, vy, vz = self._trimetric_view_dir()
        return p[0] * vx + p[1] * vy + p[2] * vz

    def _build_3d_occluders(self, draw_faces):
        occluders = []
        for item in draw_faces:
            face_depth, _face, _rotated, pts = item[:4]
            if len(pts) < 3:
                continue
            poly = QPolygonF(pts)
            occluders.append((id(item), face_depth, poly, poly.boundingRect().adjusted(-0.5, -0.5, 0.5, 0.5)))
        return occluders

    def _segment_hidden_by_faces(self, mid_rotated, mid_projected, occluders, depth_bias=1e-4, ignore_face_ids=None):
        segment_depth = self._point_depth(mid_rotated)
        test_pt = QPointF(mid_projected.x(), mid_projected.y())
        ignore_face_ids = ignore_face_ids or set()
        for face_id, face_depth, poly, bounds in occluders:
            if face_id in ignore_face_ids:
                continue
            if not bounds.contains(test_pt):
                continue
            if not poly.containsPoint(test_pt, Qt.FillRule.OddEvenFill):
                continue
            if face_depth < (segment_depth - depth_bias):
                return True
        return False

    def _draw_visible_segment(self, painter, a_rot, a_pt, b_rot, b_pt, occluders, samples=2, ignore_face_ids=None):
        visible_run = []
        for i in range(samples + 1):
            t = i / float(samples)
            rot = (
                a_rot[0] + (b_rot[0] - a_rot[0]) * t,
                a_rot[1] + (b_rot[1] - a_rot[1]) * t,
                a_rot[2] + (b_rot[2] - a_rot[2]) * t,
            )
            pt = QPointF(
                a_pt.x() + (b_pt.x() - a_pt.x()) * t,
                a_pt.y() + (b_pt.y() - a_pt.y()) * t,
            )
            hidden = self._segment_hidden_by_faces(rot, pt, occluders, ignore_face_ids=ignore_face_ids)
            if not hidden:
                visible_run.append(pt)
            else:
                if len(visible_run) >= 2:
                    for p0, p1 in zip(visible_run, visible_run[1:]):
                        painter.drawLine(p0, p1)
                visible_run = []
        if len(visible_run) >= 2:
            for p0, p1 in zip(visible_run, visible_run[1:]):
                painter.drawLine(p0, p1)

    def _draw_3d_outline_edges(self, painter, draw_faces, duplicate_shift_px=None, samples=240):
        # Fast replacement for the older sampled hidden-line tracing pass.
        # Build candidate edges directly from the already-visible front faces,
        # then keep boundary edges and strong creases. This is much faster and
        # naturally duplicates onto the 2nd ski because draw_faces already
        # contains the shifted projected geometry for that copy.
        if not draw_faces:
            return []

        crease_dot_threshold = 0.985  # keep sharper changes, drop smooth shared edges
        edge_map = {}

        def qpt(pt, scale=4.0):
            return (int(round(pt.x() * scale)), int(round(pt.y() * scale)))

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(0, 0, 0), 1.35))
        occluders = self._build_3d_occluders(draw_faces)

        for item in draw_faces:
            depth, _face, rotated, pts = item[:4]
            if len(rotated) < 3 or len(pts) < 3:
                continue
            normal = self._normalize_vec3(self._face_normal(rotated))
            count = min(len(rotated), len(pts))
            for i in range(count):
                j = (i + 1) % count
                a_pt = pts[i]
                b_pt = pts[j]
                key = tuple(sorted((qpt(a_pt), qpt(b_pt))))
                entry = edge_map.setdefault(key, {
                    'a': a_pt,
                    'b': b_pt,
                    'a_rot': rotated[i],
                    'b_rot': rotated[j],
                    'depth': depth,
                    'normals': [],
                    'count': 0,
                    'face_ids': set(),
                })
                if depth < entry['depth']:
                    entry['a'] = a_pt
                    entry['b'] = b_pt
                    entry['a_rot'] = rotated[i]
                    entry['b_rot'] = rotated[j]
                    entry['depth'] = depth
                entry['normals'].append(normal)
                entry['count'] += 1
                entry['face_ids'].add(id(item))

        for entry in edge_map.values():
            keep = entry['count'] == 1
            if not keep and len(entry['normals']) >= 2:
                n0 = entry['normals'][0]
                for n1 in entry['normals'][1:]:
                    dot = n0[0] * n1[0] + n0[1] * n1[1] + n0[2] * n1[2]
                    if dot < crease_dot_threshold:
                        keep = True
                        break
            if keep:
                self._draw_visible_segment(
                    painter,
                    entry['a_rot'],
                    entry['a'],
                    entry['b_rot'],
                    entry['b'],
                    occluders,
                    samples=2,
                    ignore_face_ids=entry.get('face_ids', set()),
                )

        painter.restore()

    def _format_global_coordinate_text(self, point):
        return f"({point.x():.1f}, {point.y():.1f})"

    def _draw_global_coordinate_labels(self, painter):
        painter.save()
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        self._begin_dimension_layout()

        def draw_label(point, color, dx=8.0, dy=-8.0):
            text = self._format_global_coordinate_text(point)
            preferred = QPointF(point.x() + dx, point.y() + dy)
            candidate_offsets = [
                QPointF(dx, dy), QPointF(10.0, -18.0), QPointF(10.0, 22.0),
                QPointF(-70.0, -18.0), QPointF(-70.0, 22.0),
                QPointF(22.0, -34.0), QPointF(22.0, 38.0),
                QPointF(-92.0, -34.0), QPointF(-92.0, 38.0),
            ]
            best_pos = preferred
            best_rect = self._dimension_text_rect(painter, best_pos, text)
            best_score = self._dimension_rect_collision_score(best_rect)

            for offset in candidate_offsets:
                candidate = QPointF(point.x() + offset.x(), point.y() + offset.y())
                rect = self._dimension_text_rect(painter, candidate, text)
                score = self._dimension_rect_collision_score(rect)
                if score < best_score:
                    best_pos = candidate
                    best_rect = rect
                    best_score = score
                    if score == 0:
                        break

            self._dimension_label_rects.append(best_rect)
            leader_end = QPointF(
                max(best_rect.left(), min(point.x(), best_rect.right())),
                max(best_rect.top(), min(point.y(), best_rect.bottom())),
            )
            painter.setPen(QPen(QColor(color.red(), color.green(), color.blue(), 115), 0.8, Qt.PenStyle.DotLine))
            painter.drawLine(point, leader_end)
            self._register_dimension_segment(point, leader_end)
            painter.save()
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(QColor(20, 24, 30, 175)))
            painter.drawRoundedRect(best_rect, 3, 3)
            painter.restore()
            painter.setPen(QPen(color, 1))
            painter.drawText(best_pos, text)

        shape_colors = [
            (self.points, QColor(255, 235, 235, 230)),
            (self.core_thickness_points, QColor(220, 255, 220, 230)),
            (self.camber_thickness_points, QColor(220, 235, 255, 230)),
        ]
        if getattr(self, "outline_mode", "symmetric") == "asymmetric":
            self._ensure_left_points()
            shape_colors.insert(1, (self.left_points, QColor(210, 225, 255, 230)))
        handle_color = QColor(255, 210, 120, 230)

        for points, point_color in shape_colors:
            for p in points:
                draw_label(p.pos, point_color, 8.0, -8.0)
                if hasattr(p, "handle_in"):
                    draw_label(p.handle_in, handle_color, 8.0, -8.0)
                if hasattr(p, "handle_out"):
                    draw_label(p.handle_out, handle_color, 8.0, 14.0)

        painter.restore()

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, not (self.show_3d or self.show_ski_snowboard))

        # Main Ski/Snowboard Shape
        main_ski_path = self.build_full_shape()
        painter.setBrush(QBrush(QColor(100,10,10,149)))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawPath(main_ski_path)
        if self.top_graphic_image is not None:
            self._draw_graphic_clipped(painter, main_ski_path, self.top_graphic_image, "top")
        painter.setPen(QPen(QColor(255,255,255),1))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(main_ski_path)

        # Derived Shapes
        derived_display_samples = 600
        if self.show_base_shape:
            painter.setPen(QPen(QColor(150, 150, 150), .5))
            painter.setBrush(QBrush(QColor(100, 100, 80, 100)))
            painter.drawPath(self.build_base_material_path(derived_display_samples))
            if getattr(self, "outline_mode", "symmetric") == "snowboard":
                painter.drawPath(self.build_left_base_material_path(derived_display_samples))
        if self.show_edge_inlay_shape:
            painter.setPen(QPen(QColor(150, 150, 150), .5))
            painter.setBrush(QBrush(QColor(200, 200, 200, 200)))
            painter.drawPath(self.build_edge_inlay_path(derived_display_samples))
        if self.show_core_shape:
            painter.setPen(QPen(QColor(50, 50, 50), .5))
            painter.setBrush(QBrush(QColor(150, 75, 0, 70)))
            painter.drawPath(self.build_core_footprint_path(derived_display_samples))
        if self.show_sidewall_shape:
            painter.setPen(QPen(QColor(50, 50, 50), .5))
            painter.setBrush(QBrush(QColor(80, 170, 255, 60)))
            painter.drawPath(self.build_sidewall_path(derived_display_samples))
        if self.show_tip_tail_spacers:
            painter.setPen(QPen(QColor(50, 50, 50), .5))
            painter.setBrush(QBrush(QColor(100, 200, 100, 70)))
            painter.drawPath(self.build_tip_spacer_path(derived_display_samples))
            painter.drawPath(self.build_tail_spacer_path(derived_display_samples))
            #self._draw_seam_editor(painter)
        if self.show_sidewall_spacer_shell:
            painter.setPen(QPen(QColor(180, 140, 255), .8))
            painter.setBrush(QBrush(QColor(170, 120, 255, 55)))
            painter.drawPath(self.build_sidewall_spacer_shell_path(derived_display_samples))

        # 3D
        if self.show_3d:
            render_mode = getattr(self, "render_3d_mode", "shaded")
            if render_mode == "shaded_edges":
                faces = self.build_ski_mesh(108, force_samples=True)
            elif render_mode == "wireframe":
                faces = self.build_ski_mesh(96, force_samples=True)
            else:
                faces = self.build_ski_mesh()
            draw_faces = []
            az = math.radians(self.light_azimuth_deg)
            el = math.radians(self.light_elevation_deg)
            lnx = math.cos(el) * math.cos(az)
            lny = math.sin(el)
            lnz = math.cos(el) * math.sin(az)
            lnx, lny, lnz = self._normalize_vec3((lnx, lny, lnz))
            duplicate_offset_cm = self.get_second_3d_side_by_side_offset_cm(faces) if self.show_ski_snowboard else None
            base_to_base = bool(getattr(self, "second_3d_base_to_base", False))
            base_sep_cm = float(getattr(self, "second_3d_base_separation_cm", 7.5))
            dovetail_preview_bounds = None
            if faces:
                dovetail_preview_bounds = self._get_dovetail_zone_bounds(
                    station_count=max(180, int(getattr(self, "full_res_mesh_samples", 120)) * 2),
                    outline_samples=max(600, int(getattr(self, "full_res_mesh_samples", 120)) * 6),
                )
                if (
                    dovetail_preview_bounds.get("tip_end_x") is None
                    and dovetail_preview_bounds.get("tail_start_x") is None
                ):
                    dovetail_preview_bounds = None
            for raw_face in faces:
                face = self._orient_face_outward(raw_face)
                rotated = [self.rotate_point(v) for v in face]
                original_visible = self._face_visible(rotated)
                if (
                    not original_visible
                    and dovetail_preview_bounds is not None
                    and self._is_dovetail_preview_wall_face(face, dovetail_preview_bounds)
                ):
                    face = list(reversed(face))
                    rotated = list(reversed(rotated))
                    original_visible = True
                if original_visible:
                    depth = self._face_depth(rotated)
                    pts = [self.project(v) for v in rotated]
                    draw_faces.append((depth, face, rotated, pts))
                if duplicate_offset_cm is not None:
                    if base_to_base:
                        # Base-to-base: rotate 180 degrees about the long axis (x), then
                        # separate along the thickness axis (z). Explicitly invert the
                        # polygon winding for the duplicated ski at mesh-build time so its
                        # visible/front-facing surfaces remain drawable across the full
                        # signed separation range, including negative offsets.
                        face2 = [(vx, -vy, (base_sep_cm - vz)) for (vx, vy, vz) in face]
                        face2 = list(reversed(face2))
                        rotated2 = [self.rotate_point(v) for v in face2]
                        if self._face_visible(rotated2):
                            depth2 = self._face_depth(rotated2)
                            pts2 = [self.project(v) for v in rotated2]
                            draw_faces.append((depth2, face2, rotated2, pts2, list(reversed(face))))
                    else:
                        # Side-by-side duplicates are mirrored in model space before
                        # rotation/projection so both skis move as one 3D assembly.
                        face2 = [(vx, -vy + duplicate_offset_cm, vz) for (vx, vy, vz) in face]
                        face2 = list(reversed(face2))
                        rotated2 = [self.rotate_point(v) for v in face2]
                        if self._face_visible(rotated2):
                            depth2 = self._face_depth(rotated2)
                            pts2 = [self.project(v) for v in rotated2]
                            draw_faces.append((depth2, face2, rotated2, pts2, list(reversed(face))))
            draw_faces.sort(key=lambda item: item[0], reverse=True)
            if render_mode == "wireframe":
                # Paint an occlusion mask using the visible front faces so wireframe
                # edges that are behind other surfaces do not show through.
                painter.setPen(Qt.PenStyle.NoPen)
                mask_color = QColor(getattr(self, "background_3d_color", QColor(46, 50, 58, 210)))
                mask_color = mask_color.darker(108)
                mask_color.setAlpha(255)
                painter.setBrush(QBrush(mask_color))
                for item in draw_faces:
                    _depth, _face, _rotated, pts = item[:4]
                    painter.drawPolygon(QPolygonF(pts))
            else:
                painter.setPen(Qt.PenStyle.NoPen)
                for item in draw_faces:
                    depth, face, rotated, pts = item[:4]
                    poly = QPolygonF(pts)
                    nx, ny, nz = self._normalize_vec3(self._face_normal(rotated))
                    ndotl = max(0.0, nx * lnx + ny * lny + nz * lnz)
                    light = max(0.0, min(1.0, self.light_brightness * (0.2 + 0.8 * ndotl)))
                    base_r = self.ski_color.red()
                    base_g = self.ski_color.green()
                    base_b = self.ski_color.blue()
                    r = max(0, min(255, int(base_r * light)))
                    g = max(0, min(255, int(base_g * light)))
                    b = max(0, min(255, int(base_b * light)))
                    painter.setBrush(QBrush(QColor(r, g, b)))
                    painter.drawPolygon(poly)

                if render_mode == "graphic":
                    self._draw_3d_graphic_overlay(painter, draw_faces, "top", self.top_graphic_image)
                    self._draw_3d_graphic_overlay(painter, draw_faces, "bottom", self.base_graphic_image)
            if render_mode in {"shaded_edges", "wireframe"}:
                self._draw_3d_outline_edges(painter, draw_faces)
        # Ski/Snowboard
        if self.show_ski_snowboard:
            second_ski_path = self.build_second_ski_shape()

            # Fill once
            painter.setBrush(QBrush(QColor(100, 10, 10, 149)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawPath(second_ski_path)

            # Optional base artwork
            if self.base_graphic_image is not None:
                self._draw_graphic_clipped(painter, second_ski_path, self.base_graphic_image, "base")

            # Outline once
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(255, 255, 255), 1))
            painter.drawPath(second_ski_path)
        # Design Aids
        if self.show_sidecut_circle:
            self.draw_sidecut_circle(painter)
        self._draw_relative_point_lock_cues(painter)
        self._draw_point_circles(painter)
        self._draw_point_dimensions(painter)
        selected_regular_points = self._get_selected_regular_points()
        if len(selected_regular_points) == 2:
            self._draw_selected_distance_preview(painter, selected_regular_points[0], selected_regular_points[1])
        elif len(selected_regular_points) == 3:
            self._draw_selected_circle_preview(painter)
        if self.show_points:
            if self.show_core_shape or self.show_tip_tail_spacers:
                self._draw_seam_editor(painter)

            for p in self.points:
                painter.setPen(QPen(QColor(120,120,120),1))
                painter.drawLine(p.pos,p.handle_in)
                painter.drawLine(p.pos,p.handle_out)
                painter.setBrush(QBrush(QColor(255,0,0)))
                painter.drawEllipse(p.handle_in,4,4)
                painter.drawEllipse(p.handle_out,4,4)
                if p.locked: 
                    if p.lock_direction == "vertical":
                        painter.setPen(QPen(QColor(255,0,255,200),1))
                        painter.setBrush(QBrush(QColor(255,0,255,200)))
                    elif p.lock_direction == "horizontal":
                        painter.setPen(QPen(QColor(0,255,255,200),1))
                        painter.setBrush(QBrush(QColor(0,255,255,200)))
                    else:
                        painter.setPen(QPen(QColor(255,255,255,200),1))         #locked ski Point Color
                        painter.setBrush(QBrush(QColor(255,255,255,200)))       #locked ski Point Color
                else:
                    painter.setPen(QPen(QColor(100,100,100,200),1))             #unlocked ski point color
                    painter.setBrush(QBrush(QColor(100,100,100,200)))           #unlocked ski point color   
                painter.drawEllipse(p.pos,6,6)

            if getattr(self, "outline_mode", "symmetric") == "asymmetric":
                self._ensure_left_points()
                for p in self.left_points:
                    painter.setPen(QPen(QColor(120,120,120),1))
                    painter.drawLine(p.pos,p.handle_in)
                    painter.drawLine(p.pos,p.handle_out)
                    painter.setBrush(QBrush(QColor(255,0,0)))
                    painter.drawEllipse(p.handle_in,4,4)
                    painter.drawEllipse(p.handle_out,4,4)
                    painter.setPen(QPen(QColor(120, 170, 255, 220),1))
                    painter.setBrush(QBrush(QColor(120, 170, 255, 200)))
                    painter.drawEllipse(p.pos,6,6)

            for p in self.core_thickness_points:

                painter.setPen(QPen(QColor(255,0,0),1))
                painter.drawLine(p.pos,p.handle_in)
                painter.drawLine(p.pos,p.handle_out)

                painter.setBrush(QBrush(QColor(255,0,0)))
                painter.drawEllipse(p.handle_in,4,4)
                painter.drawEllipse(p.handle_out,4,4)

                painter.setBrush(QBrush(QColor(0,255,0)))
                painter.drawEllipse(p.pos,5,5)

                if p.locked: 
                    if p.lock_direction == "vertical":
                        painter.setPen(QPen(QColor(255,0,255,200),1))
                        painter.setBrush(QBrush(QColor(255,0,255,200)))
                    elif p.lock_direction == "horizontal":
                        painter.setPen(QPen(QColor(0,255,255,200),1))
                        painter.setBrush(QBrush(QColor(0,255,255,200)))
                    else:
                        painter.setPen(QPen(QColor(255,255,255,200),1))         #locked ski Point Color
                        painter.setBrush(QBrush(QColor(255,255,255,200)))       #locked ski Point Color
                else:
                    painter.setPen(QPen(QColor(100,100,100,200),1))             #unlocked ski point color
                    painter.setBrush(QBrush(QColor(100,100,100,200)))           #unlocked ski point color   
                painter.drawEllipse(p.pos,6,6)

            for p in self.camber_thickness_points:

                painter.setPen(QPen(QColor(120,120,120),1))
                painter.drawLine(p.pos,p.handle_in)
                painter.drawLine(p.pos,p.handle_out)

                painter.setBrush(QBrush(QColor(255,0,0)))
                painter.drawEllipse(p.handle_in,4,4)
                painter.drawEllipse(p.handle_out,4,4)

                painter.setBrush(QBrush(QColor(0,255,0)))
                painter.drawEllipse(p.pos,5,5)

                if p.locked: 
                    if p.lock_direction == "vertical":
                        painter.setPen(QPen(QColor(255,0,255,200),1))
                        painter.setBrush(QBrush(QColor(255,0,255,200)))
                    elif p.lock_direction == "horizontal":
                        painter.setPen(QPen(QColor(0,255,255,200),1))
                        painter.setBrush(QBrush(QColor(0,255,255,200)))
                    else:
                        painter.setPen(QPen(QColor(255,255,255,200),1))         #locked ski Point Color
                        painter.setBrush(QBrush(QColor(255,255,255,200)))       #locked ski Point Color
                else:
                    painter.setPen(QPen(QColor(100,100,100,200),1))             #unlocked ski point color
                    painter.setBrush(QBrush(QColor(100,100,100,200)))           #unlocked ski point color   
                painter.drawEllipse(p.pos,6,6)

            for p in self.cosmetic_points:
                if p.selected:
                    painter.setPen(QPen(QColor(255, 210, 80, 240), 2))
                    painter.setBrush(QBrush(QColor(255, 170, 40, 240)))
                    painter.drawEllipse(p.pos, 6, 6)
                else:
                    painter.setPen(QPen(QColor(255, 170, 40, 220), 1.5))
                    painter.setBrush(QBrush(QColor(255, 140, 20, 220)))
                    painter.drawEllipse(p.pos, 5, 5)

        # ===== Core Thickness Profile =====
        core_curve = self.build_core_curve()
        flat_x = self.get_core_profile_left_x()
        core_shape = QPainterPath()
        core_shape.moveTo(QPointF(flat_x, self.core_thickness_points[0].pos.y()))
        core_shape.lineTo(self.core_thickness_points[0].pos)
        core_shape.connectPath(core_curve)
        core_shape.lineTo(QPointF(flat_x, self.core_thickness_points[-1].pos.y()))
        core_shape.closeSubpath()
        painter.setPen(QPen(QColor(200,200,200),1))
        painter.setBrush(QBrush(QColor(100,50,0,149)))
        painter.drawPath(core_shape)

        # ===== Camber Profile =====
        camber_curve = self.build_camber_curve()
        flat_x = min(p.pos.x() for p in self.camber_thickness_points)-50
        camber_shape = QPainterPath()
        camber_shape.moveTo(QPointF(flat_x, self.camber_thickness_points[0].pos.y()))
        camber_shape.lineTo(self.camber_thickness_points[0].pos)
        camber_shape.connectPath(camber_curve)
        camber_shape.lineTo(QPointF(flat_x, self.camber_thickness_points[-1].pos.y()))
        camber_shape.closeSubpath()
        painter.setPen(QPen(QColor(200,200,200),1))
        painter.setBrush(QBrush(QColor(100,50,0,149)))
        painter.drawPath(camber_shape)

        show_upper_mold = not bool(getattr(self, "show_dimensions", False))
        if show_upper_mold:
            # ===== Upper Mold Profile =====
            upper_mold_shape = self.build_upper_mold_path()
            painter.setPen(QPen(QColor(200,200,200),1))
            painter.setBrush(QBrush(QColor(100,50,0,149)))
            painter.drawPath(upper_mold_shape)
        self.draw_mold_holes(painter, include_upper=show_upper_mold)

        if self.show_global_coordinates:
            self._draw_global_coordinate_labels(painter)
        self._draw_selected_point_rings(painter)
        if self.show_dimensions:
            if not self.show_global_coordinates:
                self._begin_dimension_layout()
            # Centerlines
            painter.setPen(QPen(QColor(0,150,255),1,Qt.PenStyle.DashDotDotLine))
            self.draw_vertical_dimension_line2(
                painter,
                self.points[0].pos,
                self.points[-1].pos,
                offset_cm=0
            )
            pen = QPen(QColor(100,255,255), 1)
            painter.setPen(pen)
            # Dynamic horizontal centerline (100mm wide)
            painter.setPen(QPen(QColor(0,150,255),1,Qt.PenStyle.DashLine))
            half_width_px = 25.4  # True Centerline Half-Width
            y_top = self.points[-1].pos.y()
            y_bottom = self.points[0].pos.y()
            y_center = (y_top + y_bottom) / 2
            ski_length = y_top + y_bottom
            # Draw Centerline
            painter.drawLine(
                QPointF(-half_width_px, y_center),
                QPointF(half_width_px, y_center)
            )
            #Overall Height
            painter.setPen(QPen(QColor(255,255,255),1,Qt.PenStyle.SolidLine))
            self.draw_vertical_dimension_line(
                painter,
                self.points[0].pos,
                self.points[-1].pos,
                offset_cm=self._right_side_dimension_offset_cm(self.points[0].pos, self.points[-1].pos)
            )           
            # Effective Edge
            self.draw_vertical_dimension_line(
            painter,
            self.points[1].pos,
            self.points[-2].pos,
            offset_cm=7
            )
            # Tip Length
            self.draw_vertical_dimension_line(
            painter,
            self.points[0].pos,
            self.points[1].pos,
            offset_cm=7
            )
            # Tail Length
            self.draw_vertical_dimension_line(
            painter,
            self.points[-1].pos,
            self.points[-2].pos,
            offset_cm=7
            )
            # Camber Dim 1 - Full Height
            self.draw_vertical_dimension_line(
            painter,
            self.camber_thickness_points[1].pos,
            self.camber_thickness_points[-2].pos,
            offset_cm=8
            )          
            # Camber Dim 2
            self.draw_vertical_dimension_line(
            painter,
            self.camber_thickness_points[1].pos,
            self.camber_thickness_points[2].pos,
            offset_cm=3
            )
            # Camber Dim 3
            self.draw_vertical_dimension_line(
            painter,
            self.camber_thickness_points[2].pos,
            self.camber_thickness_points[3].pos,
            offset_cm=4
            )
            # Camber Dim 4
            self.draw_vertical_dimension_line(
            painter,
            self.camber_thickness_points[3].pos,
            self.camber_thickness_points[4].pos,
            offset_cm=4
            )
            # Camber Dim 5
            self.draw_vertical_dimension_line(
            painter,
            self.camber_thickness_points[4].pos,
            self.camber_thickness_points[5].pos,
            offset_cm=3
            )

            self.draw_camber_thickness_horizontal_dimensions(painter)
            
            core_pts = self.core_thickness_points
            if len(core_pts) >= 2:
                for i in range(len(core_pts) - 1):
                    self.draw_vertical_dimension_line(
                        painter,
                        core_pts[i].pos,
                        core_pts[i + 1].pos,
                        offset_cm=4,
                    )
            #-------------------------------------------------------------

            self.draw_core_thickness_horizontal_dimensions(painter)
            #----------------------------------------------------------------------
            # Dimension from dynamic horizontal centerline to middle control point
            centerline_point = QPointF(0, y_center)
            mid_point = self.points[2].pos

            self.draw_vertical_dimension_line(
                painter,
                centerline_point,
                mid_point,
                offset_cm=3
            )

            for p in self.points:
                self.draw_mirror_dimension(painter, p.pos, pen)
 
        owner = getattr(self, "owner_window", None)
        if owner is not None and hasattr(owner, "draw_selected_cnc_shape_overlay"):
            owner.draw_selected_cnc_shape_overlay(painter)

        self._draw_hover_point_ring(painter)
        self._draw_selected_point_rings(painter)
        self._draw_selection_box(painter)
        if owner is not None and hasattr(owner, "should_show_main_window_cnc_view") and owner.should_show_main_window_cnc_view():
            if hasattr(owner, "draw_main_window_cnc_toolpath_view"):
                owner.draw_main_window_cnc_toolpath_view(painter)
        elif owner is None or not hasattr(owner, "should_draw_stiffness_plot") or owner.should_draw_stiffness_plot():
            self.draw_stiffness_plot(painter)

        # Draw stats
        owner = getattr(self, "owner_window", None)
        if owner is None or not hasattr(owner, "should_draw_stats") or owner.should_draw_stats():
            painter.resetTransform()
            painter.setFont(QFont("Kristen ITC",14))
            stats = [                               #All the dynamic stats
                f"Length: {self.get_ski_length():.1f} cm",
                f"Camber Curve Length: {self.get_camber_curve_length(1, 5):.1f} cm",
                f"Tip Width: {self.get_tip_width():.1f} mm",
                f"Waist Width: {self.get_waist_width():.1f} mm",
                f"Tail Width: {self.get_tail_width():.1f} mm",
                f"Area Above Centerline: {self.get_main_shape_area_above_centerline_cm2():.1f} cm²",
                f"Area Behind Centerline: {self.get_main_shape_area_behind_centerline_cm2():.1f} cm²",
                f"Area Above Boot Center: {self.get_main_shape_area_above_boot_center_cm2():.1f} cm²",
                f"Area Below Boot Center: {self.get_main_shape_area_below_boot_center_cm2():.1f} cm²",
            ]
            if getattr(self, "outline_mode", "symmetric") == "asymmetric":
                self._ensure_left_points()
                stats.insert(2, f"Right Turning Radius: {.01*self.get_turning_radius_for_points(self.points):.1f} m")
                stats.insert(3, f"Left Turning Radius: {.01*self.get_turning_radius_for_points(self.left_points):.1f} m")
            else:
                stats.insert(2, f"Turning Radius: {.01*self.get_turning_radius():.1f} m")
            metrics = painter.fontMetrics()
            line_h = metrics.height() + 6
            box_x = 14
            box_y = 10
            if owner is not None and hasattr(owner, "should_draw_cnc_stats") and owner.should_draw_cnc_stats():
                box_y = 96
            box_w = max(metrics.horizontalAdvance(s) for s in stats) + 28
            box_h = line_h * len(stats) + 18
            painter.setPen(QPen(QColor(210, 220, 235, 235), 1.2))
            painter.setBrush(QBrush(QColor(22, 24, 30, 175)))
            painter.drawRoundedRect(QRectF(box_x, box_y, box_w, box_h), 12, 12)
            painter.setPen(QPen(QColor(255,255,255)))
            y = box_y + metrics.ascent() + 10
            for s in stats:
                painter.drawText(box_x + 13, y, s)
                y += line_h

        if owner is not None and hasattr(owner, "should_draw_cnc_stats") and owner.should_draw_cnc_stats():
            painter.resetTransform()
            painter.setFont(QFont("Kristen ITC",14))
            cnc_stats = []
            if hasattr(owner, "get_cnc_shape_start_stat_text"):
                start_stat = owner.get_cnc_shape_start_stat_text()
                if start_stat:
                    cnc_stats.append(start_stat)
            if hasattr(owner, "get_cnc_shape_center_stat_text"):
                center_stat = owner.get_cnc_shape_center_stat_text()
                if center_stat:
                    cnc_stats.append(center_stat)
            if not cnc_stats:
                cnc_stats.append("No CNC shape selected")
            metrics = painter.fontMetrics()
            line_h = metrics.height() + 6
            box_x = 14
            box_y = 10
            box_w = max(metrics.horizontalAdvance(s) for s in cnc_stats) + 28
            box_h = line_h * len(cnc_stats) + 18
            painter.setPen(QPen(QColor(210, 220, 235, 235), 1.2))
            painter.setBrush(QBrush(QColor(22, 24, 30, 175)))
            painter.drawRoundedRect(QRectF(box_x, box_y, box_w, box_h), 12, 12)
            painter.setPen(QPen(QColor(255,255,255)))
            y = box_y + metrics.ascent() + 10
            for s in cnc_stats:
                painter.drawText(box_x + 13, y, s)
                y += line_h

        if owner is not None and hasattr(owner, "should_draw_interface_shortcuts") and owner.should_draw_interface_shortcuts():
            painter.resetTransform()
            painter.setFont(QFont("Kristen ITC",14))
            shortcuts = [
                "Interface Shortcuts",
                "Ctrl + Z: Undo",
                "Ctrl + Y: Redo",
                "Delete: Remove selected points",
                "Arrow keys: Nudge selected point 0.5 mm",
                "Shift/Cmd + arrows: Nudge selected point 0.1 mm",
                "L: Toggle colinear tangent lock",
                "H: Toggle horizontal tangent lock",
                "V: Toggle vertical tangent lock",
                "I: Toggle paired vertical tangent lock",
                "O: Toggle paired horizontal tangent lock",
                "D: Toggle dimension between 2 selected points",
                "C: Toggle 3-point circle",
                "Hold A + double click: Add left edge point in asymmetrical mode",
                "Hold C + double click: Add camber profile point",
                "Hold T + double click: Add core thickness point",
                "Shift + click/drag select: Add to selection",
                "Hold Z + drag select: Zoom to box + 20%",
                "Ctrl + double click: Add cosmetic point",
                "Shift + MMB drag: Axis-constrained pan",
                "Shift + RMB drag: Alternate 3D orbit behavior",
            ]
            metrics = painter.fontMetrics()
            line_h = metrics.height() + 6
            box_x = 14
            viewport_h = 0
            if hasattr(owner, "view") and owner.view is not None and owner.view.viewport() is not None:
                viewport_h = owner.view.viewport().height()
            box_w = max(metrics.horizontalAdvance(s) for s in shortcuts) + 28
            box_h = line_h * len(shortcuts) + 18
            box_y = max(10, viewport_h - box_h - 14) if viewport_h > 0 else 10
            painter.setPen(QPen(QColor(210, 220, 235, 235), 1.2))
            painter.setBrush(QBrush(QColor(22, 24, 30, 175)))
            painter.drawRoundedRect(QRectF(box_x, box_y, box_w, box_h), 12, 12)
            painter.setPen(QPen(QColor(255,255,255)))
            y = box_y + metrics.ascent() + 10
            for s in shortcuts:
                painter.drawText(box_x + 13, y, s)
                y += line_h

        self._draw_measurement_popup(painter)

        # Scale overlay is drawn in SkiView.drawForeground so it stays screen-fixed

    def draw_core_thickness_horizontal_dimensions(self, painter):
        core_pts = self.core_thickness_points

        if len(core_pts) < 2:
            return

        # spacing so labels don’t overlap
        base_offset_cm = -5
        offset_step_cm = -10

        for i in range(len(core_pts) - 1):
            p1 = core_pts[i].pos
            p2 = core_pts[i + 1].pos

            # skip tiny segments (optional but helps cleanliness)
            if abs(p2.x() - p1.x()) < 0.01:
                continue

            offset = base_offset_cm + i * offset_step_cm

            self.draw_horizontal_dimension_line(
                painter,
                p1,
                p2,
                offset_cm=offset,
                text_offset_px_v=2,
                text_offset_px_h=-50,
            )

    def draw_camber_thickness_horizontal_dimensions(self, painter):
        camber_pts = self.camber_thickness_points

        if len(camber_pts) < 2:
            return

        # spacing so labels don’t overlap
        base_offset_cm = -5
        offset_step_cm = -8

        for i in range(len(camber_pts) - 1):
            p1 = camber_pts[i].pos
            p2 = camber_pts[i + 1].pos

            # skip tiny segments (optional but helps cleanliness)
            if abs(p2.x() - p1.x()) < 0.01:
                continue

            offset = base_offset_cm + i * offset_step_cm

            self.draw_horizontal_dimension_line(
                painter,
                p1,
                p2,
                offset_cm=offset,
                text_offset_px_v=-5,
                text_offset_px_h=-50,
            )



    # Interaction  
    def dist(self,a,b):
        return math.hypot(a.x()-b.x(),a.y()-b.y())
    def find_hit(self,pos):

        for p in self.points:
            if self.dist(pos,p.pos)<10:
                return p,"point"
            if self.dist(pos,p.handle_in)<8:
                return p,"handle_in"
            if self.dist(pos,p.handle_out)<8:
                return p,"handle_out"

        if getattr(self, "outline_mode", "symmetric") == "asymmetric":
            self._ensure_left_points()
            for p in self.left_points:
                if self.dist(pos,p.pos)<10:
                    return p,"point"
                if self.dist(pos,p.handle_in)<8:
                    return p,"handle_in"
                if self.dist(pos,p.handle_out)<8:
                    return p,"handle_out"

        for p in self.core_thickness_points:
            if self.dist(pos,p.pos)<10:
                return p,"point"
            if self.dist(pos,p.handle_in)<8:
                return p,"handle_in"
            if self.dist(pos,p.handle_out)<8:
                return p,"handle_out"

        for p in self.camber_thickness_points:
            if self.dist(pos,p.pos)<10:
                return p,"point"
            if self.dist(pos,p.handle_in)<8:
                return p,"handle_in"
            if self.dist(pos,p.handle_out)<8:
                return p,"handle_out"

        for p in self.cosmetic_points:
            if self.dist(pos, p.pos) < 10:
                return p, "point"

        for handle in self.get_seam_editor_handles():
            if self.dist(pos, handle["pos"]) < 10:
                return handle, "seam_handle"

        return None,None
    def _draw_lock_badge(self, painter, text, anchor):
        painter.save()
        painter.setPen(QPen(QColor(255, 255, 255, 245), 1.2))
        painter.drawText(anchor, text)
        painter.restore()
    def _draw_relative_point_lock_cues(self, painter):
        self._prune_relative_point_locks()
        if not self.relative_point_locks:
            return
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for entry in self.relative_point_locks:
            point_a = self._get_point_by_uid(entry["a"])
            point_b = self._get_point_by_uid(entry["b"])
            if point_a is None or point_b is None:
                continue
            if entry["axis"] == "vertical":
                pen = QPen(QColor(255, 0, 255, 220), 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                x = (point_a.pos.x() + point_b.pos.x()) / 2.0
                y0 = min(point_a.pos.y(), point_b.pos.y()) - 12.0
                y1 = max(point_a.pos.y(), point_b.pos.y()) + 12.0
                painter.drawLine(QPointF(x, y0), QPointF(x, y1))
                painter.drawLine(QPointF(x - 6.0, point_a.pos.y()), QPointF(x + 6.0, point_a.pos.y()))
                painter.drawLine(QPointF(x - 6.0, point_b.pos.y()), QPointF(x + 6.0, point_b.pos.y()))
                self._draw_lock_badge(painter, "V", QPointF(x + 18.0, (y0 + y1) / 2.0 - 14.0))
            elif entry["axis"] == "horizontal":
                pen = QPen(QColor(0, 255, 255, 220), 2, Qt.PenStyle.DashLine)
                painter.setPen(pen)
                y = (point_a.pos.y() + point_b.pos.y()) / 2.0
                x0 = min(point_a.pos.x(), point_b.pos.x()) - 12.0
                x1 = max(point_a.pos.x(), point_b.pos.x()) + 12.0
                painter.drawLine(QPointF(x0, y), QPointF(x1, y))
                painter.drawLine(QPointF(point_a.pos.x(), y - 6.0), QPointF(point_a.pos.x(), y + 6.0))
                painter.drawLine(QPointF(point_b.pos.x(), y - 6.0), QPointF(point_b.pos.x(), y + 6.0))
                self._draw_lock_badge(painter, "H", QPointF((x0 + x1) / 2.0 + 8.0, y + 30.0))
        painter.restore()
    def _draw_point_circles(self, painter):
        entries = self._get_circle_entries()
        if not entries:
            return
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for idx, (_pts, center, radius) in enumerate(entries, start=1):
            painter.setPen(QPen(QColor(255, 210, 80, 220), 2, Qt.PenStyle.DashLine))
            painter.drawEllipse(center, radius, radius)
            painter.setPen(QPen(QColor(255, 210, 80, 220), 1.5))
            radial_point = QPointF(center.x() + radius / math.sqrt(2.0), center.y() - radius / math.sqrt(2.0))
            painter.drawLine(center, radial_point)
            painter.setPen(QPen(QColor(255, 240, 160, 230), 1))
            label_pos = QPointF((center.x() + radial_point.x()) / 2.0 + 8.0, (center.y() + radial_point.y()) / 2.0 - 6.0)
            painter.drawText(label_pos, f"R {radius / PIXELS_PER_CM:.1f} cm")
            painter.drawText(QPointF(label_pos.x(), label_pos.y() + painter.fontMetrics().height() + 2.0), f"Circle {idx}")
        painter.restore()
    def _draw_selected_circle_preview(self, painter):
        selected_points = self._get_selected_circle_points()
        if len(selected_points) != 3:
            return
        circle = self._circle_from_points(selected_points[0].pos, selected_points[1].pos, selected_points[2].pos)
        if circle is None:
            return
        center, radius = circle
        painter.save()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor(255, 255, 255, 160), 1.5, Qt.PenStyle.DotLine))
        painter.drawEllipse(center, radius, radius)
        for p in selected_points:
            painter.drawLine(center, p.pos)
        label_pos = QPointF(center.x() + radius + 8.0, center.y() - 8.0)
        painter.drawText(label_pos, f"R {radius / PIXELS_PER_CM:.1f} cm")
        painter.restore()
    def _dimension_label_position(self, point_a, point_b, offset_px=14.0):
        dx = point_b.pos.x() - point_a.pos.x()
        dy = point_b.pos.y() - point_a.pos.y()
        length = math.hypot(dx, dy)
        mid = QPointF((point_a.pos.x() + point_b.pos.x()) / 2.0, (point_a.pos.y() + point_b.pos.y()) / 2.0)
        if length <= 1e-9:
            return QPointF(mid.x() + 8.0, mid.y() - 8.0)
        nx = -dy / length
        ny = dx / length
        if ny > 0:
            nx = -nx
            ny = -ny
        return QPointF(mid.x() + nx * offset_px, mid.y() + ny * offset_px)
    def _draw_selected_distance_preview(self, painter, point_a, point_b):
        distance_px = self._distance_between_points(point_a, point_b)
        if distance_px <= 1e-9:
            return
        painter.save()
        painter.setPen(QPen(QColor(255, 215, 0, 200), 1.5, Qt.PenStyle.DotLine))
        painter.drawLine(point_a.pos, point_b.pos)
        label_pos = self._dimension_label_position(point_a, point_b, offset_px=16.0)
        painter.setPen(QPen(QColor(255, 235, 150, 230), 1.0))
        painter.drawText(label_pos, f"{distance_px / PIXELS_PER_CM:.1f} cm")
        painter.restore()
    def _draw_point_dimensions(self, painter):
        entries = self._get_dimension_entries()
        if not entries:
            return
        painter.save()
        for idx, (point_a, point_b, distance_px) in enumerate(entries, start=1):
            painter.setPen(QPen(QColor(120, 255, 180, 220), 1.6, Qt.PenStyle.DashLine))
            painter.drawLine(point_a.pos, point_b.pos)
            label_pos = self._dimension_label_position(point_a, point_b, offset_px=16.0)
            painter.setPen(QPen(QColor(190, 255, 220, 235), 1.0))
            painter.drawText(label_pos, f"{distance_px / PIXELS_PER_CM:.1f} cm")
            painter.drawText(QPointF(label_pos.x(), label_pos.y() + painter.fontMetrics().height() + 2.0), f"Distance {idx}")
        painter.restore()
    def _measurement_table_rows(self):
        rows = []
        for idx, (_point_a, _point_b, distance_px) in enumerate(self._get_dimension_entries(), start=1):
            rows.append((f"Distance {idx}", f"{distance_px / PIXELS_PER_CM:.1f} cm"))
        for idx, (_pts, _center, radius) in enumerate(self._get_circle_entries(), start=1):
            rows.append((f"Circle {idx}", f"R {radius / PIXELS_PER_CM:.1f} cm"))
        return rows
    def _refresh_measurement_table(self):
        self.update()
        owner = getattr(self, "owner_window", None)
        view = getattr(owner, "view", None) if owner is not None else None
        viewport = view.viewport() if view is not None else None
        if viewport is not None:
            viewport.update()
    def _draw_measurement_popup(self, painter):
        rows = self._measurement_table_rows()
        if not rows:
            return
        owner = getattr(self, "owner_window", None)
        if owner is None or not hasattr(owner, "view") or owner.view is None or owner.view.viewport() is None:
            return
        viewport_rect = owner.view.viewport().rect()
        painter.save()
        painter.resetTransform()
        painter.setFont(QFont("Kristen ITC", 14))
        metrics = painter.fontMetrics()
        line_h = metrics.height() + 6
        title = "Locked Features"
        feature_header = "Feature"
        value_header = "Value"
        feature_w = max([metrics.horizontalAdvance(feature_header)] + [metrics.horizontalAdvance(row[0]) for row in rows])
        value_w = max([metrics.horizontalAdvance(value_header)] + [metrics.horizontalAdvance(row[1]) for row in rows])
        col_gap = 24
        pad = 13
        box_w = max(metrics.horizontalAdvance(title), feature_w + value_w + col_gap) + pad * 2
        box_h = line_h * (len(rows) + 2) + 22
        box_x = max(14, viewport_rect.width() - box_w - 16)
        box_y = max(10, viewport_rect.height() - box_h - 16)
        painter.setPen(QPen(QColor(210, 220, 235, 235), 1.2))
        painter.setBrush(QBrush(QColor(22, 24, 30, 190)))
        painter.drawRoundedRect(QRectF(box_x, box_y, box_w, box_h), 12, 12)
        painter.setPen(QPen(QColor(255, 255, 255)))
        y = box_y + metrics.ascent() + 10
        painter.drawText(box_x + pad, y, title)
        y += line_h
        header_y = y
        value_x = box_x + pad + feature_w + col_gap
        painter.setPen(QPen(QColor(210, 220, 235, 235)))
        painter.drawText(box_x + pad, header_y, feature_header)
        painter.drawText(value_x, header_y, value_header)
        divider_y = header_y + 6
        painter.setPen(QPen(QColor(210, 220, 235, 110), 1))
        painter.drawLine(QPointF(box_x + pad, divider_y), QPointF(box_x + box_w - pad, divider_y))
        y += line_h
        painter.setPen(QPen(QColor(255, 255, 255)))
        for feature, value in rows:
            painter.drawText(box_x + pad, y, feature)
            painter.drawText(value_x, y, value)
            y += line_h
        painter.restore()
    def _draw_selected_point_rings(self, painter):
        selected_points = self._get_selected_regular_points()
        if not selected_points:
            return
        painter.save()
        painter.setPen(QPen(QColor(255, 0, 0, 220), 3))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        for p in selected_points:
            handle_kind = getattr(p, "selected_handle_kind", None)
            if handle_kind == "handle_in" and hasattr(p, "handle_in"):
                painter.drawEllipse(p.handle_in, 9, 9)
            elif handle_kind == "handle_out" and hasattr(p, "handle_out"):
                painter.drawEllipse(p.handle_out, 9, 9)
            else:
                painter.drawEllipse(p.pos, 9, 9)
        painter.restore()
    def _selection_rect(self):
        if self.selection_box_origin is None or self.selection_box_current is None:
            return QRectF()
        return QRectF(self.selection_box_origin, self.selection_box_current).normalized()
    def _update_selection_box_preview(self):
        if not self.selection_box_active:
            return
        if getattr(self, "selection_box_zoom", False):
            return
        rect = self._selection_rect()
        if rect.isNull() or rect.width() < 2.0 or rect.height() < 2.0:
            return
        if not self.selection_box_additive and not self.selection_box_toggle:
            self._clear_regular_point_selection()
        for p in self._iter_selectable_points():
            inside = rect.contains(p.pos)
            if self.selection_box_toggle:
                p.selected = inside
                if hasattr(p, "selected_handle_kind"):
                    p.selected_handle_kind = None
            elif inside:
                p.selected = True
                if hasattr(p, "selected_handle_kind"):
                    p.selected_handle_kind = None
        self._sync_multi_select_order()
    def _finish_selection_box(self):
        if not self.selection_box_active:
            return
        self._update_selection_box_preview()
        self.selection_box_active = False
        self.selection_box_origin = None
        self.selection_box_current = None
        self.selection_box_additive = False
        self.selection_box_toggle = False
        self.selection_box_zoom = False
        self.update()
    def _finish_zoom_box(self):
        if not self.selection_box_active:
            return
        rect = self._selection_rect()
        self.selection_box_active = False
        self.selection_box_origin = None
        self.selection_box_current = None
        self.selection_box_additive = False
        self.selection_box_toggle = False
        self.selection_box_zoom = False
        if not rect.isNull() and rect.width() >= 4.0 and rect.height() >= 4.0:
            scene_rect = self.mapToScene(rect).boundingRect()
            scene = self.scene()
            views = scene.views() if scene is not None else []
            if views and hasattr(views[0], "zoom_to_scene_rect"):
                views[0].zoom_to_scene_rect(scene_rect, extra_scale=1.2)
        self.update()
    def _draw_selection_box(self, painter):
        if not self.selection_box_active:
            return
        rect = self._selection_rect()
        if rect.isNull():
            return
        painter.save()
        if getattr(self, "selection_box_zoom", False):
            painter.setPen(QPen(QColor(255, 215, 120, 235), 1.8, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(255, 215, 120, 38)))
        else:
            painter.setPen(QPen(QColor(140, 190, 255, 230), 1.5, Qt.PenStyle.DashLine))
            painter.setBrush(QBrush(QColor(140, 190, 255, 40)))
        painter.drawRect(rect)
        painter.restore()
    def _draw_hover_point_ring(self, painter):
        if self.hover_point_uid is None:
            return
        point = self._get_point_by_uid(self.hover_point_uid)
        if point is None or getattr(point, 'selected', False):
            return
        painter.save()
        painter.setPen(QPen(QColor(255, 255, 255, 180), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(point.pos, 8, 8)
        painter.restore()
    def hoverMoveEvent(self, event):
        hit, typ = self.find_hit(event.pos())
        if typ == 'point' and hit is not None:
            self._ensure_point_ids()
            self.hover_point_uid = getattr(hit, 'uid', None)
        else:
            self.hover_point_uid = None
        self.update()
        super().hoverMoveEvent(event)
    def hoverLeaveEvent(self, event):
        self.hover_point_uid = None
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self,event):
        self.setFocus()
        if event.button() != Qt.MouseButton.LeftButton:
            super().mousePressEvent(event)
            return
        hit,typ=self.find_hit(event.pos())
        if hit:
            self.push_undo()
        shift_held = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        regular_hit = hit if typ != "seam_handle" else None
        if regular_hit is None and typ != "seam_handle":
            self.dragging_point = None
            self.drag_type = None
            self.selected_seam_handle = None
            for p in [self.tip_seam_center, self.tail_seam_center] + self.tip_seam_points + self.tail_seam_points:
                p.selected = False
            self.selection_box_active = True
            self.selection_box_origin = QPointF(event.pos())
            self.selection_box_current = QPointF(event.pos())
            self.selection_box_additive = shift_held
            self.selection_box_toggle = False
            self.selection_box_zoom = bool(getattr(self, "zoom_box_key", False))
            if self.selection_box_zoom:
                self.selection_box_additive = False
            elif not shift_held:
                self._clear_regular_point_selection()
            self.update()
            event.accept()
            return
        if not shift_held or regular_hit is None:
            self._clear_regular_point_selection()
        for p in [self.tip_seam_center, self.tail_seam_center] + self.tip_seam_points + self.tail_seam_points:
            p.selected = False
        self.selected_seam_handle = None
        if hit:
            if typ != "seam_handle":
                self._select_regular_point(hit, additive=shift_held)
                if getattr(hit, "selected", False):
                    hit.selected_handle_kind = typ if typ in ("handle_in", "handle_out") else None
            else:
                seam_points = self.tip_seam_points if hit["seam"] == "tip" else self.tail_seam_points
                if hit.get("kind") in ("center_point", "center_handle_in", "center_handle_out"):
                    center_point = self.tip_seam_center if hit["seam"] == "tip" else self.tail_seam_center
                    center_point.selected = True
                    self.selected_seam_handle = (hit["seam"], -1, hit["kind"])
                elif 0 <= hit.get("index", -1) < len(seam_points):
                    seam_points[hit["index"]].selected = True
                    self.selected_seam_handle = (hit["seam"], hit["index"], hit["kind"])
            self.dragging_point=hit
            self.drag_type=typ
        else:
            self.dragging_point = None
            self.drag_type = None
        self._sync_multi_select_order()
        self.update()
    def mouseMoveEvent(self,event):
        if self.restoring_state:
            return
        if self.selection_box_active:
            self.selection_box_current = QPointF(event.pos())
            self._update_selection_box_preview()
            self.update()
            event.accept()
            return
        if not self.dragging_point:
            return

        pos=event.pos()
        p=self.dragging_point

        if self.drag_type == "point":
            delta = pos - p.pos
            if isinstance(p, CosmeticPoint):
                p.pos = QPointF(pos)
            else:
                # Lock first and last control point horizontally
                if p == self.points[0] or p == self.points[-1]:
                    # Only allow vertical movement
                    new_pos = QPointF(0, pos.y())
                    delta = new_pos - p.pos
                    p.pos = new_pos
                else:
                    p.pos = pos
                p.handle_in += delta
                p.handle_out += delta

        elif self.drag_type=="handle_in":
            p.handle_in=pos
            if p.locked:
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_out=QPointF(p.pos.x()+dx,p.pos.y()+dy)
            if p.lock_direction=="vertical": 
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_out=QPointF(p.pos.x(),p.pos.y()+dy)
                p.handle_in=QPointF(p.pos.x(),p.pos.y()-dy)
            if p.lock_direction=="horizontal": 
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_out=QPointF(p.pos.x()+dx,p.pos.y())
                p.handle_in=QPointF(p.pos.x()-dx,p.pos.y())

        elif self.drag_type=="handle_out":
            p.handle_out=pos
            if p.locked:
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_in=QPointF(p.pos.x()+dx,p.pos.y()+dy)
            if p.lock_direction=="vertical": 
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_out=QPointF(p.pos.x(),p.pos.y()-dy)
                p.handle_in=QPointF(p.pos.x(),p.pos.y()+dy)
            if p.lock_direction=="horizontal": 
                dx=p.pos.x()-pos.x()
                dy=p.pos.y()-pos.y()
                p.handle_out=QPointF(p.pos.x()-dx,p.pos.y())
                p.handle_in=QPointF(p.pos.x()+dx,p.pos.y())
        elif self.drag_type=="seam_handle":
            self._set_seam_handle_from_pos(p["seam"], p["kind"], p.get("index", 0), pos)
            return

        self.apply_design_constraints()
        self._cache.clear()
        self.update()
    def mouseReleaseEvent(self,event):
        if self.selection_box_active and event.button() == Qt.MouseButton.LeftButton:
            if getattr(self, "selection_box_zoom", False):
                self._finish_zoom_box()
            else:
                self._finish_selection_box()
            event.accept()
            return
        dragged_shape_point = self.dragging_point is not None and self.drag_type in ("point", "handle_in", "handle_out", "seam_handle")
        self.dragging_point=None
        self.drag_type = None
        if dragged_shape_point:
            owner = getattr(self, "owner_window", None)
            if owner is not None and hasattr(owner, "refresh_cnc_after_shape_edit"):
                owner.refresh_cnc_after_shape_edit()
        self.update()
    def _selected_seam_points(self):
        selected = []
        for seam_name, center_point, points in (("tip", self.tip_seam_center, self.tip_seam_points), ("tail", self.tail_seam_center, self.tail_seam_points)):
            if center_point.selected:
                selected.append((seam_name, -1, center_point))
            for idx, p in enumerate(points):
                if p.selected:
                    selected.append((seam_name, idx, p))
        return selected
    def _insert_profile_point(self, point_list, point):
        self.push_undo()
        self.selection_box_active = False
        self.selection_box_origin = None
        self.selection_box_current = None
        self._clear_regular_point_selection()
        point_list.append(point)
        point_list.sort(key=lambda p: p.pos.y(), reverse=True)
        self._assign_point_uid(point)
        point.selected = True
        self.multi_select_order = [point.uid]
        self.apply_design_constraints()
        self._cache.clear()
        self.update()

    def _insert_asymmetric_left_edge_point(self, point):
        self.push_undo()
        self.selection_box_active = False
        self.selection_box_origin = None
        self.selection_box_current = None
        self._ensure_left_points()
        self._clear_regular_point_selection()
        self.left_points.append(point)
        self.left_points.sort(key=lambda p: p.pos.y(), reverse=True)
        self._assign_point_uid(point)
        point.selected = True
        self.multi_select_order = [point.uid]
        self.apply_design_constraints()
        self._cache.clear()
        self.update()

    def mouseDoubleClickEvent(self,event):
        if event.button() != Qt.MouseButton.LeftButton:
            super().mouseDoubleClickEvent(event)
            return
        if (
            getattr(self, "left_edge_insert_key", False)
            and getattr(self, "outline_mode", "symmetric") == "asymmetric"
        ):
            self._insert_asymmetric_left_edge_point(ControlPointMid(QPointF(event.pos())))
            event.accept()
            return
        if getattr(self, "profile_insert_key", None) == "camber":
            self._insert_profile_point(self.camber_thickness_points, ControlPointCoreCamber1(QPointF(event.pos())))
            event.accept()
            return
        if getattr(self, "profile_insert_key", None) == "thickness":
            self._insert_profile_point(self.core_thickness_points, ControlPointCoreThickness(QPointF(event.pos())))
            event.accept()
            return
        self.push_undo()
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            new = CosmeticPoint(event.pos())
            self._assign_point_uid(new)
            self.cosmetic_points.append(new)
            self._clear_regular_point_selection()
            new.selected = True
            self.multi_select_order = [new.uid]
        else:
            new=ControlPointMid(event.pos())
            self._assign_point_uid(new)
            self.points.append(new)
            self.points.sort(key=lambda p:p.pos.y(), reverse=True)
            self.apply_design_constraints()
        self._cache.clear()
        self.update()
    def keyPressEvent(self,event):
        if not event.isAutoRepeat():
            if event.key() == Qt.Key.Key_C:
                self.profile_insert_key = "camber"
            elif event.key() == Qt.Key.Key_T:
                self.profile_insert_key = "thickness"
            elif event.key() == Qt.Key.Key_A:
                self.left_edge_insert_key = True
            elif event.key() == Qt.Key.Key_Z and not (event.modifiers() & Qt.KeyboardModifier.ControlModifier):
                self.zoom_box_key = True

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() in (Qt.Key.Key_Z, Qt.Key.Key_Y):
            if event.key() == Qt.Key.Key_Z:
                self.undo()
            elif event.key() == Qt.Key.Key_Y:
                self.redo()
        elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down):
            fine_nudge = bool(event.modifiers() & (Qt.KeyboardModifier.ShiftModifier | Qt.KeyboardModifier.ControlModifier))
            step_px = PIXELS_PER_MM * (0.1 if fine_nudge else 0.5)
            dx = 0.0
            dy = 0.0
            if event.key() == Qt.Key.Key_Left:
                dx = -step_px
            elif event.key() == Qt.Key.Key_Right:
                dx = step_px
            elif event.key() == Qt.Key.Key_Up:
                dy = -step_px
            elif event.key() == Qt.Key.Key_Down:
                dy = step_px
            if abs(dx) > 1e-9 or abs(dy) > 1e-9:
                if not event.isAutoRepeat():
                    self.push_undo()
                if self._nudge_selected_points(QPointF(dx, dy)):
                    event.accept()
                    return
        elif event.key()==Qt.Key.Key_Delete:
            self.push_undo()
            self.points=[p for p in self.points if not p.selected]
            if hasattr(self, "left_points"):
                self.left_points=[p for p in self.left_points if not p.selected]
            self.core_thickness_points=[p for p in self.core_thickness_points if not p.selected]
            self.camber_thickness_points=[p for p in self.camber_thickness_points if not p.selected]
            self.cosmetic_points=[p for p in self.cosmetic_points if not p.selected]
            self._prune_relative_point_locks()
            self._prune_point_circles()
            self._prune_point_dimensions()
            self._sync_multi_select_order()
            self.apply_design_constraints()
            self.update()
        elif event.key()==Qt.Key.Key_L:
            self.push_undo()
            for p in self.points:
                if p.selected:
                    p.locked=not p.locked
            for p in self.core_thickness_points:
                if p.selected:
                    p.locked=not p.locked
            for p in self.camber_thickness_points:
                if p.selected:
                    p.locked=not p.locked
            for _, _, p in self._selected_seam_points():
                p.locked = not p.locked
            self._cache.clear()
            self.update()
        elif event.key() == Qt.Key.Key_H:
            self.push_undo()
            for p in self.points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="horizontal"
            for p in self.core_thickness_points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="horizontal"            
            for p in self.camber_thickness_points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="horizontal"
            for _, _, p in self._selected_seam_points():
                if p.lock_direction=="vertical":
                    p.lock_direction=None
                elif p.lock_direction=="horizontal":
                    p.lock_direction=None
                else:
                    p.lock_direction="horizontal"
            self._cache.clear()
            self.update()
        elif event.key() == Qt.Key.Key_V:
            self.push_undo()
            for p in self.points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="vertical"
            for p in self.core_thickness_points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="vertical"
            for p in self.camber_thickness_points:
                if p.selected:
                    if p.lock_direction=="vertical":
                        p.lock_direction=None
                    elif p.lock_direction=="horizontal":
                        p.lock_direction=None
                    else:
                        p.lock_direction="vertical"
            for _, _, p in self._selected_seam_points():
                if p.lock_direction=="vertical":
                    p.lock_direction=None
                elif p.lock_direction=="horizontal":
                    p.lock_direction=None
                else:
                    p.lock_direction="vertical"
            self._cache.clear()
            self.update()
        elif event.key() in (Qt.Key.Key_I, Qt.Key.Key_O):
            selected_points = self._get_selected_regular_points()
            if len(selected_points) == 2:
                self.push_undo()
                axis = "vertical" if event.key() == Qt.Key.Key_I else "horizontal"
                self._set_relative_point_lock(selected_points[0], selected_points[1], axis)
                self.apply_design_constraints()
                self._cache.clear()
                self.update()
        elif event.key() == Qt.Key.Key_D:
            selected_points = self._get_selected_regular_points()
            if len(selected_points) == 2:
                distance_px = self._distance_between_points(selected_points[0], selected_points[1])
                if distance_px > 1e-9:
                    self.push_undo()
                    self._toggle_point_dimension(selected_points)
                    self.apply_design_constraints()
                    self._cache.clear()
                    self._refresh_measurement_table()
        elif event.key() == Qt.Key.Key_C:
            selected_points = self._get_selected_circle_points()
            if len(selected_points) == 3:
                circle = self._circle_from_points(selected_points[0].pos, selected_points[1].pos, selected_points[2].pos)
                if circle is not None:
                    self.push_undo()
                    self._toggle_point_circle(selected_points)
                    self._cache.clear()
                    self._refresh_measurement_table()
    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            if event.key() == Qt.Key.Key_C and getattr(self, "profile_insert_key", None) == "camber":
                self.profile_insert_key = None
            elif event.key() == Qt.Key.Key_T and getattr(self, "profile_insert_key", None) == "thickness":
                self.profile_insert_key = None
            elif event.key() == Qt.Key.Key_A:
                self.left_edge_insert_key = False
            elif event.key() == Qt.Key.Key_Z:
                self.zoom_box_key = False
        super().keyReleaseEvent(event)
    # Dimension Call Outs
    def draw_mirror_dimension(self, painter, point, pen=None, arrow_size=8):
        if self.restoring_state:
            return
        if pen is not None:
            painter.setPen(pen)

        p1 = point
        p2 = QPointF(-point.x(), point.y())

        # Draw main line
        painter.drawLine(p1, p2)
        self._register_dimension_segment(p1, p2)

        # Compute direction vector
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        length = math.hypot(dx, dy)

        if length == 0:
            return

        ux = dx / length
        uy = dy / length

        # Perpendicular vector
        px = -uy
        py = ux

        # Arrowhead function
        def draw_arrow(base, direction):

            bx, by = base.x(), base.y()

            left = QPointF(
                bx + direction[0]*arrow_size - px*arrow_size*0.5,
                by + direction[1]*arrow_size - py*arrow_size*0.5
            )

            right = QPointF(
                bx + direction[0]*arrow_size + px*arrow_size*0.5,
                by + direction[1]*arrow_size + py*arrow_size*0.5
            )

            painter.drawLine(base, left)
            painter.drawLine(base, right)
            self._register_dimension_segment(base, left)
            self._register_dimension_segment(base, right)

        # Draw arrows at both ends
        draw_arrow(p1, (ux, uy))
        draw_arrow(p2, (-ux, -uy))

        # Draw length text
        mid = QPointF((p1.x()+p2.x())/2, (p1.y()+p2.y())/2)

#        length_cm = length / PIXELS_PER_CM
#        text = f"{length_cm:.1f} cm"
        length_mm = length / PIXELS_PER_CM * 10
        text = f"{length_mm:.0f} mm"


        self._draw_dimension_label(painter, mid + QPointF(5, -5), text, "horizontal")
    def push_undo(self):
        state = self.serialize()
        if self.undo_stack and self.undo_stack[-1] == state:
            return
        self.undo_stack.append(state)
        if len(self.undo_stack) > 100:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
    def undo(self):

        if not self.undo_stack:
            return

        self.dragging_point = None
        self.drag_type = None
        self.selected_seam_handle = None
        self.selection_box_active = False
        self.selection_box_zoom = False

        current = self.serialize()
        if not self.redo_stack or self.redo_stack[-1] != current:
            self.redo_stack.append(current)

        state = self.undo_stack.pop()

        self.restoring_state = True
        self.deserialize(state)
        self.restoring_state = False

        self.update()
    def redo(self):

        if not self.redo_stack:
            return

        self.dragging_point = None
        self.drag_type = None
        self.selected_seam_handle = None
        self.selection_box_active = False
        self.selection_box_zoom = False

        current = self.serialize()
        if not self.undo_stack or self.undo_stack[-1] != current:
            self.undo_stack.append(current)

        state = self.redo_stack.pop()

        self.restoring_state = True
        self.deserialize(state)
        self.restoring_state = False

        self.update()
    def world_to_screen(self, x, y):
        sx = x*self.view_x_scale + self.view_x_offset
        sy = -y*self.view_y_scale + self.view_y_offset
        return sx, sy
    def move_points(self, x, y):
        sx = x*10+self.view_x_offset2
        sy = -y*10+self.view_y_offset2
        return sx, sy
    def _current_view_scale(self):
        views = []
        try:
            views = self.scene().views()
        except Exception:
            views = []
        if not views:
            return 1.0
        view = views[0]
        try:
            transform = view.transform()
            scale_x = abs(transform.m11())
            if scale_x > 1e-9:
                return scale_x
        except Exception:
            pass
        return 1.0

    def _nice_scale_length_mm(self, target_px=120.0):
        px_per_mm = max(1e-6, PIXELS_PER_MM * self._current_view_scale())
        raw_mm = max(1.0, target_px / px_per_mm)
        exponent = math.floor(math.log10(raw_mm))
        base = 10 ** exponent
        nice_steps = [1, 2, 5, 10]
        chosen = nice_steps[-1] * base
        for step in nice_steps:
            candidate = step * base
            if candidate >= raw_mm:
                chosen = candidate
                break
        return max(1, int(round(chosen)))

    def draw_scale_reference(self, painter, viewport_rect=None):
        if viewport_rect is None:
            viewport_rect = painter.viewport()
        try:
            viewport_rect = QRectF(viewport_rect)
        except Exception:
            viewport_rect = QRectF(painter.viewport())
        if viewport_rect.isEmpty():
            return

        scale_mm = self._nice_scale_length_mm(target_px=130.0)
        current_scale = max(1e-6, self._current_view_scale())
        bar_px = scale_mm * PIXELS_PER_MM * current_scale

        pad = 14
        title_gap = 1
        label_gap = 18
        tick_h_major = 12
        tick_h_minor = 7
        box_w = int(max(220, bar_px + 2 * pad + 10))
        box_h = 50
        margin = 15
        x0 = max(margin, viewport_rect.width()/2 - box_w/2)
        y0 = max(margin, viewport_rect.height() - box_h - margin)

        box = QRectF(x0, y0, box_w, box_h)
        painter.save()
        painter.setPen(QPen(QColor(210, 210, 210), 1))
        painter.setBrush(QBrush(QColor(20, 20, 20, 215)))
        painter.drawRoundedRect(box, 8, 8)

        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setFont(QFont('Arial', 20))
        #painter.drawText(QPointF(x0 + pad, y0 + 16), 'Scale Reference')

        bar_x0 = x0 + pad
        bar_y = y0 + 25
        bar_x1 = bar_x0 + bar_px

        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.drawLine(QPointF(bar_x0, bar_y), QPointF(bar_x1, bar_y))

        major_step_mm = 10 if scale_mm >= 10 else 1
        tick_count = int(scale_mm // major_step_mm)
        for i in range(tick_count + 1):
            x = bar_x0 + i * major_step_mm * PIXELS_PER_MM * current_scale
            painter.drawLine(QPointF(x, bar_y - tick_h_major / 2), QPointF(x, bar_y + tick_h_major / 2))

        if major_step_mm > 1:
            minor_step_mm = max(1, major_step_mm // 2)
            minor_count = int(scale_mm // minor_step_mm)
            for i in range(minor_count + 1):
                if i % 2 == 0:
                    continue
                x = bar_x0 + i * minor_step_mm * PIXELS_PER_MM * current_scale
                if x >= bar_x1 - 0.5:
                    continue
                #painter.drawLine(QPointF(x, bar_y - tick_h_minor / 2), QPointF(x, bar_y + tick_h_minor / 2))

        painter.setFont(QFont('Arial', 18))
        painter.drawText(QPointF(bar_x0, bar_y + label_gap), '0')
        mid_mm = scale_mm / 2.0
        mid_x = bar_x0 + mid_mm * PIXELS_PER_MM * current_scale
        mid_cm = mid_mm / 10.0
        mid_label = f'{mid_cm:.1f} cm' if mid_mm >= 10 else f'{int(round(mid_mm))} mm'
        #painter.drawText(QPointF(mid_x - 18, bar_y + label_gap), mid_label)

        end_cm = scale_mm / 10.0
        end_label = f'{int(scale_mm)} mm'
        painter.drawText(QPointF(max(bar_x0 + 50, bar_x1 - 45), bar_y + label_gap), end_label)

#        painter.setFont(QFont('Arial', 18))
#        zoom_text = f'Zoom: {current_scale:.2f}x'
#        painter.drawText(QPointF(x0 + pad, y0 + box_h - 10), zoom_text)
        painter.restore()

# =========================
# Screen View Overlay
# =========================

class ScaleOverlay(QWidget):
    def __init__(self, view):
        super().__init__(view.viewport())
        self.view = view
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(view.viewport().size())
        self.show()

    def paintEvent(self, event):
        if self.view.ski_item is None:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.ski_item.draw_scale_reference(painter, QRectF(self.rect()))
        painter.end()


# =========================
# Screen View Interactions
# =========================
class SkiView(QGraphicsView):
    def __init__(self,scene):
        super().__init__(scene)
        self.panning = False
        self.pan_start = None
        self.pan_constraint_axis = None
        self.orbiting_3d = False
        self.orbit_start = None
        self.orbit_constraint_axis = None
        self.double_click_guard_ms = 325
        self.double_click_move_threshold_px = 14
        self.last_orbit_release_ms = 0
        self.last_pan_release_ms = 0
        self.last_right_press_ms = 0
        self.last_right_press_pos = None
        self.orbit_sensitivity = 1.0
        self.roll_orbit_sensitivity = 0.85
        self.orbit_yaw_sensitivity = 1.0
        self.orbit_pitch_sensitivity = 1.0
        self.orbit_roll_sensitivity = 0.85
        self.orbit_dominant_axis_bias = 0.88
        self.orbit_invert_horizontal = False
        self.orbit_invert_vertical = False
        self.orbit_swap_drag_axes = False
        self.orbit_enable_roll_gesture = True
        self.orbit_swap_pitch_yaw = False
        self.orbit_swap_pitch_roll = False
        self.orbit_swap_yaw_roll = False
        self.orbit_shift_roll_to_pitch = True
        self.orbit_shift_mode_enabled = True
        self.orbit_shift_horizontal_axis = "pitch"
        self.orbit_shift_vertical_axis = "yaw"
        self.orbit_shift_invert_horizontal = False
        self.orbit_shift_invert_vertical = False
        self.orbit_shift_lock_dominant_axis = True
        self.orbit_gesture_center = None
        self.load_mouse_input_defaults()
        self.orbit_anchor_scene = None
        self.orbit_pivot_model = None
        self.ski_item = None
        self.min_zoom = 0.05
        self.max_zoom = 12.0
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setMouseTracking(True)
        self.scale(0.5, 0.5)   # 50% zoom
        self.dragging_point = None
        self.scale_overlay = None

    def _refresh_scale_overlay(self):
        if not hasattr(self, 'scale_overlay') or self.scale_overlay is None:
            return
        self.scale_overlay.setGeometry(self.viewport().rect())
        self.scale_overlay.raise_()
        self.scale_overlay.update()

    def _current_zoom(self):
        return abs(self.transform().m11())

    def zoom_to_scene_rect(self, scene_rect, extra_scale=1.2):
        if scene_rect is None or scene_rect.isNull() or scene_rect.width() <= 1e-6 or scene_rect.height() <= 1e-6:
            return
        view_rect = self.viewport().rect()
        if view_rect.width() <= 1 or view_rect.height() <= 1:
            return
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
        current_zoom = self._current_zoom()
        target_zoom = max(self.min_zoom, min(self.max_zoom, current_zoom * float(extra_scale)))
        if current_zoom > 1e-9 and target_zoom > 1e-9:
            factor = target_zoom / current_zoom
            self.scale(factor, factor)
        self.centerOn(scene_rect.center())
        self._refresh_scale_overlay()
        self.update()
        viewport = self.viewport()
        if viewport is not None:
            viewport.update()

    def _constrain_delta(self, delta, axis):
        dx = int(round(delta.x()))
        dy = int(round(delta.y()))
        if axis == 'x':
            return dx, 0
        if axis == 'y':
            return 0, dy
        return dx, dy

    def _dominant_axis(self, delta):
        return 'x' if abs(delta.x()) >= abs(delta.y()) else 'y'

    def _mouse_input_defaults_path(self):
        try:
            home = Path.home()
            return home / ".ski_design_mouse_input_defaults.json"
        except Exception:
            return None

    def get_mouse_input_settings(self):
        return {
            "invert_horizontal": bool(self.orbit_invert_horizontal),
            "invert_vertical": bool(self.orbit_invert_vertical),
            "swap_drag_axes": bool(self.orbit_swap_drag_axes),
            "enable_roll_gesture": bool(self.orbit_enable_roll_gesture),
            "swap_pitch_yaw": bool(self.orbit_swap_pitch_yaw),
            "swap_pitch_roll": bool(self.orbit_swap_pitch_roll),
            "swap_yaw_roll": bool(self.orbit_swap_yaw_roll),
            "shift_roll_to_pitch": bool(self.orbit_shift_roll_to_pitch),
            "shift_mode_enabled": bool(self.orbit_shift_mode_enabled),
            "shift_horizontal_axis": str(self.orbit_shift_horizontal_axis),
            "shift_vertical_axis": str(self.orbit_shift_vertical_axis),
            "shift_invert_horizontal": bool(self.orbit_shift_invert_horizontal),
            "shift_invert_vertical": bool(self.orbit_shift_invert_vertical),
            "shift_lock_dominant_axis": bool(self.orbit_shift_lock_dominant_axis),
            "yaw_sensitivity": float(self.orbit_yaw_sensitivity),
            "pitch_sensitivity": float(self.orbit_pitch_sensitivity),
            "roll_sensitivity": float(self.orbit_roll_sensitivity),
            "dominant_axis_bias": float(self.orbit_dominant_axis_bias),
        }

    def apply_mouse_input_settings(self, settings):
        if not isinstance(settings, dict):
            return
        self.orbit_invert_horizontal = bool(settings.get("invert_horizontal", self.orbit_invert_horizontal))
        self.orbit_invert_vertical = bool(settings.get("invert_vertical", self.orbit_invert_vertical))
        self.orbit_swap_drag_axes = bool(settings.get("swap_drag_axes", self.orbit_swap_drag_axes))
        self.orbit_enable_roll_gesture = bool(settings.get("enable_roll_gesture", self.orbit_enable_roll_gesture))
        self.orbit_swap_pitch_yaw = bool(settings.get("swap_pitch_yaw", self.orbit_swap_pitch_yaw))
        self.orbit_swap_pitch_roll = bool(settings.get("swap_pitch_roll", self.orbit_swap_pitch_roll))
        self.orbit_swap_yaw_roll = bool(settings.get("swap_yaw_roll", self.orbit_swap_yaw_roll))
        self.orbit_shift_roll_to_pitch = bool(settings.get("shift_roll_to_pitch", self.orbit_shift_roll_to_pitch))
        self.orbit_shift_mode_enabled = bool(settings.get("shift_mode_enabled", self.orbit_shift_mode_enabled))
        self.orbit_shift_horizontal_axis = str(settings.get("shift_horizontal_axis", self.orbit_shift_horizontal_axis)).lower()
        self.orbit_shift_vertical_axis = str(settings.get("shift_vertical_axis", self.orbit_shift_vertical_axis)).lower()
        if self.orbit_shift_horizontal_axis not in ("pitch", "yaw", "roll", "none"):
            self.orbit_shift_horizontal_axis = "pitch"
        if self.orbit_shift_vertical_axis not in ("pitch", "yaw", "roll", "none"):
            self.orbit_shift_vertical_axis = "yaw"
        self.orbit_shift_invert_horizontal = bool(settings.get("shift_invert_horizontal", self.orbit_shift_invert_horizontal))
        self.orbit_shift_invert_vertical = bool(settings.get("shift_invert_vertical", self.orbit_shift_invert_vertical))
        self.orbit_shift_lock_dominant_axis = bool(settings.get("shift_lock_dominant_axis", self.orbit_shift_lock_dominant_axis))
        self.orbit_yaw_sensitivity = max(0.05, float(settings.get("yaw_sensitivity", self.orbit_yaw_sensitivity)))
        self.orbit_pitch_sensitivity = max(0.05, float(settings.get("pitch_sensitivity", self.orbit_pitch_sensitivity)))
        self.orbit_roll_sensitivity = max(0.0, float(settings.get("roll_sensitivity", self.orbit_roll_sensitivity)))
        self.roll_orbit_sensitivity = self.orbit_roll_sensitivity
        self.orbit_dominant_axis_bias = max(0.0, min(0.98, float(settings.get("dominant_axis_bias", self.orbit_dominant_axis_bias))))

    def save_mouse_input_defaults(self):
        path = self._mouse_input_defaults_path()
        if path is None:
            return False
        try:
            path.write_text(json.dumps(self.get_mouse_input_settings(), indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def load_mouse_input_defaults(self):
        path = self._mouse_input_defaults_path()
        if path is None or not path.exists():
            return False
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
            self.apply_mouse_input_settings(settings)
            return True
        except Exception:
            return False

    def _get_ski_orbit_center_view(self):
        if self.ski_item is None:
            return self.viewport().rect().center()
        try:
            faces = self.ski_item.build_ski_mesh(80)
            xs = []
            ys = []
            zs = []
            for face in faces:
                for vx, vy, vz in face:
                    xs.append(vx)
                    ys.append(vy)
                    zs.append(vz)
            if xs:
                center_scene = self.ski_item.project(
                    (min(xs) + max(xs)) * 0.5,
                    (min(ys) + max(ys)) * 0.5,
                    (min(zs) + max(zs)) * 0.5,
                )
            else:
                center_scene = self.ski_item.project(0.0, 0.0, 0.0)
            return self.mapFromScene(center_scene)
        except Exception:
            try:
                center_scene = self.ski_item.project(0.0, 0.0, 0.0)
                return self.mapFromScene(center_scene)
            except Exception:
                return self.viewport().rect().center()

    def _pick_orbit_pivot_model(self, view_pos):
        if self.ski_item is None:
            return (0.0, 0.0, 0.0)
        scene_pos = self.mapToScene(view_pos)
        try:
            faces = self.ski_item.build_ski_mesh(80)
        except Exception:
            return (0.0, 0.0, 0.0)

        best_inside = None
        best_inside_depth = None
        best_near = None
        best_near_dist2 = None

        for face in faces:
            try:
                rotated = [self.ski_item.rotate_point(v) for v in face]
            except Exception:
                continue
            if not self.ski_item._face_visible(rotated):
                continue

            poly_pts = [self.ski_item.project(v) for v in rotated]
            poly = QPolygonF(poly_pts)
            if len(poly_pts) >= 3 and poly.containsPoint(scene_pos, Qt.FillRule.OddEvenFill):
                cx = sum(v[0] for v in face) / len(face)
                cy = sum(v[1] for v in face) / len(face)
                cz = sum(v[2] for v in face) / len(face)
                depth = sum(v[2] for v in rotated) / len(rotated)
                if best_inside is None or depth > best_inside_depth:
                    best_inside = (cx, cy, cz)
                    best_inside_depth = depth

            for model_v, proj_v in zip(face, poly_pts):
                dx = proj_v.x() - scene_pos.x()
                dy = proj_v.y() - scene_pos.y()
                dist2 = dx * dx + dy * dy
                if best_near is None or dist2 < best_near_dist2:
                    best_near = tuple(model_v)
                    best_near_dist2 = dist2

        if best_inside is not None:
            return best_inside
        if best_near is not None:
            return best_near
        return (0.0, 0.0, 0.0)

    def _update_orbit_anchor_offset(self):
        if self.ski_item is None or self.orbit_pivot_model is None or self.orbit_anchor_scene is None:
            return
        try:
            rotated_pivot = self.ski_item.rotate_point(self.orbit_pivot_model)
            pivot_scene = self.ski_item.project(rotated_pivot)
            delta = self.orbit_anchor_scene - pivot_scene
            self.ski_item.offset_x += delta.x()
            self.ski_item.offset_y += delta.y()
            self.ski_item.update()
        except Exception:
            pass

    def _orbit_roll_delta(self, previous_pos, current_pos):
        # Keep orbit behavior in a stable CAD-style turntable mode by default.
        # Fusion / Creo style RMB orbiting is generally much easier to control
        # when horizontal drags yaw and vertical drags pitch without accidental
        # roll being introduced by circular mouse motion.
        return 0.0

    def _wrap_angle_deg(self, angle_deg):
        while angle_deg > 180.0:
            angle_deg -= 360.0
        while angle_deg < -180.0:
            angle_deg += 360.0
        return angle_deg

    def _clamp_pitch_deg(self, pitch_deg):
        return max(-89.5, min(89.5, pitch_deg))

    def _matrix_multiply3(self, a, b):
        return [
            [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)
        ]

    def _rotation_x_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ]

    def _rotation_y_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ]

    def _rotation_z_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]

    def _current_rotation_matrix(self, owner):
        ski = getattr(owner, "ski", None)
        matrix = getattr(ski, "rotation_matrix", None)
        if matrix and len(matrix) == 3:
            return [[float(matrix[r][c]) for c in range(3)] for r in range(3)]

        pitch = math.radians(owner.rot_x_spin.value())
        yaw = math.radians(owner.rot_y_spin.value())
        roll = math.radians(owner.rot_z_spin.value())
        return self._matrix_multiply3(
            self._rotation_z_matrix(roll),
            self._matrix_multiply3(
                self._rotation_y_matrix(yaw),
                self._rotation_x_matrix(pitch),
            ),
        )

    def _local_delta_rotation_matrix(self, pitch_deg, yaw_deg, roll_deg):
        pitch = math.radians(pitch_deg)
        yaw = math.radians(yaw_deg)
        roll = math.radians(roll_deg)
        return self._matrix_multiply3(
            self._rotation_z_matrix(roll),
            self._matrix_multiply3(
                self._rotation_y_matrix(yaw),
                self._rotation_x_matrix(pitch),
            ),
        )

    def _extract_euler_xyz_deg(self, rotation_matrix):
        r20 = max(-1.0, min(1.0, rotation_matrix[2][0]))
        yaw = math.asin(-r20)

        if abs(abs(r20) - 1.0) < 1e-8:
            pitch = 0.0
            roll = math.atan2(-rotation_matrix[0][1], rotation_matrix[1][1])
        else:
            pitch = math.atan2(rotation_matrix[2][1], rotation_matrix[2][2])
            roll = math.atan2(rotation_matrix[1][0], rotation_matrix[0][0])

        return (
            self._wrap_angle_deg(math.degrees(pitch)),
            self._wrap_angle_deg(math.degrees(yaw)),
            self._wrap_angle_deg(math.degrees(roll)),
        )

    def _apply_rotation_matrix_to_owner(self, owner, rotation_matrix):
        owner.ski.rotation_matrix = [[float(rotation_matrix[r][c]) for c in range(3)] for r in range(3)]

        pitch_deg, yaw_deg, roll_deg = self._extract_euler_xyz_deg(rotation_matrix)

        owner.rot_x_spin.blockSignals(True)
        owner.rot_y_spin.blockSignals(True)
        owner.rot_z_spin.blockSignals(True)
        owner.rot_x_spin.setValue(float(pitch_deg))
        owner.rot_y_spin.setValue(float(yaw_deg))
        owner.rot_z_spin.setValue(float(roll_deg))
        owner.rot_x_spin.blockSignals(False)
        owner.rot_y_spin.blockSignals(False)
        owner.rot_z_spin.blockSignals(False)

        owner.ski.rot_x = math.radians(pitch_deg)
        owner.ski.rot_y = math.radians(yaw_deg)
        owner.ski.rot_z = math.radians(roll_deg)
        owner.ski.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._refresh_scale_overlay()

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)
        self._refresh_scale_overlay()

    def wheelEvent(self,event):
        owner = getattr(self.ski_item, "owner_window", None)
        if owner is not None:
            scene_pos = self.mapToScene(event.position().toPoint())
            if owner.handle_main_window_cnc_3d_wheel(scene_pos, event.angleDelta().y()):
                self._refresh_scale_overlay()
                self.update()
                viewport = self.viewport()
                if viewport is not None:
                    viewport.update()
                    if hasattr(viewport, "repaint"):
                        viewport.repaint()
                event.accept()
                return
        angle = event.angleDelta().y()
        if angle == 0:
            event.ignore()
            return
        zoom = 1.15 if angle > 0 else (1 / 1.15)
        current_zoom = self._current_zoom()
        target_zoom = current_zoom * zoom
        if target_zoom < self.min_zoom:
            zoom = self.min_zoom / max(1e-9, current_zoom)
        elif target_zoom > self.max_zoom:
            zoom = self.max_zoom / max(1e-9, current_zoom)
        anchor_before = self.mapToScene(event.position().toPoint())
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.scale(zoom, zoom)
        anchor_after = self.mapToScene(event.position().toPoint())
        delta_scene = anchor_after - anchor_before
        self.translate(delta_scene.x(), delta_scene.y())
        self._refresh_scale_overlay()
        self.update()
        viewport = self.viewport()
        if viewport is not None:
            viewport.update()
            if hasattr(viewport, "repaint"):
                viewport.repaint()
        event.accept()

    def _can_orbit_3d(self):
        return self.ski_item is not None and getattr(self.ski_item, "show_3d", False)

    def _set_orbit_angles_from_delta(self, previous_pos, current_pos, modifiers=Qt.KeyboardModifier.NoModifier):
        owner = getattr(self.ski_item, "owner_window", None)
        if owner is None:
            return

        delta = current_pos - previous_pos
        view_rect = self.viewport().rect()
        width = max(240, view_rect.width())
        height = max(240, view_rect.height())

        dx = float(delta.x())
        dy = float(delta.y())

        if self.orbit_swap_drag_axes:
            dx, dy = dy, dx
        if self.orbit_invert_horizontal:
            dx = -dx
        if self.orbit_invert_vertical:
            dy = -dy

        abs_dx = abs(dx)
        abs_dy = abs(dy)
        move_mag = abs_dx + abs_dy

        base_yaw = (-dx / width) * 145.0 * self.orbit_sensitivity * self.orbit_yaw_sensitivity
        base_pitch = (dy / height) * 145.0 * self.orbit_sensitivity * self.orbit_pitch_sensitivity

        if move_mag <= 1e-9:
            yaw_weight = 0.0
            pitch_weight = 0.0
        else:
            yaw_weight = 0.20 + 0.80 * (abs_dx / move_mag)
            pitch_weight = 0.20 + 0.80 * (abs_dy / move_mag)

            bias = max(0.0, min(0.98, self.orbit_dominant_axis_bias))
            if abs_dx > abs_dy * 1.8:
                pitch_weight *= (1.0 - bias)
            elif abs_dy > abs_dx * 1.8:
                yaw_weight *= (1.0 - bias)

        yaw_delta = base_yaw * yaw_weight
        pitch_delta = base_pitch * pitch_weight
        roll_delta = 0.0

        center = self.orbit_gesture_center if self.orbit_gesture_center is not None else previous_pos
        prev_vec = previous_pos - center
        curr_vec = current_pos - center
        prev_r = math.hypot(prev_vec.x(), prev_vec.y())
        curr_r = math.hypot(curr_vec.x(), curr_vec.y())

        if self.orbit_enable_roll_gesture and prev_r > 16.0 and curr_r > 16.0 and curr_r < min(width, height) * 0.22:
            prev_ang = math.atan2(prev_vec.y(), prev_vec.x())
            curr_ang = math.atan2(curr_vec.y(), curr_vec.x())
            ang_delta = math.degrees(curr_ang - prev_ang)
            while ang_delta > 180.0:
                ang_delta -= 360.0
            while ang_delta < -180.0:
                ang_delta += 360.0

            tangent_dx = curr_vec.x() - prev_vec.x()
            tangent_dy = curr_vec.y() - prev_vec.y()
            tangential_measure = abs((curr_vec.x() * tangent_dy) - (curr_vec.y() * tangent_dx)) / max(1.0, curr_r)

            circular_intent = tangential_measure > 2.6 and abs(ang_delta) > 1.0
            if circular_intent:
                roll_delta = ang_delta * 0.42 * self.orbit_roll_sensitivity
                yaw_delta *= 0.20
                pitch_delta *= 0.20

        if modifiers & Qt.KeyboardModifier.ShiftModifier and self.orbit_shift_mode_enabled:
            self.orbit_constraint_axis = None

            horiz_value = dx
            vert_value = dy
            if self.orbit_shift_invert_horizontal:
                horiz_value = -horiz_value
            if self.orbit_shift_invert_vertical:
                vert_value = -vert_value

            horiz_amount = (-horiz_value / width) * 145.0 * self.orbit_sensitivity
            vert_amount = (vert_value / height) * 145.0 * self.orbit_sensitivity

            pitch_delta = 0.0
            yaw_delta = 0.0
            roll_delta = 0.0

            axis_sensitivity = {
                "pitch": self.orbit_pitch_sensitivity,
                "yaw": self.orbit_yaw_sensitivity,
                "roll": self.orbit_roll_sensitivity,
                "none": 0.0,
            }

            def add_axis_delta(axis_name, amount):
                nonlocal pitch_delta, yaw_delta, roll_delta
                axis_name = str(axis_name).lower()
                amount *= axis_sensitivity.get(axis_name, 1.0)
                if axis_name == "pitch":
                    pitch_delta += amount
                elif axis_name == "yaw":
                    yaw_delta += amount
                elif axis_name == "roll":
                    roll_delta += amount

            horiz_weight = 0.20 + 0.80 * (abs_dx / max(1e-9, move_mag)) if move_mag > 1e-9 else 0.0
            vert_weight = 0.20 + 0.80 * (abs_dy / max(1e-9, move_mag)) if move_mag > 1e-9 else 0.0

            if self.orbit_shift_lock_dominant_axis:
                if abs_dx > abs_dy * 1.8:
                    horiz_weight = 1.0
                    vert_weight *= 0.05
                elif abs_dy > abs_dx * 1.8:
                    vert_weight = 1.0
                    horiz_weight *= 0.05

            add_axis_delta(self.orbit_shift_horizontal_axis, horiz_amount * horiz_weight)
            add_axis_delta(self.orbit_shift_vertical_axis, vert_amount * vert_weight)
        else:
            self.orbit_constraint_axis = None

        if self.orbit_swap_pitch_yaw:
            pitch_delta, yaw_delta = yaw_delta, pitch_delta
        if self.orbit_swap_pitch_roll:
            pitch_delta, roll_delta = roll_delta, pitch_delta
        if self.orbit_swap_yaw_roll:
            yaw_delta, roll_delta = roll_delta, yaw_delta

        current_rotation = self._current_rotation_matrix(owner)
        local_delta_rotation = self._local_delta_rotation_matrix(pitch_delta, yaw_delta, roll_delta)
        next_rotation = self._matrix_multiply3(current_rotation, local_delta_rotation)
        self._apply_rotation_matrix_to_owner(owner, next_rotation)

    def mousePressEvent(self,event):
        owner = getattr(self.ski_item, "owner_window", None)
        if owner is not None:
            scene_pos = self.mapToScene(event.pos())
            if owner.begin_main_window_cnc_3d_interaction(event.button(), scene_pos, event.pos()):
                if event.button() == Qt.MouseButton.MiddleButton:
                    self.setCursor(Qt.CursorShape.ClosedHandCursor)
                elif event.button() == Qt.MouseButton.LeftButton:
                    self.setCursor(Qt.CursorShape.SizeAllCursor)
                event.accept()
                return
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = True
            self.pan_start = event.pos()
            self.pan_constraint_axis = None
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.RightButton and self._can_orbit_3d():
            if self.ski_item is not None:
                self.ski_item.update_3d_background_center_cache()
            self.last_right_press_ms = int(QDateTime.currentMSecsSinceEpoch())
            self.last_right_press_pos = QPointF(event.pos())
            self.orbiting_3d = True
            self.orbit_start = event.pos()
            self.orbit_gesture_center = event.pos()
            self.orbit_constraint_axis = None
            self.orbit_anchor_scene = self.mapToScene(event.pos())
            self.orbit_pivot_model = self._pick_orbit_pivot_model(event.pos())
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self,event):
        owner = getattr(self.ski_item, "owner_window", None)
        if owner is not None and owner.update_main_window_cnc_3d_interaction(event.pos(), event.modifiers()):
            self._refresh_scale_overlay()
            event.accept()
            return
        if self.panning:
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = True
            raw_delta = event.pos() - self.pan_start
            dx = int(round(raw_delta.x()))
            dy = int(round(raw_delta.y()))
            if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
                if self.pan_constraint_axis is None:
                    self.pan_constraint_axis = self._dominant_axis(raw_delta)
                dx, dy = self._constrain_delta(raw_delta, self.pan_constraint_axis)
            else:
                self.pan_constraint_axis = None
            self.pan_start = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - dx)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - dy)
            self._refresh_scale_overlay()
            event.accept()
            return

        if self.orbiting_3d and self._can_orbit_3d():
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = True
            previous_pos = self.orbit_start
            self.orbit_start = event.pos()
            self._set_orbit_angles_from_delta(previous_pos, self.orbit_start, event.modifiers())
            self._refresh_scale_overlay()
            event.accept()
            return

        super().mouseMoveEvent(event)

        if self.dragging_point is not None:
            self.dragging_point.pos = event.position()
            self.update()

    def mouseReleaseEvent(self,event):
        owner = getattr(self.ski_item, "owner_window", None)
        if owner is not None and owner.finish_main_window_cnc_3d_interaction(event.button()):
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self.panning = False
            self.pan_start = None
            self.pan_constraint_axis = None
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = False
                self.ski_item.update_3d_background_center_cache()
                self.ski_item.update()
            self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.RightButton and self.orbiting_3d:
            self.last_orbit_release_ms = int(QDateTime.currentMSecsSinceEpoch())
            self.orbiting_3d = False
            self.orbit_start = None
            self.orbit_gesture_center = None
            self.orbit_constraint_axis = None
            self.orbit_anchor_scene = None
            self.orbit_pivot_model = None
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = False
                self.ski_item.update_3d_background_center_cache()
                self.ski_item.update()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)
        self.dragging_point = None

    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)

    def drawBackground(self,painter,rect):
        painter.fillRect(rect,QColor(30,30,30))
        pen=QPen(QColor(60,60,60))
        painter.setPen(pen)
        spacing=GRID_SPACING_CM*PIXELS_PER_CM
        left=rect.left()-(rect.left()%spacing)
        top=rect.top()-(rect.top()%spacing)
        x=left
        while x<rect.right():
            painter.drawLine(QPointF(x,rect.top()),
                             QPointF(x,rect.bottom()))
            x+=spacing
        y=top
        while y<rect.bottom():
            painter.drawLine(QPointF(rect.left(),y),
                             QPointF(rect.right(),y))
            y+=spacing

        ski = self.ski_item
        if ski is not None and getattr(ski, "show_3d", False):
            visible_scene_rect = self.mapToScene(self.viewport().rect()).boundingRect()
            zone_rect = ski.get_3d_background_rect(max_width=visible_scene_rect.width())
            if zone_rect.intersects(rect):
                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
                base_color = QColor(getattr(ski, "background_3d_color", QColor(46, 50, 58, 210)))
                top_color = QColor(base_color)
                mid_color = QColor(base_color)
                bottom_color = QColor(base_color)
                top_color.setAlpha(min(255, int(base_color.alpha() * 1.05)))
                mid_color = mid_color.darker(108)
                bottom_color = bottom_color.darker(135)
                panel_gradient = QLinearGradient(zone_rect.topLeft(), zone_rect.bottomLeft())
                panel_gradient.setColorAt(0.0, top_color)
                panel_gradient.setColorAt(0.5, mid_color)
                panel_gradient.setColorAt(1.0, bottom_color)
                edge_color = QColor(base_color.lighter(160))
                edge_color.setAlpha(70)
                painter.setPen(QPen(edge_color, 1.25))
                painter.setBrush(QBrush(panel_gradient))
                painter.drawRoundedRect(zone_rect, 22.0, 22.0)

                glow_center = zone_rect.center()
                glow_radius = max(zone_rect.width(), zone_rect.height()) * 0.48
                glow = QRadialGradient(glow_center, glow_radius)
                glow_base = QColor(base_color.lighter(140))
                glow_base.setAlpha(65)
                glow_mid = QColor(base_color.lighter(118))
                glow_mid.setAlpha(24)
                glow.setColorAt(0.0, glow_base)
                glow.setColorAt(0.42, glow_mid)
                glow.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(glow))
                painter.drawRoundedRect(zone_rect.adjusted(12.0, 12.0, -12.0, -12.0), 20.0, 20.0)
                painter.restore()

        viewport_rect = painter.viewport()
        '''
        margin = 10
        box1_w = 740
        box1_h = 375
        box1_x = -1600
        box1_y = -250
        
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QColor(20, 20, 20, 180))
        painter.drawRoundedRect(QRectF(box1_x, box1_y, box1_w, box1_h),15,15)
        text_rect = QRectF(box1_x + 8, box1_y + 8, box1_w - 16, box1_h - 16)
        painter.setFont(QFont("Kristen ITC",24))

        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
            "Double click mouse adds a point to ski shape\nScroll mouse wheel zooms in/out\nClick mouse wheel and drag:  pan view\nSelect Point:\n   v - vertical lock/unlock(violet)\n   h - horizontal lock/unlock(teal)\n   l - colinear lock/unlock(gray/white) \n   delete - deletes points",          
            )
     '''  
class HelpTextDialog(QDialog):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.resize(640, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2F34;
                color: #EAEAEA;
            }
            QTextEdit {
                background-color: #23272D;
                color: #EAEAEA;
                border: 1px solid #555B63;
                border-radius: 6px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3A3D42;
                border: 1px solid #5B616A;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F2F2F2;
            }
            QPushButton:hover {
                background-color: #4A4E55;
            }
            QPushButton:pressed {
                background-color: #2D3035;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        self.text_box = QTextEdit()
        self.text_box.setReadOnly(True)
        self.text_box.setPlainText(text)
        layout.addWidget(self.text_box)

        self.exit_button = QPushButton("Exit")
        self.exit_button.setMinimumHeight(38)
        self.exit_button.clicked.connect(self.accept)
        layout.addWidget(self.exit_button)


class StartupDialog(QDialog):
    def __init__(self, initial_values, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Super Simple Ski/Snowboard Design")
        self.loaded_file_data = None
        self.loaded_file_path = None
        self.resize(460, 360)
        self.setStyleSheet("""
            QDialog {
                background-color: #2B2F34;
                color: #EAEAEA;
            }
            QLabel {
                color: #EAEAEA;
            }
            QLabel[sectionTitle="true"] {
                color: #F2F2F2;
                font-size: 16px;
                font-weight: bold;
                padding-top: 4px;
                padding-bottom: 4px;
            }
            QPushButton {
                background-color: #3A3D42;
                border: 1px solid #5B616A;
                border-radius: 6px;
                padding: 8px 12px;
                color: #F2F2F2;
            }
            QPushButton:hover {
                background-color: #4A4E55;
            }
            QPushButton:pressed {
                background-color: #2D3035;
            }
            QComboBox, QDoubleSpinBox {
                background-color: #2E3238;
                color: #EAEAEA;
                border: 1px solid #555B63;
                border-radius: 4px;
                padding: 6px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2E3238;
                color: #EAEAEA;
                border: 1px solid #555B63;
                selection-background-color: #4A4E55;
            }
            QDialogButtonBox QPushButton {
                min-width: 120px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title_label2 = QLabel("Load Design")
        title_label2.setStyleSheet("font-family: Kristen ITC; font-size: 24px; font-weight: bold;")
        title_label2.setProperty("sectionTitle", True)
        title_label2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label2)
        self.load_file_button = QPushButton("Load File")
        startup_button_height = 40
        self.load_file_button.setFixedHeight(startup_button_height)
        self.load_file_button.clicked.connect(self.load_startup_file)
        layout.addWidget(self.load_file_button)
        layout.addSpacing(18)


        title_label = QLabel("Start from Template")
        title_label.setStyleSheet("font-family: Kristen ITC; font-size: 24px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        form.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(10)
        layout.addLayout(form)
        self.ski_type_combo = QComboBox()
        self.ski_type_combo.setMinimumWidth(260)
        self.ski_type_combo.addItems([
            "All Mountain Ski",
            "Park Ski",
            "Carving Ski",
            "Powder Ski",
            "Powder Board",
            "Caving Board",
        ])
        form.addRow("Board Type:", self.ski_type_combo)

        self.overall_length_spin = QDoubleSpinBox()
        self.overall_length_spin.setRange(50.0, 400.0)
        self.overall_length_spin.setDecimals(1)
        self.overall_length_spin.setSingleStep(1.0)
        self.overall_length_spin.setValue(float(initial_values.get("overall_length_cm", 175.0)))
        form.addRow("Overall Length (cm)", self.overall_length_spin)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(10)

        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        for btn in (ok_button, cancel_button):
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setFixedHeight(startup_button_height)
            footer_layout.addWidget(btn)

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        layout.addLayout(footer_layout)
    def load_startup_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Ski Design",
            "",
            "Ski Design (*.ski)"
        )
        if not filename:
            return
        try:
            with open(filename, "r") as f:
                data = json.load(f)
        except Exception as exc:
            QMessageBox.warning(self, "Load Failed", f"Could not load ski file.\n\n{exc}")
            return

        self.loaded_file_data = data
        self.loaded_file_path = filename
        self.accept()
    def values(self):
        values = {
            "ski_type": self.ski_type_combo.currentText(),
            "overall_length_cm": self.overall_length_spin.value(),
        }
        if self.loaded_file_data is not None:
            values["loaded_file_data"] = self.loaded_file_data
            values["loaded_file_path"] = self.loaded_file_path
        return values


class MouseInputSettingsDialog(QDialog):
    def __init__(self, view, parent=None):
        super().__init__(parent)
        self.view = view
        self.setWindowTitle("3D Ski/Board Mouse Input Settings")
        self.resize(460, 420)

        layout = QVBoxLayout(self)

        info = QLabel(
            "Adjust how right-click 3D orbit responds. Changes apply live.\n"
            "Use these controls to flip axes, remap pitch/yaw/roll, and tune sensitivity."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.invert_horizontal_check = QCheckBox("Swap left/right behavior")
        self.invert_vertical_check = QCheckBox("Swap up/down behavior")
        self.swap_axes_check = QCheckBox("Swap left/right with up/down")
        self.enable_roll_check = QCheckBox("Enable circular-gesture roll")
        self.swap_pitch_yaw_check = QCheckBox("Swap pitch and yaw")
        self.swap_pitch_roll_check = QCheckBox("Swap pitch and roll")
        self.swap_yaw_roll_check = QCheckBox("Swap yaw and roll")
        self.shift_roll_to_pitch_check = QCheckBox("Shift mode remaps left/right into pitch")
        self.shift_mode_enabled_check = QCheckBox("Enable special Shift remap mode")
        self.shift_invert_horizontal_check = QCheckBox("Shift: invert left/right")
        self.shift_invert_vertical_check = QCheckBox("Shift: invert up/down")
        self.shift_lock_dominant_axis_check = QCheckBox("Shift: strongly lock to dominant mouse axis")

        layout.addWidget(self.invert_horizontal_check)
        layout.addWidget(self.invert_vertical_check)
        layout.addWidget(self.swap_axes_check)
        layout.addWidget(self.enable_roll_check)
        layout.addWidget(self.swap_pitch_yaw_check)
        layout.addWidget(self.swap_pitch_roll_check)
        layout.addWidget(self.swap_yaw_roll_check)
        layout.addWidget(self.shift_roll_to_pitch_check)
        layout.addWidget(self.shift_mode_enabled_check)
        layout.addWidget(self.shift_invert_horizontal_check)
        layout.addWidget(self.shift_invert_vertical_check)
        layout.addWidget(self.shift_lock_dominant_axis_check)

        shift_group = QGroupBox("Shift remap")
        shift_layout = QGridLayout(shift_group)
        self.shift_horizontal_axis_combo = QComboBox()
        self.shift_vertical_axis_combo = QComboBox()
        for combo in (self.shift_horizontal_axis_combo, self.shift_vertical_axis_combo):
            combo.addItems(["Pitch", "Yaw", "Roll", "None"])
        shift_layout.addWidget(QLabel("Shift + left/right controls"), 0, 0)
        shift_layout.addWidget(self.shift_horizontal_axis_combo, 0, 1)
        shift_layout.addWidget(QLabel("Shift + up/down controls"), 1, 0)
        shift_layout.addWidget(self.shift_vertical_axis_combo, 1, 1)
        layout.addWidget(shift_group)

        form = QGridLayout()
        layout.addLayout(form)

        self.yaw_slider = QSlider(Qt.Orientation.Horizontal)
        self.pitch_slider = QSlider(Qt.Orientation.Horizontal)
        self.roll_slider = QSlider(Qt.Orientation.Horizontal)
        self.bias_slider = QSlider(Qt.Orientation.Horizontal)
        self.double_click_guard_slider = QSlider(Qt.Orientation.Horizontal)
        self.double_click_move_slider = QSlider(Qt.Orientation.Horizontal)

        self.yaw_value = QLabel()
        self.pitch_value = QLabel()
        self.roll_value = QLabel()
        self.bias_value = QLabel()

        for slider in (self.yaw_slider, self.pitch_slider, self.roll_slider):
            slider.setRange(5, 300)
        self.bias_slider.setRange(0, 98)
        self.double_click_guard_slider.setRange(0, 1000)
        self.double_click_move_slider.setRange(0, 40)

        form.addWidget(QLabel("Yaw sensitivity"), 0, 0)
        form.addWidget(self.yaw_slider, 0, 1)
        form.addWidget(self.yaw_value, 0, 2)

        form.addWidget(QLabel("Pitch sensitivity"), 1, 0)
        form.addWidget(self.pitch_slider, 1, 1)
        form.addWidget(self.pitch_value, 1, 2)

        form.addWidget(QLabel("Roll sensitivity"), 2, 0)
        form.addWidget(self.roll_slider, 2, 1)
        form.addWidget(self.roll_value, 2, 2)

        form.addWidget(QLabel("Dominant-axis bias"), 3, 0)
        form.addWidget(self.bias_slider, 3, 1)
        form.addWidget(self.bias_value, 3, 2)

        form.addWidget(QLabel("Double-click guard"), 4, 0)
        form.addWidget(self.double_click_guard_slider, 4, 1)
        self.double_click_guard_value = QLabel()
        form.addWidget(self.double_click_guard_value, 4, 2)

        form.addWidget(QLabel("Double-click move filter"), 5, 0)
        form.addWidget(self.double_click_move_slider, 5, 1)
        self.double_click_move_value = QLabel()
        form.addWidget(self.double_click_move_value, 5, 2)

        button_row = QHBoxLayout()
        layout.addLayout(button_row)
        self.reset_button = QPushButton("Reset Defaults")
        self.save_default_button = QPushButton("Save As Default")
        self.close_button = QPushButton("Close")
        button_row.addWidget(self.reset_button)
        button_row.addWidget(self.save_default_button)
        button_row.addStretch(1)
        button_row.addWidget(self.close_button)

        self.close_button.clicked.connect(self.accept)
        self.reset_button.clicked.connect(self.reset_defaults)
        self.save_default_button.clicked.connect(self.save_as_default)

        for widget in (
            self.invert_horizontal_check,
            self.invert_vertical_check,
            self.swap_axes_check,
            self.enable_roll_check,
            self.swap_pitch_yaw_check,
            self.swap_pitch_roll_check,
            self.swap_yaw_roll_check,
            self.shift_roll_to_pitch_check,
            self.shift_mode_enabled_check,
            self.shift_invert_horizontal_check,
            self.shift_invert_vertical_check,
            self.shift_lock_dominant_axis_check,
        ):
            widget.toggled.connect(self.apply_to_view)

        self.shift_horizontal_axis_combo.currentIndexChanged.connect(self.apply_to_view)
        self.shift_vertical_axis_combo.currentIndexChanged.connect(self.apply_to_view)

        for slider in (
            self.yaw_slider,
            self.pitch_slider,
            self.roll_slider,
            self.bias_slider,
            self.double_click_guard_slider,
            self.double_click_move_slider,
        ):
            slider.valueChanged.connect(self.apply_to_view)

        self.sync_from_view()

    def sync_from_view(self):
        s = self.view.get_mouse_input_settings()
        self.invert_horizontal_check.setChecked(bool(s["invert_horizontal"]))
        self.invert_vertical_check.setChecked(bool(s["invert_vertical"]))
        self.swap_axes_check.setChecked(bool(s["swap_drag_axes"]))
        self.enable_roll_check.setChecked(bool(s["enable_roll_gesture"]))
        self.swap_pitch_yaw_check.setChecked(bool(s["swap_pitch_yaw"]))
        self.swap_pitch_roll_check.setChecked(bool(s["swap_pitch_roll"]))
        self.swap_yaw_roll_check.setChecked(bool(s["swap_yaw_roll"]))
        self.shift_roll_to_pitch_check.setChecked(bool(s["shift_roll_to_pitch"]))
        self.shift_mode_enabled_check.setChecked(bool(s["shift_mode_enabled"]))
        self.shift_invert_horizontal_check.setChecked(bool(s["shift_invert_horizontal"]))
        self.shift_invert_vertical_check.setChecked(bool(s["shift_invert_vertical"]))
        self.shift_lock_dominant_axis_check.setChecked(bool(s["shift_lock_dominant_axis"]))
        self.shift_horizontal_axis_combo.setCurrentText(str(s["shift_horizontal_axis"]).capitalize())
        self.shift_vertical_axis_combo.setCurrentText(str(s["shift_vertical_axis"]).capitalize())
        self.yaw_slider.setValue(int(round(float(s["yaw_sensitivity"]) * 100.0)))
        self.pitch_slider.setValue(int(round(float(s["pitch_sensitivity"]) * 100.0)))
        self.roll_slider.setValue(int(round(float(s["roll_sensitivity"]) * 100.0)))
        self.bias_slider.setValue(int(round(float(s["dominant_axis_bias"]) * 100.0)))
        self.double_click_guard_slider.setValue(int(round(float(getattr(self.view, "double_click_guard_ms", 325)))))
        self.double_click_move_slider.setValue(int(round(float(getattr(self.view, "double_click_move_threshold_px", 14)))))
        self.refresh_labels()

    def refresh_labels(self):
        self.yaw_value.setText(f"{self.yaw_slider.value() / 100.0:.2f}x")
        self.pitch_value.setText(f"{self.pitch_slider.value() / 100.0:.2f}x")
        self.roll_value.setText(f"{self.roll_slider.value() / 100.0:.2f}x")
        self.bias_value.setText(f"{self.bias_slider.value()}%")
        self.double_click_guard_value.setText(f"{self.double_click_guard_slider.value()} ms")
        self.double_click_move_value.setText(f"{self.double_click_move_slider.value()} px")

    def apply_to_view(self):
        self.refresh_labels()
        self.view.apply_mouse_input_settings({
            "invert_horizontal": self.invert_horizontal_check.isChecked(),
            "invert_vertical": self.invert_vertical_check.isChecked(),
            "swap_drag_axes": self.swap_axes_check.isChecked(),
            "enable_roll_gesture": self.enable_roll_check.isChecked(),
            "swap_pitch_yaw": self.swap_pitch_yaw_check.isChecked(),
            "swap_pitch_roll": self.swap_pitch_roll_check.isChecked(),
            "swap_yaw_roll": self.swap_yaw_roll_check.isChecked(),
            "shift_roll_to_pitch": self.shift_roll_to_pitch_check.isChecked(),
            "shift_mode_enabled": self.shift_mode_enabled_check.isChecked(),
            "shift_horizontal_axis": self.shift_horizontal_axis_combo.currentText().lower(),
            "shift_vertical_axis": self.shift_vertical_axis_combo.currentText().lower(),
            "shift_invert_horizontal": self.shift_invert_horizontal_check.isChecked(),
            "shift_invert_vertical": self.shift_invert_vertical_check.isChecked(),
            "shift_lock_dominant_axis": self.shift_lock_dominant_axis_check.isChecked(),
            "yaw_sensitivity": self.yaw_slider.value() / 100.0,
            "pitch_sensitivity": self.pitch_slider.value() / 100.0,
            "roll_sensitivity": self.roll_slider.value() / 100.0,
            "dominant_axis_bias": self.bias_slider.value() / 100.0,
        })
        self.view.double_click_guard_ms = int(self.double_click_guard_slider.value())
        self.view.double_click_move_threshold_px = int(self.double_click_move_slider.value())

    def reset_defaults(self):
        self.view.apply_mouse_input_settings({
            "invert_horizontal": False,
            "invert_vertical": False,
            "swap_drag_axes": False,
            "enable_roll_gesture": True,
            "swap_pitch_yaw": False,
            "swap_pitch_roll": False,
            "swap_yaw_roll": False,
            "shift_roll_to_pitch": True,
            "shift_mode_enabled": True,
            "shift_horizontal_axis": "pitch",
            "shift_vertical_axis": "yaw",
            "shift_invert_horizontal": False,
            "shift_invert_vertical": False,
            "shift_lock_dominant_axis": True,
            "yaw_sensitivity": 1.0,
            "pitch_sensitivity": 1.0,
            "roll_sensitivity": 0.85,
            "dominant_axis_bias": 0.88,
        })
        self.view.double_click_guard_ms = 325
        self.view.double_click_move_threshold_px = 14
        self.sync_from_view()

    def save_as_default(self):
        self.apply_to_view()
        ok = self.view.save_mouse_input_defaults()
        QMessageBox.information(
            self,
            "3D Ski/Board Mouse Input Settings",
            "Saved current mouse input settings as the default."
            if ok else
            "Could not save the default mouse input settings."
        )


class CollapsiblePanel(QFrame):
    def __init__(self, title, content_widget, parent=None, expanded=True):
        super().__init__(parent)
        self.content_widget = content_widget
        self.toggle_button = QToolButton()
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(expanded)
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.content_widget)

        self.content_widget.setVisible(expanded)
        self.toggle_button.toggled.connect(self._set_expanded)
        self.setObjectName("collapsiblePanel")
        self.toggle_button.setObjectName("collapsiblePanelToggle")

    def _set_expanded(self, expanded):
        self.content_widget.setVisible(expanded)
        self.toggle_button.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)



class CNCToolpath3DView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._segment_groups = []
        self._workspace_size = (300.0, 2000.0, 150.0)
        self._workspace_origin = (0.0, 0.0, 0.0)
        self._show_workspace_boundary = True
        self._start_point = (0.0, 0.0, 10.0)
        self._entry_point = None
        self._preview_offset_xy = (0.0, 0.0)
        self.rot_x = -62.0
        self.rot_y = -18.0
        self.rot_z = 132.0
        self.rotation_matrix = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._orbiting = False
        self._panning = False
        self._last_mouse_pos = None
        self.double_click_guard_ms = 325
        self.double_click_move_threshold_px = 14
        self.orbit_sensitivity = 1.0
        self.orbit_yaw_sensitivity = 1.0
        self.orbit_pitch_sensitivity = 1.0
        self.orbit_roll_sensitivity = 0.85
        self.orbit_dominant_axis_bias = 0.88
        self.orbit_invert_horizontal = False
        self.orbit_invert_vertical = False
        self.orbit_swap_drag_axes = False
        self.orbit_enable_roll_gesture = True
        self.orbit_swap_pitch_yaw = False
        self.orbit_swap_pitch_roll = False
        self.orbit_swap_yaw_roll = False
        self.orbit_shift_roll_to_pitch = True
        self.orbit_shift_mode_enabled = True
        self.orbit_shift_horizontal_axis = "pitch"
        self.orbit_shift_vertical_axis = "yaw"
        self.orbit_shift_invert_horizontal = False
        self.orbit_shift_invert_vertical = False
        self.orbit_shift_lock_dominant_axis = True
        self.load_mouse_input_defaults()
        self.setMinimumHeight(240)
        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._interaction_active = False
        self._cached_geometry_key = None
        self._cached_scene_points = []
        self._cached_projected = None
        self._cached_projected_key = None
        self._cached_draw_data_full = None
        self._cached_draw_data_interaction = None

    def _mouse_input_defaults_path(self):
        try:
            home = Path.home()
            return home / ".ski_design_cnc_preview_mouse_input_defaults.json"
        except Exception:
            return None

    def get_mouse_input_settings(self):
        return {
            "invert_horizontal": bool(self.orbit_invert_horizontal),
            "invert_vertical": bool(self.orbit_invert_vertical),
            "swap_drag_axes": bool(self.orbit_swap_drag_axes),
            "enable_roll_gesture": bool(self.orbit_enable_roll_gesture),
            "swap_pitch_yaw": bool(self.orbit_swap_pitch_yaw),
            "swap_pitch_roll": bool(self.orbit_swap_pitch_roll),
            "swap_yaw_roll": bool(self.orbit_swap_yaw_roll),
            "shift_roll_to_pitch": bool(self.orbit_shift_roll_to_pitch),
            "shift_mode_enabled": bool(self.orbit_shift_mode_enabled),
            "shift_horizontal_axis": str(self.orbit_shift_horizontal_axis),
            "shift_vertical_axis": str(self.orbit_shift_vertical_axis),
            "shift_invert_horizontal": bool(self.orbit_shift_invert_horizontal),
            "shift_invert_vertical": bool(self.orbit_shift_invert_vertical),
            "shift_lock_dominant_axis": bool(self.orbit_shift_lock_dominant_axis),
            "yaw_sensitivity": float(self.orbit_yaw_sensitivity),
            "pitch_sensitivity": float(self.orbit_pitch_sensitivity),
            "roll_sensitivity": float(self.orbit_roll_sensitivity),
            "dominant_axis_bias": float(self.orbit_dominant_axis_bias),
        }

    def apply_mouse_input_settings(self, settings):
        if not isinstance(settings, dict):
            return
        self.orbit_invert_horizontal = bool(settings.get("invert_horizontal", self.orbit_invert_horizontal))
        self.orbit_invert_vertical = bool(settings.get("invert_vertical", self.orbit_invert_vertical))
        self.orbit_swap_drag_axes = bool(settings.get("swap_drag_axes", self.orbit_swap_drag_axes))
        self.orbit_enable_roll_gesture = bool(settings.get("enable_roll_gesture", self.orbit_enable_roll_gesture))
        self.orbit_swap_pitch_yaw = bool(settings.get("swap_pitch_yaw", self.orbit_swap_pitch_yaw))
        self.orbit_swap_pitch_roll = bool(settings.get("swap_pitch_roll", self.orbit_swap_pitch_roll))
        self.orbit_swap_yaw_roll = bool(settings.get("swap_yaw_roll", self.orbit_swap_yaw_roll))
        self.orbit_shift_roll_to_pitch = bool(settings.get("shift_roll_to_pitch", self.orbit_shift_roll_to_pitch))
        self.orbit_shift_mode_enabled = bool(settings.get("shift_mode_enabled", self.orbit_shift_mode_enabled))
        self.orbit_shift_horizontal_axis = str(settings.get("shift_horizontal_axis", self.orbit_shift_horizontal_axis)).lower()
        self.orbit_shift_vertical_axis = str(settings.get("shift_vertical_axis", self.orbit_shift_vertical_axis)).lower()
        if self.orbit_shift_horizontal_axis not in ("pitch", "yaw", "roll", "none"):
            self.orbit_shift_horizontal_axis = "pitch"
        if self.orbit_shift_vertical_axis not in ("pitch", "yaw", "roll", "none"):
            self.orbit_shift_vertical_axis = "yaw"
        self.orbit_shift_invert_horizontal = bool(settings.get("shift_invert_horizontal", self.orbit_shift_invert_horizontal))
        self.orbit_shift_invert_vertical = bool(settings.get("shift_invert_vertical", self.orbit_shift_invert_vertical))
        self.orbit_shift_lock_dominant_axis = bool(settings.get("shift_lock_dominant_axis", self.orbit_shift_lock_dominant_axis))
        self.orbit_yaw_sensitivity = max(0.05, float(settings.get("yaw_sensitivity", self.orbit_yaw_sensitivity)))
        self.orbit_pitch_sensitivity = max(0.05, float(settings.get("pitch_sensitivity", self.orbit_pitch_sensitivity)))
        self.orbit_roll_sensitivity = max(0.0, float(settings.get("roll_sensitivity", self.orbit_roll_sensitivity)))
        self.orbit_dominant_axis_bias = max(0.0, min(0.98, float(settings.get("dominant_axis_bias", self.orbit_dominant_axis_bias))))
        self.update()

    def save_mouse_input_defaults(self):
        path = self._mouse_input_defaults_path()
        if path is None:
            return False
        payload = dict(self.get_mouse_input_settings())
        payload["double_click_guard_ms"] = int(self.double_click_guard_ms)
        payload["double_click_move_threshold_px"] = int(self.double_click_move_threshold_px)
        try:
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def load_mouse_input_defaults(self):
        path = self._mouse_input_defaults_path()
        if path is None or not path.exists():
            return False
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False
        self.apply_mouse_input_settings(settings)
        self.double_click_guard_ms = int(round(float(settings.get("double_click_guard_ms", self.double_click_guard_ms))))
        self.double_click_move_threshold_px = int(round(float(settings.get("double_click_move_threshold_px", self.double_click_move_threshold_px))))
        return True

    def _mouse_input_source_view(self):
        return self

    def set_preview_data(self, segment_groups, workspace_size=None, start_point=None, entry_point=None, preview_offset_xy=None, workspace_origin=None, show_workspace_boundary=None):
        self._segment_groups = list(segment_groups or [])
        if workspace_size is not None and len(workspace_size) == 3:
            self._workspace_size = tuple(max(1.0, float(v)) for v in workspace_size)
        if workspace_origin is not None and len(workspace_origin) == 3:
            self._workspace_origin = tuple(float(v) for v in workspace_origin)
        if show_workspace_boundary is not None:
            self._show_workspace_boundary = bool(show_workspace_boundary)
        if start_point is not None and len(start_point) == 3:
            self._start_point = tuple(float(v) for v in start_point)
        self._entry_point = tuple(float(v) for v in entry_point) if entry_point is not None else None
        if preview_offset_xy is not None and len(preview_offset_xy) == 2:
            self._preview_offset_xy = (float(preview_offset_xy[0]), float(preview_offset_xy[1]))
        self._invalidate_geometry_cache()
        self.update()

    def _invalidate_geometry_cache(self):
        self._cached_geometry_key = None
        self._cached_scene_points = []
        self._cached_draw_data_full = None
        self._cached_draw_data_interaction = None
        self._invalidate_projection_cache()

    def _invalidate_projection_cache(self):
        self._cached_projected = None
        self._cached_projected_key = None

    def _preview_geometry_key(self):
        rounded_groups = []
        for group in self._segment_groups:
            segs = []
            for seg in group.get('segments', []):
                start_pt, end_pt, seg_type = seg[:3]
                feed_value = seg[3] if len(seg) > 3 else None
                segs.append((
                    tuple(round(float(v), 4) for v in start_pt),
                    tuple(round(float(v), 4) for v in end_pt),
                    str(seg_type),
                    None if feed_value is None else round(float(feed_value), 4),
                ))
            rounded_groups.append(tuple(segs))
        return (
            tuple(rounded_groups),
            tuple(round(float(v), 4) for v in self._workspace_size),
            tuple(round(float(v), 4) for v in self._workspace_origin),
            bool(self._show_workspace_boundary),
            tuple(round(float(v), 4) for v in self._start_point),
            None if self._entry_point is None else tuple(round(float(v), 4) for v in self._entry_point),
            tuple(round(float(v), 4) for v in self._preview_offset_xy),
        )

    def _ensure_geometry_cache(self):
        key = self._preview_geometry_key()
        if key == self._cached_geometry_key and self._cached_draw_data_full is not None:
            return
        scene_points = list(self._workspace_points())
        segment_ranges_full = []
        segment_ranges_interaction = []
        idx = len(scene_points)
        for group in self._segment_groups:
            segments = list(group.get('segments', []))
            start_idx = idx
            for seg in segments:
                scene_points.extend([seg[0], seg[1]])
                idx += 2
            segment_ranges_full.append((segments, start_idx))
            if len(segments) <= 120:
                light_segments = segments
            else:
                step = max(2, int(math.ceil(len(segments) / 120.0)))
                light_segments = segments[::step]
                if segments and light_segments[-1] is not segments[-1]:
                    light_segments = light_segments + [segments[-1]]
            interaction_start = idx
            for seg in light_segments:
                scene_points.extend([seg[0], seg[1]])
                idx += 2
            segment_ranges_interaction.append((light_segments, interaction_start))
        start_idx = idx
        scene_points.append(self._start_point)
        idx += 1
        entry_idx = None
        if self._entry_point is not None:
            entry_idx = idx
            scene_points.append(self._entry_point)
        workspace_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        self._cached_scene_points = scene_points
        self._cached_draw_data_full = {
            'workspace_edges': workspace_edges,
            'segment_ranges': segment_ranges_full,
            'start_idx': start_idx,
            'entry_idx': entry_idx,
        }
        self._cached_draw_data_interaction = {
            'workspace_edges': workspace_edges,
            'segment_ranges': segment_ranges_interaction,
            'start_idx': start_idx,
            'entry_idx': entry_idx,
        }
        self._cached_geometry_key = key
        self._invalidate_projection_cache()

    def _project_cached_points(self, rect):
        self._ensure_geometry_cache()
        matrix = getattr(self, 'rotation_matrix', None)
        if not matrix or len(matrix) != 3:
            matrix = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
            self.rotation_matrix = matrix
        flat_matrix = tuple(round(float(v), 6) for row in matrix for v in row)
        cache_key = (
            self._cached_geometry_key,
            round(float(rect.left()), 3), round(float(rect.top()), 3), round(float(rect.width()), 3), round(float(rect.height()), 3),
            flat_matrix,
            round(float(self.zoom), 6), round(float(self.pan_x), 3), round(float(self.pan_y), 3),
        )
        if cache_key == self._cached_projected_key and self._cached_projected is not None:
            return self._cached_projected
        projected, scale = self._project_points(self._cached_scene_points, rect)
        self._cached_projected = (projected, scale)
        self._cached_projected_key = cache_key
        return projected, scale

    def reset_view(self):
        self.rot_x = -62.0
        self.rot_y = -18.0
        self.rot_z = 132.0
        self.rotation_matrix = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
        self.zoom = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self._invalidate_projection_cache()
        self.update()

    def _preview_viewport_rect(self):
        outer_rect = self.rect().adjusted(8, 8, -8, -8)
        return outer_rect.adjusted(10, 38, -10, -12)

    def _toolpath_points(self):
        points = []
        for group in self._segment_groups or []:
            for seg in group.get('segments', []):
                if len(seg) >= 2:
                    points.extend([seg[0], seg[1]])
        return points

    def _rotated_bounds_for_points(self, points):
        rotated = [self._rotate_point(pt) for pt in points or []]
        if not rotated:
            return None
        xs = [pt[0] for pt in rotated]
        ys = [pt[1] for pt in rotated]
        return (min(xs), min(ys), max(xs), max(ys))

    def _center_toolpath_in_view(self):
        self._ensure_geometry_cache()
        toolpath_bounds = self._rotated_bounds_for_points(self._toolpath_points())
        scene_bounds = self._rotated_bounds_for_points(self._cached_scene_points)
        if toolpath_bounds is None or scene_bounds is None:
            self.pan_x = 0.0
            self.pan_y = 0.0
            return False
        tool_cx = (toolpath_bounds[0] + toolpath_bounds[2]) * 0.5
        tool_cy = (toolpath_bounds[1] + toolpath_bounds[3]) * 0.5
        scene_cx = (scene_bounds[0] + scene_bounds[2]) * 0.5
        scene_cy = (scene_bounds[1] + scene_bounds[3]) * 0.5
        self.pan_x = -(tool_cx - scene_cx) * float(self.zoom)
        self.pan_y = (tool_cy - scene_cy) * float(self.zoom)
        return True

    def center_toolpath_in_view(self):
        centered = self._center_toolpath_in_view()
        self._invalidate_projection_cache()
        self.update()
        return centered

    def fit_toolpath_to_view(self, fill_ratio=0.90, viewport_rect=None):
        viewport_rect = viewport_rect if viewport_rect is not None else self._preview_viewport_rect()
        if viewport_rect.width() <= 1.0 or viewport_rect.height() <= 1.0:
            return False
        toolpath_bounds = self._rotated_bounds_for_points(self._toolpath_points())
        if toolpath_bounds is None:
            return False
        span_x = max(1e-6, toolpath_bounds[2] - toolpath_bounds[0])
        span_y = max(1e-6, toolpath_bounds[3] - toolpath_bounds[1])
        target_zoom = min(
            (float(viewport_rect.width()) * float(fill_ratio)) / span_x,
            (float(viewport_rect.height()) * float(fill_ratio)) / span_y,
        )
        self.zoom = max(0.01, min(250.0, target_zoom))
        self._center_toolpath_in_view()
        self._invalidate_projection_cache()
        self.update()
        return True

    def set_view_angles(self, pitch_deg, yaw_deg, roll_deg):
        self.rot_x = float(pitch_deg)
        self.rot_y = float(yaw_deg)
        self.rot_z = float(roll_deg)
        self.rotation_matrix = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
        self._invalidate_projection_cache()
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta:
            factor = 1.12 if delta > 0 else 1.0 / 1.12
            self.zoom = max(0.15, min(25.0, self.zoom * factor))
            self._invalidate_projection_cache()
            self.update()
            if hasattr(self, "repaint"):
                self.repaint()
            parent = self.parentWidget()
            if parent is not None:
                parent.update()
                if hasattr(parent, "repaint"):
                    parent.repaint()
            event.accept()
            return
        super().wheelEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.reset_view()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def _matrix_multiply3(self, a, b):
        return [
            [sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)]
            for i in range(3)
        ]

    def _rotation_x_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [1.0, 0.0, 0.0],
            [0.0, c, -s],
            [0.0, s, c],
        ]

    def _rotation_y_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, 0.0, s],
            [0.0, 1.0, 0.0],
            [-s, 0.0, c],
        ]

    def _rotation_z_matrix(self, angle_rad):
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        return [
            [c, -s, 0.0],
            [s, c, 0.0],
            [0.0, 0.0, 1.0],
        ]

    def _rotation_matrix_from_euler_deg(self, pitch_deg, yaw_deg, roll_deg):
        pitch = math.radians(float(pitch_deg))
        yaw = math.radians(float(yaw_deg))
        roll = math.radians(float(roll_deg))
        return self._matrix_multiply3(
            self._rotation_z_matrix(roll),
            self._matrix_multiply3(
                self._rotation_y_matrix(yaw),
                self._rotation_x_matrix(pitch),
            ),
        )

    def _extract_euler_xyz_deg(self, rotation_matrix):
        r20 = max(-1.0, min(1.0, rotation_matrix[2][0]))
        yaw = math.asin(-r20)
        if abs(abs(r20) - 1.0) < 1e-8:
            pitch = 0.0
            roll = math.atan2(-rotation_matrix[0][1], rotation_matrix[1][1])
        else:
            pitch = math.atan2(rotation_matrix[2][1], rotation_matrix[2][2])
            roll = math.atan2(rotation_matrix[1][0], rotation_matrix[0][0])
        def wrap(angle_deg):
            while angle_deg > 180.0:
                angle_deg -= 360.0
            while angle_deg < -180.0:
                angle_deg += 360.0
            return angle_deg
        return (wrap(math.degrees(pitch)), wrap(math.degrees(yaw)), wrap(math.degrees(roll)))

    def _apply_rotation_matrix(self, rotation_matrix):
        self.rotation_matrix = [[float(rotation_matrix[r][c]) for c in range(3)] for r in range(3)]
        self.rot_x, self.rot_y, self.rot_z = self._extract_euler_xyz_deg(self.rotation_matrix)

    def _set_orbit_angles_from_delta(self, previous_pos, current_pos, modifiers=Qt.KeyboardModifier.NoModifier):
        source_view = self._mouse_input_source_view()
        delta = current_pos - previous_pos
        view_rect = self.rect()
        width = max(240.0, float(view_rect.width()))
        height = max(240.0, float(view_rect.height()))

        dx = float(delta.x())
        dy = float(delta.y())

        orbit_sensitivity = 1.0
        orbit_yaw_sensitivity = 1.0
        orbit_pitch_sensitivity = 1.0
        orbit_roll_sensitivity = 0.85
        orbit_dominant_axis_bias = 0.88
        orbit_invert_horizontal = False
        orbit_invert_vertical = False
        orbit_swap_drag_axes = False
        orbit_shift_mode_enabled = True
        orbit_shift_horizontal_axis = 'pitch'
        orbit_shift_vertical_axis = 'yaw'
        orbit_shift_invert_horizontal = False
        orbit_shift_invert_vertical = False
        orbit_shift_lock_dominant_axis = True
        orbit_swap_pitch_yaw = False
        orbit_swap_pitch_roll = False
        orbit_swap_yaw_roll = False

        if source_view is not None:
            orbit_sensitivity = float(getattr(source_view, 'orbit_sensitivity', orbit_sensitivity))
            orbit_yaw_sensitivity = float(getattr(source_view, 'orbit_yaw_sensitivity', orbit_yaw_sensitivity))
            orbit_pitch_sensitivity = float(getattr(source_view, 'orbit_pitch_sensitivity', orbit_pitch_sensitivity))
            orbit_roll_sensitivity = float(getattr(source_view, 'orbit_roll_sensitivity', orbit_roll_sensitivity))
            orbit_dominant_axis_bias = float(getattr(source_view, 'orbit_dominant_axis_bias', orbit_dominant_axis_bias))
            orbit_invert_horizontal = bool(getattr(source_view, 'orbit_invert_horizontal', orbit_invert_horizontal))
            orbit_invert_vertical = bool(getattr(source_view, 'orbit_invert_vertical', orbit_invert_vertical))
            orbit_swap_drag_axes = bool(getattr(source_view, 'orbit_swap_drag_axes', orbit_swap_drag_axes))
            orbit_shift_mode_enabled = bool(getattr(source_view, 'orbit_shift_mode_enabled', orbit_shift_mode_enabled))
            orbit_shift_horizontal_axis = str(getattr(source_view, 'orbit_shift_horizontal_axis', orbit_shift_horizontal_axis)).lower()
            orbit_shift_vertical_axis = str(getattr(source_view, 'orbit_shift_vertical_axis', orbit_shift_vertical_axis)).lower()
            orbit_shift_invert_horizontal = bool(getattr(source_view, 'orbit_shift_invert_horizontal', orbit_shift_invert_horizontal))
            orbit_shift_invert_vertical = bool(getattr(source_view, 'orbit_shift_invert_vertical', orbit_shift_invert_vertical))
            orbit_shift_lock_dominant_axis = bool(getattr(source_view, 'orbit_shift_lock_dominant_axis', orbit_shift_lock_dominant_axis))
            orbit_swap_pitch_yaw = bool(getattr(source_view, 'orbit_swap_pitch_yaw', orbit_swap_pitch_yaw))
            orbit_swap_pitch_roll = bool(getattr(source_view, 'orbit_swap_pitch_roll', orbit_swap_pitch_roll))
            orbit_swap_yaw_roll = bool(getattr(source_view, 'orbit_swap_yaw_roll', orbit_swap_yaw_roll))

        if orbit_swap_drag_axes:
            dx, dy = dy, dx
        if orbit_invert_horizontal:
            dx = -dx
        if orbit_invert_vertical:
            dy = -dy

        abs_dx = abs(dx)
        abs_dy = abs(dy)
        move_mag = abs_dx + abs_dy

        horiz_amount = (-dx / width) * 145.0 * orbit_sensitivity
        vert_amount = (dy / height) * 145.0 * orbit_sensitivity

        if move_mag <= 1e-9:
            horiz_weight = 0.0
            vert_weight = 0.0
        else:
            horiz_weight = 0.20 + 0.80 * (abs_dx / move_mag)
            vert_weight = 0.20 + 0.80 * (abs_dy / move_mag)
            bias = max(0.0, min(0.98, orbit_dominant_axis_bias))
            if abs_dx > abs_dy * 1.8:
                vert_weight *= (1.0 - bias)
            elif abs_dy > abs_dx * 1.8:
                horiz_weight *= (1.0 - bias)

        pitch_delta = horiz_amount * horiz_weight * orbit_pitch_sensitivity
        yaw_delta = vert_amount * vert_weight * orbit_yaw_sensitivity
        roll_delta = 0.0

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            pitch_delta = 0.0
            yaw_delta = vert_amount * vert_weight * orbit_yaw_sensitivity
            roll_delta = horiz_amount * horiz_weight * orbit_roll_sensitivity

        if orbit_swap_pitch_yaw:
            pitch_delta, yaw_delta = yaw_delta, pitch_delta
        if orbit_swap_pitch_roll:
            pitch_delta, roll_delta = roll_delta, pitch_delta
        if orbit_swap_yaw_roll:
            yaw_delta, roll_delta = roll_delta, yaw_delta

        current_rotation = getattr(self, 'rotation_matrix', None)
        if not current_rotation or len(current_rotation) != 3:
            current_rotation = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
        local_delta_rotation = self._rotation_matrix_from_euler_deg(pitch_delta, yaw_delta, roll_delta)
        next_rotation = self._matrix_multiply3(current_rotation, local_delta_rotation)
        self._apply_rotation_matrix(next_rotation)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            if self.ski_item is not None and hasattr(self.ski_item, "update_3d_background_center_cache"):
                self.ski_item.update_3d_background_center_cache()
            self._orbiting = True
            self._last_mouse_pos = QPointF(event.position())
            self.setCursor(Qt.CursorShape.SizeAllCursor)
            event.accept()
            return
        if event.button() == Qt.MouseButton.MiddleButton:
            self._panning = True
            self._last_mouse_pos = QPointF(event.position())
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def _force_full_redraw(self):
        self.update()

    def mouseMoveEvent(self, event):
        pos = QPointF(event.position())
        if self._orbiting and self._last_mouse_pos is not None:
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = True
            previous_pos = self._last_mouse_pos
            self._last_mouse_pos = pos
            modifiers = event.modifiers()
            delta = pos - previous_pos
            if modifiers & Qt.KeyboardModifier.ShiftModifier:
                dx = float(delta.x())
                dy = float(delta.y())
                delta = QPointF(0.0, -dx) if abs(dx) >= abs(dy) else QPointF(dy, 0.0)
                previous_pos = QPointF(pos.x() - delta.x(), pos.y() - delta.y())
            self._set_orbit_angles_from_delta(previous_pos, pos, modifiers)
            self._interaction_active = True
            self._invalidate_projection_cache()
            self._force_full_redraw()
            event.accept()
            return
        if self._panning and self._last_mouse_pos is not None:
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = True
            delta = pos - self._last_mouse_pos
            self._last_mouse_pos = pos
            self.pan_x += delta.x()
            self.pan_y += delta.y()
            self._interaction_active = True
            self._invalidate_projection_cache()
            self._force_full_redraw()
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton and self._orbiting:
            self._orbiting = False
            self._last_mouse_pos = None
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = False
                if hasattr(self.ski_item, "update_3d_background_center_cache"):
                    self.ski_item.update_3d_background_center_cache()
                self.ski_item.update()
            self._interaction_active = False
            self._invalidate_projection_cache()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.update()
            event.accept()
            return
        if event.button() == Qt.MouseButton.MiddleButton and self._panning:
            self._panning = False
            self._last_mouse_pos = None
            if self.ski_item is not None:
                self.ski_item.interaction_3d_active = False
                if hasattr(self.ski_item, "update_3d_background_center_cache"):
                    self.ski_item.update_3d_background_center_cache()
                self.ski_item.update()
            self.setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def _rotate_point(self, pt):
        x, y, z = (float(pt[0]), float(pt[1]), float(pt[2]))
        x = -x
        matrix = getattr(self, 'rotation_matrix', None)
        if not matrix or len(matrix) != 3:
            matrix = self._rotation_matrix_from_euler_deg(self.rot_x, self.rot_y, self.rot_z)
            self.rotation_matrix = matrix
        rx = matrix[0][0] * x + matrix[0][1] * y + matrix[0][2] * z
        ry = matrix[1][0] * x + matrix[1][1] * y + matrix[1][2] * z
        rz = matrix[2][0] * x + matrix[2][1] * y + matrix[2][2] * z
        return (rx, ry, rz)

    def _project_points(self, points3d, rect):
        rotated = [self._rotate_point(pt) for pt in points3d]
        if not rotated:
            return {}, 1.0
        xs = [p[0] for p in rotated]
        ys = [p[1] for p in rotated]
        span_x = max(1e-6, max(xs) - min(xs))
        span_y = max(1e-6, max(ys) - min(ys))
        scale = self.zoom
        cx = (min(xs) + max(xs)) * 0.5
        cy = (min(ys) + max(ys)) * 0.5
        ox = rect.center().x() + self.pan_x
        oy = rect.center().y() + self.pan_y
        projected = {}
        for idx, rp in enumerate(rotated):
            sx = ox + (rp[0] - cx) * scale
            sy = oy - (rp[1] - cy) * scale
            projected[idx] = (sx, sy, rp[2])
        return projected, scale

    def _workspace_points(self):
        wx, wy, wz = self._workspace_size
        ox, oy, oz = self._workspace_origin
        return [
            (ox, oy, oz),
            (ox + wx, oy, oz),
            (ox + wx, oy + wy, oz),
            (ox, oy + wy, oz),
            (ox, oy, oz + wz),
            (ox + wx, oy, oz + wz),
            (ox + wx, oy + wy, oz + wz),
            (ox, oy + wy, oz + wz),
        ]

    def _draw_arrow_head(self, painter, tip_point, tail_point, color, size=8.0):
        dx = float(tip_point.x() - tail_point.x())
        dy = float(tip_point.y() - tail_point.y())
        length = math.hypot(dx, dy)
        if length <= 1e-6:
            return
        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux
        back_x = tip_point.x() - ux * size
        back_y = tip_point.y() - uy * size
        wing = size * 0.48
        poly = QPolygonF([
            QPointF(tip_point.x(), tip_point.y()),
            QPointF(back_x + px * wing, back_y + py * wing),
            QPointF(back_x - px * wing, back_y - py * wing),
        ])
        painter.save()
        painter.setPen(QPen(color, 1))
        painter.setBrush(QBrush(color))
        painter.drawPolygon(poly)
        painter.restore()

    def _draw_coordinate_axes_overlay(self, painter, rect, projected, origin_idx=0, x_idx=1, y_idx=3, z_idx=4, label_font=None):
        if origin_idx not in projected or x_idx not in projected or y_idx not in projected or z_idx not in projected:
            return
        margin = 18.0
        axis_len = 56.0
        base = QPointF(rect.left() + margin + 8.0, rect.bottom() - margin - 8.0)
        origin_pt = QPointF(projected[origin_idx][0], projected[origin_idx][1])
        axis_map = {
            'X': QPointF(projected[x_idx][0], projected[x_idx][1]),
            'Y': QPointF(projected[y_idx][0], projected[y_idx][1]),
            'Z': QPointF(projected[z_idx][0], projected[z_idx][1]),
        }
        colors = {
            'X': QColor(255, 120, 120, 235),
            'Y': QColor(120, 235, 150, 235),
            'Z': QColor(120, 180, 255, 235),
        }
        painter.save()
        if label_font is not None:
            painter.setFont(label_font)
        for label, axis_pt in axis_map.items():
            vx = float(axis_pt.x() - origin_pt.x())
            vy = float(axis_pt.y() - origin_pt.y())
            vlen = math.hypot(vx, vy)
            if vlen <= 1e-6:
                continue
            ux = vx / vlen
            uy = vy / vlen
            end_pt = QPointF(base.x() + ux * axis_len, base.y() + uy * axis_len)
            pen = QPen(colors[label], 2.2)
            pen.setCosmetic(True)
            painter.setPen(pen)
            painter.drawLine(base, end_pt)
            self._draw_arrow_head(painter, end_pt, base, colors[label], size=9.0)
            text_pt = QPointF(end_pt.x() + ux * 8.0 + 2.0, end_pt.y() + uy * 8.0 + 2.0)
            painter.setPen(QPen(colors[label], 1))
            painter.drawText(text_pt, label)
        painter.setPen(QPen(QColor(235, 238, 242, 220), 1))
        painter.setBrush(QBrush(QColor(235, 238, 242, 220)))
        painter.drawEllipse(base, 2.8, 2.8)
        painter.restore()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, not self._interaction_active)
        rect = self.rect().adjusted(8, 8, -8, -8)
        painter.fillRect(rect, QColor(30, 33, 38))
        panel_pen = QPen(QColor(85, 92, 102), 1)
        painter.setPen(panel_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(rect, 10, 10)

        base_font = painter.font()
        base_size = max(base_font.pointSize(), 9)
        title_font = QFont(base_font)
        title_font.setPointSize(max(int(round(base_size * 3.0)), 27))
        title_font.setBold(True)
        info_font = QFont(base_font)
        info_font.setPointSize(max(int(round(base_size * 2.4)), 22))
        axis_font = QFont(base_font)
        axis_font.setPointSize(max(int(round(base_size * 1.4)), 13))
        stats_font = QFont(base_font)
        stats_font.setPointSize(12)
        marker_font = QFont(base_font)
        marker_font.setPointSize(7)

        title_rect = rect.adjusted(12, 8, -12, -8)
        painter.setPen(QColor(195, 200, 208))
        painter.setFont(title_font)
        painter.drawText(title_rect, int(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft), "3D CNC Toolpath Preview")
        painter.setFont(info_font)
        painter.drawText(title_rect.adjusted(0, title_font.pointSize() + 8, 0, 0), int(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft), "RMB orbit  •  Shift changes left/right from pitch to roll  •  MMB pan  •  Wheel zoom")

        viewport_rect = rect.adjusted(10, max(94, title_font.pointSize() + info_font.pointSize() + 34), -10, -12)
        self._ensure_geometry_cache()
        if len(self._cached_scene_points) <= 9:
            painter.setPen(QColor(180, 185, 192))
            painter.drawText(viewport_rect, int(Qt.AlignmentFlag.AlignCenter), "No 3D CNC toolpath to preview")
            return

        projected, scale = self._project_cached_points(viewport_rect)
        if not projected:
            painter.setPen(QColor(180, 185, 192))
            painter.drawText(viewport_rect, int(Qt.AlignmentFlag.AlignCenter), "No 3D CNC toolpath to preview")
            return

        draw_data = self._cached_draw_data_interaction if self._interaction_active else self._cached_draw_data_full
        workspace_pen = QPen(QColor(70, 76, 84, 210), 1)
        workspace_pen.setStyle(Qt.PenStyle.DashLine)
        workspace_pen.setCosmetic(True)
        if self._show_workspace_boundary:
            painter.setPen(workspace_pen)
            for a, b in draw_data['workspace_edges']:
                painter.drawLine(QPointF(projected[a][0], projected[a][1]), QPointF(projected[b][0], projected[b][1]))

        owner = getattr(getattr(self, 'ski_item', None), 'owner_window', None)
        fallback_pen = QPen(QColor(0, 180, 180, 245), 2)
        fallback_pen.setCosmetic(True)

        for segments, start_idx_for_group in draw_data['segment_ranges']:
            idx = start_idx_for_group
            for seg in segments:
                seg_type = seg[2]
                feed_value = seg[3] if len(seg) > 3 else None
                if owner is not None and hasattr(owner, '_cnc_segment_pen'):
                    pen = owner._cnc_segment_pen(seg_type, feed_value, 2)
                else:
                    pen = fallback_pen
                pen.setCosmetic(True)
                painter.setPen(pen)
                painter.drawLine(QPointF(projected[idx][0], projected[idx][1]), QPointF(projected[idx + 1][0], projected[idx + 1][1]))
                idx += 2

        start_idx = draw_data['start_idx']
        painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawEllipse(QPointF(projected[start_idx][0], projected[start_idx][1]), 5.0, 5.0)
        painter.setFont(marker_font)
        painter.drawText(QPointF(projected[start_idx][0] + 8.0, projected[start_idx][1] - 8.0), 'G54 (0,0,0)')
        entry_idx = draw_data['entry_idx']

        if entry_idx is not None:
            painter.setPen(QPen(QColor(255, 160, 160, 225), 1.5))
            painter.setBrush(QBrush(QColor(255, 160, 160, 230)))
            painter.drawEllipse(QPointF(projected[entry_idx][0], projected[entry_idx][1]), 4.0, 4.0)
            painter.setFont(info_font)
            #painter.drawText(QPointF(projected[entry_idx][0] + 8.0, projected[entry_idx][1] + 14.0), 'Entry')

        self._draw_coordinate_axes_overlay(painter, viewport_rect, projected, label_font=axis_font)

        painter.setPen(QColor(195, 200, 208))
        painter.setFont(stats_font)
        wx, wy, wz = self._workspace_size
        ox, oy, oz = self._workspace_origin
        preview_x, preview_y = self._preview_offset_xy
        stats_line_h = max(18.0, float(painter.fontMetrics().height()) + 5.0)
        stats_box = QRectF(viewport_rect.left() + 12.0, viewport_rect.top() + 152.0, 560.0, stats_line_h * 4.0 + 42.0)
        painter.setPen(QPen(QColor(95, 102, 112, 160), 1))
        painter.setBrush(QBrush(QColor(20, 22, 26, 155)))
        painter.drawRoundedRect(stats_box, 4, 4)
        painter.setPen(QColor(195, 200, 208))
        text_rect = stats_box.adjusted(10.0, 8.0, -10.0, -8.0)
        painter.drawText(QRectF(text_rect.left(), text_rect.top(), text_rect.width(), stats_line_h), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                         f"Workspace X {wx:.0f}  Y {wy:.0f}  Z {wz:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h, text_rect.width(), stats_line_h), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                         f"Offset X {preview_x:.0f}  Y {preview_y:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h * 2.0, text_rect.width(), stats_line_h), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                         f"Move X {ox:.0f}  Y {oy:.0f}  Z {oz:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h * 3.0, text_rect.width(), stats_line_h), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter),
                         f"View P {self.rot_x:.0f}  Y {self.rot_y:.0f}  R {self.rot_z:.0f}")


class MainWindow(QWidget):
    def __init__(self, startup_values=None):

        super().__init__()
        self.setWindowTitle("Ski/Snowboard CAD & CAM")
        self.resize(2000, 1200)
        self.undo_stack = []
        self.redo_stack = []
        self._exiting_via_confirm = False
        self._startup_initializing = True
        self._cnc_preview_payload_cache_key = None
        self._cnc_preview_payload_cache_value = None
        self.setStyleSheet("""
            QWidget {
                background-color: #2B2F34;
                color: #EAEAEA;
            }

            QGroupBox {
                background-color: #33383F;
                border: 1px solid #4E535B;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px;
            }

            QPushButton {
                background-color: #3A3D42;
                border: 1px solid #5B616A;
                padding: 6px;
                color: #F2F2F2;
            }

            QPushButton:hover {
                background-color: #4A4E55;
            }

            QPushButton:pressed {
                background-color: #2D3035;
            }

            QSlider::groove:horizontal {
                background: #444;
                height: 4px;
            }

            QSlider::handle:horizontal {
                background: #888;
                width: 10px;
                margin: -4px 0;
            }

            QSpinBox, QDoubleSpinBox {
                background-color: #2E3238;
                border: 1px solid #555;
                padding: 2px;
                padding-right: 28px;   /* reserve space for arrow buttons */
 
 }

            QLabel {
                color: #E0E0E0;
            }

            QScrollArea {
                border: none;
                background: #262A30;
            }

            QScrollBar:vertical {
                background: #262A30;
                width: 20px;
                margin: 0;
            }

            QScrollBar::handle:vertical {
                background: #5B616A;
                min-height: 200px;
                border-radius: 8px;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                height: 0;
            }

            QScrollBar:horizontal {
                background: #262A30;
                height: 20px;
                margin: 0;
            }

            QScrollBar::handle:horizontal {
                background: #5B616A;
                min-width: 200px;
                border-radius: 8px;
            }

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
                width: 0;
            }

            #sidebarScrollContents {
                background-color: #262A30;
            }

            #sidebarScrollContents QPushButton,
            #sidebarScrollContents QToolButton {
                min-height: 28px;
                padding: 4px 6px;
            }

            #sidebarScrollContents QDoubleSpinBox,
            #sidebarScrollContents QSpinBox,
            #sidebarScrollContents QComboBox {
                min-height: 24px;
            }

            #sidebarScrollContents QTextEdit {
                background-color: #22262C;
                border: 1px solid #4E535B;
                border-radius: 6px;
                min-height: 180px;
            }

            #mainSplitter::handle {
                background-color: #1D2025;
                border-left: 1px solid #4E535B;
                border-right: 1px solid #121418;
            }

            #mainSplitter::handle:hover {
                background-color: #56606C;
            }

            #collapsiblePanel {
                background-color: transparent;
                border: none;
            }

            #collapsiblePanelToggle {
                text-align: left;
                font-weight: bold;
                border: 1px solid #4E535B;
                border-radius: 8px;
                background-color: #33383F;
                padding: 6px 8px;
            }

            #collapsiblePanelToggle:hover {
                background-color: #3B4048;
            }

            #collapsiblePanelToggle:checked {
                background-color: #3A3F47;
            }
        """)
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)
        self.setLayout(outer_layout)

        self.menu_bar = QMenuBar()
        outer_layout.addWidget(self.menu_bar)

        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        outer_layout.addLayout(root_layout, 1)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setObjectName("mainSplitter")
        self.main_splitter.setChildrenCollapsible(False)
        self.main_splitter.setHandleWidth(8)
        root_layout.addWidget(self.main_splitter, 1)

        self.scene = QGraphicsScene()
        self.scene.setSceneRect(-50000, -50000, 100000, 100000)
        self.ski = SkiShape()
        loaded_file_data = startup_values.get("loaded_file_data") if startup_values else None
        if loaded_file_data is not None:
            self.ski.deserialize(loaded_file_data)
        elif startup_values:
            preset_name = startup_values.get("ski_type")
            if preset_name:
                self.ski.apply_shape_preset(preset_name)
            self.ski.apply_startup_values(startup_values)
        self.scene.addItem(self.ski)
        self.ski.owner_window = self
        self.view = SkiView(self.scene)
        self.view.ski_item = self.ski
        self.view.centerOn(self.ski.boundingRect().center())
        self.view._refresh_scale_overlay()
        self.view_container = QWidget()
        self.view_container.setObjectName("viewContainer")
        self.view_container_layout = QGridLayout(self.view_container)
        self.view_container_layout.setContentsMargins(0, 0, 0, 0)
        self.view_container_layout.setSpacing(0)
        self.view_container_layout.addWidget(self.view, 0, 0)
        self.fit_whole_view_overlay = QWidget()
        self.fit_whole_view_overlay.setObjectName("fitWholeViewOverlay")
        self.fit_whole_view_overlay.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.fit_whole_view_overlay.setStyleSheet("#fitWholeViewOverlay { background: transparent; }")
        self.fit_whole_view_overlay.setFixedSize(196, 128)
        self.fit_whole_view_overlay_layout = QVBoxLayout(self.fit_whole_view_overlay)
        self.fit_whole_view_overlay_layout.setContentsMargins(0, 18, 24, 0)
        self.fit_whole_view_overlay_layout.setSpacing(6)
        self.fit_whole_view_button = QPushButton("Fit View")
        self.fit_whole_view_button.setObjectName("fitWholeViewButton")
        self.fit_whole_view_button.setToolTip("Recenter and rescale the whole workspace")
        self.fit_whole_view_button.setFixedSize(172, 68)
        self.fit_whole_view_button.setStyleSheet(
            "#fitWholeViewButton {"
            "background-color: rgba(46, 50, 56, 225);"
            "border: 1px solid #8D96A2;"
            "border-radius: 6px;"
            "color: #F6FBFF;"
            "font-size: 18px;"
            "font-weight: 600;"
            "padding: 8px 14px;"
            "}"
            "#fitWholeViewButton:hover { background-color: rgba(70, 76, 84, 240); }"
            "#fitWholeViewButton:pressed { background-color: rgba(35, 39, 45, 245); }"
        )
        self.save_whole_view_button = QPushButton("Save View")
        self.save_whole_view_button.setObjectName("saveWholeViewButton")
        self.save_whole_view_button.setToolTip("Save the current workspace position and zoom for Fit View")
        self.save_whole_view_button.setFixedSize(116, 32)
        self.save_whole_view_button.setStyleSheet(
            "#saveWholeViewButton {"
            "background-color: rgba(46, 50, 56, 225);"
            "border: 1px solid #8D96A2;"
            "border-radius: 6px;"
            "color: #F6FBFF;"
            "font-size: 13px;"
            "font-weight: 600;"
            "padding: 4px 8px;"
            "}"
            "#saveWholeViewButton:hover { background-color: rgba(70, 76, 84, 240); }"
            "#saveWholeViewButton:pressed { background-color: rgba(35, 39, 45, 245); }"
        )
        self.fit_whole_view_overlay_layout.addWidget(self.fit_whole_view_button, 0, Qt.AlignmentFlag.AlignRight)
        self.fit_whole_view_overlay_layout.addWidget(self.save_whole_view_button, 0, Qt.AlignmentFlag.AlignRight)
        self.fit_whole_view_overlay_layout.addStretch(1)
        self.view_container_layout.addWidget(
            self.fit_whole_view_overlay,
            0,
            0,
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight,
        )

        sidebar = QScrollArea()
        sidebar.setWidgetResizable(True)
        sidebar.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        sidebar.setFrameShape(QFrame.Shape.NoFrame)
        sidebar.setMinimumWidth(280)
        sidebar.setMaximumWidth(760)

        sidebar_contents = QWidget()
        sidebar_contents.setObjectName("sidebarScrollContents")
        sidebar_layout = QVBoxLayout(sidebar_contents)
        sidebar_layout.setContentsMargins(8, 8, 8, 8)
        sidebar_layout.setSpacing(8)

        view_group = QGroupBox()
        view_layout = QGridLayout(view_group)
        view_layout.setHorizontalSpacing(6)
        view_layout.setVerticalSpacing(6)

        layup_group = QGroupBox()
        layup_layout = QGridLayout(layup_group)
        layup_layout.setHorizontalSpacing(6)
        layup_layout.setVerticalSpacing(6)

        mold_group = QGroupBox()
        mold_layout = QGridLayout(mold_group)
        mold_layout.setHorizontalSpacing(6)
        mold_layout.setVerticalSpacing(6)

        two_d_appearance_group = QGroupBox()
        two_d_appearance_layout = QGridLayout(two_d_appearance_group)
        two_d_appearance_layout.setHorizontalSpacing(6)
        two_d_appearance_layout.setVerticalSpacing(6)

        lighting_group = QGroupBox()
        lighting_layout = QGridLayout(lighting_group)
        lighting_layout.setHorizontalSpacing(6)
        lighting_layout.setVerticalSpacing(6)
        cnc_group = QGroupBox()
        cnc_layout = QGridLayout(cnc_group)
        cnc_layout.setHorizontalSpacing(6)
        cnc_layout.setVerticalSpacing(6)
        # Project Section
        # View Section
        self.toggle_points_button = QPushButton("Show Points")
        self.toggle_dimensions_button = QPushButton("Show Dim's")
        self.toggle_circle_button = QPushButton("Show Sidecut Circle")
        self.toggle_global_coordinates_button = QPushButton("Show Global Coordinates")
        self.toggle_stiffness_plot_button = QPushButton("Show Stiffness Plot")
        self.toggle_stats_button = QPushButton("Show Geometry Stats")
        self.toggle_cnc_stats_button = QPushButton("Show CNC Stats")
        self.toggle_interface_shortcuts_button = QPushButton("Interface Shortcuts")
        self.view_style_shaded_button = QPushButton("Shaded")
        self.view_style_edges_button = QPushButton("Shade+Edges")
        self.view_style_wire_button = QPushButton("Wireframe")
        self.view_style_graphic_button = QPushButton("Graphic")
        self.view_home_button = QPushButton("Home View")
        self.view_front_button = QPushButton("Front View")
        self.view_top_button = QPushButton("Top View")
        self.view_side_button = QPushButton("Side View")
        self.save_3d_position_button = QPushButton("Save 3D Position")
        self.load_3d_position_button = QPushButton("Load 3D Position")
        self.second_ski_layout_button = QPushButton("Base to Base")
        self.background_toggle_button = QPushButton("Background")
        self.background_toggle_button.setCheckable(True)
        self.second_ski_spacing_label = QLabel("2nd Ski Base Spacing")
        self.second_ski_spacing_slider = QSlider(Qt.Orientation.Horizontal)
        self.second_ski_spacing_value_label = QLabel()
        self.toggle_second_ski_button = QPushButton("Show 2nd Ski")
        self.load_right_graphic_button = QPushButton("Load/Show Right Graphic")
        self.load_left_graphic_button = QPushButton("Load/Show Left Graphic")
        self.mouse_input_settings_button = QPushButton("3D Mouse Input Settings")
        self.pick_3d_color_button = QPushButton("3D Ski Color")
        self.pick_3d_background_color_button = QPushButton("3D Background Color")
        self.two_d_graphic_target_combo = QComboBox()
        self.two_d_graphic_target_combo.addItems(["Right / Top Graphic", "Left / Base Graphic"])
        self.two_d_graphic_offset_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.two_d_graphic_offset_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.two_d_graphic_scale_x_slider = QSlider(Qt.Orientation.Horizontal)
        self.two_d_graphic_scale_y_slider = QSlider(Qt.Orientation.Horizontal)
        self.two_d_graphic_offset_x_value_label = QLabel()
        self.two_d_graphic_offset_y_value_label = QLabel()
        self.two_d_graphic_scale_x_value_label = QLabel()
        self.two_d_graphic_scale_y_value_label = QLabel()
        self.upper_mold_offset_slider = QSlider(Qt.Orientation.Horizontal)
        self.mold_hole_count_slider = QSlider(Qt.Orientation.Horizontal)
        self.mold_hole_diameter_slider = QSlider(Qt.Orientation.Horizontal)
        self.upper_mold_offset_value_label = QLabel()
        self.mold_hole_count_value_label = QLabel()
        self.mold_hole_diameter_value_label = QLabel()
        #self.seam_editor_note = QLabel("L - Lock tangent handles 180 deg from eachother(gray/white)\nV-Lock tangent handles vertically(violette).\nH-Locks tangent handles horizontally(teal).")
        self.seam_editor_values = QLabel("")

        for btn in [self.toggle_points_button, self.toggle_dimensions_button, self.toggle_circle_button, self.toggle_global_coordinates_button, self.toggle_stiffness_plot_button, self.toggle_stats_button, self.toggle_cnc_stats_button, self.toggle_interface_shortcuts_button]:
            btn.setCheckable(True)
        self.toggle_stiffness_plot_button.setChecked(False)
        self.toggle_stats_button.setChecked(False)
        self.toggle_cnc_stats_button.setChecked(False)
        self.toggle_interface_shortcuts_button.setChecked(False)
        for btn in [self.view_style_shaded_button, self.view_style_edges_button, self.view_style_wire_button, self.view_style_graphic_button]:
            btn.setCheckable(True)


        self.base_toggle_button = QPushButton("Base On")
        self.edge_inlay_toggle_button = QPushButton("Edge Inlay On")
        self.core_toggle_button = QPushButton("Core On")
        self.sidewall_toggle_button = QPushButton("Sidewalls On")
        self.spacer_toggle_button = QPushButton("Tip/Tail Spacers On")
        self.shell_toggle_button = QPushButton("Shell On")
        for btn in [self.base_toggle_button, self.edge_inlay_toggle_button, self.core_toggle_button, self.sidewall_toggle_button, self.spacer_toggle_button, self.shell_toggle_button]:
            btn.setCheckable(True)
            btn.setChecked(True)

        self.rot_x_spin = QDoubleSpinBox()
        self.rot_y_spin = QDoubleSpinBox()
        self.rot_z_spin = QDoubleSpinBox()
        self.light_azimuth_slider = QSlider(Qt.Orientation.Horizontal)
        self.light_elevation_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.background_width_slider = QSlider(Qt.Orientation.Horizontal)
        self.background_height_slider = QSlider(Qt.Orientation.Horizontal)
        self.second_ski_spacing_slider.setRange(-300, 300)
        self.second_ski_spacing_slider.setSingleStep(1)
        self.second_ski_spacing_slider.setPageStep(5)
        self.second_ski_spacing_slider.setValue(int(round(float(getattr(self.ski, "second_3d_base_separation_cm", 7.5)) * 10.0)) if hasattr(self, "ski") else 75)
        self.two_d_graphic_offset_x_slider.setRange(-2000, 2000)
        self.two_d_graphic_offset_y_slider.setRange(-2000, 2000)
        self.two_d_graphic_scale_x_slider.setRange(10, 400)
        self.two_d_graphic_scale_x_slider.setSingleStep(1)
        self.two_d_graphic_scale_x_slider.setPageStep(10)
        self.two_d_graphic_scale_y_slider.setRange(10, 400)
        self.two_d_graphic_scale_y_slider.setSingleStep(1)
        self.two_d_graphic_scale_y_slider.setPageStep(10)
        self.upper_mold_offset_slider.setRange(0, 120)
        self.upper_mold_offset_slider.setSingleStep(1)
        self.upper_mold_offset_slider.setPageStep(5)
        self.mold_hole_count_slider.setRange(1, 10)
        self.mold_hole_count_slider.setSingleStep(1)
        self.mold_hole_diameter_slider.setRange(1, 80)
        self.mold_hole_diameter_slider.setSingleStep(1)
        self.mold_hole_diameter_slider.setPageStep(5)
        self.light_azimuth_value_label = QLabel()
        self.light_elevation_value_label = QLabel()
        self.brightness_value_label = QLabel()
        self.background_width_value_label = QLabel()
        self.background_height_value_label = QLabel()
        self.background_width_text_label = QLabel("Background Width")
        self.background_height_text_label = QLabel("Background Height")
        self.edge_thickness_spin = QDoubleSpinBox()
        self.sidewall_thickness_spin = QDoubleSpinBox()
        self.left_sidewall_thickness_spin = QDoubleSpinBox()
        self.edge_inlay_tip_spin = QDoubleSpinBox()
        self.edge_inlay_tail_spin = QDoubleSpinBox()
        self.base_edge_corner_radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.base_edge_corner_radius_value_label = QLabel()
        self.splitboard_inside_edge_check = QCheckBox("Include Splitboard Inside Edge")
        self.minimum_core_thickness_spin = QDoubleSpinBox()
        self.tip_spacer_spin = QDoubleSpinBox()
        self.tail_spacer_spin = QDoubleSpinBox()
        self.seam_depth_spin = QDoubleSpinBox()
        self.tip_seam_point_count_spin = QDoubleSpinBox()
        self.tail_seam_point_count_spin = QDoubleSpinBox()
        self.seam_inner_x_spin = QDoubleSpinBox()
        self.seam_inner_y_spin = QDoubleSpinBox()
        self.seam_outer_x_spin = QDoubleSpinBox()
        self.seam_outer_y_spin = QDoubleSpinBox()
        #self.seam_editor_note = QLabel("L - Lock tangent handles 180 deg from eachother(gray/white)\nV-Lock tangent handles vertically(violette).\nH-Locks tangent handles horizontally(teal).")
        self.seam_editor_values = QLabel("")
        self.lower_reinf_slider = QSlider(Qt.Orientation.Horizontal)
        self.core_stiffness_slider = QSlider(Qt.Orientation.Horizontal)
        self.upper_reinf_slider = QSlider(Qt.Orientation.Horizontal)
        self.lower_reinf_value_label = QLabel()
        self.core_stiffness_value_label = QLabel()
        self.upper_reinf_value_label = QLabel()
        self.build_sheet_note_editors = {}

        self.cnc_shape_button_group = QButtonGroup(self)
        self.cnc_shape_button_group.setExclusive(True)
        self.cnc_shape_buttons = {}
        self.selected_cnc_shape_name = None
        self._cnc_toolpath_cache = {}
        self.cnc_outside_stub_filter_mm = 0.06
        self.cnc_outside_bridge_filter_mm = 0.20
        self.cnc_outside_spike_area_factor = 0.30
        self.cnc_shape_grid = QGridLayout()
        self.cnc_shape_grid.setHorizontalSpacing(6)
        self.cnc_shape_grid.setVerticalSpacing(6)
        self.cnc_operation_combo = QComboBox()
        self.cnc_operation_combo.addItems(["On Line", "Outside", "Pocket", "Boring", "Helical Boring"])
        self.cnc_preview_color_mode_combo = QComboBox()
        self.cnc_preview_color_mode_combo.addItems(["Feed Rate", "Motion Type"])
        self.cnc_depth_mode_check = QCheckBox("Depth From Core Profile")
        self.cnc_depth_mode_check.setChecked(False)
        self.cnc_depth_profile_invert_check = QCheckBox("Mirror Depth Profile Horizontally")
        self.cnc_depth_profile_invert_check.setChecked(True)
        self.cnc_snap_home_button = QPushButton("Home")
        self.cnc_snap_front_button = QPushButton("Front")
        self.cnc_snap_top_button = QPushButton("Top")
        self.cnc_snap_side_button = QPushButton("Side")
        self.cnc_recenter_button = QPushButton("Recenter")
        self.cnc_rescale_button = QPushButton("Re-scale")
        self.cnc_save_view_button = QPushButton("Save Custom View")
        self.cnc_load_view_button = QPushButton("Custom 1")
        self.cnc_custom_2_view_button = QPushButton("Custom 2")
        self.cnc_duplicate_check = QCheckBox("Duplicate Toolpath")
        self.cnc_duplicate_check.setChecked(False)
        self.cnc_duplicate_x_spin = QDoubleSpinBox()
        self.cnc_duplicate_x_spin.setRange(-100000.0, 100000.0)
        self.cnc_duplicate_x_spin.setDecimals(1)
        self.cnc_duplicate_x_spin.setSingleStep(10.0)
        self.cnc_duplicate_x_spin.setSuffix(" mm")
        self.cnc_duplicate_x_spin.setValue(0.0)
        self.cnc_duplicate_y_spin = QDoubleSpinBox()
        self.cnc_duplicate_y_spin.setRange(-100000.0, 100000.0)
        self.cnc_duplicate_y_spin.setDecimals(1)
        self.cnc_duplicate_y_spin.setSingleStep(10.0)
        self.cnc_duplicate_y_spin.setSuffix(" mm")
        self.cnc_duplicate_y_spin.setValue(0.0)
        self.cnc_ramp_entry_check = QCheckBox("Ramp Entry")
        self.cnc_ramp_entry_check.setChecked(False)
        self.cnc_ramp_angle_spin = QDoubleSpinBox()
        self.cnc_ramp_angle_spin.setRange(0.1, 45.0)
        self.cnc_ramp_angle_spin.setDecimals(1)
        self.cnc_ramp_angle_spin.setSingleStep(0.5)
        self.cnc_ramp_angle_spin.setSuffix(" deg")
        self.cnc_ramp_angle_spin.setValue(3.0)
        self.cnc_helix_angle_spin = QDoubleSpinBox()
        self.cnc_helix_angle_spin.setRange(0.1, 45.0)
        self.cnc_helix_angle_spin.setDecimals(1)
        self.cnc_helix_angle_spin.setSingleStep(0.5)
        self.cnc_helix_angle_spin.setSuffix(" deg")
        self.cnc_helix_angle_spin.setValue(3.0)
        self.cnc_ramp_feed_rate_spin = QDoubleSpinBox()
        self.cnc_ramp_feed_rate_spin.setRange(1.0, 50000.0)
        self.cnc_ramp_feed_rate_spin.setDecimals(1)
        self.cnc_ramp_feed_rate_spin.setSingleStep(10.0)
        self.cnc_ramp_feed_rate_spin.setSuffix(" mm/min")
        self.cnc_ramp_feed_rate_spin.setValue(450.0)
        self.cnc_tool_diameter_spin = QDoubleSpinBox()
        self.cnc_tool_diameter_spin.setRange(0.1, 50.0)
        self.cnc_tool_diameter_spin.setDecimals(3)
        self.cnc_tool_diameter_spin.setSingleStep(0.1)
        self.cnc_tool_diameter_spin.setSuffix(" mm")
        self.cnc_tool_diameter_spin.setValue(6.35)
        self.cnc_safety_z_spin = QDoubleSpinBox()
        self.cnc_safety_z_spin.setRange(0.0, 100.0)
        self.cnc_safety_z_spin.setDecimals(3)
        self.cnc_safety_z_spin.setSingleStep(1.0)
        self.cnc_safety_z_spin.setSuffix(" mm")
        self.cnc_safety_z_spin.setValue(10.0)
        self.cnc_start_x_spin = QDoubleSpinBox()
        self.cnc_start_x_spin.setRange(-5000.0, 5000.0)
        self.cnc_start_x_spin.setDecimals(3)
        self.cnc_start_x_spin.setSingleStep(10.0)
        self.cnc_start_x_spin.setSuffix(" mm")
        self.cnc_start_y_spin = QDoubleSpinBox()
        self.cnc_start_y_spin.setRange(-5000.0, 5000.0)
        self.cnc_start_y_spin.setDecimals(3)
        self.cnc_start_y_spin.setSingleStep(10.0)
        self.cnc_start_y_spin.setSuffix(" mm")
        self.cnc_cut_depth_spin = QDoubleSpinBox()
        self.cnc_cut_depth_spin.setRange(0.01, 100.0)
        self.cnc_cut_depth_spin.setDecimals(3)
        self.cnc_cut_depth_spin.setSingleStep(0.5)
        self.cnc_cut_depth_spin.setSuffix(" mm")
        self.cnc_cut_depth_spin.setValue(3.0)
        self.cnc_stepdown_spin = QDoubleSpinBox()
        self.cnc_stepdown_spin.setRange(0.01, 50.0)
        self.cnc_stepdown_spin.setDecimals(3)
        self.cnc_stepdown_spin.setSingleStep(0.5)
        self.cnc_stepdown_spin.setSuffix(" mm")
        self.cnc_stepdown_spin.setValue(1.0)
        self.cnc_feed_rate_spin = QDoubleSpinBox()
        self.cnc_feed_rate_spin.setRange(1.0, 50000.0)
        self.cnc_feed_rate_spin.setDecimals(1)
        self.cnc_feed_rate_spin.setSingleStep(10.0)
        self.cnc_feed_rate_spin.setSuffix(" mm/min")
        self.cnc_feed_rate_spin.setValue(1200.0)
        self.cnc_plunge_rate_spin = QDoubleSpinBox()
        self.cnc_plunge_rate_spin.setRange(1.0, 20000.0)
        self.cnc_plunge_rate_spin.setDecimals(1)
        self.cnc_plunge_rate_spin.setSingleStep(10.0)
        self.cnc_plunge_rate_spin.setSuffix(" mm/min")
        self.cnc_plunge_rate_spin.setValue(300.0)
        self.cnc_spindle_spin = QDoubleSpinBox()
        self.cnc_spindle_spin.setRange(0.0, 100000.0)
        self.cnc_spindle_spin.setDecimals(0)
        self.cnc_spindle_spin.setSingleStep(500.0)
        self.cnc_spindle_spin.setSuffix(" RPM")
        self.cnc_spindle_spin.setValue(18000.0)
        self.generate_gcode_button = QPushButton("Generate G-Code")
        self.save_gcode_button = QPushButton("Save G-Code")
        self.cnc_preview = QTextEdit()
        self.cnc_preview.setReadOnly(True)
        self.cnc_preview.setFont(QFont("Courier New", 12))
        self.cnc_3d_preview_widget = CNCToolpath3DView(self)
        self.cnc_workspace_x_spin = QDoubleSpinBox()
        self.cnc_workspace_x_spin.setRange(1.0, 100000.0)
        self.cnc_workspace_x_spin.setDecimals(1)
        self.cnc_workspace_x_spin.setSingleStep(10.0)
        self.cnc_workspace_x_spin.setSuffix(" mm")
        self.cnc_workspace_x_spin.setValue(300.0)
        self.cnc_workspace_y_spin = QDoubleSpinBox()
        self.cnc_workspace_y_spin.setRange(1.0, 100000.0)
        self.cnc_workspace_y_spin.setDecimals(1)
        self.cnc_workspace_y_spin.setSingleStep(10.0)
        self.cnc_workspace_y_spin.setSuffix(" mm")
        self.cnc_workspace_y_spin.setValue(2000.0)
        self.cnc_workspace_z_spin = QDoubleSpinBox()
        self.cnc_workspace_z_spin.setRange(1.0, 100000.0)
        self.cnc_workspace_z_spin.setDecimals(1)
        self.cnc_workspace_z_spin.setSingleStep(10.0)
        self.cnc_workspace_z_spin.setSuffix(" mm")
        self.cnc_workspace_z_spin.setValue(150.0)
        self.cnc_workspace_move_x_spin = QDoubleSpinBox()
        self.cnc_workspace_move_x_spin.setRange(-100000.0, 100000.0)
        self.cnc_workspace_move_x_spin.setDecimals(1)
        self.cnc_workspace_move_x_spin.setSingleStep(10.0)
        self.cnc_workspace_move_x_spin.setSuffix(" mm")
        self.cnc_workspace_move_x_spin.setValue(0.0)
        self.cnc_workspace_move_y_spin = QDoubleSpinBox()
        self.cnc_workspace_move_y_spin.setRange(-100000.0, 100000.0)
        self.cnc_workspace_move_y_spin.setDecimals(1)
        self.cnc_workspace_move_y_spin.setSingleStep(10.0)
        self.cnc_workspace_move_y_spin.setSuffix(" mm")
        self.cnc_workspace_move_y_spin.setValue(0.0)
        self.cnc_workspace_move_z_spin = QDoubleSpinBox()
        self.cnc_workspace_move_z_spin.setRange(-100000.0, 100000.0)
        self.cnc_workspace_move_z_spin.setDecimals(1)
        self.cnc_workspace_move_z_spin.setSingleStep(10.0)
        self.cnc_workspace_move_z_spin.setSuffix(" mm")
        self.cnc_workspace_move_z_spin.setValue(0.0)
        self.cnc_show_machine_boundary_check = QCheckBox("Show Machine Boundary")
        self.cnc_show_machine_boundary_check.setChecked(False)
        self.cnc_preview_offset_ud_spin = QDoubleSpinBox()
        self.cnc_preview_offset_ud_spin.setRange(-100000.0, 100000.0)
        self.cnc_preview_offset_ud_spin.setDecimals(1)
        self.cnc_preview_offset_ud_spin.setSingleStep(10.0)
        self.cnc_preview_offset_ud_spin.setSuffix(" mm")
        self.cnc_preview_offset_ud_spin.setValue(0.0)
        self.cnc_preview_offset_lr_spin = QDoubleSpinBox()
        self.cnc_preview_offset_lr_spin.setRange(-100000.0, 100000.0)
        self.cnc_preview_offset_lr_spin.setDecimals(1)
        self.cnc_preview_offset_lr_spin.setSingleStep(10.0)
        self.cnc_preview_offset_lr_spin.setSuffix(" mm")
        self.cnc_preview_offset_lr_spin.setValue(0.0)
        self.cnc_preview_offset_z_spin = QDoubleSpinBox()
        self.cnc_preview_offset_z_spin.setRange(-100000.0, 100000.0)
        self.cnc_preview_offset_z_spin.setDecimals(1)
        self.cnc_preview_offset_z_spin.setSingleStep(1.0)
        self.cnc_preview_offset_z_spin.setSuffix(" mm")
        self.cnc_preview_offset_z_spin.setValue(0.0)
        self.load_cnc_machine_setup_defaults()
        self._last_generated_cnc_code = ""
        self._cnc_gcode_dirty = True
        self._cnc_preview_first_open_done = False

        for spin in [self.rot_x_spin, self.rot_y_spin, self.rot_z_spin]:
            spin.setRange(-180.0, 180.0)
            spin.setWrapping(True)
            spin.setDecimals(1)
            spin.setSingleStep(1)
            spin.setKeyboardTracking(False)

        self.light_azimuth_slider.setRange(-180, 180)
        self.light_elevation_slider.setRange(-90, 90)
        self.brightness_slider.setRange(0, 250)
        self.background_width_slider.setRange(0, 5000)
        self.background_height_slider.setRange(0, 5000)
        self.light_azimuth_slider.setValue(int(round(self.ski.light_azimuth_deg)))
        self.light_elevation_slider.setValue(int(round(self.ski.light_elevation_deg)))
        self.brightness_slider.setValue(int(round(self.ski.light_brightness * 100)))
        self.background_width_slider.setValue(int(round(getattr(self.ski, "background_3d_width_px", 760.0))))
        self.background_height_slider.setValue(int(round(getattr(self.ski, "background_3d_height_px", 1280.0))))
        self.background_toggle_button.setChecked(bool(getattr(self.ski, "show_3d_background", True)))
        self.upper_mold_offset_slider.setValue(int(round(float(getattr(self.ski, "upper_mold_offset_mm", 40.0)))))
        self.mold_hole_count_slider.setValue(int(getattr(self.ski, "mold_hole_count", 4)))
        self.mold_hole_diameter_slider.setValue(int(round(float(getattr(self.ski, "mold_hole_diameter_mm", 20.0)))))

        for slider in [self.lower_reinf_slider, self.core_stiffness_slider, self.upper_reinf_slider]:
            slider.setRange(10, 300)
        self.lower_reinf_slider.setValue(int(round(self.ski.lower_reinforcement_factor * 100.0)))
        self.core_stiffness_slider.setValue(int(round(self.ski.wood_core_stiffness_factor * 100.0)))
        self.upper_reinf_slider.setValue(int(round(self.ski.upper_reinforcement_factor * 100.0)))

        for spin in [self.edge_thickness_spin, self.sidewall_thickness_spin, self.left_sidewall_thickness_spin, self.edge_inlay_tip_spin, self.edge_inlay_tail_spin, self.tip_spacer_spin, self.tail_spacer_spin, self.seam_depth_spin]:
            spin.setRange(0.0, 400.0)
            spin.setDecimals(1)
            spin.setSingleStep(1.0)
            spin.setKeyboardTracking(False)
            spin.setSuffix(" mm")

        self.base_edge_corner_radius_slider.setRange(0, 50)
        self.base_edge_corner_radius_slider.setSingleStep(1)
        self.base_edge_corner_radius_slider.setPageStep(5)

        self.minimum_core_thickness_spin.setRange(1.0, 10.0)
        self.minimum_core_thickness_spin.setDecimals(1)
        self.minimum_core_thickness_spin.setSingleStep(1.0)
        self.minimum_core_thickness_spin.setKeyboardTracking(False)
        self.minimum_core_thickness_spin.setSuffix(" mm")

        for spin in [self.tip_seam_point_count_spin, self.tail_seam_point_count_spin]:
            spin.setRange(0.0, 3.0)
            spin.setDecimals(0)
            spin.setSingleStep(1.0)
            spin.setKeyboardTracking(False)

        for spin in [self.seam_inner_x_spin, self.seam_outer_x_spin]:
            spin.setRange(5.0, 98.0)
            spin.setDecimals(0)
            spin.setSingleStep(1.0)
            spin.setKeyboardTracking(False)
            spin.setSuffix(" %")

        for spin in [self.seam_inner_y_spin, self.seam_outer_y_spin]:
            spin.setRange(-150.0, 150.0)
            spin.setDecimals(0)
            spin.setSingleStep(5.0)
            spin.setKeyboardTracking(False)
            spin.setSuffix(" %")

        for spin in [self.seam_depth_spin, self.seam_inner_x_spin, self.seam_inner_y_spin, self.seam_outer_x_spin, self.seam_outer_y_spin]:
            spin.setReadOnly(True)
            spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            spin.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        #self.seam_editor_note.setWordWrap(True)

        self.rot_x_spin.setValue(.0)
        self.rot_y_spin.setValue(-120.0)
        self.rot_z_spin.setValue(45.0)
        self.edge_thickness_spin.setValue(self.ski.edge_thickness_px)
        self.sidewall_thickness_spin.setValue(self.ski.sidewall_thickness_px)
        self.left_sidewall_thickness_spin.setValue(getattr(self.ski, "left_sidewall_thickness_px", self.ski.sidewall_thickness_px))
        self.edge_inlay_tip_spin.setValue(self.ski.edge_inlay_tip_trim_px)
        self.edge_inlay_tail_spin.setValue(self.ski.edge_inlay_tail_trim_px)
        self.base_edge_corner_radius_slider.setValue(int(round(getattr(self.ski, "base_edge_corner_min_radius_px", 0.0))))
        self.base_edge_corner_radius_value_label.setText(f"{self.base_edge_corner_radius_slider.value()} mm")
        self.splitboard_inside_edge_check.setChecked(bool(getattr(self.ski, "include_splitboard_inside_edge", True)))
        self.minimum_core_thickness_spin.setValue(getattr(self.ski, "minimum_core_thickness_px", 5.0))
        self.tip_spacer_spin.setValue(self.ski.tip_spacer_length_px)
        self.tail_spacer_spin.setValue(self.ski.tail_spacer_length_px)
        self.seam_depth_spin.setValue(self.ski.seam_depth_px)
        self.tip_seam_point_count_spin.setValue(getattr(self.ski, "tip_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.tail_seam_point_count_spin.setValue(getattr(self.ski, "tail_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.seam_inner_x_spin.setValue(getattr(self.ski, "seam_inner_x_frac", 0.34) * 100.0)
        self.seam_inner_y_spin.setValue(getattr(self.ski, "seam_inner_y_frac", 1.0) * 100.0)
        self.seam_outer_x_spin.setValue(getattr(self.ski, "seam_outer_x_frac", 0.72) * 100.0)
        self.seam_outer_y_spin.setValue(getattr(self.ski, "seam_outer_y_frac", -0.32) * 100.0)

        view_layout.addWidget(self.toggle_points_button, 0, 0)
        view_layout.addWidget(self.toggle_dimensions_button, 0, 1)
        view_layout.addWidget(self.toggle_global_coordinates_button, 1, 0)
        view_layout.addWidget(self.toggle_circle_button, 1, 1)
        view_layout.addWidget(self.toggle_stats_button, 2, 0)
        view_layout.addWidget(self.toggle_cnc_stats_button, 2, 1)
        view_layout.addWidget(self.toggle_stiffness_plot_button, 3, 0)
        view_layout.addWidget(self.toggle_interface_shortcuts_button, 3, 1)

        layer_buttons_widget = QWidget()
        layer_buttons_layout = QGridLayout(layer_buttons_widget)
        layer_buttons_layout.setContentsMargins(0, 0, 0, 0)
        layer_buttons_layout.setHorizontalSpacing(6)
        layer_buttons_layout.setVerticalSpacing(6)
        layer_buttons_layout.addWidget(self.base_toggle_button, 0, 0)
        layer_buttons_layout.addWidget(self.edge_inlay_toggle_button, 0, 1)
        layer_buttons_layout.addWidget(self.core_toggle_button, 1, 0)
        layer_buttons_layout.addWidget(self.sidewall_toggle_button, 1, 1)
        layer_buttons_layout.addWidget(self.spacer_toggle_button, 2, 0)
        layer_buttons_layout.addWidget(self.shell_toggle_button, 2, 1)

        layup_scroll_boxes_widget = QWidget()
        layup_scroll_boxes_layout = QGridLayout(layup_scroll_boxes_widget)
        layup_scroll_boxes_layout.setContentsMargins(0, 0, 0, 0)
        layup_scroll_boxes_layout.setHorizontalSpacing(6)
        layup_scroll_boxes_layout.setVerticalSpacing(6)
        layup_scroll_boxes_layout.addWidget(QLabel("Right Sidewall Thickness"), 0, 0)
        layup_scroll_boxes_layout.addWidget(self.sidewall_thickness_spin, 0, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Left Sidewall Thickness"), 1, 0)
        layup_scroll_boxes_layout.addWidget(self.left_sidewall_thickness_spin, 1, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Edge Thickness"), 2, 0)
        layup_scroll_boxes_layout.addWidget(self.edge_thickness_spin, 2, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Edge to Tip"), 3, 0)
        layup_scroll_boxes_layout.addWidget(self.edge_inlay_tip_spin, 3, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Edge to Tail"), 4, 0)
        layup_scroll_boxes_layout.addWidget(self.edge_inlay_tail_spin, 4, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Base Edge Corner Min Radius"), 5, 0)
        layup_scroll_boxes_layout.addWidget(self.base_edge_corner_radius_slider, 5, 1)
        layup_scroll_boxes_layout.addWidget(self.base_edge_corner_radius_value_label, 5, 2)
        layup_scroll_boxes_layout.addWidget(self.splitboard_inside_edge_check, 6, 0, 1, 3)
        layup_scroll_boxes_layout.addWidget(QLabel("Minimum Core Thickness"), 7, 0)
        layup_scroll_boxes_layout.addWidget(self.minimum_core_thickness_spin, 7, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Tip Spacer Length"), 8, 0)
        layup_scroll_boxes_layout.addWidget(self.tip_spacer_spin, 8, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Tail Spacer Length"), 9, 0)
        layup_scroll_boxes_layout.addWidget(self.tail_spacer_spin, 9, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Tip Seam Pts"), 10, 0)
        layup_scroll_boxes_layout.addWidget(self.tip_seam_point_count_spin, 10, 1)
        layup_scroll_boxes_layout.addWidget(QLabel("Tail Seam Pts"), 11, 0)
        layup_scroll_boxes_layout.addWidget(self.tail_seam_point_count_spin, 11, 1)

        pseudo_stiffness_widget = QWidget()
        pseudo_stiffness_layout = QGridLayout(pseudo_stiffness_widget)
        pseudo_stiffness_layout.setContentsMargins(0, 0, 0, 0)
        pseudo_stiffness_layout.setHorizontalSpacing(6)
        pseudo_stiffness_layout.setVerticalSpacing(6)
        pseudo_stiffness_layout.addWidget(QLabel("Lower Reinforcement"), 0, 0)
        pseudo_stiffness_layout.addWidget(self.lower_reinf_slider, 0, 1)
        pseudo_stiffness_layout.addWidget(self.lower_reinf_value_label, 0, 2)
        pseudo_stiffness_layout.addWidget(QLabel("Core Stiffness"), 1, 0)
        pseudo_stiffness_layout.addWidget(self.core_stiffness_slider, 1, 1)
        pseudo_stiffness_layout.addWidget(self.core_stiffness_value_label, 1, 2)
        pseudo_stiffness_layout.addWidget(QLabel("Upper Reinforcement"), 2, 0)
        pseudo_stiffness_layout.addWidget(self.upper_reinf_slider, 2, 1)
        pseudo_stiffness_layout.addWidget(self.upper_reinf_value_label, 2, 2)

        build_sheet_notes_widget = QWidget()
        build_sheet_notes_layout = QGridLayout(build_sheet_notes_widget)
        build_sheet_notes_layout.setContentsMargins(0, 0, 0, 0)
        build_sheet_notes_layout.setHorizontalSpacing(6)
        build_sheet_notes_layout.setVerticalSpacing(6)
        for row, (key, label) in enumerate(BUILD_SHEET_NOTE_FIELDS):
            label_widget = QLabel(label)
            label_widget.setWordWrap(True)
            editor = QTextEdit()
            editor.setObjectName("buildSheetNoteEditor")
            editor.setAcceptRichText(False)
            editor.setFixedHeight(62)
            editor.setMaximumWidth(220)
            editor.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            editor.setStyleSheet("#buildSheetNoteEditor { min-height: 62px; max-height: 62px; }")
            self.build_sheet_note_editors[key] = editor
            build_sheet_notes_layout.addWidget(label_widget, row, 0)
            build_sheet_notes_layout.addWidget(editor, row, 1)

        self.layup_layers_panel = CollapsiblePanel("Layers", layer_buttons_widget, expanded=False)
        self.layup_scroll_boxes_panel = CollapsiblePanel("Layer Adjustments", layup_scroll_boxes_widget, expanded=False)
        self.build_sheet_notes_panel = CollapsiblePanel("Build Sheet Inputs", build_sheet_notes_widget, expanded=False)
        self.pseudo_stiffness_panel = CollapsiblePanel("Pseudo-stiffness Sliders", pseudo_stiffness_widget, expanded=False)

        layup_layout.addWidget(self.layup_layers_panel, 0, 0, 1, 3)
        layup_layout.addWidget(self.layup_scroll_boxes_panel, 1, 0, 1, 3)
        layup_layout.addWidget(self.build_sheet_notes_panel, 2, 0, 1, 3)
        layup_layout.addWidget(self.pseudo_stiffness_panel, 3, 0, 1, 3)
        #layup_layout.addWidget(self.seam_editor_note, 17, 0, 1, 3)

        mold_layout.addWidget(QLabel("Upper Mold Offset"), 0, 0)
        mold_layout.addWidget(self.upper_mold_offset_slider, 0, 1)
        mold_layout.addWidget(self.upper_mold_offset_value_label, 0, 2)
        mold_layout.addWidget(QLabel("Number of Holes"), 1, 0)
        mold_layout.addWidget(self.mold_hole_count_slider, 1, 1)
        mold_layout.addWidget(self.mold_hole_count_value_label, 1, 2)
        mold_layout.addWidget(QLabel("Hole Diameter"), 2, 0)
        mold_layout.addWidget(self.mold_hole_diameter_slider, 2, 1)
        mold_layout.addWidget(self.mold_hole_diameter_value_label, 2, 2)

        lighting_layout.addWidget(self.view_style_shaded_button, 0, 0)
        lighting_layout.addWidget(self.view_style_edges_button, 0, 1)
        lighting_layout.addWidget(self.view_style_wire_button, 0, 2)
        lighting_layout.addWidget(self.view_style_graphic_button, 0, 3)
        lighting_layout.addWidget(QLabel("Roll"), 1, 0)
        lighting_layout.addWidget(self.rot_x_spin, 1, 1, 1, 3)
        lighting_layout.addWidget(QLabel("Butter"), 2, 0)
        lighting_layout.addWidget(self.rot_y_spin, 2, 1, 1, 3)
        lighting_layout.addWidget(QLabel("Spin"), 3, 0)
        lighting_layout.addWidget(self.rot_z_spin, 3, 1, 1, 3)
        lighting_layout.addWidget(self.view_home_button, 4, 0)
        lighting_layout.addWidget(self.view_front_button, 4, 1)
        lighting_layout.addWidget(self.view_top_button, 4, 2)
        lighting_layout.addWidget(self.view_side_button, 4, 3)
        lighting_layout.addWidget(self.save_3d_position_button, 5, 0, 1, 2)
        lighting_layout.addWidget(self.load_3d_position_button, 5, 2, 1, 2)
        lighting_layout.addWidget(self.second_ski_layout_button, 6, 0, 1, 4)
        lighting_layout.addWidget(self.mouse_input_settings_button, 7, 0, 1, 4)
        lighting_layout.addWidget(self.pick_3d_color_button, 8, 0, 1, 2)
        lighting_layout.addWidget(self.pick_3d_background_color_button, 8, 2, 1, 2)
        lighting_layout.addWidget(self.background_toggle_button, 9, 0, 1, 4)
        lighting_layout.addWidget(self.second_ski_spacing_label, 10, 0)
        lighting_layout.addWidget(self.second_ski_spacing_slider, 10, 1, 1, 2)
        lighting_layout.addWidget(self.second_ski_spacing_value_label, 10, 3)
        lighting_layout.addWidget(QLabel("Light Azimuth"), 11, 0)
        lighting_layout.addWidget(self.light_azimuth_slider, 11, 1, 1, 2)
        lighting_layout.addWidget(self.light_azimuth_value_label, 11, 3)
        lighting_layout.addWidget(QLabel("Light Elevation"), 12, 0)
        lighting_layout.addWidget(self.light_elevation_slider, 12, 1, 1, 2)
        lighting_layout.addWidget(self.light_elevation_value_label, 12, 3)
        lighting_layout.addWidget(QLabel("Brightness"), 13, 0)
        lighting_layout.addWidget(self.brightness_slider, 13, 1, 1, 2)
        lighting_layout.addWidget(self.brightness_value_label, 13, 3)
        lighting_layout.addWidget(self.background_width_text_label, 14, 0)
        lighting_layout.addWidget(self.background_width_slider, 14, 1, 1, 2)
        lighting_layout.addWidget(self.background_width_value_label, 14, 3)
        lighting_layout.addWidget(self.background_height_text_label, 15, 0)
        lighting_layout.addWidget(self.background_height_slider, 15, 1, 1, 2)
        lighting_layout.addWidget(self.background_height_value_label, 15, 3)

        two_d_appearance_layout.addWidget(self.toggle_second_ski_button, 0, 0, 1, 3)
        two_d_appearance_layout.addWidget(self.load_right_graphic_button, 1, 0, 1, 3)
        two_d_appearance_layout.addWidget(self.load_left_graphic_button, 2, 0, 1, 3)
        two_d_appearance_layout.addWidget(QLabel("Graphic"), 3, 0)
        two_d_appearance_layout.addWidget(self.two_d_graphic_target_combo, 3, 1, 1, 2)
        two_d_appearance_layout.addWidget(QLabel("X Offset"), 4, 0)
        two_d_appearance_layout.addWidget(self.two_d_graphic_offset_x_slider, 4, 1)
        two_d_appearance_layout.addWidget(self.two_d_graphic_offset_x_value_label, 4, 2)
        two_d_appearance_layout.addWidget(QLabel("Y Offset"), 5, 0)
        two_d_appearance_layout.addWidget(self.two_d_graphic_offset_y_slider, 5, 1)
        two_d_appearance_layout.addWidget(self.two_d_graphic_offset_y_value_label, 5, 2)
        two_d_appearance_layout.addWidget(QLabel("Scale X"), 6, 0)
        two_d_appearance_layout.addWidget(self.two_d_graphic_scale_x_slider, 6, 1)
        two_d_appearance_layout.addWidget(self.two_d_graphic_scale_x_value_label, 6, 2)
        two_d_appearance_layout.addWidget(QLabel("Scale Y"), 7, 0)
        two_d_appearance_layout.addWidget(self.two_d_graphic_scale_y_slider, 7, 1)
        two_d_appearance_layout.addWidget(self.two_d_graphic_scale_y_value_label, 7, 2)

        self.cnc_ramp_angle_label = QLabel("Ramp Angle")
        self.cnc_ramp_feed_rate_label = QLabel("Ramp Speed")
        self.cnc_tool_diameter_label = QLabel("Mill Diameter")
        self.cnc_safety_z_label = QLabel("Safety Retract")
        self.cnc_cut_depth_label = QLabel("Cut Depth")
        self.cnc_stepdown_label = QLabel("Stepdown")
        self.cnc_feed_rate_label = QLabel("Feed Rate")
        self.cnc_plunge_rate_label = QLabel("Plunge Rate")
        self.cnc_spindle_label = QLabel("Spindle")
        self.cnc_helix_angle_label = QLabel("Helix Angle")

        selectable_shapes_widget = QWidget()
        selectable_shapes_layout = QVBoxLayout(selectable_shapes_widget)
        selectable_shapes_layout.setContentsMargins(0, 0, 0, 0)
        selectable_shapes_layout.setSpacing(6)
        selectable_shapes_layout.addLayout(self.cnc_shape_grid)

        snap_to_view_widget = QWidget()
        snap_to_view_layout = QGridLayout(snap_to_view_widget)
        snap_to_view_layout.setContentsMargins(0, 0, 0, 0)
        snap_to_view_layout.setHorizontalSpacing(6)
        snap_to_view_layout.setVerticalSpacing(6)
        snap_to_view_layout.addWidget(self.cnc_snap_home_button, 0, 0)
        snap_to_view_layout.addWidget(self.cnc_snap_front_button, 0, 1)
        snap_to_view_layout.addWidget(self.cnc_snap_top_button, 1, 0)
        snap_to_view_layout.addWidget(self.cnc_snap_side_button, 1, 1)
        snap_to_view_layout.addWidget(self.cnc_recenter_button, 2, 0)
        snap_to_view_layout.addWidget(self.cnc_rescale_button, 2, 1)
        snap_to_view_layout.addWidget(self.cnc_save_view_button, 3, 0, 1, 2)
        snap_to_view_layout.addWidget(self.cnc_load_view_button, 4, 0)
        snap_to_view_layout.addWidget(self.cnc_custom_2_view_button, 4, 1)

        machine_setup_widget = QWidget()
        machine_setup_layout = QGridLayout(machine_setup_widget)
        machine_setup_layout.setContentsMargins(0, 0, 0, 0)
        machine_setup_layout.setHorizontalSpacing(6)
        machine_setup_layout.setVerticalSpacing(6)
        machine_setup_layout.addWidget(self.cnc_show_machine_boundary_check, 0, 0, 1, 2)
        machine_setup_layout.addWidget(QLabel("Workspace X"), 1, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_x_spin, 1, 1)
        machine_setup_layout.addWidget(QLabel("Workspace Y"), 2, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_y_spin, 2, 1)
        machine_setup_layout.addWidget(QLabel("Workspace Z"), 3, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_z_spin, 3, 1)
        machine_setup_layout.addWidget(QLabel("Move X"), 4, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_move_x_spin, 4, 1)
        machine_setup_layout.addWidget(QLabel("Move Y"), 5, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_move_y_spin, 5, 1)
        machine_setup_layout.addWidget(QLabel("Move Z"), 6, 0)
        machine_setup_layout.addWidget(self.cnc_workspace_move_z_spin, 6, 1)


        toolpath_params_widget = QWidget()
        toolpath_params_layout = QGridLayout(toolpath_params_widget)
        toolpath_params_layout.setContentsMargins(0, 0, 0, 0)
        toolpath_params_layout.setHorizontalSpacing(6)
        toolpath_params_layout.setVerticalSpacing(6)
        toolpath_params_layout.addWidget(QLabel("Operation"), 0, 0)
        toolpath_params_layout.addWidget(self.cnc_operation_combo, 0, 1)
        toolpath_params_layout.addWidget(QLabel("Preview Colors"), 1, 0)
        toolpath_params_layout.addWidget(self.cnc_preview_color_mode_combo, 1, 1)
        toolpath_params_layout.addWidget(QLabel("Move Toolpath X"), 2, 0)
        toolpath_params_layout.addWidget(self.cnc_preview_offset_lr_spin, 2, 1)
        toolpath_params_layout.addWidget(QLabel("Move Toolpath Y"), 3, 0)
        toolpath_params_layout.addWidget(self.cnc_preview_offset_ud_spin, 3, 1)
        toolpath_params_layout.addWidget(QLabel("Move Toolpath Z"), 4, 0)
        toolpath_params_layout.addWidget(self.cnc_preview_offset_z_spin, 4, 1)
        toolpath_params_layout.addWidget(self.cnc_depth_profile_invert_check, 5, 0, 1, 2)
        toolpath_params_layout.addWidget(self.cnc_depth_mode_check, 6, 0, 1, 2)
        toolpath_params_layout.addWidget(self.cnc_ramp_entry_check, 7, 0, 1, 2)
        toolpath_params_layout.addWidget(self.cnc_duplicate_check, 8, 0, 1, 2)
        toolpath_params_layout.addWidget(QLabel("Duplicate X Offset"), 9, 0)
        toolpath_params_layout.addWidget(self.cnc_duplicate_x_spin, 9, 1)
        toolpath_params_layout.addWidget(QLabel("Duplicate Y Offset"), 10, 0)
        toolpath_params_layout.addWidget(self.cnc_duplicate_y_spin, 10, 1)
        toolpath_params_layout.addWidget(self.cnc_ramp_angle_label, 11, 0)
        toolpath_params_layout.addWidget(self.cnc_ramp_angle_spin, 11, 1)
        toolpath_params_layout.addWidget(self.cnc_ramp_feed_rate_label, 12, 0)
        toolpath_params_layout.addWidget(self.cnc_ramp_feed_rate_spin, 12, 1)
        toolpath_params_layout.addWidget(self.cnc_tool_diameter_label, 13, 0)
        toolpath_params_layout.addWidget(self.cnc_tool_diameter_spin, 13, 1)
        toolpath_params_layout.addWidget(self.cnc_safety_z_label, 14, 0)
        toolpath_params_layout.addWidget(self.cnc_safety_z_spin, 14, 1)
        toolpath_params_layout.addWidget(self.cnc_cut_depth_label, 15, 0)
        toolpath_params_layout.addWidget(self.cnc_cut_depth_spin, 15, 1)
        toolpath_params_layout.addWidget(self.cnc_stepdown_label, 16, 0)
        toolpath_params_layout.addWidget(self.cnc_stepdown_spin, 16, 1)
        toolpath_params_layout.addWidget(self.cnc_feed_rate_label, 17, 0)
        toolpath_params_layout.addWidget(self.cnc_feed_rate_spin, 17, 1)
        toolpath_params_layout.addWidget(self.cnc_plunge_rate_label, 18, 0)
        toolpath_params_layout.addWidget(self.cnc_plunge_rate_spin, 18, 1)
        toolpath_params_layout.addWidget(self.cnc_spindle_label, 19, 0)
        toolpath_params_layout.addWidget(self.cnc_spindle_spin, 19, 1)
        toolpath_params_layout.addWidget(self.cnc_helix_angle_label, 20, 0)
        toolpath_params_layout.addWidget(self.cnc_helix_angle_spin, 20, 1)

        self.cnc_selectable_shapes_panel = CollapsiblePanel("Selectable Shapes", selectable_shapes_widget, expanded=False)
        self.cnc_snap_to_view_panel = CollapsiblePanel("Snap to View", snap_to_view_widget, expanded=False)
        self.cnc_machine_setup_panel = CollapsiblePanel("Machine Setup", machine_setup_widget, expanded=False)
        self.cnc_toolpath_params_panel = CollapsiblePanel("Toolpath Parameters", toolpath_params_widget, expanded=False)

        cnc_layout.addWidget(self.cnc_selectable_shapes_panel, 0, 0, 1, 2)
        cnc_layout.addWidget(self.cnc_snap_to_view_panel, 1, 0, 1, 2)
        cnc_layout.addWidget(self.cnc_machine_setup_panel, 2, 0, 1, 2)
        cnc_layout.addWidget(self.cnc_toolpath_params_panel, 3, 0, 1, 2)
        self.cnc_3d_preview_widget.hide()
        cnc_layout.addWidget(self.cnc_preview, 4, 0, 1, 2)
        cnc_layout.addWidget(self.generate_gcode_button, 5, 0)
        cnc_layout.addWidget(self.save_gcode_button, 5, 1)

        self.edge_thickness_spin.setValue(self.ski.edge_thickness_px)
        self.sidewall_thickness_spin.setValue(self.ski.sidewall_thickness_px)
        self.left_sidewall_thickness_spin.setValue(getattr(self.ski, "left_sidewall_thickness_px", self.ski.sidewall_thickness_px))
        self.edge_inlay_tip_spin.setValue(self.ski.edge_inlay_tip_trim_px)
        self.edge_inlay_tail_spin.setValue(self.ski.edge_inlay_tail_trim_px)
        self.base_edge_corner_radius_slider.setValue(int(round(getattr(self.ski, "base_edge_corner_min_radius_px", 0.0))))
        self.base_edge_corner_radius_value_label.setText(f"{self.base_edge_corner_radius_slider.value()} mm")
        self.splitboard_inside_edge_check.setChecked(bool(getattr(self.ski, "include_splitboard_inside_edge", True)))
        self.minimum_core_thickness_spin.setValue(getattr(self.ski, "minimum_core_thickness_px", 5.0))
        self.tip_spacer_spin.setValue(self.ski.tip_spacer_length_px)
        self.tail_spacer_spin.setValue(self.ski.tail_spacer_length_px)
        self.seam_depth_spin.setValue(self.ski.seam_depth_px)
        self.tip_seam_point_count_spin.setValue(getattr(self.ski, "tip_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.tail_seam_point_count_spin.setValue(getattr(self.ski, "tail_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.seam_inner_x_spin.setValue(getattr(self.ski, "seam_inner_x_frac", 0.34) * 100.0)
        self.seam_inner_y_spin.setValue(getattr(self.ski, "seam_inner_y_frac", 1.0) * 100.0)
        self.seam_outer_x_spin.setValue(getattr(self.ski, "seam_outer_x_frac", 0.72) * 100.0)
        self.seam_outer_y_spin.setValue(getattr(self.ski, "seam_outer_y_frac", -0.32) * 100.0)

        self.build_file_menu()
        self._sync_second_ski_layout_button()
        self.build_cnc_menu()
        self.build_help_menu()

        for group in (view_group, layup_group, mold_group, two_d_appearance_group, lighting_group, cnc_group):
            group.setFlat(True)
            group.setStyleSheet("QGroupBox { border: none; margin-top: 0; padding-top: 6px; background-color: transparent; } QGroupBox::title { subcontrol-origin: margin; left: 0px; padding: 0; }")

        self.view_panel = CollapsiblePanel("View", view_group, expanded=False)
        self.layup_panel = CollapsiblePanel("Layup", layup_group, expanded=False)
        self.mold_panel = CollapsiblePanel("Mold", mold_group, expanded=False)
        self.two_d_appearance_panel = CollapsiblePanel("2D Appearance", two_d_appearance_group, expanded=False)
        self.appearance_panel = CollapsiblePanel("3D Appearance", lighting_group, expanded=False)
        self.cnc_panel = CollapsiblePanel("CNC Toolpaths", cnc_group, expanded=False)
        self.cnc_panel.toggle_button.toggled.connect(self._on_cnc_panel_toggled)
        sidebar_layout.addWidget(self.view_panel)
        sidebar_layout.addWidget(self.layup_panel)
        sidebar_layout.addWidget(self.mold_panel)
        sidebar_layout.addWidget(self.two_d_appearance_panel)
        sidebar_layout.addWidget(self.appearance_panel)
        sidebar_layout.addWidget(self.cnc_panel)
        sidebar_layout.addStretch(1)
        sidebar.setWidget(sidebar_contents)

        self.main_splitter.addWidget(sidebar)
        self.main_splitter.addWidget(self.view_container)
        self.main_splitter.setSizes([430, 1200])
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)

        self.toggle_points_button.clicked.connect(self.toggle_points)
        self.toggle_dimensions_button.clicked.connect(self.toggle_dimensions)
        self.toggle_circle_button.clicked.connect(self.toggle_circle)
        self.toggle_global_coordinates_button.clicked.connect(self.toggle_global_coordinates)
        self.toggle_stiffness_plot_button.clicked.connect(self.toggle_stiffness_plot)
        self.toggle_stats_button.clicked.connect(self.toggle_stats)
        self.toggle_cnc_stats_button.clicked.connect(self.toggle_cnc_stats)
        self.toggle_interface_shortcuts_button.clicked.connect(self.toggle_interface_shortcuts)
        self.appearance_panel.toggle_button.toggled.connect(self.on_appearance_panel_toggled)
        self.view_style_shaded_button.clicked.connect(lambda: self.set_3d_view_style("shaded"))
        self.view_style_edges_button.clicked.connect(lambda: self.set_3d_view_style("shaded_edges"))
        self.view_style_wire_button.clicked.connect(lambda: self.set_3d_view_style("wireframe"))
        self.view_style_graphic_button.clicked.connect(lambda: self.set_3d_view_style("graphic"))
        self.view_home_button.clicked.connect(self.set_home_view)
        self.fit_whole_view_button.clicked.connect(self.recenter_rescale_whole_view)
        self.save_whole_view_button.clicked.connect(self.save_whole_view_target)
        self.view_front_button.clicked.connect(self.set_front_view)
        self.view_top_button.clicked.connect(self.set_top_view)
        self.view_side_button.clicked.connect(self.set_side_view)
        self.save_3d_position_button.clicked.connect(self.save_3d_position)
        self.load_3d_position_button.clicked.connect(self.load_3d_position)
        self.toggle_second_ski_button.clicked.connect(self.toggle_ski_snowboard)
        self.load_right_graphic_button.clicked.connect(self.toggle_or_prompt_top_graphic)
        self.load_left_graphic_button.clicked.connect(self.toggle_or_prompt_base_graphic)
        self.second_ski_layout_button.clicked.connect(self.toggle_second_3d_layout)
        self.mouse_input_settings_button.clicked.connect(self.show_mouse_input_settings_dialog)
        self.pick_3d_color_button.clicked.connect(self.pick_3d_color)
        self.pick_3d_background_color_button.clicked.connect(self.pick_3d_background_color)
        self.second_ski_spacing_slider.valueChanged.connect(self.update_second_ski_spacing_controls)
        self.two_d_graphic_target_combo.currentIndexChanged.connect(self.sync_2d_graphic_controls_from_model)
        self.two_d_graphic_offset_x_slider.valueChanged.connect(self.update_2d_graphic_controls)
        self.two_d_graphic_offset_y_slider.valueChanged.connect(self.update_2d_graphic_controls)
        self.two_d_graphic_scale_x_slider.valueChanged.connect(self.update_2d_graphic_controls)
        self.two_d_graphic_scale_y_slider.valueChanged.connect(self.update_2d_graphic_controls)
        self.upper_mold_offset_slider.valueChanged.connect(self.update_mold_controls)
        self.mold_hole_count_slider.valueChanged.connect(self.update_mold_controls)
        self.mold_hole_diameter_slider.valueChanged.connect(self.update_mold_controls)
        self.base_toggle_button.clicked.connect(self.toggle_base_shape)
        self.edge_inlay_toggle_button.clicked.connect(self.toggle_edge_inlay_shape)
        self.core_toggle_button.clicked.connect(self.toggle_core_shape)
        self.sidewall_toggle_button.clicked.connect(self.toggle_sidewall_shape)
        self.spacer_toggle_button.clicked.connect(self.toggle_spacer_shapes)
        self.shell_toggle_button.clicked.connect(self.toggle_sidewall_spacer_shell)
        for editor in self.build_sheet_note_editors.values():
            editor.textChanged.connect(self.update_build_sheet_notes_from_fields)

        self.rot_x_spin.valueChanged.connect(self.update_rot)
        self.rot_y_spin.valueChanged.connect(self.update_rot)
        self.rot_z_spin.valueChanged.connect(self.update_rot)
        self.light_azimuth_slider.valueChanged.connect(self.update_light_controls)
        self.light_elevation_slider.valueChanged.connect(self.update_light_controls)
        self.brightness_slider.valueChanged.connect(self.update_light_controls)
        self.background_width_slider.valueChanged.connect(self.update_3d_background_controls)
        self.background_height_slider.valueChanged.connect(self.update_3d_background_controls)
        self.background_toggle_button.clicked.connect(self.toggle_3d_background)
        self.generate_gcode_button.clicked.connect(self.generate_cnc_gcode)
        self.save_gcode_button.clicked.connect(self.save_cnc_gcode)
        self.cnc_snap_home_button.clicked.connect(self.set_cnc_home_view)
        self.cnc_snap_front_button.clicked.connect(self.set_cnc_front_view)
        self.cnc_snap_top_button.clicked.connect(self.set_cnc_top_view)
        self.cnc_snap_side_button.clicked.connect(self.set_cnc_side_view)
        self.cnc_recenter_button.clicked.connect(self.recenter_cnc_preview_view)
        self.cnc_rescale_button.clicked.connect(self.rescale_cnc_preview_view)
        self.cnc_save_view_button.clicked.connect(self.save_cnc_preview_view)
        self.cnc_load_view_button.clicked.connect(lambda: self.load_cnc_preview_view(1))
        self.cnc_custom_2_view_button.clicked.connect(lambda: self.load_cnc_preview_view(2))
        self.cnc_operation_combo.currentIndexChanged.connect(self._on_cnc_toolpath_geometry_changed)
        self.cnc_preview_color_mode_combo.currentIndexChanged.connect(self._on_cnc_preview_settings_changed)
        self.cnc_depth_mode_check.toggled.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_depth_profile_invert_check.toggled.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_ramp_entry_check.toggled.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_ramp_angle_spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_ramp_feed_rate_spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_helix_angle_spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_tool_diameter_spin.valueChanged.connect(self._on_cnc_toolpath_geometry_changed)
        for spin in [self.cnc_safety_z_spin, self.cnc_start_x_spin, self.cnc_start_y_spin, self.cnc_workspace_x_spin, self.cnc_workspace_y_spin, self.cnc_workspace_z_spin, self.cnc_cut_depth_spin, self.cnc_stepdown_spin, self.cnc_feed_rate_spin, self.cnc_plunge_rate_spin, self.cnc_spindle_spin]:
            spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        for spin in [self.cnc_workspace_move_x_spin, self.cnc_workspace_move_y_spin, self.cnc_workspace_move_z_spin, self.cnc_preview_offset_ud_spin, self.cnc_preview_offset_lr_spin, self.cnc_preview_offset_z_spin, self.cnc_duplicate_x_spin, self.cnc_duplicate_y_spin]:
            spin.valueChanged.connect(self._on_cnc_preview_settings_changed)
        for spin in [self.cnc_preview_offset_ud_spin, self.cnc_preview_offset_lr_spin, self.cnc_preview_offset_z_spin]:
            spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_show_machine_boundary_check.toggled.connect(self._on_cnc_preview_settings_changed)
        self.cnc_duplicate_check.toggled.connect(self._on_cnc_preview_settings_changed)
        self.cnc_duplicate_check.toggled.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_duplicate_x_spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.cnc_duplicate_y_spin.valueChanged.connect(self._on_cnc_gcode_settings_changed)
        self.edge_thickness_spin.valueChanged.connect(self.update_layup_controls)
        self.sidewall_thickness_spin.valueChanged.connect(self.update_layup_controls)
        self.left_sidewall_thickness_spin.valueChanged.connect(self.update_layup_controls)
        self.edge_inlay_tip_spin.valueChanged.connect(self.update_layup_controls)
        self.edge_inlay_tail_spin.valueChanged.connect(self.update_layup_controls)
        self.base_edge_corner_radius_slider.valueChanged.connect(self.update_layup_controls)
        self.splitboard_inside_edge_check.toggled.connect(self.update_layup_controls)
        self.minimum_core_thickness_spin.valueChanged.connect(self.update_layup_controls)
        self.tip_spacer_spin.valueChanged.connect(self.update_layup_controls)
        self.tail_spacer_spin.valueChanged.connect(self.update_layup_controls)
        self.tip_seam_point_count_spin.valueChanged.connect(self.update_layup_controls)
        self.tail_seam_point_count_spin.valueChanged.connect(self.update_layup_controls)
        self.lower_reinf_slider.valueChanged.connect(self.update_stiffness_controls)
        self.core_stiffness_slider.valueChanged.connect(self.update_stiffness_controls)
        self.upper_reinf_slider.valueChanged.connect(self.update_stiffness_controls)

        self.sync_2d_graphic_controls_from_model()
        self.update_rot()
        self.update_light_controls()
        if hasattr(self, "second_ski_spacing_slider"):
            self.second_ski_spacing_slider.blockSignals(True)
            self.second_ski_spacing_slider.setValue(int(round(float(getattr(self.ski, "second_3d_base_separation_cm", 7.5)) * 10.0)))
            self.second_ski_spacing_slider.blockSignals(False)
        self._sync_second_ski_layout_button()
        self.update_3d_background_controls()
        self.update_stiffness_controls()
        self.update_mold_controls()
        self.sync_build_sheet_note_fields_from_model()
        self.refresh_layup_toggle_labels()
        self.refresh_splitboard_inside_edge_controls()
        self.refresh_3d_view_style_buttons()
        self._update_cnc_operation_dependent_visibility()
        self._mark_cnc_gcode_dirty()
        self.sync_seam_editor_widgets()
        self._startup_initializing = False
        QTimer.singleShot(0, self._finish_startup_cnc_setup)
    def _get_selected_2d_graphic_key(self):
        index = int(self.two_d_graphic_target_combo.currentIndex()) if hasattr(self, "two_d_graphic_target_combo") else 0
        return "base" if index == 1 else "top"

    def sync_build_sheet_note_fields_from_model(self):
        if not hasattr(self, "build_sheet_note_editors"):
            return
        notes = default_build_sheet_notes()
        saved_notes = getattr(self.ski, "build_sheet_notes", {}) if hasattr(self, "ski") else {}
        if isinstance(saved_notes, dict):
            for key in notes:
                notes[key] = str(saved_notes.get(key, ""))
        for key, editor in self.build_sheet_note_editors.items():
            editor.blockSignals(True)
            editor.setPlainText(notes.get(key, ""))
            editor.blockSignals(False)

    def update_build_sheet_notes_from_fields(self):
        if not hasattr(self, "ski") or self.ski is None:
            return
        self.ski.build_sheet_notes = {
            key: editor.toPlainText().strip()
            for key, editor in getattr(self, "build_sheet_note_editors", {}).items()
        }

    def sync_2d_graphic_controls_from_model(self):
        if not hasattr(self, "ski") or self.ski is None:
            return
        key = self._get_selected_2d_graphic_key()
        if key == "base":
            x_value = float(getattr(self.ski, "base_graphic_offset_x_px", 0.0))
            y_value = float(getattr(self.ski, "base_graphic_offset_y_px", 0.0))
            scale_x_value = float(getattr(self.ski, "base_graphic_scale_x", getattr(self.ski, "base_graphic_scale", 1.0)))
            scale_y_value = float(getattr(self.ski, "base_graphic_scale_y", getattr(self.ski, "base_graphic_scale", 1.0)))
        else:
            x_value = float(getattr(self.ski, "top_graphic_offset_x_px", 0.0))
            y_value = float(getattr(self.ski, "top_graphic_offset_y_px", 0.0))
            scale_x_value = float(getattr(self.ski, "top_graphic_scale_x", getattr(self.ski, "top_graphic_scale", 1.0)))
            scale_y_value = float(getattr(self.ski, "top_graphic_scale_y", getattr(self.ski, "top_graphic_scale", 1.0)))

        for slider, value in (
            (self.two_d_graphic_offset_x_slider, int(round(x_value))),
            (self.two_d_graphic_offset_y_slider, int(round(y_value))),
            (self.two_d_graphic_scale_x_slider, int(round(scale_x_value * 100.0))),
            (self.two_d_graphic_scale_y_slider, int(round(scale_y_value * 100.0))),
        ):
            slider.blockSignals(True)
            slider.setValue(value)
            slider.blockSignals(False)
        self._refresh_2d_graphic_value_labels()

    def _refresh_2d_graphic_value_labels(self):
        if not hasattr(self, "two_d_graphic_offset_x_value_label"):
            return
        self.two_d_graphic_offset_x_value_label.setText(f"{int(self.two_d_graphic_offset_x_slider.value())} px")
        self.two_d_graphic_offset_y_value_label.setText(f"{int(self.two_d_graphic_offset_y_slider.value())} px")
        self.two_d_graphic_scale_x_value_label.setText(f"{self.two_d_graphic_scale_x_slider.value() / 100.0:.2f}x")
        self.two_d_graphic_scale_y_value_label.setText(f"{self.two_d_graphic_scale_y_slider.value() / 100.0:.2f}x")

    def update_2d_graphic_controls(self):
        if not hasattr(self, "ski") or self.ski is None:
            return
        key = self._get_selected_2d_graphic_key()
        x_value = float(self.two_d_graphic_offset_x_slider.value())
        y_value = float(self.two_d_graphic_offset_y_slider.value())
        scale_x_value = max(0.01, float(self.two_d_graphic_scale_x_slider.value()) / 100.0)
        scale_y_value = max(0.01, float(self.two_d_graphic_scale_y_slider.value()) / 100.0)
        if key == "base":
            self.ski.base_graphic_offset_x_px = x_value
            self.ski.base_graphic_offset_y_px = y_value
            self.ski.base_graphic_scale_x = scale_x_value
            self.ski.base_graphic_scale_y = scale_y_value
        else:
            self.ski.top_graphic_offset_x_px = x_value
            self.ski.top_graphic_offset_y_px = y_value
            self.ski.top_graphic_scale_x = scale_x_value
            self.ski.top_graphic_scale_y = scale_y_value
        self._refresh_2d_graphic_value_labels()
        self.ski.update()
        self.view.viewport().update()

    def build_file_menu(self):
        file_menu = self.menu_bar.addMenu("File")

        self.save_action = QAction("Save", self)
        self.load_action = QAction("Load", self)
        self.export_build_sheet_action = QAction("Export Build Sheet PDF", self)
        self.export_svg_action = QAction("Export SVG", self)
        self.export_dxf_action = QAction("Export DXF", self)
        self.export_stl_action = QAction("Export STL", self)
        self.exit_action = QAction("Exit", self)

        for action in [
            self.save_action,
            self.load_action,
            None,
            self.export_build_sheet_action,
            self.export_svg_action,
            self.export_dxf_action,
            self.export_stl_action,
            None,
            self.exit_action,
        ]:
            if action is None:
                file_menu.addSeparator()
            else:
                file_menu.addAction(action)

        self.save_action.triggered.connect(self.save_file)
        self.load_action.triggered.connect(self.load_file)
        self.export_build_sheet_action.triggered.connect(self.export_build_sheet_pdf_file)
        self.export_svg_action.triggered.connect(self.export_svg_file)
        self.export_dxf_action.triggered.connect(self.export_dxf_file)
        self.export_stl_action.triggered.connect(self.export_stl_file)
        self.exit_action.triggered.connect(self.confirm_exit)
    def _cnc_machine_setup_defaults_path(self):
        try:
            home = Path.home()
            return home / ".ski_design_cnc_machine_setup_defaults.json"
        except Exception:
            return None

    def get_cnc_machine_setup_settings(self):
        return {
            "start_x": float(self.cnc_start_x_spin.value()),
            "start_y": float(self.cnc_start_y_spin.value()),
            "workspace_x": float(self.cnc_workspace_x_spin.value()),
            "workspace_y": float(self.cnc_workspace_y_spin.value()),
            "workspace_z": float(self.cnc_workspace_z_spin.value()),
            "workspace_move_x": float(self.cnc_workspace_move_x_spin.value()),
            "workspace_move_y": float(self.cnc_workspace_move_y_spin.value()),
            "workspace_move_z": float(self.cnc_workspace_move_z_spin.value()),
            "show_machine_boundary": bool(self.cnc_show_machine_boundary_check.isChecked()),
            "preview_offset_ud": float(self.cnc_preview_offset_ud_spin.value()),
            "preview_offset_lr": float(self.cnc_preview_offset_lr_spin.value()),
            "preview_offset_z": float(self.cnc_preview_offset_z_spin.value()),
            "duplicate_enabled": bool(self.cnc_duplicate_check.isChecked()),
            "duplicate_x": float(self.cnc_duplicate_x_spin.value()),
            "duplicate_y": float(self.cnc_duplicate_y_spin.value()),
            "mirror_depth_profile_horizontally": bool(self.cnc_depth_profile_invert_check.isChecked()),
        }

    def apply_cnc_machine_setup_settings(self, settings, mark_dirty=True):
        if not isinstance(settings, dict):
            return False
        mapping = (
            (self.cnc_start_x_spin, "start_x"),
            (self.cnc_start_y_spin, "start_y"),
            (self.cnc_workspace_x_spin, "workspace_x"),
            (self.cnc_workspace_y_spin, "workspace_y"),
            (self.cnc_workspace_z_spin, "workspace_z"),
            (self.cnc_workspace_move_x_spin, "workspace_move_x"),
            (self.cnc_workspace_move_y_spin, "workspace_move_y"),
            (self.cnc_workspace_move_z_spin, "workspace_move_z"),
            (self.cnc_preview_offset_ud_spin, "preview_offset_ud"),
            (self.cnc_preview_offset_lr_spin, "preview_offset_lr"),
            (self.cnc_preview_offset_z_spin, "preview_offset_z"),
            (self.cnc_duplicate_x_spin, "duplicate_x"),
            (self.cnc_duplicate_y_spin, "duplicate_y"),
        )
        for spin, key in mapping:
            if key not in settings:
                continue
            try:
                value = float(settings[key])
            except Exception:
                continue
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)

        if "duplicate_enabled" in settings:
            self.cnc_duplicate_check.blockSignals(True)
            self.cnc_duplicate_check.setChecked(bool(settings.get("duplicate_enabled", False)))
            self.cnc_duplicate_check.blockSignals(False)

        if "mirror_depth_profile_horizontally" in settings:
            self.cnc_depth_profile_invert_check.blockSignals(True)
            self.cnc_depth_profile_invert_check.setChecked(bool(settings.get("mirror_depth_profile_horizontally", True)))
            self.cnc_depth_profile_invert_check.blockSignals(False)

        if "show_machine_boundary" in settings:
            self.cnc_show_machine_boundary_check.blockSignals(True)
            self.cnc_show_machine_boundary_check.setChecked(bool(settings.get("show_machine_boundary", True)))
            self.cnc_show_machine_boundary_check.blockSignals(False)

        if mark_dirty:
            self._on_cnc_preview_settings_changed()
            self._mark_cnc_gcode_dirty()
        return True

    def save_cnc_machine_setup_defaults(self, settings=None):
        path = self._cnc_machine_setup_defaults_path()
        if path is None:
            return False
        payload = settings if isinstance(settings, dict) else self.get_cnc_machine_setup_settings()
        try:
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            return True
        except Exception:
            return False

    def load_cnc_machine_setup_defaults(self):
        path = self._cnc_machine_setup_defaults_path()
        if path is None or not path.exists():
            return False
        try:
            settings = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return False
        return self.apply_cnc_machine_setup_settings(settings, mark_dirty=False)

    def build_cnc_menu(self):
        settings_menu = self.menu_bar.addMenu("Settings")

        self.symmetric_mode_action = QAction("Ski Mode", self)
        self.snowboard_mode_action = QAction("Snowboard Mode", self)
        self.splitboard_mode_action = QAction("Splitboard Mode", self)
        self.asymmetric_mode_action = QAction("Asymmetrical Board Mode", self)
        for action in (self.symmetric_mode_action, self.snowboard_mode_action, self.splitboard_mode_action, self.asymmetric_mode_action):
            action.setCheckable(True)
            settings_menu.addAction(action)
        settings_menu.addSeparator()
        self.symmetric_mode_action.triggered.connect(lambda: self.set_shape_outline_mode("symmetric"))
        self.snowboard_mode_action.triggered.connect(lambda: self.set_shape_outline_mode("snowboard"))
        self.splitboard_mode_action.triggered.connect(lambda: self.set_shape_outline_mode("splitboard"))
        self.asymmetric_mode_action.triggered.connect(lambda: self.set_shape_outline_mode("asymmetric"))

        self.mouse_input_settings_action = QAction("3D Mouse Input Settings", self)
        settings_menu.addAction(self.mouse_input_settings_action)
        self.mouse_input_settings_action.triggered.connect(self.show_mouse_input_settings_dialog)

        self.cnc_mouse_input_settings_action = QAction("3D Toolpath Preview Mouse Input Settings", self)
        settings_menu.addAction(self.cnc_mouse_input_settings_action)
        self.cnc_mouse_input_settings_action.triggered.connect(self.show_cnc_mouse_input_settings_dialog)
        self.refresh_shape_outline_mode_actions()

    def _saved_cnc_preview_view_path(self):
        return Path.home() / ".ski_design_cnc_preview_view.json"

    def _capture_cnc_preview_view_payload(self):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is None:
            return None
        return {
            "rot_x_deg": float(getattr(preview_widget, 'rot_x', 0.0)),
            "rot_y_deg": float(getattr(preview_widget, 'rot_y', 0.0)),
            "rot_z_deg": float(getattr(preview_widget, 'rot_z', 0.0)),
            "zoom": float(getattr(preview_widget, 'zoom', 1.0)),
            "pan_x": float(getattr(preview_widget, 'pan_x', 0.0)),
            "pan_y": float(getattr(preview_widget, 'pan_y', 0.0)),
        }

    def _apply_cnc_preview_view_payload(self, payload):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is None or not isinstance(payload, dict):
            return False
        preview_widget.set_view_angles(
            float(payload.get('rot_x_deg', getattr(preview_widget, 'rot_x', 0.0))),
            float(payload.get('rot_y_deg', getattr(preview_widget, 'rot_y', 0.0))),
            float(payload.get('rot_z_deg', getattr(preview_widget, 'rot_z', 0.0))),
        )
        preview_widget.zoom = max(0.15, min(250.0, float(payload.get('zoom', getattr(preview_widget, 'zoom', 1.0)))))
        preview_widget.pan_x = float(payload.get('pan_x', getattr(preview_widget, 'pan_x', 0.0)))
        preview_widget.pan_y = float(payload.get('pan_y', getattr(preview_widget, 'pan_y', 0.0)))
        preview_widget._invalidate_projection_cache()
        preview_widget.update()
        if hasattr(self, 'ski') and self.ski is not None:
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.viewport().update()
        return True

    def _read_cnc_preview_view_store(self):
        path = self._saved_cnc_preview_view_path()
        if not path.exists():
            return {}
        try:
            payload = json.loads(path.read_text(encoding='utf-8'))
        except Exception:
            return {}
        if not isinstance(payload, dict):
            return {}
        return payload

    def _cnc_preview_view_slot_key(self, slot):
        return f"custom_{max(1, min(2, int(slot)))}"

    def _select_cnc_custom_view_slot(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Save Custom CNC View")
        dialog.setText("Choose which custom CNC view to save.")
        custom_1_button = dialog.addButton("Custom 1", QMessageBox.ButtonRole.AcceptRole)
        custom_2_button = dialog.addButton("Custom 2", QMessageBox.ButtonRole.AcceptRole)
        dialog.addButton(QMessageBox.StandardButton.Cancel)
        dialog.exec()
        clicked = dialog.clickedButton()
        if clicked == custom_1_button:
            return 1
        if clicked == custom_2_button:
            return 2
        return None

    def save_cnc_preview_view(self):
        payload = self._capture_cnc_preview_view_payload()
        if payload is None:
            return
        slot = self._select_cnc_custom_view_slot()
        if slot is None:
            return
        store = self._read_cnc_preview_view_store()
        store[self._cnc_preview_view_slot_key(slot)] = payload
        try:
            self._saved_cnc_preview_view_path().write_text(json.dumps(store, indent=2), encoding='utf-8')
            QMessageBox.information(self, "CNC View Saved", f"Saved CNC Custom {slot}.")
        except Exception as exc:
            QMessageBox.warning(self, "Save Failed", f"Could not save CNC preview view\n{exc}")

    def load_cnc_preview_view(self, slot=1):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is None:
            return
        path = self._saved_cnc_preview_view_path()
        if not path.exists():
            QMessageBox.information(self, "No Custom CNC View", f"No CNC Custom {slot} view was found yet.")
            return
        try:
            store = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            QMessageBox.warning(self, "Load Failed", f"Could not read saved CNC preview view\n{exc}")
            return
        slot_key = self._cnc_preview_view_slot_key(slot)
        payload = store.get(slot_key) if isinstance(store, dict) else None
        if payload is None and slot == 1 and isinstance(store, dict) and "rot_x_deg" in store:
            payload = store
        if payload is None:
            QMessageBox.information(self, "No Custom CNC View", f"No CNC Custom {slot} view was found yet.")
            return
        self._apply_cnc_preview_view_payload(payload)

    def _set_cnc_preview_angles(self, pitch_deg, yaw_deg, roll_deg):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is not None:
            preview_widget.set_view_angles(pitch_deg, yaw_deg, roll_deg)
            preview_widget.update()
            if hasattr(preview_widget, "repaint"):
                preview_widget.repaint()
        if hasattr(self, "ski") and self.ski is not None:
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.viewport().update()

    def set_cnc_home_view(self):
        self._set_cnc_preview_angles(100.0, -10.0, 180.0)
        self.rescale_cnc_preview_view()
#        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
#        if preview_widget is not None:
#            preview_widget.reset_view()
#            preview_widget.fit_toolpath_to_view(0.90, self._active_cnc_preview_fit_rect())
#        if hasattr(self, "ski") and self.ski is not None:
#            self.ski.update()
#        if hasattr(self, "view") and self.view is not None:
#            self.view.viewport().update()

    def set_cnc_front_view(self):
        self._set_cnc_preview_angles(270.0, 180.0, 0.0)
        self.rescale_cnc_preview_view()

    def set_cnc_top_view(self):
        self._set_cnc_preview_angles(0.0, 180.0, 0.0)
        self.rescale_cnc_preview_view()

    def set_cnc_side_view(self):
        self._set_cnc_preview_angles(0, 270, 0)
        self.rescale_cnc_preview_view()

    def _active_cnc_preview_fit_rect(self):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is not None and preview_widget.isVisible():
            return preview_widget._preview_viewport_rect()
        rects = self._main_window_cnc_view_rects() if hasattr(self, "_main_window_cnc_view_rects") else {}
        preview_3d_rect = rects.get("preview_3d") if isinstance(rects, dict) else None
        if preview_3d_rect is not None and not preview_3d_rect.isNull():
            return preview_3d_rect.adjusted(10.0, 28.0, -10.0, -12.0)
        return preview_widget._preview_viewport_rect() if preview_widget is not None else QRectF()

    def recenter_cnc_preview_view(self):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is not None:
            preview_widget.center_toolpath_in_view()
        if hasattr(self, "ski") and self.ski is not None:
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.viewport().update()

    def rescale_cnc_preview_view(self, fill_ratio=0.90):
        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is not None:
            preview_widget.fit_toolpath_to_view(float(fill_ratio), self._active_cnc_preview_fit_rect())
        if hasattr(self, "ski") and self.ski is not None:
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.viewport().update()

    def show_cnc_machine_setup_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("CNC Machine Setup")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        workspace_x_spin = QDoubleSpinBox(dialog)
        workspace_x_spin.setRange(self.cnc_workspace_x_spin.minimum(), self.cnc_workspace_x_spin.maximum())
        workspace_x_spin.setDecimals(self.cnc_workspace_x_spin.decimals())
        workspace_x_spin.setSingleStep(self.cnc_workspace_x_spin.singleStep())
        workspace_x_spin.setSuffix(self.cnc_workspace_x_spin.suffix())
        workspace_x_spin.setValue(self.cnc_workspace_x_spin.value())

        workspace_y_spin = QDoubleSpinBox(dialog)
        workspace_y_spin.setRange(self.cnc_workspace_y_spin.minimum(), self.cnc_workspace_y_spin.maximum())
        workspace_y_spin.setDecimals(self.cnc_workspace_y_spin.decimals())
        workspace_y_spin.setSingleStep(self.cnc_workspace_y_spin.singleStep())
        workspace_y_spin.setSuffix(self.cnc_workspace_y_spin.suffix())
        workspace_y_spin.setValue(self.cnc_workspace_y_spin.value())

        workspace_z_spin = QDoubleSpinBox(dialog)
        workspace_z_spin.setRange(self.cnc_workspace_z_spin.minimum(), self.cnc_workspace_z_spin.maximum())
        workspace_z_spin.setDecimals(self.cnc_workspace_z_spin.decimals())
        workspace_z_spin.setSingleStep(self.cnc_workspace_z_spin.singleStep())
        workspace_z_spin.setSuffix(self.cnc_workspace_z_spin.suffix())
        workspace_z_spin.setValue(self.cnc_workspace_z_spin.value())

        workspace_move_x_spin = QDoubleSpinBox(dialog)
        workspace_move_x_spin.setRange(self.cnc_workspace_move_x_spin.minimum(), self.cnc_workspace_move_x_spin.maximum())
        workspace_move_x_spin.setDecimals(self.cnc_workspace_move_x_spin.decimals())
        workspace_move_x_spin.setSingleStep(self.cnc_workspace_move_x_spin.singleStep())
        workspace_move_x_spin.setSuffix(self.cnc_workspace_move_x_spin.suffix())
        workspace_move_x_spin.setValue(self.cnc_workspace_move_x_spin.value())

        workspace_move_y_spin = QDoubleSpinBox(dialog)
        workspace_move_y_spin.setRange(self.cnc_workspace_move_y_spin.minimum(), self.cnc_workspace_move_y_spin.maximum())
        workspace_move_y_spin.setDecimals(self.cnc_workspace_move_y_spin.decimals())
        workspace_move_y_spin.setSingleStep(self.cnc_workspace_move_y_spin.singleStep())
        workspace_move_y_spin.setSuffix(self.cnc_workspace_move_y_spin.suffix())
        workspace_move_y_spin.setValue(self.cnc_workspace_move_y_spin.value())

        workspace_move_z_spin = QDoubleSpinBox(dialog)
        workspace_move_z_spin.setRange(self.cnc_workspace_move_z_spin.minimum(), self.cnc_workspace_move_z_spin.maximum())
        workspace_move_z_spin.setDecimals(self.cnc_workspace_move_z_spin.decimals())
        workspace_move_z_spin.setSingleStep(self.cnc_workspace_move_z_spin.singleStep())
        workspace_move_z_spin.setSuffix(self.cnc_workspace_move_z_spin.suffix())
        workspace_move_z_spin.setValue(self.cnc_workspace_move_z_spin.value())

        show_machine_boundary_check = QCheckBox("Show Machine Boundary", dialog)
        show_machine_boundary_check.setChecked(self.cnc_show_machine_boundary_check.isChecked())

        form.addRow(show_machine_boundary_check)
        form.addRow("Workspace X", workspace_x_spin)
        form.addRow("Workspace Y", workspace_y_spin)
        form.addRow("Workspace Z", workspace_z_spin)
        form.addRow("Move X", workspace_move_x_spin)
        form.addRow("Move Y", workspace_move_y_spin)
        form.addRow("Move Z", workspace_move_z_spin)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=dialog)
        save_defaults_button = buttons.addButton("Save As New Defaults", QDialogButtonBox.ButtonRole.ActionRole)

        def _dialog_settings_payload():
            return {
                "start_x": float(self.cnc_start_x_spin.value()),
                "start_y": float(self.cnc_start_y_spin.value()),
                "workspace_x": float(workspace_x_spin.value()),
                "workspace_y": float(workspace_y_spin.value()),
                "workspace_z": float(workspace_z_spin.value()),
                "workspace_move_x": float(workspace_move_x_spin.value()),
                "workspace_move_y": float(workspace_move_y_spin.value()),
                "workspace_move_z": float(workspace_move_z_spin.value()),
                "show_machine_boundary": bool(show_machine_boundary_check.isChecked()),
                "preview_offset_ud": float(self.cnc_preview_offset_ud_spin.value()),
                "preview_offset_lr": float(self.cnc_preview_offset_lr_spin.value()),
                "preview_offset_z": float(self.cnc_preview_offset_z_spin.value()),
                "duplicate_enabled": bool(self.cnc_duplicate_check.isChecked()),
                "duplicate_x": float(self.cnc_duplicate_x_spin.value()),
                "duplicate_y": float(self.cnc_duplicate_y_spin.value()),
                "mirror_depth_profile_horizontally": bool(self.cnc_depth_profile_invert_check.isChecked()),
            }

        def _save_dialog_defaults():
            ok = self.save_cnc_machine_setup_defaults(_dialog_settings_payload())
            QMessageBox.information(dialog, "Defaults Saved", "Saved the current machine setup values as the new defaults." if ok else "Could not save the machine setup defaults.")

        save_defaults_button.clicked.connect(_save_dialog_defaults)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            for dest, src in (
                (self.cnc_workspace_x_spin, workspace_x_spin),
                (self.cnc_workspace_y_spin, workspace_y_spin),
                (self.cnc_workspace_z_spin, workspace_z_spin),
                (self.cnc_workspace_move_x_spin, workspace_move_x_spin),
                (self.cnc_workspace_move_y_spin, workspace_move_y_spin),
                (self.cnc_workspace_move_z_spin, workspace_move_z_spin),
            ):
                dest.blockSignals(True)
                dest.setValue(src.value())
                dest.blockSignals(False)
            self.cnc_show_machine_boundary_check.blockSignals(True)
            self.cnc_show_machine_boundary_check.setChecked(show_machine_boundary_check.isChecked())
            self.cnc_show_machine_boundary_check.blockSignals(False)
            self._on_cnc_preview_settings_changed()
            self._mark_cnc_gcode_dirty()

    def show_cnc_parameters_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("CNC Toolpath Parameters")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        form.setContentsMargins(0, 0, 0, 0)

        stub_spin = QDoubleSpinBox(dialog)
        stub_spin.setRange(0.0, 10.0)
        stub_spin.setDecimals(3)
        stub_spin.setSingleStep(0.01)
        stub_spin.setSuffix(" mm")
        stub_spin.setValue(float(getattr(self, "cnc_outside_stub_filter_mm", 0.06)))

        bridge_spin = QDoubleSpinBox(dialog)
        bridge_spin.setRange(0.0, 20.0)
        bridge_spin.setDecimals(3)
        bridge_spin.setSingleStep(0.01)
        bridge_spin.setSuffix(" mm")
        bridge_spin.setValue(float(getattr(self, "cnc_outside_bridge_filter_mm", 0.20)))

        area_spin = QDoubleSpinBox(dialog)
        area_spin.setRange(0.0, 2.0)
        area_spin.setDecimals(3)
        area_spin.setSingleStep(0.01)
        area_spin.setValue(float(getattr(self, "cnc_outside_spike_area_factor", 0.30)))

        duplicate_check = QCheckBox("Duplicate Toolpath", dialog)
        duplicate_check.setChecked(self.cnc_duplicate_check.isChecked())

        preview_lr_spin = QDoubleSpinBox(dialog)
        preview_lr_spin.setRange(self.cnc_preview_offset_lr_spin.minimum(), self.cnc_preview_offset_lr_spin.maximum())
        preview_lr_spin.setDecimals(self.cnc_preview_offset_lr_spin.decimals())
        preview_lr_spin.setSingleStep(self.cnc_preview_offset_lr_spin.singleStep())
        preview_lr_spin.setSuffix(self.cnc_preview_offset_lr_spin.suffix())
        preview_lr_spin.setValue(self.cnc_preview_offset_lr_spin.value())

        preview_ud_spin = QDoubleSpinBox(dialog)
        preview_ud_spin.setRange(self.cnc_preview_offset_ud_spin.minimum(), self.cnc_preview_offset_ud_spin.maximum())
        preview_ud_spin.setDecimals(self.cnc_preview_offset_ud_spin.decimals())
        preview_ud_spin.setSingleStep(self.cnc_preview_offset_ud_spin.singleStep())
        preview_ud_spin.setSuffix(self.cnc_preview_offset_ud_spin.suffix())
        preview_ud_spin.setValue(self.cnc_preview_offset_ud_spin.value())

        preview_z_spin = QDoubleSpinBox(dialog)
        preview_z_spin.setRange(self.cnc_preview_offset_z_spin.minimum(), self.cnc_preview_offset_z_spin.maximum())
        preview_z_spin.setDecimals(self.cnc_preview_offset_z_spin.decimals())
        preview_z_spin.setSingleStep(self.cnc_preview_offset_z_spin.singleStep())
        preview_z_spin.setSuffix(self.cnc_preview_offset_z_spin.suffix())
        preview_z_spin.setValue(self.cnc_preview_offset_z_spin.value())

        duplicate_x_spin = QDoubleSpinBox(dialog)
        duplicate_x_spin.setRange(self.cnc_duplicate_x_spin.minimum(), self.cnc_duplicate_x_spin.maximum())
        duplicate_x_spin.setDecimals(self.cnc_duplicate_x_spin.decimals())
        duplicate_x_spin.setSingleStep(self.cnc_duplicate_x_spin.singleStep())
        duplicate_x_spin.setSuffix(self.cnc_duplicate_x_spin.suffix())
        duplicate_x_spin.setValue(self.cnc_duplicate_x_spin.value())

        duplicate_y_spin = QDoubleSpinBox(dialog)
        duplicate_y_spin.setRange(self.cnc_duplicate_y_spin.minimum(), self.cnc_duplicate_y_spin.maximum())
        duplicate_y_spin.setDecimals(self.cnc_duplicate_y_spin.decimals())
        duplicate_y_spin.setSingleStep(self.cnc_duplicate_y_spin.singleStep())
        duplicate_y_spin.setSuffix(self.cnc_duplicate_y_spin.suffix())
        duplicate_y_spin.setValue(self.cnc_duplicate_y_spin.value())

        mirror_check = QCheckBox("Mirror Depth Profile Horizontally", dialog)
        mirror_check.setChecked(self.cnc_depth_profile_invert_check.isChecked())

        color_mode_combo = QComboBox(dialog)
        color_mode_combo.addItems(["Feed Rate", "Motion Type"])
        color_mode_combo.setCurrentText(self.cnc_preview_color_mode_combo.currentText())

        note = QLabel(
            "Outside cleanup only. Lower values keep more tiny segments; higher values remove more local artifacts near tight intersections."
        )
        note.setWordWrap(True)

        form.addRow("Outside stub filter", stub_spin)
        form.addRow("Outside bridge filter", bridge_spin)
        form.addRow("Outside spike factor", area_spin)
        form.addRow("Preview Colors", color_mode_combo)
        form.addRow("Move Toolpath X", preview_lr_spin)
        form.addRow("Move Toolpath Y", preview_ud_spin)
        form.addRow("Move Toolpath Z", preview_z_spin)
        form.addRow(duplicate_check)
        form.addRow("Duplicate X Offset", duplicate_x_spin)
        form.addRow("Duplicate Y Offset", duplicate_y_spin)
        layout.addLayout(form)
        layout.addWidget(mirror_check)
        layout.addWidget(note)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=dialog)
        reset_btn = buttons.addButton("Defaults", QDialogButtonBox.ButtonRole.ResetRole)
        reset_btn.clicked.connect(lambda: (
            stub_spin.setValue(0.06),
            bridge_spin.setValue(0.20),
            area_spin.setValue(0.30)
        ))
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.cnc_outside_stub_filter_mm = float(stub_spin.value())
            self.cnc_outside_bridge_filter_mm = float(bridge_spin.value())
            self.cnc_outside_spike_area_factor = float(area_spin.value())
            self.cnc_preview_offset_lr_spin.blockSignals(True)
            self.cnc_preview_offset_lr_spin.setValue(preview_lr_spin.value())
            self.cnc_preview_offset_lr_spin.blockSignals(False)
            self.cnc_preview_offset_ud_spin.blockSignals(True)
            self.cnc_preview_offset_ud_spin.setValue(preview_ud_spin.value())
            self.cnc_preview_offset_ud_spin.blockSignals(False)
            self.cnc_preview_offset_z_spin.blockSignals(True)
            self.cnc_preview_offset_z_spin.setValue(preview_z_spin.value())
            self.cnc_preview_offset_z_spin.blockSignals(False)
            self.cnc_duplicate_x_spin.blockSignals(True)
            self.cnc_duplicate_x_spin.setValue(duplicate_x_spin.value())
            self.cnc_duplicate_x_spin.blockSignals(False)
            self.cnc_duplicate_y_spin.blockSignals(True)
            self.cnc_duplicate_y_spin.setValue(duplicate_y_spin.value())
            self.cnc_duplicate_y_spin.blockSignals(False)
            self.cnc_duplicate_check.blockSignals(True)
            self.cnc_duplicate_check.setChecked(duplicate_check.isChecked())
            self.cnc_duplicate_check.blockSignals(False)
            self.cnc_preview_color_mode_combo.blockSignals(True)
            self.cnc_preview_color_mode_combo.setCurrentText(color_mode_combo.currentText())
            self.cnc_preview_color_mode_combo.blockSignals(False)
            self.cnc_depth_profile_invert_check.blockSignals(True)
            self.cnc_depth_profile_invert_check.setChecked(mirror_check.isChecked())
            self.cnc_depth_profile_invert_check.blockSignals(False)
            self._invalidate_cnc_toolpath_cache()
            self._mark_cnc_gcode_dirty()
            self.ski.update()

    def build_help_menu(self):
        help_menu = self.menu_bar.addMenu("Help")

        self.about_action = QAction("About", self)
        self.help_action = QAction("Help", self)

        help_menu.addAction(self.about_action)
        help_menu.addAction(self.help_action)

        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_action.triggered.connect(self.show_help_dialog)
    def show_about_dialog(self):
        about_text = (
            "Super Simple Ski Designer\n\n"
            "A tool for sketching ski and snowboard shapes, adjusting layup details, "
            "previewing in 3D, and exporting design geometry.\n\n"
            "Written by JD Ritchey, starting ~3.1.2026."
        )
        dialog = HelpTextDialog("About", about_text, self)
        dialog.exec()
    def show_help_dialog(self):
        help_text = (
            "Super Simple Ski Designer Help\n\n"
            "This app is used to sketch ski and snowboard outlines, tune construction details, preview the design in 2D and 3D, and generate CNC toolpaths from the selected design geometry.\n\n"

            "File Menu\n"
            "- Save: saves the current design file.\n"
            "- Load: opens a previously saved design file.\n"
            "- Export Build Sheet PDF: exports the outline, core profile, camber profile, dimensions, and material notes.\n"
            "- Export SVG: exports 2D vector geometry for drawing, templates, or downstream CAD work.\n"
            "- Export DXF: exports design geometry for CAD/CAM workflows.\n"
            "- Export STL: exports the 3D model for mesh-based preview, printing, or machining workflows.\n"
            "- Exit: closes the app after confirmation when needed.\n\n"

            "Main 2D View Navigation\n"
            "- Mouse wheel: zoom in and out.\n"
            "- Middle mouse drag: pan the 2D workspace.\n"
            "- Hold Z and drag a box to zoom to that area, then zoom in another 20 percent.\n"
            "- The fixed scale overlay remains screen-aligned while the design view moves underneath it.\n\n"

            "Editing Shape Points\n"
            "- Double click the main red outline to add a shape point.\n"
            "- Ctrl + double click adds a cosmetic point.\n"
            "- Click a point to select it.\n"
            "- Shift + click selects additional points without clearing the current selection.\n"
            "- Drag a selection box to select multiple points.\n"
            "- Arrow keys nudge selected points by 0.5 mm.\n"
            "- Shift or Command plus arrow keys nudges selected points by 0.1 mm.\n"
            "- Delete removes selected points.\n"
            "- V toggles vertical tangent handle locking on selected points.\n"
            "- H toggles horizontal tangent handle locking on selected points.\n"
            "- L toggles colinear tangent handle locking on selected points.\n"
            "- I and O toggle paired in/out tangent locks where supported.\n"
            "- C toggles a 3-point circle through selected points.\n"
            "- When two points are selected, a distance preview is shown.\n"
            "- D toggles a locked dimension between two selected points.\n\n"

            "View Panel\n"
            "- Toggle Points shows or hides editable control points.\n"
            "- Toggle Dimensions shows or hides dimension annotations.\n"
            "- Toggle Global Coordinates shows or hides global coordinate labels.\n"
            "- Toggle Circle shows or hides the selected 3-point circle helper.\n\n"

            "Layup Panel\n"
            "- Base, Edge Inlay, Core, Sidewalls, Tip/Tail Spacers, and Shell buttons show or hide construction layers.\n"
            "- Sidewall Thickness, Edge Thickness, Edge to Tip, and Edge to Tail tune layer offsets and trims.\n"
            "- Minimum Core Thickness, Tip Spacer Length, and Tail Spacer Length control core and spacer geometry.\n"
            "- Tip Seam Pts and Tail Seam Pts adjust seam point counts.\n"
            "- Lower Reinforcement, Wood Core Stiffness, and Upper Reinforcement affect the stiffness visualization.\n\n"

            "2D Appearance Panel\n"
            "- Load Right Graphic and Load Left Graphic add graphics for visual layout work.\n"
            "- Graphic selects whether controls apply to the top or base graphic.\n"
            "- X Offset and Y Offset move the selected graphic in the 2D view.\n"
            "- Scale X and Scale Y resize the selected graphic independently.\n\n"

            "3D Appearance Panel\n"
            "- Shaded, Edges, Wire, and Graphic change the 3D render style.\n"
            "- Roll, Butter, and Spin control the 3D ski orientation.\n"
            "- Home View, Front View, Top View, and Side View snap the 3D ski to preset angles.\n"
            "- Save 3D Position and Load 3D Position store and restore the current 3D ski camera position.\n"
            "- Second Ski Layout toggles the two-ski layout controls.\n"
            "- Mouse Input Settings opens detailed controls for right-click orbit behavior.\n"
            "- Pick 3D Color and Pick Background Color change model and scene colors.\n"
            "- Background toggles the 3D background graphic or color.\n"
            "- Second Ski Spacing changes spacing between paired skis.\n"
            "- Light Azimuth, Light Elevation, and Brightness tune scene lighting.\n"
            "- Background Width and Background Height resize the 3D background.\n\n"

            "3D Mouse Controls\n"
            "- Right mouse drag orbits the 3D view.\n"
            "- Shift changes the alternate orbit gesture behavior according to the mouse input settings.\n"
            "- Middle mouse drag pans.\n"
            "- Mouse wheel zooms.\n"
            "- Settings > 3D Mouse Input Settings tunes invert, swap, roll, pitch, yaw, sensitivity, and dominant-axis behavior.\n\n"

            "CNC Toolpaths Panel\n"
            "- Open CNC Toolpaths to select shapes, preview toolpaths, and generate G-code.\n"
            "- Selectable Shapes chooses which exported design shape is active for machining.\n"
            "- Show CNC Stats shows the CNC Bottom Reference Point and CNC Center Point for the selected shape.\n"
            "- Generate G-Code refreshes the text preview from the current CNC settings.\n"
            "- Save G-Code writes the generated toolpath to a file.\n\n"

            "CNC Snap To View\n"
            "- Home returns the CNC preview to the default angled view and fits the toolpath.\n"
            "- Front, Top, and Side snap to preset CNC preview orientations.\n"
            "- Recenter pans the CNC preview so the selected toolpath center is in the preview center.\n"
            "- Re-scale zooms the selected toolpath to about 90 percent of the preview width or height, whichever is limiting.\n"
            "- Save Custom View saves the current CNC preview angle, zoom, and pan to Custom 1 or Custom 2.\n"
            "- Custom 1 and Custom 2 load the saved custom CNC preview slots.\n\n"

            "CNC Machine Setup\n"
            "- Workspace X, Workspace Y, and Workspace Z set the machine boundary size.\n"
            "- Move X, Move Y, and Move Z move the machine boundary in the CNC preview.\n"
            "- Show Machine Boundary toggles the dashed machine workspace box.\n"
            "- Save As New Defaults in the machine setup dialog stores the current machine setup defaults.\n\n"

            "CNC Toolpath Parameters\n"
            "- Operation selects On Line, Outside, or Pocket machining behavior.\n"
            "- Preview Colors switches the 3D toolpath colors between feed-rate and motion-type modes.\n"
            "- Move Toolpath X, Move Toolpath Y, and Move Toolpath Z shift the generated and previewed toolpath.\n"
            "- Mirror Depth Profile Horizontally flips profile-based depth behavior horizontally.\n"
            "- Depth From Core Profile uses the core profile for Z depth instead of a flat cut depth.\n"
            "- Ramp Entry enables gradual ramping into supported operations.\n"
            "- Duplicate Toolpath creates a second copy using Duplicate X Offset and Duplicate Y Offset.\n"
            "- Ramp Angle and Ramp Speed control ramp entry shape and feed rate.\n"
            "- Mill Diameter affects offsets and toolpath geometry.\n"
            "- Safety Retract sets the rapid Z clearance height.\n"
            "- Cut Depth sets flat-depth machining depth.\n"
            "- Stepdown controls pass depth increments.\n"
            "- Feed Rate, Plunge Rate, and Spindle set basic cutting parameters.\n\n"

            "CNC Preview Mouse Controls\n"
            "- Right mouse drag orbits the CNC 3D preview.\n"
            "- Middle mouse drag pans the CNC preview.\n"
            "- Mouse wheel zooms the CNC preview.\n"
            "- Settings > 3D Toolpath Preview Mouse Input Settings tunes CNC preview orbit behavior independently from the ski 3D view.\n\n"

            "General Workflow Tips\n"
            "- Start by shaping the main outline and construction layers in 2D.\n"
            "- Use Geometry Stats to monitor length, widths, and areas; use CNC Stats for CNC reference points.\n"
            "- Use the 3D Appearance panel to inspect the ski or snowboard form before export.\n"
            "- Open CNC Toolpaths, choose a shape, set the operation and tool parameters, then generate G-code.\n"
            "- After changing CNC parameters, regenerate G-code before saving it.\n"
            "- Save design files frequently before making major geometry or CNC setup changes."
        )
        dialog = HelpTextDialog("Help", help_text, self)
        dialog.exec()

    def show_mouse_input_settings_dialog(self):
        dialog = MouseInputSettingsDialog(self.view, self)
        dialog.exec()

    def show_cnc_mouse_input_settings_dialog(self):
        dialog = MouseInputSettingsDialog(self.cnc_3d_preview_widget, self)
        dialog.setWindowTitle("3D Toolpath Preview Mouse Input Settings")
        dialog.exec()
    def refresh_shape_outline_mode_actions(self):
        mode = getattr(self.ski, "outline_mode", "symmetric") if hasattr(self, "ski") else "symmetric"
        mapping = {
            "symmetric": getattr(self, "symmetric_mode_action", None),
            "snowboard": getattr(self, "snowboard_mode_action", None),
            "splitboard": getattr(self, "splitboard_mode_action", None),
            "asymmetric": getattr(self, "asymmetric_mode_action", None),
        }
        for key, action in mapping.items():
            if action is None:
                continue
            action.blockSignals(True)
            action.setChecked(key == mode)
            action.blockSignals(False)
    def set_shape_outline_mode(self, mode):
        if not hasattr(self, "ski") or self.ski is None:
            return
        self.ski.set_outline_mode(mode)
        self.refresh_shape_outline_mode_actions()
        self.refresh_splitboard_inside_edge_controls()
        self._sync_second_ski_layout_button()
        self._sync_graphic_buttons()
        self.refresh_cnc_shape_buttons()
        self.refresh_cnc_3d_preview_widget()
        self.ski.update()
    def refresh_3d_view_style_buttons(self):
        mode = getattr(self.ski, "render_3d_mode", "shaded")
        mapping = {
            "shaded": self.view_style_shaded_button,
            "shaded_edges": self.view_style_edges_button,
            "wireframe": self.view_style_wire_button,
            "graphic": self.view_style_graphic_button,
        }
        for key, btn in mapping.items():
            active = (key == mode)
            btn.blockSignals(True)
            btn.setChecked(active)
            if active:
                btn.setStyleSheet("background-color: #5B616A; border: 1px solid #8D96A2; color: #FFFFFF;")
            else:
                btn.setStyleSheet("")
            btn.blockSignals(False)

    def set_3d_view_style(self, mode):
        if mode not in {"shaded", "shaded_edges", "wireframe", "graphic"}:
            return
        self.ski.render_3d_mode = mode
        self.refresh_3d_view_style_buttons()
        self.ski.update()

    def save_whole_view_target(self):
        if not hasattr(self, "view") or self.view is None:
            return
        viewport = self.view.viewport()
        if viewport is None:
            return
        center = self.view.mapToScene(viewport.rect().center())
        zoom = self.view._current_zoom() if hasattr(self.view, "_current_zoom") else abs(self.view.transform().m11())
        self._saved_whole_view_target = {
            "center_x": float(center.x()),
            "center_y": float(center.y()),
            "zoom": max(1e-9, float(zoom)),
        }
        if hasattr(self, "save_whole_view_button"):
            self.save_whole_view_button.setText("Update")

    def _apply_saved_whole_view_target(self):
        target = getattr(self, "_saved_whole_view_target", None)
        if not target or not hasattr(self, "view") or self.view is None:
            return False
        zoom = max(1e-9, float(target.get("zoom", 1.0)))
        max_zoom = float(getattr(self.view, "max_zoom", 12.0))
        zoom = min(zoom, max_zoom)
        self.view.resetTransform()
        self.view.scale(zoom, zoom)
        self.view.centerOn(QPointF(float(target.get("center_x", 0.0)), float(target.get("center_y", 0.0))))
        return True

    def recenter_rescale_whole_view(self):
        if not hasattr(self, "view") or self.view is None or not hasattr(self, "ski"):
            return
        if self._apply_saved_whole_view_target():
            self.view._refresh_scale_overlay()
            self.view.update()
            viewport = self.view.viewport()
            if viewport is not None:
                viewport.update()
            return
        target_rect = QRectF(self.ski.boundingRect()).adjusted(-80.0, -80.0, 80.0, 80.0)
        if target_rect.isNull() or target_rect.width() <= 0.0 or target_rect.height() <= 0.0:
            return
        self.view.resetTransform()
        self.view.fitInView(target_rect, Qt.AspectRatioMode.KeepAspectRatio)
        current_zoom = self.view._current_zoom() if hasattr(self.view, "_current_zoom") else abs(self.view.transform().m11())
        zoom_factor = 1.15 ** 10
        max_zoom = float(getattr(self.view, "max_zoom", 12.0))
        if current_zoom > 1e-9:
            zoom_factor = min(zoom_factor, max_zoom / current_zoom)
        if zoom_factor > 1.0:
            self.view.scale(zoom_factor, zoom_factor)
        self.view.centerOn(target_rect.center())
        self.view._refresh_scale_overlay()
        self.view.update()
        viewport = self.view.viewport()
        if viewport is not None:
            viewport.update()

    def apply_view_angles(self, pitch_deg, yaw_deg, roll_deg):
        self.rot_x_spin.blockSignals(True)
        self.rot_y_spin.blockSignals(True)
        self.rot_z_spin.blockSignals(True)
        self.rot_x_spin.setValue(float(pitch_deg))
        self.rot_y_spin.setValue(float(yaw_deg))
        self.rot_z_spin.setValue(float(roll_deg))
        self.rot_x_spin.blockSignals(False)
        self.rot_y_spin.blockSignals(False)
        self.rot_z_spin.blockSignals(False)
        self.ski.show_3d = bool(self.appearance_panel.toggle_button.isChecked())
        self.update_rot()
    def set_home_view(self):
        self.apply_view_angles(-75.0, -60.0, 135.0)
    def set_front_view(self):
        self.apply_view_angles(0.0, 35.0, -135.0)
    def set_top_view(self):
        self.apply_view_angles(0.0, -120.0, 45.0)
    def set_side_view(self):
        self.apply_view_angles(-35.0, 0.0, 135.0)
    def on_appearance_panel_toggled(self, expanded):
        self.ski.show_3d = bool(expanded)
        self.ski.update()

    def should_draw_stiffness_plot(self):
        return bool(getattr(self, "toggle_stiffness_plot_button", None) is None or self.toggle_stiffness_plot_button.isChecked())

    def should_draw_stats(self):
        return bool(getattr(self, "toggle_stats_button", None) is None or self.toggle_stats_button.isChecked())

    def should_draw_cnc_stats(self):
        return bool(getattr(self, "toggle_cnc_stats_button", None) is not None and self.toggle_cnc_stats_button.isChecked())

    def should_draw_interface_shortcuts(self):
        return bool(getattr(self, "toggle_interface_shortcuts_button", None) is not None and self.toggle_interface_shortcuts_button.isChecked())

    def _second_ski_toggle_label(self):
        show_second = bool(getattr(self.ski, "show_ski_snowboard", False))
        mode = getattr(self.ski, "outline_mode", "symmetric")
        if mode == "splitboard":
            return "Show Editable Side Only" if show_second else "Show Both Sides"
        if mode == "snowboard":
            return "Hide Base" if show_second else "Show Base"
        return "Show Single Ski" if show_second else "Show 2nd Ski"

    def toggle_ski_snowboard(self):
        self.ski.show_ski_snowboard = not self.ski.show_ski_snowboard
        if hasattr(self, "toggle_ski_snowboard_action"):
            self.toggle_ski_snowboard_action.blockSignals(True)
            self.toggle_ski_snowboard_action.setChecked(self.ski.show_ski_snowboard)
            self.toggle_ski_snowboard_action.setText(self._second_ski_toggle_label())
            self.toggle_ski_snowboard_action.blockSignals(False)
        self._sync_second_ski_layout_button()
        self._sync_graphic_buttons()
        if hasattr(self, "refresh_cnc_shape_buttons"):
            self.refresh_cnc_shape_buttons()
        self.ski.update()

    def _sync_second_ski_layout_button(self):
        if not hasattr(self, "second_ski_layout_button"):
            return
        show_second = bool(getattr(self.ski, "show_ski_snowboard", False))
        label = "Side to Side" if bool(getattr(self.ski, "second_3d_base_to_base", False)) else "Base to Base"
        self.second_ski_layout_button.setText(label)
        self.second_ski_layout_button.setVisible(show_second)
        if hasattr(self, "toggle_second_ski_button"):
            self.toggle_second_ski_button.setText(self._second_ski_toggle_label())
        if hasattr(self, "toggle_ski_snowboard_action"):
            self.toggle_ski_snowboard_action.blockSignals(True)
            self.toggle_ski_snowboard_action.setChecked(show_second)
            self.toggle_ski_snowboard_action.setText(self._second_ski_toggle_label())
            self.toggle_ski_snowboard_action.blockSignals(False)
        if hasattr(self, "second_ski_spacing_slider"):
            self.second_ski_spacing_slider.setVisible(show_second)
        if hasattr(self, "second_ski_spacing_value_label"):
            self.second_ski_spacing_value_label.setVisible(show_second)
        if hasattr(self, "second_ski_spacing_label"):
            self.second_ski_spacing_label.setVisible(show_second)
        self.update_second_ski_spacing_controls()

    def toggle_second_3d_layout(self):
        self.ski.second_3d_base_to_base = not bool(getattr(self.ski, "second_3d_base_to_base", False))
        self._sync_second_ski_layout_button()
        self.ski.update()

    def update_second_ski_spacing_controls(self):
        if hasattr(self, "second_ski_spacing_slider"):
            self.ski.second_3d_base_separation_cm = float(self.second_ski_spacing_slider.value()) / 10.0
        if hasattr(self, "second_ski_spacing_value_label"):
            self.second_ski_spacing_value_label.setText(f"{getattr(self.ski, 'second_3d_base_separation_cm', 0.0):.1f} cm")
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()
    def sync_seam_editor_widgets(self):
        widgets = [
            (self.seam_depth_spin, self.ski.seam_depth_px),
            (self.seam_inner_x_spin, self.ski.tip_seam_points[0].pos.x() if self.ski.tip_seam_points else 0.0),
            (self.seam_inner_y_spin, self.ski.tip_seam_points[0].pos.y() if self.ski.tip_seam_points else 0.0),
            (self.seam_outer_x_spin, self.ski.tip_seam_points[1].pos.x() if len(self.ski.tip_seam_points) > 1 else 0.0),
            (self.seam_outer_y_spin, self.ski.tip_seam_points[1].pos.y() if len(self.ski.tip_seam_points) > 1 else 0.0),
        ]
        for widget, value in widgets:
            widget.blockSignals(True)
            widget.setValue(float(value))
            widget.blockSignals(False)
        for widget, value in [
            (self.tip_seam_point_count_spin, getattr(self.ski, "tip_seam_point_count", getattr(self.ski, "seam_point_count", 3))),
            (self.tail_seam_point_count_spin, getattr(self.ski, "tail_seam_point_count", getattr(self.ski, "seam_point_count", 3))),
        ]:
            widget.blockSignals(True)
            widget.setValue(float(value))
            widget.blockSignals(False)
        self.seam_editor_values.setText(
            "Drag the gold seam points and blue tangent handles on the ski. Mirroring stays on, but shape limits are removed."
        )
    def refresh_layup_toggle_labels(self):
        self.base_toggle_button.setText("Hide Base" if self.ski.show_base_shape else "Show Base")
        self.edge_inlay_toggle_button.setText("Hide Edge Inlay" if self.ski.show_edge_inlay_shape else "Show Edge Inlay")
        self.core_toggle_button.setText("Hide Core" if self.ski.show_core_shape else "Show Core")
        self.sidewall_toggle_button.setText("Hide Sidewalls" if self.ski.show_sidewall_shape else "Show Sidewalls")
        self.spacer_toggle_button.setText("Hide Tip/Tail Spacers" if self.ski.show_tip_tail_spacers else "Show Tip/Tail Spacers")
        self.shell_toggle_button.setText("Hide Shell" if self.ski.show_sidewall_spacer_shell else "Show Shell")
        self.base_toggle_button.setChecked(self.ski.show_base_shape)
        self.edge_inlay_toggle_button.setChecked(self.ski.show_edge_inlay_shape)
        self.core_toggle_button.setChecked(self.ski.show_core_shape)
        self.sidewall_toggle_button.setChecked(self.ski.show_sidewall_shape)
        self.spacer_toggle_button.setChecked(self.ski.show_tip_tail_spacers)
        self.shell_toggle_button.setChecked(self.ski.show_sidewall_spacer_shell)
    def refresh_splitboard_inside_edge_controls(self):
        if not hasattr(self, "splitboard_inside_edge_check"):
            return
        is_splitboard = getattr(self.ski, "outline_mode", "symmetric") == "splitboard"
        self.splitboard_inside_edge_check.blockSignals(True)
        self.splitboard_inside_edge_check.setChecked(bool(getattr(self.ski, "include_splitboard_inside_edge", True)))
        self.splitboard_inside_edge_check.blockSignals(False)
        self.splitboard_inside_edge_check.setVisible(is_splitboard)
    def update_layup_controls(self):
        self._invalidate_cnc_toolpath_cache()
        self.ski.edge_thickness_px = float(self.edge_thickness_spin.value())
        self.ski.sidewall_thickness_px = float(self.sidewall_thickness_spin.value())
        self.ski.left_sidewall_thickness_px = float(self.left_sidewall_thickness_spin.value())
        self.ski.edge_inlay_tip_trim_px = float(self.edge_inlay_tip_spin.value())
        self.ski.edge_inlay_tail_trim_px = float(self.edge_inlay_tail_spin.value())
        self.ski.base_edge_corner_min_radius_px = float(self.base_edge_corner_radius_slider.value())
        self.base_edge_corner_radius_value_label.setText(f"{self.base_edge_corner_radius_slider.value()} mm")
        self.ski.include_splitboard_inside_edge = bool(self.splitboard_inside_edge_check.isChecked())
        self.ski.minimum_core_thickness_px = float(self.minimum_core_thickness_spin.value())
        self.ski.tip_spacer_length_px = float(self.tip_spacer_spin.value())
        self.ski.tail_spacer_length_px = float(self.tail_spacer_spin.value())
        self.ski.tip_seam_point_count = self.ski._normalize_seam_point_count(self.tip_seam_point_count_spin.value())
        self.ski.tail_seam_point_count = self.ski._normalize_seam_point_count(self.tail_seam_point_count_spin.value())
        self.ski.seam_point_count = max(self.ski.tip_seam_point_count, self.ski.tail_seam_point_count)
        self.ski._cache.clear()
        self.sync_seam_editor_widgets()
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()
    def update_stiffness_controls(self):
        self.ski.lower_reinforcement_factor = float(self.lower_reinf_slider.value()) / 100.0
        self.ski.wood_core_stiffness_factor = float(self.core_stiffness_slider.value()) / 100.0
        self.ski.upper_reinforcement_factor = float(self.upper_reinf_slider.value()) / 100.0
        self.lower_reinf_value_label.setText(f"{self.ski.lower_reinforcement_factor:.2f}x")
        self.core_stiffness_value_label.setText(f"{self.ski.wood_core_stiffness_factor:.2f}x")
        self.upper_reinf_value_label.setText(f"{self.ski.upper_reinforcement_factor:.2f}x")
        self.ski._cache.clear()
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()
    def update_mold_controls(self):
        self._invalidate_cnc_toolpath_cache()
        self.ski.upper_mold_offset_mm = float(self.upper_mold_offset_slider.value())
        self.ski.mold_hole_count = int(self.mold_hole_count_slider.value())
        self.ski.mold_hole_diameter_mm = float(self.mold_hole_diameter_slider.value())
        self.upper_mold_offset_value_label.setText(f"{self.ski.upper_mold_offset_mm:.0f} mm")
        self.mold_hole_count_value_label.setText(f"{self.ski.mold_hole_count:d}")
        self.mold_hole_diameter_value_label.setText(f"{self.ski.mold_hole_diameter_mm:.0f} mm")
        self.ski._cache.clear()
        self._mark_cnc_gcode_dirty(update_view=False)
        if not getattr(self, "_startup_initializing", False):
            self.refresh_cnc_3d_preview_widget()
            self.ski.update()
    def toggle_base_shape(self):
        self.ski.show_base_shape = not self.ski.show_base_shape
        self.refresh_layup_toggle_labels()
        self.ski.update()
    def toggle_edge_inlay_shape(self):
        self.ski.show_edge_inlay_shape = not self.ski.show_edge_inlay_shape
        self.refresh_layup_toggle_labels()
        self.ski.update()
    def toggle_core_shape(self):
        self.ski.show_core_shape = not self.ski.show_core_shape
        self.refresh_layup_toggle_labels()
        self.ski.update()
    def toggle_sidewall_shape(self):
        self.ski.show_sidewall_shape = not self.ski.show_sidewall_shape
        self.refresh_layup_toggle_labels()
        self.ski.update()
    def toggle_spacer_shapes(self):
        self.ski.show_tip_tail_spacers = not self.ski.show_tip_tail_spacers
        self.refresh_layup_toggle_labels()
        self.ski.update()

    def toggle_sidewall_spacer_shell(self):
        self.ski.show_sidewall_spacer_shell = not self.ski.show_sidewall_spacer_shell
        self.refresh_layup_toggle_labels()
        self.ski.update()
    def update_rot(self):
        pitch_deg = float(self.rot_x_spin.value())
        yaw_deg = float(self.rot_y_spin.value())
        roll_deg = float(self.rot_z_spin.value())

        self.ski.rot_x = math.radians(pitch_deg)
        self.ski.rot_y = math.radians(yaw_deg)
        self.ski.rot_z = math.radians(roll_deg)

        rotation_matrix = None
        if hasattr(self, "view") and hasattr(self.view, "_local_delta_rotation_matrix"):
            try:
                rotation_matrix = self.view._local_delta_rotation_matrix(pitch_deg, yaw_deg, roll_deg)
            except Exception:
                rotation_matrix = None

        if rotation_matrix is None:
            cx = math.cos(self.ski.rot_x)
            sx = math.sin(self.ski.rot_x)
            cy = math.cos(self.ski.rot_y)
            sy = math.sin(self.ski.rot_y)
            cz = math.cos(self.ski.rot_z)
            sz = math.sin(self.ski.rot_z)
            rotation_matrix = [
                [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
                [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
                [-sy, cy * sx, cy * cx],
            ]

        self.ski.rotation_matrix = [[float(rotation_matrix[r][c]) for c in range(3)] for r in range(3)]
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()
    def update_color_button_style(self):
        return
    def update_light_controls(self):
        self.ski.light_azimuth_deg = float(self.light_azimuth_slider.value())
        self.ski.light_elevation_deg = float(self.light_elevation_slider.value())
        self.ski.light_brightness = float(self.brightness_slider.value()) / 100.0
        self.light_azimuth_value_label.setText(f"{self.ski.light_azimuth_deg:.0f}°")
        self.light_elevation_value_label.setText(f"{self.ski.light_elevation_deg:.0f}°")
        self.brightness_value_label.setText(f"{self.ski.light_brightness:.2f}")
        self.update_color_button_style()
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()

    def update_3d_background_controls(self):
        self.ski.background_3d_width_px = float(self.background_width_slider.value())
        self.ski.background_3d_height_px = float(self.background_height_slider.value())
        self.background_width_value_label.setText(f"{self.ski.background_3d_width_px:.0f} px")
        self.background_height_value_label.setText(f"{self.ski.background_3d_height_px:.0f} px")
        self.sync_3d_background_visibility_controls()
        if not getattr(self, "_startup_initializing", False):
            self.ski.update()

    def toggle_3d_background(self):
        self.ski.show_3d_background = bool(self.background_toggle_button.isChecked())
        self.sync_3d_background_visibility_controls()
        self.ski.update()

    def sync_3d_background_visibility_controls(self):
        show_bg = bool(getattr(self.ski, "show_3d_background", True))
        if hasattr(self, "background_toggle_button"):
            self.background_toggle_button.blockSignals(True)
            self.background_toggle_button.setChecked(show_bg)
            self.background_toggle_button.setText("Background Off" if show_bg else "Background On")
            self.background_toggle_button.blockSignals(False)
        for w in (
            getattr(self, "background_width_text_label", None),
            getattr(self, "background_width_slider", None),
            getattr(self, "background_width_value_label", None),
            getattr(self, "background_height_text_label", None),
            getattr(self, "background_height_slider", None),
            getattr(self, "background_height_value_label", None),
        ):
            if w is not None:
                w.setVisible(show_bg)
    def _saved_3d_position_path(self):
        return Path.home() / ".ski_design_79_3d_position.json"

    def save_3d_position(self):
        reply = QMessageBox.question(
            self,
            "Confirm Save 3D Position",
            "Are you sure you want to overwrite the saved 3D position?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        payload = {
            "rot_x_deg": float(self.rot_x_spin.value()),
            "rot_y_deg": float(self.rot_y_spin.value()),
            "rot_z_deg": float(self.rot_z_spin.value()),
            "offset_x": float(getattr(self.ski, "offset_x", 0.0)),
            "offset_y": float(getattr(self.ski, "offset_y", 0.0)),
            "show_3d": bool(getattr(self.ski, "show_3d", False)),
            "show_second_3d_ski": bool(getattr(self.ski, "show_ski_snowboard", False)),
            "second_3d_base_to_base": bool(getattr(self.ski, "second_3d_base_to_base", False)),
            "render_3d_mode": str(getattr(self.ski, "render_3d_mode", "shaded")),
            "background_3d_width_px": float(getattr(self.ski, "background_3d_width_px", 760.0)),
            "background_3d_height_px": float(getattr(self.ski, "background_3d_height_px", 1280.0)),
            "show_3d_background": bool(getattr(self.ski, "show_3d_background", True)),
        }
        try:
            self._saved_3d_position_path().write_text(json.dumps(payload, indent=2))
            QMessageBox.information(self, "3D Position Saved", "Saved 3D position.")
        except Exception as exc:
            QMessageBox.warning(self, "Save Failed", f"Could not save 3D position\n{exc}")

    def load_3d_position(self):
        path = self._saved_3d_position_path()
        if not path.exists():
            QMessageBox.information(self, "No Saved 3D Position", "No saved 3D position was found yet.")
            return
        try:
            payload = json.loads(path.read_text())
        except Exception as exc:
            QMessageBox.warning(self, "Load Failed", f"Could not read saved 3D position\n{exc}")
            return

        self.rot_x_spin.setValue(float(payload.get("rot_x_deg", self.rot_x_spin.value())))
        self.rot_y_spin.setValue(float(payload.get("rot_y_deg", self.rot_y_spin.value())))
        self.rot_z_spin.setValue(float(payload.get("rot_z_deg", self.rot_z_spin.value())))
        self.ski.offset_x = float(payload.get("offset_x", getattr(self.ski, "offset_x", 0.0)))
        self.ski.offset_y = float(payload.get("offset_y", getattr(self.ski, "offset_y", 0.0)))
        self.ski.show_3d = bool(payload.get("show_3d", True))
        self.ski.show_ski_snowboard = bool(payload.get("show_second_3d_ski", getattr(self.ski, "show_ski_snowboard", False)))
        self.ski.second_3d_base_to_base = bool(payload.get("second_3d_base_to_base", getattr(self.ski, "second_3d_base_to_base", False)))
        self.ski.render_3d_mode = str(payload.get("render_3d_mode", getattr(self.ski, "render_3d_mode", "shaded")))
        self.ski.background_3d_width_px = float(payload.get("background_3d_width_px", getattr(self.ski, "background_3d_width_px", 760.0)))
        self.ski.background_3d_height_px = float(payload.get("background_3d_height_px", getattr(self.ski, "background_3d_height_px", 1280.0)))
        self.ski.show_3d_background = bool(payload.get("show_3d_background", getattr(self.ski, "show_3d_background", True)))
        if self.ski.render_3d_mode not in {"shaded", "shaded_edges", "wireframe", "graphic"}:
            self.ski.render_3d_mode = "shaded"
        self.ski.show_3d = bool(self.appearance_panel.toggle_button.isChecked())
        if hasattr(self, "toggle_ski_snowboard_action"):
            self.toggle_ski_snowboard_action.blockSignals(True)
            self.toggle_ski_snowboard_action.setChecked(self.ski.show_ski_snowboard)
            self.toggle_ski_snowboard_action.setText(self._second_ski_toggle_label())
            self.toggle_ski_snowboard_action.blockSignals(False)
        self._sync_second_ski_layout_button()
        self.update_rot()
        self.refresh_3d_view_style_buttons()
        self.background_width_slider.blockSignals(True)
        self.background_height_slider.blockSignals(True)
        self.background_width_slider.setValue(int(round(getattr(self.ski, "background_3d_width_px", 760.0))))
        self.background_height_slider.setValue(int(round(getattr(self.ski, "background_3d_height_px", 1280.0))))
        self.background_width_slider.blockSignals(False)
        self.background_height_slider.blockSignals(False)
        self.background_toggle_button.blockSignals(True)
        self.background_toggle_button.setChecked(bool(getattr(self.ski, "show_3d_background", True)))
        self.background_toggle_button.blockSignals(False)
        self.update_3d_background_controls()
        self.ski.update()

    def _friendly_cnc_shape_name(self, shape_name):
        name = str(shape_name)
        outline_mode = getattr(self.ski, "outline_mode", "symmetric")
        if name == "ski_outline":
            if outline_mode == "snowboard":
                return "Snowboard Outline"
            return "Right Side Outline" if outline_mode == "splitboard" else "Right Ski Outline"
        if name == "left_ski_outline":
            return "Left Side Outline" if outline_mode == "splitboard" else "Left Ski Outline"
        if name == "both_ski_outlines":
            return "Both Side Outlines" if outline_mode == "splitboard" else "Both Ski Outlines"
        if name == "right_base_material":
            return "Right Base"
        if name == "left_base_material":
            return "Left Base"
        if name == "both_base_materials":
            return "Both Bases"
        if name == "camber_profile":
            return "Lower Mold/Camber"
        if name == "core_footprint":
            return "Right Core" if outline_mode in {"splitboard", "asymmetric"} else "Core"
        if name == "left_core_footprint":
            return "Left Core"
        if name == "both_core_footprints":
            return "Both Cores"
        if name == "tip_spacer" and outline_mode in {"splitboard", "asymmetric"}:
            return "Right Tip Spacer"
        if name == "tail_spacer" and outline_mode in {"splitboard", "asymmetric"}:
            return "Right Tail Spacer"
        if name == "sidewall_spacer_shell":
            return "Right Shell" if outline_mode in {"splitboard", "asymmetric"} else "Shell"
        if name == "left_tip_spacer":
            return "Left Tip Spacer"
        if name == "both_tip_spacers":
            return "Both Tip Spacers"
        if name == "left_tail_spacer":
            return "Left Tail Spacer"
        if name == "both_tail_spacers":
            return "Both Tail Spacers"
        if name == "left_sidewall_spacer_shell":
            return "Left Shell"
        if name == "both_sidewall_spacer_shells":
            return "Both Shells"
        return name.replace("_", " ").title()

    def _get_cnc_shapes(self):
        raw_shapes = self.ski.get_export_shapes(include_all=True)
        filtered = []
        hidden_names = {"core_profile"}
        for shape in raw_shapes:
            name = str(shape.get("name", ""))
            if not name:
                continue
            if name in hidden_names:
                continue
            if name.startswith("edge_inlay"):
                continue
            if name.startswith("sidewall") and name != "sidewall_spacer_shell":
                continue
            filtered.append(shape)
        return filtered

    def _shape_from_path_for_cnc(self, name, shape_path, closed=True, sample_path=True):
        pts = self._sample_qpath_loop_cm(shape_path, samples=2400) if sample_path and closed else []
        if sample_path and not closed:
            pts = self._sample_qpath_open_cm(shape_path, samples=2400)
        if not pts:
            pts = self.ski.path_to_fill_points_cm(shape_path, precision_scale=4.0)
        if not pts:
            return None
        return {"name": name, "layer": name, "closed": bool(closed), "points": pts}

    def _sample_qpath_loop_cm(self, qpath, samples=2400):
        if qpath is None or qpath.isEmpty():
            return []
        samples = max(80, int(samples))
        pts = []
        for i in range(samples):
            pt = qpath.pointAtPercent(i / float(samples))
            value = (-pt.y() / PIXELS_PER_CM, pt.x() / PIXELS_PER_CM)
            if not pts or abs(pts[-1][0] - value[0]) > 1e-9 or abs(pts[-1][1] - value[1]) > 1e-9:
                pts.append(value)
        if len(pts) >= 2 and abs(pts[0][0] - pts[-1][0]) <= 1e-9 and abs(pts[0][1] - pts[-1][1]) <= 1e-9:
            pts = pts[:-1]
        return pts
    def _sample_qpath_open_cm(self, qpath, samples=2400):
        if qpath is None or qpath.isEmpty():
            return []
        samples = max(2, int(samples))
        pts = []
        for i in range(samples + 1):
            pt = qpath.pointAtPercent(i / float(samples))
            value = (-pt.y() / PIXELS_PER_CM, pt.x() / PIXELS_PER_CM)
            if not pts or abs(pts[-1][0] - value[0]) > 1e-9 or abs(pts[-1][1] - value[1]) > 1e-9:
                pts.append(value)
        return pts

    def _build_cnc_shape(self, name, samples=1200):
        name = str(name or "")
        if name == "ski_outline":
            pts = self._sample_qpath_loop_cm(self.ski.build_full_shape(), samples=2400)
            return {"name": name, "layer": name, "closed": True, "points": pts} if pts else None
        if name == "left_ski_outline":
            if getattr(self.ski, "outline_mode", "symmetric") not in {"splitboard", "asymmetric"}:
                return None
            pts = self._sample_qpath_loop_cm(self.ski.build_second_ski_shape(), samples=2400)
            return {"name": name, "layer": name, "closed": True, "points": pts} if pts else None
        if name == "both_ski_outlines":
            right_pts = self._sample_qpath_loop_cm(self.ski.build_full_shape(), samples=2400)
            left_pts = self._sample_qpath_loop_cm(self.ski.build_second_ski_shape(), samples=2400)
            pts = right_pts + left_pts
            if not pts:
                return None
            return {"name": name, "layer": name, "closed": True, "points": pts, "disjoint_loops": True}
        if name == "camber_profile":
            pts = self.ski.build_camber_profile_export_points_cm(samples=2000)
            return {"name": name, "layer": name, "closed": True, "points": pts} if pts else None
        if name == "upper_mold":
            pts = self.ski.build_upper_mold_export_points_cm(samples=2000)
            return {"name": name, "layer": name, "closed": True, "points": pts} if pts else None
        if name == "base_material":
            return self._shape_from_path_for_cnc(name, self.ski.build_base_material_path(samples), closed=True)
        if name == "right_base_material":
            return self._shape_from_path_for_cnc(name, self.ski.build_base_material_path(samples), closed=True)
        if name == "left_base_material":
            return self._shape_from_path_for_cnc(name, self.ski.build_left_base_material_path(samples), closed=True)
        if name == "both_base_materials":
            shape = self._shape_from_path_for_cnc(name, self.ski.build_both_base_material_paths(samples), closed=True, sample_path=False)
            if shape is not None:
                shape["disjoint_loops"] = True
            return shape
        if name == "core_footprint":
            return self._shape_from_path_for_cnc(name, self.ski.build_core_footprint_path(samples), closed=True)
        if name == "left_core_footprint":
            return self._shape_from_path_for_cnc(name, self.ski.build_left_core_footprint_path(samples), closed=True)
        if name == "both_core_footprints":
            shape = self._shape_from_path_for_cnc(name, self.ski.build_both_core_footprint_paths(samples), closed=True, sample_path=False)
            if shape is not None:
                shape["disjoint_loops"] = True
            return shape
        if name == "tip_spacer":
            return self._shape_from_path_for_cnc(name, self.ski.build_tip_spacer_path(samples), closed=True)
        if name == "left_tip_spacer":
            return self._shape_from_path_for_cnc(name, self.ski.build_left_tip_spacer_path(samples), closed=True)
        if name == "both_tip_spacers":
            shape = self._shape_from_path_for_cnc(name, self.ski.build_both_tip_spacer_paths(samples), closed=True, sample_path=False)
            if shape is not None:
                shape["disjoint_loops"] = True
            return shape
        if name == "tail_spacer":
            return self._shape_from_path_for_cnc(name, self.ski.build_tail_spacer_path(samples), closed=True)
        if name == "left_tail_spacer":
            return self._shape_from_path_for_cnc(name, self.ski.build_left_tail_spacer_path(samples), closed=True)
        if name == "both_tail_spacers":
            shape = self._shape_from_path_for_cnc(name, self.ski.build_both_tail_spacer_paths(samples), closed=True, sample_path=False)
            if shape is not None:
                shape["disjoint_loops"] = True
            return shape
        if name == "sidewall_spacer_shell":
            return self._shape_from_path_for_cnc(name, self.ski.build_sidewall_spacer_shell_path(samples), closed=True)
        if name == "left_sidewall_spacer_shell":
            return self._shape_from_path_for_cnc(name, self.ski.build_left_sidewall_spacer_shell_path(samples), closed=True)
        if name == "both_sidewall_spacer_shells":
            shape = self._shape_from_path_for_cnc(name, self.ski.build_both_sidewall_spacer_shell_paths(samples), closed=True, sample_path=False)
            if shape is not None:
                shape["disjoint_loops"] = True
            return shape
        return None

    def _get_cnc_shape_names(self):
        outline_mode = getattr(self.ski, "outline_mode", "symmetric")
        if outline_mode in {"splitboard", "asymmetric"}:
            return [
                "left_ski_outline", "ski_outline", "both_ski_outlines",
                "left_base_material", "right_base_material", "both_base_materials",
                "left_core_footprint", "core_footprint", "both_core_footprints",
                "left_tip_spacer", "tip_spacer", "both_tip_spacers",
                "left_tail_spacer", "tail_spacer", "both_tail_spacers",
                "left_sidewall_spacer_shell", "sidewall_spacer_shell", "both_sidewall_spacer_shells",
                "upper_mold", "camber_profile",
            ]
        base_names = ["base_material"]
        if outline_mode in {"splitboard", "asymmetric"}:
            base_names = ["right_base_material", "left_base_material", "both_base_materials"]
        tip_spacer_names = ["tip_spacer"]
        tail_spacer_names = ["tail_spacer"]
        shell_names = ["sidewall_spacer_shell"]
        if outline_mode == "splitboard":
            tip_spacer_names = ["tip_spacer", "left_tip_spacer", "both_tip_spacers"]
            tail_spacer_names = ["tail_spacer", "left_tail_spacer", "both_tail_spacers"]
            shell_names = ["sidewall_spacer_shell", "left_sidewall_spacer_shell", "both_sidewall_spacer_shells"]
        core_names = ["core_footprint"]
        if outline_mode == "splitboard":
            core_names = ["core_footprint", "left_core_footprint", "both_core_footprints"]
        names = [
            "ski_outline",
        ]
        if outline_mode in {"splitboard", "asymmetric"}:
            names.append("left_ski_outline")
        if outline_mode == "splitboard":
            names.append("both_ski_outlines")
        names.extend([
            "camber_profile",
            "upper_mold",
            *base_names,
            *core_names,
            *tip_spacer_names,
            *tail_spacer_names,
            *shell_names,
        ])
        return names

    def _finish_startup_cnc_setup(self):
        if getattr(self, "_startup_cnc_setup_done", False):
            return
        self._startup_cnc_setup_done = True
        self.refresh_cnc_shape_buttons()

    def _selected_cnc_shape(self):
        shape = self._build_cnc_shape(self.selected_cnc_shape_name)
        if shape is not None:
            return shape
        for name in self._get_cnc_shape_names():
            shape = self._build_cnc_shape(name)
            if shape is not None:
                self.selected_cnc_shape_name = name
                return shape
        return None

    def _selected_cnc_shape_start_point_mm(self):
        shape = self._selected_cnc_shape()
        if shape is None:
            return None
        if self.cnc_operation_combo.currentText() in {"Boring", "Helical Boring"}:
            paths = self._boring_paths_mm(shape)
            if paths and paths[0]:
                first = paths[0][0]
                return (float(first[0]), float(first[1]))
            return None
        paths = self._shape_paths_mm_for_operation(shape)
        if not paths or not paths[0]:
            return None
        first = paths[0][0]
        return (float(first[0]), float(first[1]))

    def _polygon_centroid_mm(self, points_mm):
        pts = self._normalized_path_points_mm(points_mm)
        if not pts:
            return None
        if len(pts) < 3:
            xs = [float(x) for x, _ in pts]
            ys = [float(y) for _, y in pts]
            return ((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5)
        cross_sum = 0.0
        cx_sum = 0.0
        cy_sum = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            cross = x1 * y2 - x2 * y1
            cross_sum += cross
            cx_sum += (x1 + x2) * cross
            cy_sum += (y1 + y2) * cross
        if abs(cross_sum) <= 1e-9:
            xs = [float(x) for x, _ in pts]
            ys = [float(y) for _, y in pts]
            return ((min(xs) + max(xs)) * 0.5, (min(ys) + max(ys)) * 0.5)
        return (cx_sum / (3.0 * cross_sum), cy_sum / (3.0 * cross_sum))

    def _selected_cnc_shape_center_point_mm(self):
        shape = self._selected_cnc_shape()
        if shape is None:
            return None
        loops = self._shape_source_loops_mm(shape)
        weighted_x = 0.0
        weighted_y = 0.0
        total_area = 0.0
        fallback_points = []
        for loop in loops:
            centroid = self._polygon_centroid_mm(loop)
            if centroid is None:
                continue
            fallback_points.extend(loop)
            area = abs(self._polygon_area_mm2(loop))
            if area <= 1e-9:
                continue
            weighted_x += centroid[0] * area
            weighted_y += centroid[1] * area
            total_area += area
        if total_area > 1e-9:
            return (weighted_x / total_area, weighted_y / total_area)
        return self._polygon_centroid_mm(fallback_points)

    def _selected_cnc_shape_overlay_path(self):
        if not hasattr(self, "cnc_panel") or not self.cnc_panel.toggle_button.isChecked():
            return None
        shape = self._selected_cnc_shape()
        if shape is None:
            return None
        source_loops = self._shape_source_loops_mm(shape)
        if source_loops:
            overlay = QPainterPath()
            for pts in source_loops:
                if not pts:
                    continue
                first_x_mm, first_y_mm = pts[0]
                overlay.moveTo(QPointF(float(first_y_mm) * PIXELS_PER_MM, -float(first_x_mm) * PIXELS_PER_MM))
                for x_mm, y_mm in pts[1:]:
                    overlay.lineTo(QPointF(float(y_mm) * PIXELS_PER_MM, -float(x_mm) * PIXELS_PER_MM))
                if bool(shape.get("closed", True)) and len(pts) >= 3:
                    overlay.closeSubpath()
            if not overlay.isEmpty():
                return overlay
        pts = shape.get("points", [])
        if not pts:
            return None
        path = QPainterPath()
        first_x_cm, first_y_cm = pts[0]
        path.moveTo(QPointF(float(first_y_cm) * PIXELS_PER_CM, -float(first_x_cm) * PIXELS_PER_CM))
        for x_cm, y_cm in pts[1:]:
            path.lineTo(QPointF(float(y_cm) * PIXELS_PER_CM, -float(x_cm) * PIXELS_PER_CM))
        if bool(shape.get("closed", True)) and len(pts) >= 3:
            path.closeSubpath()
        return path

    def _toolpath_points_to_painter_path(self, pts_mm, closed=True):
        if not pts_mm:
            return QPainterPath()
        path = QPainterPath()
        first_x_mm, first_y_mm = pts_mm[0]
        path.moveTo(QPointF(float(first_y_mm) * PIXELS_PER_MM, -float(first_x_mm) * PIXELS_PER_MM))
        for x_mm, y_mm in pts_mm[1:]:
            path.lineTo(QPointF(float(y_mm) * PIXELS_PER_MM, -float(x_mm) * PIXELS_PER_MM))
        if closed and len(pts_mm) >= 3:
            path.closeSubpath()
        return path

    def _selected_cnc_toolpath_overlay_paths(self):
        if not hasattr(self, "cnc_panel") or not self.cnc_panel.toggle_button.isChecked():
            return []
        shape = self._selected_cnc_shape()
        if shape is None:
            return []
        op = self.cnc_operation_combo.currentText()
        if op in {"Boring", "Helical Boring"}:
            loops = self._boring_paths_mm(shape)
            return [self._toolpath_points_to_painter_path(loop, closed=(len(loop) > 1)) for loop in loops if loop]
        if op == "Pocket":
            loops = self._pocket_paths_mm(shape)
            return [self._toolpath_points_to_painter_path(loop, closed=(len(loop) >= 3)) for loop in loops if loop]
        path_sets = self._shape_paths_mm_for_operation(shape)
        if not path_sets:
            return []
        return [
            self._toolpath_points_to_painter_path(path_pts, closed=bool(shape.get("closed", True)))
            for path_pts in path_sets if path_pts
        ]

    def draw_selected_cnc_shape_overlay(self, painter):
        shape_path = self._selected_cnc_shape_overlay_path()
        tool_paths = [p for p in self._selected_cnc_toolpath_overlay_paths() if p is not None and not p.isEmpty()]
        if (shape_path is None or shape_path.isEmpty()) and not tool_paths:
            return
        painter.save()
        if shape_path is not None and not shape_path.isEmpty():
            shape_pen = QPen(QColor(90, 210, 255, 220), 3)
            shape_pen.setCosmetic(True)
            painter.setPen(shape_pen)
            painter.setBrush(QBrush(QColor(90, 210, 255, 28)))
            painter.drawPath(shape_path)
        if tool_paths:
            route_pen = QPen(QColor(255, 210, 90, 245), 2)
            route_pen.setCosmetic(True)
            painter.setPen(route_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            for tool_path in tool_paths:
                painter.drawPath(tool_path)
                start_pt = tool_path.pointAtPercent(0.0)
                painter.setBrush(QBrush(QColor(255, 210, 90, 245)))
                painter.drawEllipse(start_pt, 4.0, 4.0)
                painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.restore()

    def get_cnc_shape_start_stat_text(self):
        if not self.selected_cnc_shape_name:
            return ""
        start = self._selected_cnc_shape_start_point_mm()
        if start is None:
            return ""
        return f"CNC Bottom Reference Point: X {start[0]:.1f} mm, Y {start[1]:.1f} mm"

    def get_cnc_shape_center_stat_text(self):
        if not self.selected_cnc_shape_name:
            return ""
        center = self._selected_cnc_shape_center_point_mm()
        if center is None:
            return ""
        return f"CNC Center Point: X {center[0]:.1f} mm, Y {center[1]:.1f} mm"

    def _update_cnc_shape_button_styles(self):
        selected_style = (
            "QPushButton { background-color: #2E6F9E; border: 1px solid #79B8FF; "
            "border-radius: 8px; color: #F6FBFF; padding: 5px 8px; font-weight: 600; min-height: 28px; }"
            "QPushButton:hover { background-color: #377FB3; }"
            "QPushButton:pressed { background-color: #275D83; }"
        )
        normal_style = (
            "QPushButton { background-color: #3A3D42; border: 1px solid #5B616A; "
            "border-radius: 8px; color: #F2F2F2; padding: 5px 8px; min-height: 28px; }"
            "QPushButton:hover { background-color: #4A4E55; }"
            "QPushButton:pressed { background-color: #2D3035; }"
        )
        for name, btn in self.cnc_shape_buttons.items():
            btn.setStyleSheet(selected_style if name == self.selected_cnc_shape_name else normal_style)

    def refresh_cnc_shape_buttons(self):
        while self.cnc_shape_grid.count():
            item = self.cnc_shape_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                self.cnc_shape_button_group.removeButton(widget)
                widget.deleteLater()
        self.cnc_shape_buttons = {}

        unique_names = self._get_cnc_shape_names()

        if not unique_names:
            self.selected_cnc_shape_name = None
            self._last_generated_cnc_code = ""
            self._cnc_gcode_dirty = True
            self.cnc_preview.setPlainText("No exportable shapes are currently available.")
            if hasattr(self.ski, "update"):
                self.ski.update()
            return

        if self.selected_cnc_shape_name not in unique_names:
            self.selected_cnc_shape_name = unique_names[0]

        for idx, name in enumerate(unique_names):
            btn = QPushButton(self._friendly_cnc_shape_name(name))
            btn.setCheckable(True)
            btn.setChecked(name == self.selected_cnc_shape_name)
            btn.clicked.connect(lambda checked=False, n=name: self.select_cnc_shape(n))
            self.cnc_shape_button_group.addButton(btn)
            self.cnc_shape_buttons[name] = btn
            column_count = 3 if getattr(self.ski, "outline_mode", "symmetric") in {"splitboard", "asymmetric"} else 2
            self.cnc_shape_grid.addWidget(btn, idx // column_count, idx % column_count)

        self._update_cnc_shape_button_styles()
        self._mark_cnc_gcode_dirty(update_view=False)
        if not getattr(self, "_startup_initializing", False) and hasattr(self.ski, "update"):
            self.ski.update()

    def select_cnc_shape(self, shape_name):
        self.selected_cnc_shape_name = shape_name
        self._invalidate_cnc_toolpath_cache()
        for name, btn in self.cnc_shape_buttons.items():
            btn.blockSignals(True)
            btn.setChecked(name == shape_name)
            btn.blockSignals(False)
        self._update_cnc_shape_button_styles()
        self._reposition_selected_cnc_shape_in_workspace()
        self._mark_cnc_gcode_dirty(update_view=False)
        self.refresh_cnc_3d_preview_widget()
        self.ski.update()

    def _invalidate_cnc_toolpath_cache(self):
        self._cnc_toolpath_cache = {}
        self._cnc_preview_payload_cache_key = None
        self._cnc_preview_payload_cache_value = None

    def _normalized_path_points_mm(self, points_mm):
        pts = [(float(x), float(y)) for x, y in points_mm]
        if len(pts) >= 2 and abs(pts[0][0] - pts[-1][0]) <= 1e-9 and abs(pts[0][1] - pts[-1][1]) <= 1e-9:
            pts = pts[:-1]
        return pts

    def _cnc_shape_cache_key(self, shape):
        pts = self._normalized_path_points_mm([(float(x) * 10.0, float(y) * 10.0) for x, y in shape.get("points", [])])
        rounded = tuple((round(x, 3), round(y, 3)) for x, y in pts)
        return (str(shape.get("name", "")), bool(shape.get("closed", True)), rounded)

    def _clone_path_points_mm(self, points_mm):
        return [(float(x), float(y)) for x, y in points_mm]

    def _clone_path_loops_mm(self, loops_mm):
        return [[(float(x), float(y)) for x, y in loop] for loop in loops_mm]

    def _line_intersection(self, p1, p2, p3, p4):
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        x4, y4 = p4
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-9:
            return None
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
        return (px, py)

    def _path_from_points_mm(self, points_mm):
        pts = self._normalized_path_points_mm(points_mm)
        if len(pts) < 3:
            return QPainterPath(), []
        path = QPainterPath(QPointF(pts[0][0], pts[0][1]))
        for x, y in pts[1:]:
            path.lineTo(x, y)
        path.closeSubpath()
        return path, pts

    def _largest_polygon_from_path_mm(self, path):
        best = []
        best_area = -1.0
        for poly in path.toSubpathPolygons():
            pts = [(float(p.x()), float(p.y())) for p in poly]
            if len(pts) >= 2 and abs(pts[0][0] - pts[-1][0]) <= 1e-9 and abs(pts[0][1] - pts[-1][1]) <= 1e-9:
                pts = pts[:-1]
            if len(pts) < 3:
                continue
            area2 = 0.0
            for i in range(len(pts)):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % len(pts)]
                area2 += x1 * y2 - x2 * y1
            area = abs(area2) * 0.5
            if area > best_area:
                best_area = area
                best = pts
        return best

    def _polygon_area_mm2(self, points_mm):
        pts = self._normalized_path_points_mm(points_mm)
        if len(pts) < 3:
            return 0.0
        area2 = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            area2 += x1 * y2 - x2 * y1
        return abs(area2) * 0.5

    def _remove_near_collinear_points_mm(self, points_mm, eps=1e-6):
        pts = self._normalized_path_points_mm(points_mm)
        if len(pts) < 3:
            return pts
        cleaned = []
        count = len(pts)
        for i in range(count):
            prev = pts[i - 1]
            curr = pts[i]
            nxt = pts[(i + 1) % count]
            v1x = curr[0] - prev[0]
            v1y = curr[1] - prev[1]
            v2x = nxt[0] - curr[0]
            v2y = nxt[1] - curr[1]
            len1 = math.hypot(v1x, v1y)
            len2 = math.hypot(v2x, v2y)
            if len1 <= eps or len2 <= eps:
                continue
            cross = abs(v1x * v2y - v1y * v2x)
            if cross <= eps * max(len1, len2):
                dot = v1x * v2x + v1y * v2y
                if dot >= 0.0:
                    continue
            cleaned.append(curr)
        return self._normalized_path_points_mm(cleaned)

    def _clean_offset_loop_mm(self, points_mm, radius_mm=0.0):
        pts = self._normalized_path_points_mm(points_mm)
        if len(pts) < 3:
            return pts

        # Keep this cleanup conservative. The earlier version removed too much
        # valid geometry around the ski waist and other tighter transitions.
        # Here we only strip truly tiny duplicate/hair segments and only collapse
        # a corner when replacing it with the direct prev->next chord is clearly
        # a tiny local simplification rather than a real shape feature.
        op_name = self.cnc_operation_combo.currentText() if hasattr(self, "cnc_operation_combo") else ""
        if op_name == "Outside":
            short_limit = max(float(getattr(self, "cnc_outside_stub_filter_mm", 0.06)), abs(float(radius_mm)) * 0.04)
            bridge_limit = max(float(getattr(self, "cnc_outside_bridge_filter_mm", 0.20)), abs(float(radius_mm)) * 0.12)
            spike_area_factor = float(getattr(self, "cnc_outside_spike_area_factor", 0.30))
        else:
            short_limit = max(0.06, abs(float(radius_mm)) * 0.04)
            bridge_limit = max(0.20, abs(float(radius_mm)) * 0.12)
            spike_area_factor = 0.30

        changed = True
        passes = 0
        while changed and len(pts) >= 3 and passes < 4:
            passes += 1
            changed = False
            cleaned = []
            count = len(pts)
            for i in range(count):
                prev = pts[i - 1]
                curr = pts[i]
                nxt = pts[(i + 1) % count]

                v1x = curr[0] - prev[0]
                v1y = curr[1] - prev[1]
                v2x = nxt[0] - curr[0]
                v2y = nxt[1] - curr[1]
                len1 = math.hypot(v1x, v1y)
                len2 = math.hypot(v2x, v2y)

                if len1 <= 1e-9 or len2 <= 1e-9:
                    changed = True
                    continue

                remove = False
                if len1 < short_limit or len2 < short_limit:
                    # Only remove microscopic stubs. This is basically a size
                    # filter and avoids deleting larger valid sections.
                    remove = True
                else:
                    chord_x = nxt[0] - prev[0]
                    chord_y = nxt[1] - prev[1]
                    chord_len = math.hypot(chord_x, chord_y)
                    dot = (v1x * v2x + v1y * v2y) / max(1e-9, len1 * len2)
                    tri_area2 = abs(v1x * v2y - v1y * v2x)
                    max_len = max(len1, len2, chord_len, 1e-9)

                    # Remove a tiny spike only when both legs are short, the
                    # direct bridge is also short, and the point creates a very
                    # small local triangle. That focuses cleanup near small
                    # intersection artifacts instead of broad corners.
                    if (
                        min(len1, len2) < bridge_limit
                        and chord_len < (len1 + len2) * 0.75
                        and tri_area2 <= max_len * bridge_limit * spike_area_factor
                        and dot < 0.35
                    ):
                        remove = True
                    # Still merge nearly collinear runs, but only when the turn
                    # is extremely small.
                    elif tri_area2 <= max_len * 1e-6 and dot > 0.999:
                        remove = True

                if remove:
                    changed = True
                    continue
                cleaned.append(curr)

            pts = self._normalized_path_points_mm(cleaned if cleaned else pts)

        pts = self._remove_near_collinear_points_mm(pts)
        return pts

    def _offset_closed_polygon_stroke_fallback(self, points_mm, offset_mm):
        path, pts = self._path_from_points_mm(points_mm)
        if len(pts) < 3 or abs(offset_mm) < 1e-9 or path.isEmpty():
            return pts

        stroker = QPainterPathStroker()
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        stroker.setWidth(abs(offset_mm) * 2.0)
        border_band = stroker.createStroke(path).simplified()

        if offset_mm < 0.0:
            candidate = path.subtracted(border_band).simplified()
        else:
            candidate = path.united(border_band).simplified()

        result = self._largest_polygon_from_path_mm(candidate)
        result = self._remove_near_collinear_points_mm(result)
        original_area = self._polygon_area_mm2(pts)
        result_area = self._polygon_area_mm2(result)
        if len(result) < 3:
            return pts
        if offset_mm < 0.0 and result_area >= original_area - 1e-6:
            return pts
        if offset_mm > 0.0 and result_area <= original_area + 1e-6:
            return pts
        return result

    def _offset_closed_polygon(self, points_mm, offset_mm):
        pts = self._remove_near_collinear_points_mm(points_mm)
        if len(pts) < 3 or abs(offset_mm) < 1e-9:
            return pts

        signed_area = self.ski._polygon_signed_area_xy(pts)
        if abs(signed_area) <= 1e-9:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)

        orientation = 1.0 if signed_area > 0.0 else -1.0
        distance = float(offset_mm)
        shifted_lines = []
        count = len(pts)

        for i in range(count):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % count]
            dx = x2 - x1
            dy = y2 - y1
            seg_len = math.hypot(dx, dy)
            if seg_len <= 1e-9:
                continue
            # For CCW polygons, interior is on the left side of each edge.
            inward_nx = -dy / seg_len
            inward_ny = dx / seg_len
            move = -orientation * distance
            ox = inward_nx * move
            oy = inward_ny * move
            shifted_lines.append(((x1 + ox, y1 + oy), (x2 + ox, y2 + oy)))

        if len(shifted_lines) < 3:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)

        out = []
        line_count = len(shifted_lines)
        for i in range(line_count):
            prev_a, prev_b = shifted_lines[i - 1]
            curr_a, curr_b = shifted_lines[i]
            inter = self._line_intersection(prev_a, prev_b, curr_a, curr_b)
            if inter is None:
                inter = curr_a
            out.append((float(inter[0]), float(inter[1])))

        out = self._clean_offset_loop_mm(out, abs(distance))
        if len(out) < 3:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)

        original_area = self._polygon_area_mm2(pts)
        result_area = self._polygon_area_mm2(out)
        if result_area <= 1e-6:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)
        if distance > 0.0 and result_area <= original_area + 1e-6:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)
        if distance < 0.0 and result_area >= original_area - 1e-6:
            return self._offset_closed_polygon_stroke_fallback(pts, offset_mm)
        return out

    def _loops_mm_from_qpath(self, qpath, min_area_mm2=1.0):
        loops_mm = []
        try:
            loops_cm = self.ski.path_to_points_cm(qpath, precision_scale=4.0)
        except Exception:
            loops_cm = []
        for loop_cm in loops_cm:
            pts_mm = self._normalized_path_points_mm(
                [(float(x) * 10.0, float(y) * 10.0) for x, y in loop_cm]
            )
            if len(pts_mm) >= 3 and abs(self._polygon_area_mm2(pts_mm)) > float(min_area_mm2):
                loops_mm.append(pts_mm)
        loops_mm.sort(key=lambda pts: abs(self._polygon_area_mm2(pts)), reverse=True)
        return loops_mm

    def _single_loop_mm_from_shape_points(self, shape):
        pts_mm = self._normalized_path_points_mm(
            [(float(x) * 10.0, float(y) * 10.0) for x, y in shape.get("points", [])]
        )
        if len(pts_mm) >= 3 and abs(self._polygon_area_mm2(pts_mm)) > 1e-3:
            return [pts_mm]
        return []

    def _single_loop_mm_from_filled_qpath(self, qpath):
        pts_cm = self._sample_qpath_loop_cm(qpath, samples=2400)
        if not pts_cm:
            try:
                pts_cm = self.ski.path_to_fill_points_cm(qpath, precision_scale=4.0)
            except Exception:
                pts_cm = []
        pts_mm = self._normalized_path_points_mm(
            [(float(x) * 10.0, float(y) * 10.0) for x, y in pts_cm]
        )
        if len(pts_mm) >= 3 and abs(self._polygon_area_mm2(pts_mm)) > 1e-3:
            return [pts_mm]
        return []

    def _single_loop_mm_from_fill_polygon_qpath(self, qpath):
        try:
            pts_cm = self.ski.path_to_fill_points_cm(qpath, precision_scale=4.0)
        except Exception:
            pts_cm = []
        pts_mm = self._normalized_path_points_mm(
            [(float(x) * 10.0, float(y) * 10.0) for x, y in pts_cm]
        )
        if len(pts_mm) >= 3 and abs(self._polygon_area_mm2(pts_mm)) > 1e-3:
            return [pts_mm]
        return []

    def _base_dovetail_zone_ranges_mm(self, margin_mm=2.0):
        try:
            bounds = self.ski._get_dovetail_zone_bounds(station_count=360, outline_samples=1200)
        except Exception:
            return []

        try:
            min_x = float(bounds.get("min_x", 0.0)) * 10.0
            max_x = float(bounds.get("max_x", 0.0)) * 10.0
        except Exception:
            return []

        ranges = []
        tip_end_x = bounds.get("tip_end_x")
        tail_start_x = bounds.get("tail_start_x")
        if tip_end_x is not None:
            try:
                ranges.append((min_x - margin_mm, float(tip_end_x) * 10.0 + margin_mm))
            except Exception:
                pass
        if tail_start_x is not None:
            try:
                ranges.append((float(tail_start_x) * 10.0 - margin_mm, max_x + margin_mm))
            except Exception:
                pass
        return ranges

    def _point_x_in_ranges_mm(self, point_mm, ranges_mm):
        x = float(point_mm[0])
        return any(lo <= x <= hi for lo, hi in ranges_mm)

    def _clean_base_dovetail_spike_points_mm(self, loop_mm):
        pts = self._normalized_path_points_mm(loop_mm)
        if len(pts) < 5:
            return pts

        ranges = self._base_dovetail_zone_ranges_mm()
        if not ranges:
            return pts

        original_area = self._polygon_area_mm2(pts)
        if original_area <= 1e-6:
            return pts

        def dist(a, b):
            return math.hypot(float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))

        def removable_spike(prev_pt, curr_pt, next_pt):
            if not self._point_x_in_ranges_mm(curr_pt, ranges):
                return False
            len1 = dist(prev_pt, curr_pt)
            len2 = dist(curr_pt, next_pt)
            chord = dist(prev_pt, next_pt)
            if len1 <= 1e-9 or len2 <= 1e-9:
                return True

            v1x = float(curr_pt[0]) - float(prev_pt[0])
            v1y = float(curr_pt[1]) - float(prev_pt[1])
            v2x = float(next_pt[0]) - float(curr_pt[0])
            v2y = float(next_pt[1]) - float(curr_pt[1])
            cross = abs(v1x * v2y - v1y * v2x)
            max_len = max(len1, len2)
            min_len = min(len1, len2)

            # Tiny local hooks from polygon fill conversion should not become
            # CNC moves. Keep this small enough that real dovetail edges remain.
            if max_len <= 3.0 and chord <= 3.25 and cross <= 6.0:
                return True

            # A single bad valley vertex often appears as a needle: previous
            # and next are close together, while the current point is far away.
            if chord <= 4.0 and min_len >= 8.0 and max_len <= min_len * 2.75:
                return True

            # Remove duplicate-ish one-sided spurs without collapsing longer
            # dovetail geometry.
            if min_len <= 0.20 and chord <= max_len + 0.05 and max_len <= 8.0:
                return True

            return False

        cleaned = pts
        changed = True
        passes = 0
        area_limit = max(75.0, original_area * 0.0005)
        while changed and len(cleaned) >= 5 and passes < 3:
            passes += 1
            changed = False
            out = []
            count = len(cleaned)
            for i, curr in enumerate(cleaned):
                prev_pt = cleaned[i - 1]
                next_pt = cleaned[(i + 1) % count]
                if removable_spike(prev_pt, curr, next_pt):
                    candidate = out + cleaned[i + 1:]
                    if len(candidate) >= 3:
                        area_delta = abs(self._polygon_area_mm2(candidate) - original_area)
                        if area_delta <= area_limit:
                            changed = True
                            continue
                out.append(curr)
            cleaned = self._normalized_path_points_mm(out)

        if len(cleaned) < 3:
            return pts
        return cleaned

    def _shape_source_loops_mm(self, shape):
        name = str(shape.get("name", ""))
        if not bool(shape.get("closed", True)):
            path_sets = []
            raw_paths = shape.get("paths")
            if isinstance(raw_paths, (list, tuple)) and raw_paths:
                for raw in raw_paths:
                    pts_mm = self._normalized_path_points_mm(
                        [(float(x) * 10.0, float(y) * 10.0) for x, y in raw]
                    )
                    if len(pts_mm) >= 2:
                        path_sets.append(pts_mm)
            else:
                pts_mm = self._normalized_path_points_mm(
                    [(float(x) * 10.0, float(y) * 10.0) for x, y in shape.get("points", [])]
                )
                if len(pts_mm) >= 2:
                    path_sets.append(pts_mm)
            return path_sets
        base_shape_names = {"base_material", "right_base_material", "left_base_material", "both_base_materials"}
        loops_mm = []
        if name == "both_ski_outlines":
            loops_mm = (
                self._single_loop_mm_from_filled_qpath(self.ski.build_full_shape())
                + self._single_loop_mm_from_filled_qpath(self.ski.build_second_ski_shape())
            )
            if loops_mm:
                return loops_mm
        elif name in {"base_material", "right_base_material"}:
            loops_mm = self._single_loop_mm_from_fill_polygon_qpath(self.ski.build_base_material_path())
        elif name == "left_base_material":
            loops_mm = self._single_loop_mm_from_fill_polygon_qpath(self.ski.build_left_base_material_path())
        elif name == "both_base_materials":
            loops_mm = (
                self._single_loop_mm_from_fill_polygon_qpath(self.ski.build_base_material_path())
                + self._single_loop_mm_from_fill_polygon_qpath(self.ski.build_left_base_material_path())
            )
        if loops_mm and name in base_shape_names:
            return [self._clean_base_dovetail_spike_points_mm(loop) for loop in loops_mm]
        elif name == "core_footprint":
            loops_mm = self._single_loop_mm_from_filled_qpath(self.ski.build_core_footprint_path())
            if loops_mm:
                return loops_mm
        elif name == "left_core_footprint":
            loops_mm = self._single_loop_mm_from_filled_qpath(self.ski.build_left_core_footprint_path())
            if loops_mm:
                return loops_mm
        elif name == "both_core_footprints":
            loops_mm = (
                self._single_loop_mm_from_filled_qpath(self.ski.build_core_footprint_path())
                + self._single_loop_mm_from_filled_qpath(self.ski.build_left_core_footprint_path())
            )
            if loops_mm:
                return loops_mm
        elif name == "sidewall_spacer_shell":
            loops_mm = self._loops_mm_from_qpath(self.ski.build_sidewall_spacer_shell_path())
            if loops_mm:
                return loops_mm
        elif name == "left_sidewall_spacer_shell":
            loops_mm = self._loops_mm_from_qpath(self.ski.build_left_sidewall_spacer_shell_path())
            if loops_mm:
                return loops_mm
        elif name == "both_sidewall_spacer_shells":
            loops_mm = (
                self._loops_mm_from_qpath(self.ski.build_sidewall_spacer_shell_path())
                + self._loops_mm_from_qpath(self.ski.build_left_sidewall_spacer_shell_path())
            )
            if loops_mm:
                return loops_mm
        elif name == "tip_spacer":
            loops_mm = self._single_loop_mm_from_shape_points(shape)
            if not loops_mm:
                loops_mm = self._loops_mm_from_qpath(self.ski.build_tip_spacer_path())
            if loops_mm:
                return loops_mm
        elif name == "left_tip_spacer":
            loops_mm = self._single_loop_mm_from_filled_qpath(self.ski.build_left_tip_spacer_path())
            if not loops_mm:
                loops_mm = self._loops_mm_from_qpath(self.ski.build_left_tip_spacer_path())
            if loops_mm:
                return loops_mm
        elif name == "both_tip_spacers":
            loops_mm = (
                self._single_loop_mm_from_filled_qpath(self.ski.build_tip_spacer_path())
                + self._single_loop_mm_from_filled_qpath(self.ski.build_left_tip_spacer_path())
            )
            if loops_mm:
                return loops_mm
        elif name == "tail_spacer":
            loops_mm = self._single_loop_mm_from_shape_points(shape)
            if not loops_mm:
                loops_mm = self._loops_mm_from_qpath(self.ski.build_tail_spacer_path())
            if loops_mm:
                return loops_mm
        elif name == "left_tail_spacer":
            loops_mm = self._single_loop_mm_from_filled_qpath(self.ski.build_left_tail_spacer_path())
            if not loops_mm:
                loops_mm = self._loops_mm_from_qpath(self.ski.build_left_tail_spacer_path())
            if loops_mm:
                return loops_mm
        elif name == "both_tail_spacers":
            loops_mm = (
                self._single_loop_mm_from_filled_qpath(self.ski.build_tail_spacer_path())
                + self._single_loop_mm_from_filled_qpath(self.ski.build_left_tail_spacer_path())
            )
            if loops_mm:
                return loops_mm
        else:
            loops_mm = []
        if loops_mm and name in base_shape_names:
            return [self._clean_base_dovetail_spike_points_mm(loop) for loop in loops_mm]
        if loops_mm:
            return loops_mm
        pts_mm = self._normalized_path_points_mm([(float(x) * 10.0, float(y) * 10.0) for x, y in shape.get("points", [])])
        if not pts_mm:
            return []
        # Preserve the original point sequence for on-line machining so explicit
        # closing edges, like the camber profile's straight left edge, are not
        # simplified away before the toolpath is built.
        return [pts_mm] if len(pts_mm) >= 3 else []

    def _shape_paths_mm_for_operation(self, shape):
        op = self.cnc_operation_combo.currentText()
        radius = max(0.0, float(self.cnc_tool_diameter_spin.value()) * 0.5)
        cache_key = ("shape_paths", self._cnc_shape_cache_key(shape), op, round(radius, 4), bool(shape.get("disjoint_loops", False)))
        cached = self._cnc_toolpath_cache.get(cache_key)
        if cached is not None:
            return self._clone_path_loops_mm(cached)

        base_loops = self._shape_source_loops_mm(shape)
        if not base_loops:
            self._cnc_toolpath_cache[cache_key] = []
            return []

        result_loops = []
        multi_loop = len(base_loops) > 1
        disjoint_loops = bool(shape.get("disjoint_loops", False))
        for loop_index, loop in enumerate(base_loops):
            offset_sign = 0.0
            if not bool(shape.get("closed", True)):
                offset_sign = 0.0
            elif op == "Outside":
                offset_sign = 1.0
            elif op == "Inside":
                offset_sign = -1.0

            if multi_loop and loop_index > 0 and offset_sign != 0.0 and not disjoint_loops:
                offset_sign *= -1.0

            if offset_sign != 0.0:
                result = self._offset_closed_polygon(loop, radius * offset_sign)
                result = self._clean_offset_loop_mm(result, radius)
                result = self._normalized_path_points_mm(result)
            else:
                # Keep on-line paths as faithful as possible to the original
                # shape definition so explicit border segments are preserved.
                result = self._normalized_path_points_mm(loop)
                if bool(shape.get("closed", True)) and len(result) >= 2 and result[0] != result[-1]:
                    result = result + [result[0]]

            if not bool(shape.get("closed", True)):
                if len(result) >= 2:
                    result_loops.append(result)
                continue

            area_source = result[:-1] if len(result) >= 2 and result[0] == result[-1] else result
            if len(area_source) >= 3 and abs(self._polygon_area_mm2(area_source)) > 1e-3:
                result_loops.append(result)

        self._cnc_toolpath_cache[cache_key] = self._clone_path_loops_mm(result_loops)
        return self._clone_path_loops_mm(result_loops)

    def _shape_points_mm_for_operation(self, shape):
        paths = self._shape_paths_mm_for_operation(shape)
        if not paths:
            return []
        return self._clone_path_points_mm(paths[0])

    def _boring_hole_centers_mm(self, shape):
        name = str(shape.get("name", "")) if shape is not None else ""
        if name == "camber_profile":
            center_sets = [self.ski._mold_hole_centers(upper=False)]
        elif name == "upper_mold":
            center_sets = [self.ski._mold_hole_centers(upper=True)]
        else:
            return []
        centers = []
        for center_set in center_sets:
            for pt in center_set:
                centers.append((-float(pt.y()) / PIXELS_PER_MM, float(pt.x()) / PIXELS_PER_MM))
        return centers

    def _boring_circle_path_mm(self, center_mm, segments=72):
        tool_diameter = max(0.1, float(self.cnc_tool_diameter_spin.value()))
        hole_diameter = max(0.1, float(getattr(self.ski, "mold_hole_diameter_mm", 20.0)))
        radius = max(0.0, (hole_diameter - tool_diameter) * 0.5)
        cx, cy = float(center_mm[0]), float(center_mm[1])
        if radius <= 1e-6:
            return [(cx, cy)]
        pts = []
        for i in range(max(12, int(segments)) + 1):
            angle = (2.0 * math.pi * i) / max(12, int(segments))
            pts.append((cx + math.cos(angle) * radius, cy + math.sin(angle) * radius))
        return pts

    def _boring_paths_mm(self, shape):
        return [self._boring_circle_path_mm(center) for center in self._boring_hole_centers_mm(shape)]

    def _helical_boring_path_xyz_mm(self, center_mm, surface_z_mm, final_z_mm):
        tool_diameter = max(0.1, float(self.cnc_tool_diameter_spin.value()))
        hole_diameter = max(0.1, float(getattr(self.ski, "mold_hole_diameter_mm", 20.0)))
        radius = max(0.0, (hole_diameter - tool_diameter) * 0.5)
        cx, cy = float(center_mm[0]), float(center_mm[1])
        surface_z = float(surface_z_mm)
        final_z = float(final_z_mm)
        total_depth = max(0.0, surface_z - final_z)
        if radius <= 1e-6 or total_depth <= 1e-6:
            return [(cx, cy, surface_z), (cx, cy, final_z)]

        helix_angle = math.radians(max(0.1, min(89.0, float(self.cnc_helix_angle_spin.value()))))
        drop_per_rev = max(1e-6, (2.0 * math.pi * radius) * math.tan(helix_angle))
        revolutions = max(total_depth / drop_per_rev, 0.25)
        helix_segments = max(12, int(math.ceil(revolutions * 72.0)))
        pts = []
        for i in range(helix_segments + 1):
            t = i / float(helix_segments)
            theta = 2.0 * math.pi * revolutions * t
            pts.append((
                cx + math.cos(theta) * radius,
                cy + math.sin(theta) * radius,
                surface_z - total_depth * t,
            ))

        start_theta = 2.0 * math.pi * revolutions
        cleanup_segments = 72
        for i in range(1, cleanup_segments + 1):
            theta = start_theta + (2.0 * math.pi * i / cleanup_segments)
            pts.append((
                cx + math.cos(theta) * radius,
                cy + math.sin(theta) * radius,
                final_z,
            ))
        return pts

    def _scanline_segments_in_polygon_mm(self, polygon_mm, scan_y_mm):
        return self._scanline_segments_in_loops_mm([polygon_mm], scan_y_mm)

    def _scanline_segments_in_loops_mm(self, loops_mm, scan_y_mm):
        intersections = []
        for loop in loops_mm:
            pts = self._normalized_path_points_mm(loop)
            if len(pts) < 3:
                continue
            for i in range(len(pts)):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % len(pts)]
                if abs(y2 - y1) <= 1e-9:
                    continue
                y_min = min(y1, y2)
                y_max = max(y1, y2)
                if not (y_min <= scan_y_mm < y_max):
                    continue
                t = (scan_y_mm - y1) / (y2 - y1)
                intersections.append(x1 + t * (x2 - x1))
        intersections.sort()
        spans = []
        for i in range(0, len(intersections) - 1, 2):
            x_start = float(intersections[i])
            x_end = float(intersections[i + 1])
            if x_end - x_start > 1e-6:
                spans.append((x_start, x_end))
        return spans

    def _pocket_paths_mm(self, shape):
        tool_diameter = max(0.1, float(self.cnc_tool_diameter_spin.value()))
        cache_key = (
            "pocket",
            self._cnc_shape_cache_key(shape),
            round(tool_diameter, 4),
            bool(shape.get("disjoint_loops", False)),
        )
        cached = self._cnc_toolpath_cache.get(cache_key)
        if cached is not None:
            return self._clone_path_loops_mm(cached)

        base_loops = self._shape_source_loops_mm(shape)
        if not base_loops:
            return []

        radius = max(0.0, tool_diameter * 0.5)
        inner_loops = []
        multi_loop = len(base_loops) > 1
        disjoint_loops = bool(shape.get("disjoint_loops", False))
        for loop_index, loop in enumerate(base_loops):
            offset_sign = -1.0
            if multi_loop and loop_index > 0 and not disjoint_loops:
                offset_sign = 1.0
            inner = self._normalized_path_points_mm(self._offset_closed_polygon(loop, radius * offset_sign))
            inner = self._remove_near_collinear_points_mm(inner)
            if len(inner) >= 3 and abs(self._polygon_area_mm2(inner)) > 1e-3:
                inner_loops.append(inner)

        if not inner_loops:
            self._cnc_toolpath_cache[cache_key] = []
            return []

        ys = [p[1] for loop in inner_loops for p in loop]
        min_y = min(ys)
        max_y = max(ys)
        step_over = max(0.75, tool_diameter * 0.8)
        loops = [self._clone_path_points_mm(loop) for loop in inner_loops]

        span = max_y - min_y
        line_count = max(1, int(math.floor(span / max(step_over, 1e-6))))
        reverse = False
        for i in range(line_count + 1):
            y = min_y + i * step_over
            if y > max_y + 1e-6:
                break
            spans = self._scanline_segments_in_loops_mm(inner_loops, y)
            if not spans:
                continue
            for x_start, x_end in spans:
                if reverse:
                    loops.append([(x_end, y), (x_start, y)])
                else:
                    loops.append([(x_start, y), (x_end, y)])
                reverse = not reverse

        self._cnc_toolpath_cache[cache_key] = self._clone_path_loops_mm(loops)
        return self._clone_path_loops_mm(loops)

    def _depth_from_core_profile_mm(self, length_mm):
        length_cm = float(length_mm) / 10.0
        try:
            profile = list(self.ski.get_thickness_profile_cm())
        except Exception:
            profile = []

        if not profile:
            return 0.0

        try:
            thickness_cm = float(self.ski.get_thickness_at_length(length_cm))
        except Exception:
            thickness_cm = 0.0

        thickness_cm = max(0.0, thickness_cm)

        if getattr(self, "cnc_depth_profile_invert_check", None) is not None and self.cnc_depth_profile_invert_check.isChecked():
            thickness_values = [float(p[1]) for p in profile]
            if thickness_values:
                min_thickness_cm = min(thickness_values)
                max_thickness_cm = max(thickness_values)
                mirrored_cm = min_thickness_cm + max_thickness_cm - thickness_cm
                thickness_cm = max(0.0, mirrored_cm)

        return thickness_cm * 10.0

    def _densify_profile_path_xy_mm(self, path_xy_mm, closed=False, max_step_mm=5.0):
        pts = [(float(x), float(y)) for x, y in path_xy_mm]
        if len(pts) < 2:
            return pts

        max_step_mm = max(1.0, float(max_step_mm))
        densified = [pts[0]]
        segment_pairs = list(zip(pts[:-1], pts[1:]))
        if closed and pts[0] != pts[-1]:
            segment_pairs.append((pts[-1], pts[0]))

        for (x0, y0), (x1, y1) in segment_pairs:
            dx = x1 - x0
            dy = y1 - y0
            dist = math.hypot(dx, dy)
            steps = max(1, int(math.ceil(dist / max_step_mm)))
            for step in range(1, steps + 1):
                t = step / steps
                densified.append((x0 + dx * t, y0 + dy * t))

        if not closed and pts[-1] != densified[-1]:
            densified.append(pts[-1])
        return densified

    def _profile_follow_step_mm(self):
        tool_diameter = max(0.1, float(self.cnc_tool_diameter_spin.value()))
        return max(0.75, min(2.5, tool_diameter * 0.35))

    def _path_points_xyz_mm(self, path_xy_mm, closed=False):
        use_profile = bool(self.cnc_depth_mode_check.isChecked())
        if use_profile:
            xy_points = self._densify_profile_path_xy_mm(
                path_xy_mm,
                closed=closed,
                max_step_mm=self._profile_follow_step_mm(),
            )
        else:
            xy_points = [(float(x), float(y)) for x, y in path_xy_mm]
        xyz = []
        for x_mm, y_mm in xy_points:
            if use_profile:
                z_mm = -self._depth_from_core_profile_mm(x_mm)
            else:
                z_mm = -abs(float(self.cnc_cut_depth_spin.value()))
            xyz.append((float(x_mm), float(y_mm), float(z_mm)))
        return xyz

    def _cnc_ramp_enabled_for_current_op(self):
        if not hasattr(self, "cnc_ramp_entry_check"):
            return False
        if not self.cnc_ramp_entry_check.isChecked():
            return False
        return self.cnc_operation_combo.currentText() in {"On Line", "Outside"}

    def _build_ramp_entry_segments(self, xyz_path, safe_z):
        if not self._cnc_ramp_enabled_for_current_op() or len(xyz_path) < 2:
            return [], xyz_path
        angle_deg = max(0.1, float(self.cnc_ramp_angle_spin.value()))
        angle_rad = math.radians(min(89.0, angle_deg))
        tan_angle = math.tan(angle_rad)
        if tan_angle <= 1e-6:
            return [], xyz_path
        target_depth = abs(float(xyz_path[0][2]))
        if target_depth <= 1e-6:
            return [], xyz_path
        ramp_len = target_depth / tan_angle
        if ramp_len <= 0.25:
            return [], xyz_path

        total_len = 0.0
        for (x0, y0, _), (x1, y1, _) in zip(xyz_path[:-1], xyz_path[1:]):
            total_len += math.hypot(x1 - x0, y1 - y0)
        if total_len < max(1.0, ramp_len * 0.8):
            return [], xyz_path

        def _same_xy(a, b, tol=1e-6):
            return abs(float(a[0]) - float(b[0])) <= tol and abs(float(a[1]) - float(b[1])) <= tol

        closed_loop = len(xyz_path) >= 3 and _same_xy(xyz_path[0], xyz_path[-1])
        start = xyz_path[0]
        ramp_pts = [(start[0], start[1], safe_z)]
        consumed = 0.0
        remainder = []
        for idx, (p0, p1) in enumerate(zip(xyz_path[:-1], xyz_path[1:])):
            x0, y0, _ = p0
            x1, y1, _ = p1
            seg_len = math.hypot(x1 - x0, y1 - y0)
            if seg_len <= 1e-9:
                continue
            next_consumed = consumed + seg_len
            if next_consumed >= ramp_len:
                t = (ramp_len - consumed) / seg_len
                t = max(0.0, min(1.0, t))
                ex = x0 + (x1 - x0) * t
                ey = y0 + (y1 - y0) * t
                ez = -target_depth
                end_pt = (ex, ey, ez)
                if ramp_pts[-1] != end_pt:
                    ramp_pts.append(end_pt)
                remainder = [end_pt]
                if t < 1.0 - 1e-9:
                    remainder.append((x1, y1, p1[2]))
                remainder.extend(xyz_path[idx + 2:])
                if closed_loop:
                    remainder.extend(xyz_path[1:idx + 1])
                    remainder.append(end_pt)
                break
            frac = next_consumed / ramp_len
            z = safe_z + (-target_depth - safe_z) * frac
            ramp_pts.append((x1, y1, z))
            consumed = next_consumed

        if len(ramp_pts) < 2 or not remainder:
            return [], xyz_path
        cleaned_remainder = [remainder[0]]
        for pt in remainder[1:]:
            if pt != cleaned_remainder[-1]:
                cleaned_remainder.append(pt)
        return ramp_pts, cleaned_remainder

    def _selected_cnc_3d_preview_paths(self):
        if not self.should_show_main_window_cnc_view():
            return []
        shape = self._selected_cnc_shape()
        if shape is None:
            return []
        op = self.cnc_operation_combo.currentText()
        if op in {"Boring", "Helical Boring"}:
            loops = self._boring_paths_mm(shape)
            return [self._path_points_xyz_mm(loop, closed=(len(loop) > 1)) for loop in loops if loop]
        if op == "Pocket":
            loops = self._pocket_paths_mm(shape)
            return [self._path_points_xyz_mm(loop, closed=False) for loop in loops if loop]
        path_sets = self._shape_paths_mm_for_operation(shape)
        if not path_sets:
            return []
        return [
            self._path_points_xyz_mm(path_pts, closed=bool(shape.get("closed", True) and op != "Pocket"))
            for path_pts in path_sets if path_pts
        ]

    def _cnc_design_xy_to_machine_xy(self, x_mm, y_mm):
        return (float(y_mm), float(x_mm))

    def _cnc_design_xyz_to_machine_xyz(self, pt):
        return (float(pt[1]), float(pt[0]), float(pt[2]))

    def _segment_groups_from_cnc_gcode(self, code):
        start_x = float(self.cnc_start_x_spin.value()) if hasattr(self, "cnc_start_x_spin") else 0.0
        start_y = float(self.cnc_start_y_spin.value()) if hasattr(self, "cnc_start_y_spin") else 0.0
        current = (start_x, start_y, 0.0)
        motion_mode = 'G0'
        current_feed = None
        groups = []
        current_group = {'segments': [], 'path': [current]}

        def _same_point(a, b, tol=1e-6):
            return (
                abs(float(a[0]) - float(b[0])) <= tol
                and abs(float(a[1]) - float(b[1])) <= tol
                and abs(float(a[2]) - float(b[2])) <= tol
            )

        def _classify_segment(mode, start_pt, end_pt):
            sx, sy, sz = map(float, start_pt)
            ex, ey, ez = map(float, end_pt)
            same_xy = abs(sx - ex) <= 1e-6 and abs(sy - ey) <= 1e-6
            moving_xy = abs(sx - ex) > 1e-6 or abs(sy - ey) > 1e-6
            moving_z = abs(sz - ez) > 1e-6
            if mode == 'G0':
                return 'rapid'
            if same_xy and moving_z and ez < sz:
                return 'plunge'
            if moving_xy and moving_z:
                return 'ramp'
            return 'mill'

        def _begin_new_group():
            nonlocal current_group
            if current_group.get('segments'):
                groups.append(current_group)
            current_group = {'segments': [], 'path': [current]}

        for raw_line in str(code or '').splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(';'):
                if line.startswith('; Pass') or line.startswith('; Loop') or line.startswith('; 3D profile loop') or line.startswith('; Copy'):
                    _begin_new_group()
                continue
            line_no_comment = line.split(';', 1)[0].strip()
            if not line_no_comment:
                continue
            tokens = line_no_comment.split()
            mode = motion_mode
            x = current[0]
            y = current[1]
            z = current[2]
            line_feed = current_feed
            for token in tokens:
                upper = token.upper()
                if upper in {'G0', 'G00'}:
                    mode = 'G0'
                    continue
                if upper in {'G1', 'G01'}:
                    mode = 'G1'
                    continue
                if upper.startswith('X'):
                    try:
                        x = float(token[1:])
                    except Exception:
                        pass
                elif upper.startswith('Y'):
                    try:
                        y = float(token[1:])
                    except Exception:
                        pass
                elif upper.startswith('Z'):
                    try:
                        z = float(token[1:])
                    except Exception:
                        pass
                elif upper.startswith('F'):
                    try:
                        line_feed = float(token[1:])
                    except Exception:
                        pass
            motion_mode = mode
            current_feed = line_feed
            end_pt = (float(x), float(y), float(z))
            if _same_point(current, end_pt):
                continue
            seg_type = _classify_segment(mode, current, end_pt)
            seg_feed = None if seg_type == 'rapid' else (float(line_feed) if line_feed is not None else None)
            current_group['segments'].append((current, end_pt, seg_type, seg_feed))
            current_group['path'].append(end_pt)
            current = end_pt

        if current_group.get('segments'):
            groups.append(current_group)
        return groups

    def _cnc_preview_color_mode(self):
        combo = getattr(self, 'cnc_preview_color_mode_combo', None)
        if combo is None:
            return 'feed'
        text = str(combo.currentText()).strip().lower()
        return 'motion' if 'motion' in text else 'feed'

    def _cnc_feed_band_color(self, feed_value, alpha=245):
        if feed_value is None:
            return QColor(0, 180, 180, alpha)
        clamped = max(0.0, min(2000.0, float(feed_value)))
        t = clamped / 2000.0
        return QColor(0, int(round(255.0 * (1.0 - t))), int(round(255.0 * t)), alpha)

    def _cnc_segment_color(self, seg_type, feed_value=None, alpha=245):
        if seg_type == 'rapid':
            return QColor(255, 90, 90, alpha)
        if self._cnc_preview_color_mode() == 'motion':
            if seg_type == 'plunge':
                return QColor(90, 210, 255, alpha)
            if seg_type == 'ramp':
                return QColor(145, 255, 145, alpha)
            return QColor(255, 210, 90, alpha)
        return self._cnc_feed_band_color(feed_value, alpha)

    def _cnc_segment_pen(self, seg_type, feed_value=None, width=2.0):
        pen = QPen(self._cnc_segment_color(seg_type, feed_value, 245), width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        return pen

    def _selected_cnc_3d_preview_segments(self):
        if not self.should_show_main_window_cnc_view():
            return []
        return self._segment_groups_from_cnc_gcode(self.build_cnc_gcode())

    def _cnc_preview_payload_key(self):
        return (
            bool(self.should_show_main_window_cnc_view()),
            str(self.selected_cnc_shape_name),
            self.cnc_operation_combo.currentText() if hasattr(self, 'cnc_operation_combo') else '',
            round(float(self.cnc_safety_z_spin.value()), 4) if hasattr(self, 'cnc_safety_z_spin') else 0.0,
            round(float(self.cnc_workspace_x_spin.value()), 4) if hasattr(self, 'cnc_workspace_x_spin') else 0.0,
            round(float(self.cnc_workspace_y_spin.value()), 4) if hasattr(self, 'cnc_workspace_y_spin') else 0.0,
            round(float(self.cnc_workspace_z_spin.value()), 4) if hasattr(self, 'cnc_workspace_z_spin') else 0.0,
            tuple(round(float(v), 4) for v in self._get_cnc_workspace_origin_xyz()),
            bool(self._show_cnc_machine_boundary()),
            round(float(self.cnc_start_x_spin.value()), 4) if hasattr(self, 'cnc_start_x_spin') else 0.0,
            round(float(self.cnc_start_y_spin.value()), 4) if hasattr(self, 'cnc_start_y_spin') else 0.0,
            round(float(self.cnc_cut_depth_spin.value()), 4) if hasattr(self, 'cnc_cut_depth_spin') else 0.0,
            round(float(self.cnc_stepdown_spin.value()), 4) if hasattr(self, 'cnc_stepdown_spin') else 0.0,
            round(float(self.cnc_feed_rate_spin.value()), 4) if hasattr(self, 'cnc_feed_rate_spin') else 0.0,
            round(float(self.cnc_plunge_rate_spin.value()), 4) if hasattr(self, 'cnc_plunge_rate_spin') else 0.0,
            round(float(self.cnc_spindle_spin.value()), 4) if hasattr(self, 'cnc_spindle_spin') else 0.0,
            bool(self.cnc_depth_mode_check.isChecked()) if hasattr(self, 'cnc_depth_mode_check') else False,
            round(float(self.cnc_ramp_angle_spin.value()), 4) if hasattr(self, 'cnc_ramp_angle_spin') else 0.0,
            round(float(self.cnc_ramp_feed_rate_spin.value()), 4) if hasattr(self, 'cnc_ramp_feed_rate_spin') else 0.0,
            round(float(self.cnc_helix_angle_spin.value()), 4) if hasattr(self, 'cnc_helix_angle_spin') else 0.0,
            bool(self.cnc_ramp_entry_check.isChecked()) if hasattr(self, 'cnc_ramp_entry_check') else False,
            bool(self._cnc_duplicate_enabled()),
            tuple(round(float(v), 4) for v in self._get_cnc_duplicate_offset_xy()),
            tuple(round(float(v), 4) for v in self._get_cnc_preview_offset_xyz()),
        )

    def _get_cached_cnc_preview_payload(self):
        key = self._cnc_preview_payload_key()
        if key == self._cnc_preview_payload_cache_key and self._cnc_preview_payload_cache_value is not None:
            return self._cnc_preview_payload_cache_value
        segment_groups = self._selected_cnc_3d_preview_segments()
        workspace = (
            float(self.cnc_workspace_x_spin.value()),
            float(self.cnc_workspace_y_spin.value()),
            float(self.cnc_workspace_z_spin.value()),
        )
        workspace_origin = self._get_cnc_workspace_origin_xyz()
        start_point = (
            float(self.cnc_start_x_spin.value()),
            float(self.cnc_start_y_spin.value()),
            0.0,
        )
        entry_point = start_point
        payload = (segment_groups, workspace, start_point, entry_point, (0.0, 0.0), workspace_origin, self._show_cnc_machine_boundary())
        self._cnc_preview_payload_cache_key = key
        self._cnc_preview_payload_cache_value = payload
        return payload

    def build_cnc_gcode(self):
        selected = self._selected_cnc_shape()
        if selected is None:
            return "; No shape selected or available.\n"
        self._update_cnc_shape_button_styles()

        op = self.cnc_operation_combo.currentText()
        safe_z = float(self.cnc_safety_z_spin.value())
        start_x = float(self.cnc_start_x_spin.value())
        start_y = float(self.cnc_start_y_spin.value())
        cut_depth = abs(float(self.cnc_cut_depth_spin.value()))
        stepdown = max(0.001, abs(float(self.cnc_stepdown_spin.value())))
        feed = float(self.cnc_feed_rate_spin.value())
        plunge = float(self.cnc_plunge_rate_spin.value())
        spindle = int(round(float(self.cnc_spindle_spin.value())))
        use_profile = bool(self.cnc_depth_mode_check.isChecked())
        if op in {"Boring", "Helical Boring"}:
            use_profile = False

        if op == "Pocket":
            paths = self._pocket_paths_mm(selected)
        elif op in {"Boring", "Helical Boring"}:
            paths = self._boring_paths_mm(selected)
        else:
            paths = self._shape_paths_mm_for_operation(selected)

        if not paths:
            return "; Unable to generate a valid toolpath from the selected shape.\n"

        lines = []
        lines.append("; Simple CNC toolpath generated from ski design geometry")
        lines.append(f"; Shape: {selected.get('name', '')}")
        lines.append(f"; Operation: {op}")
        lines.append(f"; Tool diameter: {self.cnc_tool_diameter_spin.value():.3f} mm")
        if op in {"Boring", "Helical Boring"}:
            lines.append(f"; Hole diameter: {getattr(self.ski, 'mold_hole_diameter_mm', 20.0):.3f} mm")
        lines.append(f"; Depth mode: {'Core thickness profile' if use_profile else 'Flat depth'}")
        lines.append("G21")
        lines.append("G90")
        lines.append("G17")
        lines.append("G94")
        lines.append("G54")     
        workspace_offset_x, workspace_offset_y, workspace_offset_z = self._get_cnc_preview_offset_xyz()
        safe_z_with_offset = safe_z + workspace_offset_z
        lines.append(f"G0 Z{safe_z_with_offset:.3f}")
        #lines.append(f"G0 X{start_x:.3f} Y{start_y:.3f}")
        if spindle > 0:
            lines.append(f"M3 S{spindle}")

        duplicate_offsets = [(workspace_offset_x, workspace_offset_y)]
        if self._cnc_duplicate_enabled():
            duplicate_x, duplicate_y = self._get_cnc_duplicate_offset_xy()
            duplicate_offsets.append((workspace_offset_x + duplicate_x, workspace_offset_y + duplicate_y))

        if op == "Helical Boring":
            centers = self._boring_hole_centers_mm(selected)
            if not centers:
                return "; No mold holes are available for helical boring.\n"
            surface_z = workspace_offset_z
            final_z = -cut_depth + workspace_offset_z
            for copy_index, (copy_dx, copy_dy) in enumerate(duplicate_offsets, start=1):
                if len(duplicate_offsets) > 1:
                    lines.append(f"; Copy {copy_index} offset X{copy_dx:.3f} Y{copy_dy:.3f}")
                for hole_index, center in enumerate(centers, start=1):
                    design_path = self._helical_boring_path_xyz_mm(center, surface_z, final_z)
                    machine_path = [
                        (
                            float(mx) + copy_dx,
                            float(my) + copy_dy,
                            float(z),
                        )
                        for mx, my, z in [self._cnc_design_xyz_to_machine_xyz(pt) for pt in design_path]
                    ]
                    if len(machine_path) < 2:
                        continue
                    first = machine_path[0]
                    lines.append(f"; Helical bore {hole_index}")
                    lines.append(f"G0 Z{safe_z_with_offset:.3f}")
                    lines.append(f"G0 X{first[0]:.3f} Y{first[1]:.3f}")
                    lines.append(f"G1 Z{first[2]:.3f} F{plunge:.1f}")
                    for x, y, z in machine_path[1:]:
                        lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed:.1f}")
                    lines.append(f"G0 Z{safe_z_with_offset:.3f}")
            lines.append(f"G0 X{start_x:.3f} Y{start_y:.3f}")
            lines.append("M5")
            lines.append("M30")
            return "\n".join(lines) + "\n"

        if use_profile:
            for copy_index, (copy_dx, copy_dy) in enumerate(duplicate_offsets, start=1):
                if len(duplicate_offsets) > 1:
                    lines.append(f"; Copy {copy_index} offset X{copy_dx:.3f} Y{copy_dy:.3f}")
                for loop_index, path in enumerate(paths, start=1):
                    closed_path = bool(selected.get("closed", True) and op != "Pocket")
                    design_xyz_path = self._path_points_xyz_mm(path, closed=closed_path)
                    xyz_path = [(float(x) + copy_dx, float(y) + copy_dy, float(z) + workspace_offset_z) for x, y, z in [self._cnc_design_xyz_to_machine_xyz(pt) for pt in design_xyz_path]]
                    if len(xyz_path) < 2:
                        continue
                    first = xyz_path[0]
                    lines.append(f"; 3D profile loop {loop_index}")
                    lines.append(f"G0 Z{safe_z_with_offset:.3f}")
                    lines.append(f"G0 X{first[0]:.3f} Y{first[1]:.3f}")
                    ramp_pts, remaining_path = self._build_ramp_entry_segments(xyz_path, safe_z_with_offset)
                    if ramp_pts:
                        ramp_feed = float(self.cnc_ramp_feed_rate_spin.value())
                        for x, y, z in ramp_pts[1:]:
                            lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{ramp_feed:.1f}")
                        for x, y, z in remaining_path[1:]:
                            lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed:.1f}")
                    else:
                        lines.append(f"G1 Z{first[2]:.3f} F{plunge:.1f}")
                        for x, y, z in xyz_path[1:]:
                            lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f} F{feed:.1f}")
                    lines.append(f"G0 Z{safe_z_with_offset:.3f}")
        else:
            pass_count = max(1, int(math.ceil(cut_depth / stepdown)))
            current_depth = 0.0
            for pass_index in range(pass_count):
                current_depth = min(cut_depth, current_depth + stepdown)
                z = -current_depth + workspace_offset_z
                lines.append(f"; Pass {pass_index + 1} / {pass_count}")
                for copy_index, (copy_dx, copy_dy) in enumerate(duplicate_offsets, start=1):
                    if len(duplicate_offsets) > 1:
                        lines.append(f"; Copy {copy_index} offset X{copy_dx:.3f} Y{copy_dy:.3f}")
                    for loop_index, path in enumerate(paths, start=1):
                        if not path:
                            continue
                        first_design = path[0]
                        first = self._cnc_design_xy_to_machine_xy(first_design[0], first_design[1])
                        first = (float(first[0]) + copy_dx, float(first[1]) + copy_dy)
                        machine_path = [(float(x_m) + copy_dx, float(y_m) + copy_dy) for x_m, y_m in [self._cnc_design_xy_to_machine_xy(x, y) for x, y in path]]
                        closed_loop = bool((op in {"Boring", "Helical Boring"} and len(path) > 1) or (op != "Pocket" and selected.get("closed", True)))
                        closed_machine_path = list(machine_path)
                        if closed_loop and len(closed_machine_path) >= 2 and closed_machine_path[0] != closed_machine_path[-1]:
                            closed_machine_path.append(closed_machine_path[0])
                        lines.append(f"; Loop {loop_index}")
                        lines.append(f"G0 Z{safe_z_with_offset:.3f}")
                        lines.append(f"G0 X{first[0]:.3f} Y{first[1]:.3f}")
                        if self._cnc_ramp_enabled_for_current_op():
                            flat_xyz = [(x_m, y_m, z) for x_m, y_m in closed_machine_path]
                            ramp_pts, remaining_path = self._build_ramp_entry_segments(flat_xyz, safe_z_with_offset)
                        else:
                            ramp_pts, remaining_path = [], []
                        if ramp_pts:
                            ramp_feed = float(self.cnc_ramp_feed_rate_spin.value())
                            for x, y, z_ramp in ramp_pts[1:]:
                                lines.append(f"G1 X{x:.3f} Y{y:.3f} Z{z_ramp:.3f} F{ramp_feed:.1f}")
                            for x, y, _ in remaining_path[1:]:
                                lines.append(f"G1 X{x:.3f} Y{y:.3f} F{feed:.1f}")
                        else:
                            lines.append(f"G1 Z{z:.3f} F{plunge:.1f}")
                            follow_path = closed_machine_path if closed_loop else machine_path
                            for x, y in follow_path[1:]:
                                lines.append(f"G1 X{x:.3f} Y{y:.3f} F{feed:.1f}")
                lines.append(f"G0 Z{safe_z_with_offset:.3f}")

        lines.append(f"G0 X{start_x:.3f} Y{start_y:.3f}")
        lines.append("M5")
        lines.append("M30")
        return "\n".join(lines) + "\n"

    def refresh_cnc_3d_preview_widget(self):
        if not hasattr(self, "cnc_3d_preview_widget"):
            return
        if getattr(self, "_startup_initializing", False):
            return
        payload = self._get_cached_cnc_preview_payload()
        if len(payload) >= 7:
            segment_groups, workspace, start_point, entry_point, preview_offset, workspace_origin, show_workspace_boundary = payload
        elif len(payload) >= 6:
            segment_groups, workspace, start_point, entry_point, preview_offset, workspace_origin = payload
            show_workspace_boundary = True
        else:
            segment_groups, workspace, start_point, entry_point, preview_offset = payload
            workspace_origin = (0.0, 0.0, 0.0)
            show_workspace_boundary = True
        self.cnc_3d_preview_widget.set_preview_data(segment_groups, workspace, start_point, entry_point, preview_offset, workspace_origin, show_workspace_boundary)

    def _should_refresh_cnc_preview_now(self):
        if getattr(self, "_startup_initializing", False):
            return False
        if self.should_show_main_window_cnc_view():
            return True
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        return bool(preview_widget is not None and preview_widget.isVisible())

    def _mark_cnc_gcode_dirty(self, update_view=True):
        self._cnc_gcode_dirty = True
        if hasattr(self, "cnc_preview"):
            if self.selected_cnc_shape_name:
                self.cnc_preview.setPlainText("G-code preview out of date. Press Generate G-Code.")
            else:
                self.cnc_preview.setPlainText("No shape selected or available.")
        if self._should_refresh_cnc_preview_now():
            self.refresh_cnc_3d_preview_widget()
        if update_view and hasattr(self, "ski"):
            self.ski.update()

    def _on_cnc_gcode_settings_changed(self, *args):
        self._mark_cnc_gcode_dirty()

    def _on_cnc_toolpath_geometry_changed(self, *args):
        self._invalidate_cnc_toolpath_cache()
        self._update_cnc_operation_dependent_visibility()
        self._reposition_selected_cnc_shape_in_workspace()
        self._mark_cnc_gcode_dirty()

    def refresh_cnc_after_shape_edit(self):
        if not hasattr(self, "cnc_panel") or not self.cnc_panel.toggle_button.isChecked():
            return
        selected_name = str(getattr(self, "selected_cnc_shape_name", "") or "")
        self._invalidate_cnc_toolpath_cache()
        self.refresh_cnc_shape_buttons()
        if selected_name:
            available_names = set(self._get_cnc_shape_names())
            if selected_name in available_names:
                self.selected_cnc_shape_name = selected_name
                self._update_cnc_shape_button_styles()
        self._mark_cnc_gcode_dirty()

    def _update_cnc_operation_dependent_visibility(self):
        op = self.cnc_operation_combo.currentText() if hasattr(self, "cnc_operation_combo") else ""
        show_ramp = op in {"On Line", "Outside"}
        show_helix = op == "Helical Boring"
        widgets = [
            getattr(self, "cnc_ramp_entry_check", None),
            getattr(self, "cnc_ramp_angle_label", None),
            getattr(self, "cnc_ramp_angle_spin", None),
            getattr(self, "cnc_ramp_feed_rate_label", None),
            getattr(self, "cnc_ramp_feed_rate_spin", None),
        ]
        for widget in widgets:
            if widget is not None:
                widget.setVisible(show_ramp)
        for widget in (
            getattr(self, "cnc_helix_angle_label", None),
            getattr(self, "cnc_helix_angle_spin", None),
        ):
            if widget is not None:
                widget.setVisible(show_helix)


    def _get_cnc_duplicate_offset_xy(self):
        duplicate_x = float(self.cnc_duplicate_x_spin.value()) if hasattr(self, "cnc_duplicate_x_spin") else 0.0
        duplicate_y = float(self.cnc_duplicate_y_spin.value()) if hasattr(self, "cnc_duplicate_y_spin") else 0.0
        return (duplicate_x, duplicate_y)

    def _cnc_duplicate_enabled(self):
        return bool(getattr(self, "cnc_duplicate_check", None) is not None and self.cnc_duplicate_check.isChecked())

    def _offset_segment_group_machine_xy(self, group, offset_x, offset_y):
        new_group = dict(group)
        new_segments = []
        for seg in group.get('segments', []):
            start_pt, end_pt, seg_type = seg[:3]
            extras = tuple(seg[3:])
            new_segments.append(((float(start_pt[0]) + offset_x, float(start_pt[1]) + offset_y, float(start_pt[2])), (float(end_pt[0]) + offset_x, float(end_pt[1]) + offset_y, float(end_pt[2])), seg_type, *extras))
        new_group['segments'] = new_segments
        new_group['path'] = [(float(pt[0]) + offset_x, float(pt[1]) + offset_y, float(pt[2])) for pt in group.get('path', [])]
        return new_group

    def _duplicate_cnc_segment_groups(self, segment_groups):
        groups = [dict(group) for group in (segment_groups or [])]
        if not groups or not self._cnc_duplicate_enabled():
            return groups
        duplicate_x, duplicate_y = self._get_cnc_duplicate_offset_xy()
        if abs(duplicate_x) <= 1e-9 and abs(duplicate_y) <= 1e-9:
            return groups
        duplicated = [self._offset_segment_group_machine_xy(group, duplicate_x, duplicate_y) for group in groups]
        return groups + duplicated

    def _selected_cnc_machine_xy_bounds(self, include_duplicate=False):
        shape = self._selected_cnc_shape()
        if shape is None:
            return None
        op = self.cnc_operation_combo.currentText()
        if op == "Pocket":
            raw_paths = self._pocket_paths_mm(shape)
            closed = False
        elif op in {"Boring", "Helical Boring"}:
            raw_paths = self._boring_paths_mm(shape)
            closed = False
        else:
            raw_paths = self._shape_paths_mm_for_operation(shape)
            closed = bool(shape.get("closed", True) and op != "Pocket")
        machine_paths = []
        for path_pts in raw_paths:
            if not path_pts:
                continue
            design_xyz = self._path_points_xyz_mm(path_pts, closed=closed)
            xyz_path = [self._cnc_design_xyz_to_machine_xyz(pt) for pt in design_xyz]
            machine_paths.append([(float(pt[0]), float(pt[1])) for pt in xyz_path])
        if not machine_paths:
            return None
        duplicate_offsets = [(0.0, 0.0)]
        if include_duplicate and self._cnc_duplicate_enabled():
            duplicate_offsets.append(self._get_cnc_duplicate_offset_xy())
        xs = []
        ys = []
        for off_x, off_y in duplicate_offsets:
            for path_pts in machine_paths:
                for x_mm, y_mm in path_pts:
                    xs.append(x_mm + off_x)
                    ys.append(y_mm + off_y)
        if not xs or not ys:
            return None
        return (min(xs), min(ys), max(xs), max(ys))

    def _reposition_selected_cnc_shape_in_workspace(self):
        if not hasattr(self, "cnc_preview_offset_lr_spin") or not hasattr(self, "cnc_preview_offset_ud_spin"):
            return
        bounds = self._selected_cnc_machine_xy_bounds(include_duplicate=self._cnc_duplicate_enabled())
        if bounds is None:
            return
        min_x, min_y, max_x, max_y = bounds
        workspace_x = float(self.cnc_workspace_x_spin.value()) if hasattr(self, "cnc_workspace_x_spin") else 0.0
        workspace_y = float(self.cnc_workspace_y_spin.value()) if hasattr(self, "cnc_workspace_y_spin") else 0.0
        shift_x = -min_x if min_x < 0.0 else 0.0
        shift_y = -min_y if min_y < 0.0 else 0.0
        if max_x + shift_x > workspace_x:
            shift_x += workspace_x - (max_x + shift_x)
        if max_y + shift_y > workspace_y:
            shift_y += workspace_y - (max_y + shift_y)
        self.cnc_preview_offset_lr_spin.blockSignals(True)
        self.cnc_preview_offset_ud_spin.blockSignals(True)
        self.cnc_preview_offset_lr_spin.setValue(shift_x)
        self.cnc_preview_offset_ud_spin.setValue(shift_y)
        self.cnc_preview_offset_lr_spin.blockSignals(False)
        self.cnc_preview_offset_ud_spin.blockSignals(False)

    def _get_cnc_preview_offset_xy(self):
        # Preview Left/Right should move machine X, and Preview Up/Down should move machine Y.
        preview_x = float(self.cnc_preview_offset_lr_spin.value()) if hasattr(self, "cnc_preview_offset_lr_spin") else 0.0
        preview_y = float(self.cnc_preview_offset_ud_spin.value()) if hasattr(self, "cnc_preview_offset_ud_spin") else 0.0
        return (preview_x, preview_y)

    def _get_cnc_preview_offset_xyz(self):
        preview_x, preview_y = self._get_cnc_preview_offset_xy()
        preview_z = float(self.cnc_preview_offset_z_spin.value()) if hasattr(self, "cnc_preview_offset_z_spin") else 0.0
        return (preview_x, preview_y, preview_z)

    def _get_cnc_workspace_origin_xyz(self):
        move_x = float(self.cnc_workspace_move_x_spin.value()) if hasattr(self, "cnc_workspace_move_x_spin") else 0.0
        move_y = float(self.cnc_workspace_move_y_spin.value()) if hasattr(self, "cnc_workspace_move_y_spin") else 0.0
        move_z = float(self.cnc_workspace_move_z_spin.value()) if hasattr(self, "cnc_workspace_move_z_spin") else 0.0
        return (move_x, move_y, move_z)

    def _show_cnc_machine_boundary(self):
        checkbox = getattr(self, "cnc_show_machine_boundary_check", None)
        return True if checkbox is None else bool(checkbox.isChecked())

    def _apply_cnc_preview_offset_to_point(self, pt):
        preview_x, preview_y, preview_z = self._get_cnc_preview_offset_xyz()
        return (float(pt[0]) + preview_x, float(pt[1]) + preview_y, float(pt[2]) + preview_z)

    def _preview_adjusted_cnc_segment_groups(self, segment_groups):
        adjusted = []
        for group in segment_groups or []:
            new_group = dict(group)
            new_segments = []
            for seg in group.get('segments', []):
                start_pt, end_pt, seg_type = seg[:3]
                extras = tuple(seg[3:])
                new_segments.append((
                    self._apply_cnc_preview_offset_to_point(start_pt),
                    self._apply_cnc_preview_offset_to_point(end_pt),
                    seg_type,
                    *extras,
                ))
            new_group['segments'] = new_segments
            new_group['path'] = [self._apply_cnc_preview_offset_to_point(pt) for pt in group.get('path', [])]
            adjusted.append(new_group)
        return adjusted

    def _on_cnc_preview_settings_changed(self, *args):
        self.refresh_cnc_3d_preview_widget()
        if hasattr(self, "ski"):
            self.ski.update()

    def generate_cnc_gcode(self):
        self.refresh_cnc_shape_buttons()
        code = self.build_cnc_gcode()
        self._last_generated_cnc_code = code
        self._cnc_gcode_dirty = False
        self.cnc_preview.setPlainText(code)
        self.refresh_cnc_3d_preview_widget()
        self.ski.update()

    def _on_cnc_panel_toggled(self, expanded):
        if expanded and not getattr(self, "_cnc_preview_first_open_done", False):
            self._set_cnc_preview_angles(0.0, 180.0, 0.0)
            self.refresh_cnc_3d_preview_widget()
            self.rescale_cnc_preview_view(fill_ratio=0.90 / (1.12 ** 2))
            self._cnc_preview_first_open_done = True
            self.ski.update()
            return
        self.refresh_cnc_3d_preview_widget()
        self.ski.update()

    def should_show_main_window_cnc_view(self):
        if not hasattr(self, "cnc_panel") or not self.cnc_panel.toggle_button.isChecked():
            return False
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        if preview_widget is not None and preview_widget.isVisible():
            return False
        return True

    def _main_window_cnc_view_rects(self):
        if not self.should_show_main_window_cnc_view():
            return {}
        box_left = -2750.0
        box_top = -1000.0
        box_width = 1800.0
        box_height = 1800.0
        rect = QRectF(box_left, box_top, box_width, box_height)
        inner = rect.adjusted(12.0, 12.0, -12.0, -12.0)
        content_rect = inner.adjusted(0.0, 24.0, 0.0, -2.0)
        views_rect = content_rect.adjusted(0.0, 38.0, 0.0, 0.0)
        preview_3d_rect = QRectF(views_rect)
        return {
            "outer": rect,
            "views": views_rect,
            "preview_3d": preview_3d_rect,
            "side": QRectF(),
            "top": QRectF(),
        }

    def _point_in_main_window_cnc_3d_view(self, scene_pos):
        rects = self._main_window_cnc_view_rects()
        preview_rect = rects.get("preview_3d")
        if preview_rect is None or preview_rect.isNull():
            return False
        return preview_rect.contains(QPointF(scene_pos))

    def handle_main_window_cnc_3d_wheel(self, scene_pos, delta_y):
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        if preview_widget is None or delta_y == 0:
            return False
        if not self._point_in_main_window_cnc_3d_view(scene_pos):
            return False
        factor = 1.12 if delta_y > 0 else (1.0 / 1.12)
        preview_widget.zoom = max(0.15, min(25.0, preview_widget.zoom * factor))
        preview_widget.update()
        if hasattr(preview_widget, "repaint"):
            preview_widget.repaint()
        if hasattr(self, "ski"):
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.update()
            viewport = self.view.viewport()
            if viewport is not None:
                viewport.update()
                if hasattr(viewport, "repaint"):
                    viewport.repaint()
        return True

    def begin_main_window_cnc_3d_interaction(self, button, scene_pos, view_pos):
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        if preview_widget is None:
            return False
        if button not in (Qt.MouseButton.RightButton, Qt.MouseButton.MiddleButton):
            return False
        if not self._point_in_main_window_cnc_3d_view(scene_pos):
            return False
        preview_widget._last_mouse_pos = QPointF(view_pos)
        if button == Qt.MouseButton.MiddleButton:
            preview_widget._panning = True
        else:
            preview_widget._orbiting = True
        if hasattr(self, "ski"):
            self.ski.update()
        return True

    def update_main_window_cnc_3d_interaction(self, view_pos, modifiers=Qt.KeyboardModifier.NoModifier):
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        if preview_widget is None:
            return False
        if not (getattr(preview_widget, "_orbiting", False) or getattr(preview_widget, "_panning", False)):
            return False
        last_pos = getattr(preview_widget, "_last_mouse_pos", None)
        if last_pos is None:
            preview_widget._last_mouse_pos = QPointF(view_pos)
            return True
        pos = QPointF(view_pos)
        delta = pos - last_pos
        preview_widget._last_mouse_pos = pos
        if getattr(preview_widget, "_orbiting", False):
            preview_widget._set_orbit_angles_from_delta(last_pos, pos, modifiers)
        elif getattr(preview_widget, "_panning", False):
            preview_widget.pan_x += delta.x()
            preview_widget.pan_y += delta.y()
        if hasattr(self, "ski"):
            self.ski.update()
        if hasattr(self, "view") and self.view is not None:
            self.view.update()
            viewport = self.view.viewport()
            if viewport is not None:
                viewport.update()
                if hasattr(viewport, "repaint"):
                    viewport.repaint()
        return True

    def finish_main_window_cnc_3d_interaction(self, button):
        preview_widget = getattr(self, "cnc_3d_preview_widget", None)
        if preview_widget is None:
            return False
        handled = False
        if button == Qt.MouseButton.MiddleButton and getattr(preview_widget, "_panning", False):
            preview_widget._panning = False
            handled = True
        elif button == Qt.MouseButton.RightButton and getattr(preview_widget, "_orbiting", False):
            preview_widget._orbiting = False
            handled = True
        if handled:
            preview_widget._last_mouse_pos = None
            if hasattr(self, "ski"):
                self.ski.update()
        return handled

    def _draw_cnc_projection_panel(self, painter, view_rect, view_name, segment_groups, projector, axis_h, axis_v, mill_pen, plunge_pen, ramp_pen, rapid_pen, panel_bg, border_color, axis_color, start_brush):
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(panel_bg))
        painter.drawRoundedRect(view_rect, 10, 10)

        label_font = QFont(painter.font())
        label_font.setPointSize(max(int(round(max(label_font.pointSize(), 9) * 3.0)), 27))
        painter.setFont(label_font)
        painter.setPen(QPen(QColor(215, 220, 226), 1))
        painter.drawText(view_rect.adjusted(10.0, 4.0, -10.0, 0.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, view_name)

        plot_rect = view_rect.adjusted(12.0, max(64.0, float(painter.fontMetrics().height()) + 16.0), -12.0, -12.0)
        if plot_rect.width() <= 8 or plot_rect.height() <= 8:
            return

        projected = []
        for group in segment_groups:
            entries = []
            for seg in group.get('segments', []):
                p0, p1, seg_kind = seg[:3]
                feed_value = seg[3] if len(seg) > 3 else None
                entries.append((projector(p0), projector(p1), seg_kind, feed_value))
            if entries:
                projected.append(entries)
        proj_points = [pt for entries in projected for entry in entries for pt in (entry[0], entry[1])]
        if not proj_points:
            return

        xs = [p[0] for p in proj_points]
        ys = [p[1] for p in proj_points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        span_x = max(1e-6, max_x - min_x)
        span_y = max(1e-6, max_y - min_y)

        if view_name == 'Top':
            fit_x = 0.92
            fit_y = 0.94
        else:
            fit_x = 0.86
            fit_y = 0.92
        scale = min(plot_rect.width() * fit_x / span_x, plot_rect.height() * fit_y / span_y)

        left_pad = (plot_rect.width() - span_x * scale) * 0.5
        top_pad = (plot_rect.height() - span_y * scale) * 0.5

        def map_pt(pt2):
            return QPointF(
                plot_rect.left() + left_pad + (pt2[0] - min_x) * scale,
                plot_rect.bottom() - top_pad - (pt2[1] - min_y) * scale,
            )

        axis_origin = map_pt((0.0, 0.0))
        axis_origin.setX(max(plot_rect.left() + 6.0, min(plot_rect.right() - 6.0, axis_origin.x())))
        axis_origin.setY(max(plot_rect.top() + 6.0, min(plot_rect.bottom() - 6.0, axis_origin.y())))

        painter.setPen(QPen(axis_color, 1, Qt.PenStyle.DashLine))
        painter.drawLine(QPointF(plot_rect.left() + 6.0, axis_origin.y()), QPointF(plot_rect.right() - 6.0, axis_origin.y()))
        painter.drawLine(QPointF(axis_origin.x(), plot_rect.top() + 6.0), QPointF(axis_origin.x(), plot_rect.bottom() - 6.0))
        painter.setPen(QPen(QColor(145, 150, 158), 1))
        axis_label_size = max(36.0, float(painter.fontMetrics().height()) + 6.0)
        painter.drawText(QRectF(plot_rect.right() - axis_label_size, axis_origin.y() - axis_label_size * 0.5, axis_label_size, axis_label_size), Qt.AlignmentFlag.AlignCenter, axis_h)
        painter.drawText(QRectF(axis_origin.x() - axis_label_size * 0.5, plot_rect.top() + 2.0, axis_label_size, axis_label_size), Qt.AlignmentFlag.AlignCenter, axis_v)

        first_marker = None
        pen_map = {'mill': mill_pen, 'plunge': plunge_pen, 'ramp': ramp_pen, 'rapid': rapid_pen}
        for entries in projected:
            if not entries:
                continue
            if first_marker is None:
                first_marker = map_pt(entries[0][0])
            for p0, p1, seg_kind, feed_value in entries:
                painter.setPen(self._cnc_segment_pen(seg_kind, feed_value, 2))
                painter.drawLine(map_pt(p0), map_pt(p1))
        if first_marker is not None:
            painter.setPen(QPen(QColor(35, 40, 45), 1))
            painter.setBrush(start_brush)
            painter.drawEllipse(first_marker, 3.5, 3.5)

    def _draw_cnc_3d_panel_in_main_view(self, painter, view_rect, segment_groups, panel_bg, border_color, mill_pen, plunge_pen, ramp_pen, rapid_pen):
        painter.setPen(QPen(border_color, 1))
        painter.setBrush(QBrush(panel_bg))
        painter.drawRoundedRect(view_rect, 10, 10)

        panel_font = QFont(painter.font())
        panel_font.setPointSize(max(int(round(max(panel_font.pointSize(), 9) * 3.0)), 27))
        panel_font.setBold(True)
        painter.setFont(panel_font)
        painter.setPen(QPen(QColor(215, 220, 226), 1))

        plot_rect = view_rect.adjusted(10.0, 28.0, -10.0, -12.0)
        if plot_rect.width() <= 10.0 or plot_rect.height() <= 10.0:
            return

        workspace = (
            float(self.cnc_workspace_x_spin.value()),
            float(self.cnc_workspace_y_spin.value()),
            float(self.cnc_workspace_z_spin.value()),
        )
        workspace_origin = self._get_cnc_workspace_origin_xyz()
        start_point = (
            float(self.cnc_start_x_spin.value()),
            float(self.cnc_start_y_spin.value()),
            0.0,
        )
        # Keep the entry marker pinned to the machine boundary start point.
        # The first actual preview segment may move to safe Z or across to the shape,
        # but the entry location itself should be the machine start X/Y/Z origin.
        entry_point = start_point

        ox, oy, oz = workspace_origin
        scene_points = [
            (ox, oy, oz), (ox + workspace[0], oy, oz), (ox + workspace[0], oy + workspace[1], oz), (ox, oy + workspace[1], oz),
            (ox, oy, oz + workspace[2]), (ox + workspace[0], oy, oz + workspace[2]), (ox + workspace[0], oy + workspace[1], oz + workspace[2]), (ox, oy + workspace[1], oz + workspace[2]),
            start_point,
        ]
        if entry_point is not None:
            scene_points.append(entry_point)
        for group in segment_groups:
            for seg in group.get('segments', []):
                start_pt, end_pt = seg[:2]
                scene_points.extend([start_pt, end_pt])

        preview_widget = getattr(self, 'cnc_3d_preview_widget', None)
        if preview_widget is None or len(scene_points) <= 9:
            painter.setPen(QPen(QColor(180, 185, 192), 1))
            painter.drawText(plot_rect, Qt.AlignmentFlag.AlignCenter, 'No 3D CNC toolpath to preview')
            return

        projected, _scale = preview_widget._project_points(scene_points, plot_rect)
        if not projected:
            painter.setPen(QPen(QColor(180, 185, 192), 1))
            painter.drawText(plot_rect, Qt.AlignmentFlag.AlignCenter, 'No 3D CNC toolpath to preview')
            return

        workspace_edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]
        workspace_pen = QPen(QColor(70, 76, 84, 210), 1)
        workspace_pen.setStyle(Qt.PenStyle.DashLine)
        workspace_pen.setCosmetic(True)
        if self._show_cnc_machine_boundary():
            painter.setPen(workspace_pen)
            for a, b in workspace_edges:
                painter.drawLine(QPointF(projected[a][0], projected[a][1]), QPointF(projected[b][0], projected[b][1]))

        start_idx = 8
        entry_idx = 9 if entry_point is not None else None
        # scene_points contains 8 workspace corners, then the start marker,
        # then the entry marker before any toolpath segment endpoints.
        idx = 10 if entry_idx is not None else 9
        for group in segment_groups:
            for seg in group.get('segments', []):
                seg_type = seg[2]
                feed_value = seg[3] if len(seg) > 3 else None
                painter.setPen(self._cnc_segment_pen(seg_type, feed_value, 2))
                painter.drawLine(QPointF(projected[idx][0], projected[idx][1]), QPointF(projected[idx + 1][0], projected[idx + 1][1]))
                idx += 2

        painter.setPen(QPen(QColor(255, 255, 255, 220), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawEllipse(QPointF(projected[start_idx][0], projected[start_idx][1]), 4.5, 4.5)
        marker_font = QFont(painter.font())
        marker_font.setPointSize(7)
        painter.setFont(marker_font)
        painter.drawText(QPointF(projected[start_idx][0] + 8.0, projected[start_idx][1] - 8.0), 'G54 (0,0,0)')

        if entry_idx is not None and entry_idx in projected:
            painter.setPen(QPen(QColor(255, 160, 160, 225), 1.5))
            painter.setBrush(QBrush(QColor(255, 160, 160, 230)))
            painter.drawEllipse(QPointF(projected[entry_idx][0], projected[entry_idx][1]), 4.0, 4.0)
            #painter.drawText(QPointF(projected[entry_idx][0] + 8.0, projected[entry_idx][1] + 14.0), 'Entry')

        axis_font = QFont(painter.font())
        axis_font.setPointSize(13)
        preview_widget._draw_coordinate_axes_overlay(painter, plot_rect, projected, label_font=axis_font)

        stats_font = QFont(painter.font())
        stats_font.setPointSize(12)
        painter.setFont(stats_font)
        preview_x, preview_y = self._get_cnc_preview_offset_xy()
        stats_line_h = max(18.0, float(painter.fontMetrics().height()) + 5.0)
        stats_box = QRectF(plot_rect.left() + 12.0, plot_rect.top() + 152.0, 560.0, stats_line_h * 4.0 + 42.0)
        painter.setPen(QPen(QColor(95, 102, 112, 160), 1))
        painter.setBrush(QBrush(QColor(20, 22, 26, 155)))
        painter.drawRoundedRect(stats_box, 4, 4)
        painter.setPen(QPen(QColor(195, 200, 208), 1))
        text_rect = stats_box.adjusted(10.0, 8.0, -10.0, -8.0)
        painter.drawText(QRectF(text_rect.left(), text_rect.top(), text_rect.width(), stats_line_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"X {workspace[0]:.0f}  Y {workspace[1]:.0f}  Z {workspace[2]:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h, text_rect.width(), stats_line_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"Offset X {preview_x:.0f}  Y {preview_y:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h * 2.0, text_rect.width(), stats_line_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"Move X {workspace_origin[0]:.0f}  Y {workspace_origin[1]:.0f}  Z {workspace_origin[2]:.0f} mm")
        painter.drawText(QRectF(text_rect.left(), text_rect.top() + stats_line_h * 3.0, text_rect.width(), stats_line_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, f"P {preview_widget.rot_x:.0f}  Y {preview_widget.rot_y:.0f}  R {preview_widget.rot_z:.0f}")

    def draw_main_window_cnc_toolpath_view(self, painter):
        payload = self._get_cached_cnc_preview_payload()
        segment_groups = payload[0]

        rects = self._main_window_cnc_view_rects()
        rect = rects.get('outer', QRectF(-1735.0, -620.0, 980.0, 1120.0))
        inner = rect.adjusted(12.0, 12.0, -12.0, -12.0)

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(QColor(85, 92, 102), 1))
        painter.setBrush(QBrush(QColor(20, 20, 24, 170)))
        painter.drawRoundedRect(rect, 12, 12)

        title_rect = QRectF(rect.left() + 10.0, rect.top() + 6.0, rect.width() - 20.0, 64.0)
        painter.setPen(QPen(QColor(235, 235, 235), 1))
        painter.setFont(QFont('Arial', 60))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'CNC Toolpath Preview')
        #painter.drawText(title_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, 'Hover 3D panel: RMB drag orbit • Shift changes left/right from pitch to roll • MMB pan • Wheel zoom')

        content_rect = inner.adjusted(0.0, 72.0, 0.0, -2.0)
        legend_rect = QRectF(content_rect.left(), content_rect.top(), content_rect.width(), 150.0)
        views_rect = content_rect.adjusted(0.0, 156.0, 0.0, 0.0)

        mill_color = QColor(255, 210, 90, 245)
        plunge_color = QColor(90, 210, 255, 245)
        ramp_color = QColor(145, 255, 145, 245)
        rapid_color = QColor(255, 90, 90, 245)
        panel_bg = QColor(26, 29, 34, 210)
        border_color = QColor(72, 79, 88)
        axis_color = QColor(70, 76, 84)

        def draw_cnc_preview_legend():
            legend_bg = legend_rect.adjusted(0.0, 2.0, 0.0, -2.0)
            painter.setPen(QPen(QColor(78, 86, 96), 1))
            painter.setBrush(QBrush(QColor(16, 18, 22, 245)))
            painter.drawRoundedRect(legend_bg, 8, 8)

            title_font = QFont('Arial', 30)
            tick_font = QFont('Arial', 24)
            painter.setFont(title_font)
            painter.setPen(QPen(QColor(245, 248, 252), 1))

            if self._cnc_preview_color_mode() == 'feed':
                painter.drawText(QRectF(legend_rect.left() + 10.0, legend_rect.top() + 4.0, 720.0, 48.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'Feed rate heatmap (mm/min)')

                bar_x0 = legend_rect.left() + 12.0
                bar_x1 = legend_rect.right() - 230.0
                bar_y0 = legend_rect.top() + 64.0
                bar_h = 28.0
                band_count = 10
                band_w = max(1.0, (bar_x1 - bar_x0) / float(band_count))

                for band in range(band_count):
                    color = self._cnc_feed_band_color((band * 200.0) + 100.0, 255)
                    x = bar_x0 + band * band_w
                    painter.fillRect(QRectF(x, bar_y0, band_w + 0.5, bar_h), color)

                painter.setPen(QPen(QColor(235, 238, 244), 1))
                painter.drawRect(QRectF(bar_x0, bar_y0, bar_x1 - bar_x0, bar_h))

                painter.setFont(tick_font)
                for tick in range(band_count + 1):
                    x = bar_x0 + (bar_x1 - bar_x0) * (tick / float(band_count))
                    painter.drawLine(QPointF(x, bar_y0 + bar_h), QPointF(x, bar_y0 + bar_h + 10.0))
                    label_value = tick * 200
                    label = '2000+' if tick == band_count else str(label_value)
                    text_rect = QRectF(x - 42.0, bar_y0 + bar_h + 12.0, 88.0, 34.0)
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, label)

                rapid_x0 = legend_rect.right() - 200.0
                rapid_y = bar_y0 + (bar_h / 2.0)
                painter.setFont(title_font)
                painter.setPen(QPen(rapid_color, 3))
                painter.drawLine(QPointF(rapid_x0, rapid_y), QPointF(rapid_x0 + 54.0, rapid_y))
                painter.setPen(QPen(QColor(245, 248, 252), 1))
                painter.drawText(QRectF(rapid_x0 + 66.0, bar_y0 - 12.0, 150.0, 44.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'Rapid')
                painter.setFont(tick_font)
                painter.drawText(QRectF(rapid_x0 + 66.0, bar_y0 + 30.0, 170.0, 40.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'G0 travel')
            else:
                painter.drawText(QRectF(legend_rect.left() + 10.0, legend_rect.top() + 4.0, 720.0, 48.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 'Motion type colors')
                legend_items = [
                    ('Mill', mill_color),
                    ('Plunge', plunge_color),
                    ('Ramp', ramp_color),
                    ('Rapid', rapid_color),
                ]
                x = legend_rect.left() + 12.0
                y = legend_rect.top() + 86.0
                for label, color in legend_items:
                    painter.setPen(QPen(color, 3))
                    painter.drawLine(QPointF(x, y), QPointF(x + 54.0, y))
                    painter.setPen(QPen(QColor(245, 248, 252), 1))
                    painter.drawText(QRectF(x + 66.0, y - 24.0, 170.0, 54.0), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
                    x += 240.0

        if not segment_groups:
            painter.setPen(QPen(QColor(180, 185, 192), 1))
            painter.drawText(views_rect, Qt.AlignmentFlag.AlignCenter, 'Open CNC Toolpaths to preview')
            draw_cnc_preview_legend()
            painter.restore()
            return

        all_points = []
        for group in segment_groups:
            all_points.extend(group.get('path', []))
        if not all_points:
            painter.setPen(QPen(QColor(180, 185, 192), 1))
            painter.drawText(views_rect, Qt.AlignmentFlag.AlignCenter, 'No CNC toolpath to preview')
            draw_cnc_preview_legend()
            painter.restore()
            return

        preview_3d_rect = rects.get('preview_3d', QRectF())

        mill_pen = QPen(mill_color, 2)
        mill_pen.setCosmetic(True)
        plunge_pen = QPen(plunge_color, 2)
        plunge_pen.setCosmetic(True)
        ramp_pen = QPen(ramp_color, 2)
        ramp_pen.setCosmetic(True)
        rapid_pen = QPen(rapid_color, 2)
        rapid_pen.setCosmetic(True)
        start_brush = QBrush(QColor(235, 235, 235, 220))

        self._draw_cnc_3d_panel_in_main_view(painter, preview_3d_rect, segment_groups, panel_bg, border_color, mill_pen, plunge_pen, ramp_pen, rapid_pen)
        draw_cnc_preview_legend()

        painter.restore()

    def save_cnc_gcode(self):
        if self._cnc_gcode_dirty or not self._last_generated_cnc_code:
            self.generate_cnc_gcode()
        code = self._last_generated_cnc_code
        filename, _ = QFileDialog.getSaveFileName(self, "Save G-Code", "", "G-Code Files (*.nc *.gcode *.tap);;All Files (*)")
        if not filename:
            return
        try:
            Path(filename).write_text(code, encoding="utf-8")
        except Exception as exc:
            QMessageBox.warning(self, "Save Failed", f"Could not save G-code\n{exc}")
            return
        self.cnc_preview.setPlainText(code)

    def pick_3d_color(self):
        color = QColorDialog.getColor(self.ski.ski_color, self, "Pick 3D Ski Color")
        if color.isValid():
            self.ski.ski_color = color
            self.update_color_button_style()
            self.ski.update()
    def pick_3d_background_color(self):
        current = QColor(getattr(self.ski, "background_3d_color", QColor(46, 50, 58, 210)))
        color = QColorDialog.getColor(current, self, "Pick 3D Background Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.ski.background_3d_color = color
            self.ski.update()
    def _graphic_is_visible(self, kind):
        image = self.ski.base_graphic_image if kind == "base" else self.ski.top_graphic_image
        return image is not None and not image.isNull()
    def _graphic_has_saved_path(self, kind):
        path = self.ski.base_graphic_path if kind == "base" else self.ski.top_graphic_path
        return bool(path)
    def _sync_graphic_buttons(self):
        if hasattr(self, "load_right_graphic_button"):
            self.load_right_graphic_button.setText("Hide Right Graphic" if self._graphic_is_visible("top") else "Load/Show Right Graphic")
        if hasattr(self, "load_left_graphic_button"):
            self.load_left_graphic_button.setText("Hide Left Graphic" if self._graphic_is_visible("base") else "Load/Show Left Graphic")
    def _hide_graphic(self, kind):
        if kind == "base":
            self.ski.base_graphic_image = None
        else:
            self.ski.top_graphic_image = None
        self._sync_graphic_buttons()
        self.ski.update()
        self.view.viewport().update()
    def _show_hidden_graphic(self, kind):
        path = self.ski.base_graphic_path if kind == "base" else self.ski.top_graphic_path
        if not path:
            return False
        ok = self.ski.load_base_graphic(path) if kind == "base" else self.ski.load_top_graphic(path)
        if ok:
            self.sync_2d_graphic_controls_from_model()
            self._sync_graphic_buttons()
            self.ski.update()
            self.view.viewport().update()
        return ok
    def _prompt_load_or_show_graphic(self, kind):
        title = "Left Graphic" if kind == "base" else "Right Graphic"
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(f"What would you like to do with the {title.lower()}?")
        msg.setIcon(QMessageBox.Icon.Question)
        load_btn = msg.addButton("Load", QMessageBox.ButtonRole.AcceptRole)
        show_btn = None
        if self._graphic_has_saved_path(kind):
            show_btn = msg.addButton("Show", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(load_btn)
        msg.exec()
        clicked = msg.clickedButton()
        if clicked == load_btn:
            return "load"
        if show_btn is not None and clicked == show_btn:
            return "show"
        if clicked == cancel_btn:
            return None
        return None
    def toggle_or_prompt_top_graphic(self):
        if self._graphic_is_visible("top"):
            self._hide_graphic("top")
            return
        choice = self._prompt_load_or_show_graphic("top")
        if choice == "show":
            self._show_hidden_graphic("top")
        elif choice == "load":
            self.load_top_graphic()
    def toggle_or_prompt_base_graphic(self):
        if self._graphic_is_visible("base"):
            self._hide_graphic("base")
            return
        choice = self._prompt_load_or_show_graphic("base")
        if choice == "show":
            self._show_hidden_graphic("base")
        elif choice == "load":
            self.load_base_graphic()
    def load_top_graphic(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Right Graphic",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename and self.ski.load_top_graphic(filename):
            self.sync_2d_graphic_controls_from_model()
            self._sync_graphic_buttons()
            self.ski.update()
            self.view.viewport().update()
    def load_base_graphic(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Left Graphic",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if filename and self.ski.load_base_graphic(filename):
            self.sync_2d_graphic_controls_from_model()
            self._sync_graphic_buttons()
            self.ski.update()
            self.view.viewport().update()
    def _show_exit_confirmation(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Exit")
        msg.setText("Do you want to save your ski design before exiting?")
        msg.setIcon(QMessageBox.Icon.NoIcon )
        msg.setStandardButtons(
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        )
        msg.setDefaultButton(QMessageBox.StandardButton.Save)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2B2F34;
            }
            QMessageBox QLabel {
                color: #EAEAEA;
                min-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #3A3D42;
                border: 1px solid #5B616A;
                border-radius: 8px;
                padding: 8px 12px;
                color: #F2F2F2;
                min-height: 40px;
            }
            QMessageBox QPushButton:hover {
                background-color: #4A4E55;
            }
            QMessageBox QPushButton:pressed {
                background-color: #2D3035;
            }
        """)
        buttons = [
            msg.button(QMessageBox.StandardButton.Save),
            msg.button(QMessageBox.StandardButton.Discard),
            msg.button(QMessageBox.StandardButton.Cancel),
        ]
        for btn in buttons:
            if btn is not None:
                btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                btn.setMinimumHeight(40)
                btn.setMinimumWidth(120)
        layout = msg.layout()
        if layout is not None:
            layout.setSpacing(10)
            layout.setContentsMargins(18, 18, 18, 18)
        return msg.exec()

    def confirm_exit(self):

        result = self._show_exit_confirmation()

        if result == QMessageBox.StandardButton.Save:
            if self.save_file():
                self._exiting_via_confirm = True
                self.close()
        elif result == QMessageBox.StandardButton.Discard:
            self._exiting_via_confirm = True
            self.close()
    def closeEvent(self, event):

        if getattr(self, "_exiting_via_confirm", False):
            self._exiting_via_confirm = False
            event.accept()
            return

        result = self._show_exit_confirmation()

        if result == QMessageBox.StandardButton.Save:
            if self.save_file():
                event.accept()
            else:
                event.ignore()
        elif result == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()
    def save_file(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Ski Design",
            "",
            "Ski Design (*.ski)"
        )

        if not filename:
            return False

        data = self.ski.serialize()

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

        return True
    def load_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Load Ski Design",
            "",
            "Ski Design (*.ski)"
        )

        if not filename:
            return

        with open(filename, "r") as f:
            data = json.load(f)

        self.ski.deserialize(data)
        self.edge_thickness_spin.setValue(self.ski.edge_thickness_px)
        self.sidewall_thickness_spin.setValue(self.ski.sidewall_thickness_px)
        self.left_sidewall_thickness_spin.setValue(getattr(self.ski, "left_sidewall_thickness_px", self.ski.sidewall_thickness_px))
        self.edge_inlay_tip_spin.setValue(self.ski.edge_inlay_tip_trim_px)
        self.edge_inlay_tail_spin.setValue(self.ski.edge_inlay_tail_trim_px)
        self.base_edge_corner_radius_slider.setValue(int(round(getattr(self.ski, "base_edge_corner_min_radius_px", 0.0))))
        self.base_edge_corner_radius_value_label.setText(f"{self.base_edge_corner_radius_slider.value()} mm")
        self.splitboard_inside_edge_check.setChecked(bool(getattr(self.ski, "include_splitboard_inside_edge", True)))
        self.tip_spacer_spin.setValue(self.ski.tip_spacer_length_px)
        self.tail_spacer_spin.setValue(self.ski.tail_spacer_length_px)
        self.tip_seam_point_count_spin.setValue(getattr(self.ski, "tip_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.tail_seam_point_count_spin.setValue(getattr(self.ski, "tail_seam_point_count", getattr(self.ski, "seam_point_count", 3)))
        self.sync_seam_editor_widgets()
        self.light_azimuth_slider.setValue(int(round(self.ski.light_azimuth_deg)))
        self.light_elevation_slider.setValue(int(round(self.ski.light_elevation_deg)))
        self.brightness_slider.setValue(int(round(self.ski.light_brightness * 100)))
        self.background_width_slider.setValue(int(round(getattr(self.ski, "background_3d_width_px", 760.0))))
        self.background_height_slider.setValue(int(round(getattr(self.ski, "background_3d_height_px", 1280.0))))
        self.update_color_button_style()
        self.update_light_controls()
        self.refresh_shape_outline_mode_actions()
        self.refresh_splitboard_inside_edge_controls()
        self.refresh_cnc_shape_buttons()
        self.generate_cnc_gcode()
        self.refresh_layup_toggle_labels()
    def export_svg_file(self):
        filename, _ = QFileDialog.getSaveFileName(self,"Export SVG","","SVG Files (*.svg)")
        if filename:
            self.ski.export_svg(filename)
    def export_dxf_file(self):
        filename, _ = QFileDialog.getSaveFileName(self,"Export DXF","","DXF Files (*.dxf)")
        if filename:
            self.ski.export_dxf(filename)
    def export_stl_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Export STL", "", "STL Files (*.stl)")
        if filename:
            self.write_ascii_stl(filename, self._build_stl_export_faces())

    def _build_stl_export_faces(self):
        faces = self.ski.build_ski_mesh()
        if getattr(self.ski, "outline_mode", "symmetric") != "splitboard":
            return faces

        split_gap_cm = 1.0
        half_gap_cm = split_gap_cm * 0.5
        right_faces = [
            [(float(x), float(y) + half_gap_cm, float(z)) for x, y, z in face]
            for face in faces
        ]
        mirrored_faces = []
        for face in faces:
            mirrored = [(float(x), -float(y) - half_gap_cm, float(z)) for x, y, z in face]
            mirrored_faces.append(list(reversed(mirrored)))
        return right_faces + mirrored_faces

    def export_build_sheet_pdf_file(self):
        self.update_build_sheet_notes_from_fields()

        filename, _ = QFileDialog.getSaveFileName(self, "Export Build Sheet PDF", "", "PDF Files (*.pdf)")
        if not filename:
            return
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        try:
            self.write_build_sheet_pdf(filename)
            QMessageBox.information(self, "Build Sheet Exported", f"Saved build sheet PDF:\n{filename}")
        except Exception as exc:
            QMessageBox.warning(self, "Export Failed", f"Could not export build sheet PDF\n{exc}")

    def show_build_sheet_notes_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Build Sheet Notes")
        dialog.setModal(True)
        layout = QVBoxLayout(dialog)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.ExpandingFieldsGrow)

        notes = dict(getattr(self.ski, "build_sheet_notes", default_build_sheet_notes()))
        editors = {}
        for key, label in BUILD_SHEET_NOTE_FIELDS:
            editor = QTextEdit(dialog)
            editor.setAcceptRichText(False)
            editor.setMinimumHeight(48 if key != "additional_notes" else 96)
            editor.setPlainText(str(notes.get(key, "")))
            editors[key] = editor
            form.addRow(label, editor)

        layout.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, parent=dialog)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        self.ski.build_sheet_notes = {key: editors[key].toPlainText().strip() for key, _label in BUILD_SHEET_NOTE_FIELDS}
        return True

    def _shape_dimensions_text(self, shape):
        pts = shape.get("points", [])
        if not pts:
            return "No geometry"
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        length_cm = max(xs) - min(xs)
        width_mm = (max(ys) - min(ys)) * 10.0
        if shape.get("name") in {"core_profile", "camber_profile"}:
            return f"Length {length_cm:.1f} cm    Max height {width_mm:.1f} mm"
        return f"Length {length_cm:.1f} cm    Max width {width_mm:.0f} mm"

    def _vertical_dimension_cm(self, point_a, point_b):
        return abs(point_a.y() - point_b.y()) / PIXELS_PER_CM

    def _horizontal_dimension_mm(self, point_a, point_b):
        return abs(point_a.x() - point_b.x()) / PIXELS_PER_CM * 10.0

    def _build_view_dimension_rows(self):
        rows = []
        ski = self.ski
        pts = ski.points
        if len(pts) >= 5:
            y_top = pts[-1].pos.y()
            y_bottom = pts[0].pos.y()
            y_center = (y_top + y_bottom) / 2.0
            centerline_point = QPointF(0, y_center)
            rows.extend([
                ("Outline", "Overall length", f"{self._vertical_dimension_cm(pts[0].pos, pts[-1].pos):.1f} cm"),
                ("Outline", "Effective edge", f"{self._vertical_dimension_cm(pts[1].pos, pts[-2].pos):.1f} cm"),
                ("Outline", "Tail section", f"{self._vertical_dimension_cm(pts[0].pos, pts[1].pos):.1f} cm"),
                ("Outline", "Tip section", f"{self._vertical_dimension_cm(pts[-1].pos, pts[-2].pos):.1f} cm"),
                ("Outline", "Centerline to mid point", f"{self._vertical_dimension_cm(centerline_point, pts[2].pos):.1f} cm"),
            ])
            for idx, point in enumerate(pts, start=1):
                rows.append(("Outline widths", f"P{idx} mirrored width", f"{abs(point.pos.x() * 2.0) / PIXELS_PER_CM * 10.0:.0f} mm"))

        camber_pts = ski.camber_thickness_points
        if len(camber_pts) >= 6:
            pairs = [
                ("Full camber length", 1, -2),
                ("Camber segment 1", 1, 2),
                ("Camber segment 2", 2, 3),
                ("Camber segment 3", 3, 4),
                ("Camber segment 4", 4, 5),
            ]
            for label, a, b in pairs:
                rows.append(("Camber", label, f"{self._vertical_dimension_cm(camber_pts[a].pos, camber_pts[b].pos):.1f} cm"))
            for i in range(len(camber_pts) - 1):
                p1 = camber_pts[i].pos
                p2 = camber_pts[i + 1].pos
                if abs(p2.x() - p1.x()) >= 0.01:
                    rows.append(("Camber", f"Thickness step {i + 1}", f"{self._horizontal_dimension_mm(p1, p2):.1f} mm"))

        core_pts = ski.core_thickness_points
        if len(core_pts) >= 2:
            for i in range(len(core_pts) - 1):
                rows.append(("Core", f"Core segment {i + 1}", f"{self._vertical_dimension_cm(core_pts[i].pos, core_pts[i + 1].pos):.1f} cm"))
                if abs(core_pts[i + 1].pos.x() - core_pts[i].pos.x()) >= 0.01:
                    rows.append(("Core", f"Thickness step {i + 1}", f"{self._horizontal_dimension_mm(core_pts[i].pos, core_pts[i + 1].pos):.1f} mm"))

        for idx, (_point_a, _point_b, distance_px) in enumerate(ski._get_dimension_entries(), start=1):
            rows.append(("Custom", f"Point dimension {idx}", f"{distance_px / PIXELS_PER_CM:.1f} cm"))
        return rows

    def _draw_pdf_wrapped_text(self, painter, rect, text, color=None):
        painter.save()
        if color is not None:
            painter.setPen(QPen(color, 1))
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.WordWrap)
        painter.drawText(rect, str(text), option)
        painter.restore()

    def _draw_pdf_shape(self, painter, rect, shape, color):
        pts = shape.get("points", [])
        if len(pts) < 2:
            return
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        minx, maxx = min(xs), max(xs)
        miny, maxy = min(ys), max(ys)
        span_x = max(1e-6, maxx - minx)
        span_y = max(1e-6, maxy - miny)
        scale = min(float(rect.width()) / span_x, float(rect.height()) / span_y)
        draw_w = span_x * scale
        draw_h = span_y * scale
        offset_x = rect.left() + (rect.width() - draw_w) * 0.5
        offset_y = rect.top() + (rect.height() - draw_h) * 0.5

        def map_point(pt):
            x, y = float(pt[0]), float(pt[1])
            return QPointF(offset_x + (x - minx) * scale, offset_y + (maxy - y) * scale)

        path = QPainterPath()
        path.moveTo(map_point(pts[0]))
        for pt in pts[1:]:
            path.lineTo(map_point(pt))
        if shape.get("closed", True):
            path.closeSubpath()

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(color, 1.4))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 18)))
        painter.drawPath(path)
        painter.restore()

    def _draw_pdf_dimension_table(self, painter, rect, rows, section_font, body_font, small_font):
        if not rows:
            return
        painter.save()
        painter.setFont(section_font)
        painter.setPen(QPen(QColor(25, 28, 32), 1))
        painter.drawText(QRectF(rect.left(), rect.top(), rect.width(), 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "View Dimensions")

        row_h = 16.0
        top = rect.top() + 28.0
        col_gap = 18.0
        col_w = (rect.width() - col_gap) / 2.0
        split_at = int(math.ceil(len(rows) / 2.0))
        for idx, (group, label, value) in enumerate(rows):
            col = 0 if idx < split_at else 1
            row = idx if idx < split_at else idx - split_at
            x = rect.left() + col * (col_w + col_gap)
            y = top + row * row_h
            if row % 2 == 0:
                painter.fillRect(QRectF(x, y, col_w, row_h), QColor(248, 249, 250))
            painter.setFont(small_font)
            painter.setPen(QPen(QColor(100, 106, 114), 1))
            painter.drawText(QRectF(x + 4, y, 70, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, group)
            painter.setFont(body_font)
            painter.setPen(QPen(QColor(25, 28, 32), 1))
            painter.drawText(QRectF(x + 78, y, col_w - 142, row_h), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
            painter.drawText(QRectF(x + col_w - 62, y, 58, row_h), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, value)
        painter.restore()

    def _pdf_shape_points_from_path(self, path):
        return [QPointF(pt) for pt in path.toFillPolygon()]

    def _build_pdf_core_profile_path(self):
        path = QPainterPath()
        pts = self.ski.core_thickness_points
        if len(pts) < 2:
            return path
        flat_x = self.ski.get_core_profile_left_x()
        path.moveTo(QPointF(flat_x, pts[0].pos.y()))
        path.lineTo(pts[0].pos)
        path.connectPath(self.ski.build_core_curve())
        path.lineTo(QPointF(flat_x, pts[-1].pos.y()))
        path.closeSubpath()
        return path

    def _build_pdf_camber_profile_path(self):
        path = QPainterPath()
        pts = self.ski.camber_thickness_points
        if len(pts) < 2:
            return path
        flat_x = min(p.pos.x() for p in pts) - 50.0
        path.moveTo(QPointF(flat_x, pts[0].pos.y()))
        path.lineTo(pts[0].pos)
        path.connectPath(self.ski.build_camber_curve())
        path.lineTo(QPointF(flat_x, pts[-1].pos.y()))
        path.closeSubpath()
        return path

    def _pdf_rotated_mapper(self, model_points, rect):
        rotated = [QPointF(-pt.y(), pt.x()) for pt in model_points]
        if not rotated:
            return lambda pt: QPointF(rect.center())
        min_x = min(pt.x() for pt in rotated)
        max_x = max(pt.x() for pt in rotated)
        min_y = min(pt.y() for pt in rotated)
        max_y = max(pt.y() for pt in rotated)
        span_x = max(1e-6, max_x - min_x)
        span_y = max(1e-6, max_y - min_y)
        scale = min(rect.width() / span_x, rect.height() / span_y)
        draw_w = span_x * scale
        draw_h = span_y * scale
        offset_x = rect.left() + (rect.width() - draw_w) * 0.5
        offset_y = rect.top() + (rect.height() - draw_h) * 0.5

        def map_point(pt):
            rotated_pt = QPointF(-pt.y(), pt.x())
            return QPointF(
                offset_x + (rotated_pt.x() - min_x) * scale,
                offset_y + (max_y - rotated_pt.y()) * scale,
            )
        return map_point

    def _draw_pdf_arrow(self, painter, tip, tail, size=6.0):
        dx = tip.x() - tail.x()
        dy = tip.y() - tail.y()
        length = math.hypot(dx, dy)
        if length <= 1e-6:
            return
        ux = dx / length
        uy = dy / length
        px = -uy
        py = ux
        left = QPointF(tip.x() - ux * size + px * size * 0.45, tip.y() - uy * size + py * size * 0.45)
        right = QPointF(tip.x() - ux * size - px * size * 0.45, tip.y() - uy * size - py * size * 0.45)
        painter.drawLine(tip, left)
        painter.drawLine(tip, right)

    def _draw_pdf_label(self, painter, pos, text):
        metrics = painter.fontMetrics()
        rect = QRectF(pos.x() - 4, pos.y() - metrics.ascent() - 3, metrics.horizontalAdvance(text) + 8, metrics.height() + 6)
        painter.save()
        painter.setPen(QPen(QColor(205, 210, 216), 1))
        painter.setBrush(QBrush(QColor(255, 255, 255, 235)))
        painter.drawRect(rect)
        painter.setPen(QPen(QColor(20, 24, 30), 1))
        painter.drawText(pos, text)
        painter.restore()

    def _draw_pdf_model_path(self, painter, path, mapper, color):
        pts = self._pdf_shape_points_from_path(path)
        if len(pts) < 2:
            return
        draw_path = QPainterPath()
        draw_path.moveTo(mapper(pts[0]))
        for pt in pts[1:]:
            draw_path.lineTo(mapper(pt))
        draw_path.closeSubpath()
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(QPen(color, 1.8))
        painter.setBrush(QBrush(QColor(color.red(), color.green(), color.blue(), 18)))
        painter.drawPath(draw_path)
        painter.restore()

    def _draw_pdf_vertical_dimension_model(self, painter, mapper, p1, p2, offset_cm, text):
        if p1.y() < p2.y():
            p1, p2 = p2, p1
        offset_px = offset_cm * PIXELS_PER_CM
        x_dim = max(p1.x(), p2.x()) + offset_px
        ext1 = QPointF(x_dim, p1.y())
        ext2 = QPointF(x_dim, p2.y())
        mp1, mp2, me1, me2 = mapper(p1), mapper(p2), mapper(ext1), mapper(ext2)
        painter.drawLine(mp1, me1)
        painter.drawLine(mp2, me2)
        painter.drawLine(me1, me2)
        self._draw_pdf_arrow(painter, me1, me2)
        self._draw_pdf_arrow(painter, me2, me1)
        mid = QPointF((me1.x() + me2.x()) * 0.5 + 6.0, (me1.y() + me2.y()) * 0.5 - 4.0)
        self._draw_pdf_label(painter, mid, text)

    def _draw_pdf_horizontal_dimension_model(self, painter, mapper, p1, p2, offset_cm, text):
        if p1.x() > p2.x():
            p1, p2 = p2, p1
        offset_px = offset_cm * PIXELS_PER_CM
        y_dim = min(p1.y(), p2.y()) - offset_px
        ext1 = QPointF(p1.x(), y_dim)
        ext2 = QPointF(p2.x(), y_dim)
        mp1, mp2, me1, me2 = mapper(p1), mapper(p2), mapper(ext1), mapper(ext2)
        painter.drawLine(mp1, me1)
        painter.drawLine(mp2, me2)
        painter.drawLine(me1, me2)
        self._draw_pdf_arrow(painter, me1, me2)
        self._draw_pdf_arrow(painter, me2, me1)
        mid = QPointF((me1.x() + me2.x()) * 0.5 + 6.0, (me1.y() + me2.y()) * 0.5 - 4.0)
        self._draw_pdf_label(painter, mid, text)

    def _draw_pdf_mirror_dimension_model(self, painter, mapper, point):
        p1 = point
        p2 = QPointF(-point.x(), point.y())
        mp1, mp2 = mapper(p1), mapper(p2)
        painter.drawLine(mp1, mp2)
        self._draw_pdf_arrow(painter, mp1, mp2)
        self._draw_pdf_arrow(painter, mp2, mp1)
        mid = QPointF((mp1.x() + mp2.x()) * 0.5 + 6.0, (mp1.y() + mp2.y()) * 0.5 - 4.0)
        self._draw_pdf_label(painter, mid, f"{abs(point.x() * 2.0) / PIXELS_PER_CM * 10.0:.0f} mm")

    def _draw_pdf_custom_dimension_model(self, painter, mapper, point_a, point_b, distance_px):
        mp1, mp2 = mapper(point_a.pos), mapper(point_b.pos)
        painter.save()
        painter.setPen(QPen(QColor(35, 145, 90), 1.2, Qt.PenStyle.DashLine))
        painter.drawLine(mp1, mp2)
        self._draw_pdf_arrow(painter, mp1, mp2)
        self._draw_pdf_arrow(painter, mp2, mp1)
        mid = QPointF((mp1.x() + mp2.x()) * 0.5 + 6.0, (mp1.y() + mp2.y()) * 0.5 - 4.0)
        self._draw_pdf_label(painter, mid, f"{distance_px / PIXELS_PER_CM:.1f} cm")
        painter.restore()

    def _draw_pdf_dimensioned_shape_panel(self, painter, panel_rect, title, path, color, dimension_kind, font_scale=1.0):
        title_rect = QRectF(panel_rect.left() + 8.0, panel_rect.top() + 6.0, panel_rect.width() - 16.0, 20.0)
        drawing_rect = panel_rect.adjusted(8.0, 30.0, -8.0, -8.0)

        painter.setPen(QPen(QColor(225, 228, 232), 1))
        painter.setBrush(QBrush(QColor(252, 253, 254)))
        painter.drawRect(panel_rect)
        painter.setFont(QFont("Arial", max(9, int(round(11 * font_scale))), QFont.Weight.Bold))
        painter.setPen(QPen(QColor(25, 28, 32), 1))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
        painter.setFont(QFont("Arial", max(6, int(round(7 * font_scale)))))
        painter.setPen(QPen(QColor(90, 96, 104), 1))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "Rotated 90 degrees")
        painter.setPen(QPen(QColor(225, 228, 232), 1))
        painter.drawRect(drawing_rect)

        shape_pts = self._pdf_shape_points_from_path(path)
        extra_pts = list(shape_pts)
        ski = self.ski
        if dimension_kind == "outline" and len(ski.points) >= 5:
            extra_pts.extend([p.pos for p in ski.points])
            extra_pts.extend([QPointF(-p.pos.x(), p.pos.y()) for p in ski.points])
        elif dimension_kind == "core":
            extra_pts.extend([p.pos for p in ski.core_thickness_points])
        elif dimension_kind == "camber":
            extra_pts.extend([p.pos for p in ski.camber_thickness_points])

        mapper = self._pdf_rotated_mapper(extra_pts, drawing_rect.adjusted(28.0, 28.0, -28.0, -28.0))
        self._draw_pdf_model_path(painter, path, mapper, color)

        painter.save()
        painter.setFont(QFont("Arial", max(5, int(round(6 * font_scale)))))
        painter.setPen(QPen(QColor(30, 34, 40), 0.9))
        if dimension_kind == "outline":
            pts = ski.points
            if len(pts) >= 5:
                y_center = (pts[-1].pos.y() + pts[0].pos.y()) / 2.0
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[0].pos, pts[-1].pos, 24, f"{self._vertical_dimension_cm(pts[0].pos, pts[-1].pos):.1f} cm")
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[1].pos, pts[-2].pos, 9, f"{self._vertical_dimension_cm(pts[1].pos, pts[-2].pos):.1f} cm")
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[0].pos, pts[1].pos, 15, f"{self._vertical_dimension_cm(pts[0].pos, pts[1].pos):.1f} cm")
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[-1].pos, pts[-2].pos, 15, f"{self._vertical_dimension_cm(pts[-1].pos, pts[-2].pos):.1f} cm")
                self._draw_pdf_vertical_dimension_model(painter, mapper, QPointF(0, y_center), pts[2].pos, 5, f"{self._vertical_dimension_cm(QPointF(0, y_center), pts[2].pos):.1f} cm")
                for point in pts:
                    self._draw_pdf_mirror_dimension_model(painter, mapper, point.pos)
                for point_a, point_b, distance_px in ski._get_dimension_entries():
                    self._draw_pdf_custom_dimension_model(painter, mapper, point_a, point_b, distance_px)
        elif dimension_kind == "core":
            pts = ski.core_thickness_points
            for i in range(len(pts) - 1):
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[i].pos, pts[i + 1].pos, 5, f"{self._vertical_dimension_cm(pts[i].pos, pts[i + 1].pos):.1f} cm")
                if abs(pts[i + 1].pos.x() - pts[i].pos.x()) >= 0.01:
                    self._draw_pdf_horizontal_dimension_model(painter, mapper, pts[i].pos, pts[i + 1].pos, -6 - i * 3, f"{self._horizontal_dimension_mm(pts[i].pos, pts[i + 1].pos):.1f} mm")
        elif dimension_kind == "camber":
            pts = ski.camber_thickness_points
            if len(pts) >= 6:
                self._draw_pdf_vertical_dimension_model(painter, mapper, pts[1].pos, pts[-2].pos, 8, f"{self._vertical_dimension_cm(pts[1].pos, pts[-2].pos):.1f} cm")
                for i in range(1, 5):
                    self._draw_pdf_vertical_dimension_model(painter, mapper, pts[i].pos, pts[i + 1].pos, 4, f"{self._vertical_dimension_cm(pts[i].pos, pts[i + 1].pos):.1f} cm")
            for i in range(len(pts) - 1):
                if abs(pts[i + 1].pos.x() - pts[i].pos.x()) >= 0.01:
                    self._draw_pdf_horizontal_dimension_model(painter, mapper, pts[i].pos, pts[i + 1].pos, -6 - i * 3, f"{self._horizontal_dimension_mm(pts[i].pos, pts[i + 1].pos):.1f} mm")
        painter.restore()

    def _append_dimensioned_shape_sheet(self, writer, painter):
        writer.newPage()
        page_rect = QRectF(0, 0, writer.width(), writer.height())
        margin = 36.0
        content = page_rect.adjusted(margin, margin, -margin, -margin)
        painter.fillRect(page_rect, QColor(255, 255, 255))

        title_rect = QRectF(content.left(), content.top(), content.width(), 24.0)
        painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        painter.setPen(QPen(QColor(25, 28, 32), 1))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Dimensioned Views")
        painter.setFont(QFont("Arial", 8))
        painter.setPen(QPen(QColor(90, 96, 104), 1))
        painter.drawText(title_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, "All views rotated 90 degrees")

        gap = 12.0
        panels_top = content.top() + 34.0
        panel_h = (content.bottom() - panels_top - 2.0 * gap) / 3.0
        panel_w = content.width()
        panels = [
            (QRectF(content.left(), panels_top, panel_w, panel_h), "Dimensioned Outline", self.ski.build_full_shape(), QColor(32, 92, 168), "outline"),
            (QRectF(content.left(), panels_top + panel_h + gap, panel_w, panel_h), "Dimensioned Core Thickness", self._build_pdf_core_profile_path(), QColor(42, 132, 82), "core"),
            (QRectF(content.left(), panels_top + (panel_h + gap) * 2.0, panel_w, panel_h), "Dimensioned Camber", self._build_pdf_camber_profile_path(), QColor(168, 92, 32), "camber"),
        ]
        for panel_rect, title, path, color, kind in panels:
            self._draw_pdf_dimensioned_shape_panel(painter, panel_rect, title, path, color, kind, font_scale=0.86)

    def write_build_sheet_pdf(self, filename):
        writer = QPdfWriter(filename)
        writer.setResolution(96)
        writer.setPageSize(QPageSize(QPageSize.PageSizeId.Letter))

        painter = QPainter(writer)
        try:
            page_rect = QRectF(0, 0, writer.width(), writer.height())
            margin = 48.0
            content = page_rect.adjusted(margin, margin, -margin, -margin)

            title_font = QFont("Arial", 22)
            title_font.setBold(True)
            section_font = QFont("Arial", 12)
            section_font.setBold(True)
            body_font = QFont("Arial", 9)
            small_font = QFont("Arial", 8)

            painter.fillRect(page_rect, QColor(255, 255, 255))
            painter.setPen(QPen(QColor(25, 28, 32), 1))
            painter.setFont(title_font)
            painter.drawText(QRectF(content.left(), content.top(), content.width(), 34), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Ski Build Sheet")
            painter.setFont(small_font)
            painter.setPen(QPen(QColor(90, 96, 104), 1))
            painter.drawText(QRectF(content.left(), content.top(), content.width(), 28), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, QDateTime.currentDateTime().toString("yyyy-MM-dd h:mm AP"))

            shape_lookup = {shape.get("name"): shape for shape in self.ski.get_export_shapes(samples=2000, include_all=True)}
            shape_order = [
                ("ski_outline", "Outline", QColor(32, 92, 168)),
                ("core_profile", "Core Thickness", QColor(42, 132, 82)),
                ("camber_profile", "Camber", QColor(168, 92, 32)),
            ]

            y = content.top() + 52.0
            shape_h = 128.0
            gap = 18.0
            for shape_name, title, color in shape_order:
                shape = shape_lookup.get(shape_name)
                panel = QRectF(content.left(), y, content.width(), shape_h)
                painter.setPen(QPen(QColor(195, 200, 206), 1))
                painter.setBrush(QBrush(QColor(250, 251, 252)))
                painter.drawRect(panel)
                painter.setFont(section_font)
                painter.setPen(QPen(QColor(25, 28, 32), 1))
                painter.drawText(QRectF(panel.left() + 12, panel.top() + 8, panel.width() - 24, 20), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
                painter.setFont(body_font)
                painter.setPen(QPen(QColor(70, 76, 84), 1))
                dims = self._shape_dimensions_text(shape) if shape is not None else "No geometry"
                painter.drawText(QRectF(panel.left() + 12, panel.top() + 30, panel.width() - 24, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, dims)
                if shape is not None:
                    self._draw_pdf_shape(painter, QRectF(panel.left() + 12, panel.top() + 52, panel.width() - 24, panel.height() - 62), shape, color)
                y += shape_h + gap

            if y + 310.0 > content.bottom():
                writer.newPage()
                page_rect = QRectF(0, 0, writer.width(), writer.height())
                content = page_rect.adjusted(margin, margin, -margin, -margin)
                painter.fillRect(page_rect, QColor(255, 255, 255))
                painter.setFont(section_font)
                painter.setPen(QPen(QColor(25, 28, 32), 1))
                painter.drawText(QRectF(content.left(), content.top(), content.width(), 24), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Ski Build Sheet")
                y = content.top() + 42.0

            notes = getattr(self.ski, "build_sheet_notes", default_build_sheet_notes())
            painter.setFont(section_font)
            painter.setPen(QPen(QColor(25, 28, 32), 1))
            painter.drawText(QRectF(content.left(), y, content.width(), 22), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, "Materials and Notes")
            y += 28.0

            row_h = 44.0
            col_gap = 18.0
            col_w = (content.width() - col_gap) / 2.0
            for idx, (key, label) in enumerate(BUILD_SHEET_NOTE_FIELDS):
                is_wide = key == "additional_notes"
                col = idx % 2
                x = content.left() if is_wide else content.left() + col * (col_w + col_gap)
                w = content.width() if is_wide else col_w
                if is_wide and col == 1:
                    y += row_h + 8.0
                rect = QRectF(x, y, w, 86.0 if is_wide else row_h)
                painter.setPen(QPen(QColor(205, 210, 216), 1))
                painter.setBrush(QBrush(QColor(250, 251, 252)))
                painter.drawRect(rect)
                painter.setFont(small_font)
                painter.setPen(QPen(QColor(82, 88, 96), 1))
                painter.drawText(QRectF(rect.left() + 8, rect.top() + 5, rect.width() - 16, 14), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, label)
                painter.setFont(body_font)
                self._draw_pdf_wrapped_text(painter, QRectF(rect.left() + 8, rect.top() + 22, rect.width() - 16, rect.height() - 28), notes.get(key, ""), QColor(20, 24, 30))
                if is_wide or col == 1:
                    y += rect.height() + 8.0
            self._append_dimensioned_shape_sheet(writer, painter)
        finally:
            painter.end()
    def write_ascii_stl(self, filename, faces):
        def sub(a, b):
            return (a[0] - b[0], a[1] - b[1], a[2] - b[2])

        def cross(a, b):
            return (
                a[1] * b[2] - a[2] * b[1],
                a[2] * b[0] - a[0] * b[2],
                a[0] * b[1] - a[1] * b[0],
            )

        def normalize(v):
            mag = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
            if mag <= 1e-12:
                return (0.0, 0.0, 0.0)
            return (v[0] / mag, v[1] / mag, v[2] / mag)

        def write_triangle(f, p1, p2, p3):
            n = normalize(cross(sub(p2, p1), sub(p3, p1)))
            f.write(f"  facet normal {n[0]:.8g} {n[1]:.8g} {n[2]:.8g}\n")
            f.write("    outer loop\n")
            f.write(f"      vertex {p1[0]:.8g} {p1[1]:.8g} {p1[2]:.8g}\n")
            f.write(f"      vertex {p2[0]:.8g} {p2[1]:.8g} {p2[2]:.8g}\n")
            f.write(f"      vertex {p3[0]:.8g} {p3[1]:.8g} {p3[2]:.8g}\n")
            f.write("    endloop\n")
            f.write("  endfacet\n")

        with open(filename, "w", encoding="utf-8") as f:
            f.write("solid ski\n")
            for face in faces:
                if len(face) < 3:
                    continue
                if len(face) == 3:
                    write_triangle(f, face[0], face[1], face[2])
                elif len(face) == 4:
                    write_triangle(f, face[0], face[1], face[2])
                    write_triangle(f, face[0], face[2], face[3])
                else:
                    for i in range(1, len(face) - 1):
                        write_triangle(f, face[0], face[i], face[i + 1])
            f.write("endsolid ski\n")
    def toggle_points(self):

        self.ski.show_points = not self.ski.show_points

        if self.ski.show_points:
            self.toggle_points_button.setText("Hide Points")
        else:
            self.toggle_points_button.setText("Show Points")

        self.ski.update()
    def toggle_dimensions(self):

        self.ski.show_dimensions = not self.ski.show_dimensions
        
        if self.ski.show_dimensions:
            self.toggle_dimensions_button.setText("Hide Dimensions")
        else:
            self.toggle_dimensions_button.setText("Show Dimensions")

        self.ski.update()
    def toggle_circle(self):

        self.ski.show_sidecut_circle = not self.ski.show_sidecut_circle

        if self.ski.show_sidecut_circle:
            self.toggle_circle_button.setText("Hide Sidecut Circle")
        else:
            self.toggle_circle_button.setText("Show Sidecut Circle")

        self.ski.update()

    def toggle_global_coordinates(self):

        self.ski.show_global_coordinates = not self.ski.show_global_coordinates

        if self.ski.show_global_coordinates:
            self.toggle_global_coordinates_button.setText("Hide Global Coordinates")
        else:
            self.toggle_global_coordinates_button.setText("Show Global Coordinates")

        self.ski.update()

    def toggle_stiffness_plot(self):

        if self.toggle_stiffness_plot_button.isChecked():
            self.toggle_stiffness_plot_button.setText("Hide Stiffness Plot")
        else:
            self.toggle_stiffness_plot_button.setText("Show Stiffness Plot")

        self.ski.update()

    def toggle_stats(self):

        if self.toggle_stats_button.isChecked():
            self.toggle_stats_button.setText("Hide Geometry Stats")
        else:
            self.toggle_stats_button.setText("Show Geometry Stats")

        self.ski.update()

    def toggle_cnc_stats(self):

        if self.toggle_cnc_stats_button.isChecked():
            self.toggle_cnc_stats_button.setText("Hide CNC Stats")
        else:
            self.toggle_cnc_stats_button.setText("Show CNC Stats")

        self.ski.update()

    def toggle_interface_shortcuts(self):

        if self.toggle_interface_shortcuts_button.isChecked():
            self.toggle_interface_shortcuts_button.setText("Hide Interface Shortcuts")
        else:
            self.toggle_interface_shortcuts_button.setText("Interface Shortcuts")

        self.ski.update()
# =========================
# Main
# =========================
def main():

    app = QApplication(sys.argv)

    preview_ski = SkiShape()
    startup_dialog = StartupDialog(preview_ski.get_startup_values())
    if startup_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)

    window = MainWindow(startup_dialog.values())
    window.show()

    sys.exit(app.exec())

if __name__=="__main__":
    main()
    
