from src.photos_model import PhotosModel

if __name__ == '__main__':
    name = "Filters_Example-Picture_01"
    model = PhotosModel(textures_path="images/textures/", curves_path="data/curves/")

    model.open("images/" + name + ".jpg")

    filters = model.get_filter_names()

    for f in filters:
        model.apply_filter(f)
        filename = "images/filter_thumbnails/" + "filter_" + f + ".jpg"
        print filename
        model.save(filename)
