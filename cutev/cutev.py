import argparse
import curses


def setup_header(filename: str, width: int) -> str:
    padding = width - len(filename)
    left_padding = int(padding / 2)
    right_padding = padding - left_padding
    return f"{' ' * left_padding}{filename}{' ' * right_padding}"


def load_file(filename: str) -> str:
    try:
        with open(filename) as f:
            data = f.read()
    except FileNotFoundError:
        raise FileNotFoundError
    else:
        return data


def setup_curses_colors() -> None:
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_GREEN)


def curses_main(screen, file_data: str, filename: str) -> None:
    setup_curses_colors()
    curses.curs_set(0)  # Set the cursor to off.
    line_data = file_data.splitlines()

    line_modifier = 0
    while True:
        screen_height, screen_width = screen.getmaxyx()
        header = setup_header(filename, screen_width)
        part_data = line_data[line_modifier:line_modifier + screen_height]

        screen.clear()
        screen.addstr(0, 0, header, curses.color_pair(1))
        # screen.addstr(1, 0, file_data)
        # part_data = line_data[line_modifier:line_modifier + screen_height]
        for i, line in enumerate(part_data, start=1):
            if i >= screen_height - 2:
                break
            screen.addstr(i, 0, line)

        screen.refresh()
        ch = screen.getch()
        if ch in [81, 113]:  # q, Q
            break
        elif ch == curses.KEY_DOWN:
            if line_modifier <= len(line_data) - screen_height + 2:
                line_modifier += 1
        elif ch == curses.KEY_UP:
            if line_modifier > 0:
                line_modifier -= 1
        elif ch == curses.KEY_NPAGE:
            line_modifier += screen_height - 4
            if line_modifier >= len(line_data) - screen_height + 2:
                line_modifier = len(line_data) - screen_height + 3
        elif ch == curses.KEY_PPAGE:
            line_modifier -= screen_height - 4
            if line_modifier <= 0:
                line_modifier = 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="filename to view")
    args = parser.parse_args()

    try:
        data = load_file(args.filename)
    except FileNotFoundError:
        print("Error file not found")
        return 1
    else:
        curses.wrapper(curses_main, data, args.filename)
        return 0


if __name__ == "__main__":
    exit(main())
