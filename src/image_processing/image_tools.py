import numpy
import math
from scipy import ndimage, stats

from PIL import Image
from PIL import ImageOps
from PIL import ImageDraw
from PIL import ImageFilter
from PIL import ImageEnhance
import colorsys

from .. import util
from ..resource_prefixes import *
from .curve import Curve
from .curve import CurveManager
from .distortions import Distortion

"""
Pretty much all the image processing functionality we coded right now. Maybe
someday split into filters, basic tools, etc.
"""

def limit_size(image, size_limits):
    width, height = image.size
    width_limit, height_limit = size_limits
    if width < width_limit and height < height_limit:
        return image
    else:
        scale = min(width_limit / float(width), height_limit / float(height))
        new_size = list(map(int, (width * scale, height * scale)))
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

def apply_curve(image, curve_file):
    img_curve = Curve(curve_file, 'crgb')
    image_array = numpy.array(image)
    curve_manager = CurveManager()
    curve_manager.add_curve(img_curve)
    curve_array = curve_manager.apply_curve('crgb', image_array)
    return Image.fromarray(curve_array)

def make_linear_ramp(color):
    ramp = []
    r, g, b = color
    for i in range(256):
        ramp.extend((int(r*i/255), int(g*i/255), int(b*i/255)))
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
    texture = util.load_pil_image_from_resource(TEXTURES_RESOURCE_PREFIX + texture_file)
    texture = texture.resize(image.size)
    return Image.blend(image, texture, alpha)

def vignette(image, texture_file):
    black = util.load_pil_image_from_resource(TEXTURES_RESOURCE_PREFIX + "black.png")
    black = black.resize(image.size)
    texture = util.load_pil_image_from_resource(TEXTURES_RESOURCE_PREFIX + texture_file)
    texture = texture.resize(image.size)
    return Image.composite(black, image, texture)

def sepia_tone(image):
    return apply_palette(image, make_linear_ramp((255, 201, 159)))

def old_photo(image):
    image = apply_curve(image, "lumo.acv")
    image = sepia_tone(image)
    return texture_overlay(image, "old_film.jpg", 0.25)

def _depth_of_field_mask(center_x, center_y, size, radius):
    # center_x/center_y: the (x,y) coordinate of the transparent disk
    # radius: radius of the transparent disk
    # size: dimensions of the blur mask
    height, width = size
    yy, xx = numpy.mgrid[0:height, 0:width]
    xx = xx - center_x
    yy = yy - center_y
    rad = numpy.sqrt(numpy.power(xx, 2) + numpy.power(yy, 2))
    rad = stats.threshold(rad, threshmax=radius, newval=radius)
    rad = (rad / radius) * 255
    mask = Image.fromarray(numpy.uint8(rad))

    return mask

def _tilt_shift_mask(angle, rot_angle, size, center_pct, amplitude):
    # angle: the slope of the linear blur gradient, measured from rot_angle
    # rot_angle: corresponds to the angle of the plane of focus
    # center_pct: value from (0,1) indicating where the focus is on the y axis
    # amplitude: scales the blur after normalization
    height, width = size
    c = int(height * center_pct)
    rot_angle = 90.0
    mask = Image.new('L', (1,height))
    draw = ImageDraw.Draw(mask)
    l_slope = math.tan(math.radians(rot_angle + angle))
    l_max = -l_slope * c
    l_intercept = l_max
    r_slope = math.tan(math.radians(rot_angle - angle))
    r_max = r_slope * (height - c)
    r_intercept = -r_slope * c
    for y in range(0,c):
        raw = l_slope * y + l_intercept
        raw = (raw / l_max) * amplitude
        normalized = raw if raw < 255 else 255
        draw.point((0,y), int(normalized))
    for y in range(c,height):
        raw = r_slope * y + r_intercept
        raw = (raw / r_max) * amplitude
        normalized = raw if raw < 255 else 255
        draw.point((0,y), int(normalized))

    return mask

def tilt_shift_blur(image):
    mask = _tilt_shift_mask(30.0, 90.0, image.size, 0.5, 350)
    
    return blur_with_mask(image, mask, 3)

def depth_of_field_blur(image):
    height, width = image.size
    mask = _depth_of_field_mask(width/2, height/2, image.size, width/2)
    
    return blur_with_mask(image, mask, 3)

def boring_blur(image):
    return image.filter(ImageFilter.BLUR)

def blur_with_mask(image, mask, amount):
    blur_size = amount

    base = image.copy()
    mask = mask.resize(base.size)
    blurred = numpy.array(base, dtype=float)
    blurred = ndimage.gaussian_filter(blurred, sigma=[blur_size,blur_size,0])
    blurred = Image.fromarray(numpy.uint8(blurred))
    
    # paste the blurred image onto the original, using the alpha mask
    base.paste(blurred, (0,0), mask)
    return base

# Rotating in the clockwise direction, which seems more natural in code,
# is the reverse of the polar increasing direction. So, flip the values here
angle_constants = {
    0: None,
    90: Image.ROTATE_270,
    180: Image.ROTATE_180,
    270: Image.ROTATE_90
}

def rotate_by_angle(image, angle):
    normalized_angle = angle % 360
    pil_angle = angle_constants[normalized_angle]
    if pil_angle is not None:
        return image.copy().transpose(pil_angle)
    else:
        return image.copy()

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
    image = apply_saturation(image, 1.2)
    image = texture_overlay(image, "paper.jpg", 0.15)
    image = apply_curve(image, "lumo.acv")
    return vignette(image, "heavy_vignette.png")

def trains(image):
    image = apply_curve(image, "trains.acv")
    return vignette(image, "heavy_vignette.png")

def colorful(image):
    image = apply_contrast(image, 1.3)
    image = apply_saturation(image, 1.4)
    image = vignette(image, "light_vignette.png")
    return image

def distortion(image, disort_name):
    if disort_name == "NONE":
        return image
    image_array = numpy.array(image)
    distortion = Distortion(image_array)
    result = distortion.apply(disort_name)
    return Image.fromarray(result, 'RGB')
    
