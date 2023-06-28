## UBC Library catalogue output parser.

Uses Python 3.6+

**Installation:**

`pip install git+https://github.com/plesubc/opac_output_parser.git@master`

**Where to find everything**

Well, if you followed the above, you can probably figure out that everything is at
<https://github.com/plesubc/opac_output_parser>.

### Command line application `opac_output_parser`

If you've followed the installation instructions, and you've installed Python more or less correctly, you can invoke the application from the command line with:

`opac_output_parser`

Uses the output from creating a print record created by the following procedure:

    * Searching the library catalogue (https://webcat.library.ubc.ca/vwebv/searchBasic)
    * Saving the record by performing the following operations:
        Print/Full Record/Click To Print/Cancel/View Source/
    * Save the resulting source code as HTML

The resultant output will be a JSON representation of the records in the print output.

**Limitations:**

If the publication information  is stored in a MARC 264 field, then
the record export does not include publication information as this field
is inexplicably not exported in the "full" record.

The publication date is also derived from the call number if possible,
but not all call numbers have dates, so not all records will have dates
in the JSON output.

The application comes with help which looks like this:

```nohighlight
opac_output_parser -h
usage: opac_output_parser [-h] [-v] infile outfile

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

positional arguments:
  infile         HTML input file
  outfile        Output JSON file name. An extension of .json will be appended
                 if it doesn't exist

options:
  -h, --help     show this help message and exit
  -v, --version  Show version number and exit
```

## And if you want to use the parser in something else:

`opac_output_parser.Record`

## Record Objects

```python
class Record(dict)
```

Class representing a bibliographic record

<a id="opac_output_parser.parser.Record.__init__"></a>

#### \_\_init\_\_

```python
def __init__(brec)
```

Initialize:
brec = xml.etree.ElementTree.ElementTree.Element
    This is the <div> containing the full bibliographic record

<a id="opac_output_parser.parser.Record.clean"></a>

#### clean

```python
def clean(datatype: str) -> str
```

Parses data according to the string in the bib record.
Returns clean data as a string

<a id="opac_output_parser.parser.Record.derived_year"></a>

#### derived\_year

```python
def derived_year(datatype: str) -> int
```

Hunts for a date at the end of a call number string, and
if the last characters are digits returns them as date.

<a id="opac_output_parser.parser.main"></a>

