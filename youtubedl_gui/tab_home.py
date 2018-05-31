# -*- coding: utf-8 -*-

import os.path
import threading
import copy

from gi.repository import Gtk, Gdk, GLib, Pango

from utils import is_valid_url, seconds_to_human
from process import GetVideoInfo
from process import DownloadVideo
from processdialog import WaitDialog
from formatscombo import QualityCombo

ICONS_PATH = os.path.join(os.path.dirname(__file__), "data", "icons")
MUSIC_ICON = os.path.join(ICONS_PATH, "music.png")
VIDEO_ICON = os.path.join(ICONS_PATH, "video.png")


class URLEntry(Gtk.Entry):

    def __init__(self):
        super(URLEntry, self).__init__()

        self.STATUS = {
            None: self.set_status_icon_none,
            False: self.set_status_icon_invalid,
            True: self.set_status_icon_valid
        }

        self.status = None

        self.set_icon_sensitive(Gtk.EntryIconPosition.PRIMARY, False)
        self.set_icon_sensitive(Gtk.EntryIconPosition.SECONDARY, True)
        self.connect_after("backspace", self._on_backspace)
        self.connect_after("insert-text", self._on_insert_text)
        self.set_status_icon_default()

        GLib.timeout_add(500, self._update)

    def _update(self):
        self.STATUS.get(self.status, None).__call__()
        self._last_status = self.status
        return True

    def _check_entry_url(self, text):
        if text and is_valid_url(text):
            self.status = True
        else:
            self.status = False

    def _on_insert_text(self, entry, text, length, position):
        text = entry.get_text()
        self._check_entry_url(text)

    def _on_backspace(self, entry):
        text = entry.get_text()
        if len(text) == 0:
            self.status = None
        else:
            self._check_entry_url(text)

    def set_status_icon_default(self):
        self.set_icon_from_icon_name(
            Gtk.EntryIconPosition.SECONDARY, Gtk.STOCK_FIND)
        self.set_icon_tooltip_text(
            Gtk.EntryIconPosition.SECONDARY, "Vai")

    def set_status_icon_valid(self):
        self.set_icon_from_icon_name(
            Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_YES)
        self.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY, "URL valido")

    def set_status_icon_invalid(self):
        self.set_icon_from_icon_name(
            Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_NO)
        self.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY, "URL non valido")

    def set_status_icon_none(self):
        self.set_icon_from_icon_name(
            Gtk.EntryIconPosition.PRIMARY, Gtk.STOCK_REFRESH)
        self.set_icon_tooltip_text(
            Gtk.EntryIconPosition.PRIMARY, "")


class URLField(Gtk.Bin):

    def __init__(self):
        super(URLField, self).__init__()

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=60)
        self.add(hbox)

        url_label = Gtk.Label("URL:", xalign=0)
        self.url_entry = URLEntry()

        hbox.pack_start(url_label, False, False, 0)
        hbox.pack_start(self.url_entry, True, True, 0)


class InfoFrame(Gtk.Frame):

    def __init__(self):
        super(InfoFrame, self).__init__()

        self.set_shadow_type(Gtk.ShadowType.NONE)
        self.set_margin_top(5)
        # self.set_label("Info")
        # self.set_label_align(0.5, 0.5)

        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        self.add(grid)

        # vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        # self.add(vbox)

        like_icon = Gtk.Image.new_from_file(
            os.path.join(ICONS_PATH, "like.png"))
        dislike_icon = Gtk.Image.new_from_file(
            os.path.join(ICONS_PATH, "dislike.png"))
        view_icon = Gtk.Image.new_from_file(
            os.path.join(ICONS_PATH, "view.png"))

        self.like_value = Gtk.Label()
        self.dislike_value = Gtk.Label()
        self.view_value = Gtk.Label()

        title_label = Gtk.Label("Titolo:", yalign=0, xalign=0)
        duration_label = Gtk.Label("Durata:", yalign=0, xalign=0)
        description_label = Gtk.Label("Descrizione:", yalign=0, xalign=0)

        self.title_value = Gtk.Label(xalign=0)
        self.title_value.set_line_wrap(True)
        self.title_value.set_selectable(True)

        self.duration_value = Gtk.Label(xalign=0)
        self.duration_value.set_selectable(True)

        self.description_value = Gtk.Label(xalign=0)
        self.description_value.set_line_wrap(True)
        self.description_value.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.description_value.set_selectable(True)

        description_scroll = Gtk.ScrolledWindow()
        description_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        description_scroll.add(self.description_value)

        hbox_counters = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        hbox_counters.pack_start(like_icon, False, False, 0)
        hbox_counters.pack_start(self.like_value, False, False, 0)
        hbox_counters.pack_start(dislike_icon, False, False, 0)
        hbox_counters.pack_start(self.dislike_value, False, False, 0)
        hbox_counters.pack_start(view_icon, False, False, 0)
        hbox_counters.pack_start(self.view_value, False, False, 0)

        grid.attach(hbox_counters, 1, 0, 2, 1)

        grid.attach(title_label, 0, 1, 1, 1)
        grid.attach_next_to(self.title_value, title_label,
                            Gtk.PositionType.RIGHT, 1, 1)

        grid.attach(duration_label, 0, 2, 1, 1)
        grid.attach_next_to(self.duration_value, duration_label,
                            Gtk.PositionType.RIGHT, 1, 1)

        grid.attach(description_label, 0, 3, 1, 1)
        grid.attach_next_to(description_scroll, description_label,
                            Gtk.PositionType.RIGHT, 2, 10)


