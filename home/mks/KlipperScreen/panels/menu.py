import logging

import gi

import json


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from jinja2 import Environment, Template

from ks_includes.screen_panel import ScreenPanel



def create_panel(*args):
    return MenuPanel(*args)


class MenuPanel(ScreenPanel):
    i = 0
    j2_data = None

    def __init__(self, screen, title):
        super().__init__(screen, title)
        self.items = None
        self._cur_panels = screen._cur_panels
        self.grid = self._gtk.HomogeneousGrid()

    def initialize(self, items):
        self.items = items
        self.create_menu_items()
        scroll = self._gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.grid)
        self.content.add(scroll)

    def activate(self):
        if self._screen.vertical_mode:
            self.arrangeMenuItems(self.items, 3)
        else:
            self.arrangeMenuItems(self.items, 4)

    def arrangeMenuItems(self, items, columns, expand_last=False):
        for child in self.grid.get_children():
            self.grid.remove(child)
        #judge the state of panel
        self._cur_panels = self._screen._cur_panels
        logging.info(self._cur_panels)
        cipher = False
        if self._cur_panels:
            if self._cur_panels[0] == "splash_screen":
                cipher = True
            else:
                cipher = False

        length = len(items)
        logging.info("How many items:" + str(length) + "\n");
        i = 0
        #judge whether to arrange first line of hided widget
        if cipher:
            bt0  = self._gtk.Button()
            bt1  = self._gtk.Button()
            bt2  = self._gtk.Button()
            bt0.hide()
            bt1.hide()
            bt2.hide()
            if self._screen.vertical_mode and length <= 7:
                self.grid.attach(bt0, 0, 0, 1, 1)
                self.grid.attach(bt1, 1, 0, 1, 1)
                self.grid.attach(bt2, 2, 0, 1, 1)
        
        for item in items:
            key = list(item)[0]
            if not self.evaluate_enable(item[key]['enable']):
                logging.debug(f"X > {key}")
                continue

            if columns == 4:
                if length <= 4:
                    # Arrange 2 x 2
                    columns = 2
                elif 4 < length <= 6:
                    # Arrange 3 x 2
                    columns = 3

            col = i % columns
            if cipher:
                row = int(i / columns)+1
            else:
                row = int(i / columns)

            if key == "print":
                width = 3
                height = 1
            else:
                width = height = 1
            logging.info("col:" + str(col) + ", row:" + str(row) + ", width:" + str(width) +", height:" + str(height))
            self.grid.attach(self.labels[key], col, row, width, height)
            i += 1
        #hided widget for ui arrange
        bt3  = self._gtk.Button()
        bt4  = self._gtk.Button()
        bt5  = self._gtk.Button()
        bt3.hide()
        bt4.hide()
        bt5.hide()
        if self._screen.vertical_mode and length <= 7:
            self.grid.attach(bt3, 0, 2, 1, 1)
            self.grid.attach(bt4, 1, 2, 1, 1)
            self.grid.attach(bt5, 2, 2, 1, 1)
        

        return self.grid

    def create_menu_items(self):
        for i in range(len(self.items)):
            key = list(self.items[i])[0]
            item = self.items[i][key]

            env = Environment(extensions=["jinja2.ext.i18n"], autoescape=True)
            env.install_gettext_translations(self._config.get_lang())

            printer = self._printer.get_printer_status_data()

            name = env.from_string(item['name']).render(printer)
            icon = env.from_string(item['icon']).render(printer) if item['icon'] else None
            style = env.from_string(item['style']).render(printer) if item['style'] else None

            b = self._gtk.Button(icon, name, (style if style else f"color{(i % 4) + 1}"))

            if item['panel'] is not None:
                panel = env.from_string(item['panel']).render(printer)
                b.connect("clicked", self.menu_item_clicked, panel, item)
            elif item['method'] is not None:
                params = {}

                if item['params'] is not False:
                    try:
                        p = env.from_string(item['params']).render(printer)
                        params = json.loads(p)
                    except Exception as e:
                        logging.exception(f"Unable to parse parameters for [{name}]:\n{e}")
                        params = {}

                if item['confirm'] is not None:
                    b.connect("clicked", self._screen._confirm_send_action, item['confirm'], item['method'], params)
                else:
                    b.connect("clicked", self._screen._send_action, item['method'], params)
            else:
                b.connect("clicked", self._screen._go_to_submenu, key)
            self.labels[key] = b

    def evaluate_enable(self, enable):
        if enable == "{{ moonraker_connected }}":
            logging.info(f"moonraker connected {self._screen._ws.connected}")
            return self._screen._ws.connected
        elif enable == "{{ camera_configured }}":
            return self.ks_printer_cfg and self.ks_printer_cfg.get("camera_url", None) is not None
        self.j2_data = self._printer.get_printer_status_data()
        try:
            j2_temp = Template(enable, autoescape=True)
            result = j2_temp.render(self.j2_data)
            return result == 'True'
        except Exception as e:
            logging.debug(f"Error evaluating enable statement: {enable}\n{e}")
            return False
