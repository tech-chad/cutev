## cutev

command line text viewer using curses

### Usage:
```
usage: cutev [-h] [-l] filename [filename ...]

positional arguments:
  filename           file name(s) to view

optional arguments:
 -h, --help              show this help message and exit
 -l, --linenumbers  show line numbers

```

### Commands:
- ```q``` to quit
- ```Arrow Up``` move one line up
- ```Arrow Down``` move one line down
- ```Arrow Right``` scroll right if line is wider than screen
- ```Arrow Left``` scroll left
- ```Page Up``` move one page up
- ```Page Down``` move one page down
- ```g``` Enter line number to go to
- ```l``` Show line numbers
- ```ctrl-n``` Next open file
- ```ctrl-b``` Previous open file
- ```ctrl-x``` Close current open file
- ```ctrl-a``` Close all files except current
