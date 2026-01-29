# Copyright (c) 2010 Aldo Cortesi
# Copyright (c) 2010, 2014 dequis
# Copyright (c) 2012 Randall Ma
# Copyright (c) 2012-2014 Tycho Andersen
# Copyright (c) 2012 Craig Barnes
# Copyright (c) 2013 horsik
# Copyright (c) 2013 Tao Sauvage
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import re
import subprocess
from libqtile.backend.base import Window
import time
from datetime import datetime, timedelta
from typing import Optional
# import logging
import threading
from libqtile import bar, extension, hook, layout, qtile, widget
from qtile_extras.widget.decorations import RectDecoration, BorderDecoration
from qtile_extras import widget as ewidget  # use extras’ widgets
from scripts.volume_control import volume_change, toggle_mute
from scripts.float_windows import *
from scripts.mpv_manager import mpv_manager
from scripts.toggle_apps import (
    toggle_qutebrowser,
    toggle_obsidian,
    toggle_anki,
    toggle_telegram,
    toggle_terminal,
    toggle_file_manager,
    toggle_google_chrome,
    toggle_brave,
)
from scripts.sum_app import toggle_or_spawn_sum
from libqtile.config import (
    Click,
    Drag,
    Group,
    Key,
    KeyChord,
    Match,
    Screen,
    DropDown,
    ScratchPad,
)
from libqtile.lazy import lazy

from popups.VimCheatsheet import  toggle_vim_cheatsheet , close_vim_cheatsheet, show_vim_cheatsheet
from popups.FishCheatsheet import toggle_fish_kitty_cheatsheet , close_fish_kitty_cheatsheet, show_fish_kitty_cheatsheet
from popups.QtileCheatsheet import toggle_cheatsheet, close_qtile_cheatsheet, show_qtile_cheatsheet

from popups import WallpaperPopup
from popups.WallpaperPopup import (
    toggle_wallpaper_picker,
    show_wallpaper_picker,
    close_wallpaper_picker,
    jump_to_random,
    fuzzy_search_rofi,
)



def toggle_onboarding(qtile):
    w = qtile.widgets_map.get("tooltip_widgetbox")
    if not w:
        return

    if w.box_is_open:
        # 🔴 closing
        qtile.cmd_spawn("pkill eww")
        w.toggle()
    else:
        # 🟢 opening
        qtile.cmd_spawn(
            "sh -c 'pkill eww; eww daemon & eww open onboarding-welcome'"
        )
        w.toggle()


ARCH_ICON_MAIN = "󰕰"

# 󰒓   # system / hub (you already use this – excellent choice)
# 󰘳   # dashboard
# 󰍜   # control center
# 󰍝   # control center (alt)
# 󰐙   # expand
# 󰐘   # collapse
# 󰆍   # terminal
# 󰆍   # console (alt font)
#     # terminal (classic NF)
# 󰞷   # code
# 󰙯   # dev tools
# 󰒔   # tools panel

# 󰣇   # Arch Linux (best available)
#      # Arch (space-balanced, classic)
#     # Arch (old, left-heavy)
# 󰍉   # launcher (rofi vibe)
# 󰆍   # menu / list
# 󰌧   # grid launcher
# 󰕰   # apps
# 󰕱   # apps filled
#
#
# 󰌽   # Linux
# 󰣚   # Linux outline
# 󰌾   # Tux variant
def set_icon_temporarily(qtile, icon, cmd):
    w = qtile.widgets_map.get("arch_icon_chip")
    if not w:
        return

    # update icon immediately
    w.update(icon)

    # spawn app
    qtile.cmd_spawn(cmd)

    # reset icon shortly after
    def reset():
        time.sleep(0.3)  # small delay so user sees the icon
        w.update(ARCH_ICON_MAIN)

    threading.Thread(target=reset, daemon=True).start()

def open_terminal(qtile):
    set_icon_temporarily(qtile, "󰞷", myTerm)

def open_launcher(qtile):
    set_icon_temporarily(
        qtile,
        "󰍉",
        "rofi -show drun -show-icons",
    )

# from pathlib import Path
#
# Make sure 'qtile-extras' is installed or this config will not work.
# from qtile_extras import widget
# from qtile_extras.widget.decorations import BorderDecoration

# from qtile_extras.widget import StatusNotifier
import colors

import logging
logging.basicConfig(level=logging.ERROR)

colorsW = [
    ["#282c34", "#282c34"],  # bg
    ["#bbc2cf", "#bbc2cf"],  # fg
    ["#1c1f24", "#1c1f24"],  # color01
    ["#ff6c6b", "#ff6c6b"],  # color02
    ["#98be65", "#98be65"],  # color03
    ["#da8548", "#da8548"],  # color04
    ["#51afef", "#51afef"],  # color05
    ["#c678dd", "#c678dd"],  # color06
    ["#46d9ff", "#46d9ff"],  # color15
]
DEFAULT_CHIP_COLOR=colorsW[2]

os.environ["GTK_IM_MODULE"] = "none"
os.environ["QT_IM_MODULE"] = "none"
os.environ["XMODIFIERS"] = ""

mod = "mod1"  # Sets mod key to SUPER/WINDOWS
mod2 = "mod4"  # Sets mod key to SUPER/WINDOWS
# myTerm = "alacritty"  # My terminal of choice
myTerm = "kitty"  # My terminal of choice
my2ndTerm = "alacritty"  # My terminal of choice
myFullScreenTerm = "kitty --start-as=fullscreen"
myBrowser2 = ["brave", "--layout.css.devPixelsPerPx=0.8"]
myBrowser3 = ["google-chrome-stable", "--layout.css.devPixelsPerPx=0.8"]
myBrowser4 = "qutebrowser"
sum_file = os.path.expanduser("~/ATITODOS/TODOS.md")
# myBrowser = ["zen-browser", "--layout.css.devPixelsPerPx=0.8"]
# myBrowser = ["qutebrowser", "--layout.css.devPixelsPerPx=0.8"]
# myBrowser = "firefox-small"  # My browser of choice


# edit_title = "edit-field"
home = os.path.expanduser("~")
# myEmacs = "emacsclient -c -a 'emacs' "  # The space at the end is IMPORTANT!


# Allows you to input a name when adding treetab section.
@lazy.layout.function
def add_treetab_section(layout):
    prompt = qtile.widgets_map["prompt"]
    prompt.start_input("Section name: ", layout.cmd_add_section)


# A function for hide/show all the windows in a group
# @lazy.function
# def minimize_all(qtile):
#     for win in qtile.current_group.windows:
#         if hasattr(win, "toggle_minimize"):
#             win.toggle_minimize()
#

# --- helper: previous layout ---
def kb_prev(qtile):
    w = qtile.widgets_map["keyboardlayout"]  # change if your widget has a custom name
    layouts = w.configured_keyboards
    current = w.backend.get_keyboard()
    if current in layouts:
        prev = layouts[(layouts.index(current) - 1) % len(layouts)]
    else:
        prev = layouts[-1]
    w.backend.set_keyboard(prev, w.option)
    # w.tick()


# =============================================================================
# GLOBAL CHEATSHEET STATE (for Pyright & safety)
# =============================================================================

# =============================================================================
# Wallpaper 
# =============================================================================

# =============================================================================
ACTIVE_CHORD = None

@hook.subscribe.enter_chord
def remember_chord(chord_name):
    global ACTIVE_CHORD
    ACTIVE_CHORD = chord_name



@hook.subscribe.enter_chord
def auto_enable_warpd(chord_name):
    if chord_name == "Mouse-Mode":
        qtile.spawn("warpd --normal")

@hook.subscribe.enter_chord
def auto_enable_draw(chord_name):
    if chord_name == "Draw-Mode":
        qtile.spawn("gromit-mpx -t")

@hook.subscribe.enter_chord
def auto_enable_cheatsheet(chord_name):
    if chord_name == "CheatSheet-Mode":
        show_qtile_cheatsheet(qtile)

@hook.subscribe.enter_chord
def auto_enable_wallpaper_picker(chord_name):
    if chord_name == "WallpaperPicker":

        show_wallpaper_picker(qtile)
   # Sync widget state
        w = qtile.widgets_map.get("wallpaper_toggle")
        if w and not w.box_is_open:
            w.toggle()



def exit_cheatsheet_mode(qtile):
    close_qtile_cheatsheet()
    close_vim_cheatsheet()
    close_fish_kitty_cheatsheet()
    qtile.ungrab_chord()

@hook.subscribe.leave_chord
def cleanup_on_leave():
    global ACTIVE_CHORD

    if ACTIVE_CHORD == "Draw-Mode":
        qtile.spawn("gromit-mpx -v")  # force OFF, not toggle

        # exit_cheatsheet_mode(qtile)
    elif ACTIVE_CHORD == "CheatSheet-Mode":
        close_qtile_cheatsheet()
        close_vim_cheatsheet()
        close_fish_kitty_cheatsheet()

    elif ACTIVE_CHORD == "WallpaperPicker":
        close_wallpaper_picker()
        # Sync widgetbox icon/state
        w = qtile.widgets_map.get("wallpaper_toggle")
        if w and w.box_is_open:
            w.toggle()


    ACTIVE_CHORD = None

def group_keys():
    return [
        Key([], str(i), lazy.group[str(i)].toscreen())
        for i in range(1, 10)
    ]



def set_kb(layout):
    return lazy.function(lambda q: (
        q.spawn(f"setxkbmap {layout}"),
        q.widgets_map["w_lang"].backend.set_keyboard(
            layout,
            q.widgets_map["w_lang"].option,
        ),
        q.ungrab_chord(),   # IMPORTANT
    ))



