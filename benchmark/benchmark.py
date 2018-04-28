import json
import yaml
import os.path
from subprocess import Popen, PIPE
import ps_mem

def getDecodedOutput(programWithArgs):
    process = Popen(programWithArgs, stdout=PIPE)
    (output, err) = process.communicate()
    return output.decode("utf-8")

def getPathToClang():
    pathToClang = ''
    configFileName = 'benchmark.json'
    try:
        config = json.load(open(configFileName, 'r'))
        pathToClang = config['clang']
    except FileNotFoundError:
        print("'", configFileName, "' file not found")
    
    if pathToClang == '':
        presumedClangLocation = "../../../../../../build/bin/clang"
        if os.path.isfile(presumedClangLocation):
            pathToClang = presumedClangLocation
        else:
            print('fatal error: could not locate clang (maybe you forgot to add it to benchmark.json?).')
            exit(1)

    output = getDecodedOutput([pathToClang, "-cc1", "--help"]) 

    if output.find("-templight-dump") == -1:
        print("fatal error:", pathToClang, "doesn't have the '-templight-dump' flag avaible")
        exit(1)

    if output.find("-templight-profile") == -1:
        print("fatal error:", pathToClang, "doesn't have the '-templight-profile' flag avaible")
        exit(1)
    
    return pathToClang

def getYAMLEntries(pathToClang, fileName):
    output = getDecodedOutput([pathToClang, "-cc1", "-templight-dump", fileName])
    split = output.split('---')
    ret = []
    for entry in split:
        if entry != "":
            ret.append(yaml.load(entry))
    return ret

def printTable(table):
    colLength = []
    rowCount = len(table)
    colCount = len(table[0])
    for i in range(0, colCount):
        col = []
        for j in range(0, rowCount):
            col.append(table[j][i])
        colLength.append(len(max(col, key=len)))
    
    for row in table:
        line = ""
        for i in range(0, len(row)):
            line = line + ' ' +  row[i].ljust(colLength[i], ' ')
        print(line)

def benchmark(clangWithArgs):
    p = Popen(clangWithArgs, stdout=PIPE)

    privates = []
    shareds = []
    while p.poll() == None:
        private, shared, _, _, = ps_mem.getMemStats(p.pid)
        privates.append(private)
        shareds.append(shared)

    maxPrivate = int(max(privates))
    maxShared = int(max(shareds))
    avaragePrivate = int(sum(privates) / len(privates))
    avarageShared = int(sum(shareds) / len(shareds))

    print("benchmark results for run", ' '.join(clangWithArgs))
    
    table = [
        ["",                  "priv",                              "sh"              ],
        ["maxMem",            str(maxPrivate),                     str(maxShared)    ],
        ["avarage:",          str(avaragePrivate),                 str(avarageShared)],
        ["",                  "",                                  ""                ],
        ["",                  "combined",                          ""                ],
        ["combinedMaxMem:",   str(maxPrivate + maxShared),         ""                ],
        ["combinedAvarage:",  str(avaragePrivate + avarageShared), ""                ]
    ]
    
    printTable(table)
    print("\n======================================\n")


clang = getPathToClang()
print("note: using clang:", clang)
testFile = "benchmarkTestFile.cpp"

benchmark([clang, '-c',  testFile])
benchmark([clang, '-cc1', '-templight-dump', testFile])
benchmark([clang, '-cc1', '-templight-dump', '-templight-profile', testFile])

