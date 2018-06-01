# -*- coding: utf-8 -*-

from gi.repository import Gtk


class BaseComboBox(Gtk.ComboBox):

    def __init__(self, **kwargs):
        super(BaseComboBox, self).__init__(**kwargs)

    def get_selected(self):
        tree_iter = self.get_active_iter()
        if tree_iter is not None:
            combobox_model = self.get_model()
            return combobox_model[tree_iter][0]


class BaseFormatCombo(Gtk.Box):

    format_store = Gtk.ListStore()

    def __init__(self, label, **kwargs):
        super(BaseFormatCombo, self).__init__()

        format_label = Gtk.Label(label)
        self.format_combo = BaseComboBox()
        self.format_combo.set_model(self.format_store)
        self.format_combo.connect("changed", self._on_combo_changed)

        self.pack_start(format_label, False, False, 0)
        self.pack_end(self.format_combo, False, False, 0)

    def _on_combo_changed(self, combobox):
        print(combobox.get_selected())


class QualityCombo(BaseFormatCombo):

    format_store = Gtk.ListStore(int, str)

    def __init__(self):
        super(QualityCombo, self).__init__(
            label="Qualità",
            orientation=Gtk.Orientation.HORIZONTAL
        )

        renderer_text = Gtk.CellRendererText()
        self.format_combo.pack_start(renderer_text, True)
        self.format_combo.add_attribute(renderer_text, "text", 1)


class RecodeVideoFormatCombo(BaseFormatCombo):

    format_store = Gtk.ListStore(int, str)
    format_store.append([0, "MP4"])
    format_store.append([1, "FLV"])
    format_store.append([2, "OGG"])
    format_store.append([3, "WEBM"])
    format_store.append([4, "MKV"])
    format_store.append([5, "AVI"])

    def __init__(self):
        super(RecodeVideoFormatCombo, self).__init__(
            label="Ricodifica video",
            orientation=Gtk.Orientation.HORIZONTAL
        )

        renderer_text = Gtk.CellRendererText()
        self.format_combo.pack_start(renderer_text, True)
        self.format_combo.add_attribute(renderer_text, "text", 1)


class RecodeAudioFormatCombo(BaseFormatCombo):

    format_store = Gtk.ListStore(int, str)
    format_store.append([0, "BEST"])
    format_store.append([1, "AAC"])
    format_store.append([2, "FLAC"])
    format_store.append([3, "MP3"])
    format_store.append([4, "M4A"])
    format_store.append([5, "OPUS"])
    format_store.append([6, "VORBIS"])
    format_store.append([7, "WAV"])

    def __init__(self):
        super(RecodeAudioFormatCombo, self).__init__(
            label="Ricodifica audio",
            orientation=Gtk.Orientation.HORIZONTAL
        )

        renderer_text = Gtk.CellRendererText()
        self.format_combo.pack_start(renderer_text, True)
        self.format_combo.add_attribute(renderer_text, "text", 1)