def close_wallpaper_mode(qtile):
    close_wallpaper_picker()
    qtile.ungrab_chord()

    w = qtile.widgets_map.get("wallpaper_toggle")
    if w and w.box_is_open:
        w.toggle()

def groupbox_widget():
    return chip(
        ewidget.GroupBox,
        fontsize=10,
        margin_y=2,
        margin_x=8,
        padding_y=2,
        padding_x=8,
        borderwidth=4,
        active=colors[8],
        inactive=colors[1],
        highlight_color=colors[2],
        highlight_method="text",
        this_current_screen_border=colors[7],
        this_screen_border=colors[4],
        other_current_screen_border=colors[7],
        other_screen_border=colors[4],
        hide_unused=True,
    )


def left_side_widgets():
    return [
        # logo
        #
        # chip(
        #     ewidget.Image,
        #     filename="~/.config/qtile/icons/archLogo.png",
        #     margin=5,
        #     padding=13,
        #     scale="False",
        #     mouse_callbacks={"Button1": lambda: qtile.cmd_spawn(myTerm)},
        # ),
        #     # Arch outline
        #     # Arch logo (older NF)
        #     # Arch filled (rare)

  
# 󰣇
chip(
    ewidget.TextBox,
    name="arch_icon_chip",
    text=ARCH_ICON_MAIN,
    fontsize=15,
    padding=11,
    foreground=colors[7],
    mouse_callbacks={
        "Button1": lazy.function(open_terminal),  # left click
        "Button3": lazy.function(open_launcher),  # right click
    },
),


        # chip(ewidget.WidgetBox,
        #      widgets=[
        #              widget.TextBox(text="This widget is in the box"),
        #                  widget.Memory()
        #                      ]),
        # chip(
        #     ewidget.Wallpaper,
        #     directory="~/Pictures/Wallpapers",
        #     margin=5,
        #     padding=13,
        # ),
        #
        # current layout
        chip(
            ewidget.CurrentLayout,
            padding=18,
            foreground=colors[3],
        ),

        # separator |
        widget.TextBox(
            text="|",
            font="Ubuntu Mono",
            foreground=colors[1],
            padding=3,
            fontsize=14,
        ),

        # task list
        widget.TaskList(
            font="JetBrainsMono Nerd Font",
            fontsize=11,

            # icons
            icon_size=16,
            markup=True,

            # markup styles
            markup_normal="",
            markup_focused='<span weight="bold">F {}</span>',
            markup_floating='<span foreground="#da8548">V {}</span>',
            markup_focused_floating='<span weight="bold" foreground="#ffaa00">VF {}</span>',
            markup_minimized='<span foreground="#ff6c6b">↓ {}</span>',

            max_title_width=200,
            padding_x=3,
            padding_y=2,
            margin_x=3,
            margin_y=4,
            spacing=2,

            parse_text=parse_task_name,
            window_name_location_offset=1,
            window_name_location="left",

            foreground=colors[1],
            background=None,

            highlight_method="text",
            border=colors[7],
            borderwidth=0,

            txt_minimized="↓  ",
            stretch=False,
        ),
    ]



def right_side_widgets():
    return [

        # CPU
        # chip(
        #     ewidget.CPU,
        #     name="w_cpu",
        #     _hide_on_chord=True,
        #     format="  {load_percent}%",
        #     fontsize=10,
        #     padding=11,
        #     foreground=colors[5],
        #     mouse_callbacks={
        #         "Button1": lambda: qtile.cmd_spawn(
        #             "env GTK_THEME=Adwaita:dark missioncenter"
        #         )
        #     },
        # ),
        #
        # # Memory
        # chip(
        #     ewidget.Memory,
        #     name="w_mem",
        #     format="{MemUsed: .0f}{mm}",
        #     fmt="🖥  {} ",
        #     fontsize=10,
        #     padding=11,
        #     foreground=colors[8],
        #     mouse_callbacks={
        #         "Button1": lambda: qtile.cmd_spawn(myFullScreenTerm + " -e btop")
        #     },
        # ),
        #
        # # Battery
        # chip(
        #     ewidget.Battery,
        #     name="w_battery",
        #     format="  {char}{percent:2.0%}",
        #     fontsize=10,
        #     padding=12,
        #     foreground=colors[6],
        #     low_foreground=colors[3],
        #     low_percentage=0.2,
        #     charge_char=" ↑ ",
        #     discharge_char=" ↓ ",
        #     full_char="✔ ",
        #     show_percentage=True,
        #     show_short_text=False,
        #     mouse_callbacks={
        #         "Button1": lambda: qtile.cmd_spawn(
        #             '/bin/sh -c \'notify-send "Battery Status" "$(acpi | cut -d "," -f 2-)"\''
        #         )
        #     },
        # ),
        #
        # # Disk
        # chip(
        #     ewidget.DF,
        #     name="w_disk",
        #     update_interval=60,
        #     partition="/",
        #     format="{uf}{m}",
        #     fmt="🖴  {}",
        #     fontsize=10,
        #     padding=11,
        #     visible_on_warn=False,
        #     foreground=colors[1],
        #     mouse_callbacks={"Button1": lambda: qtile.spawn("disk_notify")},
        # ),
        #
        # # Volume
        # chip(
        #     ewidget.Volume,
        #     name="w_volume",
        #     fmt="🕫  {}",
        #     padding=11,
        #     foreground=colors[7],
        # ),
        #
        # # Keyboard layout
        # chip(
        #     ewidget.KeyboardLayout,
        #     name="w_lang",
        #     configured_keyboards=["us", "ara", "tr", "de"],
        #     display_map={
        #         "us": "🇺🇸 EN",
        #         "ara": "🇸🇦 AR",
        #         "tr": "🇹🇷 TR",
        #         "de": "🇩🇪 DE",
        #     },
        #     fmt="{}",
        #     padding=11,
        #     foreground=colors[4],
        # ),


chip(
    ewidget.WidgetBox,
    name="tooltip_widgetbox",

    widgets=[],  # 👈 empty on purpose

    padding=11,
    fontsize=13,


text_closed="󰌶"   # dot-outline
,text_open="󰌵"     # dot-filled
,    close_button_location="right",
    start_opened=False,

    foreground=colors[1],

    mouse_callbacks={
        "Button1": lazy.function(toggle_onboarding),
    },
),


chip(
    ewidget.WidgetBox,
    name="system_widgetbox",
    fontsize=14,
    padding=10,
    close_button_location="right",
    start_opened=False,
    text_closed="󰖯"
    ,text_open="󰖰"
,
    widgets=[
        # CPU
        chip(
            ewidget.CPU,
            name="w_cpu",
            _hide_on_chord=True,
            format="  {load_percent}%",
            fontsize=10,
            padding=11,
            foreground=colors[5],
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(
                    "env GTK_THEME=Adwaita:dark missioncenter"
                )
            },
        ),

        # Memory
        chip(
            ewidget.Memory,
            name="w_mem",
            format="{MemUsed: .0f}{mm}",
            fmt="🖥  {} ",
            fontsize=10,
            padding=11,
            foreground=colors[8],
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(
                    myFullScreenTerm + " -e btop"
                )
            },
        ),



        # Battery
        chip(
            ewidget.Battery,
            name="w_battery",
            format="  {char}{percent:2.0%}",
            fontsize=10,
            padding=12,
            foreground=colors[6],
            low_foreground=colors[3],
            low_percentage=0.2,
            charge_char=" ↑ ",
            discharge_char=" ↓ ",
            full_char="✔ ",
            show_percentage=True,
            show_short_text=False,
            mouse_callbacks={
                "Button1": lambda: qtile.cmd_spawn(
                    '/bin/sh -c \'notify-send "Battery Status" "$(acpi | cut -d "," -f 2-)"\''
                )
            },
        ),
    ],

    foreground=colors[7],
)
,




chip(
    ewidget.WidgetBox,
    name="wallpaper_toggle",
    widgets=[],  # 👈 EMPTY on purpose
    padding=11,
    fontsize=12,

    text_closed="✖",
    text_open="󰍜",  # same icon (state is logical, not visual)

    close_button_location="right",
    start_opened=False,

    foreground=colors[8]  ,
    mouse_callbacks={
        "Button1": lazy.spawn(
            "sh -c 'xdotool key Alt_L+p sleep 0.05 key b'"
        )
    },
),
chip(
    ewidget.WidgetBox,
    name="2nd_system_widgetbox",
    fontsize=14,
    padding=10,
    close_button_location="right",
    start_opened=False,
text_closed="󰤂"
,text_open="󰁂"

# text_closed=""
# text_open=""
# text_closed="󰁂"
# text_open="󰁁"
# text_closed="󰍜"
# text_open="󰍝"
,
    widgets=[


        chip (              ewidget.CheckUpdates
              , padding =11
              ,  

              ),


        # Disk
        chip(
            ewidget.DF,
            name="w_disk",
            update_interval=60,
            partition="/",
            format="{uf}{m}",
            fmt="🖴  {}",
            fontsize=10,
            padding=11,
            visible_on_warn=False,
            foreground=colors[1],
            mouse_callbacks={"Button1": lambda: qtile.spawn("disk_notify")},
        ),

        # Volume
        chip(
            ewidget.Volume,
            name="w_volume",
            fmt="🕫  {}",
            padding=11,
            foreground=colors[7],
        ),

        # Keyboard layout
        chip(
            ewidget.KeyboardLayout,
            name="w_lang",
            configured_keyboards=["us", "ara", "tr", "de"],
            display_map={
                "us": "🇺🇸 EN",
                "ara": "🇸🇦 AR",
                "tr": "🇹🇷 TR",
                "de": "🇩🇪 DE",
            },
            fmt="{}",
            padding=11,
            foreground=colors[4],
        ),


        ]
,
foreground = colors[5],
        ),


        chip(
            ewidget.Chord,
            name="chord_chip",
            fmt=" {} ",
            padding=11,
            foreground=colors[2],
            background=None,
            name_transform=lambda name: {
                "Resize-Mode": "󰩨   RESIZE : H, J, N",
                "Rofi-Mode": "󰍉   ROFI : i , o , p , w , z , b , e , r , t , y , f , s , n , h ",
                "Media-Mode": "󰕾   MEDIA : J , K , P , M ",
                "Scratch-Mode": "󰈆   SCRATCH",
                "Draw-Mode": "󰏫   DRAW : w , c , z , r , v ",
                "Mouse-Mode": "󰍽   MOUSE : n , f , g , e , r , m ",
                "Lang-Switch": "   LANG : a , e , t , d ",
                "CheatSheet-Mode": "󰆍   CHEATSHEET : k , v , f ",
                "WallpaperPicker": "󰸉   WALLPAPERS : / , h , j , k ,l , R , ENTER ",
            }.get(name, name.upper()),
        ),

        # Clock
        chip(
            ewidget.Clock,
            format=" %a, %b %d - %H:%M",
            padding=11,
            foreground=colors[8],
            mouse_callbacks={"Button1": lambda: qtile.spawn("clock_popup")},
        ),


