from setuptools import setup

APP = ['gumma.py']
DATA_FILES = ['phone.png','phone_orange.png']
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps',
                 'mechanize',
                 'bs4',
                 'urllib2',
                 'cookielib',
                 're',
                 'keyring',
                 'webbrowser'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    # options={'py2app': OPTIONS},
    # setup_requires=['py2app'],
)
