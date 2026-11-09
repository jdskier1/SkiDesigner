"""Asynchronous GRBL 1.1 sender and compact Qt control panel."""
import re
import time
import json
import math
from cnc_gamepad import CncGamepad
from cnc_macros import CncMacros
from pathlib import Path

from PySide6.QtCore import QTimer, QIODevice, QEvent, Qt, QKeyCombination, Signal
from PySide6.QtGui import QKeySequence, QTextCursor
from PySide6.QtSerialPort import QSerialPort, QSerialPortInfo
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QGridLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDoubleSpinBox, QPlainTextEdit, QLineEdit, QFileDialog,
    QMessageBox, QProgressBar,
    QApplication, QDialog, QDialogButtonBox, QFormLayout, QKeySequenceEdit,
    QCheckBox, QAbstractSpinBox, QTextEdit, QScrollArea,
    QToolButton,
)


class GrblControl(QWidget):
    position_changed = Signal()
    def __init__(self, owner):
        super().__init__(owner)
        self.setObjectName("cncControl")
        self.setStyleSheet(
            "QWidget#cncControl QPushButton, QWidget#cncControl QToolButton {"
            "padding: 2px 6px; min-height: 20px; }"
        )
        self.owner = owner
        self.port = QSerialPort(self)
        self.port.readyRead.connect(self._read)
        self.port.errorOccurred.connect(self._serial_error)
        self.buffer = b""
        self.ready = False
        self.state = "Disconnected"
        self.last_status = 0
        self.jog_cancelled_at = 0.0
        self.pending = None
        self.lines = []
        self.index = 0
        self.running = False
        self.paused = False
        self.finishing = False
        self.program = ""
        self.source = ""
        self.wco = None
        self.mpos = None
        self.wpos = None
        self.laser_mode = None
        self.laser_queried = False
        self.preview_segments = []
        self.preview_revision = 0
        self.executed_segment = -1
        self.active_fraction = 0
        self.preview_error = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(4, 4, 4, 4)
        root.setSpacing(4)
        layout = self._section(root, "Machine Connection", expanded=False)
        connection = QHBoxLayout()
        self.ports = QComboBox()
        self.ports.setMinimumWidth(0)
        self.baud = QComboBox()
        self.baud.addItems(["115200", "57600", "9600"])
        connection.addWidget(self.ports, 1)
        connection.addWidget(self.baud)
        layout.addLayout(connection)
        self._buttons(layout, [
            ("Refresh Ports", self.refresh_ports), ("Connect", self.connect_port),
            ("Disconnect", self.disconnect_port),
        ])
        self.status = QLabel("Disconnected")
        self.position = QLabel("Machine XYZ: --\nWork XYZ: --")
        self.telemetry = QLabel("Feed / spindle: --")
        layout.addWidget(self.status)
        self.position.hide()
        layout.addWidget(self.telemetry)
        layout = self._section(root, "File / Program", expanded=False)
        self.source_label = QLabel("No program loaded")
        self.source_label.setWordWrap(True)
        layout.addWidget(self.source_label)
        self._buttons(layout, [
            ("Load File", self.load_file), ("Use Active", self.load_active),
            ("Use Sequence", self.load_sequence),
        ])
        self.macros = CncMacros(self)
        layout.addWidget(self.macros)
        self.progress = QProgressBar()
        self.progress.setFormat("Acknowledged %v / %m")
        layout.addWidget(self.progress)
        self.program_view = QPlainTextEdit()
        self.program_view.setReadOnly(True)
        self.program_view.setFixedHeight(105)
        layout.addWidget(self.program_view)
        self.execution_label = QLabel("Execution progress: --")
        self.execution_label.setWordWrap(True)
        layout.addWidget(self.execution_label)
        view_layout = self._section(root, "View")
        self._buttons(view_layout, [
            ("Home View", owner.set_cnc_home_view), ("Front", owner.set_cnc_front_view),
            ("Top", owner.set_cnc_top_view), ("Side", owner.set_cnc_side_view),
        ])
        self._buttons(view_layout, [
            ("Recenter", owner.recenter_cnc_preview_view),
            ("Re-scale", lambda: owner.rescale_cnc_preview_view()),
        ])
        self._buttons(view_layout, [
            ("Save View", owner.save_cnc_preview_view),
            ("Custom 1", lambda: owner.load_cnc_preview_view(1)),
            ("Custom 2", lambda: owner.load_cnc_preview_view(2)),
        ])
        layout = self._section(root, "Machine Control", expanded=False)
        machine_layout = layout
        self._buttons(layout, [
            ("Start", self.start), ("Hold", self.hold), ("Resume", self.resume),
        ])
        self._buttons(layout, [
            ("Stop / Reset", self.stop), ("Home ($H)", self.home),
            ("Unlock ($X)", self.unlock),
        ])
        self.laser_button = QPushButton("Laser Mode: Unknown")
        self.laser_button.setCheckable(True)
        self.laser_button.clicked.connect(self.toggle_laser_mode)
        layout.addWidget(self.laser_button)
        jog_settings = QHBoxLayout()
        self.distance = QDoubleSpinBox()
        self.distance.setRange(0.01, 100)
        self.distance.setValue(1)
        self.distance.setSuffix(" mm")
        self.feed = QDoubleSpinBox()
        self.feed.setRange(1, 5000)
        self.feed.setValue(300)
        self.feed.setSuffix(" mm/min")
        jog_settings.addWidget(QLabel("XY Jog"))
        jog_settings.addWidget(self.distance)
        jog_settings.addWidget(self.feed)
        layout.addLayout(jog_settings)
        z_settings = QHBoxLayout()
        self.z_distance = QDoubleSpinBox()
        self.z_distance.setRange(0.01, 100)
        self.z_distance.setValue(1)
        self.z_distance.setSuffix(" mm")
        self.z_feed = QDoubleSpinBox()
        self.z_feed.setRange(1, 5000)
        self.z_feed.setValue(100)
        self.z_feed.setSuffix(" mm/min")
        z_settings.addWidget(QLabel("Z Jog"))
        z_settings.addWidget(self.z_distance)
        z_settings.addWidget(self.z_feed)
        layout.addLayout(z_settings)
        jog = QGridLayout()
        for text, axis, direction, row, col in [
            ("Y+", "Y", 1, 0, 1), ("X-", "X", -1, 1, 0),
            ("X+", "X", 1, 1, 2), ("Y-", "Y", -1, 2, 1),
            ("Z+", "Z", 1, 0, 3), ("Z-", "Z", -1, 2, 3),
        ]:
            button = QPushButton(text)
            button.clicked.connect(lambda checked=False, a=axis, d=direction: self.jog(a, d))
            jog.addWidget(button, row, col)
        cancel = QPushButton("Cancel Jog")
        cancel.clicked.connect(lambda: self._realtime(b"\x85"))
        jog.addWidget(cancel, 1, 1)
        layout.addLayout(jog)
        self._buttons(layout, [
            ("Zero X", lambda: self.zero("X")), ("Zero Y", lambda: self.zero("Y")),
            ("Zero Z", lambda: self.zero("Z")), ("Zero XYZ", lambda: self.zero("XYZ")),
        ])
        layout.addWidget(QLabel("Work zero uses G54. Home runs the controller's homing cycle."))
        layout = self._section(root, "Overrides")
        self._buttons(layout, [
            ("Feed -10%", lambda: self._realtime(b"\x92")),
            ("Feed 100%", lambda: self._realtime(b"\x90")),
            ("Feed +10%", lambda: self._realtime(b"\x91")),
        ])
        self._buttons(layout, [
            ("Spindle -10%", lambda: self._realtime(b"\x9b")),
            ("Spindle 100%", lambda: self._realtime(b"\x99")),
            ("Spindle +10%", lambda: self._realtime(b"\x9a")),
        ])
        spindle_row = QHBoxLayout()
        self.spindle_rpm = QDoubleSpinBox()
        self.spindle_rpm.setRange(0, 100000)
        self.spindle_rpm.setDecimals(0)
        self.spindle_rpm.setValue(10000)
        self.spindle_rpm.setSuffix(" RPM")
        spindle_row.addWidget(self.spindle_rpm)
        spindle_on = QPushButton("Spindle On")
        spindle_on.clicked.connect(lambda: self.manual(f"M3 S{self.spindle_rpm.value():.0f}"))
        spindle_off = QPushButton("Spindle Off")
        spindle_off.clicked.connect(lambda: self.manual("M5"))
        spindle_row.addWidget(spindle_on)
        spindle_row.addWidget(spindle_off)
        layout.addLayout(spindle_row)
        layout = machine_layout
        self._buttons(layout, [
            ("Settings ($$)", lambda: self.manual("$$", allow_alarm=True)),
            ("Parser ($G)", lambda: self.manual("$G")),
            ("Offsets ($#)", lambda: self.manual("$#", allow_alarm=True)),
        ])
        command_row = QHBoxLayout()
        self.command = QLineEdit()
        self.command.setPlaceholderText("Manual command")
        send = QPushButton("Send")
        send.clicked.connect(self.send_manual)
        self.command.returnPressed.connect(self.send_manual)
        command_row.addWidget(self.command)
        command_row.addWidget(send)
        layout.addLayout(command_row)
        self.console = QPlainTextEdit()
        self.console.setReadOnly(True)
        self.console.setMaximumBlockCount(1500)
        self.console.setFixedHeight(90)
        layout.addWidget(self.console)
        layout = self._section(root, "Hardware Interfaces")
        self.keyboard_enabled = QCheckBox("Enable CNC Keyboard / Pendant")
        self._configuring_shortcuts = False
        layout.addWidget(self.keyboard_enabled)
        shortcuts_button = QPushButton("Configure Keyboard Shortcuts")
        shortcuts_button.clicked.connect(self.configure_shortcuts)
        layout.addWidget(shortcuts_button)
        self.shortcut_actions = {
            "Jog X+": lambda: self.jog("X", 1),
            "Jog X-": lambda: self.jog("X", -1),
            "Jog Y+": lambda: self.jog("Y", 1),
            "Jog Y-": lambda: self.jog("Y", -1),
            "Jog Z+": lambda: self.jog("Z", 1),
            "Jog Z-": lambda: self.jog("Z", -1),
            "Cancel Jog": lambda: self._realtime(b"\x85"),
            "Start Program": self.start, "Hold": self.hold, "Resume": self.resume,
            "Stop / Reset": self.stop, "Home": self.home,
            "Zero X": lambda: self.zero("X"), "Zero Y": lambda: self.zero("Y"),
            "Zero Z": lambda: self.zero("Z"), "Zero XYZ": lambda: self.zero("XYZ"),
            "Toggle Laser Mode": self.toggle_laser_mode,
        }
        self.shortcuts = {name: "" for name in self.shortcut_actions}
        self.shortcuts.update({
            "Jog X+": "Right", "Jog X-": "Left",
            "Jog Y+": "Up", "Jog Y-": "Down",
            "Jog Z+": "PgUp", "Jog Z-": "PgDown", "Cancel Jog": "Esc",
        })
        self.shortcuts_path = Path(__file__).resolve().with_name("cnc_keyboard_shortcuts.json")
        try:
            if self.shortcuts_path.exists():
                self.shortcuts = self._validate_shortcuts(json.loads(self.shortcuts_path.read_text()))
        except (OSError, ValueError) as exc:
            self._log("Could not load keyboard shortcuts: " + str(exc))
        self.keyboard_status = QLabel()
        self.keyboard_status.setWordWrap(True)
        layout.addWidget(self.keyboard_status)
        self.keyboard_enabled.toggled.connect(self._update_keyboard_status)
        self._update_keyboard_status()
        QApplication.instance().installEventFilter(self)
        self.gamepad = CncGamepad(self)
        layout.addWidget(self.gamepad)
        self.poll = QTimer(self)
        self.poll.setInterval(250)
        self.poll.timeout.connect(self._poll)
        for child_layout in self.findChildren(QVBoxLayout) + self.findChildren(QHBoxLayout) + self.findChildren(QGridLayout):
            child_layout.setSpacing(3)
        self.refresh_ports()

    def _buttons(self, layout, definitions):
        row = QHBoxLayout()
        for label, callback in definitions:
            button = QPushButton(label)
            if label == "Stop / Reset":
                button.setStyleSheet("QPushButton { background-color: #701f26; color: white; } QPushButton:hover { background-color: #902b34; }")
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)

    def _section(self, root, title, expanded=False):
        container = QWidget()
        container.setObjectName("collapsiblePanel")
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(2)
        toggle = QToolButton()
        toggle.setObjectName("collapsiblePanelToggle")
        toggle.setText(title)
        toggle.setCheckable(True)
        toggle.setChecked(expanded)
        toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        body = QWidget()
        content = QVBoxLayout(body)
        content.setContentsMargins(3, 2, 3, 2)
        body.setVisible(expanded)
        toggle.toggled.connect(body.setVisible)
        toggle.toggled.connect(lambda checked: toggle.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow))
        outer.addWidget(toggle)
        outer.addWidget(body)
        root.addWidget(container)
        return content

    @staticmethod
    def _shortcut_text(sequence):
        if sequence.count() == 1:
            combination = sequence[0]
            navigation_keys = {
                Qt.Key.Key_Left, Qt.Key.Key_Right, Qt.Key.Key_Up, Qt.Key.Key_Down,
                Qt.Key.Key_Home, Qt.Key.Key_End, Qt.Key.Key_PageUp, Qt.Key.Key_PageDown,
            }
            if combination.key() in navigation_keys:
                # macOS marks navigation keys as keypad input even on ordinary keyboards.
                modifiers = combination.keyboardModifiers() & ~Qt.KeyboardModifier.KeypadModifier
                sequence = QKeySequence(QKeyCombination(modifiers, combination.key()))
        return sequence.toString(QKeySequence.SequenceFormat.PortableText)

    def _validate_shortcuts(self, saved):
        if not isinstance(saved, dict):
            raise ValueError("Invalid shortcut settings.")
        result, seen = {}, set()
        for name in self.shortcut_actions:
            value = saved.get(name, "")
            if not isinstance(value, str):
                raise ValueError("Invalid shortcut.")
            sequence = QKeySequence.fromString(value, QKeySequence.SequenceFormat.PortableText)
            if sequence.count() > 1:
                raise ValueError("Use a single key or key combination per action.")
            canonical = self._shortcut_text(sequence)
            if canonical and canonical in seen:
                raise ValueError("Each shortcut must be unique.")
            if canonical:
                seen.add(canonical)
            result[name] = canonical
        return result

    def configure_shortcuts(self):
        self._configuring_shortcuts = True
        dialog = QDialog(self)
        dialog.setWindowTitle("CNC Keyboard / Pendant Shortcuts")
        layout = QVBoxLayout(dialog)
        content = QWidget()
        form = QFormLayout(content)
        editors = {}
        for name in self.shortcut_actions:
            editor = QKeySequenceEdit(QKeySequence(self.shortcuts[name]))
            editor.setMaximumSequenceLength(1)
            editors[name] = editor
            form.addRow(name, editor)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        buttons.rejected.connect(dialog.reject)
        def save():
            try:
                settings = self._validate_shortcuts({
                    name: editor.keySequence().toString(QKeySequence.SequenceFormat.PortableText)
                    for name, editor in editors.items()
                })
                temporary = self.shortcuts_path.with_suffix(".json.tmp")
                temporary.write_text(json.dumps(settings, indent=2))
                temporary.replace(self.shortcuts_path)
                self.shortcuts = settings
                dialog.accept()
            except (OSError, ValueError) as exc:
                QMessageBox.warning(dialog, "Shortcut Save Failed", str(exc))
        buttons.accepted.connect(save)
        layout.addWidget(buttons)
        dialog.resize(380, 550)
        try:
            dialog.exec()
        finally:
            self._configuring_shortcuts = False
            self._update_keyboard_status()

    def _update_keyboard_status(self, *_args):
        assigned = [f"{name}: {key}" for name, key in self.shortcuts.items() if key]
        if not assigned:
            self.keyboard_status.setText("No keys assigned. Open Configure Keyboard Shortcuts.")
        elif self.keyboard_enabled.isChecked():
            self.keyboard_status.setText("Keyboard enabled. Click the view or a button before jogging.\n" + " | ".join(assigned))
            self.keyboard_enabled.setFocus()
        else:
            self.keyboard_status.setText("Keyboard disabled. Enable to use assigned keys.")

    def eventFilter(self, watched, event):
        if event.type() == QEvent.Type.ApplicationDeactivate and not self._configuring_shortcuts:
            if self.keyboard_enabled.isChecked():
                self.keyboard_status.setText("Keyboard paused while the app is inactive.")
        if (event.type() == QEvent.Type.WindowDeactivate and watched is self.window()
                and not self._configuring_shortcuts):
            if self.keyboard_enabled.isChecked():
                self.keyboard_status.setText("Keyboard paused while the CNC window is inactive.")
        if event.type() == QEvent.Type.Hide and watched is self:
            if self.keyboard_enabled.isChecked():
                self.keyboard_status.setText("Keyboard paused while CNC Control is hidden.")
        if event.type() not in (QEvent.Type.KeyPress, QEvent.Type.ShortcutOverride):
            return False
        if not self.keyboard_enabled.isChecked() or not self.isVisible() or not self.window().isActiveWindow():
            return False
        if QApplication.activeModalWidget() or QApplication.activePopupWidget():
            return False
        focus = QApplication.focusWidget()
        editing_types = (QLineEdit, QTextEdit, QPlainTextEdit, QAbstractSpinBox, QKeySequenceEdit, QComboBox)
        while focus is not None:
            if isinstance(focus, editing_types):
                if not isinstance(focus, (QLineEdit, QTextEdit, QPlainTextEdit)) or not focus.isReadOnly():
                    self.keyboard_status.setText("Keyboard paused while editing a field. Click Enable CNC Keyboard / Pendant to return focus.")
                    return False
            focus = focus.parentWidget()
        sequence = QKeySequence(QKeyCombination(event.modifiers(), Qt.Key(event.key())))
        text = self._shortcut_text(sequence)
        for name, shortcut in self.shortcuts.items():
            if shortcut and text == shortcut:
                if event.type() == QEvent.Type.ShortcutOverride:
                    event.accept()
                    return True
                if not event.isAutoRepeat():
                    reason = self.command_block_reason() if name.startswith("Jog ") else ""
                    if reason:
                        self.keyboard_status.setText(f"{text} received. Jog blocked: {reason}")
                        return True
                    self.shortcut_actions[name]()
                    self.keyboard_status.setText(f"{text} received: {name}")
                return True
        if event.type() == QEvent.Type.KeyPress and not event.isAutoRepeat():
            self.keyboard_status.setText(f"{text} received; no CNC action is assigned to this key.")
        return False

    def _log(self, text):
        self.console.appendPlainText(text)

    def refresh_ports(self):
        selected = self.ports.currentData()
        self.ports.clear()
        for info in QSerialPortInfo.availablePorts():
            self.ports.addItem(info.portName(), info.systemLocation())
        index = self.ports.findData(selected)
        if index >= 0:
            self.ports.setCurrentIndex(index)

    def connect_port(self):
        if self.port.isOpen() or not self.ports.currentData():
            return
        self.port.setPortName(self.ports.currentData())
        self.port.setBaudRate(int(self.baud.currentText()))
        if not self.port.open(QIODevice.OpenModeFlag.ReadWrite):
            self._log(self.port.errorString())
            return
        self.ready = False
        self.state = "Connecting"
        self.buffer = b""
        self.wco = self.mpos = self.wpos = None
        self.status.setText("Connecting — waiting for GRBL 1.1")
        self.port.setDataTerminalReady(True)
        self.port.write(b"\x18")
        self.poll.start()

    def disconnect_port(self):
        if self.running and QMessageBox.question(
            self, "Disconnect", "Abort the program and disconnect?"
        ) != QMessageBox.StandardButton.Yes:
            return
        self.shutdown()

    def shutdown(self):
        self.gamepad.shutdown()
        if self.port.isOpen():
            self.port.write(b"!\x18")
            self.port.flush()
            self.port.close()
        self.poll.stop()
        self.ready = self.running = self.paused = self.finishing = False
        self.pending = None
        self.jog_cancelled_at = 0.0
        self.state = "Disconnected"
        self.status.setText(self.state)
        self._set_laser_mode(None)
        self.position_changed.emit()

    def _serial_error(self, error):
        if error in (QSerialPort.SerialPortError.ResourceError, QSerialPort.SerialPortError.DeviceNotFoundError):
            self._log(self.port.errorString())
            self.shutdown()

    def _realtime(self, data):
        if self.port.isOpen():
            self.port.write(data)

    def _poll(self):
        if not self.port.isOpen():
            return
        self._realtime(b"?")
        if self.laser_mode is None and not self.laser_queried and self._idle():
            self.laser_queried = True
            self.manual("$$")
        if self.ready and time.monotonic() - self.last_status > 3:
            self.paused = True
            self._realtime(b"!")
            self.status.setText("Status timeout — held; check connection")

    def _read(self):
        self.buffer += bytes(self.port.readAll())
        while b"\n" in self.buffer:
            line, self.buffer = self.buffer.split(b"\n", 1)
            self._receive(line.decode("ascii", errors="replace").strip())

    def _receive(self, line):
        if not line:
            return
        if line.startswith("<"):
            self._status(line)
            return
        self._log("< " + line)
        if line.startswith("Grbl "):
            self._set_laser_mode(None)
            self.laser_queried = False
            self.ready = line.startswith("Grbl 1.1")
            self.running = self.paused = self.finishing = False
            self.pending = None
            self.jog_cancelled_at = 0.0
            self.last_status = 0
            self.state = "Connecting"
            self.status.setText("Connected" if self.ready else "Requires GRBL 1.1")
        elif line.startswith("$32="):
            value = line.split("=", 1)[1].split()[0]
            if value in {"0", "1"}:
                self._set_laser_mode(value == "1")
        elif line.startswith("ALARM:"):
            self.running = self.finishing = False
            self.paused = True
            self.pending = None
            self.state = "Alarm"
            self.status.setText(line)
        elif line.startswith("error:"):
            self.pending = None
            self.running = self.finishing = False
            self.paused = True
            self._realtime(b"!")
            self.status.setText(line + " — program aborted; reset before restarting")
            self.ready = False
        elif line == "ok" and self.pending is not None:
            kind, command = self.pending
            self.pending = None
            if command in {"$32=0", "$32=1"}:
                self._set_laser_mode(command.endswith("1"))
            if kind == "program":
                self.index += 1
                self.progress.setValue(self.index)
                if re.search(r"(?<![A-Z])M0?0(?!\d)", command):
                    self.paused = True
                if self.index == len(self.lines):
                    self.finishing = True
                    self._realtime(b"?")
                else:
                    self._send_next()

    def _status(self, line):
        fields = line.strip("<>").split("|")
        self.state = fields[0].split(":")[0]
        self.last_status = time.monotonic()
        if self.state == "Idle":
            self.jog_cancelled_at = 0.0
        position_kind = None
        for field in fields[1:]:
            key, _, value = field.partition(":")
            if key in {"WCO", "MPos", "WPos"}:
                try:
                    xyz = tuple(float(v) for v in value.split(",")[:3])
                    if len(xyz) != 3:
                        continue
                    if key == "WCO":
                        self.wco = xyz
                    elif key == "MPos":
                        self.mpos = xyz
                        position_kind = key
                    else:
                        self.wpos = xyz
                        position_kind = key
                except ValueError:
                    continue
            elif key == "FS":
                self.telemetry.setText("Feed / spindle: " + value)
        if position_kind == "MPos" and self.mpos and self.wco:
            self.wpos = tuple(a-b for a,b in zip(self.mpos, self.wco))
        elif position_kind == "WPos" and self.wpos and self.wco:
            self.mpos = tuple(a+b for a,b in zip(self.wpos, self.wco))
        def fmt(values):
            return "  ".join(f"{v:.3f}" for v in values) if values else "--"
        self.position.setText(f"Machine XYZ: {fmt(self.mpos)}\nWork XYZ: {fmt(self.wpos)}")
        self.status.setText(self.state + (" — sender paused" if self.paused else ""))
        if self.state in {"Hold", "Door", "Alarm"}:
            self.paused = True
        if self.finishing and self.state == "Idle":
            self.running = self.finishing = False
            self.status.setText("Complete — controller idle")
            self.executed_segment = len(self.preview_segments) - 1
            self.active_fraction = 0
            self.execution_label.setText("Complete — controller idle")
        if self.running:
            self._update_execution_progress()
        self.position_changed.emit()

    def command_block_reason(self, allow_alarm=False, allow_jog=False):
        if not self.port.isOpen():
            return "not connected; open Machine Connection, select the X-Controller port and press Connect."
        if not self.ready:
            return "waiting for the GRBL 1.1 startup response; check Machine Connection and the serial log."
        if time.monotonic() - self.last_status >= 3:
            return "no recent controller status; check the USB connection."
        if self.running:
            return "a program is running; stop it before jogging."
        if self.pending is not None:
            return "waiting for the controller to acknowledge the previous command."
        if self.jog_cancelled_at and (self.last_status <= self.jog_cancelled_at or self.state != "Idle"):
            return "waiting for jog cancellation to finish."
        if self.gamepad.jogging and not allow_jog:
            return "joystick jogging is active; release the stick and hold button first."
        allowed = {"Idle", "Alarm"} if allow_alarm else {"Idle"}
        if allow_jog:
            allowed.add("Jog")
        if self.state not in allowed:
            return f"controller state is {self.state}; it must be Idle before jogging."
        return ""

    def gamepad_jog_block_reason(self):
        return self.command_block_reason(allow_jog=self.gamepad.jogging)

    def stream_gamepad_jog(self, axis, distance, feed):
        if axis not in "XYZ" or len(axis) != 1 or not all(math.isfinite(v) for v in (distance, feed)) or feed <= 0 or distance == 0:
            return False
        if self.gamepad_jog_block_reason():
            return False
        return self._write_line(f"$J=G91 G21 {axis}{distance:.4f} F{feed:.1f}", "jog")

    def cancel_gamepad_jog(self):
        self.jog_cancelled_at = time.monotonic()
        self._realtime(b"\x85")
        self._realtime(b"?")

    def _idle(self, allow_alarm=False):
        return not self.command_block_reason(allow_alarm)

    def manual(self, command, allow_alarm=False):
        reason = self.command_block_reason(allow_alarm)
        if reason:
            self._log("Command blocked: " + reason)
            return False
        return self._write_line(command, "manual")

    def _write_line(self, command, kind):
        data = (command + "\n").encode("ascii")
        if self.port.write(data) != len(data):
            self._log("Serial write failed")
            self.shutdown()
            return False
        self.pending = (kind, command)
        self._log("> " + command)
        return True

    def _load(self, code, source):
        if self.running:
            self._log("Stop the current program before loading another.")
            return
        lines = []
        for line in code.splitlines():
            cleaned = re.sub(r"\([^)]*\)", "", line.split(";")[0]).strip().upper()
            if not cleaned or cleaned == "%":
                continue
            if any(ord(c) > 127 for c in cleaned) or len(cleaned.encode("ascii")) > 79:
                raise ValueError("Program contains a non-ASCII or overlong GRBL block.")
            if any(c in cleaned for c in ("!", "~", "?", "\x18")) or cleaned.startswith("$"):
                raise ValueError("Program contains controller/realtime commands.")
            lines.append(cleaned)
        if not lines:
            raise ValueError("Program has no G-code blocks.")
        self.program, self.source, self.lines = code, source, lines
        self.program_view.setPlainText("\n".join(lines))
        self._prepare_live_preview()
        self.index = 0
        self.progress.setRange(0, len(lines))
        self.progress.setValue(0)
        self.source_label.setText(f"{source} — {len(lines)} blocks")
        self.position_changed.emit()

    def _prepare_live_preview(self):
        self.preview_segments = []
        self.executed_segment = -1
        self.active_fraction = 0
        self.preview_error = ""
        current = self.mpos or (0., 0., 0.)
        offset = self.wco or (0., 0., 0.)
        absolute, scale, mode = True, 1., 0
        plane = (0, 1, 2)
        try:
            for line_index, line in enumerate(self.lines):
                words = [(a, float(b)) for a,b in re.findall(r"([A-Z])([+-]?(?:\d+\.?\d*|\.\d+))", line)]
                g_codes = [v for a,v in words if a == "G"]
                if any(g in {10,28,30,43.1,53,55,56,57,58,59,92,92.1,93} for g in g_codes):
                    raise ValueError("Preview unavailable for coordinate changes or inverse-time blocks.")
                for g in g_codes:
                    if g == 20: scale = 25.4
                    elif g == 21: scale = 1.
                    elif g == 90: absolute = True
                    elif g == 91: absolute = False
                    elif g in {0,1,2,3}: mode = int(g)
                    elif g == 17: plane = (0,1,2)
                    elif g == 18: plane = (2,0,1)
                    elif g == 19: plane = (1,2,0)
                    elif g == 80: mode = None
                values = dict(words)
                if not any(a in values for a in "XYZIJKR") or mode is None:
                    continue
                target = list(current)
                for axis, letter in enumerate("XYZ"):
                    if letter in values:
                        target[axis] = values[letter]*scale + (offset[axis] if absolute else current[axis])
                points = [tuple(target)]
                if mode in {2,3}:
                    u,v,w = plane
                    du, dv = target[u]-current[u], target[v]-current[v]
                    if "R" in values:
                        radius = abs(values["R"]*scale)
                        chord = math.hypot(du,dv)
                        if chord <= 1e-8 or chord > 2*radius+1e-6:
                            raise ValueError("Invalid radius arc.")
                        height = math.sqrt(max(0, radius*radius-chord*chord/4))
                        sign = (1 if mode == 3 else -1) * (1 if values["R"] >= 0 else -1)
                        center = ((current[u]+target[u])/2-sign*dv/chord*height,
                                  (current[v]+target[v])/2+sign*du/chord*height)
                    else:
                        center = (current[u]+values.get("IJK"[u],0)*scale,
                                  current[v]+values.get("IJK"[v],0)*scale)
                        radius = math.hypot(current[u]-center[0],current[v]-center[1])
                    if radius <= 1e-8:
                        raise ValueError("Invalid arc center.")
                    start = math.atan2(current[v]-center[1],current[u]-center[0])
                    end = math.atan2(target[v]-center[1],target[u]-center[0])
                    sweep = (end-start) % (2*math.pi) if mode == 3 else -((start-end) % (2*math.pi))
                    if abs(sweep) < 1e-8:
                        sweep = 2*math.pi if mode == 3 else -2*math.pi
                    count = max(2, int(math.ceil(abs(sweep)*radius/1.0)), int(math.ceil(abs(sweep)/0.05)))
                    if count > 100000:
                        raise ValueError("Arc too large for live preview.")
                    points = []
                    for step in range(1,count+1):
                        t = step/count
                        p = list(current)
                        p[u] = center[0]+radius*math.cos(start+sweep*t)
                        p[v] = center[1]+radius*math.sin(start+sweep*t)
                        p[w] = current[w]+(target[w]-current[w])*t
                        points.append(tuple(p))
                    points[-1] = tuple(target)
                for point in points:
                    if point != current:
                        self.preview_segments.append((current,point,line_index))
                    current = point
            self.execution_label.setText("Execution progress estimated from machine position.")
        except ValueError as exc:
            self.preview_segments = []
            self.preview_error = str(exc)
            self.execution_label.setText(self.preview_error)
        self.preview_revision += 1

    def _update_execution_progress(self):
        if self.mpos is None or not self.preview_segments:
            return
        start_index = self.executed_segment+1
        best = None
        for index in range(start_index, min(len(self.preview_segments), start_index+500)):
            a,b,line = self.preview_segments[index]
            if line > self.index:
                break
            delta = tuple(y-x for x,y in zip(a,b))
            length2 = sum(d*d for d in delta)
            t = max(0., min(1., sum((p-x)*d for p,x,d in zip(self.mpos,a,delta))/length2))
            distance = sum((p-(x+t*d))**2 for p,x,d in zip(self.mpos,a,delta))
            candidate = (distance,index,t)
            if best is None or candidate[:2] < best[:2]:
                best = candidate
        if best is None or best[0] > 0.25:
            return
        _, index, t = best
        self.executed_segment = index if t >= 0.999 else index-1
        self.active_fraction = 0 if t >= 0.999 else t
        line = self.preview_segments[index][2]
        cursor = QTextCursor(self.program_view.document().findBlockByNumber(line))
        cursor.select(QTextCursor.SelectionType.LineUnderCursor)
        self.program_view.setTextCursor(cursor)
        self.program_view.ensureCursorVisible()
        self.execution_label.setText(f"Estimated execution — block {line+1} / {len(self.lines)}")

    def live_preview_groups(self):
        completed, future = [], []
        for index,(a,b,line) in enumerate(self.preview_segments):
            if index <= self.executed_segment:
                completed.append((a,b,"live_done",None))
            elif index == self.executed_segment+1 and self.active_fraction:
                middle = tuple(x+(y-x)*self.active_fraction for x,y in zip(a,b))
                completed.append((a,middle,"live_done",None))
                future.append((middle,b,"live_future",None))
            else:
                future.append((a,b,"live_future",None))
        return [{"segments": segments, "path": [p for seg in segments for p in seg[:2]]}
                for segments in (future,completed) if segments]

    def _load_safely(self, callback, source):
        try:
            self._load(callback(), source)
        except (ValueError, OSError) as exc:
            QMessageBox.warning(self, "Load Failed", str(exc))

    def load_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load CNC Program", "", "G-code (*.nc *.gcode *.tap);;All Files (*)")
        if filename:
            self._load_safely(lambda: Path(filename).read_text(), Path(filename).name)

    def load_active(self):
        self._load_safely(self.owner.build_cnc_gcode, "Active toolpath")

    def load_sequence(self):
        self._load_safely(self.owner._build_cnc_sequence_gcode, "Toolpath sequence")

    def start(self):
        if not self._idle() or not self.lines:
            self._log("Start blocked — load a program and connect an idle controller.")
            return
        if QMessageBox.question(self, "Start Program", f"Run {self.source} on the connected machine?") != QMessageBox.StandardButton.Yes:
            return
        self.index = 0
        self._prepare_live_preview()
        self.running = True
        self.paused = self.finishing = False
        self.progress.setValue(0)
        self._send_next()

    def _send_next(self):
        if self.running and not self.paused and not self.pending and self.index < len(self.lines):
            self._write_line(self.lines[self.index], "program")

    def hold(self):
        self.paused = True
        self._realtime(b"!")

    def resume(self):
        if not self.ready or self.state not in {"Hold", "Idle", "Run"} or time.monotonic()-self.last_status > 3:
            return
        self._realtime(b"~")
        self.paused = False
        self._send_next()

    def stop(self):
        self.running = self.finishing = False
        self.paused = True
        self.pending = None
        self.ready = False
        self._realtime(b"!\x18")
        self.status.setText("Aborted — waiting for GRBL reset")

    def home(self):
        if QMessageBox.question(self, "Home Machine", "Run the configured GRBL homing cycle ($H)?") == QMessageBox.StandardButton.Yes:
            self.manual("$H", allow_alarm=True)

    def unlock(self):
        if QMessageBox.question(self, "Unlock Alarm", "Clear the controller alarm lock ($X)?") == QMessageBox.StandardButton.Yes:
            self.manual("$X", allow_alarm=True)

    def jog(self, axis, direction):
        distance = self.z_distance.value() if axis == "Z" else self.distance.value()
        feed = self.z_feed.value() if axis == "Z" else self.feed.value()
        self.manual(f"$J=G91 G21 {axis}{direction*distance:.3f} F{feed:.1f}")

    def _set_laser_mode(self, enabled):
        self.laser_mode = enabled
        self.laser_button.setChecked(enabled is True)
        text = "Unknown" if enabled is None else ("On" if enabled else "Off")
        self.laser_button.setText("Laser Mode: " + text)

    def toggle_laser_mode(self):
        self.laser_button.setChecked(self.laser_mode is True)
        if self.laser_mode is None:
            self.manual("$$")
        else:
            self.manual("$32=0" if self.laser_mode else "$32=1")

    def zero(self, axes):
        if QMessageBox.question(self, "Set Work Zero", f"Set G54 {axes} zero at the current position?") == QMessageBox.StandardButton.Yes:
            self.manual("G10 L20 P1 " + " ".join(axis+"0" for axis in axes))

    def send_manual(self):
        command = self.command.text().strip().upper()
        if command and "\n" not in command and "\r" not in command:
            self.manual(command)
