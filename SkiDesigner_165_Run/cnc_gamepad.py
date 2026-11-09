"""Configurable SDL joystick input for bounded GRBL jogging."""
import json
import os
import time
from pathlib import Path

from PySide6.QtCore import QTimer, QEvent, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QHBoxLayout, QComboBox, QPushButton,
    QLabel, QCheckBox, QDoubleSpinBox, QApplication, QMessageBox,
)


class CncGamepad(QWidget):
    JOG_SEGMENT_SECONDS = 0.10
    JOG_LOOKAHEAD_SECONDS = 0.25

    def __init__(self, control):
        super().__init__(control)
        self.control = control
        self.backend = None
        self.device = None
        self.jogging = False
        self.jog_queued_until = 0.0
        self.jog_direction = None
        self.previous_buttons = set()
        self.neutral_seen = False
        self.path = Path(__file__).resolve().with_name("cnc_gamepad_settings.json")
        layout = QVBoxLayout(self)
        self.devices = QComboBox()
        layout.addWidget(self.devices)
        row = QHBoxLayout()
        for text, callback in [("Scan Gamepads", self.scan)]:
            button = QPushButton(text)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        self.enable = QCheckBox("Enable Gamepad")
        self.enable.toggled.connect(self._enable_changed)
        layout.addWidget(self.enable)
        self.parameters = QWidget()
        parameters_layout = QVBoxLayout(self.parameters)
        parameters_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.parameters)
        self.parameters.setVisible(False)
        self.status = QLabel("Scan to detect the F710 or another USB gamepad.")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.monitor = QLabel("Axes / buttons: --")
        self.monitor.setWordWrap(True)
        parameters_layout.addWidget(self.monitor)
        form = QFormLayout()
        self.axes = {}
        self.invert = {}
        for axis in "XYZ":
            row = QHBoxLayout()
            combo = QComboBox()
            invert = QCheckBox("Invert")
            row.addWidget(combo)
            row.addWidget(invert)
            self.axes[axis], self.invert[axis] = combo, invert
            form.addRow(axis + " stick axis", row)
            combo.currentIndexChanged.connect(self._mapping_changed)
            invert.toggled.connect(self._mapping_changed)
        self.buttons = {}
        for action in ("Hold to Jog", "Hold", "Cancel Jog", "Stop / Reset", "Start", "Resume", "Home"):
            combo = QComboBox()
            self.buttons[action] = combo
            combo.currentIndexChanged.connect(self._mapping_changed)
            form.addRow(action + " button", combo)
        self.deadzone = QDoubleSpinBox()
        self.deadzone.setRange(0.1, 0.8)
        self.deadzone.setSingleStep(0.05)
        self.deadzone.setValue(0.25)
        self.deadzone.valueChanged.connect(self._mapping_changed)
        form.addRow("Stick dead zone", self.deadzone)
        parameters_layout.addLayout(form)
        save_button = QPushButton("Save Mapping")
        save_button.clicked.connect(self.save)
        parameters_layout.addWidget(save_button)
        self.timer = QTimer(self)
        self.timer.setInterval(20)
        self.timer.setTimerType(Qt.TimerType.PreciseTimer)
        self.timer.timeout.connect(self.poll)
        self.devices.currentIndexChanged.connect(self.select_device)
        QApplication.instance().installEventFilter(self)

    def disarm(self, *_args):
        self.enable.setChecked(False)
        self.neutral_seen = False
        self._stop_jog()

    def _stop_jog(self):
        if self.jogging:
            self.control.cancel_gamepad_jog()
        self.jogging = False
        self.jog_queued_until = 0.0
        self.jog_direction = None

    def _mapping_changed(self, *_args):
        self.neutral_seen = False
        self._stop_jog()

    def _enable_changed(self, checked):
        self.neutral_seen = False
        if not checked:
            self.disarm()
        elif self.device is None:
            self.status.setText("Gamepad enabled, waiting for a device. Scan and select a gamepad.")
        elif self.buttons["Hold to Jog"].currentData() in (None, -1):
            self.status.setText("Gamepad enabled for monitoring. Assign a Hold to Jog button to enable movement.")
        else:
            self.status.setText("Release buttons and center sticks to arm.")

    def eventFilter(self, watched, event):
        if ((event.type() == QEvent.Type.WindowDeactivate and watched is self.window())
                or (event.type() == QEvent.Type.Hide and watched is self)):
            self._mapping_changed()
            if self.enable.isChecked():
                self.status.setText("Gamepad paused while CNC Control is inactive or hidden. Return and center sticks to resume.")
        return False

    def scan(self):
        self._mapping_changed()
        self.timer.stop()
        previous_guid = self.device.get_guid() if self.device is not None else None
        if self.device is not None:
            self.device.quit()
        self.device = None
        try:
            if self.backend is None:
                os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
                os.environ.setdefault("SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS", "1")
                import pygame
                self.backend = pygame
                pygame.display.init()
            self.backend.joystick.quit()
            self.backend.joystick.init()
            self.backend.event.pump()
            self.devices.blockSignals(True)
            try:
                self.devices.clear()
                selected_index = 0
                for index in range(self.backend.joystick.get_count()):
                    device = self.backend.joystick.Joystick(index)
                    device.init()
                    self.devices.addItem(device.get_name(), index)
                    if device.get_guid() == previous_guid:
                        selected_index = index
                self.devices.setCurrentIndex(selected_index if self.devices.count() else -1)
            finally:
                self.devices.blockSignals(False)
            self.select_device()
            self.timer.start()
            if not self.devices.count():
                self.status.setText("No joystick detected. For an F710 on this Mac, close the app, set its X/D switch to D, reconnect the USB receiver, reopen and scan again.")
        except (ImportError, RuntimeError, self.backend.error if self.backend else RuntimeError) as exc:
            self.status.setText("Gamepad unavailable: " + str(exc))

    def select_device(self, *_args):
        self._mapping_changed()
        if self.device is not None:
            self.device.quit()
        self.device = None
        self.parameters.setVisible(False)
        if self.backend is None or self.devices.currentData() is None:
            return
        try:
            self.device = self.backend.joystick.Joystick(self.devices.currentData())
            self.device.init()
            for axis, combo in self.axes.items():
                combo.clear()
                combo.addItem("Disabled", -1)
                for index in range(self.device.get_numaxes()):
                    combo.addItem(str(index), index)
                default = {"X": 0, "Y": 1, "Z": 3}[axis]
                combo.setCurrentIndex(max(0, combo.findData(default)))
                self.invert[axis].setChecked(axis in "YZ")
            for action, combo in self.buttons.items():
                combo.clear()
                combo.addItem("Unassigned", -1)
                for index in range(self.device.get_numbuttons()):
                    combo.addItem(str(index), index)
            self._load_mapping()
            self.previous_buttons = set()
            self.parameters.setVisible(True)
            self.status.setText("Gamepad detected. Assign Hold to Jog, enable the gamepad, then release all buttons and center the sticks.")
        except self.backend.error as exc:
            self.status.setText(str(exc))
            self.device = None

    def _mapping(self):
        return {
            "axes": {a: c.currentData() for a,c in self.axes.items()},
            "invert": {a: c.isChecked() for a,c in self.invert.items()},
            "buttons": {a: c.currentData() for a,c in self.buttons.items()},
            "deadzone": self.deadzone.value(),
            "guid": self.device.get_guid(),
        }

    def save(self):
        if self.device is None:
            return
        try:
            mapping = self._mapping()
            assigned = [v for v in mapping["buttons"].values() if v >= 0]
            axes = [v for v in mapping["axes"].values() if v >= 0]
            if len(set(assigned)) != len(assigned) or len(set(axes)) != len(axes):
                raise ValueError("Assign each axis and button to only one function.")
            temporary = self.path.with_suffix(".json.tmp")
            temporary.write_text(json.dumps(mapping, indent=2))
            temporary.replace(self.path)
            self.status.setText("Gamepad mapping saved.")
        except (OSError, ValueError) as exc:
            QMessageBox.warning(self, "Mapping Save Failed", str(exc))

    def _load_mapping(self):
        if not self.path.exists():
            return
        try:
            saved = json.loads(self.path.read_text())
            if saved.get("guid") != self.device.get_guid():
                return
            for group, combos in (("axes", self.axes), ("buttons", self.buttons)):
                for name, combo in combos.items():
                    combo.setCurrentIndex(max(0, combo.findData(saved.get(group, {}).get(name, -1))))
            for axis, checkbox in self.invert.items():
                checkbox.setChecked(bool(saved.get("invert", {}).get(axis, False)))
            self.deadzone.setValue(float(saved.get("deadzone", 0.25)))
        except (OSError, ValueError, TypeError, AttributeError):
            self.status.setText("Could not load mapping. Configure the gamepad again.")

    def poll(self):
        if self.device is None:
            return
        try:
            events = self.backend.event.get()
            if any(e.type == self.backend.JOYDEVICEREMOVED and
                   e.instance_id == self.device.get_instance_id() for e in events):
                raise RuntimeError("Gamepad disconnected")
            axes = [self.device.get_axis(i) for i in range(self.device.get_numaxes())]
            buttons = {i for i in range(self.device.get_numbuttons()) if self.device.get_button(i)}
            self.monitor.setText("Axes " + " ".join(f"{i}:{v:+.2f}" for i,v in enumerate(axes))
                                 + "\nButtons " + ", ".join(map(str, sorted(buttons))))
            self.process_input(axes, buttons)
        except (RuntimeError, self.backend.error) as exc:
            self.disarm()
            self.device = None
            self.status.setText(str(exc) + " — scan to reconnect.")

    def process_input(self, raw_axes, buttons):
        pressed = buttons - self.previous_buttons
        self.previous_buttons = set(buttons)
        if not self.enable.isChecked():
            return
        if not self.window().isActiveWindow() or not self.control.isVisible():
            self._mapping_changed()
            self.status.setText("Gamepad paused while CNC Control is inactive or hidden. Return and center sticks to resume.")
            return
        if QApplication.activeModalWidget() or QApplication.activePopupWidget():
            self._mapping_changed()
            self.status.setText("Gamepad paused while a menu or dialog is open.")
            return
        mappings = [combo.currentData() for combo in self.buttons.values()]
        assigned = [v for v in mappings if v is not None and v >= 0]
        axis_ids = [combo.currentData() for combo in self.axes.values()]
        assigned_axes = [v for v in axis_ids if v is not None and v >= 0]
        if len(set(assigned)) != len(assigned) or len(set(assigned_axes)) != len(assigned_axes):
            self._mapping_changed()
            self.status.setText("Duplicate mapping — assign each input once.")
            return
        if self.buttons["Hold to Jog"].currentData() in (None, -1):
            self.status.setText("Gamepad enabled for monitoring. Assign a Hold to Jog button to enable movement.")
            return
        values = {}
        for axis, combo in self.axes.items():
            index = combo.currentData()
            if index is not None and 0 <= index < len(raw_axes):
                value = raw_axes[index] * (-1 if self.invert[axis].isChecked() else 1)
                values[axis] = value if abs(value) > self.deadzone.value() else 0
        if not self.neutral_seen:
            self.neutral_seen = not buttons and not any(values.values())
            self.status.setText("Ready — hold assigned jog button." if self.neutral_seen
                                else "Release buttons and center sticks to arm.")
            return
        actions = {"Hold": self.control.hold, "Cancel Jog": lambda: self.control._realtime(b"\x85"),
                   "Stop / Reset": self.control.stop, "Start": self.control.start,
                   "Resume": self.control.resume, "Home": self.control.home}
        for name, callback in actions.items():
            if self.buttons[name].currentData() in pressed:
                self.disarm()
                callback()
                return
        deadman = self.buttons["Hold to Jog"].currentData()
        if deadman not in buttons or not any(values.values()):
            self._stop_jog()
            return
        axis = max(values, key=lambda a: abs(values[a]))
        if self.jog_direction is not None:
            previous_axis = self.jog_direction[0]
            if abs(values.get(previous_axis, 0)) * 1.15 >= abs(values[axis]):
                axis = previous_axis
        value = values[axis]
        direction = (axis, 1 if value > 0 else -1)
        if self.jogging and direction != self.jog_direction:
            self._stop_jog()
            return
        reason = self.control.gamepad_jog_block_reason()
        if reason:
            self.status.setText("Jog blocked: " + reason)
            return
        now = time.monotonic()
        if max(0.0, self.jog_queued_until - now) + self.JOG_SEGMENT_SECONDS > self.JOG_LOOKAHEAD_SECONDS:
            return
        feed = self.control.z_feed.value() if axis == "Z" else self.control.feed.value()
        feed *= abs(value)
        distance = feed / 60 * self.JOG_SEGMENT_SECONDS * direction[1]
        # Replenish short, acknowledged segments during Jog, with bounded lookahead.
        if self.control.stream_gamepad_jog(axis, distance, feed):
            self.jogging = True
            self.jog_direction = direction
            self.jog_queued_until = max(now, self.jog_queued_until) + self.JOG_SEGMENT_SECONDS
            self.status.setText(f"Jogging {axis}")

    def shutdown(self):
        self.disarm()
        self.timer.stop()
        if self.device is not None:
            self.device.quit()
            self.device = None
