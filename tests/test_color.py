import testenv
from papers import color

def perf_color():
    s = str(range(1000))
    for _ in range(5000000):
        color.dye(s, color.red)

if __name__ == '__main__':
    perf_color()