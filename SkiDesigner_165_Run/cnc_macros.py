"""Named G-code links and a small motion-sequence editor."""
import copy
import json
import math
import re
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QDialog, QComboBox, QCheckBox,
    QLineEdit, QPushButton, QDoubleSpinBox, QListWidget, QMessageBox,
    QFileDialog, QDialogButtonBox, QInputDialog,
    QSizePolicy, QScrollArea,
)

NUMERIC_FIELDS = {
    "distance": ("Distance", 0.001, 100000, 10, " mm"),
    "feed": ("Feed", 0.001, 100000, 300, " mm/min"),
    "seconds": ("Pause Time", 0, 86400, 1, " s"),
    "safe_z": ("Home Travel Z (G54)", 0.001, 10000, 10, " mm"),
    "rpm": ("Spindle RPM", 0, 100000, 10000, " RPM"),
    "radius": ("Radius", 0.001, 100000, 10, " mm"),
    "start_angle": ("Start Angle", -360, 360, 0, " deg"),
    "sweep_angle": ("Sweep Angle", 0.001, 360, 90, " deg"),
}


def step_numeric_fields(step):
    kind = step.get("kind")
    if kind == "Spindle" and step.get("spindle_action", "Off") != "Off":
        return ("rpm",)
    return {
        "Move": ("distance", "feed"),
        "Pause": ("seconds",),
        "Return to Work Home": ("safe_z",),
        "Circle": ("radius", "start_angle", "feed"),
        "Arc": ("radius", "start_angle", "sweep_angle", "feed"),
    }.get(kind, ())


def numeric_field(key, value=None):
    _, minimum, maximum, default, suffix = NUMERIC_FIELDS[key]
    spin = QDoubleSpinBox()
    spin.setDecimals(3)
    spin.setRange(minimum, maximum)
    spin.setValue(default if value is None else value)
    spin.setSuffix(suffix)
    return spin


