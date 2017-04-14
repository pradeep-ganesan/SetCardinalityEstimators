from random import randint

def generate():
    with open('testfile.txt', 'w') as fp:
        i = 0
        while i < 1000:
            j = 0
            while j < 10:
                fp.write('{} '.format(randint(0, 256)))
                j += 1
            i+=1

def main():
    generate()
    
if __name__ == '__main__':
    main()