import sys

contws = ["if", "for", "while", "else", "elif", "try", "except", "finally", "with", "match"]
spacind =  [';', '{', '}', '(', ')']
indent = "    "

def separate_lexemes(code):
	lexemes = []
	for lex in code.rsplit():
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

def parse(code):
	outcode = ""
	lexemes = separate_lexemes(code)
	#print(lexemes)
	newline = True
	lexi = 0
	cur_depth = 0
	while lexi < len(lexemes):
		if newline:
			if lexemes[lexi] in contws:
				outcode += cur_depth*indent + lexemes[lexi]
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
						outcode += ' ' + lexemes[lexi]
						lexi += 1
				while lexemes[lexi] != '{':
					outcode += ' ' + lexemes[lexi]
					lexi += 1
				cur_depth += 1
				outcode += ":\n"
				lexi += 1
				continue
			if lexemes[lexi] == '}':
				cur_depth -= 1
				lexi += 1
				continue
			if lexemes[lexi] == '{': # the use case of this is to make a local scope without condition
				outcode += "if True:\n"
				cur_depth += 1
				lexi += 1
				continue
			outcode += cur_depth*indent
		else:
			if ';' in lexemes[lexi]:
				newline = True
				lexi += 1
				outcode += '\n'
				continue
			outcode += ' '
		outcode += lexemes[lexi]
		#print(lexemes[lexi])
		lexi += 1
		newline = False
	
	return outcode
	
if __name__ == "__main__":
	with open(sys.argv[1]) as fi:
		print(parse(fi.read()))
		
			
