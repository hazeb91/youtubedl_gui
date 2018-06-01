# -*- coding: utf-8 -*-

import os
import json
import subprocess
import math
from operator import mul
from functools import reduce

import validators


def get_ydl_path():
    youtubedl_bin = "youtube-dl"
    if os.name == "nt":
        youtubedl_bin += ".exe"
    return youtubedl_bin


def is_valid_url(text):
    if validators.url(text) is True:
        return True
    else:
        return False


def seconds_to_human(seconds):
    time_values = [365, 24, 60, 60, 1]
    time_list = []
    for i in range(len(time_values)):
        time_mul = reduce(mul, time_values[i:])
        result = seconds // time_mul
        seconds -= time_mul * result
        if i < 3 and result == 0:
            continue
        str_result = str(result)
        if len(time_list) > 0 and len(str_result) == 1:
            time_list.append("0{res}".format(res=str_result))
        else:
            time_list.append(str_result)
    return ":".join(time_list)


def size_to_human(size):
    units = ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    exp = int(math.log10(size))
    res = exp // 3
    return "{n:.2f}{u}".format(n=(size / math.pow(10, 3*res)), u=units[res])


class CommandCaller(object):

    def __init__(self, command, **flags):
        self.output = None
        self.error = None
        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **flags)

    def run(self):
        self.output, self.error = self.process.communicate()


class VideoInfo(object):

    def __init__(self, json_data):
        self.json_data = json_data
        self.info_dict = json.loads(self.json_data)

        self.url = self.info_dict["webpage_url"]
        self.id = self.info_dict.get("id", "Sconosciuto")
        self.title = self.info_dict["title"]
        self.filename = self.info_dict["_filename"].rpartition(".")[0]
        self.description = self.info_dict.get("description", "Sconosciuto")
        self.like_count = self.info_dict.get("like_count", 0)
        self.dislike_count = self.info_dict.get("dislike_count", 0)
        self.view_count = self.info_dict.get("view_count", 0)
        self.formats = list(self._get_formats())

    def _get_formats(self):
        if "entries" in self.info_dict:  # FIXME: No playlist support
            formats = self.info_dict["entries"][0].get(
                "formats", [self.info_dict])
        else:
            formats = self.info_dict.get("formats", [self.info_dict])
        # reverse: best formats are at the end of the list, but we want as firsts
        for format_ in filter(lambda f: f.get('preference') is None or f['preference'] >= -1000, reversed(formats)):
            desc = []
            desc.append(format_["ext"].upper())
            if "unknown" in format_["format"]:
                desc.append(format_["format"])
            else:
                if format_.get("height", None):
                    desc.append("{0}p".format(format_["height"]))
                if format_["vcodec"] and format_["acodec"] == "none":
                    desc.append("{0}fps".format(format_["fps"]))
                    desc.append("(solo video)")
                elif format_["acodec"] and format_["vcodec"] == "none":
                    desc.append("{0}k".format(format_["abr"]))
                    desc.append("(solo audio)")
                if format_.get("filesize"):
                    desc.append(size_to_human(int(format_.get("filesize"))))
                print(desc)

            format_["format_desc"] = " ".join(desc)

            yield format_

    @property
    def duration(self):
        seconds = self.info_dict.get("duration", 0)
        if isinstance(seconds, int):
            return seconds
        return 0


if __name__ == "__main__":
    j = get_ydl_json("https://www.youtube.com/watch?v=Z-VxGSCfRQ0")
    x = VideoInfo(j)
    for f in x.formats:
        print(f)
