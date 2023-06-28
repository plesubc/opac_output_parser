# IMPORTANT
# Full record print
# Procedure:
# Print/Full Record/Click To Print/Cancel/View Source/
# Save resulting html
# Note: if the publication is stored in a MARC 264 field, then 
# the record export does not include publication information
# Publication date is also derived from the call number if possible,
# but not all call numbers have dates

import xml.etree.ElementTree
import bs4
import sys
import json
STRIP = '\n  ./' 
with open('tmp/many_records.html', mode='r', encoding='utf-8') as f:
    #with open(sys.argv[1], mode='r', encoding='utf-8') as f:
    cleaner = f.read().replace('<br>','\n').replace('<br/>','\n')
    
#bs4 is needed because the HTML is badly formed and bs4 will clean it.
soup = bs4.BeautifulSoup(cleaner, 'html.parser')
tree = xml.etree.ElementTree.ElementTree(xml.etree.ElementTree.fromstring(soup.prettify()))
root=tree.getroot()


#alldivs = root.findall('.//div')#must use XPATH expr
#is the same as
#alldivs = [x for x in root.iter('div')]

bib_records =[x for x in root.iter('div') if x.attrib.get('class') =='bibliographicData'] 

outjson = {'records':[]} 
for brec in bib_records:
    #so easy 🙄
    #fields needed: title, PURL, subject headings, publication year, record date
    #['bibTitle']
    title = [x for x in brec.findall('.//div') if x.attrib.get('class') == 'bibTitle'][0].find('p').text.strip(STRIP)
    purl =  brec.text.replace('Permanent URL:', '').strip(STRIP)
    subj = [ x for x in brec.findall('.//li') for y in x.findall('span') if 'ubj' in y.text][0] 
    #subjlist = [x for x in subj.findall('span') if x.get('class') == 'subfieldData'][0].text.strip()
    subjlist = [x for x in subj.findall('span') if x.get('class','') == 'subfieldData']
    #finalsub = subjlist[0].text.strip() + [x for x in subjlist[0].findall('br')]
    finalsub=[x.strip(STRIP) for x in subjlist[0].text.split('\n')]
    finalsub=[x for x in finalsub if x]
    #Published == 'Published/Created:'
    pub = [x for x in brec.findall('.//li') for y in x.findall('span') if 'Published/Created:' in y.text]
    if pub:
        pub = pub[0][1].text.strip(STRIP)
    else:
        pub = None 

    call = [x for x in brec.findall('.//li') for y in x.findall('span') if 'Call Number' in y.text]
    if call:
        call = call[0][1].text.strip(STRIP)
    else:
        call = None 
    if call:
        try:
            derived_year = int(call[-4:])
        except ValueError:
            derived_year = None
            
    recjson = dict(title=title, 
                   purl=purl,
                   subject=finalsub, 
                   publication=pub,
                   call_number=call,
                   derived_year=derived_year)
    outjson['records'].append(recjson)
with open('tmp/outjson.json', 'w', encoding='utf-8') as f:
    json.dump(outjson, f)
