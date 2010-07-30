import gtk
import webkit
import gobject

gobject.threads_init()

w = gtk.Window()

wv = webkit.WebView()

sw = gtk.ScrolledWindow()
w.add(sw)
sw.add(wv)

urls = open('urls.txt').read().splitlines()

def loadpage():
    wv.load_uri(urls.pop())
    if not urls:
        gtk.main_quit()
        return False
    else:
        return True

gobject.timeout_add(10000, loadpage)
loadpage()

w.resize(640, 480)

w.show_all()
gtk.main()

