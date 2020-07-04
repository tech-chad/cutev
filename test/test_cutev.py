
import pytest
from hecate import Runner

from cutev import cutev


def run_cutev(*args):
    options = [a for a in args]
    return ["python3", "cutev/cutev.py"] + options


def sample_file_small():
    # returns contents of a sample file as a string
    data = ["# sample python 3 file\n",
            "\n",
            "\n",
            "def main():\n",
            "    print('hello world')\n",
            "\n",
            "\n",
            "if __name__ == '__main__':\n",
            "    main()\n"
            ]
    return "".join(data)


def sample_file_medium():
    # returns contents of a sample file as a string
    data = ["# sample python 3 medium file\n",
            "\n",
            "\n",
            "def main():\n",
            "    # main function\n",
            "    for x in range(10):\n",
            "        # loop for 10 times\n",
            "        print('hello world')\n",  # showing
            "        print(f'{x} + 1 = {x + 1}')\n",
            "        print('done')\n",
            "\n",
            "\n",
            "if __name__ == '__main__':\n",
            "    # entry point for this script that calls the main function\n",
            "    main()\n",
            ]
    return "".join(data)


def test_setup_header_single_file():
    pad = " " * 37
    expected_result = pad + "foo.py" + pad
    result = cutev.setup_header("foo.py", 0, 1, 80)
    assert result == expected_result


def test_setup_header_multiple_files():
    pad_r = " " * 33
    pad_l = " " * 34
    expected_result = pad_r + "foo.py  1 / 2" + pad_l
    result = cutev.setup_header("foo.py", 0, 2, 80)
    assert result == expected_result


