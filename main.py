import write_organizer

ifArgsDo(func):
    if len(sys.argv) <= 1:
        print("ERROR: A directory argument must be passed, but wasn't")
    else:
        func(sys.argv)

main(args):
    writeCMakeFiles(args[1])

ifArgsDo(main)
