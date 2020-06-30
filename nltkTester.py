import nltk
import re
import inflect
from collections import Counter
iEngine = inflect.engine()


# FUNCTION- reads all the words from any file with one word per line
#         - returns the words as a set
def read_words_from_file(filename):
    wordFile = open(filename, "r")
    wordSet = set()
    for line in wordFile:
        word = line.strip()
        if word == '': continue
        wordSet.add(word)
    wordFile.close()
    return wordSet
# END-OF-FUNCTION


# creates file names for the various word lists
sentence_split_file_name = "word_lists/sentence_splitters.txt"
abstract_ingrs_file_name = "word_lists/abstract_ingrs.txt"
good_words_file_name = "word_lists/good_words.txt"
bad_words_file_name = "word_lists/bad_words.txt"
# retrieves the word lists from their respective files
sentence_splitters = read_words_from_file(sentence_split_file_name)
abstract_ingrs = read_words_from_file(abstract_ingrs_file_name)
good_words = read_words_from_file(good_words_file_name)
bad_words = read_words_from_file(bad_words_file_name)

# creates a name for and opens a file for reading the counted ingredients
ingrFileName = "counter_ingrs.txt"
ingrFile = open(ingrFileName, "r")

# creates a name for, clears, and opens a file for writing the output
outFileName = "nltk_test_dump.txt"
outFile = open(outFileName, "w")
outFile.write("")
outFile.close()
outFile = open(outFileName, "a")

# creates a name for, clears, and opens a file for writing the ingr categories
ingrCatFileName = 'ingredientCategories.txt'
ingrCatFile = open(ingrCatFileName, "w")
ingrCatFile.write('')
ingrCatFile.close()
ingrCatFile = open(ingrCatFileName, "a")


# FUNCTION- tags the words in the sentence and converts the plural to singular
def singularize_tokens(tokens):
    newTokens = []
    for i in range(len(tokens)):
        pos = (nltk.pos_tag([tokens[i]]))[0][1]
        if (pos == 'NNS' or pos == 'NNPS') and iEngine.singular_noun(tokens[i]) is not False:
            newTokens.append(iEngine.singular_noun(tokens[i]))
        else:
            newTokens.append(tokens[i])

    # returns the singularized tokens as a sentence
    return ' '.join(newTokens)
# END-OF-FUNCTION


# FUNCTION- removes chunks of the ingredient after specific key words
#         - because some words signal the rest of the ingredient as unnecessary
def remove_sentence_splits(ingr, wordSet):
    reg_beg = "(\s"
    reg_end = "\s.*$)"
    for word in wordSet:
        ingr = re.sub(reg_beg + word + reg_end, '', ingr)
    return ingr
# END-OF-FUNCTION


# FUNCTION- removes unnecessary words from the ingredient
def remove_bad_words(ingr, wordSet):
    reg_beg = "((^|\s)"
    reg_end = "($|\s))"
    for word in wordSet:
        ingr = re.sub(reg_beg + word + reg_end, ' ', ingr)
    return ingr.strip()
# END-OF-FUNCTION


# FUNCTION- marks all good phrases (phrases we want to keep) with hyphens
def mark_good_words(ingr, wordSet):
    reg_beg = '((?<=^\s)?'
    reg_end = '(?=$\s)?)'
    for word in wordSet:
        ingr = re.sub(reg_beg+word+reg_end, word.replace(' ', '-'), ingr)
    return ingr.strip()
#END-OF-FUNCTION


# FUNCTION- prepares an ingredient to be searched through from a line
def prep_ingredient(line):
    frequencyReg = '((?<=:\s)+\d+(?=$\s)?)'
    frequency = int(re.findall(frequencyReg, line)[0])
    # removes the line number and comma from the beginning of the line
    ingr = re.sub("(^[^,]*,)", "", line)
    # removes the colon and frequency from the end of the line
    ingr = re.sub("(:[^:]*$)", "", ingr)
    ingr = ingr.strip()
    # replaces all the underscores and hyphens with spaces
    ingr = ingr.replace('_', ' ')
    ingr = ingr.replace('-', ' ')
    # turns all the plural nouns in the ingredient to singular
    ingr = singularize_tokens(ingr.split())
    ingr = mark_good_words(ingr, good_words)
    ingr = remove_sentence_splits(ingr, sentence_splitters)
    ingr = remove_bad_words(ingr, bad_words)
    # collapses all sections of whitespace into single spaces
    ingr = re.sub("(\s+)", " ", ingr.strip())
    return ingr.strip().split(), frequency
# END-OF-FUNCTION

# FUNCTION- takes an ingredient and returns the category of ingredient it fits in
#         - takes an ingredient split by its words with POS tagging
def categorize_ingredient(ingrPos):
    if (len(ingrPos) == 0) or len(ingrPos[0]) == 0:
        return ''
    rIngrPos = list(reversed(ingrPos))
    if (len(rIngrPos) > 1) and (rIngrPos[0][0] in abstract_ingrs):
        category = rIngrPos[1][0] + ' ' + rIngrPos[0][0]
    else:
        category = rIngrPos[0][0]
    return category
# END-OF-FUNCTION

# creates a counter to keep track of the various ingredient categories
ingrCategories = Counter()

for line in ingrFile:
    outFile.write(line.strip() + '\n')
    # prepares the ingredient to be searched through
    ingrList, frequency = prep_ingredient(line)
    # tags the part-of-speech for the words in the ingredient
    ingrPos = nltk.pos_tag(ingrList)
    ingrCategory = categorize_ingredient(ingrPos)
    ingrCategories[ingrCategory] += frequency
    outFile.write(' '.join(ingrList) + '\n')
    outFile.write(str(ingrPos) + '\n')
    outFile.write(ingrCategory + '\n')
    outFile.write('\n')

ingrCategories = ingrCategories.most_common()
for i in range(len(ingrCategories)):
    category = ingrCategories[i]
    ingrCatFile.write('#-'+str(i+1)+':\t'+str(category[1])+'\t'+str(category[0])+'\n')

ingrCatFile.close()
outFile.close()
ingrFile.close()