chip(
    ewidget.WidgetBox,
    fontsize=11,
    padding=11,

#     text_closed="󰍜",
#     text_open="|",
#
# text_closed="󰍜"   # tray / dots
# ,text_open="󰍛"     # dots expanded

# text_closed="󰁔"   # chevron down
# text_open="󰁅"     # chevron up

# text_closed="󰒓"   # system
# ,text_open="󰒓"     # keep same (no jump)

# text_closed="󰐙"   # expand
# ,text_open="󰐘"     # collapse
#
text_closed="△"   # three dots vertical
,text_open=""     # three dots horizontal


,    start_opened=False,
    close_button_location="right",

    widgets=[
        ewidget.Systray(
            icon_size=14,
            padding=6,
            hide_crash=True,
        ),
    ],

    foreground=colors[4],
),
    ]

#     ██╗  ██╗███████╗██╗   ██╗██████╗ ██╗███╗   ██╗██████╗ ██╗███╗   ██╗ ██████╗ ███████╗
#     ██║ ██╔╝██╔════╝╚██╗ ██╔╝██╔══██╗██║████╗  ██║██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝
#     █████╔╝ █████╗   ╚████╔╝ ██████╔╝██║██╔██╗ ██║██║  ██║██║██╔██╗ ██║██║  ███╗███████╗
#     ██╔═██╗ ██╔══╝    ╚██╔╝  ██╔══██╗██║██║╚██╗██║██║  ██║██║██║╚██╗██║██║   ██║╚════██║
#     ██║  ██╗███████╗   ██║   ██████╔╝██║██║ ╚████║██████╔╝██║██║ ╚████║╚██████╔╝███████║
#     ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝


