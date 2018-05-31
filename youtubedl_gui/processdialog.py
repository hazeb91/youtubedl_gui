# -*- coding: utf-8 -*-

import threading

from gi.repository import Gtk, GLib


class ProcessDialog(Gtk.Dialog):

    def __init__(self, parent, label, process):
        Gtk.Dialog.__init__(self, label, parent)

        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_resizable(False)
        self.set_decorated(True)
        self.set_border_width(10)

        box = self.get_content_area()

        self.spinner = Gtk.Spinner()
        self.status = Gtk.Label()

        vbox_contents = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        vbox_contents.pack_start(self.spinner, True, True, 0)
        vbox_contents.pack_start(self.status, True, True, 0)

        box.add(vbox_contents)
        box.show_all()

        self.process = process
        self.update()

    def update(self):
        self._t_proc = threading.Thread(target=self.process.run)
        self._t_proc.setDaemon(True)
        self._t_proc.start()

        self.spinner.start()

        self.g_timeout = GLib.timeout_add(250, self._on_update)

    def _on_update(self):
        self.status.set_text(self.process.status)

        if self.process.error:
            self.spinner.stop()
            self.set_title("Errore")
            self.add_button(Gtk.STOCK_CLOSE, Gtk.ResponseType.CANCEL)
            return False

        if self._t_proc.isAlive() is False:
            self.response(Gtk.ResponseType.OK)
            self.spinner.stop()
            return False

        return True


class WaitDialog(ProcessDialog):

    def __init__(self, parent, process):
        super(WaitDialog, self).__init__(
            parent=parent, label="Attendere...", process=process)
