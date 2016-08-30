#!/usr/bin/env python
# coding: utf-8
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep, time
import json
import argparse

#The Solomon Ucko Memorial Python 2/3 Input Method Compatibility Hack
try:
	input = raw_input
except NameError as e:
	pass

#parse command-line arguments
parser = argparse.ArgumentParser(description="Schopenhauer is a program that autonomously plays Protobowl, a digital version of Quizbowl, which is a quiz game.")
parser.add_argument("--name", "-n", help="set the name of the bot (Default \"Schopenhauer\")")
parser.add_argument("--room", "-r", help="set the Protobowl.com room the bot will operate in (Default \"Schopenhauer\"). This will be overidden by the url option, if both are given")
parser.add_argument("--url", "-u", help="set the url the bot will operate on (Default \"protobowl.com/Schopenhauer\"). This overrides the room option, if both are given. Make sure to include http or whatever!")
parser.add_argument("--times", "-t", type=int, help="set the number of times the main loop of the bot will run (If this option is missing or set to a non-positive number (including 0), the bot will run forever. Please note that the bot will not record any changes to its knowledge if it is terminated by a keyboard interupt or other external pressures)")
parser.add_argument("--delay", "-d", type=float, help="set the amount of seconds the bot will wait for answering a question. This can help him appear to be human. This is set to 1 by default, so that Schopenhauer will avoid rate-limitation. This feature was added because Eric Zhu wanted the d")
parser.add_argument("--verbose", "-v", action="store_true", help="make vague comments about the internal operation of Schopenhauer as it runs")
parser.add_argument("--input", "-i", help="read in knowledge from the specified file (defaults to knowledge.json in the current working directory)")
parser.add_argument("--output", "-o", help="write out knowledge to the specified file (defaults to knowledge.json in the current working directory)")
parser.add_argument("--centennial", "-c", help="write out the bot's knowledge to file whenever the times counter is divisible by 100", action="store_true")
parser.add_argument("--be_the_schopenhauer", "-b", help="enables a primitive python command line just before the main loop so one can execute python during runtime. Useful for debugging and performing transformations on the knowledge base. Somewhat dangerous", action="store_true")
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
if args.be_the_schopenhauer:
	be_the_schopenhauer = True
else:
	be_the_schopenhauer = False
	

# define various keys to be sent to protobowl as keyboard shortcuts
pause = 'p'
resume = 'r'
#DO NOT use buzz as an alias for Keys.SPACE; that will reference the function "buzz" instead
next = 'n'
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
	sleep(.5) # let the guess box appear
	top_bundle.send_keys(text + enter)
	top_bundle.send_keys("n")

def get_knowledge(i):
	bundle = browser.find_elements_by_class_name('bundle')[i]
	qid = bundle.get_attribute("class").split("qid-")[1].split(" ")[0]
	if i > 0: #this feels inelegant, but works
		raw_breadcrumb = bundle.find_element_by_class_name('breadcrumb').text
		answer = raw_breadcrumb.split("/Edit\n")[1]
		answer = answer.split("(")[0] #get only the first part of the answer, not the parenthetical note
		answer = answer.split("[")[0] #get only the first part of the answer, not the parenthetical note
		answer = answer.strip() #strip whitespace characters from around the answer (presumably in between the parenthetical note and the real answer)
		answer = answer.strip(u"\u2018").strip(u"\u2019").strip(u"\u201c").strip(u"\u201d").strip("'").strip("\"") # strip all quote marks, which occasionally cause Protobowl to reject correct answers
	else:
		answer = ''
	return {'qid': qid, 'answer': answer} #maybe changes this to {qid:answer} in the future

def get_raw_breadcrumb(i):
	return browser.find_elements_by_class_name('breadcrumb')[i].text

def get_breadcrumb(i):
	return get_raw_breadcrumb(i).split("/Edit\n")[0]

def get_answer(i):
	if i > 0: #this feels inelegant, but works
		return get_raw_breadcrumb(i).split("/Edit\n")[1]
	else:
		return ''

