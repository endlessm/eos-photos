from skimage.transform import *
from skimage.morphology import *
from skimage import img_as_ubyte, img_as_float
import numpy
from scipy import ndimage
import scipy

class Distortion:

    def __init__(self, arr):
        self._image_array = arr

    def fish_eye(self, k, radius_d):
        return (radius_d * (1 + (k * (radius_d ** 2))))

    def bulge(self, radius_d):
        return radius_d ** 2

    def pinch(self, k, radius_d):
        return radius_d ** k 

    def radius_distort(self, xy, width, height, radius_func, zoom_factor):
        x, y = xy.T

        # scale image down to -1 to 1 scale
        x = ((2 * x) / width) -1
        y = ((2 * y) / height) -1

        x0 = y0 = 0
        radius_d = np.sqrt((x - x0) ** 2 + (y - y0) ** 2)

        radius_u = radius_func(radius_d)

        # hack to prevent divide by zero warnings
        radius_d[numpy.where(radius_d == 0)] = 1

        unit_x = (x - x0) / radius_d
        unit_y = (y - y0) / radius_d

        x = x0 + (unit_x * radius_u)
        y = y0 + (unit_y * radius_u)
    
        #zoom zoom!
        x /= zoom_factor
        y /= zoom_factor

        xy[..., 0] = (x + 1) * width / 2
        xy[..., 1] = (y + 1) * height / 2 

        return xy

    def apply(self, distort_name):
        shape = self._image_array.shape

        center = np.array(self._image_array.shape)[:2] / 2
        warp_args = {'width': shape[1], 'height': shape[0]}

        if distort_name == "SWIRL":
            radius = max(shape[0], shape[1]) / 2
            result = swirl(self._image_array, center=(shape[1]/2, shape[0]/2), strength=5, 
                radius=radius, order=1, mode='nearest')
        elif distort_name == "FISH EYE LIGHT":
            warp_args['radius_func'] = lambda radius_d: self.fish_eye(0.3, radius_d)
            warp_args['zoom_factor'] = 1.6
            result = warp(self._image_array, self.radius_distort, map_args=warp_args, mode='nearest')
        elif distort_name == "FISH EYE HEAVY":
            warp_args['radius_func'] = lambda radius_d: self.fish_eye(0.6, radius_d)
            warp_args['zoom_factor'] = 2.2
            result = warp(self._image_array, self.radius_distort, map_args=warp_args, mode='nearest')
        elif distort_name == "BULGE":
            warp_args['radius_func'] = lambda radius_d: self.bulge(radius_d)
            warp_args['zoom_factor'] = 1.45
            result = warp(self._image_array, self.radius_distort, map_args=warp_args, mode='nearest')
        elif distort_name == "PINCH LIGHT":
            warp_args['radius_func'] = lambda radius_d: self.pinch(0.8, radius_d)
            warp_args['zoom_factor'] = 1
            result = warp(self._image_array, self.radius_distort, map_args=warp_args, mode='nearest')
        elif distort_name == "PINCH HEAVY":
            warp_args['radius_func'] = lambda radius_d: self.pinch(0.5, radius_d)
            warp_args['zoom_factor'] = 1
            result = warp(self._image_array, self.radius_distort, map_args=warp_args, mode='nearest')
        else:
            result = self._image_array

        return img_as_ubyte(result)
