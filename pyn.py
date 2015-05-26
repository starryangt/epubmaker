from soupy import Soupy, Q
import urllib.request
import urllib.error
import codecs
import os
import copy

def safe_chars(string):

    '''
    given a string, returns a string with characters that cannot be used in
    a windows filepath removed.
    '''

    valid_chars = "-_().abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return ''.join(c for c in string if c in valid_chars)

def download(url, retry = 5):

    '''
    downloads a file given a url. Tries 5 times before raising an error
    '''
    
    attempts = 0
    while attempts <= retry:
        try:
            f = urllib.request.urlopen(url)
            return f
            break
        except urllib.error.URLError as Error:
            attempts += 1
    raise NameError('Download Failed')

def make_dir(directory):

    '''
    given a filepath, check if the directory exists and if
    not, create it.
    '''

    if not os.path.exists(directory):
        os.makedirs(directory)

def format_xhtml(body, title = "Lorem Ipsum"):

    '''
    given a body of html, correctly returns a string with
    proper xhtml formatting
    '''

    return """<?xml version="1.0" encoding="utf-8" standalone="no"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
	<head>
		<title></title>
	</head> 
	<body>
		<h3 align="right">{}</h3>
		<hr />
		{}
	</body>
</html>
    """.format(title, body)


def write_img(image, filepath = "temp.jpg"):
    
    '''
    given an image and a filepath, writes to disk
    '''

    with open(filepath, 'wb') as f:
        f.write(image.read())

def write_html(html, filepath = "temp.html"):

    '''
    given html and a filepath, writes to disk
    '''

    with codecs.open(filepath, 'w', 'UTF-8') as f:
        f.write(html)

def has_string(tag):

    '''
    tests if a tag has a string or not. Is used for ugly sites which don't
    put text into <p> tags like normal people
    '''
    t = tag.name.val()
    if t == 'script' or t == 'a' or t == 'li' or t == 'style':
        return False
    elif len(tag.text.val()) > 12:
        return True
    return False


def is_junk(tag):

    '''
    detects if the tag is 'junk' or not. Junk tags include social media
    buttons, comments, random javascript, etc. Not perfect, but kills most things
    '''
    name = tag.name.val()
    if 'table' in name: return True
    elif 'th' in name: return True
    for key, value in tag.attrs.val().items():
        for meta in value:
            metadata = meta.lower()
            if 'comment' in metadata: return True
            elif 'reply' in metadata: return True
            elif 'google' in metadata: return True
            elif 'share' in metadata: return True
            elif 'twitter' in metadata: return True
            elif 'facebook' in metadata: return True
            elif 'social' in metadata: return True
    return False


def grab_from_start_tag(start_tag):

    '''
    a generator that yields all the tags from a starting tag forward
    '''

    for sibling in start_tag.next_siblings:
        for child in sibling.find_all():
            pass
            #yield child
        yield sibling

def is_null(tag):

    '''
    Soupy does weird things sometimes. .notnull() does not work. Like,
    at all. But this does.
    '''
    
    if tag.name.val():
        return True
    return False

def find_start_tag(soup):
    
    '''
    companion function for grab_from_start_tag. Tries to find the tag
    where 'content' (i.e text) first starts by detecting large,
    consecutive strings of tags which contain text.
    '''

    for tag in soup.find_all():
        correct = 0
        fail = 0
        for siblings in tag.next_siblings.filter(is_null):
            if has_string(siblings) and not is_junk(siblings):
                correct += 1
            else:
                fail += 1
                
            if correct > 10:
                return tag
            elif fail > 2:
                break

    raise NameError('Cannot find content')

def correct_content_generator(soup):
    
    '''
    generator that uses find_start_tag and grab_from_start_tag to
    (hopefully) yield only relevant content
    '''

    start = find_start_tag(soup)
    for tag in grab_from_start_tag(start):
        yield tag

def only_p_generator(soup):

    '''
    generator that simply yields all p tags
    '''

    for p in soup.find_all(['p', 'img']):
        yield p

def everything_generator(soup):

    '''
    generator that yields everything with text
    '''

    for tag in soup.find_all().filter(has_string):
        yield tag

def get_img_url(img):
    
    '''
    given an img tag, returns the src
    '''
    
    for key, value in img.attrs.val().items():
        if key == 'src':
            return value
    raise NameError('Could not find href')

def detect_img_tag(tag):

    '''
    detects if a tag is a <img>
    '''
    
    if tag.name.val() == 'img':
        return True
    for img in tag.find_all('img'):
        return True
    return False

