import sys

if(len(sys.argv) != 6):
    exit()

src = sys.argv[1]
dst = sys.argv[2]
dep = sys.argv[3]
arr = sys.argv[4]
date = sys.argv[5]

info = f'{{"src":"{src}", "dst":"{dst}", "dep":"{dep}", "arr":"{arr}", "date":"{date}", "status":"incomplete"}}'
results = f'[{{"src":"{src}", "dst":"{dst}", "dep":"{dep}", "arr":"{arr}", "price":"5000"}}]'

filename = 'test.txt'
faresFile = open(filename, 'w')
faresFile.write(f'{{"info":{info},"results":{results}}}')
faresFile.close()