class StartButtons(Gtk.ButtonBox):

    def __init__(self, **kwargs):
        super(StartButtons, self).__init__(**kwargs)

        self.set_layout(Gtk.ButtonBoxStyle.EXPAND)

        music_icon = Gtk.Image.new_from_file(MUSIC_ICON)
        video_icon = Gtk.Image.new_from_file(VIDEO_ICON)

        self.music_button = Gtk.Button()
        self.music_button.set_image(music_icon)
        self.music_button.set_tooltip_text("Scarica Audio")

        self.video_button = Gtk.Button()
        self.video_button.set_image(video_icon)
        self.video_button.set_tooltip_text("Scarica Video")

        self.pack_start(self.music_button, True, True, 0)
        self.pack_start(self.video_button, True, True, 0)


class CaptureClipboardCheck(Gtk.CheckButton):

    def __init__(self):
        super(CaptureClipboardCheck, self).__init__()

        self.set_label("Cattura clipboard")
        self.set_active(True)


class Home(Gtk.Bin):

    def __init__(self):
        super(Home, self).__init__()

        self.set_border_width(5)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.connect("owner-change", self._on_clipboard_owner_change)

        self.capture_check_btn = CaptureClipboardCheck()

        self.url_field = URLField()
        self.url_field.url_entry.connect_after("activate", self._on_entry_activate)
        self.url_field.url_entry.connect_after("icon-release", self._on_entry_activate)
        self.info_frame = InfoFrame()
        self.quality_combo = QualityCombo()

        self.start_buttons = StartButtons(orientation=Gtk.Orientation.HORIZONTAL)
        self.start_buttons.set_sensitive(False)
        self.start_buttons.music_button.connect("clicked", self._on_start, "music")
        self.start_buttons.video_button.connect("clicked", self._on_start, "video")

        vbox.pack_start(self.capture_check_btn, False, False, 0)
        vbox.pack_start(self.quality_combo, False, False, 10)
        vbox.pack_start(self.url_field, False, False, 0)
        vbox.pack_start(self.info_frame, False, False, 0)
        vbox.pack_end(self.start_buttons, False, False, 0)

        self.add(vbox)

    def _on_clipboard_owner_change(self, clipboard, event):
        text = clipboard.wait_for_text()
        if text and self.capture_check_btn.get_active():
            self.url_field.url_entry.delete_text(0, -1)
            self.url_field.url_entry.set_text(text)
            self._on_entry_activate(self.url_field.url_entry)

    def _on_entry_activate(self, entry, *args):
        self.start_buttons.set_sensitive(False)
        GLib.timeout_add(250, self._update_info, entry.get_text())

    def _update_info(self, url):
        if not url.startswith("http"):
            return
        t_video_info = GetVideoInfo(url)

        wait_dlg = WaitDialog(parent=self.get_toplevel(), process=t_video_info)
        response = wait_dlg.run()
        wait_dlg.destroy()

        if response == Gtk.ResponseType.OK:
            self.video_info_obj = t_video_info.info_obj

            self.info_frame.like_value.set_text(
                "{:,}".format(self.video_info_obj.like_count))
            self.info_frame.dislike_value.set_text(
                "{:,}".format(self.video_info_obj.dislike_count))
            self.info_frame.view_value.set_text(
                "{:,}".format(self.video_info_obj.view_count))

            self.info_frame.title_value.set_text(
                self.video_info_obj.title)
            self.info_frame.duration_value.set_text(
                seconds_to_human(self.video_info_obj.duration))
            self.info_frame.description_value.set_text(
                self.video_info_obj.description)

            formats_list = list(self.video_info_obj.formats)
            formats_list.reverse()  # best formats are at the end of list, but we want as firsts
            # self.quality_combo.format_store.append(["Auto"])
            for format in formats_list:
                self.quality_combo.format_store.append([format["format"]])
            print(*formats_list[0].items(), sep="\n")
            self.quality_combo.format_combo.set_active(0)

            self.start_buttons.set_sensitive(True)
        else:
            self.start_buttons.set_sensitive(False)

    def _on_start(self, button, format_type):
        download_video = DownloadVideo(
            parent_window=self.get_toplevel(),
            video_info_obj=copy.deepcopy(self.video_info_obj),
            format_chosen=self.quality_combo.format_combo.get_selected()
        )

        self.get_toplevel().downloads_tab.add_download_item(download_obj=download_video)
