from photos_model import PhotosModel

if __name__ == '__main__':
    name = "Filters_Example-Picture_01"
    model = PhotosModel()

    model.open("../images/" + name + ".jpg")

    filters = model.get_filter_names()

    for f in filters:
        model.apply_filter(f)
        filename = "../images/filter_examples/" + "filter_" + f + ".jpg"
        print filename
        model.save(filename)