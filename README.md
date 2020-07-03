## cutev

command line text viewer using curses

### Usage:
```
usage: cutev [-h] filename [filename ...]

positional arguments:
  filename    file name(s) to view
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
