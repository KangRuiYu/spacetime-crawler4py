import sys


# Runs in linear time in relation to the the length of the text file as it
# iterates through every line and every character in the file.
# _tokenize_string() is linear in time complexity and every iteration does a 
# constant amount of work, as append() is a constant operation.
#
# Returns list containing the tokens from file at [path].
def tokenize(path):
    tokens = []

    with open(path, 'r', encoding='ascii', errors='replace') as file:
        for line in file:
            for token in _tokenize_string(line):
                tokens.append(token)

    return tokens


# Runs in linear time in relation to the size of the tokens list as it iterates
# through every token and each iteration only does a constant amount of work
# with both dictionary retreival and insertion being a constant operation.
#
# Returns a dictionary with (token, frequency) key value pairs computed from the
# given [tokens] list.
def compute_word_freq(tokens):
    word_freqs = {}

    for token in tokens:
        word_freqs[token] = word_freqs.setdefault(token, 0) + 1

    return word_freqs


# Runs in O(nlogn) time in relation to the size of token_freq dictionary. The
# loop itself is linear in runtime complexity as it iterates through every
# token, performing a print operation each time. The dictionary, however, is
# sorted beforehand, having a O(nlogn) runtime complexity.
#
# Print the tokens and the frequencies into standard out in a formatted manner,
# in descending order.
def print_token_freqs(token_freq):
    for token, freq in sorted(token_freq.items(), key=lambda x : x[1], reverse=True):
        print(f'{token} = {freq}')


# Helper function runs in linear time in relation to the length of the string.
# It iterates through every character with lower() and with the for loop. The
# operations isalnum(), append(), len, etc are constant operations. Some
# iterations will run join(), however, summing over all iterations, it will
# perform at most N extra operations.
#
# Generator function that yields the tokens from [string].
def _tokenize_string(string):
    token_chars = []

    for char in string.lower():
        if char.isalnum():
            token_chars.append(char)
        else:
            if len(token_chars) != 0: yield ''.join(token_chars)
            token_chars = []

    if len(token_chars) != 0: yield ''.join(token_chars) # For last token.


# Program has a runtime complexity of O(nlogn) in relation to the size of the
# file. Sorting is the operation with the highest runtime complexity in the
# program and in the worst case, every other character is a token.
#
# Program logic.
def _program(args):
    if len(args) != 1:
        print(f'Invalid number of arguments. Expected 1, received {len(args)}.')
        return

    try:
        file_path = args[0]
        print_token_freqs(compute_word_freq(tokenize(file_path)))
    except OSError:
        print(f'Could not open file at path "{file_path}".')
    except UnicodeDecodeError:
        print('File has non-unicode characters.')


# Program logic.
if __name__ == '__main__':
    _program(sys.argv[1:]) # Discard first argument (program name)

