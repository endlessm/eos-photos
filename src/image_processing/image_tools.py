import numpy
from scipy import ndimage
import Image
import ImageOps
import ImageFilter
import ImageEnhance
import colorsys

from curve import Curve
from curve import CurveManager

"""
Pretty much all the image processing functionality we coded right now. Maybe
someday split into filters, basic tools, etc.
"""

_CURVES_PATH = ""
_TEXTURES_PATH = ""

rgb_to_hsv = numpy.vectorize(colorsys.rgb_to_hsv)
hsv_to_rgb = numpy.vectorize(colorsys.hsv_to_rgb)

def set_curves_path(curves_path):
    global _CURVES_PATH
    _CURVES_PATH = curves_path

def set_textures_path(textures_path):
    global _TEXTURES_PATH
    _TEXTURES_PATH = textures_path

def limit_size(image, size_limits):
    width, height = image.size
    width_limit, height_limit = size_limits
    if width < width_limit and height < height_limit:
        return image
    else:
        scale = min(width_limit / float(width), height_limit / float(height))
        new_size = map(int, (width * scale, height * scale))
        return image.resize(new_size, Image.BILINEAR)

def apply_contrast(image, value):
    enh = ImageEnhance.Contrast(image)
    return enh.enhance(value)

def apply_brightness(image, value):
    enh = ImageEnhance.Brightness(image)
    return enh.enhance(value)

def apply_saturation(image, value):
    enh = ImageEnhance.Color(image)
    return enh.enhance(value)

def color_enhance(image, amount):
    arr = numpy.array(numpy.asarray(image).astype('float'))
    r, g, b = numpy.rollaxis(arr, axis=-1)
    h, s, v = rgb_to_hsv(r, g, b)
    s = numpy.minimum(1.0, amount * s)
    r, g, b = hsv_to_rgb(h, s, v)
    arr = numpy.dstack((r, g, b))
    return Image.fromarray(arr.astype('uint8'), 'RGB')

def apply_curve(image, curve_file):
    img_curve = Curve(_CURVES_PATH + curve_file, 'crgb')
    image_array = numpy.array(image)
    curve_manager = CurveManager()
    curve_manager.add_curve(img_curve)
    curve_array = curve_manager.apply_curve('crgb', image_array)
    return Image.fromarray(curve_array)

def make_linear_ramp(color):
    ramp = []
    r, g, b = color
    for i in range(256):
        ramp.extend((r*i/255, g*i/255, b*i/255))
    return ramp

def apply_palette(image, palette):
    mode = image.mode
    image = image.convert("L")
    image.putpalette(palette)
    image = image.convert(mode)
    return image

def pixelate(image, pixel_size=10):
    width, height = image.size
    downsized = image.resize((width/16, height/16))
    return downsized.resize((width, height))

def texture_overlay(image, texture_file, alpha=0.5):
    texture = Image.open(_TEXTURES_PATH + texture_file)
    texture = texture.resize(image.size)
    return Image.blend(image, texture, alpha)

def vignette(image, texture_file):
    black = Image.open(_TEXTURES_PATH + "black.png")
    black = black.resize(image.size)
    texture = Image.open(_TEXTURES_PATH + texture_file)
    texture = texture.resize(image.size)
    return Image.composite(black, image, texture)

def sepia_tone(image):
    return apply_palette(image, make_linear_ramp((255, 201, 159)))

def old_photo(image):
    image = apply_curve(image, "lumo.acv")
    image = sepia_tone(image)
    return texture_overlay(image, "old_film.jpg", 0.25)

def tilt_shift_blur(image):
    return boring_blur(image)

def depth_of_field_blur(image):
    return boring_blur(image)

def boring_blur(image):
    im1 = image.filter(ImageFilter.BLUR)
    return im1

# These filters don't support an alpha channel, so we have to loose all transparencies.
def boxelate(image):
    image = pixelate(image)
    return image.filter(ImageFilter.FIND_EDGES)

def invert(image):
    return ImageOps.invert(image)

def solarize(image):
    return ImageOps.solarize(image)

def posterize(image, bits=2):
    return ImageOps.posterize(image, bits)

def grayscale(image):
    image = ImageOps.grayscale(image)
    image = image.convert('RGB')
    return vignette(image, "light_vignette.png")

def grunge(image):
    image = texture_overlay(image, "grunge.jpg", 0.075)
    return vignette(image, "heavy_vignette.png")

def bumpy(image):
    image = texture_overlay(image, "bumpy.jpg", 0.15)
    return vignette(image, "light_vignette.png")

def paper(image):
    image = apply_contrast(image, 1.4)
    image = texture_overlay(image, "paper.jpg", 0.4)
    return vignette(image, "light_vignette.png")

def country(image):
    image = apply_curve(image, "country.acv")
    return vignette(image, "heavy_vignette.png")

def foggy_blue(image):
    image = apply_curve(image, "fogy_blue.acv")
    return vignette(image, "heavy_vignette.png")

def desert(image):
    image = apply_curve(image, "desert.acv")
    return vignette(image, "weird_vignette.png")

def lumo(image):
    image = color_enhance(image, 1.2)
    image = texture_overlay(image, "paper.jpg", 0.15)
    image = apply_curve(image, "lumo.acv")
    return vignette(image, "heavy_vignette.png")

def trains(image):
    image = apply_curve(image, "trains.acv")
    return vignette(image, "heavy_vignette.png")
    return image

def colorful(image):
    image = apply_contrast(image, 1.3)
    image = color_enhance(image, 1.4)
    image = vignette(image, "light_vignette.png")
    return image
