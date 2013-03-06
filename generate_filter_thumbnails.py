#!/usr/bin/env python
from src.photos_model import PhotosModel

if __name__ == '__main__':
    name = "Filters_Example-Picture_01"
    model = PhotosModel(textures_path="images/textures/", curves_path="data/curves/")

    model.open("images/" + name + ".jpg")

    filters = model.get_filter_names()

    filter_no = 0
    for f in filters:
        model.apply_filter(f)
        filename = "images/filter_thumbnails/filter_" + str(filter_no) + ".jpg"
        model.save(filename)
        print filename
        filter_no+=1
