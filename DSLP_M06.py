import os # access to file system through the operating system
import re # regular expessions 
import magic # encoding detection (install libmagic with brew if on a mac)
from lxml import etree # XML and DTD parser
from bs4 import BeautifulSoup # HTML parser

# load files (M05)

dtd = etree.DTD(open('data/card.dtd')) 

htmldata = None
with open('data/card.html') as htmlcontent:
    # does not like filenames as input
    htmldata = BeautifulSoup(htmlcontent, 'html.parser')

# prepare to alter contents (M04 & M05)

original = '@email.ca' # what we no longer want
pattern = re.compile(original, re.S)
replacement = '@something.org'# what we want instead

# check encodings, fix if necessary (M01)

check = False # can be made to work on Linux and Mac, not Windows
if check: 
    m = magic.open(magic.MAGIC_MIME_ENCODING)
    m.load()

directory = 'data/batch/'

success = 0
error = 0

logfile = open('log.txt', 'w')

filelisting = os.listdir(directory)
for filename in filelisting:
    if '.xml' == filename[-4:] and 'aux' not in filename: # no backup files, no auxiliary files
        filename = directory + filename
        
        # we read as bytes since we do not wish to assume encoding
        with open(filename, 'rb') as source:
            filecontent = source.read() # not a string, just a bunch of bytes

            # validate the original file contents (M02)
            valid = dtd.validate(etree.XML(filecontent))
            if valid:
                enc = 'utf-8'
                if check:
                    enc = m.buffer(filecontent) # investigate the encoding
                    print(f'The encoding of {filename} appears to be {enc}', file = logfile)
                else:
                    xmlcontent = filecontent.decode(enc) # now we can get the decoded string
                
                # carry out replacements 
                modcontent = re.sub(pattern, replacement, xmlcontent)
                
                # access byte contents of the xml (M02)      
                xmldata = etree.XML(str.encode(modcontent))
                
                # validate the modified file contents (M02)
                assert dtd.validate(xmldata) # in case we broke something with the regex
            
                # populate the target documents  (M03)
                for target in [ 'name', 'title', 'email' ]:
                    s = htmldata.new_tag('div', **{'class': target })
                    s.string = xmldata.find(target).text
                    htmldata.select('.' + target)[0].replace_with(s)
                    
                # save the target documents (M05)
                htmlfile = filename.replace('.xml', '.html')
                with open(htmlfile, 'w') as destination:
                    print(htmldata, file = destination)
                print(f'Populated HTML document ready at {htmlfile}', file = logfile)

                # save the modified versions of the XML documents (M05)
                auxfile = filename.replace('.xml', '_aux.xml')
                with open(auxfile, 'w') as destination:
                    print(modcontent, file = destination)
                print(f'Modified XML document ready at {auxfile}', file = logfile)

                success += 1
                
            else: # it was not valid
                
                print(f'The XML in f{filename} does not match the provided DTD', file = logfile)                
                print(dtd.error_log.filter_from_errors(), file = logfile)

                error += 1
                
        print('- - - - -', file = logfile)

logfile.close()
pl = '' if success < 2 else 's'
print(f'{success} XML file{pl} correctly modified and populated into HTML')
pl = '' if error < 2 else 's'
print(f'{error} invalid file{pl}')
