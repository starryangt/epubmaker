from PySide.QtCore import*
from PySide.QtGui import*
import sys
import pyn
import epub
import shutil
from threading import Thread

qt_app = QApplication(sys.argv)        

instruction = '''Hi. Enter in the URL of an index page (i.e  a page that
holds the urls of all the pages that you want to download. Navigation
bars count). Click 'Download Index'. Select the pages that you want to
download, type in the title, author, etc. (or not, it's not neccesary)
and click compile. That's it!

If it's a Baka Tsuki page, then toggle the button on. It fixes the
urls (for whatever reason, some of the links are relative and some
are absolute) and converts the thumbnails into the fullsized
images.

The "algorithm" should only take relevant content, but, if it fails,
the fallback is to simply take all the <p> and <img> tags.

It handles most blogspot weirdness, but not all. Experiment!

Order of the chapters in the EPUB is determined by the order in which
you select them, so be careful withat that.
'''


class UrlItem(QListWidgetItem):
    def __init__(self, string, url):
        super(UrlItem, self).__init__()
        self.setText(string)
        self.text = string
        self.url = url

class WebDown(QWidget):

    def __init__(self):
        super(WebDown, self).__init__()
        #Variables not relating to the GUI
        self.index_url = ""
        self.url_list = []
        self.cover = ""
        self.title = ""
        self.author = ""
        self.baka = False

        self.setWindowTitle('Epub-maker')
        self.list_of_urls = QListWidget(self)
        
        self.list_of_urls.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.top_layout = QVBoxLayout()
        self.top_layout.addWidget(self.list_of_urls)

        self.button_layout = QHBoxLayout()
        self.download_index = QPushButton("Download Index")
        self.download_index.clicked.connect(self.download) 
        
        self.compile_epub = QPushButton("Compile")
        self.compile_epub.clicked.connect(self.comp)

        self.baka_button = QPushButton("Baka Tsuki")
        self.baka_button.setCheckable(True)
        self.baka_button.clicked.connect(self.baka_toggle)
        self.button_layout.addWidget(self.download_index)
        self.button_layout.addWidget(self.compile_epub)
        self.button_layout.addWidget(self.baka_button)

        self.input_layout = QVBoxLayout()
        self.index_down = QLineEdit(self) 
        self.index_down.setPlaceholderText("Enter Index URL") 
        self.index_down.textChanged.connect(self.index_url_changed)

        self.author_input = QLineEdit(self)
        self.author_input.setPlaceholderText("Enter Author Name")
        self.author_input.textChanged.connect(self.author_changed)

        self.title_input = QLineEdit(self)
        self.title_input.setPlaceholderText("Enter Title")
        self.title_input.textChanged.connect(self.title_changed)

        self.cover_input = QLineEdit(self)
        self.cover_input.setPlaceholderText("Enter Cover URL")
        self.cover_input.textChanged.connect(self.cover_changed)

        self.input_layout.addWidget(self.index_down)
        self.input_layout.addWidget(self.cover_input)
        self.input_layout.addWidget(self.title_input)
        self.input_layout.addWidget(self.author_input)

        self.entire_layout = QVBoxLayout()

        self.entire_layout.addLayout(self.top_layout)
        self.entire_layout.addLayout(self.button_layout)
        self.entire_layout.addLayout(self.input_layout)
        

        self.info = QLabel(instruction)
        self.status = QLabel("Idle")

        self.label_layout = QVBoxLayout()
        self.label_layout.addWidget(self.info)
        self.label_layout.addWidget(self.status)
        
        self.whole_layout = QHBoxLayout()
        self.whole_layout.addLayout(self.entire_layout)
        self.whole_layout.addLayout(self.label_layout)
        self.setLayout(self.whole_layout)

    @Slot()
    def download(self):
        self.status.setText("Downloading...")
        Thread(target=self.download_worker).start()

    def download_worker(self):
        try:
            self.url_list = pyn.return_all_links(self.index_url)
        except NameError as err:
            self.status.setText("Error: " + str(err))
            return
        except:
            self.status.setText("Error: " + str(sys.exc_info()[0]))
            return
        self.list_of_urls.clear()
        for url in self.url_list:
            self.list_of_urls.addItem(UrlItem(url.text.val(), url.val()))
        self.status.setText("Done")
    @Slot()
    def comp(self):
        self.status.setText("Starting compilation...")
        Thread(target=self.compile_epub_worker).start()
    def download_cover(self, epub, url):
        pyn.write_img(pyn.download(url), 'temp/Cover.jpg')
        epub.addCover('temp/Cover.jpg')
    def compile_epub_worker(self):
        download_list = [url.url for url in self.list_of_urls.selectedItems()]
        try:
            if self.baka:
                html, files, chapter = pyn.download_pages(pyn.baka_page_from_list_generator(download_list))
            else:
                html, files, chapter = pyn.download_pages(pyn.page_from_list_generator(download_list))
        except NameError as err:
            self.status.setText("Error: " + str(err))
            return
        except:
            self.status.setText("Error: " + str(sys.exc_info()[0]))
            return
        
        newEpub = epub.Epub()
        newEpub.addTitle(self.title)
        newEpub.addAuthor(self.author)
        if self.cover:
            try:
                self.download_cover(newEpub, self.cover)
            except:
                self.status.setText("Cover download failed, continuing...")

        for i, html in enumerate(html):
            newEpub.addHTML(html, chapter[i])
        for img in files:
            newEpub.addIMG(img)
        newEpub.createEpub()
        self.status.setText("Done")
        shutil.rmtree('temp')
    @Slot()
    def index_url_changed(self, string):
        self.index_url = string
    
    @Slot()
    def author_changed(self, string):
        self.author = string
    
    @Slot()
    def title_changed(self, string):
        self.title = string
    
    @Slot()
    def cover_changed(self, string):
        self.cover = string
    
    @Slot()
    def baka_toggle(self):
        self.baka = not self.baka
        print(self.baka)
    def run(self):
        self.show()
        qt_app.exec_()
if __name__ == '__main__':
    app = WebDown()
    app.run()
    sys.exit()

