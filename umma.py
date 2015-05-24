import rumps
import mechanize
from bs4 import BeautifulSoup
import urllib2 
import cookielib
import re
import keyring
import GChartWrapper as GC
import os

DIMS = (225,125)

def get_UM_usage(user, passwd):
    # DEBUG_LOCAL = True   # debug with local umma.html saved from account screen
    DEBUG_LOCAL = False
    if not DEBUG_LOCAL:
        cj = cookielib.CookieJar()
        br = mechanize.Browser()
        br.set_cookiejar(cj)
        br.open("https://gousmobile.com/my/account")

        br.select_form(nr=0)
        br.form['username'] = user
        br.form['password'] = passwd
        br.submit()
        content = br.response().read()
    else:
        file = open('umma.html', 'r')
        content = file.read()
        file.close()

    soup = BeautifulSoup(content)
    mins = soup.findAll("div", {"class": "planBox min"})[0]
    #mins_n = mins.findAll("span", {"class": "number"}).pop().text
    mins_pct = mins.findAll("span", {"class": "info"}).pop().text.split("%")[0]

    txt = soup.findAll("div", {"class": "planBox text"})[0]
    #txt_n = txt.findAll("span", {"class": "number"}).pop().text
    txt_pct = txt.findAll("span", {"class": "info"}).pop().text.split("%")[0]

    mb = soup.findAll("div", {"class": "planBox data"})[0]
    #mb_n = mb.findAll("span", {"class": "number"}).pop().text
    mb_pct = mb.findAll("span", {"class": "info"}).pop().text.split("%")[0]

    date = soup.findAll("div", {"class": "planInfoBox"})[0]
    label = date.findAll("label")
    days_left = label[0].text.split("\n")[0].strip().split(" ")[0]
    date_end = label[0].find().text.split(" ")
    date_end = date_end[3] + ' ' + date_end[4].split(",")[0]
    days_pct = date.findAll("span", {"class": "sr-only"}).pop().text.split(" ")[0].split("%")[0]

    return {'Minutes': [mins_pct],
            'SMS': [txt_pct],
            'Data': [mb_pct],
            'Date': [days_pct, days_left, date_end]}


class umma(rumps.App):

    def get_GC(self, field, pct):
        G = GC.Meter(float(pct))
        G.fill('bg','s','00000000')
        G.label(str(pct))
        G.size(DIMS[0],DIMS[1])
        f = app.open(field+'.png', 'w')
        G.save(f.name)
        return f.name

    @rumps.timer(60*30)  # every 30 minutes
    #@rumps.timer(3)  # every 3 seconds
    def t(self, sender):
        user, passwd = app.get_user_pass(self)
        dat = get_UM_usage(user, passwd)
        #print dat
        m = self.menu

        m.clear()

        m.add("Service ends in " + dat['Date'][1] + " days on " + dat['Date'][2])
        m.add("Date")
        icon = app.get_GC("Date", 100-int(dat["Date"][0]))
        m["Date"].set_callback(app.add)
        m["Date"].set_icon(icon, dimensions=DIMS)
        m["Date"].title = ""
        m.add(None)

        str = ['Minutes', 'SMS', 'Data']
        for s in str:
            m.add(dat[s][0] + " " + s + " Unused")
            m.add(s)
            #print s, dat[s][0]
            icon = app.get_GC(s, dat[s][0])
            m[s].set_callback(app.add)
            m[s].set_icon(icon, dimensions=DIMS)
            m[s].title = ""
            m.add(None)

        m.add("About")
        m["About"].set_callback(app.about)
        m.add("Prefs")
        m["Prefs"].set_callback(app.prefs)
        m.add("Quit")
        m["Quit"].set_callback(rumps.quit_application)

        low = [dat["Minutes"][0], dat["SMS"][0], dat["Data"][0]]
        low = [float(l) for l in low]
        days = float(dat["Date"][0])
        # Less % of something than % of days? Warn me.
        thresh = (min(low) < (100-days))
        if thresh:
            self.icon = "phone_orange.png"
        else:
            self.icon = "phone.png"            


    @rumps.clicked("About")
    def about(self, _):
        rumps.alert("umma",
                    "US Mobile Menu App: Track usage\n" +
                    "http://github.com/mankoff/umma")

    @rumps.clicked("Prefs")
    def prefs(self, _):
        app.get_user_pass(self)

    @rumps.clicked("Add")
    def add(self, _):
        import webbrowser
        url = "https://gousmobile.com/my/account"
        webbrowser.open(url, new=2)

    def get_user_pass(self, _):
        try:
            with app.open('user', 'r') as f:
                user = f.read()
        except IOError:
            w = rumps.Window(message='US Mobile login name/email',
                             title='Login',
                             dimensions=(250,24),
                             default_text="your@email.com")
            r = w.run()
            user = r.text

        passwd = keyring.get_password("umma", user)
        if passwd is None:
            w = rumps.Window(message='US Mobile login password',
                             title='Login',
                             dimensions=(250, 24),
                             default_text="Your password")
            r = w.run()
            passwd = r.text
            keyring.set_password("umma", user, passwd)
        with app.open('user', 'w') as f:
            f.write(user)
        return user, passwd


if __name__ == "__main__":
    app = umma("umma",
               quit_button=rumps.MenuItem('Quit', key='q'),
               icon="phone.png")
    # app.menu = ["DateInfo", "Date",
    #             None,
    #             "Minutes Info", "Minutes",
    #             None,
    #             "SMS Info", "SMS",
    #             None,
    #             "Data Info", "Data",
    #             None,
    #             #"Add",
    #             #None,
    #             "About", "Prefs"]

    # check if first run and/or no credentials
    app.get_user_pass("umma")
    app.run(debug=True)

