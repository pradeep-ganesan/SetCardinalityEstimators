from random import randint

def generate():
    with open('testfile.txt', 'w') as fp:
        i = 0
        while i < 10:
            j = 0
            while j < 500:
                fp.write('{} '.format(randint(0, 65536)))
                j += 1
            i+=1

def main():
    generate()
    
if __name__ == '__main__':
    main()