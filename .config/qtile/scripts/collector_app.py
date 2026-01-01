def toggle_collector(qtile):
    global _spawning_collector

    for w in qtile.windows_map.values():
        if w.window.get_wm_class() and "collector" in w.window.get_wm_class()[0].lower():

            _spawning_collector = False  # ✅ window exists now

            current_group = qtile.current_group

            # 🚀 CASE 1: on another workspace → bring directly
            if w.group != current_group:
                w.togroup(current_group.name)

                if w.minimized:
                    w.toggle_minimize()

                w.floating = True

                screen = qtile.current_screen
                margin = 8
                x = screen.x + screen.width - 360 - margin
                y = screen.y + margin

                w.cmd_set_position_floating(x, y)
                w.cmd_bring_to_front()
                w.focus()
                return

            # 🚀 CASE 2: same workspace
            if w.minimized:
                w.toggle_minimize()
                w.floating = True

            elif qtile.current_window != w:
                w.focus()
                w.cmd_bring_to_front()

            else:
                w.toggle_minimize()
                return

            screen = qtile.current_screen
            margin = 8
            x = screen.x + screen.width - 360 - margin
            y = screen.y + margin

            w.cmd_set_position_floating(x, y)
            w.cmd_bring_to_front()
            w.focus()
            return

    # 🚀 CASE 3: not running → spawn (LOCKED)
    if not _spawning_collector:
        _spawning_collector = True
        qtile.cmd_spawn("flatpak run it.mijorus.collector")

