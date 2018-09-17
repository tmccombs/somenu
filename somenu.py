#!/usr/bin/env python3
'''
A stand-alone menu application launcher.

Primarily for window managers like i3 and sway that
don't have built-in app launchers.
'''

import sys

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import xdg.Menu

MENU_CONFIG = "/etc/xdg/menus/applications.menu"

def build_menu(model):
    'Build a Gtk.Menu from an xdg.Menu.Menu'
    view = Gtk.Menu()
    for item in model.getEntries():
        if isinstance(item, xdg.Menu.Menu):
            add_submenu(view, item)
        elif isinstance(item, xdg.Menu.MenuEntry):
            add_entry(view, item.DesktopEntry)
        elif isinstance(item, xdg.Menu.Separator):
            seperator = Gtk.SeparatorMenuItem.new()
            view.append(seperator)
            seperator.show()
    view.show_all()
    return view

def append_menu_item(menu, label, icon_name, comment):
    'Add an item to a Gtk.Menu'
    item = Gtk.MenuItem(label=label)
    # TODO icon
    if comment is not None:
        item.set_tooltip_text(comment)
    menu.append(item)
    return item

def add_entry(menu, entry):
    'Add an item to Gtk.Menu for an xdg.Menu.MenuEntry'
    view = append_menu_item(menu, entry.getName(), entry.getIcon(), entry.getComment())
    view.connect('activate', on_execute, entry)

def add_submenu(menu, model):
    'Add a submenu to a Gtk.Menu for an xdg.Menu.Menu'
    submenu = build_menu(model)
    item = append_menu_item(menu, model.getName(), model.getIcon(), model.getComment())
    item.set_submenu(submenu)

def on_execute(widget, entry):
    'Callback for clicking on a menu entry'
    # TODO: better launch
    print("should run: {}".format(entry.getExec()))

class MenuApplication(Gio.Application):
    '''The application to show the menu'''

    def __init__(self):
        '''Initialize the application'''
        print("a")
        Gio.Application.__init__( self, application_id="com.github.tmccombs.somenu")
        print("b")
        self.menu = None

    def do_startup(self):
        self.hold()
        print("startup")
        #Gtk.Application.do_startup(self)
        print("creating")

        # create a menu
        self.menu = build_menu(xdg.Menu.parse(MENU_CONFIG))

    def do_activate(self):
        print("activating ({})".format(self.menu))
        self.menu.popup(None, None, None, None, 0, Gtk.get_current_event_time())

if __name__ == '__main__':
    app = MenuApplication()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)
