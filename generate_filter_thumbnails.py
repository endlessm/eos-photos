#!/usr/bin/env python
from gi.repository import GtkClutter

from src.photos_model import PhotosModel
import Image

if __name__ == '__main__':
    GtkClutter.init([])

    name = "Filters_Example-Picture_01"
    model = PhotosModel(textures_path="images/textures/", curves_path="data/curves/", borders_path="images/borders/")
    model.open("images/" + name + ".jpg")

    filters = model.get_filter_names()

    filter_no = 0
    for f in filters:
        model.set_filter(f)
        filename = "images/filter_thumbnails/filter_" + str(filter_no) + ".jpg"
        model.save(filename)
        print filename
        filter_no+=1

    model.set_filter("NORMAL")
    border_no = 0
    for b in model._border_dict.keys():
        model.set_border(b)
        model.save("images/border_thumbnails/" + "border_" + str(border_no) + ".png")
        border_no += 1

    model.set_border("NONE")
    distort_no = 0
    for d in model._distortions_dict.keys():
        model.set_distortion(d)
        model.save("images/distortion_thumbnails/" + "distort_" + str(distort_no) + ".jpg")
        distort_no += 1