keys = [

Key(
    [mod2],
    "grave",
    lazy.widget["system_widgetbox"].toggle(),
    desc="Toggle system widget box",
),
Key(
    [mod],
    "grave",
    lazy.widget["2nd_system_widgetbox"].toggle(),
    desc="Toggle system widget box",
),

   Key(
        [mod2, "shift"],
        "r",
   lazy.spawn(
        "sh -c 'xmodmap ~/.Xmodmap && notify-send \"Qtile\" \"Alt keymap reapplied\"'"
    ),
    desc="Reapply Alt keymap safely",
    ),
     # Key([mod2, "shift"],"d",lazy.function(toggle_collector),desc="Toggle Collector (Drop over like app) "),
    #---------------------
    # Key([mod], "s", lazy.spawn("bash -c \"notify-send '🎤 STT' 'Speak now…' && ~/.config/qtile/scripts/stt_script.sh\"")),
    # --- Open todo manager ---
    Key(
        [mod2, "shift"],
        "s",
        lazy.function(lambda qtile: toggle_or_spawn_sum(qtile, my2ndTerm, sum_file)),
        desc="Open or focus sum.md globally",
    ),
    # ---zen-mode---
    Key(
        [mod, "shift"], "z", lazy.hide_show_bar(position="top"), desc="Toggle Zen Mode"
    ),
    Key([mod2, "shift"], "k", lazy.spawn("rofi_keymaps"), desc="Show keymaps"),
    # --- Gromit-MPX controls ---
    # Key([mod2, "shift"], "w", lazy.spawn("gromit-mpx -t"), desc="Gromit: toggle draw"),
    # Key([mod2, "shift"], "z", lazy.spawn("gromit-mpx -z"), desc="Gromit: undo"),
    # # Key([mod2, "shift"], "r", lazy.spawn("gromit-mpx -y"), desc="Gromit: redo"),
    # Key([mod2, "shift"], "c", lazy.spawn("gromit-mpx -c"), desc="Gromit: clear"),
    # Key(
    #     [mod2, "shift"],
    #     "v",
    #     lazy.spawn("gromit-mpx -v"),
    #     desc="Gromit: toggle visibility",
    # ),
    # ---today & week: plans-todos popup---
    Key(
        [mod2],
        "p",
        lazy.spawn("clock_popup"),
        desc="clock popup (today & week: plans-todos)",
    ),
    # ---volume---
    Key(
        [mod2],
        "bracketleft",
        lazy.function(lambda q: volume_change(-5)),
        desc="volume down",
    ),
    Key(
        [mod2],
        "bracketright",
        lazy.function(lambda q: volume_change(5)),
        desc="volume up",
    ),
    Key([mod2], "minus", lazy.function(lambda q: toggle_mute()), desc="mute volume"),
    # ---close notifications---
    Key([mod2], "n", lazy.spawn("dunstctl close")),
    # ---hints start---
    # Key([mod2], "f", lazy.spawn("hints -m hint")),
    # Key([mod2], "s", lazy.spawn("hints -m scroll")),
     # Key([mod2], "f", lazy.spawn("warpd --hint")),
     # Key([mod2], "s", lazy.spawn("warpd --grid")),
    # NOTE:  a good tool for hints and navigation is "hints"
    # ```
    #  pipx install git+https://github.com/AlfredoSequeida/hints.git
    #  "Installing Wayland/X11-specific dependencies for 'hints'...""
    #  yay -S --needed --noconfirm libwnck3
    #
    #   NOTE: "Configuring accessibility environment variables in /etc/environment..."
    #       sudo tee -a /etc/environment >/dev/null <<EOF
    #       # Required for 'hints'
    #       ACCESSIBILITY_ENABLED=1
    #       QT_ACCESSIBILITY=1
    #       QT_LINUX_ACCESSIBILITY_ALWAYS_ON=1
    #       EOF
    # ```
    # "Enabling and starting hintsd and accessibility DBus service..."
    # systemctl --user enable --now hintsd.service
    # systemctl --user restart at-spi-dbus-bus.service
    #
    #  WARN: important to work:
    #   systemctl --user enable --now hintsd.service
    #   systemctl --user restart at-spi-dbus-bus.service
    # "NOTE: To customize hints configuration, edit:"
    # NOTE: copy the hintsConfig form `~/.dotfiles/installScript/hintsConfig.py`to this:
    #  `~/.local/share/pipx/venvs/hints/lib/python*/site-packages hints/constants.py`
    #
    # ---hints end---
    # ---gptscript-inline---
    # NOTE:  not working ,,,,
    # Key(
    #     [mod],
    #     "g",
    #     lazy.spawn(
    #         "fish -c 'xdotool key ctrl+a ctrl+x; ~/.config/GptScript/gpt_inline_auto.py'"
    #     ),
    #     desc="gpt inline script (/gpt ,/mail, /sum)",
    # ),
    # ---toggle obsidian session---
    Key(
        [mod2, "shift"],
        "o",
        toggle_obsidian(),
        desc="Open Obsidian to draw (u should have exclidraw in obsidian)",
    ),
    # ---toggle telegram  session---
    Key([mod2, "shift"], "t", toggle_telegram(), desc="toggle telegram session"),
    # ---toggle sum.md nvim session---
    # Key([mod2, "shift"], "s",toggle_sum(),desc="toggle sum.md nvim session"),
    # ---toggle anki app session---
    Key([mod2, "shift"], "a", toggle_anki(), desc="toggle anki app session"),
    # ---toggle qutebrowser app session---
    Key([mod], "v", toggle_qutebrowser(), desc="toggle qutebrowser session (video+others"),
    # --- toggle terminal app session ---
    Key([mod], "n", toggle_terminal(), desc="toggle terminal session"),
    # --- toggle file manager app session ---
    Key([mod], "m", toggle_file_manager(), desc="toggle filemanager session"),
    # Key([mod2,"shift"], "n", toggle_alacritty(),desc="toggle alacritty session"),
    # --- toggle google chrome app session ---
    # NOTE: not needed anymore
    # Key(
    #     [mod2, "shift"],
    #     "b",
    #     toggle_google_chrome(),
    #     desc="toggle google chrome session",
    # ),

    # --- toggle brave app session ---
    Key([mod], "b", toggle_brave(), desc="toggle brave session(browsing)"),
    # ---keyboardlayout---
    # Key(
    #     [mod2],
    #     "space",
    #     lazy.widget["keyboardlayout"].next_keyboard(),
    #     desc="Switch keyboard layout",
    # ),
    # Key(
    #     [mod2, "shift"],
    #     "space",
    #     lazy.function(kb_prev),
    #     desc="Previous keyboard layout",
    # ),
    # ---vimium like scroll motions---
    # NOTE:  not  the gg and G  commands no need ...
    # Key(
    #     [mod2, "shift"],
    #     "g",
    #     lazy.spawn("xdotool click --repeat 500 --delay 1 5"),
    #     desc="scroll down fast",
    # ),
    # Key([mod2], "g", lazy.spawn("xdotool click --repeat 500 --delay 1 4"), desc="scroll up fast"),
    # Key(
    #     [mod2],
    #     "j",
    #     lazy.spawn("xdotool click --repeat 4 --delay 1 5"),
    #     desc="scroll down x4",
    # ),
    # Key(
    #     [mod2],
    #     "k",
    #     lazy.spawn("xdotool click --repeat 4 --delay 1 4"),
    #     desc="scroll up x4",
    # ),
    # Key(
    #     [mod2],
    #     "h",
    #     lazy.spawn("xdotool click --repeat 4 --delay 1 6"),
    #     desc="scroll left x4",
    # ),
    # Key(
    #     [mod2],
    #     "l",
    #     lazy.spawn("xdotool click --repeat 4 --delay 1 7"),
    #     desc="scroll right x4",
    # ),
    # ---left-middle-right click---
    # Key([mod2], "m", lazy.spawn("xdotool click 1"), desc="left click"),
    # Key([mod2], "comma", lazy.spawn("xdotool click 2"),desc="middle click"),
    # Key([mod2], "period", lazy.spawn("xdotool click 3"), desc=" right click"),
    # ---youtube like PIP mpv---
    # Key(
    #     [mod],
    #     "slash",
    #     lazy.function(mpv_manager.toggle_pip_mode),
    #     desc="Toggle MPV PIP mode",
    # ),
    # ---open termianl---
    Key([mod], "Return", lazy.spawn(myTerm), desc="Terminal"),
    # ---open rofi---
    Key(
        [mod, "shift"],
        "Return",
        lazy.spawn("rofi -show drun -show-icons"),
        desc="Run Launcher",
    ),
    # ---open browsers---
    # Key([mod], "b", lazy.spawn(myBrowser4), desc="Web browser"),
    # Key([mod, "shift"],"b", lazy.spawn(myBrowser3), desc="Web browser3"),
    # ---toggle between layouts---
    Key([mod], "Tab", lazy.next_layout(), desc="Toggle between layouts"),
    # ---kill focused window---
    Key([mod, "shift"], "c", lazy.window.kill(), desc="Kill focused window"),
    # ---reload the qtile config with notification and without---
    # Key([mod, "shift"], "r", lazy.reload_config(), desc="Reload the config"),
    Key(
        [mod, "shift"],
        "r",
        lazy.function(
            lambda qtile: (
                qtile.reload_config(),
                qtile.spawn(
                    "notify-send -u critical -i dialog-ok-symbolic  'success' ' Qtile Config : Successfully reloaded!'"
                ),
            )
        ),
        desc="Reload the config",
    ),
    # --- logout menu ---
    Key([mod, "shift"], "q", lazy.spawn("dm-logout -r"), desc="Logout menu"),
    # --- spawn a command using a prompt widget ---
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    # Switch between windows
    # Some layouts like 'monadtall' only need to use j/k to move
    # through the stack, but other layouts like 'columns' will
    # require all four directions h/j/k/l to move around.
    # --- Move focus to left, right, down, up ---
    Key([mod], "h", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "l", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "j", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "k", lazy.layout.up(), desc="Move focus up"),
    # Key([mod], "space", lazy.layout.next(), desc="Move window focus to other window"),
    # Move windows between left/right columns or move up/down in current stack.
    # Moving out of range in Columns layout will create new column.
    # --- Move window to the left,right,down,up in treetab ---
    Key(
        [mod, "shift"],
        "h",
        lazy.layout.shuffle_left(),
        lazy.layout.move_left().when(layout=["treetab"]),
        desc="Move window to the left/move tab left in treetab",
    ),
    Key(
        [mod, "shift"],
        "l",
        lazy.layout.shuffle_right(),
        lazy.layout.move_right().when(layout=["treetab"]),
        desc="Move window to the right/move tab right in treetab",
    ),
    Key(
        [mod, "shift"],
        "j",
        lazy.layout.shuffle_down(),
        lazy.layout.section_down().when(layout=["treetab"]),
        desc="Move window down/move down a section in treetab",
    ),
    Key(
        [mod, "shift"],
        "k",
        lazy.layout.shuffle_up(),
        lazy.layout.section_up().when(layout=["treetab"]),
        desc="Move window downup/move up a section in treetab",
    ),
    # Toggle between split and unsplit sides of stack.
    # Split = all windows displayed
    # Unsplit = 1 window displayed, like Max layout, but still with
    # multiple stack panes
    # --- Toggle between split and unsplit sides of stack ---
    Key(
        [mod, "shift"],
        "space",
        lazy.layout.toggle_split(),
        desc="Toggle between split and unsplit sides of stack",
    ),
    # Treetab prompt
    # --- Prompt to add new section in treetab ---
    Key(
        [mod, "shift"],
        "a",
        add_treetab_section,
        desc="Prompt to add new section in treetab",
    ),
    # Grow/shrink windows left/right.
    # This is mainly for the 'monadtall' and 'monadwide' layouts
    # although it does also work in the 'bsp' and 'columns' layouts.
    # --- Grow window to the left,right ---
    Key(
        [mod],
        "equal",
        lazy.layout.grow_left().when(layout=["bsp", "columns"]),
        lazy.layout.grow().when(layout=["monadtall", "monadwide"]),
        desc="Grow window to the left",
    ),
    Key(
        [mod],
        "minus",
        lazy.layout.grow_right().when(layout=["bsp", "columns"]),
        lazy.layout.shrink().when(layout=["monadtall", "monadwide"]),
        desc="Grow window to the left",
    ),
    # Grow windows up, down, left, right.  Only works in certain layouts.
    # Works in 'bsp' and 'columns' layout.
    # --- Grow window up, down, left, right columns layout ---
    Key([mod, "control"], "h", lazy.layout.grow_left(), desc="Grow window to the left"),
    Key(
        [mod, "control"], "l", lazy.layout.grow_right(), desc="Grow window to the right"
    ),
    Key([mod, "control"], "j", lazy.layout.grow_down(), desc="Grow window down"),
    Key([mod, "control"], "k", lazy.layout.grow_up(), desc="Grow window up"),
    # --- Reset all window sizes ---
    # Key([mod], "n", lazy.layout.normalize(), desc="Reset all window sizes"),
    # --- Toggle between min and max sizes ---
    Key([mod], "x", lazy.layout.maximize(), desc="Toggle between min and max sizes"),
    # --- toggle floating ---
    Key([mod], "t", lazy.window.toggle_floating(), desc="toggle floating"),
    # --- toggle fullscreen ---
    Key([mod], "f", lazy.window.toggle_fullscreen(), desc="toggle fullscreen"),
    # --- Toggle hide/show all windows on current group ---
    # Key(
    #     [mod, "shift"],
    #     "m",
    #     minimize_all(),
    #     desc="Toggle hide/show all windows on current group",
    # ),
    # Switch focus of monitors
    # --- Move focus to next/prev monitor ---
    Key([mod], "period", lazy.next_screen(), desc="Move focus to next monitor"),
    Key([mod], "comma", lazy.prev_screen(), desc="Move focus to prev monitor"),
    # --- "P" with letter to do actions
    KeyChord(
        [mod],
        "p",
        [
            #
            # Key([], "a", lazy.spawn("dm-sounds -r"), desc='Choose ambient sound'),
            # Key([], "o", lazy.spawn("emacsclient --eval '(emacs-everywhere)'"), desc='Open emacs edit field'),
            # Key([], "c", lazy.spawn("dtos-colorscheme"), desc='Choose color scheme'),
            # Key([], "e", lazy.spawn("dm-confedit"), desc='Choose a config file to edit'),
            # Key([], "o", lazy.spawn("dm-bookman -r"), desc='Browser bookmarks'),
            # Key([], "p", lazy.spawn('passmenu -p "Pass: "'), desc="pass menu"),
            # Key([], "u", lazy.spawn("dm-music -r"), desc='Toggle music mpc/mpd')
            # Key([], "r", lazy.spawn("dm-record -r"), desc='record'),
            #
            # --- Translate text ---
            # Key([], "e", lazy.spawn("rofi_translator"), desc='Translate text'),
            Key(
                [],
                "e",
                lazy.spawn(
                    "python3 /home/ati/.config/rofi_translator/wordreference.py"
                ),
                desc="Translate text",
            ),
            # --- add anki note ---
            Key([], "a", lazy.spawn("rofi_anki"), desc="add anki note"),
            # --- Close all notifications ---
            Key(
                [],
                "x",
                lazy.spawn("dunstctl close-all"),
                desc="Close all notifications",
            ),
            # --- List all dmscripts ---
            Key([], "h", lazy.spawn("dm-hub -r"), desc="List all dmscripts"),
            # --- Choose a config file to edit ---
            Key(
                [], "f", lazy.spawn("dm-confedit"), desc="Choose a config file to edit"
            ),
            # --- choose shared link-preview ---
            Key([], "z", lazy.spawn("rofi_shared"), desc="shared link-preview"),
            # --- Set background ---
            # Key([], "b", lazy.spawn("dm-setbg -r"), desc="Set background"),
KeyChord(
        [], "b",
    [

# NAVIGATE LEFT / RIGHT
            Key([], "h", lazy.function(lambda q: WallpaperPopup.move(0, -1))), 
            Key([], "l", lazy.function(lambda q: WallpaperPopup.move(0, 1))),
            Key([], "R", lazy.function(lambda q: WallpaperPopup.jump_to_random())), # <--- NEW: Random
        Key([], "slash", lazy.function(lambda q: WallpaperPopup.fuzzy_search_rofi())), # <--- NEW: Search (/)
            # NAVIGATE DOWN / UP
            Key([], "j", lazy.function(lambda q: WallpaperPopup.move(1, 0))),
            Key([], "k", lazy.function(lambda q: WallpaperPopup.move(-1, 0))),
            
            # ACTIONS
            Key([], "Return", lazy.function(lambda q: WallpaperPopup.apply(q))),
            Key([], "q", lazy.function(lambda q: WallpaperPopup.close_wallpaper_picker()) and lazy.ungrab_chord()),
            Key([], "Escape", lazy.function(lambda q: WallpaperPopup.close_wallpaper_picker())),


    ],

        mode=True,
        name="WallpaperPicker",
        desc="Wallpaper picker mode",
    ),
            # --- show documents ---
            Key([], "d", lazy.spawn("dm-documents -r"), desc="Show documents"),
            # make a screenshot of today's todos
            Key(
                [],
                "c",
                lazy.spawn("fish -c 'screenshot_todos_today'"),
                desc="Screenshot today's todos",
            ),
            # --- Take a screenshot v2 of dm-maim ---
            Key(
                [], "i", lazy.spawn("dm-satty"), desc="Take a screenshot v2 of dm-maim"
            ),
            # --- Kill processes ---
            Key([], "k", lazy.spawn("rofi-kill"), desc="Kill processes "),
            # --- View manpages ---
            Key([], "m", lazy.spawn("dm-man -r"), desc="View manpages"),
            # --- Store and copy notes ---
            Key([], "n", lazy.spawn("dm-note -r"), desc="Store and copy notes"),
            # --- rofi password menu ---
            Key([], "p", lazy.spawn("rofi-pass"), desc="Password menu"),
            # --- youtube menu ---
            Key(
                [],
                "y",
                lazy.spawn("dm-youtube -r"),
                desc="youtube menu",
            ),
            # --- logout menu ---
            Key([], "q", lazy.spawn("dm-logout -r"), desc="Logout menu"),
            # --- record  Version2 ---
            Key([], "r", lazy.spawn("dm-recordV2"), desc="record"),
            # --- Search various engines ---
            # Key([], "s", lazy.spawn("dm-websearch -r"), desc='Search various engines'),
            # ---  Spell check menu ---
            Key([], "s", lazy.spawn("dm-spellcheck -r"), desc="Spell check menu"),
            # --- Search wifi ---
            # Key([], "w", lazy.spawn("dm-wifi -r"), desc="Search wifi"),
            # --- Search weather ---
             Key([], "w", lazy.spawn("dm-weather -r"), desc="Search weather"),
            # --- Open todo manager ---
            Key([], "t", lazy.spawn("rofi_todo"), desc="Open todo manager"),
            # --- screen light ---
            Key([], "l", lazy.spawn("rofi_light"), desc="screen light"),
            # --- iLovePDF style image,pdf converter ---
            # TODO : can be replaced with another thing late
            # Key([],"u",lazy.spawn("rofi_ilovepdf"),desc="Ultimate converter ( iLovePDF style image,pdf )",),
            #

            # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
            *group_keys(),
        ],
            name= "Rofi-Mode"
            , swallow=True,
    ),



KeyChord(
            # done
    [mod],
    "slash",
    [
        Key(["shift"], "j", lazy.function(lambda q: volume_change(-5))),
        Key(["shift"], "k", lazy.function(lambda q: volume_change(5))),
        Key(["shift"], "m", lazy.function(lambda q: toggle_mute())),

        Key(["shift"], "p", lazy.function(mpv_manager.toggle_pip_mode)),

        # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
        *group_keys(),
        Key([], "q", lazy.ungrab_chord()),
        Key([], "Escape", lazy.ungrab_chord()),
    ],
    name="Media-Mode",
    mode=True,
    swallow=True,
),

KeyChord(
    [mod2],
    "r",
    [
        # # BSP / Columns (directional)
        # Key(
        #     [],
        #     "h",
        #     lazy.layout.grow_left().when(layout=["bsp", "columns"]),
        # ),
        # Key(
        #     [],
        #     "l",
        #     lazy.layout.grow_right().when(layout=["bsp", "columns"]),
        # ),
        # Key(
        #     [],
        #     "j",
        #     lazy.layout.grow_down().when(layout=["bsp", "columns"]),
        # ),
        # Key(
        #     [],
        #     "k",
        #     lazy.layout.grow_up().when(layout=["bsp", "columns"]),
        # ),

        # MonadTall / MonadWide (ratio-based)
        Key(
            ["shift"],
            "h",
            lazy.layout.shrink().when(layout=["monadtall", "monadwide"]),
        ),
        Key(
            ["shift"],
            "l",
            lazy.layout.grow().when(layout=["monadtall", "monadwide"]),
        ),

        # Common
        Key(["shift"], "n", lazy.layout.reset()),

        # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
        *group_keys(),
        Key([], "q", lazy.ungrab_chord()),
        Key([], "Escape", lazy.ungrab_chord()),
    ],
    name="Resize-Mode",

    mode=True,  
    swallow=True,
)
,

# NOTE: it is working but i think it is not perfect using normal : win+12334,890 is better  i think
# BUT I WILL BE USING IT FOR FUTURE SECONDARY APPS (NOT FOR PRIMARY APPS LIKE CHATGPT,WHATSAPP..etc)
# Slack , OSB, Discord zoom , .....etc
# KeyChord( 
#     [mod2],
#     "s",
#     [
#         Key([], "1", lazy.group["scratchpad"].dropdown_toggle("term1")),
#         Key([], "2", lazy.group["scratchpad"].dropdown_toggle("term2")),
#         Key([], "3", lazy.group["scratchpad"].dropdown_toggle("mixer")),
#         Key([], "4", lazy.group["scratchpad"].dropdown_toggle("2ndScreen")),
#         Key([], "5", lazy.group["scratchpad"].dropdown_toggle("calc")),
#         Key([], "8", lazy.group["scratchpad"].dropdown_toggle("whats")),
#         Key([], "9", lazy.group["scratchpad"].dropdown_toggle("deepseek")),
#         Key([], "0", lazy.group["scratchpad"].dropdown_toggle("chatgpt")),
#
#
#
#         Key([], "q", lazy.ungrab_chord()),
#
#         Key([], "Escape", lazy.ungrab_chord()),
#     ],
#     name="Scratch-Mode",
#     mode=True,
#     swallow=True
# ),

KeyChord( 
    [mod2, "shift"],
    "w",
    [
        Key([], "w", lazy.spawn("gromit-mpx -t"), desc="Gromit: toggle draw"),
        Key([], "c", lazy.spawn("gromit-mpx -c"), desc="Gromit: clear "),
        Key([], "z", lazy.spawn("gromit-mpx -z"), desc="Gromit: undo "),
        Key([], "r", lazy.spawn("gromit-mpx -y"), desc="Gromit: redo "),
        Key([], "v", lazy.spawn("gromit-mpx -v"), desc="Gromit: toggle visibility"),

        # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
        *group_keys(),
        Key([], "q", lazy.ungrab_chord()),
        Key([], "Escape", lazy.ungrab_chord()),

    ],
    name="Draw-Mode",
    mode=True,
    swallow=True,
),
KeyChord(
    [mod2],
    "f",
    [
        Key([], "f", lazy.spawn("warpd --hint")),
        Key([], "n", lazy.spawn("warpd --normal")),
        # Key([], "g", lazy.spawn("warpd --grid")),
        # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
        *group_keys(),
        Key([], "q", lazy.ungrab_chord()),
        Key([], "Escape", lazy.ungrab_chord()),


        # fast scroll (gg / G equivalents)
        Key([], "t",
            lazy.spawn("xdotool click --repeat 150 --delay 2 4"),
            desc="scroll up fast"),
        Key([], "b",
            lazy.spawn("xdotool click --repeat 150 --delay 2 5"),
            desc="scroll down fast"),
    ],
    name="Mouse-Mode",
    mode=True,
    swallow=True,
)
,

KeyChord(
    [mod2],
    "space",
    [
        Key([], 26, set_kb("us")),   # e
        Key([], 38, set_kb("ara")),  # a
        Key([], 28, set_kb("tr")),   # t
        Key([], 40, set_kb("de")),   # d

        Key([], "Escape", lazy.ungrab_chord()),
        Key([], "q", lazy.ungrab_chord()),
    ],
    name="Lang-Switch",
    mode=True,
    swallow=True,
)


,KeyChord( 
    [mod2, "shift"],
    "k",
    [
        Key(
        [],
        "k",
        lazy.function(toggle_cheatsheet),
        desc="Show cheatsheet",
        ),
        Key([],"v",lazy.function(toggle_vim_cheatsheet),desc="Test popup widget scrolling",),
        Key([],"f",lazy.function(toggle_fish_kitty_cheatsheet),desc="Test popup widget scrolling",),

        # NOTE:  workspace switching inside the modes ("by using 1,2,3,4,5,6,7,8,9,0")
        *group_keys(),
        # Key([], "q", lazy.ungrab_chord()),
Key(
    [],
    "q",
    lazy.function(exit_cheatsheet_mode),
    desc="Exit cheatsheet mode",
),

    ],
    name="CheatSheet-Mode",
    mode=True,
    swallow=True,
),

#   KeyChord(
#         ["mod4"], "w",
#     [
#
# # NAVIGATE LEFT / RIGHT
#             Key([], "h", lazy.function(lambda q: WallpaperPopup.move(0, -1))), 
#             Key([], "l", lazy.function(lambda q: WallpaperPopup.move(0, 1))),
#             Key([], "R", lazy.function(lambda q: WallpaperPopup.jump_to_random())), # <--- NEW: Random
#         Key([], "slash", lazy.function(lambda q: WallpaperPopup.fuzzy_search_rofi())), # <--- NEW: Search (/)
#             # NAVIGATE DOWN / UP
#             Key([], "j", lazy.function(lambda q: WallpaperPopup.move(1, 0))),
#             Key([], "k", lazy.function(lambda q: WallpaperPopup.move(-1, 0))),
#             
#             # ACTIONS
#             Key([], "Return", lazy.function(lambda q: WallpaperPopup.apply(q))),
#             Key([], "q", lazy.function(lambda q: WallpaperPopup.close_wallpaper_picker())),
#             Key([], "Escape", lazy.function(lambda q: WallpaperPopup.close_wallpaper_picker())),
#
#
#     ],
#
#         mode=True,
#         name="WallpaperPicker",
#         desc="Wallpaper picker mode",
#     )



]

