# -*- coding: utf-8 -*-

import os.path

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tab_home import Home
from tab_downloads import Downloads
from tab_options import Options

icons = Gtk.IconTheme()
icons.add_resource_path(os.path.join(os.path.dirname(__file__), "data", "icons", "ydl-gui"))
icons.rescan_if_needed()


class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self)

        self.set_title("YDL Gui")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_size_request(400, 400)
        self.connect("delete-event", Gtk.main_quit)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(vbox)

        home_icon = Gtk.Image.new_from_icon_name(
            Gtk.STOCK_HOME, Gtk.IconSize.MENU)
        download_icon = Gtk.Image.new_from_icon_name(
            Gtk.STOCK_GO_DOWN, Gtk.IconSize.MENU)
        option_icon = Gtk.Image.new_from_icon_name(
            Gtk.STOCK_PREFERENCES, Gtk.IconSize.MENU)

        notebook = Gtk.Notebook()
        notebook.set_margin_top(10)

        self.home_tab = Home()
        self.downloads_tab = Downloads()
        self.options_tab = Options()

        notebook.append_page(self.home_tab, home_icon)
        notebook.append_page(self.downloads_tab, download_icon)
        notebook.append_page(self.options_tab, option_icon)

        vbox.pack_start(notebook, True, True, 0)


if __name__ == "__main__":
    win = MainWindow()
    win.show_all()
    Gtk.main()
