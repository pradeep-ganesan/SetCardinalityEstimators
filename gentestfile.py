from random import randint

def generate():
    with open('./testfile2.txt', 'w') as fp:
        i = 0
        while i < 1:
            j = 0
            while j < 10000:
                fp.write('{} '.format(randint(1, 4000)))
                j += 1
            i+=1

def main():
    generate()
    
if __name__ == '__main__':
    main()