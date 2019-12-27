#!/usr/bin/env python3
'''
A stand-alone menu application launcher.

Primarily for window managers like i3 and sway that
don't have built-in app launchers.
'''

import sys
import traceback

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GMenu', '3.0')
from gi.repository import Gtk, Gio, GLib, GMenu, Gdk
import os.path

MENU_CONFIG = "/etc/xdg/menus/applications.menu"
ICON_SIZE = 48
FOLDER_ICON = Gio.ThemedIcon.new('folder')
APP_ICON = Gio.ThemedIcon.new('utilities-terminal')


def build_menu(directory):
    'Build a Gtk.Menu from a GMenu.TreeDirectory'
    view = Gtk.Menu()
    it = directory.iter()
    for item_type in iter(it.next, GMenu.TreeItemType.INVALID):
        if item_type == GMenu.TreeItemType.DIRECTORY:
            item = create_submenu(it.get_directory())
        elif item_type == GMenu.TreeItemType.ENTRY:
            item = create_entry(it.get_entry())
        elif item_type == GMenu.TreeItemType.SEPARATOR:
            item = Gtk.SeparatorMenuItem.new()
        else:
            # maybe at some point add support for headers and aliases
            continue
        view.append(item)
    view.show_all()
    return view

def build_menu_item(label, icon, comment, fallback_icon):
    'Create a Gtk.Menu'
    item = Gtk.MenuItem()
    box = Gtk.Box()
    image = get_image(icon, fallback_icon)
    box.pack_start(image, False, False, 0)
    box.pack_end(Gtk.Label.new(label), True, True, 0)
    item.add(box)
    if comment is not None:
        item.set_tooltip_text(comment)
    return item

def create_entry(entry):
    'Create a Gtk.MenuItem for an GMenu.TreeEntry'
    info = entry.get_app_info()
    item = build_menu_item(info.get_name(), info.get_icon(), info.get_description(), APP_ICON)
    item.connect('activate', launch_app, info)
    return item

def create_submenu(directory):
    'Add a submenu to a Gtk.Menu for a GMenu.TreeDirectory'
    submenu = build_menu(directory)
    item = build_menu_item(directory.get_name(), directory.get_icon(), directory.get_comment(), FOLDER_ICON)
    item.set_submenu(submenu)
    return item

def load_icon(icon):
    'Load the PixBuf for a Gio.Icon'
    try:
        key = icon.to_string()
    except AttributeError:
        return None
    if key not in load_icon.lookup:
        info = Gtk.IconTheme.get_default().lookup_by_gicon(
            icon,
            ICON_SIZE,
            Gtk.IconLookupFlags.FORCE_SIZE)
        try:
            pixbuf = info and info.load_icon()
        except GLib.Error:
            traceback.print_exc()
            pixbuf = None
        load_icon.lookup[key] = pixbuf
    return load_icon.lookup[key]
load_icon.lookup = dict()

def get_image(icon, fallback):
    pixbuf = load_icon(icon) or load_icon(fallback)
    return Gtk.Image.new_from_pixbuf(pixbuf)

def launch_app(_menu, app):
    'Launch an app from the menu'
    app.launch()


class MenuApplication(Gio.Application):
    '''The application to show the menu'''

    def __init__(self):
        '''Initialize the application'''
        Gio.Application.__init__(self, application_id="com.github.tmccombs.somenu", flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.add_main_option('file',
                             ord('f'),
                             GLib.OptionFlags.NONE, GLib.OptionArg.FILENAME,
                             "XDG Menu file to read menu config from")
        self.add_main_option('prefix',
                             ord('p'),
                             GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
                             "Prefix to use to find XDG Menu file")
        self.menus = {}

    def do_startup(self):
        self.hold()
        self.window = Gtk.Window(resizable=False)
        self.window.set_type_hint(Gdk.WindowTypeHint.MENU)
        Gio.Application.do_startup(self)


    def do_command_line(self, cl):
        options = cl.get_options_dict()
        prefix_opt = options.lookup_value('prefix')
        file_opt = options.lookup_value('file')
        if file_opt:
            conf_file = file_opt.get_bytestring().decode()
        elif prefix_opt:
            conf_file = '/etc/xdg/menus/{}-applications.menu'.format(prefix_opt.get_string())
        else:
            conf_file = '/etc/xdg/menus/applications.menu'
        if conf_file not in self.menus:
            print("building menu for {}".format(conf_file))
            tree = GMenu.Tree.new_for_path(conf_file, 0)
            tree.load_sync()

            # TODO: should we listen for if the menu was changed?
            self.menus[conf_file] = build_menu(tree.get_root_directory())
        self.show_menu(self.menus[conf_file])

        Gio.Application.do_command_line(self, cl)

    def show_menu(self, menu):
        # using a popup without showing the root window is hacky, but it seems to work better than anything else
        menu.popup_at_widget(self.window, Gdk.Gravity.STATIC, Gdk.Gravity.NORTH_WEST, None)

def main():
    "Entrance point"
    app = MenuApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()
