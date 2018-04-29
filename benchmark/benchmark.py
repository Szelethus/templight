import json
import yaml
import os.path
from subprocess import Popen, PIPE
import ps_mem
import os
import sys

def getDecodedOutput(programWithArgs):
    process = Popen(programWithArgs, stdout=PIPE)
    (output, err) = process.communicate()
    return output.decode("utf-8")

def parseConfigFile(configFileJson):
    pathToClang = ''
    try:
        config = json.load(open(configFileJson, 'r'))
        pathToClang = config['clang']
    except FileNotFoundError:
        print("fatal error: '", configFileJson, "' file not found")
        exit(1)
    
    if pathToClang == '':
        presumedClangLocation = "../../../../../../build/bin/clang"
        if os.path.isfile(presumedClangLocation):
            pathToClang = presumedClangLocation
        else:
            print('fatal error: could not locate clang')
            print('maybe you forgot to add it to benchmark.json?')
            exit(1)

    print("note: using clang:", pathToClang)
    
    output = getDecodedOutput([pathToClang, "-cc1", "--help"]) 

    if output.find("-templight-dump") == -1:
        print("fatal error:", pathToClang, "doesn't have the '-templight-dump' flag avaible")
        print("maybe you forgot to update clang to a more recent version?")
        exit(1)

    if output.find("-templight-profile") == -1:
        print("fatal error:", pathToClang, "doesn't have the '-templight-profile' flag avaible")
        print("maybe you forgot to apply the 'templight_clang_patch.diff'?")
        exit(1)
    
    testFile = config['testfile']
    if os.path.isfile(testFile) == False:
        print("fatal error: testfile '", testFile, "'doesn't exist")
        print("maybe a typo in'", configFileJson, "'?")
        exit(1)

    return pathToClang, testFile

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

def benchmark(clangWithArgs, numberOfRuns = 15):
    privates = []
    shareds = []
    devnull = open(os.devnull, 'w')

    for i in range(0, numberOfRuns):
        p = Popen(clangWithArgs, stdout=devnull)

        while p.poll() == None:
            private, shared, _, _, = ps_mem.getMemStats(p.pid)
            privates.append(private)
            shareds.append(shared)

    maxPrivate = int(max(privates))
    maxShared = int(max(shareds))
    avaragePrivate = int(sum(privates) / len(privates))
    avarageShared = int(sum(shareds) / len(shareds))

    print("\n======================================\n")
    print("benchmark results after", numberOfRuns, "runs of", ' '.join(clangWithArgs))
    print("")

    table = [
        ["",                  "private",                           "shared"          ],
        ["maxMem",            str(maxPrivate),                     str(maxShared)    ],
        ["avarage:",          str(avaragePrivate),                 str(avarageShared)],
        ["",                  "",                                  ""                ],
        ["",                  "combined",                          ""                ],
        ["combinedMaxMem:",   str(maxPrivate + maxShared),         ""                ],
        ["combinedAvarage:",  str(avaragePrivate + avarageShared), ""                ]
    ]
    
    printTable(table)


clang, testFile = parseConfigFile('benchmark.json')

benchmark([clang, '-c',  testFile])
benchmark([clang, '-c', '-Xclang', '-templight-dump', testFile])
benchmark([clang, '-c', '-Xclang', '-templight-dump', '-Xclang', '-templight-profile', testFile])
