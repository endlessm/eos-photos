## Process this file with automake to produce Makefile.in

# Copyright 2013 Endless Mobile, Inc.

## -----------
## Makefile.am
## -----------
## Please keep this file well-commented.

# Subdirectories where we also want to run make
SUBDIRS = po

# Our Autoconf macros are kept in the m4/ directory
ACLOCAL_AMFLAGS = -I m4

# Generated files that 'make clean' should erase
CLEANFILES =
DISTCLEANFILES =
EXTRA_DIST =

# # # BUILD RULES # # #

# Filter thumbnails. These will be made automatically when building from a
# clean source tree. After that, you need to manually run "make thumbnails" to
# force the thumbnail gresource to build
thumbnails:
	rm -f data/images/thumbnails/thumbnails.gresource.xml
	$(MAKE) $(AM_MAKEFLAGS) data/images/thumbnails/thumbnails.gresource

data/images/thumbnails/thumbnails.gresource.xml:
	$(AM_V_GEN) $(srcdir)/generate-filter-thumbnails
CLEANFILES += data/images/thumbnails/thumbnails.gresource.xml

# filter thumbnails GResource file
thumbnail_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=data/images/thumbnails --generate-dependencies data/images/thumbnails/thumbnails.gresource.xml)
data/images/thumbnails/thumbnails.gresource: data/images/thumbnails/thumbnails.gresource.xml $(thumbnail_resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=data/images/thumbnails  $<
CLEANFILES += data/images/thumbnails/thumbnails.gresource $(thumbnail_resource_files)

# static assets GResource file
asset_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=$(srcdir)/data --generate-dependencies $(srcdir)/data/endless_photos.gresource.xml)
data/endless_photos.gresource: data/endless_photos.gresource.xml $(asset_resource_files)
	mkdir -p data
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=$(srcdir)/data  $<
CLEANFILES += data/endless_photos.gresource

subst_install = sed -e 's|@pkgdatadir[@]|$(pkgdatadir)|g'
subst_local = sed -e 's|@pkgdatadir[@]|$(realpath $(dir $(lastword $(MAKEFILE_LIST))))|g'
eos-photos: eos-photos.in Makefile
	$(AM_V_GEN) $(subst_install) $< > $@
	chmod +x $@
	$(AM_V_at) $(subst_local) $< > eos-photos-local
	chmod +x eos-photos-local
CLEANFILES += eos-photos \
	eos-photos-local

# # # INSTALL RULES # # #

py_sources = \
	src/image_processing/__init__.py \
	src/image_processing/curve.py \
	src/image_processing/distortions.py \
	src/image_processing/image_tools.py \
	src/share/__init__.py \
	src/share/emailer.py \
	src/share/facebook_auth_dialog.py \
	src/share/facebook_post.py \
	src/share/facebook.py \
	src/widgets/__init__.py \
	src/widgets/clutter_image_button.py \
	src/widgets/composite_button.py \
	src/widgets/image_button.py \
	src/widgets/image_text_button.py \
	src/widgets/option_list.py \
	src/widgets/preview_file_chooser_dialog.py \
	src/widgets/slider.py \
	src/__init__.py \
	src/asyncworker.py \
	src/crop_overlay.py \
	src/draggable_box.py \
	src/drop_shadow_alignment.py \
	src/endless_photos.py \
	src/photos_category_toolbars.py \
	src/photos_image_container.py \
	src/photos_image_widget.py \
	src/photos_left_toolbar.py \
	src/photos_model.py \
	src/photos_presenter.py \
	src/photos_right_toolbar.py \
	src/photos_view.py \
	src/photos_window.py \
	src/splash_screen.py \
	$(NULL)

curves = \
	data/curves/desert.acv \
	data/curves/country.acv \
	data/curves/trains.acv \
	data/curves/fogy_blue.acv \
	data/curves/lumo.acv \
	$(NULL)

images = \
	data/images/borders/frame_3x2_brush.png \
	data/images/borders/frame_3x2_crayon.png \
	data/images/borders/frame_3x2_grunge.png \
	data/images/borders/frame_3x2_spray.png \
	data/images/textures/black.png \
	data/images/textures/bumpy.jpg \
	data/images/textures/grunge.jpg \
	data/images/textures/heavy_vignette.png \
	data/images/textures/light_vignette.png \
	data/images/textures/old_film.jpg \
	data/images/textures/paper.jpg \
	data/images/textures/weird_vignette.png \
	data/images/background-tile.jpg \
	data/images/background_splash.jpg \
	data/images/confirm_cancel-btn_hover.png \
	data/images/confirm_cancel-btn_normal.png \
	data/images/confirm_cancel-btn_pressed.png \
	data/images/confirm_ok-btn_hover.png \
	data/images/confirm_ok-btn_normal.png \
	data/images/confirm_ok-btn_pressed.png \
	data/images/crop_knob_dark.png \
	data/images/crop_knob_hover.png \
	data/images/crop_knob_normal.png \
	$(NULL)

nobase_pkgdata_DATA = \
	$(py_sources) \
	$(images) \
	$(curves) \
	data/images/thumbnails/thumbnails.gresource \
	data/endless_photos.gresource \
	$(NULL)

bin_SCRIPTS = eos-photos

dist_noinst_DATA = \
	$(NULL)

EXTRA_DIST += \
	$(py_sources) \
	$(images) \
	$(curves) \
	$(asset_resource_files) \
	eos-photos.in \
	generate-filter-thumbnails \
	data/images/thumbnail_original.jpg \
	data/endless_photos.gresource.xml \
	$(NULL)

# # # TESTS # # #
