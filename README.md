somenu (Stand-Alone MENU) is a Gtk application to show a classic system start menu for window managers that don't have their own (such as i3) or Desktop Environments that no longer use the classic nested menu format.

# Motivation

I built this because, while I use i3 wth rofi as my main application launcher, my wife prefers a more traditional way to start applications (like the Windows start menu). After looking for something that would work in i3, I was unable to find something that I liked, so I made somenu.

This project was heavily inspired by [rlmenu](https://github.com/blastrock/rlmenu). Initially, I wanted to just use that. But it hasn't been touched in 6 years, and no longer works with up-to-date libraries on Archlinux. After digging around a little, I realized it would probably be easier to build something new than resurrect rlmenu. However, I did use the rlmenu source code as a reference as I built this.

# Dependencies

- Python 3
- Gtk 3.0
- gnome-menus 3.0
