num = 90

def f1():
    global num
    num = 2

def f2():
    print(num)

if __name__ == '__main__':
    f2()
    f1()
    f2()