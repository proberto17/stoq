# -*- coding: utf-8 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## Copyright (C) 2006 Async Open Source <http://www.async.com.br>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU Lesser General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Lesser General Public License for more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., or visit: http://www.gnu.org/.
##
## Author(s):   J. Victor Martins      <jvdm@sdf.lonestar.org>
##

""" Implementation of a generic slave for including images."""

import gtk

from kiwi.ui.dialogs import open
from kiwi.datatypes import converter
from kiwi.environ import environ

from stoqlib.gui.editors.baseeditor import BaseEditorSlave
from stoqlib.lib.translation import stoqlib_gettext

_ = stoqlib_gettext


default_filename = environ.find_resource("pixmaps", "remove48px.png")

# TODO: Currently the database doesn't deal with pixbufs,
#       despite kiwi does. So, we are not going to use proxies
#       here, but in future changes it could be made. See bug #2726.
class ImageSlave(BaseEditorSlave):
    """A slave view showing a image inside a gtk.Button. When clicked
    it opens a dialog for selecting a new image, saving it on the
    'image' attribute of the model"""

    gladefile = 'ImageHolder'
    pixbuf_converter = converter.get_converter(gtk.gdk.Pixbuf)

    def __init__(self, conn, model):
        self.model_type = type(model)
        BaseEditorSlave.__init__(self, conn, model)
        self._setup_menu()

        # if the image is not set in the model, show a default image
        if not model.image:
            self._show_image(default_filename, sensitive=False)
        else:
            self.image.set_from_pixbuf(
                self.pixbuf_converter.from_string(model.image))

    def _setup_menu(self):
        """ Create popup """
        self.edit_item = gtk.MenuItem(_("Edit"))
        self.erase_item = gtk.MenuItem(_("Erase"))
        self.popmenu = gtk.Menu()
        self.popmenu.append(self.edit_item)
        self.popmenu.append(self.erase_item)
        self.edit_item.connect("activate", self._on_popup_edit__activate)
        self.erase_item.connect("activate", self._on_popup_erase__activate)
        self.edit_item.show()
        self.erase_item.show()

    def _show_image(self, filename, sensitive):
        """Show an image from filename"""
        pixbuf = gtk.gdk.pixbuf_new_from_file_at_size(filename, 64, 64)
        self.image.set_from_pixbuf(pixbuf)
        self.erase_item.set_sensitive(sensitive)

    def _edit_image(self):
        """Opens a dialog to load and save a new image"""

        # generating a list of suported formats extensions
        # to 'open' function
        patterns = []
        for format in gtk.gdk.pixbuf_get_formats():
            for extension in format["extensions"]:
                patterns.append('*.' + extension)
        filename = open(_("Select Image"), None, patterns)

        if not filename:
            return

        self._show_image(filename, sensitive=True)
        self.model.image = self.pixbuf_converter.as_string(
            self.image.get_pixbuf())

    #
    # Gtk Callbacks, for the popup menu
    #

    def _on_popup_edit__activate(self, menu):
        self._edit_image()

    def _on_popup_erase__activate(self, menu):
        self.model.image = ''
        self._show_image(default_filename, sensitive=False)

    #
    # Kiwi Callbaks
    #

    # image has no windows, using eventbox to catch events
    def on_eventbox__button_press_event(self, eventbox, event):
        if event.button == 1:
            self._edit_image()
        elif event.button == 3:
            self.popmenu.popup(None, None, None, event.button, event.time)

    def on_eventbox__enter_notify_event(self, eventbox, event):
        self.image.drag_highlight()

    def on_eventbox__leave_notify_event(self, eventbox, event):
        self.image.drag_unhighlight()

