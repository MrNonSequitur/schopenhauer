from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
buzz = Keys.SPACE
chat = '/'
enter = Keys.RETURN

# define various methods to be used in interpretting the website
def get_raw_breadcrumb():
        return browser.find_element_by_class_name('breadcrumb').text
def parse_breadcrumb(raw_breadcrumb):
        return raw_breadcrumb.split("/Edit\n")[0]

# navigate to the website
browser = webdriver.Firefox()
browser.get('http://protobowl.com/schopenhaus') # make this a command line arg at some point. Make the default 'schopenhauer' eventually
assert 'schopenhaus' in browser.title #sanity check. remove/rework eventually
assert 'Protobowl' in browser.title

#set name to Schopenhauer
elem = browser.find_element_by_id('username')  # find the username box
elem.clear()
#elem.send_keys(Keys.CONTROL + 'a' + Keys.NULL) # clear the username box. This is a backup method
elem.send_keys('Schopenhauer' + Keys.RETURN)

while True:
	breadcrumb = parse_breadcrumb(get_raw_breadcrumb())
	#quit because this loop isn't finished
	raw_input()
	browser.quit()
	raw_input()
	break
	#features below this point are not yet started
	fingerprint = parse_fingerprint(get_fingerprint())
	buzz_in(guess_answer(breadcrumb, fingerprint))
	read_real_answer()
	sleep(1) # let it be known that this sleep is an ugly way to do this.


        

