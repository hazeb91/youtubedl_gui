# -*- coding: utf-8 -*-

import threading

from gi.repository import Gtk, GLib, Pango


class ProgressBar(Gtk.ProgressBar):

    def __init__(self, **kwargs):
        super(ProgressBar, self).__init__(**kwargs)


class ImageButton(Gtk.Button):

    def __init__(self, icon_name, size):
        super(ImageButton, self).__init__()

        self.set_relief(Gtk.ReliefStyle.NONE)
        self.set_image(Gtk.Image.new_from_icon_name(icon_name, size))


class ControlButtons(Gtk.Box):

    def __init__(self, **kwargs):
        super(ControlButtons, self).__init__(**kwargs)

        self.cancel_button = ImageButton(Gtk.STOCK_CLOSE, Gtk.IconSize.BUTTON)
        self.restart_button = ImageButton(
            Gtk.STOCK_REFRESH, Gtk.IconSize.BUTTON)
        self.delete_button = ImageButton(Gtk.STOCK_DELETE, Gtk.IconSize.BUTTON)

        self.pack_start(self.cancel_button, False, False, 0)
        self.pack_start(self.restart_button, False, False, 0)
        self.pack_start(self.delete_button, False, False, 0)

    def show_only(self, button):
        for btn in self.get_children():
            if btn is not button:
                btn.hide()
        button.show()

    def hide_only(self, button):
        for btn in self.get_children():
            if btn is not button:
                btn.show()
        button.hide()


class DownloadItemRow(Gtk.ListBoxRow):

    def __init__(self, download_obj):
        super(DownloadItemRow, self).__init__()

        self.download_obj = download_obj

        self.filename_label = Gtk.Label()
        self.filename_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        self.filename_label.set_line_wrap(True)
        self.filename_label.set_max_width_chars(35)
        self.percentage_label = Gtk.Label()
        self.size_label = Gtk.Label()
        self.speed_label = Gtk.Label()
        self.eta_label = Gtk.Label()
        self.progress_bar = ProgressBar()

        self.ctrl_btns = ControlButtons(orientation=Gtk.Orientation.HORIZONTAL)
        self.ctrl_btns.cancel_button.connect(
            "clicked", self._on_cancel_clicked)
        self.ctrl_btns.restart_button.connect(
            "clicked", self._on_restart_clicked)
        self.ctrl_btns.delete_button.connect(
            "clicked", self._on_delete_clicked)

        hbox_info = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        hbox_info.pack_start(self.percentage_label, True, True, 0)
        hbox_info.pack_start(self.size_label, True, True, 0)
        hbox_info.pack_start(self.speed_label, True, True, 5)
        hbox_info.pack_start(self.eta_label, True, True, 0)

        vbox_content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vbox_content.pack_start(self.filename_label, False, False, 0)
        vbox_content.pack_start(self.progress_bar, False, False, 0)
        vbox_content.pack_start(hbox_info, False, False, 0)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        hbox.pack_start(vbox_content, True, True, 0)
        hbox.pack_start(self.ctrl_btns, False, False, 0)

        self.add(hbox)

    def update(self):
        t_download_obj = threading.Thread(target=self.download_obj.run)
        t_download_obj.setDaemon(True)
        t_download_obj.start()

        self.ctrl_btns.show_only(self.ctrl_btns.cancel_button)

        self.g_timeout = GLib.timeout_add(500, self._on_update)

    def _on_update(self):
        self.filename_label.set_text(self.download_obj.video_info_obj.filename)
        self.percentage_label.set_text(self.download_obj.perc)
        self.size_label.set_text(self.download_obj.size)
        self.speed_label.set_text(self.download_obj.speed)
        self.eta_label.set_text(self.download_obj.eta)

        if self.download_obj.is_pause:
            self.progress_bar.set_fraction(self.download_obj.fraction)
            return True

        if not self.download_obj.progress and self.download_obj.fraction < 1:
            self.progress_bar.pulse()
        else:
            self.progress_bar.set_fraction(self.download_obj.fraction)

        if self.download_obj.fraction == 1 and not self.download_obj.t_ydl_call.isAlive():
            self._clear_labels()
            self.ctrl_btns.show_only(self.ctrl_btns.delete_button)
            return False

        return True

    def _clear_labels(self):
        self.percentage_label.set_text(" ")
        self.size_label.set_text(" ")
        self.speed_label.set_text(" ")
        self.eta_label.set_text(" ")

    def _on_cancel_clicked(self, button):
        self.ctrl_btns.hide_only(self.ctrl_btns.cancel_button)
        self.download_obj.pause()

    def _on_restart_clicked(self, button):
        self.ctrl_btns.show_only(self.ctrl_btns.cancel_button)
        self.download_obj.play()

    def _on_delete_clicked(self, button):
        listbox_parent = self.get_parent()
        listbox_parent.remove(self)
        GLib.source_remove(self.g_timeout)
        self.download_obj.kill()
        self.destroy()


class DownloadsListBox(Gtk.ListBox):

    def __init__(self):
        super(DownloadsListBox, self).__init__()

        self.connect("add", self._on_add)
        self.connect("remove", self._on_remove)

        self.empty_label_row = Gtk.ListBoxRow()
        self.empty_label_row.set_selectable(False)

        empty_label = Gtk.Label()
        empty_label.set_markup(
            "<span color=\"#CCCCCC\" size=\"xx-large\"><b>Vuoto</b></span>")
        self.empty_label_row.add(empty_label)

        self.add(self.empty_label_row)

    def _on_add(self, container, object):
        children = container.get_children()
        if len(children) > 1:
            self.empty_label_row.hide()

        object.show_all()

    def _on_remove(self, container, object):
        children = container.get_children()
        if len(children) == 1:
            self.empty_label_row.show_all()


class Downloads(Gtk.Bin):

    def __init__(self):
        super(Downloads, self).__init__()

        self.set_border_width(5)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        scrolled.add(vbox)

        self.list_box = DownloadsListBox()

        vbox.pack_start(self.list_box, True, True, 0)

    def add_download_item(self, download_obj):
        item = DownloadItemRow(download_obj)
        self.list_box.add(item)
        item.update()
