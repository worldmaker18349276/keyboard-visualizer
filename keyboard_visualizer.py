import re
import curses
import keyboard


names_temp = r"""
[esc][f1][f2][f3][f4][f5][f6][f7][f8][f9][f10][f11][f12]
[`][1][2][3][4][5][6][7][8][9][0][minus][=][backspace]                                  [insert][home][page up]
[tab][q][w][e][r][t][y][u][i][o][p][[][]][\]                                            [delete][end][page down]
[caps lock][a][s][d][f][g][h][j][k][l][;]['][enter]
[left shift][z][x][c][v][b][n][m][,][.][/][right shift]                                         [up]
[left ctrl][left windows][left alt][space][right alt][right windows][menu][right ctrl]   [left][down][right]
"""

pos_temp = r"""
[_] [_][_][_][_] [_][_][_][_] [_][__][__][__]
[_][_][_][_][_][_][_][_][_][_][_][_][_][____] [_][_][_]
[__][_][_][_][_][_][_][_][_][_][_][_][_][___] [_][_][_]
[___][_][_][_][_][_][_][_][_][_][_][_][_____]
[____][_][_][_][_][_][_][_][_][_][_][_______]    [_]
[__][__][__][________________][__][__][_][__] [_][_][_]
"""

keyboard_temp = r"""
[⎋] [₁][₂][₃][₄] [₅][₆][₇][₈] [₉][₁₀][₁₁][₁₂]
[`][1][2][3][4][5][6][7][8][9][0][-][=][ ←  ] [⎀][⭰][⭱]
[↹ ][q][w][e][r][t][y][u][i][o][p][[][]][ \ ] [¬][⭲][⭳]
[⇪  ][a][s][d][f̲][g][h][j̲][k][l][;]['][  ⏎  ]
[ ⇧  ][z][x][c][v][b][n][m][,][.][/][   ⇧   ]    [⭡]
[⌃ ][𐌎 ][⌥ ][       ␣        ][⌥ ][𐌎 ][⌸][⌃ ] [⭠][⭣][⭢]
"""

keyboard_temp_shift = r"""
[⎋] [₁][₂][₃][₄] [₅][₆][₇][₈] [₉][₁₀][₁₁][₁₂]
[~][!][@][#][$][%][^][&][*][(][)][_][+][ ←  ] [⎀][⭰][⭱]
[↹ ][Q][W][E][R][T][Y][U][I][O][P][{][}][ | ] [¬][⭲][⭳]
[⇪  ][A][S][D][F̲][G][H][J̲][K][L][:]["][  ⏎  ]
[ ⇧  ][Z][X][C][V][B][N][M][<][>][?][   ⇧   ]    [⭡]
[⌃ ][𐌎 ][⌥ ][       ␣        ][⌥ ][𐌎 ][⌸][⌃ ] [⭠][⭣][⭢]
"""


codes = []
for match in re.finditer(r"\[(.+?)\]", names_temp):
    name = match.group(1)

    try:
        res = keyboard.key_to_scan_codes(name)
    except ValueError:
        res = ()

    if not res and name in ("left windows", "right windows"):
        # left/right windows => third/fourth alt
        try:
            res = keyboard.key_to_scan_codes("alt")
            res = res[2:]
        except ValueError:
            res = ()

    if not res:
        codes.append(-1)
    elif len(res) == 1:
        codes.append(res[0])
    elif name.startswith("right "):
        codes.append(res[1])
    else:
        codes.append(res[0])


pos = []
for match in re.finditer(r"\[.+?\]", pos_temp):
    start = match.start()
    num = match.end() - start
    prefix = pos_temp[:start]
    y = prefix.count("\n")
    x = len(prefix.split("\n")[-1])
    pos.append((y, x, num))


PRESSED = 0
RELEASED = 1
CLEAR = 2

def add_key_attr(stdscr, y, x, num, state):
    if state == PRESSED:
        stdscr.chgat(y, x, num, curses.A_REVERSE)
    elif state == RELEASED:
        stdscr.chgat(y, x, num, curses.A_NORMAL)
    else:
        stdscr.chgat(y, x, 1, curses.A_DIM)
        stdscr.chgat(y, x+1, num-2, curses.A_NORMAL)
        stdscr.chgat(y, x+num-1, 1, curses.A_DIM)

def draw_keyboard(stdscr, shifted, pressed, prev):
    temp = keyboard_temp_shift if shifted else keyboard_temp
    for line, line_temp in enumerate(temp.split("\n")):
        stdscr.addstr(line, 0, line_temp)

    for y, x, num in pos:
        add_key_attr(stdscr, y, x, num, CLEAR)

    for scan_code in prev:
        y, x, num = pos[codes.index(scan_code)]
        add_key_attr(stdscr, y, x, num, RELEASED)

    for scan_code in pressed:
        y, x, num = pos[codes.index(scan_code)]
        add_key_attr(stdscr, y, x, num, PRESSED)

try:
    @curses.wrapper
    def main(stdscr):
        curses.use_default_colors()
        curses.curs_set(0)

        shifted = False
        pressed = set()
        prev = set()
        currkey = None
        count = 0

        stdscr.clear()
        draw_keyboard(stdscr, shifted, pressed, prev)

        while True:
            stdscr.refresh()
            event = keyboard.read_event()

            # stdscr.move(pos_temp.count("\n") + 1, 0)
            # stdscr.clrtobot()
            # stdscr.addstr(event.to_json())

            if event.event_type == "down":
                hotkey = keyboard.get_hotkey_name() or "unknown"
                if currkey == hotkey:
                    count += 1
                else:
                    currkey = hotkey
                    count = 1
                stdscr.move(0, 0)
                stdscr.clrtoeol()
                stdscr.addstr("⌨   {}{}".format(hotkey, str(f" ✕ {count}" if count > 1 else "")))

            if event.scan_code not in codes:
                continue

            y, x, num = pos[codes.index(event.scan_code)]
            if event.event_type == keyboard.KEY_DOWN:
                pressed.add(event.scan_code)
                prev.discard(event.scan_code)
                add_key_attr(stdscr, y, x, num, PRESSED)
            elif event.scan_code in pressed and not keyboard.is_modifier(event.scan_code):
                pressed.remove(event.scan_code)
                prev.add(event.scan_code)
                add_key_attr(stdscr, y, x, num, RELEASED)
            else:
                pressed.discard(event.scan_code)
                prev.discard(event.scan_code)
                add_key_attr(stdscr, y, x, num, CLEAR)

            if event.event_type == keyboard.KEY_DOWN and not keyboard.is_modifier(event.scan_code):
                for scan_code in prev:
                    y, x, num = pos[codes.index(scan_code)]
                    add_key_attr(stdscr, y, x, num, CLEAR)
                prev.clear()

            if not shifted and event.name == "shift" and event.event_type == "down":
                shifted = True
            elif shifted and event.name == "shift" and event.event_type == "up":
                shifted = False
            else:
                continue

            draw_keyboard(stdscr, shifted, pressed, prev)

except KeyboardInterrupt:
    pass

finally:
    curses.flushinp()
