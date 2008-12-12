#!/usr/bin/python

import re
import sys


#return a unique version of a list
#and elminate all things starting with  "__" and vim syntax keywords while we're at it
def uniq(l):
	tmp = {}
	for i in l:
		if i[0:2] != "__" and not i in ("contains","contained","containedin", "ALL", "NONE", "ALLBUT"):
			tmp[i] = 0
	
	return tmp.keys()

#print a list without quotes as space-delimited
def str_list(l):
	tmp = ""
	for i in l:
		tmp += " " + str(i)
	#remember we added an extra space at the very beginning of the list
	return tmp[1:]

#remove any "." from a string and replace them with ""
def clean_str(s):
	p = re.compile(r"\.")
	ret = p.sub("", s)
	return ret


class ParseImport():
	def __init__(self, lib):
		#figure out what library we are going to analyze
		importlib = lib
		exec "import "+importlib
		exec "importlib_obj = " + importlib

		p = re.compile(r".*?'(.*)'")

		dic={}
		for i in dir(importlib_obj):
			exec "n = type("+importlib+"." + i + ")"
			cleankey = p.match(str(n)).group(1)
			if not cleankey in dic.keys():
				dic[cleankey] = []
			dic[cleankey].append(i)

		#print dic.keys()


		caldic = {}
		caldic[True],caldic[False],caldic['True'],caldic['False'] = [],[],[],[]
		for i in dic.keys():
			for j in dic[i]:
				exec "n = "+importlib+"." + j
				caldic[callable(n)].append(j)
				caldic[str(callable(n))].append(str(n))

		#print caldic
		#we now have a dic containg lots of interesting info

		#lets first get all the constants
		constants = []
		for i in caldic[False]:
			#make sure to filter off the first part, the "gtk."
			constants.append(i)

		deprecated = []
		p = re.compile(r"<deprecated")
		for i in range(0,len(caldic[True])):
			if p.match(caldic['True'][i]):
				depstr = caldic[True][i]
				deprecated.append(depstr)

		types = []
		p = re.compile(r"<type")
		for i in range(0,len(caldic[True])):
			if p.match(caldic['True'][i]):
				depstr = caldic[True][i]
				types.append(depstr)

		classes = []
		p = re.compile(r"<class")
		for i in range(0,len(caldic[True])):
			if p.match(caldic['True'][i]):
				depstr = caldic[True][i]
				classes.append(depstr)
		
		builtin = []
		p = re.compile(r"<built")
		for i in range(0,len(caldic[True])):
			if p.match(caldic['True'][i]):
				depstr = caldic[True][i]
				builtin.append(depstr)

		#print deprecated
		sub_obj_methods = []
		for i in types:
			#set obj to be the actual object we're curious about
			exec "obj = "+importlib+"."+i
			for j in dir(obj):
				sub_obj_methods.append(j)
		sub_obj_methods = uniq(sub_obj_methods)

		#print deprecated
		sub_class_methods = []
		for i in classes:
			#set obj to be the actual object we're curious about
			exec "obj = "+importlib+"."+i
			for j in dir(obj):
				sub_class_methods.append(j)
		sub_class_methods = uniq(sub_class_methods)


		self.types = uniq(types)
		self.classes = uniq(classes)
		self.constants = uniq(constants)
		self.sub_obj = uniq(sub_obj_methods)
		self.builtin = uniq(builtin)



# start the main function to output a syntax file :-D
escaped_args = []
for i in sys.argv[1:]:
	escaped_args.append(clean_str(i))


NoHighlight_str, Function_str, Constant_str, SubFunction_str, Builtin_str = ("NoHighlight","Functions","Constants","ObjectMethods", "Builtins")
structures_list = (Function_str, Constant_str, SubFunction_str, Builtin_str)

out_str = ""

out_str += """" Vim syntax file
" Language: python gtk extension
" Last Change: 2008-12-11


" Default highlighting
"""

out_str += "hi link " + NoHighlight_str + " Normal\n\n"

#set up highlight keywords for all the libraries
for libname in escaped_args:
	out_str += "hi link " + libname + Function_str + " pygtkObj\n"
	out_str += "hi link " + libname + Constant_str + " pygtkCnst\n"
	out_str += "hi link " + libname + SubFunction_str + " pygtkMthd\n"
	out_str += "hi link " + libname + Builtin_str + " pygtkMthd\n"
	out_str += "\n\n"

#set up the true colors
out_str +=""""the way things will be highlighted
hi link pygtkMthd Function
hi link pygtkObj Function
hi link pygtkCnst Constant

"""


#set up the list of keywords
for libname in sys.argv[1:]:
	x = ParseImport(libname)
	out_str += "\" " + libname + " stuff\n"
	if x.types != [] or x.classes != []:
		out_str += "syn keyword " 
		out_str +=  clean_str(libname) + Function_str + " " + str_list(x.types) + str_list(x.classes) + " contained\n" 
	if x.builtin != []:
		out_str += "syn keyword " 
		out_str +=  clean_str(libname) + Builtin_str + " " + str_list(x.builtin) + " contained\n" 
	if x.constants != []:
		out_str += "syn keyword " 
		out_str +=  clean_str(libname) + Constant_str + " " + str_list(x.constants) + " contained\n" 
	if x.sub_obj != []:
		out_str += "syn keyword " 
		out_str +=  clean_str(libname) + SubFunction_str + " " + str_list(x.sub_obj) + " contained\n" 

	out_str += "\n\n\n"

#make sure these are only highlighted after a "."
out_str += "\" only highlight terms that have a dot in front of them\n"
out_str += "syn match " + NoHighlight_str + r" '\..\{-}\ze\(\.\|\W\|$\)' contains="
for libname in escaped_args:
	for i in structures_list:
		out_str += libname + i + ","
#chop off the trailing comma
out_str = out_str[0:len(out_str)-1]
out_str += "\n"

out_str += """"See if they have set up something special in their colorscheme file
if !hlexists("IncludedFunction")
	hi link pygtkMthd IncludedFunction
endif

if !hlexists("IncludedFunction2")
	hi link pygtkObj IncludedFunction2
endif
"""

print out_str

