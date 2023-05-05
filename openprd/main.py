from openprd import ReadPRD
import argparse

arg_parser = argparse.ArgumentParser(
    prog="OpenPRD-Python",
    description="Reads OpenPRD formatted files and returns JSON object.",
)

arg_parser.add_argument('-b', '--build', required=False, help='Build prd file',
                        action='store_true')

arg_parser.add_argument('-o', '--outputfile', metavar="File to Output",
                        help='Output JSON to file', required=False, 
                        )

arg_parser.add_argument('-v', '--version', action='version')
arg_parser.add_argument('input_file')
# arg_parser.add_argument('output_file')



def main(args):
    prd = ReadPRD(args.input_file)
    if args.outputfile:
        prd.write_json(args.outputfile)
    else:
        print(prd.prd_json)

if __name__ == "__main__":
    main(arg_parser.parse_args())