def build_macro_code(name, steps):
    comment_name = name.replace("\n", " ").replace("\r", " ").encode("ascii", errors="replace").decode("ascii")
    lines = ["; Macro " + comment_name, "G21", "G54", "G90", "G94", "G17"]
    if not steps:
        raise ValueError("Add at least one step.")
    for step in steps:
        kind = step["kind"]
        if kind == "Move":
            axis = step["axis"]
            distance, feed = float(step["distance"]), float(step["feed"])
            if axis not in ("X+", "X-", "Y+", "Y-", "Z+", "Z-"):
                raise ValueError("Invalid move direction.")
            if not all(math.isfinite(v) and v > 0 for v in (distance, feed)):
                raise ValueError("Distance and feed must be positive.")
            signed = distance if axis[1] == "+" else -distance
            lines.extend([f"G91 G1 {axis[0]}{signed:.4f} F{feed:.3f}", "G90"])
        elif kind == "Pause":
            seconds = float(step["seconds"])
            if not math.isfinite(seconds) or seconds < 0:
                raise ValueError("Pause time must be nonnegative.")
            lines.append(f"G4 P{seconds:.3f}")
        elif kind == "Return to Work Home":
            safe_z = float(step["safe_z"])
            if not math.isfinite(safe_z) or safe_z <= 0:
                raise ValueError("Home travel Z must be above work zero.")
            lines.extend(["G90 G54", f"G0 Z{safe_z:.3f}", "G0 X0 Y0"])
        elif kind == "Spindle":
            action = step.get("spindle_action", "Off")
            rpm = float(step.get("rpm", 10000))
            if not math.isfinite(rpm) or not 0 <= rpm <= 100000:
                raise ValueError("Spindle RPM must be between 0 and 100000.")
            if action == "Off":
                lines.append("M5")
            elif action in {"On Clockwise", "On Counterclockwise"}:
                lines.append(f"{'M3' if action == 'On Clockwise' else 'M4'} S{rpm:.3f}")
            elif action == "Set RPM":
                lines.append(f"S{rpm:.3f}")
            else:
                raise ValueError("Unknown spindle action.")
        elif kind == "Coolant":
            state = step.get("coolant", "Off")
            if state not in {"Off", "Flood", "Mist", "Flood + Mist"}:
                raise ValueError("Unknown coolant state.")
            lines.append("M9")
            if state in {"Flood", "Flood + Mist"}:
                lines.append("M8")
            if state in {"Mist", "Flood + Mist"}:
                lines.append("M7")
        elif kind == "Custom Output":
            command = step.get("output_command", "").strip().upper()
            if not re.fullmatch(r"M\d+(?:\s+[PS]\d+(?:\.\d+)?)?", command):
                raise ValueError("Custom Output must be a single M-code with an optional P or S value.")
            if int(re.match(r"M(\d+)", command).group(1)) in {0, 1, 2, 30}:
                raise ValueError("Program-flow M-codes cannot be used as output commands.")
            lines.append(command)
        elif kind in {"Circle", "Arc"}:
            radius = float(step.get("radius", 10))
            feed = float(step["feed"])
            angle = float(step.get("start_angle", 0))
            sweep = 360.0 if kind == "Circle" else float(step.get("sweep_angle", 90))
            if not all(math.isfinite(value) for value in (radius,feed,angle,sweep)):
                raise ValueError("Arc parameters must be finite numbers.")
            if radius <= 0 or feed <= 0 or not 0 < sweep <= 360:
                raise ValueError("Radius and feed must be positive; arc sweep must be greater than 0 and at most 360 degrees.")
            planes = {"XY": ("G17", "X", "Y", "I", "J"),
                      "XZ": ("G18", "Z", "X", "K", "I"),
                      "YZ": ("G19", "Y", "Z", "J", "K")}
            plane = step.get("plane", "XY")
            if plane not in planes or step.get("rotation", "Clockwise") not in {"Clockwise", "Counterclockwise"}:
                raise ValueError("Invalid arc plane or direction.")
            plane_code, u, v, center_u, center_v = planes[plane]
            start = math.radians(angle)
            signed_sweep = math.radians(sweep) * (-1 if step.get("rotation", "Clockwise") == "Clockwise" else 1)
            # IJK centers are relative to the current tool position in GRBL.
            cu, cv = -radius*math.cos(start), -radius*math.sin(start)
            du = radius*(math.cos(start+signed_sweep)-math.cos(start))
            dv = radius*(math.sin(start+signed_sweep)-math.sin(start))
            if kind == "Circle" or sweep == 360:
                du = dv = 0.0
            motion = "G2" if signed_sweep < 0 else "G3"
            lines.extend([f"G91 {plane_code}",
                          f"{motion} {u}{du:.5f} {v}{dv:.5f} {center_u}{cu:.5f} {center_v}{cv:.5f} F{feed:.3f}",
                          "G90 G17"])
        else:
            raise ValueError("Unknown macro step.")
    # End without M2/M30 so a spindle/coolant macro retains its requested output state.
    lines.append("G90")
    return "\n".join(lines) + "\n"


