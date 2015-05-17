import rumps
import mechanize
from bs4 import BeautifulSoup
import urllib2 
import cookielib
import re
import keyring

def get_UM_usage(user, passwd):
    LOCAL = True   # debug with local umma.html saved from account screen
    LOCAL = False
    if not LOCAL:
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
    mins = soup.findAll("div",{"class":"planBox min"})[0]
    mins_n = mins.findAll("span",{"class":"number"}).pop().text
    mins_pct = mins.findAll("span",{"class":"info"}).pop().text

    txt = soup.findAll("div",{"class":"planBox text"})[0]
    txt_n = txt.findAll("span",{"class":"number"}).pop().text
    txt_pct = txt.findAll("span",{"class":"info"}).pop().text

    mb = soup.findAll("div",{"class":"planBox data"})[0]
    mb_n = mb.findAll("span",{"class":"number"}).pop().text
    mb_pct = mb.findAll("span",{"class":"info"}).pop().text

    date = soup.findAll("div",{"class":"planInfoBox"})[0]
    label = date.findAll("label")
    days_left = label[0].text.split("\n")[0].strip()
    date_end = label[0].find().text
    days_pct = date.findAll("span",{"class":"sr-only"}).pop().text.split(" ")[0]

    return {'Minutes':[mins_n, mins_pct],
            'SMS':[txt_n, txt_pct],
            'Data':[mb_n, mb_pct],
            'Date':[date_end,days_left, days_pct]}


class umma(rumps.App):

    @rumps.timer(60*30) # every 30 minutes
    def t(self,sender):
        with app.open('user', 'r') as f:
            user = f.read()
        if user == '':
            w = rumps.Window(message='US Mobile login name/email',
                             title='Login',
                             default_text="your@email.com")
            r = w.run()
            user = r.text
            w = rumps.Window(message='US Mobile login password',
                             title='Login',
                             default_text="Your password")
            r = w.run()
            passwd = r.text
            keyring.set_password("umma", user, passwd)
            with app.open('user', 'w') as f:
                f.write(user)
        else:
            passwd = keyring.get_password("umma", user)
            
        dat = get_GUM_usage(user,passwd)
        m = self.menu

        str = ['Minutes','SMS','Data','Date']
        low = False
        for s in str:
            m[s].clear()
            m[s].add(dat[s][0])
            m[s].add(dat[s][1])
            if s == "Date":
                m[s].add(dat[s][2])

        for s in str[0:3]:
            if float(dat[s][0]) < 10:
                low = True
        if low == True:
            self.icon = "phone_orange.png"
        else:
            self.icon = "phone.png"            

    @rumps.clicked("About")
    def about(self, _):
        rumps.alert("umma","US Mobile Menu App: Track usage\nhttp://github.com/mankoff/umma")
        
    @rumps.clicked("Prefs")
    def prefs(self, _):
        w = rumps.Window(message='US Mobile login name/email',
                         title='Login',
                         default_text="your@email.com")
        r = w.run()
        user = r.text
        w = rumps.Window(message='US Mobile login password',
                         title='Login',
                         default_text="Your password")
        r = w.run()
        passwd = r.text
        keyring.set_password("umma", user, passwd)
        with app.open('user', 'w') as f:
            f.write(user)


    @rumps.clicked("Add")
    def add(self,_):
        import webbrowser
        url = "https://gousmobile.com/my/account"
        webbrowser.open(url,new=2)

if __name__ == "__main__":
    app = umma("umma",
                quit_button=rumps.MenuItem('Quit', key='q'),
                icon="phone.png")
    app.menu = [{"Minutes":["fetching..."]},
                {"SMS":["fetching..."]},
                {"Data":["fetching..."]},
                {"Date":["fetching..."]},
                None,
                'Add',None,'About','Prefs']
    app.run(debug=True)

