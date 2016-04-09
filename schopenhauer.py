#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import json

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
buzz = Keys.SPACE
chat = '/'
enter = Keys.RETURN
skip = 's'

# define various methods to be used in interpretting the website
# the breadcrumb stuff could probably be refactored, but it should work as-is.
def buzz(text):
	top_bundle = browser.find_elements_by_class_name('bundle')[0] #the well is arbitrarily sent keys because we need to send keys to *something*
	top_bundle.send_keys(buzz)
	sleep(1) #ugly sleep to let the box appear (might be nessecary)
	input_box = browser.find_elements_by_class_name('guess_input')[0]
	input_box.send_keys(text + enter)

def get_knowledge(i):
	return {'qid': get_qid(i), 'answer': get_answer(i)}

def get_raw_breadcrumb(i):
        return browser.find_elements_by_class_name('breadcrumb')[i].text

def get_breadcrumb(i):
	return get_raw_breadcrumb(i).split("/Edit\n")[0]

def get_answer(i):
	if i > 0: #this feels inelegant, but works
	        return get_raw_breadcrumb(i).split("/Edit\n")[1] # We may need to scrape the answers differently, so as to only take things before ( or [. We'll see.
	else:
		return ''
def get_qid(i):
	bundle = browser.find_elements_by_class_name('bundle')[i]
	return bundle.get_attribute("class").split("qid-")[1].split(" ")[0]

# define methods to deal with guessing
knowledge = {}
with open('knowledge.json', 'r') as f:
		knowledge = json.load(f)
		#I'm not a huge fan of json (sexprs are better), but this is better than my original plan of calling eval on whatever we find in knowledge.json and hoping it's a data sctructure
def guess_answer(qid):
	if qid in knowledge:
		return knowledge[qid]
	return ""
def record_answer(qid, answer):
	knowledge[qid] = answer
	print(qid +": "+answer)
def write_out():
	with open('knowledge.json', 'w') as f:
		json.dump(knowledge, f)
		

# navigate to the website
browser = webdriver.Firefox()
browser.get('http://protobowl.com/r/schopenhaus') # make this a command line arg at some point. Make the default 'schopenhauer' eventually.
assert 'schopenhaus' in browser.title #sanity check. remove/rework eventually
assert 'Protobowl' in browser.title

#set name to Schopenhauer
elem = browser.find_element_by_id('username')  # find the username box
elem.clear()
elem.send_keys('Schopenhauer' + Keys.RETURN)

#TODO: handle pressing the big green button that starts the questions

for x in range(0, 3): #should be 'while True:' or something eventually
	
	# browser.find_elements_by_xpath("//*[contains(@class, \"bundle\")]")	

	k = get_knowledge(0)
	guess = guess_answer(k['qid']) #this should return an empty string if there is no answer, b/c I can't be bothered to learn error handling
	if guess == '':
		top_bundle.send_keys(skip)
	else:
		buzz(guess)
	sleep(1) # let it be known that this sleep is an ugly way to do this.
	a = get_knowledge(1)
	record_answer(a['qid'], a['answer'])
write_out()
browser.quit()


        

