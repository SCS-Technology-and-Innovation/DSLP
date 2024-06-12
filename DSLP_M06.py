import os # access to file system through the operating system
import re # regular expessions 
import magic # encoding detection
from lxml import etree # XML and DTD parser
from bs4 import BeautifulSoup # HTML parser

# load files (M05)

dtd = etree.DTD('data/doc.dtd') # likes filenames as input

htmldata = None
with open('data/card.html') as htmlcontent:
    # does not like filenames as input
    htmldata = BeautifulSoup(htmlcontent, 'html.parser')

# prepare to alter contents (M04 & M05)

original = '@email.ca' # what we no longer want
pattern = re.compile(original, re.S)
replacement = '@something.org'# what we want instead

# check encodings, fix if necessary (M01)

m = magic.open(magic.MAGIC_MIME_ENCODING)
m.load()

directory = 'data/batch/'

filelisting = os.listdir(directory)
for filename in filelisting:
    if '.xml' in filename:
        filename = directory + filename
        
        # we read as bytes since we do not wish to assume encoding
        with open(filename, 'rb') as source:
            filecontent = source.read() # not a string, just a bunch of bytes
            # validate the original file contents (M02)
            dtd.validate(etree.XML(filecontent))
            
            enc = m.buffer(filecontent) # investigate the encoding
            print(f'The encoding of {filename} appears to be {enc}')
            xmlcontent = filecontent.decode(enc) # now we can get the decoded string
            
            # carry out replacements 
            modcontent = re.sub(pattern, replacement, xmlcontent)
            
            # access byte contents of the xml (M02)      
            xmldata = etree.XML(str.encode(modcontent))
            
            # validate the modified file contents (M02)
            dtd.validate(xmldata) # in case we broke something with the regex
            
            # populate the target documents  (M03)
            for target in [ 'name', 'title', 'email' ]:
                s = htmldata.new_tag('div', **{'class': target })
                s.string = xmldata.find(target).text
                htmldata.select('.' + target)[0].replace_with(s)
                
            # save the target documents (M05)
            htmlfile = filename.replace('.xml', '.html')
            with open(htmlfile, 'w') as destination:
                print(htmldata, file = destination)
            print(f'Populated file ready at {htmlfile}')
