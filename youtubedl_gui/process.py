# -*- coding: utf-8 -*-

import os
import re
import signal
import threading
from time import sleep

from utils import get_ydl_path, VideoInfo, CommandCaller


class GetVideoInfo(object):

    def __init__(self, url):
        self.url = url
        command = [get_ydl_path(), "--dump-json", "--no-warnings", self.url]
        self.json_data_call = CommandCaller(command=command)
        self.status = "Sto cercando informazioni sul video..."
        self.error = None

    def run(self):
        self.json_data_call.run()
        if not self.json_data_call.error:
            self.info_obj = VideoInfo(
                json_data=self.json_data_call.output.decode("utf-8"))
        else:
            self.error = self.json_data_call.error.decode("utf-8")
            self.status = "Nessun video trovato!"


class DownloadVideo(object):

    def __init__(self, parent_window, video_info_obj, format_chosen):
        self.perc = ""
        self.size = ""
        self.speed = ""
        self.eta = ""
        self.fraction = 0
        self.progress = None
        self.is_pause = False
        self.video_info_obj = video_info_obj
        self.format = video_info_obj.formats[format_chosen]

        basename = self.video_info_obj.info_dict["_filename"].rpartition(".")[0]
        self.video_info_obj.filename = ".".join([basename, self.format["ext"]])

        command = [
            get_ydl_path(),
            "--no-warnings",
            "--no-playlist",
            "--format",
            self.format["format_id"],
            self.video_info_obj.url
        ]
        self.ydl_call = CommandCaller(command=command, universal_newlines=True)

    def pause(self):
        self.ydl_call.process.send_signal(signal.SIGSTOP)
        self.is_pause = True

    def play(self):
        self.ydl_call.process.send_signal(signal.SIGCONT)
        self.is_pause = False

    def kill(self):
        self.ydl_call.process.kill()

    def run(self):
        self.t_ydl_call = threading.Thread(target=self.ydl_call.run)
        self.t_ydl_call.setDaemon(True)
        self.t_ydl_call.start()

        ptn = "^\[.*?\]\s+(\d+\.\d+\%)\s+of\s+(\d+[\w\.]+)\s+at\s+(\d+[\w\S]+)\s+ETA\s+([\d\:]+)"
        while self.t_ydl_call.isAlive():
            line = self.ydl_call.process.stdout.readline()
            print(line)
            self.progress = re.search(ptn, line)
            if self.progress:
                self.perc, self.size, self.speed, self.eta = self.progress.groups()
                self.fraction = float(self.perc[:-1]) / 100
            sleep(0.2)

        if not self.ydl_call.error:
            self.fraction = 1

        print("out", self.ydl_call.output)
        print("err", self.ydl_call.error)