#  ██████╗ ██████╗  ██████╗ ██╗   ██╗██████╗ ███████╗
# ██╔════╝ ██╔══██╗██╔═══██╗██║   ██║██╔══██╗██╔════╝
# ██║  ███╗██████╔╝██║   ██║██║   ██║██████╔╝███████╗
# ██║   ██║██╔══██╗██║   ██║██║   ██║██╔═══╝ ╚════██║
# ╚██████╔╝██║  ██║╚██████╔╝╚██████╔╝██║     ███████║
#  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚══════╝






# NOTE: some icons may u need
# group_labels = ["", "", "👁", "", "", "", "✀", "🗯", "", "⎙"]
# group_labels = [
#     "",  # Terminal
#     "",  # Browser (Firefox)
#     "",  # Internet / Global
#     "",  # VSCode / Dev
#     "",  # Code
#     "",  # Files
#     "",  # Folder (alternative)
#     "",  # Folder-open
#     "",  # Layouts
#     "",  # Lab / Experiments
#     "",  # Slack / Chat
#     "",  # Telegram
#     "",  # Messages
#     "",  # Discord
#     "",  # Media / Video
#     "",  # Spotify
#     "🎵",  # Music
#     "🎮",  # Gaming
#     "🎨",  # Design / GFX
#     "",  # Images
#     "📸",  # Photography
#     "✀",  # Editing / Cut
#     "🧠",  # Study / Research
#     "📚",  # Reading
#     "💼",  # Work
#     "⚙️",  # System / Tools
#     "🧰",  # Toolbox
#     "📜",  # Docs / Writing
#     "🌐",  # Web general
#     "🌙",  # Chill / Night
# ]

