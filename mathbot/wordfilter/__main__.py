# Interactive command for checkig if a word is bad
# This was written for testing purposes
line = input('> ')
while line:
	if is_bad(line):
		print('That\'s bad!')
	else:
		print('All good!')
	line = input('> ')
