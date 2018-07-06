import collections

from PIL import Image
from PIL import ImageFilter

from . import util
from .resource_prefixes import *
from .image_processing import image_tools as ImageTools

class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """
    def __init__(self, displayable=True):
        super(PhotosModel, self).__init__()
        self._source_image = None
        self._cropped_image = None
        self._filtered_image = None
        self._blurred_image = None
        self._distorted_image = None
        self._adjusted_image = None
        self._rotated_image = None
        self._options_stored = False

        self._displayable = displayable
        if displayable:
            # Only import this if displayable; we don't want to do any graphical
            # operations in generate_filter_thumbnails.py
            from .photos_image_widget import PhotosImageWidget
            self._image_widget = PhotosImageWidget()
        else:
            self._image_widget = None

        self._is_saved = True
        self._build_filter_dict()
        self._build_border_dict()
        self._build_blur_dict()
        self._build_distortions_dict()

    def rotate_orientation_clockwise(self):
        self._orientation = (self._orientation + 90) % 360

    def rotate_orientation_counter_clockwise(self):
        self._orientation = (self._orientation - 90) % 360

    def rotate_image_by_orientation(self, img, orientation):
        c_rot = lambda im: ImageTools.rotate_clockwise(im)
        cc_rot = lambda im: ImageTools.rotate_counter_clockwise(im)

        if orientation == 0:
            f = lambda im: im
        if orientation == 90 or orientation == -270:
            f = c_rot
        if orientation == 180 or orientation == -180:
            f = lambda im: c_rot(c_rot(im))
        if orientation == 270 or orientation == -90:
            f = cc_rot

        return f(img)

    def _build_blur_dict(self):
        self._blur_dict = collections.OrderedDict([
            (_("None"), lambda im: im),
            (_("Tilt Shift"), lambda im: ImageTools.tilt_shift_blur(im)),
            (_("Depth of Field"), lambda im: ImageTools.depth_of_field_blur(im))
        ])

    def _build_filter_dict(self):
        self._filter_dict = collections.OrderedDict([
            (_("None"), lambda im: im),
            (_("Grayscale"), lambda im: ImageTools.grayscale(im)),
            (_("Country"), lambda im: ImageTools.country(im)),
            (_("Retro"), lambda im: ImageTools.grunge(im)),
            (_("Old Photo"), lambda im: ImageTools.old_photo(im)),
            (_("Colorful"), lambda im: ImageTools.colorful(im)),
            # (_("BUMPY"), lambda im: ImageTools.bumpy(im)),
            (_("Lomo"), lambda im: ImageTools.lumo(im)),
            # (_("SMOOTH"), lambda im: im.filter(ImageFilter.SMOOTH_MORE)),
            # (_("SHARPEN"), lambda im: im.filter(ImageFilter.SHARPEN)),
            (_("Foggy Blue"), lambda im: ImageTools.foggy_blue(im)),
            (_("Paper"), lambda im: ImageTools.paper(im)),
            (_("Trains"), lambda im: ImageTools.trains(im)),
            (_("Desert"), lambda im: ImageTools.desert(im)),
            (_("Posterize"), lambda im: ImageTools.posterize(im)),
            # (_("INVERT"), lambda im: ImageTools.invert(im)),
            # (_("EMBOSS"), lambda im: im.filter(ImageFilter.EMBOSS)),
            (_("Edges"), lambda im: im.filter(ImageFilter.FIND_EDGES)),
            # (_("PIXELATE"), lambda im: ImageTools.pixelate(im)),
            # (_("BOXELATE"), lambda im: ImageTools.boxelate(im)),
        ])

    def _build_border_dict(self):
        self._border_dict = collections.OrderedDict([
            (_("None"), None),
            # (_("HORIZONTAL BARS"), "horizontal_bars.png"),
            # (_("SIDE BARS"), "vertical_bars.png"),
            (_("Crayon"), "frame_3x2_crayon.png"),
            (_("Grunge"), "frame_3x2_grunge.png"),
            (_("Spray"), "frame_3x2_spray.png"),
            (_("Brush"), "frame_3x2_brush.png")
        ])

    def _build_distortions_dict(self):
        self._distortions_dict = collections.OrderedDict([
            (_("None"), lambda im: im),
            (_("Fish Eye Light"), lambda im: ImageTools.distortion(im, "FISH EYE LIGHT")),
            (_("Fish Eye Heavy"), lambda im: ImageTools.distortion(im, "FISH EYE HEAVY")),
            (_("Pinch Light"), lambda im: ImageTools.distortion(im, "PINCH LIGHT")),
            (_("Pinch Heavy"), lambda im: ImageTools.distortion(im, "PINCH HEAVY")),
            (_("Swirl"), lambda im: ImageTools.distortion(im, "SWIRL"))
        ])

    # Store options temporarily if nothing has already been stored, then
    # clear all settings (except orientation) to default in preparation for cropping
    def push_options(self):
        if not self._options_stored:
            self._stored_filter = self._filter
            self._stored_distort = self._distort
            self._stored_blur_type = self._blur_type
            self._stored_brightness = self._brightness
            self._stored_contrast = self._contrast
            self._stored_saturation = self._saturation
            self._stored_orientation = self._orientation
            self._stored_border = self._border
            self._stored_last_crop_coordinates = self._last_crop_coordinates
            self._stored_crop_orientation = self._crop_orientation
            self._options_stored = True
            self.clear_options()
            self._orientation = self._stored_orientation
            self._crop_orientation = self._stored_crop_orientation

    # Restore all settings after cropping either performed or cancelled (if
    # any have been stored at all)
    def pop_options(self):
        if self._options_stored:
            self._filter = self._stored_filter 
            self._distort = self._stored_distort 
            self._blur_type = self._stored_blur_type 
            self._brightness = self._stored_brightness 
            self._contrast = self._stored_contrast 
            self._border = self._stored_border
            self._last_crop_coordinates = self._stored_last_crop_coordinates
            self._saturation = self._stored_saturation 
            self._options_stored = False

    def clear_options(self):
        self._filter = self._get_default_filter()
        self._distort = self._get_default_distortion()
        self._blur_type = self._get_default_blur()
        self._orientation = 0
        self._crop_orientation = 0
        self._brightness = 1.0
        self._crop_coordinates = None
        self._contrast = 1.0
        self._saturation = 1.0
        self._last_orientation = 0
        self._last_crop_coordinates = None
        self._last_filter = ""
        self._last_blur_type = ""
        self._last_distort = ""
        self._last_brightness = self._last_contrast = self._last_saturation = -1
        self._border = self._get_default_border()

    def revert_to_original(self):
        if self._displayable:
            self._image_widget.hide_crop_overlay()
            self._image_widget.reset_crop_overlay()
        self.clear_options()
        if self.is_open():
            self._update_base_image()
            self._update_border_image()
            self._is_saved = True

    def _get_default_filter(self):
        return next(iter(self._filter_dict))

    def _get_default_border(self):
        return next(iter(self._border_dict))

    def _get_default_distortion(self):
        return next(iter(self._distortions_dict))

    def _get_default_blur(self):
        return next(iter(self._blur_dict))

    def get_image_widget(self):
        return self._image_widget

    def open(self, filename):
        self._filename = filename
        self._source_image = ImageTools.limit_size(Image.open(filename), (2056, 2056)).convert('RGB')
        self.revert_to_original()

    # format, an image format string will be inferred from filename by default
    # quality, the quality of the image (100% is max) for lossy image formats
    # save_point, whether to consider this a save point (i.e. the user triggered this save)
    def save(self, filename, format=None, quality=95, save_point=False):
        if self.is_open():
            im = self._composite_final_image()
            if format is not None:
                im.save(filename, format, quality=quality)
            else:
                im.save(filename, quality=quality)
            if save_point:
                self._is_saved = True

    def is_open(self):
        return self._source_image is not None

    def is_saved(self):
        return self._is_saved

    def is_modified(self):
        return self._curr_filter is not self.get_defualt_filter_name()

    def get_current_filename(self):
        if not self.is_open():
            return None
        return self._filename

    def get_blur_names(self):
        return list(self._blur_dict.keys())

    def get_blur_names_and_thumbnails(self):
        names_and_thumbs = []
        blur_no = 0
        for name in self.get_blur_names():
            names_and_thumbs.append((name, "blur_" + str(blur_no) + ".jpg"))
            blur_no += 1
        return names_and_thumbs

    def get_filter_names(self):
        return list(self._filter_dict.keys())

    def get_filter_names_and_thumbnails(self):
        names_and_thumbs = []
        filter_no = 0
        for name in self.get_filter_names():
            names_and_thumbs.append((name, "filter_" + str(filter_no) + ".jpg"))
            filter_no += 1
        return names_and_thumbs

    def get_border_names(self):
        return list(self._border_dict.keys())

    def get_border_names_and_thumbnails(self):
        names_and_thumbs = []
        border_no = 0
        for name in self.get_border_names():
            names_and_thumbs.append((name, "border_" + str(border_no) + ".jpg"))
            border_no += 1
        return names_and_thumbs

    def get_distortion_names(self):
        return list(self._distortions_dict.keys())

    def get_distortion_names_and_thumbnails(self):
        names_and_thumbs = []
        distort_no = 0
        for name in self.get_distortion_names():
            names_and_thumbs.append((name, "distort_" + str(distort_no) + ".jpg"))
            distort_no += 1
        return names_and_thumbs

    def get_contrast(self):
        return self._contrast

    def set_contrast(self, value):
        self._contrast = value
        self._update_base_image()

    def get_brightness(self):
        return self._brightness

    def do_rotate(self):
        self.rotate_orientation_clockwise()
        self._image_widget.rotate_crop_overlay()

        self._update_base_image()
        self._update_border_image()
        
    def is_crop_active(self):
        return self._image_widget.crop_overlay_visible

    def do_crop_activate(self):
        # Crop overlay about to become visible, so resize it to the last crop selection.
        # General strategy here is to set the cropbox's dimensions to the (potentially rotated)
        # _last_crop_coordinates, and then perform the crop overlay's "rotate" operation as
        # many times as is necessary to orient those dimensions to the current orientation.

        width, height = self._source_image.size

        # if the crop was made when the image was on its side, swap height and width
        if self._crop_orientation in (90, 270):
            width, height = height, width
        self._image_widget.set_crop_selection(self._last_crop_coordinates, width, height)

        # target_orientation = (degrees needed to rotate _crop_orientation to 0deg) + (current orientation)
        un_orient_crop = 360 - self._crop_orientation
        target_orientation = (un_orient_crop + self._orientation) % 360

        # crop overlay's rotation operation works at 90 degree intervals (clockwise)
        num_rotations = target_orientation // 90
        for times in range(0, num_rotations):
            self._image_widget.rotate_crop_overlay()

        # Reset the crop coordinates, dropping any previous croppings
        self._crop_coordinates = None

        # Store the existing image settings elsewhere, and reset current
        # settings to default so the image under the crop overlay is
        # the original one
        self.push_options()
        # Make sure the crop overlay is showing
        self._image_widget.show_crop_overlay()
        
        self._update_base_image()
        self._update_border_image()

    def do_crop_apply(self):
        # Get the coordinates of the crop overlay square. If the orientation
        # is such that the image is on its side, transpose the height/width
        # to reflect this
        width, height = self._source_image.size
        if self._orientation in (90, 270):
            width, height = height, width
        self.pop_options()
        self._last_crop_coordinates = None
        self._crop_coordinates = self._image_widget.get_crop_selection(width, height)
        self._crop_orientation = self._orientation
        self._image_widget.hide_crop_overlay()
        
        self._update_base_image()
        self._update_border_image()

    def do_crop_cancel(self):
        # Reclaim all effects which were applied before cropping began,
        # including crop coordinates (if any)
        self.pop_options()

        self._image_widget.hide_crop_overlay()
        
        # Revert the base image's crop state to what it was before
        # the crop overlay was activated
        self._update_base_image(revert_crop=True)
        self._update_border_image()

    def set_blur(self, value):
        self._blur_type = value
        self._update_base_image()

    def get_blur(self):
        return self._blur_type

    def set_brightness(self, value):
        self._brightness = value
        self._update_base_image()

    def get_saturation(self):
        return self._saturation

    def set_saturation(self, value):
        self._saturation = value
        self._update_base_image()

    def get_filter(self):
        return self._filter

    def set_filter(self, filter_name):
        self._filter = filter_name
        self._update_base_image()

    def get_border(self):
        return self._border

    def set_border(self, border_name):
        if (not self.is_open()):
            return
        self._border = border_name
        self._update_border_image()

    def set_distortion(self, distort_name):
        self._distort = distort_name
        self._update_base_image()

    def get_distortion(self):
        return self._distort

    def _update_base_image(self, revert_crop=False):
        if (not self.is_open()):
            return
        modified = False

        if self._crop_coordinates == None:
            self._cropped_image = self._source_image
        if self._orientation == 0:
            self._rotated_image = self._cropped_image

        # If we need to crop, first rotate the image, then apply the crop, and then
        # rotate the cropped image back to 0 degrees. The image must first be rotated
        # because the coordinates are oriented relative to the Clutter widget, not
        # the image. The image is then rotated back to default orientation so that
        # rotations on the cropped image are 1:1 with rotations on the base image
        if self._crop_coordinates not in (None, self._last_crop_coordinates) or revert_crop:
            if revert_crop:
                orientation_when_cropped = self._crop_orientation
                self._crop_coordinates = self._last_crop_coordinates
            else:
                orientation_when_cropped = self._orientation
                self._last_crop_coordinates = self._crop_coordinates
            modified = True
            temp_rotated = ImageTools.rotate_by_angle(self._source_image, orientation_when_cropped)
            rotated_cropped = temp_rotated.crop(self._crop_coordinates)
            self._cropped_image = ImageTools.rotate_by_angle(rotated_cropped, -orientation_when_cropped)

        if not self._last_orientation == self._orientation or modified:
            modified = True
            self._rotated_image = ImageTools.rotate_by_angle(self._cropped_image, self._orientation)
            self._last_orientation = self._orientation

        # filter
        if not self._filter == self._last_filter or modified:
            if self._filter in self._filter_dict:
                modified = True
                self._last_filter = self._filter
                self._filtered_image = self._filter_dict[self._filter](self._rotated_image)
            else:
                print("Filter not supported!")

        # distort
        if not self._distort == self._last_distort or modified:
            modified = True
            self._last_distort = self._distort
            self._distorted_image = self._distortions_dict[self._distort](self._filtered_image)

        # blur
        if not self._last_blur_type == self._blur_type or modified:
            if self._blur_type in self._blur_dict:
                modified = True
                self._last_blur_type = self._blur_type
                self._blurred_image = self._blur_dict[self._blur_type](self._distorted_image)
            else:
                print("Blur not supported!")

        # adjust
        adjusted = not (self._last_brightness == self._brightness
                        and self._last_contrast == self._contrast
                        and self._last_saturation == self._saturation)
        if adjusted or modified:
            modified = True
            im = ImageTools.apply_contrast(self._blurred_image, self._contrast)
            im = ImageTools.apply_brightness(im, self._brightness)
            im = ImageTools.apply_saturation(im, self._saturation)
            self._adjusted_image = im

        # update widget
        if modified:
            width, height = self._adjusted_image.size
            if self._displayable:
                self._image_widget.replace_base_image(
                    self._adjusted_image.tobytes(), width, height)
            self._is_saved = False

    def _update_border_image(self):
        filename = self._border_dict[self._border]
        if filename is not None:
            border = util.load_pil_image_from_resource(BORDERS_RESOURCE_PREFIX + filename)
            self._border_image = border.resize(self._adjusted_image.size, Image.BILINEAR)
            width, height = self._border_image.size
            if self._displayable:
                self._image_widget.replace_border_image(
                    self._border_image.tobytes(), width, height)
            self._is_saved = False
        else:
            self._border_image = None
            if self._displayable:
                self._image_widget.hide_border_image()

    def _composite_final_image(self):
        if self._border_image is None:
            return self._adjusted_image
        return Image.composite(self._border_image, self._adjusted_image, self._border_image)
