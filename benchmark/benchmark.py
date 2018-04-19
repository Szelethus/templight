import json
import yaml
import os.path
from subprocess import Popen, PIPE

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

clang = getPathToClang()
print("note: using clang:", clang)
entries = getYAMLEntries(clang,  "../../../test/Templight/templight-nested-memoization.cpp")

print(entries)