class CncMacros(QWidget):
    def __init__(self, control):
        super().__init__(control)
        self.control = control
        self.path = Path(__file__).resolve().with_name("cnc_macros.json")
        self.macros = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.buttons = QVBoxLayout()
        layout.addLayout(self.buttons)
        configure = QPushButton("Configure Macros")
        configure.clicked.connect(self.configure)
        layout.addWidget(configure)
        try:
            if self.path.exists():
                data = json.loads(self.path.read_text())
                if not isinstance(data, list):
                    raise ValueError("Invalid macro list.")
                self.macros = [entry for entry in data if isinstance(entry, dict)
                               and isinstance(entry.get("name"), str) and isinstance(entry.get("path"), str)]
        except (OSError, ValueError) as exc:
            QTimer.singleShot(0, lambda text=str(exc): self.control._log("Macro settings could not be loaded: " + text))
        self.refresh()

    def refresh(self):
        while self.buttons.count():
            item = self.buttons.takeAt(0)
            item.widget().deleteLater()
        for macro in self.macros:
            button = QPushButton(macro["name"])
            button.setMinimumWidth(0)
            button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
            button.setToolTip(macro["path"])
            button.clicked.connect(lambda checked=False, entry=copy.deepcopy(macro): self.load(entry))
            self.buttons.addWidget(button)

    def load(self, macro):
        if self.control.running:
            self.control._log("Stop the current program before loading another.")
            return
        source = "Macro: " + macro["name"]
        if macro.get("mode") == "Build Steps":
            steps = copy.deepcopy(macro.get("steps", []))
            prompts = [
                (index, key)
                for index, step in enumerate(steps)
                for key in step_numeric_fields(step)
                if key in step.get("adjust_on_load", [])
            ]
            if prompts:
                if self.adjust_values(macro["name"], steps, prompts):
                    self.control._load_safely(lambda: build_macro_code(macro["name"], steps), source)
                return
        path = self.resolve_program_path(macro["path"])
        self.control._load_safely(lambda: path.read_text(), source)

    def resolve_program_path(self, path):
        return self.path.parent / Path(path).expanduser()

    def adjust_values(self, name, steps, prompts):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Adjust {name}")
        layout = QVBoxLayout(dialog)
        content = QWidget()
        form = QFormLayout(content)
        editors = {}
        for index, key in prompts:
            step = steps[index]
            editor = numeric_field(key, step.get(key))
            editors[index, key] = editor
            form.addRow(f"{index + 1}. {step['kind']} - {NUMERIC_FIELDS[key][0]}", editor)
        if len(editors) > 8:
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(content)
            scroll.setFixedHeight(360)
            layout.addWidget(scroll)
        else:
            layout.addWidget(content)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Load Macro")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False
        for (index, key), editor in editors.items():
            steps[index][key] = editor.value()
        return True

    def configure(self):
        dialog = MacroEditor(self)
        dialog.exec()

    def store(self, macros):
        temporary = self.path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(macros, indent=2))
        temporary.replace(self.path)
        self.macros = macros
        self.refresh()


