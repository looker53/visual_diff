from selenium import webdriver


def test_00(eye):
    with webdriver.Chrome() as b:
        b.get("http://www.python.org")
        eye.check_page(b)


def test_01(eye):
    with webdriver.Chrome() as b:
        b.get("http://douban.com")
        eye.check_page(b)
