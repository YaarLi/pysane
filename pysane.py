import sys
import keyword

contws = ["if", "for", "while", "else", "elif", "try", "except", "finally", "with", "match"]
spacind =  [';', '{', '}', '(', ')', '+', '-', '*', '/', '[', ']', '=', ',']
indent = "    "

def separate_lexemes(code):
	lexemes = []
	for lex in code.split():
		sepper = False
		for sep in spacind:
			if sep in lex:
				sepper = True
				le = lex.partition(sep)
				if le[0] != "":
					lexemes.extend(separate_lexemes(le[0]))
				lexemes.append(le[1])
				if le[2] != "":
					lexemes.extend(separate_lexemes(le[2]))
				break
		if not sepper:
			lexemes.append(lex)
	return lexemes

def parse(code, settings):
	outcode = ""
	lexemes = None
	pseudoglobals = dict()
	if settings["newlinecodeline"]:
		lexemes = separate_lexemes(code.replace('\n', ';'))
	else:
		lexemes = separate_lexemes(code)
	#print(lexemes)
	newline = True
	lexi = 0
	cur_depth = 0
	varibs = [[]]
	
	def valid_var(name):
		if settings["explicitdeclare"]:
			#print(varibs)
			#print(sum(varibs, []))
			if name not in sum(varibs, []) and name not in pseudoglobals:
				try:
					eval(name, {}, {}) # check for built-ins
				except Exception:
					print("code so far:\n", outcode)
					raise NameError("Variable " + name + " is undeclared") from None
				
	def valid_any(name):
		if '.' in name: # for libraries and objects, check what's left of ., the latter is harder to verify validity
			name = name.partition('.')[0]
		if name.isalnum() and name[0].isalpha() and not keyword.iskeyword(name):
			valid_var(name)
			
	while lexi < len(lexemes):
		if newline:
			if lexemes[lexi] in contws:
				outcode += cur_depth*indent + lexemes[lexi]
				cur_depth += 1
				varibs.append([])
				if lexemes[lexi] == "for":
					outcode += ' '
					lexi += 1
					varibs[cur_depth].append(lexemes[lexi])
					outcode += lexemes[lexi]
					
				lexi += 1
				if lexemes[lexi] == '(':
					outcode += lexemes[lexi]
					lexi += 1
					brackets = 1
					while brackets > 0:
						if lexemes[lexi] == ')':
							brackets -= 1
						elif lexemes[lexi] == '(':
							brackets += 1
						else:
							valid_any(lexemes[lexi])
						outcode += ' ' + lexemes[lexi]
						lexi += 1
						
				
				while lexemes[lexi] != '{':
					valid_any(lexemes[lexi])
					outcode += ' ' + lexemes[lexi]
					lexi += 1
				
				outcode += ":\n"
				lexi += 1
				continue
			if lexemes[lexi] == '}':
				cur_depth -= 1
				lexi += 1
				varibs.pop()
				continue
			if lexemes[lexi] == '{': # the use case of this is to make a local scope without condition
				outcode += cur_depth*indent + "if True:\n"
				cur_depth += 1
				varibs.append([])
				lexi += 1
				continue
			if lexemes[lexi] == "import" or lexemes[lexi] == "from":
				impstate = lexemes[lexi]
				lexi += 1
				while lexemes[lexi] != ';':
					impstate += ' ' + lexemes[lexi]
					lexi += 1
				if settings["importlibs"]:
					#print(impstate)
					exec(impstate, pseudoglobals)
				outcode += cur_depth*indent + impstate + '\n'
				lexi += 1
				continue
			if lexemes[lexi] == "def":
				lexi += 1
				outcode += cur_depth*indent + "def " + lexemes[lexi] + '('
				varibs[cur_depth].append(lexemes[lexi])
				lexi += 2
				cur_depth += 1
				varibs.append([])
				while lexemes[lexi] != ')':
					if lexemes[lexi] == ',':
						outcode += lexemes[lexi]
						lexi += 1
						continue
					if lexemes[lexi] == '=':
						while lexemes[lexi] not in [',', ')']:
							valid_any(lexemes[lexi])
							outcode += lexemes[lexi]
							lexi += 1
						continue
					varibs[cur_depth].append(lexemes[lexi])
					outcode += ' ' + lexemes[lexi]
					lexi += 1
				outcode += lexemes[lexi] + ":\n"
				lexi += 2
				continue
			if lexemes[lexi] == "class":
				lexi += 1
				outcode += cur_depth*indent + "class " + lexemes[lexi]
				varibs[cur_depth].append(lexemes[lexi])
				lexi += 1
				if lexemes[lexi] == '(':
					
					while lexemes[lexi] != ')':
						valid_var(lexemes[lexi+1])
						outcode += lexemes[lexi] + lexemes[lexi+1]
						lexi += 2
					outcode += ')'
				lexi += 2
				outcode += ":\n"
				cur_depth += 1
				varibs.append([])
				continue
			outcode += cur_depth*indent
		
		if ';' in lexemes[lexi]:
			newline = True
			lexi += 1
			outcode += '\n'
			continue		
		if lexemes[lexi] == "for":
			outcode += "for "
			lexi += 1
			varibs[cur_depth].append(lexemes[lexi])
			outcode += lexemes[lexi]
			lexi += 1
			newline = False
			continue
		if lexemes[lexi] == '"':
			outcode += '"'
			lexi += 1
			while lexemes[lexi] != '"':
				outcode += lexemes[lexi]
				lexi += 1
			outcode += '"'
			lexi += 1
			continue
		if lexemes[lexi] == "let":
			lexi += 1
			varibs[cur_depth].append(lexemes[lexi])			
		elif not newline:
			outcode += ' '
		valid_any(lexemes[lexi])
				
		outcode += lexemes[lexi]
		#print(lexemes[lexi])
		lexi += 1
		newline = False
	
	return outcode
	
if __name__ == "__main__":
	settings = {"newlinecodeline": False, "explicitdeclare": True, "importlibs": True}
	with open(sys.argv[1]) as fi:
		print(parse(fi.read(), settings))
		
			
