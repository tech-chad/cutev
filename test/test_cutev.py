
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
    data = ["# sample python 3 file\n",
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


def test_setup_header():
    pad = " " * 37
    expected_result = pad + "foo.py" + pad
    result = cutev.setup_header("foo.py", 80)
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
        assert "print('hello world')" in captured
        assert "print(f'{x} + 1 = {x + 1}')" in captured
        assert "# sample python 3 file" not in captured
        h.write("q")
        h.await_exit()


def test_cutev_goto_line_prompt(tmpdir):
    # check characters does nothing
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")
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
        h.await_text("# sample python 3 file")
        h.write("g")
        h.await_text("Go to line:")
        h.write("6")
        h.press("Enter")
        captured = h.screenshot()
        c = captured.splitlines()[1]
        assert "for x in range(10):" in c


def test_cutev_goto_line_no_exist(tmpdir):
    tf = tmpdir.join("foo.py")
    data = sample_file_medium()
    tf.write(data)
    with Runner(*run_cutev(tf.strpath), height=11) as h:
        h.await_text("foo.py")
        h.await_text("# sample python 3 file")
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
        h.await_text("# sample python 3 file")
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
        h.await_text("Error file not found")


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

