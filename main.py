#!/usr/bin/env python
#TODO: Revamp the knowledge-gettting system.
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from schopensense import guess_answer, record_answer, initialize, write_out

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
buzz = Keys.SPACE
chat = '/'
enter = Keys.RETURN
skip = 's'

# define various methods to be used in interpretting the website
def get_knowledge(i):
	return {'breadcrumb': get_breadcrumb(i), 'fingerprint': get_fingerprint(i), 'answer': get_answer(i)}

def get_raw_breadcrumb(i):
        return browser.find_elements_by_class_name('breadcrumb')[i].text

def get_breadcrumb(i):
        return get_raw_breadcrumb(i).split("/Edit\n")[0]

def get_answer(i):
	if i > 0: #this feels inelegant, but works
	        return get_raw_breadcrumb(i).split("/Edit\n")[1]
	else:
		return ''

def get_fingerprint(i):
	e = browser.find_elements_by_class_name('well')[i]
	if not e.is_displayed():
		e.click()
	parse_fingerprint(e)
def parse_fingerprint(well):
	text = well.get_attribute('textContent') #".text" only returns visible text
	text = text.split(' ')
	fingerprint = []
	for word in text:
		fingerprint.append(len(word))
	return tuple(fingerprint) # must be immutible so it will hash so we can use it as a key in our dictionary

		

# navigate to the website
browser = webdriver.Firefox()
browser.get('http://protobowl.com/schopenhaus') # make this a command line arg at some point. Make the default 'schopenhauer' eventually.
assert 'schopenhaus' in browser.title #sanity check. remove/rework eventually
assert 'Protobowl' in browser.title

#set name to Schopenhauer
elem = browser.find_element_by_id('username')  # find the username box
elem.clear()
elem.send_keys('Schopenhauer' + Keys.RETURN)

for x in range(0, 30): #should be 'while True:' or something eventually
	well = browser.find_elements_by_class_name('well')[0] #the well is arbitrarily sent keys because we need to send keys to *something*
	k = get_knowledge(0)
	guess = guess_answer(k['breadcrumb'], k['fingerprint']) #this should return an empty string if there is no answer, b/c I can't be bothered to learn error handling
	if guess == '':
		well.send_keys(skip)
	else:
		well.send_keys(buzz + guess)
	sleep(3) # let it be known that this sleep is an ugly way to do this.
	a = get_knowledge(1)
	record_answer(a['breadcrumb'], a['fingerprint'], a['answer'])
write_out()


        

