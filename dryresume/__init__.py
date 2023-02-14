import sys, pathlib
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

if __name__ == '__main__':
    from . import main
    main()
