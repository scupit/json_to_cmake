from json.decoder import JSONDecodeError
import sys
import write_organizer

def ifArgsDo(func):
    if len(sys.argv) <= 1:
        print("ERROR: A directory argument must be passed, but wasn't")
    else:
        func(sys.argv)

def main(args):
    try:
        write_organizer.writeCMakeFiles(args[1])
        print("CMakeLists.txt file written successfully!")
    except FileNotFoundError as e:
        print("ERROR: JSON file not found in directory", args[1],"... make sure the file exists and is located in your project's root directory. Also make sure the directory argument given IS the root directory of you project")
        pass
    except JSONDecodeError as e:
        # print("Problem with JSON: ", str(e)[str(e).index(':'):])
        print("Problem with JSON:", str(e))
        pass

ifArgsDo(main)
