'''
Parser from UBC library catalogue printed output. Produces JSON
metadata from an HTML file. See DESC below for details.
'''


import argparse
import json
import xml.etree.ElementTree

import bs4
from .version import __version__

DESC = '''
UBC Library catalogue output parser.

Uses the output from creating a print record created by the following procedure:
    * Searching the library catalogue (https://webcat.library.ubc.ca/vwebv/searchBasic)
    * Saving the record by performing the following operations:
        Print/Full Record/Click To Print/Cancel/View Source/
    * Save the resulting source code as HTML

The resultant output will be a JSON representation of the records
in the print output.

Limitations:

If the publication information  is stored in a MARC 264 field, then
the record export does not include publication information as this field
is inexplicably not exported in the "full" record.

The publication date is also derived from the call number if possible,
but not all call numbers have dates, so not all records will have dates
in the JSON output.
'''

STRIP = '\n  ./\t'

def argp():
    '''
    Argument parser
    '''
    description = DESC
    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('infile',
                        help='HTML input file')
    parser.add_argument('outfile',
                        help=('Output JSON file name. An extension of .json '
                              'will be appended if it doesn\'t exist')
                        )
    parser.add_argument('-v','--version', action='version',
                        version=__version__,
                        help='Show version number and exit')
    return parser

class Record(dict):
    '''
    Class representing a bibliographic record
    '''
    def __init__(self, brec):
        '''
        Initialize:
        brec = xml.etree.ElementTree.ElementTree.Element
            This is the <div> containing the full bibliographic record
        '''
        self.brec = brec
        self['title'] =  [x for x in
                          self.brec.findall('.//div')
                          if x.attrib.get('class')
                          == 'bibTitle'][0].find('p').text.strip(STRIP)
        self['purl'] =  self.brec.text.replace('Permanent URL:', '').strip(STRIP)
        desired_meta = dict(variant_title = 'Variant Title',
                            publication = 'Published/Created',
                            author = 'Author/Creator',
                            subject = 'Subject(s)',
                            call_number = 'Call Number',
                            format = 'Format',
                            isbn = 'ISBN:')
        for key, value in desired_meta.items():
            self[key] = self.clean(value)
        self['derived_year'] = self.derived_year('Call Number')

    def clean(self, datatype:str) -> str:
        '''
        Parses data according to the string in the bib record.
        Returns clean data as a string
        '''
        cleandata = [x for x in self.brec.findall('.//li')
                     for y in x.findall('span') if datatype in y.text]
        if cleandata:
            cleandata = cleandata[0][1].text.strip(STRIP)
            cleandata = list(filter(None, [x.strip(STRIP) for x in cleandata.split('\n')]))
            if len(cleandata) <=1 and cleandata:
                cleandata = cleandata[0]
        else:
            cleandata = None
        return cleandata

    def derived_year(self, datatype:str) -> int:
        '''
        Hunts for a date at the end of a call number string, and
        if the last characters are digits returns them as date.
        '''
        call = self.clean(datatype)
        if call:
            try:
                derived_year = int(call[-4:])
            except ValueError:
                derived_year = None
            return derived_year
        return None

def main():
    '''
    Command line application
    '''
    parser = argp()
    args = parser.parse_args()
    if not args.outfile.lower().endswith('.json'):
        args.outfile += '.json'

    with open(args.infile, mode='r', encoding='utf-8') as fil:
        cleaner = fil.read().replace('<br>','\n').replace('<br/>','\n')

    soup = bs4.BeautifulSoup(cleaner, 'html.parser')
    tree = xml.etree.ElementTree.ElementTree(xml.etree.ElementTree.fromstring(soup.prettify()))
    root = tree.getroot()

    #Note for anybody who is not familiar with ElementTree
    #alldivs = root.findall('.//div') #must use XPATH expr to find all
    #is the same as
    #alldivs = [x for x in root.iter('div')]

    bib_records =[x for x in root.iter('div') if x.attrib.get('class') =='bibliographicData']
    records = dict(records = [])
    for bib_rec in bib_records:
        records['records'].append(Record(bib_rec))

    with open(args.outfile, 'w', encoding='utf-8', newline='') as out:
        json.dump(records, out)

if __name__ == '__main__':
    main()
