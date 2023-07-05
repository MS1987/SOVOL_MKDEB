import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
    return LEDPanel(*args)


class LEDPanel(ScreenPanel):
    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.led_speed = {}
        self.devices = {}
        # Create a grid for all devices
        self.labels['devices'] = Gtk.Grid()
        self.labels['devices'].set_valign(Gtk.Align.CENTER)
        self.scale = None

        self.add_led()

        scroll = self._gtk.ScrolledWindow()
        scroll.add(self.labels['devices'])

        self.content.add(scroll)

    def process_update(self, action, data):
        if action != "notify_status_update":
            return

        for led in self.devices:
            if led in data and "speed" in data[led]:
                self.update_led_speed(None, led, self._printer.get_led_speed(led))

    def update_led_speed(self, widget, led, speed):
        if led not in self.devices:
            return

        if self.devices[led]['changeable'] is True:
            if self.devices[led]['scale'].has_grab():
                return
            self.devices[led]["speed"] = round(float(speed) * 100)
            self.devices[led]['scale'].disconnect_by_func(self.set_led_speed)
            self.devices[led]['scale'].set_value(self.devices[led]["speed"])
            self.devices[led]['scale'].connect("button-release-event", self.set_led_speed, led)
        else:
            self.devices[led]["speed"] = float(speed)
            self.devices[led]['scale'].set_fraction(self.devices[led]["speed"])
        if widget is not None:
            self.set_led_speed(None, None, led)

    def add_led(self):
        name = Gtk.Label()
        name.set_markup(f"\n<big><b>Extruder LED</b></big>\n")
        name.set_hexpand(True)
        name.set_vexpand(True)
        name.set_halign(Gtk.Align.START)
        name.set_valign(Gtk.Align.CENTER)
        name.set_line_wrap(True)
        name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        led_col = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        led_off = self._gtk.Button("led_off", _("led off"), "color1")
        led_off.set_hexpand(False)
        led_off.connect("clicked", self.set_led_speed, "SET_PIN PIN=my_led VALUE=0")
        led_on = self._gtk.Button("led_on", _("led on"), "color2")
        led_on.set_hexpand(False)
        led_on.connect("clicked", self.set_led_speed, "SET_PIN PIN=my_led VALUE=1")

        self.labels['devices'].insert_row(0)
        self.labels['devices'].attach(led_col, 0, 0, 1, 1)
        self.labels['devices'].show_all()

        self.scale = Gtk.Scale.new_with_range(orientation=Gtk.Orientation.HORIZONTAL, min=0, max=100, step=1)
        self.scale.set_value(self._printer.get_led_power())
        self.scale.set_digits(0)
        self.scale.set_hexpand(True)
        self.scale.set_has_origin(True)
        self.scale.get_style_context().add_class("led_slider")
        self.scale.connect("button-release-event", self.set_led_speed)

        led_col.add(led_off)
        led_col.add(self.scale)
        led_col.add(led_on)

        led_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        led_row.add(name)
        led_row.add(led_col)

        self.labels['devices'].insert_row(0)
        self.labels['devices'].attach(led_row, 0, 0, 1, 1)
        self.labels['devices'].show_all()

    def set_led_speed(self, widget, command):
        print(f"command: {command}, {self.scale.get_value()}")
        if type(command) == str:
            self._screen._ws.klippy.gcode_script(command)
            if command.endswith("0"):
                self._printer.set_led_power(0)
                self.scale.set_value(0)
            elif command.endswith("1"):
                self._printer.set_led_power(100)
                self.scale.set_value(100)
        else:
            self._screen._ws.klippy.gcode_script(f"SET_PIN PIN=my_led VALUE={float(self.scale.get_value()) / 100}")
            self._printer.set_led_power(self.scale.get_value())
