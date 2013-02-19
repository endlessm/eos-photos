import os
import Image
import ImageOps
import ImageFilter
from social_bar_presenter import SocialBarPresenter
from social_bar_model import SocialBarModel

from filter import Filter
from filter import FilterManager
import numpy

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

TEMP_FILE = os.path.expanduser("~/Desktop/temp.jpg")
CURVE_FOLDER = "../data/curves/"

class PhotosModel(object):
    """
    The model for the photo being edited. Uses the Python Imaging Library to
    modify the current open photo.
    """

    

    def __init__(self):
        super(PhotosModel, self).__init__()
        self._src_image = None
        self._curr_image = None
        self._is_saved = 1
        
        #set up social bar so we can connect to facebook
        social_bar_model = SocialBarModel()
        self._social_bar = SocialBarPresenter(model=social_bar_model)

        self._curve_filters = []

        for files in os.listdir(CURVE_FOLDER):
            if files.lower().endswith(".acv"):
                self._curve_filters.append(files.split('.')[0].upper())

    def open(self, filename):
        self._filename = filename
        self._src_image = self.limit_size(Image.open(filename), (2056, 2056))
        self._curr_image = self._src_image
        self._curr_filter = self.get_default_name()
        self._is_saved = 1
        

    def save(self, filename, format=None):
        if self._curr_image != None:
            if format!=None:
                self._curr_image.save(filename, format)
            else: self._curr_image.save(filename)
            self._is_saved = 1    

    def get_image(self):
        return self._curr_image

    def is_open(self):
        return self._curr_image != None

    def get_curr_filename(self):
        if not self.is_open(): return None
        return self._filename

    def is_saved(self):
        return self._is_saved

    def is_modified(self):
        return self._curr_filter is not "NORMAL"

    def get_filter_names(self):
        filters =  ["NORMAL", "GRAYSCALE", "SEPIA", 
        "PIXELATE", "BOXELATE", "OLD PHOTO", "GRUNGIFY", 
        "SCRATCH", "FABRIC", "BUMPY", "PAPER", "CONTOUR", "SMOOTH", 
        "SHARPEN", "EMBOSS", "INVERT", "SOLARIZE", "POSTERIZE", "FIND_EDGES", "BLUR"]

        filters.extend(self._curve_filters)

        return filters

    def get_default_name(self):
        return "NORMAL"

    def post_to_facebook(self, message):
        print "facebook"
        if not self._social_bar.is_user_loged_in():
            self._social_bar.fb_login()
        
        self._curr_image.save(TEMP_FILE)
        self._social_bar.post_image(TEMP_FILE, message)
        print "end post to facebook"

    def _create_email(self, message, recipient):
        # Set up header of email
        email = MIMEMultipart()
        email["From"] = "Rory MacQueen"
        email["To"] = recipient
        email["Subject"] = "Check out my photo from Endless Photos!"

        # Embed image in body of email using HTML
        body = MIMEText('<p>' + message + ' </p><img src="cid:myimage" />', _subtype='html')
        email.attach(body)

        # Write image to email from file
        self._curr_image.save(TEMP_FILE)
        fp = open(TEMP_FILE, 'rb')
        msg = MIMEImage(fp.read())
        msg.add_header('Content-Id', '<myimage>')
        #email.add_header('Content-Disposition', 'inline', filename=TEMP_FILE)
        email.attach(msg)
        return email.as_string()

    def email_photo(self, recipient, message):
        # Set up email.
        # TODO: Change this so it is not always sending from Rory's email!
        from_addr = "rorymacqueen@gmail.com"
        to_addr = recipient
        username = 'rorymacqueen'
        password = ''

        email = self._create_email(message, recipient)

        # For now, always using gmail server
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        # Send email
        server.sendmail(from_addr, [to_addr], email)
        server.quit()


    def _apply_filter_ext(self, image, filter_name):
        img_filter = Filter("../data/curves/" + filter_name.lower() + ".acv", 'crgb')
        
        image_array = numpy.array(image)

        filter_manager = FilterManager()
        filter_manager.add_filter(img_filter)

        filter_array = filter_manager.apply_filter('crgb', image_array)
        return Image.fromarray(filter_array)


    def apply_filter(self, filter_name):
        if (not self.is_open()) or self._curr_filter == filter_name: return
        self._curr_filter = filter_name
        self._is_saved = 0
        if filter_name == "NORMAL":
            self._curr_image = self._src_image.copy()
        elif filter_name == "GRAYSCALE":
            self._curr_image = ImageOps.grayscale(self._src_image)
        elif filter_name == "SEPIA":
            self._curr_image = self.apply_palette(self._src_image, self.make_linear_ramp((255, 201, 159)))
        elif filter_name == "PIXELATE":
            self._curr_image = self.pixelate(self._src_image)
        elif filter_name == "BOXELATE":
            self._curr_image = self.boxelate(self._src_image)
        elif filter_name == "OLD PHOTO":
            self._curr_image = self.old_photo(self._src_image)
        elif filter_name == "GRUNGIFY":
            self._curr_image = self.texture_overlay(self._src_image, "../images/textures/grunge.jpg", 0.15)
        elif filter_name == "SCRATCH":
            self._curr_image = self.texture_overlay(self._src_image, "../images/textures/old_film.jpg", 0.25)
        elif filter_name == "FABRIC":
            self._curr_image = self.texture_overlay(self._src_image, "../images/textures/fabric.jpg", 0.35)
        elif filter_name == "BUMPY":
            self._curr_image = self.texture_overlay(self._src_image, "../images/textures/bumpy.jpg", 0.35)
        elif filter_name == "PAPER":
            self._curr_image = self.texture_overlay(self._src_image, "../images/textures/paper.jpg", 0.35)
        elif filter_name == "CONTOUR":
            self._curr_image = self._src_image.filter(ImageFilter.CONTOUR)
        elif filter_name == "SMOOTH":
            self._curr_image = self._src_image.filter(ImageFilter.SMOOTH_MORE)
        elif filter_name == "SHARPEN":
            self._curr_image = self._src_image.filter(ImageFilter.SHARPEN)
        elif filter_name == "EMBOSS":
            self._curr_image = self._src_image.filter(ImageFilter.EMBOSS)
        elif filter_name == "INVERT":
            self._curr_image = self.invert(self._src_image)
        elif filter_name == "SOLARIZE":
            self._curr_image = self.solarize(self._src_image)
        elif filter_name == "POSTERIZE":
            self._curr_image = self.posterize(self._src_image)
        elif filter_name == "FIND_EDGES":
            self._curr_image = self._src_image.filter(ImageFilter.FIND_EDGES)
        elif filter_name == "BLUR":
            self._curr_image = self._src_image.filter(ImageFilter.BLUR)
        elif filter_name in self._curve_filters:
            self._curr_image = self._apply_filter_ext(self._src_image, filter_name)
        else:
            self._is_saved = 1
            print "Filter not supported!"

    def limit_size(self, image, size_limits):
        width, height = image.size
        width_limit, height_limit = size_limits
        if width < width_limit and height < height_limit:
            return image
        else:
            scale = min(width_limit / float(width), height_limit / float(height))
            new_size = map(int, (width * scale, height * scale))
            return image.resize(new_size, Image.BILINEAR)

    def make_linear_ramp(self, color):
        ramp = []
        r, g, b = color
        for i in range(256):
            ramp.extend((r*i/255, g*i/255, b*i/255))
        return ramp

    def apply_palette(self, image, palette):
        mode = image.mode
        image = image.convert("L")
        image.putpalette(palette)
        image = image.convert(mode)
        return image

    def pixelate(self, image, pixel_size=10):
        width, height = image.size
        downsized = image.resize((width/16, height/16))
        return downsized.resize((width, height))

    def texture_overlay(self, image, texture_path, alpha=0.5):
        texture = Image.open(texture_path)
        texture = texture.resize(image.size)
        texture = texture.convert(image.mode)
        return Image.blend(image, texture, alpha)

    def kill_alpha(self, image):
        mode = image.mode
        if mode == "L" or mode == "RGB":
            return image
        return image.convert("RGB")

    def old_photo(self, image):
        image = self._apply_filter_ext(image, "LUMO")
        image = self.apply_palette(image, self.make_linear_ramp((255, 201, 159)))
        return self.texture_overlay(image, "../images/textures/old_film.jpg", 0.25)

    # These filters don't support an alpha channel, so we have to loose all transparencies.
    def boxelate(self, image):
        image = self.kill_alpha(image)
        image = self.pixelate(image)
        return image.filter(ImageFilter.FIND_EDGES)

    def invert(self, image):
        image = self.kill_alpha(image)
        return ImageOps.invert(image)

    def solarize(self, image):
        image = self.kill_alpha(image)
        return ImageOps.solarize(image)

    def posterize(self, image, bits=2):
        image = self.kill_alpha(image)
        return ImageOps.posterize(image, bits)
