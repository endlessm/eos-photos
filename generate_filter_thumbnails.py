#!/usr/bin/env python
from src.photos_model import PhotosModel

if __name__ == '__main__':
    name = "Filters_Example-Picture_01"
    model = PhotosModel(textures_path="images/textures/",
                        curves_path="data/curves/",
                        borders_path="images/borders/",
                        displayable=False)

    model.open("images/" + name + ".jpg")
    filter_no = 0
    for f in model.get_filter_names():
        model.set_filter(f)
        filename = "images/filter_thumbnails/filter_" + str(filter_no) + ".jpg"
        model.save(filename)
        print filename
        filter_no += 1

    model.open("images/" + name + ".jpg")
    border_no = 0
    for b in model.get_border_names():
        model.set_border(b)
        filename = "images/border_thumbnails/border_" + str(border_no) + ".jpg"
        model.save(filename)
        print filename
        border_no += 1

    model.open("images/" + name + ".jpg")
    distort_no = 0
    for d in model.get_distortion_names():
        model.set_distortion(d)
        filename = "images/distortion_thumbnails/distort_" + str(distort_no) + ".jpg"
        model.save(filename)
        print filename
        distort_no += 1

    model.open("images/" + name + ".jpg")
    distort_no = 0
    for d in model.get_blur_names():
        model.set_blur(d)
        filename = "images/blur_thumbnails/blur_" + str(distort_no) + ".jpg"
        model.save(filename)
        print filename
        distort_no += 1
