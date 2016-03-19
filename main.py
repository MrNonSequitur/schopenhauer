#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from schopensense import guess_answer, record_answer

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
buzz = Keys.SPACE
chat = '/'
enter = Keys.RETURN
skip = 's'

# define various methods to be used in interpretting the website
def get_raw_breadcrumb():
        return browser.find_element_by_class_name('breadcrumb').text
def parse_breadcrumb(raw_breadcrumb):
        return raw_breadcrumb.split("/Edit\n")[0]
def parse_fingerprint(well):
	text = well.get_attribute('textContent') #".text" only returns visible text
	text = text.split(' ')
	fingerprint = []
	for word in text:
		fingerprint.append(len(word))
	return fingerprint
def get_prev_answer():
        prev_breadcrumb = browser.find_elements_by_class_name('breadcrumb')[1].text
	return prev_breadcrumb.split("/Edit\n")[1]
		

# navigate to the website
browser = webdriver.Firefox()
browser.get('http://protobowl.com/schopenhaus') # make this a command line arg at some point. Make the default 'schopenhauer' eventually.
assert 'schopenhaus' in browser.title #sanity check. remove/rework eventually
assert 'Protobowl' in browser.title

#set name to Schopenhauer
elem = browser.find_element_by_id('username')  # find the username box
elem.clear()
elem.send_keys('Schopenhauer' + Keys.RETURN)

while True:
	breadcrumb = parse_breadcrumb(get_raw_breadcrumb())
	well = browser.find_elements_by_class_name('well')[0]
	fingerprint = parse_fingerprint(well)
	guess = guess_answer(breadcrumb, fingerprint) #this should return an empty string if there is no answer
	if guess == '':
		well.send_keys(skip) #the well is arbitrarily sent keys because we need to send keys to *something*
	else:
		well.send_keys(buzz + guess)
	sleep(1) # let it be known that this sleep is an ugly way to do this.
	answer = get_prev_answer()
	record_answer(breadcrumb, fingerprint, answer)


        

