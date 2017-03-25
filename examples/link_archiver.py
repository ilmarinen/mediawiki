from mediawiki import Bot


if __name__ == "__main__":
    bot = Bot("http://wiki.zay.io", "username", "password")
    bot.login()
    # bot.edit()
    bot.append_url("Sandbox_test", "http://www.google.com")
    bot.append_url("Sandbox_test", "http://www.stratfor.com")