# define methods to deal with guessing
knowledge = {}
try:
	with open(file_in, 'r') as f:
		knowledge = json.load(f)
		#I'm not a huge fan of json (sexprs are better), but this is better than my original plan of calling eval on whatever we find in knowledge.json and hoping it's a data structure
except Exception as e:
	print(str(e))
	knowledge = {}
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
def write_out(filename):
	with open(filename, 'w') as f:
		json.dump(knowledge, f, sort_keys=True) # keys will be sorted to reduce deltas in our version control system

# navigate to the website
browser = webdriver.Firefox()
browser.get(url)
sleep(1) #let the page render
while not browser.find_element_by_id('username').is_displayed():
	sleep(.1) #wait for the page to load
# set name
elem = browser.find_element_by_id('username') # find the username box
elem.clear()
elem.send_keys(name + Keys.RETURN)

if be_the_schopenhauer:
	depth = 0
	command = ''
	prompt = ">>> "
	schelp = "Welcome to the Schopenhauer command line! This is an interpretive python session that almost works!\n\nHit enter on an empty line to exit and make Schopenhauer begin to answer questions. Type \"exit()\" to exit Schopenhauer but keep the protobowl window open. Hit Control D (or, as always, Control C) to exit Schopenhauer and close the window.\n\nType \"schelp\" to see this message again. You can also access the native python information by typing \"help\", \"copyright\", \"credits\" or \"license\" for more information."
	print(schelp)
	line = input(prompt)
	command += line 
	while(command or depth):
		if(line is ''):
			depth -= 1
		elif(line[-1] is ":"):
			depth += 1
		if(depth == 0):
			try:
				print(str(eval(command)))
			except Exception as e:
				print(str(e))
			command = ''
			prompt = ">>> "
		else:
			command += ('\n'+'\t'*depth)
			prompt = "... "+'\t'*depth
		line = input(prompt)
		command += line

#click button to start questions
try:
	browser.find_element_by_class_name("btn-large").click()
except Exception as e:
	vprint("The button couldn't be clicked, assuming it's already pressed...")

try:
	answered = 0
	while times != 0: # deliberately allow negative numbers to cause it to loop forever
		curr_well = browser.find_element_by_class_name('well')#track well to determine the current question. the well is arbitrarily sent keys because we need to send keys to *something*
		times-=1
		if browser.find_element_by_class_name('finished').is_displayed():
			curr_well.send_keys(next)
			curr_well = browser.find_element_by_class_name('well')
		k = get_knowledge(0)
		guess = guess_answer(k['qid']) #this should return an empty string if there is no answer, b/c I can't be bothered to learn error handling		
		if browser.find_elements_by_class_name('pause')[1].is_displayed(): # must match the label [1] not the button [0]
			curr_well.send_keys(resume)
		if guess == '':
			if browser.find_element_by_class_name('pausebtn').is_displayed():
				curr_well.send_keys(skip)
			else: # Schopenhauer is probably chatting accidentally
				buzz("Franz Liszt")
		else:
			vprint(str(times)+"("+str(time())+")"+": "+k['qid']+":"+guess)
			buzz(guess)
			answered+=1
		sleep(delay) #this is ugly, but it works
		try:
			a = get_knowledge(1)
			record_answer(a['qid'], a['answer'])
		except Exception as e:
			vprint("When getting knowledge: "+str(e))
		if times % 100 == 0 and centennial:
			vprint("Only "+str(times)+" times left to go. Writing out knowledge to " + str(file_out)+"... ("+str(len(knowledge))+" pairs)")
			write_out(file_out)
		
	vprint("knowledge is now "+str(len(knowledge))+ " pairs, which is "+str(len(knowledge)-initial_knowledge_length)+" more than it was intially.")
	vprint("Schopenhauer tried to answer a question "+str(answered)+" times")
	write_out(file_out)
except:
	vprint("exception in main loop.\nAborting...")
	try:
		vprint("Writing knowledge to knowledge.tmp.json just in case...")
		write_out("knowledge.tmp.json")
	except Exception as e:
		vprint(str(e))
		vprint("Well, that didn't work. Dang.")
browser.quit()
