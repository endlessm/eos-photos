from gi.repository import Gtk, GdkPixbuf, Gdk
import os, sys

import array
import Image
import StringIO
import ImageFilter


class App:

	def __init__(self):

		window = Gtk.Window()
		window.set_title ("Photo App")
		window.connect_after('destroy', self.destroy)

		self.CHANGES_MADE = False # keeps track of unsaved changes

		# Sets Gtk box
		box = Gtk.Box()
		box.set_spacing (10)
		box.set_orientation (Gtk.Orientation.VERTICAL)
		window.add (box)

		# Sets image placeholder widget 
		self.image = Gtk.Image()
		box.pack_start (self.image, False, False, 0)

		# Sets button to open an image
		button = Gtk.Button ("Choose a picture")
		button.connect_after('clicked', self.on_open_clicked)
		box.pack_start (button, False, False, 0)

		# Sets button to apply a filter 
		button = Gtk.Button ("Filter")
		button.connect_after('clicked', self.apply_filter)
		box.pack_start (button, False, False, 0)

		# Sets button to save the image 
		button = Gtk.Button ("Save")
		button.connect_after('clicked', self.save_changes)
		box.pack_start (button, False, False, 0)
		
		window.set_default_size(250, 50)
		window.show_all()

	def on_open_clicked (self, button):

		global FILE_NAME # file address of the image
		global TEMP_FILE # file address of the temp image to apply changes

		TEMP_FILE = '~/Desktop/temp.jpg'

		# Opens a dialog window where the user can choose an image file
		dialog = Gtk.FileChooserDialog ("Open Image", button.get_toplevel(), Gtk.FileChooserAction.OPEN);

		# Adds 'Cancel' and 'Open' buttons
		dialog.add_button (Gtk.STOCK_CANCEL, 0)
		dialog.add_button (Gtk.STOCK_OK, 1)

		# Sets deafault to 'Open'
		dialog.set_default_response(1)

		# Filters and displays files which can be opened by Gtk.Image
		filefilter = Gtk.FileFilter ()
		filefilter.add_pixbuf_formats ()
		dialog.set_filter(filefilter)

		if dialog.run() == 1:

			# Loads the image
			FILE_NAME = dialog.get_filename()
			im = Image.open(FILE_NAME)

			# Creates a thumbnail of the given size
			# size = 50, 50
			# im.thumbnail(size, Image.ANTIALIAS)

			im.save(TEMP_FILE)

			# Converts image to pixbuf
			pbuf = self.image_to_pixbuf(im)

    			# Displays the chosen image
    			self.image.set_from_pixbuf(pbuf)

		dialog.destroy()

	def apply_filter (self, button):

		# Applies filter (contour) to the temporary file
		im = Image.open(TEMP_FILE)
		im = im.filter(ImageFilter.CONTOUR)
		im.save(TEMP_FILE)

		self.CHANGES_MADE = True

		# Displays image
		pbuf = self.image_to_pixbuf(im)
		self.image.set_from_pixbuf(pbuf)

	def save_changes (self, button):
		im = Image.open(TEMP_FILE)
		im.save(FILE_NAME)

		self.CHANGES_MADE = False

	# Terminates program on quitting
	def destroy(window, self):

		# Checks for unsaved changes
		if (window.CHANGES_MADE):
			dialog = Gtk.Dialog("Save before quitting?")
			dialog.set_default_size(250, 50)

			# Adds 'Cancel' and 'OK' buttons
			dialog.add_button (Gtk.STOCK_NO, 0)
			dialog.add_button (Gtk.STOCK_YES, 1)

			# Sets deafault to 'YES'
			dialog.set_default_response(1)

			# Saves the file on 'YES'
			if dialog.run() == 1:
				im = Image.open(TEMP_FILE)
				im.save(FILE_NAME)

			dialog.destroy()
			Gtk.main_quit()

	# Helper function to convert Image object to pixbuf 
	#  source: http://stackoverflow.com/questions/10341988/converting-pil-gdkpixbuf
	def image_to_pixbuf(self, img):
		if img.mode != 'RGB':
			img = img.convert('RGB')
		buff = StringIO.StringIO()
		img.save(buff, 'ppm')
		contents = buff.getvalue()
		buff.close()
		loader = GdkPixbuf.PixbufLoader.new_with_type('pnm')
		loader.write(contents)
		pixbuf = loader.get_pixbuf()
		loader.close()
		return pixbuf


def main():
	app = App()
	Gtk.main()
		
if __name__ == "__main__":
    sys.exit(main())
