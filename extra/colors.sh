#!/usr/bin/env python

print("\033[0mno color\n")

for name, flag in [('normal      : ', ''),
                   ('bold        : ', '1;'),
                   ('italics     : ', '3;'),
                   ('bold italics: ', '3;1;')]:
    print("\033[0m{}".format(name), end='')
    for code in range(8):
        print("\033[0m\033[{}3{}m {:03d} ".format(flag, code, code), end='')
    print("")


print("\033[0m")

for code in range(256):
    print("\033[33;5;0m\033[38;5;{}m {:03d} ".format(code, code), end='')

    if code <= 16:
        if (code + 1) % 8 == 0:
            print("\033[0m")
            if (code + 1) % 16 == 0:
                print("\033[0m")
    else:
        if ((code + 1) - 16) % 6 == 0:
            print("\033[0m")
            if ((code + 1) - 16) % 36 == 0:
                print("\033[0m")
