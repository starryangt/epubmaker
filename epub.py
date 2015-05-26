import os
import uuid
import zipfile

def addCFilepath(filename, fType = "HTML"):
	actualFile = os.path.basename(filename)
	if fType == "HTML":
			return "Text/"+str(actualFile)
	elif fType == "IMG":
		return "Images/"+str(actualFile)

class Chapter:

	def __init__(self):
		self.id = ''
		self.src = ''
		self.directory =''
		self.html = ''
class TocItem:
	def __init__(self, playOrder):
		self.play = playOrder
		self.title = ""
		self.src = ""
		self.depth = 0
		self.id = ""
class imgItem:
	def __init__(self):
		self.src = ''
		self.id = ''
		self.directory = ''
		self.type = 'images/jpeg'



class Epub:
	def __init__(self):

		self.author = None
		self.meta = []

		self.creationDate = None
		self.publisher = None
		self.language = "US/EN"
		self.rights = None
		self.title = "Default"


		self.img = []
		self.html = []

		self.cover = None
		self.coverXHTML = None
		self.toc = []
		self.spine = []

		self.contOpf = None
		self.tocNcx = None
	def addAuthor(self, author):
		self.author = author

	def addTitle(self, title):
		self.title = title
	def addCreationDate(self,cDate):
		self.creationDate = cDate
	def addPublisher(self, pub):
		self.publisher = pub
	def addLanguage(self, lan):
		self.language = lan
	def addRights(self, rights):
		self.rights = rights
	def addCover(self, cover):
		img = imgItem()
		img.src = addCFilepath(cover, 'IMG')
		img.id = os.path.basename(cover)
		img.directory = cover
		self.cover = img

		xhtml = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>Cover</title>
    <style type="text/css"> img { max-width: 100%; } </style>
  </head>
  <body>
      <img src="../Images/Cover.jpg"/>
  </body>
</html>"""

		self.coverXHTML = xhtml

	def addHTML(self, filepath, title = "Chapter"):
		#Create an instiance of the Chapter class, give it data, and then append it
		item = Chapter()
		item.id = "ch"+str(len(self.html)+1)
		#What the id is for each item doesn't actually matter, so for simplicities sake I'll just use ch0,ch1,ch2...
		item.src = addCFilepath(filepath)
		#The src for both content and toc files are relative
		item.directory = filepath
		item.html = "FUCKPYTHONENCODING"
		self.html.append(item)


		toc = TocItem(len(self.toc))
		toc.title = title
		#Note that os.path.basename does NOT work correctly on linux. You'll need to us an alternative method.
		toc.src = addCFilepath(filepath)
		toc.id = "ch"+str(len(self.html))
		self.toc.append(toc)

	def addIMG(self, filepath):
		img = imgItem()
		img.src = addCFilepath(filepath, 'IMG')
		img.id = os.path.basename(filepath)
		img.directory = filepath
		self.img.append(img)



	def createToc(self):
		head = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="urn:uuid:{}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle>
    <text>{}</text>
  </docTitle>
  <navMap>""".format(str(uuid.uuid4()), self.title)

		for tocEntry in self.toc:
			head += """\n    <navPoint id="navPoint-{}" playOrder="{}">
      <navLabel>
        <text>{}</text>
      </navLabel>
      <content src="{}"/>
    </navPoint>""".format(tocEntry.play, str(tocEntry.play+1), tocEntry.title, tocEntry.src)

		head += """\n  </navMap>
</ncx>"""
		self.tocNcx = head



	def createContent(self):
		head = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <dc:identifier id="BookId" opf:scheme="UUID">urn:uuid:{}</dc:identifier>""".format(str(uuid.uuid4()))

		if self.title:
			head += '\n    <dc:title>{}</dc:title>'.format(self.title)
		if self.author:
			head += '\n    <dc:creator opf:file-as="{}" opf:role="aut">{}</dc:creator>'.format(self.author, self.author)
		if self.publisher:
			head += '\n    <dc:publisher>{}</dc:publisher>'.format(self.publisher)
		if self.language:
			head += '\n    <dc:language>{}</dc:language>'.format(self.language)
		if self.rights:
			head += '\n    <dc:rights>{}</dc:rights>'.format(self.rights)
		head += '\n    <meta content="Cover.jpg" name="cover"/>'
		head += """\n  </metadata>
  <manifest>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>"""
			
		if self.cover:
			head += '\n    <item href="Text/Cover.xhtml" id="Cover.xhtml" media-type="application/xhtml+xml"/>'
		for htmlEntry in self.html:
			head += '\n    <item href="{}" id="{}" media-type="application/xhtml+xml"/>'.format(htmlEntry.src, htmlEntry.id)
		if self.cover:
			head += '\n    <item href="Images/Cover.jpg" id="Cover.jpg" media-type="image/jpeg"/>'
		for imgEntry in self.img:
			head += '\n    <item href="{}" id="{}" media-type="image/jpeg"/>'.format(imgEntry.src, imgEntry.id)

		head += """\n  </manifest>
  <spine toc="ncx">
  	<item idref="Cover.xhtml"/>"""

		for tocEntry in self.toc:
			head += '\n    <itemref idref="{}"/>'.format(tocEntry.id)

		head += """\n  </spine>
  <guide>
  	<reference href="Text/Cover.xhtml" title="Cover" type="cover"/>
  </guide>
</package>"""
		self.contOpf = head
	def printhead(self):
		print("HEAD")

	def createEpub(self):
		zipF = zipfile.ZipFile(self.title+".epub", 'w')
		zipF.write('mimetype')
		zipF.write('container.xml', 'META-INF/container.xml')
		if self.cover:
			zipF.write(self.cover.directory, 'OEBPS/Images/Cover.jpg')
			zipF.writestr('OEBPS/Text/Cover.xhtml', self.coverXHTML)
		for htmlEntry in self.html:
			zipF.write(htmlEntry.directory, 'OEBPS/'+htmlEntry.src)
		for imgEntry in self.img:
			zipF.write(imgEntry.directory, 'OEBPS/'+imgEntry.src)
		Epub.createContent(self)
		Epub.createToc(self)
		zipF.writestr('OEBPS/content.opf', self.contOpf)
		zipF.writestr('OEBPS/toc.ncx', self.tocNcx)

		zipF.close()

















