import os
import argparse
import microdata
from pathlib import Path
from zipfile import ZipFile

arg_parser = argparse.ArgumentParser(
    prog="OpenPRD-Python",
    description="Reads OpenPRD formatted files and returns JSON object.",
)

arg_parser.add_argument('-o', '--outputfile', 
                        help='Output JSON to file', required=False, 
                        action="store_true"
                        )
arg_parser.add_argument('-v', '--version', action='version')
arg_parser.add_argument('input_file')
arg_parser.add_argument('output_file')


class OpenPRDFile:
    def __init__(self, file_in, file_out=None):
        self.file_in = Path(file_in)
        self.file_out = Path(file_out) if file_out else None
        self.PRDfile = self._open_file()
        self.resources = self._parse_resources()
        self.prd_data = self._retrieve_microdata()
        self.prd_json = self.prd_data.json()
        
    def _open_file(self, read_obj=None):
        if read_obj:
            # This needs to be fixed the shouldn't have to call this twice
            # Gives zip file already closed error
            try:
                with ZipFile(self.file_in, 'r') as zip_f: 
                    return zip_f.read(read_obj)
            except FileNotFoundError as err:
                print(err)
        try:
            with ZipFile(self.file_in, 'r') as zip_f: 
                return zip_f
        except FileNotFoundError as err:
            print(err)

    def _parse_resources(self, prdfile=None):
        if not prdfile: prdfile = self.PRDfile
        
        resource_list = [i.filename for i in prdfile.filelist]
        types = {'doc_main':'.html', 'doc_style':'.css'}

        def grab_res(r_type):
            for rs in resource_list: 
                if rs[-len(r_type):].lower() == r_type:
                    resource = rs
                    break
            
            if not resource: 
                raise RuntimeError("OpenPRD file missing resources.")
            else:
                return resource
            
        resources = {x:grab_res(y) for (x,y) in types.items()} 

        return resources

    def _retrieve_microdata(self):
        pull_main_doc = self._open_file(read_obj=self.resources['doc_main'])
        return microdata.get_items(pull_main_doc)[0]

    def write_json(self, file_loc=None):
        if file_loc:
            f_path = Path(file_loc)
        elif self.file_out and not file_loc:
            f_path = Path(self.file_out)
        elif not self.file_out or file_loc:
            raise FileNotFoundError('Path to file not provided.')
        
        if not f_path.parent.exists():
            try:
                os.mkdir(f_path.parent)
            except PermissionError as err:
                print(err, "Check for proper permission for directory")
            
        with open(f_path, "w") as f:
            f.write(self.prd_json)

def main(args):
    prd = OpenPRDFile(args.input_file)
    if args.outputfile:
        prd.write_json(args.output_file)

if __name__ == "__main__":
    main(arg_parser.parse_args())