# -*- coding: utf-8 -*-

from gi.repository import Gtk


class PostProcessingFrame(Gtk.Frame):

    def __init__(self):
        super(PostProcessingFrame, self).__init__()

        self.set_label("Post Processing")


class Options(Gtk.Bin):

    def __init__(self):
        super(Options, self).__init__()

        import os.path
        wip_image = Gtk.Image.new_from_file(
            os.path.join(os.path.dirname(__file__), "data", "icons", "work-in-progress.png"))
        self.add(wip_image)

        self.set_border_width(5)