class MacroEditor(QDialog):
    def __init__(self, library):
        super().__init__(library)
        self.library = library
        self.original_name = None
        self.setWindowTitle("CNC Macro Configurer")
        self.resize(560, 600)
        layout = QVBoxLayout(self)
        self.selector = QComboBox()
        layout.addWidget(self.selector)
        form = QFormLayout()
        self.name = QLineEdit()
        self.mode = QComboBox()
        self.mode.addItems(["Build Steps", "Link G-code File"])
        self.file = QLineEdit()
        file_row = QHBoxLayout()
        file_row.addWidget(self.file)
        browse = QPushButton("Browse")
        browse.clicked.connect(self.browse)
        file_row.addWidget(browse)
        form.addRow("Macro Name", self.name)
        form.addRow("Source", self.mode)
        form.addRow("G-code File", file_row)
        layout.addLayout(form)
        self.step_widget = QWidget()
        steps_layout = QVBoxLayout(self.step_widget)
        steps_layout.setContentsMargins(0, 0, 0, 0)
        self.steps = QListWidget()
        self.steps.setFixedHeight(150)
        self.steps.currentRowChanged.connect(self.select_step)
        steps_layout.addWidget(self.steps)
        order = QHBoxLayout()
        for text, callback in [
            ("Up", lambda: self.move_step(-1)), ("Down", lambda: self.move_step(1)),
            ("Remove Step", self.remove_step),
        ]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            order.addWidget(button)
        steps_layout.addLayout(order)
        fields = QFormLayout()
        self.kind = QComboBox()
        self.kind.addItems(["Move", "Pause", "Return to Work Home", "Spindle", "Coolant",
                            "Circle", "Arc", "Custom Output"])
        self.axis = QComboBox()
        self.axis.addItems(["X+", "X-", "Y+", "Y-", "Z+", "Z-"])
        self.distance = numeric_field("distance")
        self.feed = numeric_field("feed")
        self.seconds = numeric_field("seconds")
        self.safe_z = numeric_field("safe_z")
        self.spindle_action = QComboBox()
        self.spindle_action.addItems(["Off", "On Clockwise", "On Counterclockwise", "Set RPM"])
        self.rpm = numeric_field("rpm")
        self.coolant = QComboBox()
        self.coolant.addItems(["Off", "Flood", "Mist", "Flood + Mist"])
        self.coolant.setToolTip("Mist (M7) requires firmware and hardware support.")
        self.output_command = QLineEdit()
        self.output_command.setPlaceholderText("Controller-supported M-code")
        self.output_command.setToolTip("Additional outputs require a matching command supported by your controller firmware.")
        self.plane = QComboBox()
        self.plane.addItems(["XY", "XZ", "YZ"])
        self.rotation = QComboBox()
        self.rotation.addItems(["Clockwise", "Counterclockwise"])
        self.radius = numeric_field("radius")
        self.start_angle = numeric_field("start_angle")
        self.start_angle.setToolTip("Angle of the current tool position around the circle center. 0 degrees places the center one radius in the negative first plane axis.")
        self.sweep_angle = numeric_field("sweep_angle")
        fields.addRow("Step", self.kind)
        fields.addRow("Direction", self.axis)
        fields.addRow("Distance", self.distance)
        fields.addRow("Feed", self.feed)
        fields.addRow("Pause Time", self.seconds)
        fields.addRow("Home Travel Z (G54)", self.safe_z)
        fields.addRow("Spindle Action", self.spindle_action)
        fields.addRow("Spindle RPM", self.rpm)
        fields.addRow("Coolant State", self.coolant)
        fields.addRow("Output M-code", self.output_command)
        fields.addRow("Plane", self.plane)
        fields.addRow("Rotation", self.rotation)
        fields.addRow("Radius", self.radius)
        fields.addRow("Start Angle", self.start_angle)
        fields.addRow("Sweep Angle", self.sweep_angle)
        self.fields = fields
        steps_layout.addLayout(fields)
        self.kind.currentIndexChanged.connect(self.show_step_fields)
        self.spindle_action.currentIndexChanged.connect(self.show_step_fields)
        edit_buttons = QHBoxLayout()
        for text, callback in [("Add Step", self.add_step), ("Update Step", self.update_step)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            edit_buttons.addWidget(button)
        self.adjust_step_button = QPushButton("Adjust on Load...")
        self.adjust_step_button.setEnabled(False)
        self.adjust_step_button.clicked.connect(self.configure_step_adjustments)
        edit_buttons.addWidget(self.adjust_step_button)
        steps_layout.addLayout(edit_buttons)
        steps_layout.addStretch(1)
        layout.addWidget(self.step_widget)
        self.mode.currentIndexChanged.connect(lambda: self.step_widget.setVisible(self.mode.currentIndex() == 0))
        actions = QHBoxLayout()
        for text, callback in [("Save Macro", self.save), ("Delete Macro", self.delete),
                               ("Close", self.reject)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            actions.addWidget(button)
        layout.addLayout(actions)
        self.selector.currentIndexChanged.connect(self.select_macro)
        self.refresh_selector()
        self.show_step_fields()

    def refresh_selector(self, name=None):
        self.selector.blockSignals(True)
        self.selector.clear()
        self.selector.addItem("New Macro", None)
        for entry in self.library.macros:
            self.selector.addItem(entry["name"], entry["name"])
        self.selector.setCurrentIndex(max(0, self.selector.findData(name)))
        self.selector.blockSignals(False)
        self.select_macro()

    def select_macro(self, *_args):
        self.original_name = self.selector.currentData()
        entry = next((e for e in self.library.macros if e["name"] == self.original_name), {})
        self.name.setText(entry.get("name", ""))
        path = entry.get("path")
        self.file.setText(str(self.library.resolve_program_path(path)) if path else "")
        self.mode.setCurrentText(entry.get("mode", "Link G-code File" if entry else "Build Steps"))
        self.step_widget.setVisible(self.mode.currentIndex() == 0)
        self.steps.clear()
        for step in entry.get("steps", []):
            self.append_step(copy.deepcopy(step))

    def show_step_fields(self, *_args):
        kind = self.kind.currentText()
        circular = kind in {"Circle", "Arc"}
        visibility = (
            (self.axis, kind == "Move"), (self.distance, kind == "Move"),
            (self.feed, kind == "Move" or circular),
            (self.seconds, kind == "Pause"), (self.safe_z, kind == "Return to Work Home"),
            (self.spindle_action, kind == "Spindle"),
            (self.rpm, kind == "Spindle" and self.spindle_action.currentText() != "Off"),
            (self.coolant, kind == "Coolant"), (self.output_command, kind == "Custom Output"),
            (self.plane, circular), (self.rotation, circular), (self.radius, circular),
            (self.start_angle, circular), (self.sweep_angle, kind == "Arc"),
        )
        for widget, visible in visibility:
            self.fields.setRowVisible(widget, visible)

    def step_value(self):
        return {"kind": self.kind.currentText(), "axis": self.axis.currentText(),
                "distance": self.distance.value(), "feed": self.feed.value(),
                "seconds": self.seconds.value(), "safe_z": self.safe_z.value(),
                "spindle_action": self.spindle_action.currentText(), "rpm": self.rpm.value(),
                "coolant": self.coolant.currentText(), "output_command": self.output_command.text(),
                "plane": self.plane.currentText(), "rotation": self.rotation.currentText(),
                "radius": self.radius.value(), "start_angle": self.start_angle.value(),
                "sweep_angle": self.sweep_angle.value()}

    def step_label(self, step):
        label = self.step_description(step)
        if any(key in step.get("adjust_on_load", []) for key in step_numeric_fields(step)):
            label += " (adjustable)"
        return label

    def step_description(self, step):
        if step["kind"] == "Move":
            return f"Move {step['axis']} {step['distance']:g} mm at {step['feed']:g} mm/min"
        if step["kind"] == "Pause":
            return f"Pause {step['seconds']:g} seconds"
        if step["kind"] == "Spindle":
            return f"Spindle {step.get('spindle_action', 'Off')} - {step.get('rpm',10000):g} RPM"
        if step["kind"] == "Coolant":
            return "Coolant " + step.get("coolant", "Off")
        if step["kind"] == "Custom Output":
            return "Output " + step.get("output_command", "")
        if step["kind"] in {"Circle", "Arc"}:
            sweep = 360 if step["kind"] == "Circle" else step.get("sweep_angle",90)
            return f"{step['kind']} {step.get('plane','XY')} R{step.get('radius',10):g} {sweep:g} deg {step.get('rotation','Clockwise')}"
        return f"Return G54 X0 Y0 at Z{step['safe_z']:g}"

    def append_step(self, step):
        self.steps.addItem(self.step_label(step))
        self.steps.item(self.steps.count()-1).setData(Qt.ItemDataRole.UserRole, step)

    def add_step(self):
        self.append_step(self.step_value())
        self.steps.setCurrentRow(self.steps.count()-1)

    def update_step(self):
        item = self.steps.currentItem()
        if item is not None:
            step = self.step_value()
            old = item.data(Qt.ItemDataRole.UserRole)
            step["adjust_on_load"] = [
                key for key in old.get("adjust_on_load", []) if key in step_numeric_fields(step)
            ]
            item.setData(Qt.ItemDataRole.UserRole, step)
            item.setText(self.step_label(step))
            self.adjust_step_button.setEnabled(bool(step_numeric_fields(step)))

    def configure_step_adjustments(self):
        item = self.steps.currentItem()
        if item is None:
            return
        step = item.data(Qt.ItemDataRole.UserRole)
        keys = step_numeric_fields(step)
        if not keys:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Adjust on Load - Step {self.steps.currentRow() + 1}")
        layout = QVBoxLayout(dialog)
        choices = {}
        for key in keys:
            checkbox = QCheckBox(NUMERIC_FIELDS[key][0])
            checkbox.setChecked(key in step.get("adjust_on_load", []))
            choices[key] = checkbox
            layout.addWidget(checkbox)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            step["adjust_on_load"] = [key for key, checkbox in choices.items() if checkbox.isChecked()]
            item.setData(Qt.ItemDataRole.UserRole, step)
            item.setText(self.step_label(step))

    def select_step(self, row):
        if row < 0:
            self.adjust_step_button.setEnabled(False)
            return
        step = self.steps.item(row).data(Qt.ItemDataRole.UserRole)
        self.adjust_step_button.setEnabled(bool(step_numeric_fields(step)))
        self.kind.setCurrentText(step["kind"])
        self.axis.setCurrentText(step["axis"])
        for key in ("distance", "feed", "seconds", "safe_z"):
            getattr(self, key).setValue(step[key])
        for key, default in (("rpm",10000), ("radius",10), ("start_angle",0), ("sweep_angle",90)):
            getattr(self, key).setValue(step.get(key, default))
        for key, default in (("spindle_action","Off"), ("coolant","Off"), ("plane","XY"), ("rotation","Clockwise")):
            getattr(self, key).setCurrentText(step.get(key, default))
        self.output_command.setText(step.get("output_command", ""))
        self.show_step_fields()

    def move_step(self, direction):
        row = self.steps.currentRow()
        target = row+direction
        if row >= 0 and 0 <= target < self.steps.count():
            item = self.steps.takeItem(row)
            self.steps.insertItem(target, item)
            self.steps.setCurrentRow(target)

    def remove_step(self):
        if self.steps.currentRow() >= 0:
            self.steps.takeItem(self.steps.currentRow())

    def browse(self):
        if self.mode.currentIndex() == 0:
            path, _ = QFileDialog.getSaveFileName(self, "Macro G-code File", self.file.text(), "G-code (*.nc *.gcode *.tap)")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Link G-code File", self.file.text(), "G-code (*.nc *.gcode *.tap);;All Files (*)")
        if path:
            self.file.setText(path)

    def save(self):
        try:
            name = self.name.text().strip()
            if not name:
                name, accepted = QInputDialog.getText(self, "Save Macro", "Macro Name")
                name = name.strip()
                if not accepted or not name:
                    return
                self.name.setText(name)
            if any(e["name"] == name and e["name"] != self.original_name for e in self.library.macros):
                raise ValueError("That macro name is already used.")
            if self.mode.currentIndex() == 0 and not self.steps.count():
                self.add_step()
            if not self.file.text().strip():
                if self.mode.currentIndex() == 0:
                    filename = re.sub(r"[^\w.-]+", "_", name).strip("._") or "macro"
                    path_text, _ = QFileDialog.getSaveFileName(
                        self, "Save Macro G-code", str(self.library.path.parent / (filename+".nc")),
                        "G-code (*.nc *.gcode *.tap)")
                    if path_text and not Path(path_text).suffix:
                        path_text += ".nc"
                else:
                    path_text, _ = QFileDialog.getOpenFileName(
                        self, "Link G-code File", "", "G-code (*.nc *.gcode *.tap);;All Files (*)")
                if not path_text:
                    return
                self.file.setText(path_text)
            path = self.library.resolve_program_path(self.file.text()).resolve()
            if path == self.library.path.resolve():
                raise ValueError("Choose a G-code file separate from the macro settings file.")
            steps = [self.steps.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.steps.count())]
            code = build_macro_code(name, steps) if self.mode.currentIndex() == 0 else None
            if code is not None and path.suffix.lower() not in {".nc", ".gcode", ".tap"}:
                raise ValueError("Use .nc, .gcode, or .tap for the generated file.")
            if code is None and not path.is_file():
                raise ValueError("The linked G-code file does not exist.")
            if code is not None and path.exists():
                if QMessageBox.question(self, "Replace Macro G-code", f"Replace {path.name}?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                    return
            stored_path = path.relative_to(self.library.path.parent) if path.is_relative_to(self.library.path.parent) else path
            entry = {"name": name, "path": str(stored_path), "steps": steps if code is not None else [],
                     "mode": self.mode.currentText()}
            macros = [entry if e["name"] == self.original_name else e for e in self.library.macros]
            if self.original_name is None:
                macros.append(entry)
            previous = path.read_bytes() if code is not None and path.exists() else None
            if code is not None:
                temporary = path.with_suffix(path.suffix+".tmp")
                temporary.write_text(code, encoding="ascii")
                temporary.replace(path)
            try:
                self.library.store(macros)
            except OSError:
                if code is not None:
                    if previous is None:
                        path.unlink(missing_ok=True)
                    else:
                        path.write_bytes(previous)
                raise
            self.refresh_selector(name)
        except (OSError, ValueError, KeyError) as exc:
            QMessageBox.warning(self, "Macro Save Failed", str(exc))

    def delete(self):
        if self.original_name is None:
            return
        if QMessageBox.question(self, "Delete Macro", "Remove this macro button? The G-code file will be kept.") != QMessageBox.StandardButton.Yes:
            return
        try:
            self.library.store([e for e in self.library.macros if e["name"] != self.original_name])
            self.refresh_selector()
        except OSError as exc:
            QMessageBox.warning(self, "Macro Delete Failed", str(exc))