def test_load_file(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write("# foo.py\n\nprint('hello world')")
    result = cutev.load_file(tf.strpath)
    assert result == "# foo.py\n\nprint('hello world')"


@pytest.mark.parametrize("cmd", ["-h", "--help"])
def test_cutev_show_help(cmd):
    with Runner(*run_cutev(cmd)) as h:
        h.await_text("usage")


@pytest.mark.parametrize("cmd", ["Q", "q"])
def test_cutev_quit(cmd, tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write("# foo.py\n\nprint('hello world')")
    with Runner(*run_cutev(tf.strpath)) as h:
        h.await_text("foo.py")
        h.write(cmd)
        h.press("Enter")
        h.await_exit()


def test_cutev_view_file(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_small()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath)) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        h.write("q")
        h.press("Enter")
        h.await_exit()
    assert data in captured


def test_cutev_scrolling(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_small()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        assert "if __name__ == '__main__':" in captured
        assert "    main()" not in captured
        h.press("Down")
        captured = h.screenshot()
        assert "    main()" in captured
        assert "# sample python 3 file" not in captured
        h.press("Up")
        captured = h.screenshot()
        assert "    main()" not in captured
        assert "# sample python 3 file" in captured
        h.write("q")
        h.press("Enter")
        h.await_exit()


def test_cutev_page_down_and_up(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        assert "print('hello world')" in captured
        assert "print(f'{x} + 1 = {x + 1}')" not in captured
        h.press("PageDown")
        captured = h.screenshot()
        assert "print(f'{x} + 1 = {x + 1}')" in captured
        assert "        print('done')" in captured
        assert "# sample python 3 medium file" not in captured
        h.write("q")
        h.await_exit()


def test_cutev_goto_line_prompt(tmpdir):
    # check characters does nothing
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 medium file")
        h.write("g")
        h.await_text("Go to line:")
        h.write("z")
        captured = h.screenshot()
        assert "z" not in captured


def test_cutev_goto_line(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 medium file")
        h.write("g")
        h.await_text("Go to line:")
        h.write("13")
        h.press("Enter")
        captured = h.screenshot()
        c = captured.splitlines()[1]
        assert "if __name__ == '__main__':" in c


def test_cutev_goto_line_one_off_screen(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 medium file")
        h.write("g")
        h.await_text("Go to line:")
        h.write("9")
        h.press("Enter")
        captured = h.screenshot()
        c = captured.splitlines()[1]
        assert "        print(f'{x} + 1 = {x + 1}')" in c


def test_cutev_goto_line_already_on_screen(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write(sample_file_medium())
    with Runner(*run_cutev(tf.strpath), height=20) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        c = captured.splitlines()[1]
        h.write("g")
        h.await_text("Go to line:")
        h.write("6")
        h.press("Enter")
        captured = h.screenshot()
        assert captured.splitlines()[1] == c


def test_cutev_goto_line_zero(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write(sample_file_small())
    with Runner(*run_cutev(tf.strpath), height=20) as h:
        h.await_text("foo.py")
        h.write("g")
        h.await_text("Go to line:")
        h.write("0")
        captured = h.screenshot()
        assert "Go to line: 0" not in captured


def test_cutev_goto_line_no_exist(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 medium file")
        captured = h.screenshot()
        c = captured.splitlines()[1]
        h.write("g")
        h.await_text("Go to line:")
        h.write("30")
        h.press("Enter")
        captured = h.screenshot()
        assert captured.splitlines()[1] == c


def test_cutev_goto_line_backspace(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 medium file")
        h.write("g")
        h.await_text("Go to line:")
        h.write("5")
        h.await_text("Go to line: 5")
        h.write("1")
        h.await_text("Go to line: 51")
        h.press("Backspace")
        h.await_text("Go to line: 5")


def test_cutev_file_not_found(tmpdir):
    tf = tmpdir.join("bar.py")
    with Runner("bash") as h:
        h.write("clear")
        h.press("Enter")
        h.write(f"python3 cutev/cutev.py {tf.strpath}")
        h.press("Enter")
        h.await_text("No files loaded")


def test_cutev_no_filename_passed():
    with Runner("bash") as h:
        h.write("clear")
        h.press("Enter")
        h.write("python3 cutev/cutev.py")
        h.press("Enter")
        h.await_text("usage:")


def test_cutev_line_off_screen(tmpdir):
    tf = tmpdir.join("foo.py")
    data = "a" * 85
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), width=80) as h:
        h.await_text("foo.py")
        h.await_text("a")
        captured = h.screenshot()
        expected = "a" * 79 + "$"
        assert captured.splitlines()[1] == expected


def test_cutev_single_file(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write(sample_file_small())
    with Runner(*run_cutev(tf.strpath)) as h:
        h.await_text("foo.py")


def test_cutev_multiple_files_quit(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    with Runner(*run_cutev(tf1.strpath, tf2.strpath)) as h:
        h.await_text("foo.py  1 / 2")
        h.write("q")
        h.press("Enter")
        h.await_exit()


def test_cutev_multiple_files_open(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    with Runner(*run_cutev(tf1.strpath, tf2.strpath)) as h:
        h.await_text("foo.py  1 / 2")
        h.await_text("# sample python 3 file")


def test_cutev_multiple_files_open_one_not_found(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf3 = tmpdir.join("a")
    tf3.write("test test test")
    with Runner(*run_cutev(tf1.strpath, tf2.strpath, tf3.strpath)) as h:
        h.await_text("foo.py  1 / 2")


def test_cutev_multiple_files_switching_forward(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    tf3 = tmpdir.join("a")
    tf3.write("test test test")
    with Runner(*run_cutev(tf1.strpath, tf2.strpath, tf3.strpath)) as h:
        h.await_text("foo.py  1 / 3")
        h.press("^n")
        h.await_text("bar.py  2 / 3")
        h.await_text("# sample python 3 medium file")
        h.press("^n")
        h.await_text("a  3 / 3")
        h.await_text("test test test")
        h.press("^n")
        h.await_text("foo.py  1 / 3")
        h.await_text("# sample python 3 file")


def test_cutev_multiple_files_switching_backward(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    tf3 = tmpdir.join("a")
    tf3.write("test test test")
    with Runner(*run_cutev(tf1.strpath, tf2.strpath, tf3.strpath)) as h:
        h.await_text("foo.py  1 / 3")
        h.press("^b")
        h.await_text("a  3 / 3")
        h.await_text("test test test")
        h.press("^b")
        h.await_text("bar.py  2 / 3")
        h.await_text("# sample python 3 medium file")
        h.press("^b")
        h.await_text("foo.py  1 / 3")
        h.await_text("# sample python 3 file")


def test_cutev_ctrl_x_close_single_file(tmpdir):
    tf = tmpdir.join("a.txt")
    tf.write("test test test")
    with Runner(*run_cutev(tf.strpath)) as h:
        h.await_text("a.txt")
        h.press("^x")
        h.await_exit()


def test_cutev_ctrl_x_close_multiple_files(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    tf3 = tmpdir.join("a")
    tf3.write("test test test")
    with Runner(*run_cutev(tf1.strpath, tf2.strpath, tf3.strpath)) as h:
        h.await_text("foo.py  1 / 3")
        h.press("^x")
        h.await_text("bar.py  1 / 2")
        h.await_text("# sample python 3 medium file")
        h.press("^x")
        h.await_text("a")
        h.await_text("test test test")
        h.press("^x")
        h.await_exit()


def test_cutev_ctrl_a_close_all_except_current(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    tf2 = tmpdir.join("bar.py")
    tf2.write(sample_file_medium())
    tf3 = tmpdir.join("a")
    tf3.write("test test test")
    with Runner(*run_cutev(tf1.strpath, tf2.strpath, tf3.strpath)) as h:
        h.await_text("foo.py  1 / 3")
        h.await_text("# sample python 3 file")
        h.press("^a")
        h.await_text("foo.py")
        captured = h.screenshot()
        assert "foo.py  1 / 3" not in captured
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")


def test_cutev_ctrl_a_close_all_except_current_only_one_open(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    with Runner(*run_cutev(tf1.strpath)) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")
        h.press("^a")
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")


def test_cutev_no_scroll_right_left_small_file(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    with Runner(*run_cutev(tf1.strpath)) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")
        h.await_text("    print('hello world')")
        h.press("Right")
        h.press("Right")
        captured = h.screenshot()
        assert "print('hello world')" in captured
        h.press("Left")
        h.press("left")
        captured = h.screenshot()
        assert "print('hello world')" in captured
        assert "# sample python 3 file" in captured


def test_cutev_scroll_left_right_long_line(tmpdir):
    tf = tmpdir.join("foo.txt")
    data = "a" * 24 + "bcd"
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), width=25) as h:
        h.await_text("a" * 24 + "$")
        h.press("Right")
        h.await_text("a" * 23 + "b$")
        h.press("Right")
        h.await_text("a" * 22 + "bcd")
        h.press("Right")
        h.await_text("a" * 22 + "bcd")
        h.press("Left")
        h.await_text("a" * 23 + "b$")
        h.press("Left")
        h.await_text("a" * 24 + "$")


def test_cutev_line_number(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    with Runner(*run_cutev(tf1.strpath, "-l")) as h:
        h.await_text("foo.py")
        h.await_text("1")
        captured = h.screenshot()
        assert "1# sample python 3 file" in captured


def test_cutev_line_number_scroll_down_up(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write(sample_file_medium())
    with Runner(*run_cutev(tf.strpath, "-l"), width=80, height=11) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        assert " 8        print('hello world')" in captured
        h.press("Down")
        captured = h.screenshot()
        assert " 9        print(f'{x} + 1 = {x + 1}')" in captured
        assert " 1# sample python 3 file" not in captured
        h.press("Down")
        captured = h.screenshot()
        assert "10        print('done')" in captured
        assert " 2\n" not in captured
        h.press("up")
        captured = h.screenshot()
        assert "10        print('done')" not in captured
        assert " 2\n" in captured


def test_cutev_line_numbers_right_left_scroll(tmpdir):
    tf = tmpdir.join("foo.txt")
    data = "a" * 24 + "bcd"
    tf.write(data)
    with Runner(*run_cutev(tf.strpath, "-l"), width=25) as h:
        h.await_text("1" + "a" * 23 + "$")
        h.press("Right")
        h.await_text("1" + "a" * 23 + "$")
        h.press("Right")
        h.await_text("1" + "a" * 22 + "b$")
        h.press("Right")
        h.await_text("1" + "a" * 21 + "bcd")
        h.press("Left")
        h.await_text("1" + "a" * 22 + "b$")
        h.press("Left")
        h.await_text("1" + "a" * 23 + "$")


def test_cutev_line_numbers_on_off(tmpdir):
    tf1 = tmpdir.join("foo.py")
    tf1.write(sample_file_small())
    with Runner(*run_cutev(tf1.strpath)) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        assert "# sample python 3 file" in captured
        assert "1# sample python 3 file" not in captured
        h.write("l")
        captured = h.screenshot()
        assert "1# sample python 3 file" in captured
        h.write("l")
        captured = h.screenshot()
        assert "1# sample python 3 file" not in captured


def test_cutev_last_line_show_blank(tmpdir):
    tf = tmpdir.join("foo.py")
    tf.write(sample_file_small())
    with Runner(*run_cutev(tf.strpath, "-l"), height=13) as h:
        h.await_text("foo.py")
        captured = h.screenshot()
        assert "10" in captured.splitlines()[-3:]


def test_cutev_last_line_show_line(tmpdir):
    tf = tmpdir.join("foo.txt")
    tf.write("test test test\npost toasties")
    with Runner(*run_cutev(tf.strpath, "-l")) as h:
        h.await_text("foo.txt")
        h.await_text("1test test test")
        h.await_text("2post toasties")
        captured = h.screenshot()
        assert "3" not in captured
