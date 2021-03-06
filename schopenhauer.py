#!/usr/bin/env python
# coding=utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, time
import json
import argparse
import unicodedata

#parse command-line arguments
parser = argparse.ArgumentParser(description="Schopenhauer is a bot that autonomously plays Protobowl, a digital version of Quizbowl, which is a trivia game.")
parser.add_argument("--name", "-n", help="set the name of the bot (default \"Schopenhauer\")")
parser.add_argument("--room", "-r", help="set the Protobowl.com room the bot will operate in (default \"Schopenhauer\"). This will be overidden by the url option, if both are given")
parser.add_argument("--url", "-u", help="set the url the bot will operate on (default \"http://protobowl.com/Schopenhauer\"). This overrides the room option, if both are given. Make sure to include the scheme of the url, such as \"http\"")
parser.add_argument("--times", "-t", type=int, help="set the number of times the main loop of the bot will run (If this option is missing or set to a non-positive number (including 0), the bot will run forever. Please note that the bot will not record any changes to its knowledge if it is terminated by a keyboard interupt or other external pressures)")
parser.add_argument("--delay", "-d", type=float, help="set the amount of seconds the bot will wait for answering a question. This can help him appear to be human. This is set to 1 by default, so that Schopenhauer will avoid rate-limitation. This feature was added because Eric Zhu wanted the d")
parser.add_argument("--verbose", "-v", action="store_true", help="make vague comments about the internal operation of Schopenhauer as it runs")
parser.add_argument("--input", "-i", help="read in knowledge from the specified file (defaults to knowledge.json in the current working directory)")
parser.add_argument("--output", "-o", help="write out knowledge to the specified file (defaults to knowledge.json in the current working directory)")
parser.add_argument("--centennial", "-c", help="write out the bot's knowledge to file whenever the times counter is divisible by 100", action="store_true")
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
if args.delay:
	delay = args.delay
else:
	delay = 1
if args.liszt:
	lisztomania = True
else:
	lisztomania = False
if args.verbose:
	verbose = True
else:
	verbose = False
if args.centennial:
	centennial = True
else:
	centennial = False
if args.input:
	file_in = args.input
else:
	file_in = "knowledge.json"
if args.output:
	file_out = args.output
else:
	file_out = "knowledge.json"

# define various methods to be used in interpretting the website
# the breadcrumb stuff could probably be refactored, but it should work as-is.
def vprint(text):
	if verbose:
		print(text)

def buzz(text):
	top_bundle = browser.find_elements_by_class_name('bundle')[0] #the top bundle is arbitrarily sent keys because we need to send keys to *something*
	if browser.find_element_by_class_name('buzzbtn').is_enabled():
		top_bundle.send_keys(" ")
		vprint("buzzing in")
		sleep(.5) # let the guess box appear
		top_bundle.send_keys(text + '\n')	
	
def get_knowledge(i):
	bundle = browser.find_elements_by_class_name('bundle')[i]
	qid = bundle.get_attribute("class").split("qid-")[1].split(" ")[0]
	if i > 0: #this feels inelegant, but works
		vprint("Now I'm going to get the raw breadcrumb...")
		raw_breadcrumb = bundle.find_element_by_class_name('breadcrumb').text
		vprint("raw_breadcrumb: " +raw_breadcrumb)
		answer = raw_breadcrumb.split("/Edit\n")[1]
		answer = unicodedata.normalize('NFKD', answer).encode("ascii", "ignore").decode()
		answer = answer.split("(")[0] #get only the first part of the answer, not the parenthetical note
		answer = answer.split("[")[0] #get only the first part of the answer, not the parenthetical note
		answer = answer.strip() #strip whitespace characters from around the answer (presumably in between the parenthetical note and the real answer)
		answer = answer.strip(u"\u2018").strip(u"\u2019").strip(u"\u201c").strip(u"\u201d").strip("'").strip("\"") # strip all quote marks, which occasionally cause Protobowl to reject correct answers
	else:
		answer = ''
	return {'qid': qid, 'answer': answer}

def get_raw_breadcrumb(i):
	return browser.find_elements_by_class_name('breadcrumb')[i].text

def get_breadcrumb(i):
	return get_raw_breadcrumb(i).split("/Edit\n")[0]

def get_answer(i):
	if i > 0: #this feels inelegant, but works
		return get_raw_breadcrumb(i).split("/Edit\n")[1]
	else:
		return ''

#define how to work with knowledge
knowledge = {}
try:
	with open(file_in, 'r') as f:
		knowledge = json.load(f)
		#I'm not a huge fan of json (sexprs are better), but this is better than my original plan of calling eval on whatever we find in knowledge.json and hoping it's a data structure
except Exception as e:
	print(str(e))
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
def write_out(filename, object=knowledge):
	with open(filename, 'w') as f:
		json.dump(object, f, sort_keys=True) # keys sorted to reduce deltas in our version control system

# navigate to the website
browser = webdriver.Firefox()
browser.get(url)
while not browser.find_element_by_id('username').is_displayed():
	sleep(.1) #wait for the page to load
# set name
elem = browser.find_element_by_id('username') # find the username box
elem.clear()
elem.send_keys(name + Keys.RETURN)

#click button to start questions
try:
	browser.find_element_by_class_name("btn-large").click()
except Exception as e:
	vprint("The button couldn't be clicked, assuming it's already pressed...")

#main loop:
#must use buttons to identify game state, as the state markers are not displayed on some screen sizes
#must use try click because is_displayed doesn't seem to work the way we want it to.
try:
	try:
		answered = 0
		while times != 0: # deliberately allow negative numbers to cause it to loop forever
			times-=1
			try:
				browser.find_element_by_class_name('resume').click()	
				vprint("hit resume button")
			except: vprint("couldn't hit resume")
			curr_well = browser.find_element_by_class_name('well')#track well to determine the current question. the well is arbitrarily sent keys because we need to send keys to *something*
			k = get_knowledge(0)
			guess = guess_answer(k['qid']) #this should return an empty string if there is no answer
			if guess == '':
				try:
					browser.find_element_by_class_name('skipbtn').click()	
					vprint("hit skip button")
				except: vprint("couldn't hit skip")
			else:
				buzz(guess)
				vprint(str(times)+"("+str(time())+")"+": "+k['qid']+":"+guess)
				answered+=1
			try:
				a = get_knowledge(1)
				record_answer(a['qid'], a['answer'])
			except Exception as e:
				vprint("When getting knowledge: "+str(e))
			if times + 1 % 100 == 0 and centennial:
				vprint("Only "+str(times)+" times left to go. Writing out knowledge to " + str(file_out)+"... ("+str(len(knowledge))+" pairs)")
				write_out(file_out)
			if times + 1 % 2000 == 0: #arbitrary value
                                browser.get(url) #proto disconnects you after a while
			sleep(delay)
			try:
				browser.find_element_by_class_name('nextbtn').click()	
				vprint("hit next button")
			except: vprint("couldn't hit next")
			
		vprint("knowledge is now "+str(len(knowledge))+ " pairs, which is "+str(len(knowledge)-initial_knowledge_length)+" more than it was initially.")
		vprint("Schopenhauer tried to answer a question "+str(answered)+" times")
		write_out(file_out)
	except Exception as e:
		vprint(str(e))
except:
	vprint("exception in main loop.\nAborting...")
	try:
		vprint("Writing knowledge to knowledge.tmp.json just in case...")
		write_out("knowledge.tmp.json")
	except Exception as e:
		vprint(str(e))
		vprint("Well, that didn't work. Dang.")
browser.quit()
