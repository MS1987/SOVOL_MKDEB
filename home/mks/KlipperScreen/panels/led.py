import logging

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Pango

from ks_includes.KlippyGcodes import KlippyGcodes
from ks_includes.screen_panel import ScreenPanel


def create_panel(*args):
	return LedPanel(*args)


class LedPanel(ScreenPanel):
	def __init__(self, screen, title):
		super().__init__(screen, title)
		self.fan_speed = {}
		self.devices = {}
		# Create a grid for all devices
		self.labels['devices'] = Gtk.Grid()
		self.labels['devices'].set_valign(Gtk.Align.CENTER)

		self.add_led()

		scroll = self._gtk.ScrolledWindow()
		scroll.add(self.labels['devices'])

		self.content.add(scroll)

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

		led_off = self._gtk.Button("led-off", _("led off"), "color1")
		led_off.set_hexpand(False)
		led_off.connect("clicked", self.set_led, "SET_PIN PIN=my_led VALUE=0")

		led_on = self._gtk.Button("led-on", _("led on"), "color2")
		led_on.set_hexpand(False)
		led_on.connect("clicked", self.set_led, "SET_PIN PIN=my_led VALUE=1")

		led_col.add(name)
		led_col.add(led_off)
		led_col.add(led_on)

		# led_row = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
		# led_row.add(name)
		# led_row.add(led_col)

		self.labels['devices'].insert_row(0)
		self.labels['devices'].attach(led_col, 0, 0, 1, 1)
		self.labels['devices'].show_all()

	def set_led(self, widget, led_status):
		self._screen._ws.klippy.gcode_script(led_status)
