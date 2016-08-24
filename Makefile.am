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

# static assets GResource file
asset_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=$(srcdir)/data --generate-dependencies $(srcdir)/data/endless_photos.gresource.xml)
data/endless_photos.gresource: data/endless_photos.gresource.xml $(asset_resource_files)
	mkdir -p data
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=$(srcdir)/data  $<
CLEANFILES += data/endless_photos.gresource

# Filter thumbnails. These will be made automatically when building from a
# clean source tree. After that, you need to manually run "make thumbnails" to
# force the thumbnail gresource to build
thumbnails:
	rm -f data/images/thumbnails/thumbnails.gresource.xml
	$(MAKE) $(AM_MAKEFLAGS) data/images/thumbnails/thumbnails.gresource

data/images/thumbnails/thumbnails.gresource.xml: data/endless_photos.gresource
	$(AM_V_GEN) $(builddir)/generate-filter-thumbnails
CLEANFILES += data/images/thumbnails/thumbnails.gresource.xml

# filter thumbnails GResource file
thumbnail_resource_files = $(shell $(GLIB_COMPILE_RESOURCES) --sourcedir=data/images/thumbnails --generate-dependencies data/images/thumbnails/thumbnails.gresource.xml)
data/images/thumbnails/thumbnails.gresource: data/images/thumbnails/thumbnails.gresource.xml $(thumbnail_resource_files)
	$(AM_V_GEN) $(GLIB_COMPILE_RESOURCES) --target=$@ --sourcedir=data/images/thumbnails  $<
CLEANFILES += data/images/thumbnails/thumbnails.gresource $(thumbnail_resource_files)

subst_install = sed -e 's|@pkgdatadir[@]|$(pkgdatadir)|g' \
	-e 's|@datadir[@]|$(datadir)|g' \
	-e 's|@bindir[@]|$(bindir)|g'
subst_local = sed -e 's|@pkgdatadir[@]|$(realpath $(dir $(lastword $(MAKEFILE_LIST))))|g' \
	-e 's|@datadir[@]|$(datadir)|g'
eos-photos: eos-photos.in Makefile
	$(AM_V_GEN) $(subst_install) $< > $@
	chmod +x $@
	$(AM_V_at) $(subst_local) $< > eos-photos-local
	chmod +x eos-photos-local
CLEANFILES += eos-photos \
	eos-photos-local

applicationsdir = $(datadir)/applications
dist_applications_DATA = data/com.endlessm.photos.desktop

data/com.endlessm.photos.service: data/com.endlessm.photos.service.in Makefile
	$(AM_V_GEN) $(MKDIR_P) data && \
	$(subst_install) $< > $@

servicesdir = $(datadir)/dbus-1/services
services_DATA = data/com.endlessm.photos.service

CLEANFILES += $(services_DATA)
EXTRA_DIST += data/com.endlessm.photos.service.in

gsettings_SCHEMAS = data/com.endlessm.photos.gschema.xml

@GSETTINGS_RULES@

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
	src/widgets/composite_button.py \
	src/widgets/image_text_button.py \
	src/widgets/option_list.py \
	src/widgets/preview_file_chooser_dialog.py \
	src/widgets/slider.py \
	src/widgets/text_entry.py \
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
	src/resource_prefixes.py \
	src/splash_screen.py \
	src/util.py \
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
	COPYING.GPLv2 \
	$(py_sources) \
	$(asset_resource_files) \
	eos-photos.in \
	data/images/thumbnail_original.jpg \
	data/endless_photos.gresource.xml \
	$(gsettings_SCHEMAS) \
	$(NULL)

# # # TESTS # # #
