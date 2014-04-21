"""
The extraction of the curves from the acv files are from here:
    https://github.com/WeemoApps/filteriser
"""

from struct import unpack
from scipy import interpolate
import numpy

from .. import util


class Curve:
    def __init__(self, acv_file_name, name):
        self.name = name

        acv_file = util.load_byte_stream_from_resource("/com/endlessm/photos/curves/" + acv_file_name)
        self.curves = self._read_curves(acv_file)
        self.polynomials = self._find_coefficients()

    def _read_curves(self, acv_file):
        _, nr_curves = unpack('!hh', acv_file.read(4))
        curves = []
        for i in xrange(0, nr_curves):
            curve = []
            num_curve_points, = unpack('!h', acv_file.read(2))
            for j in xrange(0, num_curve_points):
                y, x = unpack('!hh', acv_file.read(4))
                curve.append((x, y))
            curves.append(curve)

        return curves

    def _find_coefficients(self):
        polynomials = []
        for curve in self.curves:
            xdata = [x[0] for x in curve]
            ydata = [x[1] for x in curve]
            p = interpolate.lagrange(xdata, ydata)
            polynomials.append(p)
        return polynomials

    def get_r(self):
        return self.polynomials[1]

    def get_g(self):
        return self.polynomials[2]

    def get_b(self):
        return self.polynomials[3]

    def get_c(self):
        return self.polynomials[0]


class CurveManager:
    def __init__(self):
        self.curves = {}
        #add some stuff here

    def add_curve(self, curve_obj):
        # Overwrites if such a curve already exists
        # NOTE: Fix or not to fix?
        self.curves[curve_obj.name] = curve_obj

    def apply_curve(self, curve_name, image_array):

        if image_array.ndim < 3:
            raise Exception('Photos must be in color, meaning at least 3 channels')
        else:
            def interpolate(i_arr, f_arr, p, p_c):
                p_arr = p_c(f_arr)
                return p_arr

            # NOTE: Assumes that image_array is a numpy array
            image_curve = self.curves[curve_name]
            # NOTE: What happens if curve does not exist?
            width, height, channels = image_array.shape
            curve_array = numpy.zeros((width, height, 3), dtype=float)

            p_r = image_curve.get_r()
            p_g = image_curve.get_g()
            p_b = image_curve.get_b()
            p_c = image_curve.get_c()

            curve_array[:,:,0] = p_r(image_array[:,:,0])
            curve_array[:,:,1] = p_g(image_array[:,:,1])
            curve_array[:,:,2] = p_b(image_array[:,:,2])
            curve_array = curve_array.clip(0, 255)
            curve_array = p_c(curve_array)

            curve_array = numpy.ceil(curve_array).clip(0, 255)

            return curve_array.astype(numpy.uint8)
