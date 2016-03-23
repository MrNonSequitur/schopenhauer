#!/usr/bin/env python
import json

knowledge_base = {}
#"If you store using a key that is already in use, the old value associated with that key is forgotten. It is an error to extract a value using a non-existent key."

def guess_answer(breadcrumb, fingerprint):
	if breadcrumb in knowledge_base:
		if fingerprint in knowledge_base[breadcrumb]:
			return knowledge_base[breadcrumb][fingerprint]
	return ""

def record_answer(breadcrumb, fingerprint, answer):	
	if breadcrumb in knowledge_base:
		knowledge_base[breadcrumb][fingerprint] = answer
	else:
		knowledge_base[breadcrumb] = {fingerprint: answer}
	print(breadcrumb + ": " + answer + "\n" + str(fingerprint))

def initialize(): #probably this is poor practice and not the idiomatic way
	with open('knowledge.txt', 'r') as f:
		knowledge_base = json.load(f)
		#I'm not a huge fan of json (sexprs are better), but this is better than my original plan of calling eval on whatever we find in knowledge.txt and hoping it's a data sctructure

def write_out():
	with open('knowledge.txt', 'w') as f:
		json.dump(knowledge_base, f)