groups = [
    Group(
        "1",
        label="",
        matches=[
            Match(wm_class="ticktick"),
        ],
        layout="monadtall",
    ),
    Group(
        "2",
        label="",
        matches=[
            Match(wm_class="qutebrowser"),
            Match(wm_class="zen-browser"),
            Match(wm_class="vlc"),
            Match(wm_class="ops"),
            Match(wm_class="firefox"),
        ],
        layout="max",
    ),
    Group(
        "3",
        label="",
        matches=[Match(wm_class="org.gnome.Nautilus"), Match(wm_class="pcmanfm")],
        layout="monadtall",
    ),
    Group(
        "4",
        label="",
        matches=[
            Match(wm_class="code"),
            Match(wm_class="dev.zed.Zed"),
            Match(wm_class="kitty"),
            # Match(
            #     wm_class="alacritty",
            #     title=re.compile(r"^(?!.*(nvimsum|edit-field)).*$"),
            # ),
            Match(wm_class="cursor"),
        ],
        layout="monadtall",
    ),
    Group(
        "5",
        label="",
        matches=[
             Match(wm_class="brave"),
             Match(wm_class="brave-browser"),

            ],
        layout="max",
    ),
    Group(
        "6", label="👁", matches=[Match(wm_class="google-chrome")], layout="monadtall"
    ),
    Group("7", label="7", layout="monadtall"),
    Group("8", label="8", layout="monadtall"),
    Group(
        "S",
        layout="max",
        matches=[
            Match(wm_class="Anki"),
            Match(wm_class="obsidian"),
            Match(title="nvimsum"),
        ],
    ),
    Group(
        "9",
        label="",
        matches=[
            Match(wm_class="thunderbird"),
            Match(wm_class="TelegramDesktop"),
            # Match(wm_class="whatsdesk"),
            Match(wm_class="discord"),
        ],
    ),
]



for i in groups:
    if i.name == "S":
        continue  # Disable mod+s and mod+shift+s for the "S" group

    keys.extend(
        [
            # mod + group letter = switch to group
            Key(
                [mod],
                i.name,
                lazy.group[i.name].toscreen(),
                desc="Switch to group {}".format(i.name),
            ),
            Key(
                [mod, "shift"],
                i.name,
                lazy.window.togroup(i.name),
                desc="Move focused window to group {}".format(i.name),
            ),
        ]
    )

# ███████╗ ██████╗██████╗  █████╗ ████████╗ ██████╗██╗  ██╗██████╗  █████╗ ██████╗ ███████╗
# ██╔════╝██╔════╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██║  ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
# ███████╗██║     ██████╔╝███████║   ██║   ██║     ███████║██████╔╝███████║██║  ██║███████╗
# ╚════██║██║     ██╔══██╗██╔══██║   ██║   ██║     ██╔══██║██╔═══╝ ██╔══██║██║  ██║╚════██║
# ███████║╚██████╗██║  ██║██║  ██║   ██║   ╚██████╗██║  ██║██║     ██║  ██║██████╔╝███████║
# ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝╚═════╝ ╚══════╝


### IMP: the width, height and x y opacity are just for the positioning it vary , you can change it as you want

groups.append(
    ScratchPad(
        "scratchpad",
        [
            DropDown(
                "term1",
                "kitty",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "2ndScreen",
                "arandr",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "term2",
                "kitty",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.1,
                opacity=1,
            ),
            DropDown(
                "mixer",
                "env GTK_THEME=Adwaita:dark pavucontrol",
                width=0.4,
                height=0.6,
                x=0.3,
                y=0.1,
                opacity=1,
            ),

            DropDown(
                "calc",
                "env GTK_THEME=Adwaita:dark qalculate-gtk",
                width=0.6,
                height=0.6,
                x=0.2,
                y=0.1,
                opacity=1,
            ),
                DropDown(
                "collector",
                "flatpak run it.mijorus.collector",
                match=Match(wm_class="collector"),
                x=0.725,
                y=0.67,
                opacity=1.0,
                on_focus_lost_hide=False,
                ),
            # DropDown(
            #     "note",
            #     "env GTK_THEME=Adwaita:dark notorious",
            #     width=0.3,
            #     height=0.6,
            #     x=0.0,
            #     y=0.01,
            #     opacity=1,
            #     on_focus_lost_hide=False,
            # ),
            ### for chatgpt & deepseek & whatsapp i decided to use brave browser by using one browser engine for all, i  used separate profiles for
            ### each browser and it will be in the ~/.config/qtile/brave-profiles
            ### by using some flags i can disable some features like sync, background networking, component update, etc which will make it faster and reduce
            ### the memory usage ,cpu usage and battery usage
            # TODO: chage the /home/ati/.config to ~/.config
            # TODO: add the brave-profiles to the .gitignore
            DropDown(
                "chatgpt",
                "brave --user-data-dir=/home/ati/.config/qtile/brave-profiles/chatgpt "
                "--class=sp-chatgpt --name=sp-chatgpt "
                "--app=https://chat.openai.com "
                "--disable-background-networking "
                "--disable-component-update "
                "--disable-breakpad "
                "--disable-sync "
                "--no-first-run ",
                match=Match(wm_class="sp-chatgpt"),
                width=0.7,
                height=0.8,
                x=0.15,
                y=0.1,
                opacity=1,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "deepseek",
                "brave --user-data-dir=/home/ati/.config/qtile/brave-profiles/deepseek "
                "--class=sp-deepseek --name=sp-deepseek --app=https://chat.deepseek.com "
                "--disable-background-networking "
                "--disable-component-update "
                "--disable-breakpad "
                "--disable-sync "
                "--no-first-run",
                match=Match(wm_class="sp-deepseek"),
                width=0.7,
                height=0.8,
                x=0.15,
                y=0.1,
                opacity=0.95,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "whats",
                "brave --user-data-dir=/home/ati/.config/qtile/brave-profiles/whatsapp "
                "--class=sp-whatsapp --name=sp-whatsapp "
                "--app=https://web.whatsapp.com "
                "--disable-background-networking "
                "--disable-component-update "
                "--disable-breakpad "
                "--disable-sync "
                "--no-first-run ",
                match=Match(wm_class="sp-whatsapp"),
                width=0.7,
                height=0.8,
                x=0.15,
                y=0.1,
                opacity=0.95,
                on_focus_lost_hide=False,
            ),
        ],
    )
)

