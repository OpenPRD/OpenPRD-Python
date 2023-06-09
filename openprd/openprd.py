import os
import json
from pathlib import Path
from zipfile import ZipFile
from extruct.w3cmicrodata import MicrodataExtractor


class OpenPRDFile:
    def __init__(self, file_in, file_out=None):
        self.file_in = Path(file_in)
        self.file_out = Path(file_out) if file_out else None
        self.PRDfile = self._open_file()   
        
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


class ReadPRD(OpenPRDFile):
    """Reads data tags from main document and the creating a JSON object as
       prd_json also contains method write_json to write to a file."""
    def __init__(self, file_in, file_out=None):
        super().__init__(file_in, file_out)
        self.resources = self._parse_resources()
        self.prd_data = self._retrieve_microdata()
        self.prd_json = json.dumps(self.prd_data[0])

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
        mde = MicrodataExtractor()
        return mde.extract(pull_main_doc)
        # return microdata.get_items(pull_main_doc)[0]

    def write_json(self, file_loc=None):
        if file_loc:
            f_path = Path(file_loc)
        elif self.file_out and not file_loc:
            f_path = Path(self.file_out)
        elif not self.file_out or not file_loc:
            raise FileNotFoundError('Path to file not provided.')
        
        if not f_path.parent.exists():
            try:
                os.mkdir(f_path.parent)
            except PermissionError as err:
                print(err, "Check for proper permission for directory")
            
        with open(f_path, "w") as f:
            f.write(self.prd_json)
            print(f"Successfully wrote resume data to {f_path}")


class BuildPRD(OpenPRDFile):
    """This class provides methods to validate and package a prd file"""
    def __init(self, file_in, file_out):
        super().__init__(file_in, file_out)