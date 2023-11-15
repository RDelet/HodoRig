from functools import partial

kObjectMenu = "buildObjectMenuItemsNow"  # ViewPort menu


def override_maya_menu():
    for maya_menu in cmds.lsUI(menus=True):
        menu_cmd = cmds.menu(maya_menu, query=True, postMenuCommand=True)
        if menu_cmd and isinstance(menu_cmd, str):
            # override_outliner_menu(menu_cmd, maya_menu)
            override_viewport_menu(menu_cmd, maya_menu)


def override_viewport_menu(menu_cmd, maya_menu):
    if kObjectMenu not in menu_cmd:
        return
    parent_menu = menu_cmd.split(" ")[-1]
    print(f"Override menu {maya_menu}")
    func = partial(menu_switch, parent_menu)
    cmds.menu(maya_menu, edit=True, postMenuCommand=func)


def menu_switch(*args, **kwargs):
    parent_menu = args[0]
    if type(args[1]) != bool:
        custom_menu = False
        for func in viewport_menu_funcs:
            if func(parent_menu):
                custom_menu = True
                break

        if not custom_menu:
            mel.eval(f"{kObjectMenu} {parent_menu}")

    return parent_menu


def ctrl_menu_fill(parent_menu) -> bool:

    sel = cmds.ls(selection=True, long=True, type="transform")
    if not sel or not sel[0].endswith("_ctrl"):
        return False

    _parent_menu = parent_menu.replace('"', "")
    cmds.menu(_parent_menu, edit=True, deleteAllItems=True)
    cmds.menuItem(parent=_parent_menu, label="Kapouet", command=print_hodor, radialPosition="N")
    cmds.menuItem(parent=_parent_menu, label="Hodor", command=print_hodor)
    cmds.menuItem(parent=_parent_menu, label="Groot", command=print_groot)

    return True


def print_hodor(*args, **kwargs):
    print("Hodor !", args, kwargs)


def print_groot(*args, **kwargs):
    print("Groot !", args, kwargs)


viewport_menu_funcs = [ctrl_menu_fill]
override_maya_menu()