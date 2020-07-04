import argparse
import curses

from typing import List


def setup_header(filename: str,
                 file_number: int,
                 total_files: int,
                 width: int) -> str:
    if total_files == 1:
        header_str = filename
    else:
        header_str = f"{filename}  {file_number + 1} / {total_files}"
    padding = width - len(header_str)
    left_padding = int(padding / 2)
    right_padding = padding - left_padding
    return f"{' ' * left_padding}{header_str}{' ' * right_padding}"


def goto_prompt(screen, prompt_string: str, width: int, length: int) -> str:
    curses.curs_set(1)
    padding = width - len(prompt_string) - 1
    cursor_loc = (length - 1, len(prompt_string))
    p = f"{prompt_string}{' ' * padding}"
    screen.addstr(length - 1, 0, p, curses.color_pair(2))
    screen.move(*cursor_loc)
    user_input = ""
    while True:
        u = screen.getch()
        str_u = chr(u)
        if u == curses.KEY_ENTER or u == 10:
            break
        elif u == curses.KEY_BACKSPACE and len(user_input) > 0:
            y, x = screen.getyx()
            screen.move(y, x - 1)
            screen.addch(" ", curses.color_pair(2))
            screen.move(y, x - 1)
            user_input = user_input[:-1]

        elif str_u.isdigit():
            if str_u == '0' and len(user_input) == 0:
                continue
            user_input += str_u
            screen.addch(str_u, curses.color_pair(2))
    curses.curs_set(0)

    return user_input


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
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)


def curses_main(screen,
                file_data: List[str],
                filename: List[str],
                line_numbers: bool) -> None:
    setup_curses_colors()
    curses.curs_set(0)  # Set the cursor to off.
    current_file = 0
    total_files = len(file_data)
    line_data = file_data[current_file].splitlines(keepends=True)
    if line_data[-1][-1] == "\n":
        line_data.append("\n")

    line_modifier = 0
    column_modifier = 0
    max_column_mod = 0
    longest_line = 0
    while True:
        screen_height, screen_width = screen.getmaxyx()
        if line_numbers:
            line_num_mod = len(str(len(line_data)))
        else:
            line_num_mod = 0
        header = setup_header(filename[current_file],
                              current_file,
                              total_files,
                              screen_width)
        part_data = line_data[line_modifier:line_modifier + screen_height]

        screen.clear()
        screen.addstr(0, 0, header, curses.color_pair(1))
        # screen.addstr(1, 0, file_data)
        # part_data = line_data[line_modifier:line_modifier + screen_height]
        for i, line in enumerate(part_data, start=1):
            if i >= screen_height - 2:
                break
            if line_numbers:
                screen.addstr(i, 0, f"{i + line_modifier: >{line_num_mod}}",
                              curses.color_pair(2))

            if len(line) > screen_width - line_num_mod + column_modifier:
                if len(line) > longest_line:
                    longest_line = len(line)
                    max_column_mod = longest_line - screen_width + line_num_mod
                index_to = screen_width - line_num_mod - 1 + column_modifier
                screen.addstr(i, 0 + line_num_mod,
                              line[column_modifier:index_to] + "$")
            else:
                screen.addstr(i, 0 + line_num_mod, line[column_modifier:])

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
        elif ch == curses.KEY_RIGHT:
            if column_modifier < max_column_mod:
                column_modifier += 1
        elif ch == curses.KEY_LEFT:
            if column_modifier > 0:
                column_modifier -= 1
        elif ch == curses.KEY_NPAGE:
            line_modifier += screen_height - 4
            if line_modifier >= len(line_data) - screen_height + 2:
                line_modifier = len(line_data) - screen_height + 3
        elif ch == curses.KEY_PPAGE:
            line_modifier -= screen_height - 4
            if line_modifier <= 0:
                line_modifier = 0
        elif ch == 103:  # g
            line_num = goto_prompt(screen, "Go to line: ",
                                   screen_width, screen_height)
            if line_num.isdigit() and int(line_num) < len(line_data):
                line_num = int(line_num) - 1
                if line_modifier <= line_num <= line_modifier + screen_height:
                    pass
                else:
                    line_modifier = line_num
        elif ch == 108:  # l
            line_numbers = not line_numbers
        elif ch == 14:  # ctrl-n
            if current_file + 1 >= total_files:
                current_file = 0
            else:
                current_file += 1
            line_data = file_data[current_file].splitlines()
        elif ch == 2:  # ctrl-b
            if current_file == 0:
                current_file = total_files - 1
            else:
                current_file -= 1
            line_data = file_data[current_file].splitlines()
        elif ch == 24:  # ctrl-x
            close_num = current_file
            if total_files == 1:
                break
            total_files -= 1
            if current_file == total_files:
                current_file = 0
            file_data.pop(close_num)
            filename.pop(close_num)
            line_data = file_data[current_file].splitlines()
        elif ch == 1:  # ctrl-a
            if total_files > 1:
                current_file_data = file_data[current_file]
                current_file_name = filename[current_file]
                file_data.clear()
                filename.clear()
                file_data.append(current_file_data)
                filename.append(current_file_name)
                current_file = 0
                total_files = 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="+", help="file name(s) to view")
    parser.add_argument("-l", "--linenumbers", action="store_true",
                        help="show line numbers")
    args = parser.parse_args()

    file_data = []
    file_names = []
    for file in args.filename:
        try:
            file_data.append(load_file(file))
            file_names.append(file)
        except FileNotFoundError:
            pass

    if len(file_data) == 0:
        print("No files loaded")
        return 1
    else:
        curses.wrapper(curses_main, file_data, file_names, args.linenumbers)
        return 0


if __name__ == "__main__":
    exit(main())