def img_tag_generator(tag):

    '''
    generator that yields all img tags in a tag
    because people stick <img>'s in <div>'s and stuff
    '''

    if tag.name.val() == 'img':
        yield tag
    else:
        for img in tag.find_all('img'):
            yield img

def page_from_list_generator(url_list):

    '''
    given a list of urls to pages, yields the page
    '''

    for url in url_list:
        yield Page(return_href_from_a(url))

def baka_page_from_list_generator(url_list):

    '''
    given a list of urls to pages, yields baka pages
    '''

    for url in url_list:
        yield BakaPage(return_href_from_a(url))

def download_pages(page_generator):

    '''
    given a generator of pages, downloads the images and writes the
    tags into an xhtml. A 'temp' directory is created because
    I don't want to mess with the actual library to make 
    an actual temp directory.
    Yeah, everything is saved as a .jpg. Oh well.
    '''

    make_dir('temp')


    htmlfiles = []
    imgfiles = []
    chapter_titles = []
    
    for page in page_generator:

        chapter_titles.append(page.title)
        
        for i, image in enumerate(page.img_url):
            img = download(image)
            imgfilepath = 'temp/' + page.safe_title + str(i) + '.jpg'
            write_img(img, imgfilepath)
            imgfiles.append(imgfilepath)
            
        content = format_xhtml(page.return_html_as_string(), page.title)
        filepath = 'temp/' + page.safe_title + '.xhtml'
        write_html(content, filepath)
        htmlfiles.append(filepath)
        
    return htmlfiles, imgfiles, chapter_titles

def return_href_from_a(tag):
    for key, value in tag.attrs.items():
        if 'href'in key:
            return value


def is_tag_not_anchor(tag):
    for key, value in tag.attrs.val().items():

        if 'href'in key:
            return True
    return False 

def return_all_links(url):    
    soup = Soupy(download(url))
    return [tag for tag in soup.find_all('a') if is_tag_not_anchor(tag)]

    
class Page:

    '''
    class that represents a page of the site/epub/whatever
    contains a list of all the tags and a list of links to
    images used to later download them
    '''

    def __init__(self, url, generator = correct_content_generator):

        self.url = url
        self.tags = []
        self.img_url = []

        soup = Soupy(download(url))

        self.title = soup.find('title').text.val() or 'Lorem Ipsum'
        self.safe_title = safe_chars(self.title)
        try:
            find_start_tag(soup)
        except NameError as err:
            generator = only_p_generator
        
        for tag in generator(soup):
            self.retrieve_file(tag)
        
    def return_html_as_string(self):
        return '\n'.join([str(tag.val()) for tag in self.tags])

    def retrieve_file(self, tag):
        if detect_img_tag(tag):
            for img in img_tag_generator(tag):
                filepath = '../Images/' + self.safe_title + str(len(self.img_url)) + '.jpg'
                self.img_url.append(get_img_url(img))
                img['src'] = filepath
                self.tags.append(img)
        elif has_string(tag) and not is_junk(tag):
            self.tags.append(tag)

class BakaPage(Page):
    
    '''
    class that is made for the quirks of Bakatsuki pages
    Inherits from page
    '''

    def __init__(self, url):
        super(BakaPage, self).__init__(self.fix_baka_link(url))
    
    def convert_baka_thumbnail_to_full(self, url):

        '''
        Don't ask me how this works, I did this a while ago
        it's probably awful, but it does work, so I'll keep
        copypasting it
        '''

        unfUrl = url.replace('/thumb', '')
        find_ending = url[-4:]
        a = unfUrl.find(find_ending)
        return unfUrl[0:a+4]

    def fix_baka_link(self, url):

        '''
        because some bakatsuki links are relative and some
        are absolute. whhhhhyyyyy
        converts all urls to absolute
        '''

        if not 'http' in url:
            return 'https://www.baka-tsuki.org' + url
        else:
            return url

    def retrieve_file(self, tag):
        if detect_img_tag(tag):
            for img in img_tag_generator(tag):
                try:
                    img['width'] = ""
                    img['height'] = ""
                except:
                    #yeah, yeah, antipattern, just a little laziness
                    pass
                filepath = '../Images/' + self.safe_title + str(len(self.img_url)) + '.jpg'
                fixed_url = self.fix_baka_link(self.convert_baka_thumbnail_to_full(get_img_url(img)))
                self.img_url.append(fixed_url)
                img['src'] = filepath
                self.tags.append(img)
        elif has_string(tag) and not is_junk(tag):
            self.tags.append(tag)
    
