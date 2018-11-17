#!/usr/bin/env python3
'''
A stand-alone menu application launcher.

Primarily for window managers like i3 and sway that
don't have built-in app launchers.
'''

import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, GLib
import os.path
import xdg.Menu

MENU_CONFIG = "/etc/xdg/menus/applications.menu"

def build_menu(model):
    'Build a Gtk.Menu from an xdg.Menu.Menu'
    view = Gtk.Menu()
    for entry in model.getEntries():
        if not entry.Show:
            continue
        if isinstance(entry, xdg.Menu.Menu):
            item = create_submenu(entry)
        elif isinstance(entry, xdg.Menu.MenuEntry):
            item = create_entry(entry.DesktopEntry)
        elif isinstance(entry, xdg.Menu.Separator):
            item = Gtk.SeparatorMenuItem.new()
        view.append(item)
    view.show_all()
    return view

def build_menu_item(label, icon_name, comment):
    'Create a Gtk.Menu'
    item = Gtk.MenuItem()
    box = Gtk.Box()
    image = get_image(icon_name)
    if image:
        box.pack_start(get_image(icon_name), False, False, 0)
    box.pack_end(Gtk.Label.new(label), True, True, 0)
    item.add(box)
    if comment is not None:
        item.set_tooltip_text(comment)
    return item

def create_entry(entry):
    'Create a Gtk.MenuItem for an xdg.Menu.MenuEntry'
    item = build_menu_item(entry.getName(), entry.getIcon(), entry.getComment())
    item.connect('activate', on_execute, entry)
    return item

def create_submenu(model):
    'Add a submenu to a Gtk.Menu for an xdg.Menu.Menu'
    submenu = build_menu(model)
    item = build_menu_item(model.getName(), model.getIcon(), model.getComment())
    item.set_submenu(submenu)
    return item

def get_image(icon_name):
    if not icon_name:
        return None
    try:
        # FIXME: fix icon size
        if os.path.isabs(icon_name):
            image = Gtk.Image.new_from_file(icon_name)
            image.set_pixel_size(16)
            return image
        return Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.MENU)
    except:
        print("Failed to get icon for {}".format(icon_name))
        # should we use a placeholder icon?
        return None

def on_execute(widget, entry):
    'Callback for clicking on a menu entry'
    app_info = Gio.DesktopAppInfo.new_from_filename(entry.filename)
    app_info.launch()

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
        Gio.Application.do_startup(self)


    def do_command_line(self, cl):
        options = cl.get_options_dict()
        prefix_opt = options.lookup_value('prefix')
        file_opt = options.lookup_value('file')
        if file_opt:
            conf_file = str(file_opt.get_bytestring())
        elif prefix_opt:
            conf_file = '/etc/xdg/menus/{}-applications.menu'.format(prefix_opt.get_string())
        else:
            conf_file = '/etc/xdg/menus/applications.menu'
        print("conf_file ", conf_file)
        if conf_file not in self.menus:
            print("building menu for {}".format(conf_file))
            self.menus[conf_file] = build_menu(xdg.Menu.parse(conf_file))
        self.menus[conf_file].popup(None, None, None, None, 0, Gtk.get_current_event_time())

        Gio.Application.do_command_line(self, cl)

def main():
    "Entrance point"
    app = MenuApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)

if __name__ == '__main__':
    main()