keys.extend(
    [
        Key(["mod4"], "1", lazy.group["scratchpad"].dropdown_toggle("term1")),
        Key(["mod4"], "2", lazy.group["scratchpad"].dropdown_toggle("term2")),
        Key(["mod4"], "3", lazy.group["scratchpad"].dropdown_toggle("mixer")),
        Key(["mod4"], "4", lazy.group["scratchpad"].dropdown_toggle("2ndScreen")),
        Key(["mod4"], "5", lazy.group["scratchpad"].dropdown_toggle("calc")),
        Key(["mod4"], "8", lazy.group["scratchpad"].dropdown_toggle("whats")),
        Key(["mod4"], "9", lazy.group["scratchpad"].dropdown_toggle("deepseek")),
        Key(["mod4"], "0", lazy.group["scratchpad"].dropdown_toggle("chatgpt")),
        Key(["mod4","shift"], "d", lazy.group["scratchpad"].dropdown_toggle("collector")),
    ]
)
### COLORSCHEME ###
# Colors are defined in a separate 'colors.py' file.
# There 10 colorschemes available to choose from:
#
# colors = colors.DoomOne
# colors = colors.Dracula
# colors = colors.GruvboxDark
# colors = colors.MonokaiPro
# colors = colors.Nord
# colors = colors.OceanicNext
# colors = colors.Palenight
# colors = colors.SolarizedDark
# colors = colors.SolarizedLight
# colors = colors.TomorrowNight
#
# It is best not manually change the colorscheme; instead run 'dtos-colorscheme'
# which is set to 'MOD + p c'


#  ██████╗██╗  ██╗██╗██████╗     ███████╗████████╗██╗   ██╗██╗     ███████╗
# ██╔════╝██║  ██║██║██╔══██╗    ██╔════╝╚══██╔══╝╚██╗ ██╔╝██║     ██╔════╝
# ██║     ███████║██║██████╔╝    ███████╗   ██║    ╚████╔╝ ██║     █████╗
# ██║     ██╔══██║██║██╔═══╝     ╚════██║   ██║     ╚██╔╝  ██║     ██╔══╝
# ╚██████╗██║  ██║██║██║         ███████║   ██║      ██║   ███████╗███████╗
#  ╚═════╝╚═╝  ╚═╝╚═╝╚═╝         ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚══════╝
#
# (logo) ( monadtall ) | nvim config.py ~/c/qtile     CPU:54%  MEM:3445M  DISK:84%  SSD:86G  VOL:49%  LANG:EN  Sun,Nov 02 00:54 (systray)


def parse_task_name(text):
    REMOVE = [
        # Browsers
        " - Mozilla Firefox",
        " - Firefox",
        " - Chromium",
        " - Google Chrome",
        " - Brave",
        " - Microsoft Edge",
        " - Vivaldi",
        " - Opera",

        # LibreOffice
        " — LibreOffice Writer",
        " — LibreOffice Calc",
        " — LibreOffice Impress",

        # Editors / IDEs
        " - Visual Studio Code",
        " - Code",
        " - VS Code",
        " — Visual Studio Code",
        " - Sublime Text",
        " - Atom",
        " - IntelliJ IDEA",
        " - PyCharm",

        # Terminals
        " — Alacritty",
        " — Kitty",
        " — WezTerm",
        " — GNOME Terminal",
        " - Konsole",

        # Media
        " - VLC media player",
        " - MPV",
        " — Spotify",
        " - YouTube",

        # System / DE noise
        "Built-in Widgets —",
        " — Settings",
        " — Preferences",
        " — System Settings",

        # Generic separators
        " — ",
        " - ",
    ]

    for s in REMOVE:
        text = text.replace(s, "")

    return text

def chip(WCls, chip_color=None, **kwargs):

    hide = kwargs.pop("_hide_on_chord", False)
    deco = [
        RectDecoration(
            colour=chip_color if chip_color is not None else DEFAULT_CHIP_COLOR,
            radius=11,
            filled=True,
            padding_x=3,
            padding_y=2,
            # NOTE:  if u want just a border, u can use this
            # filled=False,
            # line_width=1.5,
            # line_colour= colorsW[8]
        )
    ]

    if "decorations" in kwargs and kwargs["decorations"]:
        kwargs["decorations"] = list(kwargs["decorations"]) + deco
    else:
        kwargs["decorations"] = deco

    # return WCls(**kwargs)
    w = WCls(**kwargs)
    w._hide_on_chord = hide

    return w






colors = colors.DoomOne


CHORD_CHIP_COLORS = {
    "Resize-Mode": colorsW[5],  # orange
    "Rofi-Mode":   colorsW[6],  # blue
    "Media-Mode": colorsW[4],  # cyan
    "Scratch-Mode": colorsW[8], 
    "Draw-Mode": colorsW[3],  
    "Mouse-Mode": colorsW[7],  
    "Lang-Switch": colorsW[1],
    "CheatSheet-Mode": colorsW[3],
    
    "WallpaperPicker": colorsW[3],
    
}



@hook.subscribe.enter_chord
def chord_chip_enter(chord_name):
    w = qtile.widgets_map.get("chord_chip")
    if not w:
        return

    for deco in w.decorations:
        if isinstance(deco, RectDecoration):
            deco.colour = CHORD_CHIP_COLORS.get(chord_name, colorsW[2])

    if w.bar:
        w.bar.draw()

@hook.subscribe.leave_chord
def chord_chip_leave():
    w = qtile.widgets_map.get("chord_chip")
    if not w:
        return

    for deco in w.decorations:
        if isinstance(deco, RectDecoration):
            deco.colour = colorsW[2]  # default chip color

    w.bar.draw()


### LAYOUTS ###
# Some settings that I use on almost every layout, which saves us
# from having to type these out for each individual layout.
layout_theme = {
    "border_width": 3,
    "margin": 5,
    "border_focus": colors[8],
    "border_normal": colors[1],
}

layouts = [
    # layout.Bsp(ratio=0.75,**layout_theme),
    # layout.Floating(**layout_theme)
    # layout.RatioTile(**layout_theme),
    # layout.VerticalTile(**layout_theme),
    # layout.Matrix(**layout_theme),
    # layout.MonadWide(**layout_theme),
    # layout.Stack(**layout_theme, num_stacks=2),
    # layout.Columns(**layout_theme),
    # layout.Zoomy(**layout_theme),
    # layout.Tile(shift_windows=True,ratio=0.75, **layout_theme),  # can be used  for write + reading + video = for fun
    layout.MonadTall(
        ratio=0.75,
        min_ratio=0.6,
        max_ratio=0.85,
        **layout_theme,
    ),
    layout.Max(
        border_width=0,
        margin=0,
    ),
    layout.TreeTab(
        font="Ubuntu Bold",
        fontsize=11,
        border_width=0,
        bg_color=colors[0],
        active_bg=colors[8],
        active_fg=colors[2],
        inactive_bg=colors[3],
        inactive_fg=colors[0],
        padding_left=8,
        padding_x=5,
        padding_y=6,
        sections=["ONE", "TWO", "THREE", "DEV"],
        section_fontsize=10,
        section_fg=colors[7],
        section_top=15,
        section_bottom=15,
        level_shift=8,
        vspace=3,
        panel_width=180,
    ),
]

# Some settings that I use on almost every widget, which saves us
# from having to type these out for each individual widget.
widget_defaults = dict(
    font="Ubuntu Bold",
    fontsize=10,
    padding=0,
)

extension_defaults = widget_defaults.copy()


# def init_widgets_list():
#     widgets_list = [
#             left_side_widgets(),
#             widget.Spacer(length=bar.STRETCH),
#             groupbox_widget(),
#             widget.Spacer(length=bar.STRETCH),
#             right_side_widgets(),
        # the logo part
#         chip(
#             ewidget.Image,
#             filename="~/.config/qtile/icons/archLogo.png",
#             margin=5,
#             padding=13,
#             scale="False",
#             mouse_callbacks={"Button1": lambda: qtile.cmd_spawn(myTerm)},
#         ),
#         # the current layout part
#         chip(
#             ewidget.CurrentLayout,
#             padding=18,
#             foreground=colors[3],
#         ),
#         # the | part (not a styled chip)
#         widget.TextBox(
#             text="|", font="Ubuntu Mono", foreground=colors[1], padding=3, fontsize=14
#         ),
# # widget.TaskList(padding=4,margin=5,foreground=colors[1],fontsize=10,background=None,),
# # NOTE: will be added later "weather" it is working , but the screen size is not good enough for it
# # chip(
# #     ewidget.Wttr,
# #     location={"Ankara": "Ankara"},
# #     format="%c  %t ",
# #     units="m",          # metric (°C)
# #     lang="en",          # or "tr"
# #     fontsize=11,
# #     padding=12,
# #     update_interval=600,
# # ),
# #
# widget.TaskList(
#     font="JetBrainsMono Nerd Font",
#     fontsize=11,
#
#     # ICONS
#     icon_size=16,          # ← key setting (default is often too small)
#     # theme_mode="preferred",
#  markup=True,
#
#  # NOTE:  NF =""  , F=focused, V=floating, VF=floating and focused
#  
# markup_normal="",
# markup_focused='<span weight="bold">F {}</span>',
#
# markup_floating='<span foreground="#da8548">V {}</span>',
#
# markup_focused_floating='<span weight="bold" foreground="#ffaa00">VF {}</span>',
#
# markup_minimized='<span foreground="#ff6c6b">↓ {}</span>',
#
# max_title_width=200,
#     padding_x=3,
#     padding_y=2,
#     margin_x=3,
#     margin_y=4,
#     spacing=2,
# parse_text=parse_task_name,
#     window_name_location_offset=1,
# window_name_location="left",
#     # COLORS
#     foreground=colors[1],
#     background=None,
#     # HIGHLIGHT
#     highlight_method="text",
#     border=colors[7],
#     borderwidth=0,
#
#     # TITLE CONTROL
#     #
# txt_minimized="↓  ",
#     # title_width_method="uniform",
#
#     # BEHAVIOR
#     stretch=False,
# ),
#         # the window name part (not a styled chip)
#         # widget.WindowName(
#         #     foreground=colors[1],
#         #     max_chars=50,
#         #     padding=4,
#         #     margin=5,
#         # ),
#         # space from left  to keep group centered
# # ewidget.Spacer(length=52),
#         ewidget.Spacer(length=bar.STRETCH),
        # the group box part
        # chip(
        #     ewidget.GroupBox,
        #     fontsize=10,
        #     margin_y=2,
        #     margin_x=8,
        #     padding_y=2,
        #     padding_x=8,
        #     borderwidth=4,
        #     active=colors[8],
        #     inactive=colors[1],
        #     highlight_color=colors[2],
        #     highlight_method="text",
        #     this_current_screen_border=colors[7],
        #     this_screen_border=colors[4],
        #     other_current_screen_border=colors[7],
        #     other_screen_border=colors[4],
        #     hide_unused=True,
        # ),
        # space from right  to keep group centered
        # ewidget.Spacer(length=bar.STRETCH),
        # the cpu part
