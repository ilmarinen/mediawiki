import json
import urllib
import cookielib
import requests
import datetime


class Bot(object):

    def __init__(self, *args):
        if len(args) == 3:
            url, username, password = args
            self.init(url, username, password)

    def init(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def legacy_login(self):
        api_url =\
            "{}/api.php?lgname={}&lgpassword={}&format=json&action=login".format(
                self.url, self.username, self.password)
        response = self.session.post(api_url)
        data = response.json()
        attempts = 0
        while data["login"]["result"] != "Success" and attempts < 2:
            token = data["login"]["token"]
            api_url =\
                "{}/api.php?lgname={}&lgpassword={}&format=json&action=login&lgtoken={}".format(
                    self.url, self.username, self.password, urllib.quote(token))
            response = self.session.post(api_url)
            data = response.json()
            attempts = attempts + 1

        print "Logged in"

    def login(self):
        api_url = "{}/api.php?action=query&meta=tokens&type=login&format=json".format(self.url)
        response = self.session.post(api_url)
        data = response.json()
        token = data["query"]["tokens"]["logintoken"]
        api_url = "{}/api.php?action=clientlogin&format=json".format(self.url)
        response = self.session.post(
            api_url,
            data={
                "logintoken": token,
                "loginreturnurl": self.url,
                "username": self.username,
                "password": self.password
            })
        data = response.json()
        if data["clientlogin"]["status"] == "PASS":
            print "Logged in as {}".format(data["clientlogin"]["username"])

    def edit(self):
        api_url = "{}/api.php?action=query&meta=tokens&format=json".format(self.url)
        response = self.session.post(api_url)
        data = response.json()
        csrf_token = data["query"]["tokens"]["csrftoken"]
        api_url = "{}/api.php?action=edit&format=json".format(self.url)
        payload = {
            "format": "json",
            "utf8": "",
            "appendtext": "Test text",
            "title": "Sandbox test",
            "token": csrf_token
        }
        response = self.session.post(api_url, data=payload)
        data = response.json()
        print "Edited: ", data

    def parse(self, page_title):
        api_url = "{}/api.php?action=parse&page={}&prop=sections&format=json".format(self.url, page_title)
        response = self.session.get(api_url)
        data = response.json()
        return data

    def append_url(self, page_title, url_string):
        api_url = "{}/api.php?action=query&meta=tokens&format=json".format(self.url)
        response = self.session.post(api_url)
        data = response.json()
        csrf_token = data["query"]["tokens"]["csrftoken"]

        current = datetime.datetime.now()
        current_section = current.strftime("%Y-%m")
        payload = {
            "format": "json",
            "utf8": "",
            "appendtext": "\n*{}".format(url_string),
            "title": page_title,
            "token": csrf_token
        }

        data = self.parse(page_title)
        if "error" in data and data["error"]["info"] == "The page you specified doesn't exist":
            payload["section"] = "new"
            payload["sectiontitle"] = current_section
        else:
            sections = data["parse"]["sections"]
            if len(sections) == 0:
                payload["section"] = "new"
                payload["sectiontitle"] = current_section
            else:
                section_dates = map(lambda section: datetime.datetime.strptime(section["line"], "%Y-%m"), sections)
                last_section_date = max(section_dates + [current])
                last_section_title = last_section_date.strftime("%Y-%m")
                last_sections = filter(lambda section: section["line"] == last_section_title, sections)
                if len(last_sections) > 0:
                    last_section = last_sections[0]
                    payload["section"] = last_section["number"]
                else:
                    payload["section"] = "new"
                    payload["sectiontitle"] = last_section_title

        api_url = "{}/api.php?action=edit&format=json".format(self.url)
        response = self.session.post(api_url, data=payload)
        data = response.json()
        print "Added Url: ", url_string
