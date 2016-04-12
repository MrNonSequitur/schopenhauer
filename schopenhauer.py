#!/usr/bin/env python
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, time
import json
import argparse

#parse command-line arguments
parser = argparse.ArgumentParser(description="Schopenhauer is a program that autonomously plays Protobowl, a digital version of Quiz Bowl, which is a quiz game.")
parser.add_argument("--name", "-n", help="set the name of the bot (Default \"Schopenhauer\")")
parser.add_argument("--room", "-r", help="set the Protobowl.com room the bot will operate in (Default \"Schopenhauer\"). This will be overidden by the url option, if both are given")
parser.add_argument("--url", "-u", help="set the url the bot will operate on (Default \"protobowl.com/Schopenhauer\"). This overrides the room option, if both are given. Make sure to include http or whatever!")
parser.add_argument("--times", "-t", type=int, help="set the number of times the main loop of the bot will run (If this option is missing or set to a non-positive number, the bot will run basically forever. Please note that the bot will likely not record any changes to its knowledge if it is terminated by a keyboard interupt or other external pressures)")
parser.add_argument("-v", "--verbose", action="store_true", help="make vague comments about the internal operation of Schopenhauer as it runs")
parser.add_argument("--liszt", "-l", help="enable Lisztomania", action="store_true")
args = parser.parse_args()
if args.name:
	name = args.name
else:
	name = "Schopenhauer"
if args.url:
	url = args.url
elif args.room:
	url = "http://protobowl.com/" + args.room
else:
	url = "http://protobowl.com/Schopenhauer"
if args.times:
	times = args.times
else:
	times = -1
if args.liszt:
	lisztomania = True
else:
	lisztomania = False
if args.verbose:
	verbose = True
else:
	verbose = False

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
#DO NOT use buzz as an alias for Keys.SPACE; that will reference the function "buzz" instead
chat = '/'
enter = Keys.RETURN
skip = 's'

# define various methods to be used in interpretting the website
# the breadcrumb stuff could probably be refactored, but it should work as-is.
def vprint(text):
	if verbose:
		print(text)

def buzz(text):
	top_bundle = browser.find_elements_by_class_name('bundle')[0] #the top bundle is arbitrarily sent keys because we need to send keys to *something*
	top_bundle.send_keys(Keys.SPACE)
	sleep(1) #ugly sleep to let the box appear (might be nessecary)
	top_bundle.send_keys(text + Keys.RETURN)
	top_bundle.send_keys("n")

def get_knowledge(i):
	bundle = browser.find_elements_by_class_name('bundle')[i]
	qid = bundle.get_attribute("class").split("qid-")[1].split(" ")[0]
	if i > 0: #this feels inelegant, but works
		raw_breadcrumb = bundle.find_element_by_class_name('breadcrumb').text
		answer = raw_breadcrumb.split("/Edit\n")[1]
		answer = answer.split("(")[0] #get only the first part of the answer, not the parenthetical note
		answer = answer.split("[")[0] #get only the first part of the answer, not the parenthetical note
	else:
		answer = ''
	return {'qid': qid, 'answer': answer} #maybe changes this to {qid:answer} in the future

def get_raw_breadcrumb(i):
        return browser.find_elements_by_class_name('breadcrumb')[i].text

def get_breadcrumb(i):
	return get_raw_breadcrumb(i).split("/Edit\n")[0]

def get_answer(i):
	if i > 0: #this feels inelegant, but works
	        return get_raw_breadcrumb(i).split("/Edit\n")[1] # We may need to scrape the answers differently, so as to only take things before ( or [. We'll see.
	else:
		return ''

# define methods to deal with guessing
knowledge = {}
with open('knowledge.json', 'r') as f:
		knowledge = json.load(f)
		#I'm not a huge fan of json (sexprs are better), but this is better than my original plan of calling eval on whatever we find in knowledge.json and hoping it's a data sctructure
initial_knowledge_length = len(knowledge)
vprint("knowledge currently consists of "+str(len(knowledge))+" pairs.")
def guess_answer(qid):
	if lisztomania:
		return "Franz Lizst"
	if qid in knowledge:
		return knowledge[qid]
	return ""
def record_answer(qid, answer):
	knowledge[qid] = answer
		



# navigate to the website
browser = webdriver.Firefox()
browser.get(url)
sleep(1) #let the page render
assert browser.find_element_by_id('username').is_displayed() # sanity check
# set name
elem = browser.find_element_by_id('username') # find the username box
elem.clear()
elem.send_keys(name + Keys.RETURN)

#click button to start questions
try:
	browser.find_element_by_class_name("btn-large").click()
except Exception as e:
	vprint("The button couldn't be clicked, assuming it's already pressed...")

try:
	answered = 0
	while times != 0: # deliberately allow negative numbers to cause it to loop forever
		times-=1
		top_bundle = browser.find_elements_by_class_name('bundle')[0] #the top bundle is arbitrarily sent keys because we need to send keys to *something*
		# browser.find_elements_by_xpath("//*[contains(@class, \"bundle\")]")	

		k = get_knowledge(0)
		guess = guess_answer(k['qid']) #this should return an empty string if there is no answer, b/c I can't be bothered to learn error handling
		if guess == '':
			top_bundle.send_keys(skip)
		else:
			vprint(str(times)+"("+str(time())+")"+": "+k['qid']+":"+guess)  
			buzz(guess)
			answered+=1
		sleep(1) #this is ugly, but it works
		try:
			a = get_knowledge(1)
			vprint("recording {'"+a['qid']+": '"+a['answer']+"'}")
			record_answer(a['qid'], a['answer'])
		except Exception as e:
			vprint("When getting knowledge: "+str(e))
		if times % 100 == 0:
			vprint("Only "+str(times)+" times left to go")
	vprint("knowledge is now "+str(len(knowledge))+ " pairs, which is "+str(len(knowledge)-initial_knowledge_length)+" more than it was intially.")
	vprint("Schopenhauer tried to answer a question "+str(answered)+" times, out of "+str(times)+" chances.")
	vprint("len(knowledge)-answered is "+str(len(knowledge)-answered)+", which should be equal to the initial knowledge length of "+str(initial_knowledge_length)+" but you know how these things go.")
	with open('knowledge.json', 'w') as f:
		json.dump(knowledge, f)
except Exception as e:
	vprint("exception in main loop:"+str(e)+"\nAborting...")
	with open('knowledge.tmp.json', 'w') as f:
		vprint("attempting to write knowledge to knowledge.tmp.json just in case...")
		json.dump(knowledge, f)
browser.quit()