#         chip(
#             ewidget.CPU,
#             name="w_cpu",
#
# _hide_on_chord=True,
#             format="  {load_percent}%",
#             fontsize=10,
#             padding=11,
#             foreground=colors[5],
#             mouse_callbacks={
#                 "Button1": lambda: qtile.cmd_spawn(
#                     "env GTK_THEME=Adwaita:dark missioncenter"
#                 )
#             },
#         ),
#         # the memory part
#         chip(
#             ewidget.Memory,
#             name="w_mem",
#             format="{MemUsed: .0f}{mm}",
#             fmt="🖥  {} ",
#             fontsize=10,
#             padding=11,
#             foreground=colors[8],
#             mouse_callbacks={
#                 "Button1": lambda: qtile.cmd_spawn(myFullScreenTerm + " -e btop")
#             },
#         ),
#
#         #NOTE:  check updates will be added later
#             # ewidget.CheckUpdates() ,
#         # the battery part
#         #
#         chip(
#             ewidget.Battery,
#             name="w_battery",
#             format="  {char}{percent:2.0%}",
#             fontsize=10,
#             padding=12,
#             foreground=colors[6],  # > 20%
#             low_foreground=colors[3],  # < 20%
#             low_percentage=0.2,
#             charge_char=" ↑ ",
#             discharge_char=" ↓ ",
#             full_char="✔ ",
#             show_percentage=True,
#             show_short_text=False,
#             mouse_callbacks={
#                 "Button1": lambda: qtile.cmd_spawn(
#                     '/bin/sh -c \'notify-send "Battery Status" "$(acpi | cut -d "," -f 2-)"\''
#                 )
#             },
#         ),
#         # the disk part
#         chip(
#             ewidget.DF,
#             name="w_disk",
#             update_interval=60,
#             partition="/",
#             format="{uf}{m}",
#             fmt="🖴  {}",
#             fontsize=10,
#             padding=11,
#             visible_on_warn=False,
#             foreground=colors[1],
#             mouse_callbacks={"Button1": lambda: qtile.spawn("disk_notify")},
#         ),
#         # the volume part
#         chip(
#             ewidget.Volume,
#             name="w_volume",
#             fmt="🕫  {}",
#             padding=11,
#             foreground=colors[7],
#         ),
#         # the keyboard layout part
#
#         chip(
#             ewidget.KeyboardLayout,
#             name="w_lang",
#             configured_keyboards=["us", "ara", "tr", "de"],
#             display_map={
#                 "us": "🇺🇸 EN",
#                 "ara": "🇸🇦 AR",
#                 "tr": "🇹🇷 TR",
#                 "de": "🇩🇪 DE",
#             },
#             fmt="{}",
#             padding=11,
#             foreground=colors[4],
#         ),
# chip(
#     ewidget.Chord,
#     name="chord_chip",   # 👈 important
#     fmt=" {} ",
#     padding=11,
#     foreground=colors[2],
#     background=None,
#     name_transform=lambda name: {
#         "Resize-Mode":  "󰩨   RESIZE",
#         "Rofi-Mode":    "󰍉   ROFI",
#         "Media-Mode":   "󰕾   MEDIA",
#         "Scratch-Mode": "󰈆   SCRATCH",
#         "Draw-Mode":    "󰏫   DRAW",
#         "Mouse-Mode":   "󰍽   MOUSE",
#         "Arabic-Mode":  "   ARABIC",
#         "Lang-Switch":  "   LANG",
#         "CheatSheet-Mode": "󰆍   CHEATSHEET",
#     }.get(name, name.upper()),
# ),
#         # the clock part
#         chip(
#             ewidget.Clock,
#             format=" %a, %b %d - %H:%M",
#             padding=11,
#             foreground=colors[8],
#             mouse_callbacks={"Button1": lambda: qtile.spawn("clock_popup")},
#
#         ),
#         # the system tray part (icons)
#         widget.Systray(padding=7, icon_size=14),
    # ]
    # return widgets_list


def init_widgets_list():
    return [
        *left_side_widgets(),

        ewidget.Spacer(length=bar.STRETCH),

        groupbox_widget(),
        ewidget.Spacer(length=bar.STRETCH),

        *right_side_widgets(),
    ]

# Monitor 1 will display ALL widgets in widgets_list. It is important that this
# is the only monitor that displays all widgets because the systray widget will
# crash if you try to run multiple instances of it.
def init_widgets_screen1():
    widgets_screen1 = init_widgets_list()
    return widgets_screen1


# All other monitors' bars will display everything but widgets 22 (systray) and 23 (spacer).
def init_widgets_screen2():
    widgets_screen2 = init_widgets_list()
    # del widgets_screen2[22:24]
    return widgets_screen2


# For adding transparency to your bar, add (background="#00000000") to the "Screen" line(s)
# For ex: Screen(top=bar.Bar(widgets=init_widgets_screen2(), background="#00000000", size=24)),

#
# def init_screens():
#     return [
#         Screen(top=bar.Bar(widgets=init_widgets_screen1(),
#     margin=[4, 50, 4, 50],  # top, right, bottom, left
#     size=28 ,
#             background = "#11111b00")),
#         # Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26)),
#         Screen(top=bar.Bar(widgets=init_widgets_screen2(), size=26)),
#     ]


def init_screens():
    return [
        Screen(
            top=bar.Bar(
                # all widgets (including your chip) go in this list
        widgets=init_widgets_screen1(),
        size=28,
                margin=[5, 10, 5, 10],  # top, right, bottom, left
                # IMP: this is the background color of the bar
                background="#11111b00",  # transparent
            ),

        ),
        Screen(
            top=bar.Bar(
                widgets=init_widgets_screen2(),
                # all widgets (including your chip) go in this list
                size=28,
                margin=[5, 10, 5, 10],  # top, right, bottom, left
                # IMP: this is the background color of the bar
                background="#11111b00",  # transparent


            ),
        ),
    ]


if __name__ in ["config", "__main__"]:
    screens = init_screens()
    widgets_list = init_widgets_list()
    widgets_screen1 = init_widgets_screen1()
    widgets_screen2 = init_widgets_screen2()

# Drag floating layouts.
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.bring_to_front()),
]

dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = True
bring_front_click = False
cursor_warp = False
floating_layout = layout.Floating(
    border_focus=colors[8],
    border_width=2,
    float_rules=[
        # Run the utility of `xprop` to see the wm class and name of an X client.
        *layout.Floating.default_float_rules,
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="dialog"),  # dialog boxes
        Match(wm_class="download"),  # downloads
        Match(wm_class="error"),  # error msgs
        Match(wm_class="file_progress"),  # file progress boxes
        Match(wm_class="kdenlive"),  # kdenlive
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="notification"),  # notifications
        Match(wm_class="pinentry-gtk-2"),  # GPG key password entry
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(wm_class="toolbar"),  # toolbars
        Match(wm_class="Yad"),  # yad boxes
        Match(title="branchdialog"),  # gitk
        Match(title="Confirmation"),  # tastyworks exit box
        Match(title="Qalculate!"),  # qalculate-gtk
        Match(title="pinentry"),  # GPG key password entry
        Match(title="tastycharts"),  # tastytrade pop-out charts
        Match(title="tastytrade"),  # tastytrade pop-out side gutter
        Match(title="tastytrade - Portfolio Report"),  # tastytrade pop-out allocation
        Match(wm_class="tasty.javafx.launcher.LauncherFxApp"),  # tastytrade settings
        Match(title="imv"),  # Match the imv window
        Match(title="feh"),  # Match feh
        Match(wm_class="mpv"),  # mpv
        Match(wm_class="mpvk"),  # mpv
        Match(wm_class="satty"),  # satty
        Match(wm_class="emacs"),  # emacs
        Match(title="link-preview"),  # preview of nvim (qutebrowser edit link)
        Match(wm_class="org.gnome.NautilusPreviewer"),  # make the preview float
        # Match(wm_class="Anki"),  # make the preview float
    ],
)
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
wl_input_rules = None


@hook.subscribe.startup_once
def start_once():
    home = os.path.expanduser("~")
    subprocess.call([home + "/.config/qtile/autostart.sh"])

    # -------------------------------------------


# def assign_app_to_group(client):
#     wm_class = client.window.get_wm_class()
#     if wm_class:
#         if wm_class[0] in ["firefox", "chrome", "brave", "vivaldi"]:
#             client.togroup("3")
#         # Add more rules as needed

# -------------------------------------------


# XXX: Gasp! We're lying here. In fact, nobody really uses or cares about this
# string besides java UI toolkits; you can see several discussions on the
# mailing lists, GitHub issues, and other WM documentation that suggest setting
# this string if your java app doesn't work correctly. We may as well just lie
# and say that we're a working one by default.
#
# We choose LG3D to maximize irony: it is a 3D non-reparenting WM written in
# java that happens to be on java's whitelist.
wmname = "LG3D"
