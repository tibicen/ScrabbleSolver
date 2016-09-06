# -*- coding: utf-8 -*-
import random

WORDLIST_FILENAME = "pl_slownik.txt"
PUNKTACJA_FILENAME = "pl_punktacja.txt"
LETTERS = 'a' * 9 + 'ą' * 1 + 'b' * 2 + 'c' * 3 + 'ć' * 1 + 'd' * 3 + \
          'e' * 7 + 'ę' * 1 + 'f' * 1 + 'g' * 2 + 'h' * 2 + 'i' * 8 + \
          'j' * 2 + 'k' * 3 + 'l' * 3 + 'ł' * 2 + 'm' * 3 + 'n' * 5 + \
          'ń' * 1 + 'o' * 6 + 'ó' * 1 + 'p' * 3 + 'r' * 4 + 's' * 4 + \
          'ś' * 1 + 't' * 3 + 'u' * 2 + 'w' * 4 + 'y' * 4 + 'z' * 5 + \
          'ź' * 1 + 'ż' * 1
LETTERS_DICT = {'a': 9, 'ą': 1, 'b': 2, 'c': 3, 'ć': 1, 'd': 3,
                'e': 7, 'ę': 1, 'f': 1, 'g': 2, 'h': 2, 'i': 8,
                'j': 2, 'k': 3, 'l': 3, 'ł': 2, 'm': 3, 'n': 5,
                'ń': 1, 'o': 6, 'ó': 1, 'p': 3, 'r': 4, 's': 4,
                'ś': 1, 't': 3, 'u': 2, 'w': 4, 'y': 4, 'z': 5,
                'ź': 1, 'ż': 1}


def loadWords(filename):
    """
    Returns a list of valid words. Words are strings of lowercase letters.
    wordList: list of list of strings sorted in words length
    """
    # inFile = open(filename, 'r', encoding='utf-8')

    wordList = []
    with open(filename, 'r', encoding='utf-8') as inFile:
        for line in inFile:
            wordList.append(line.strip('\n').split(','))
    return wordList


# def loadWords_deprecated(filename):
#     """
#     Returns a list of valid words. Words are strings of lowercase letters.
#
#     Depending on the size of the word list, this function may
#     take a while to finish.
#     wordList: list of list of strings sorted in words length
#     """
#     # inFile = open(filename, 'r', encoding='utf-8')
#
#     wordList = []
#     with open(filename, 'r', encoding='utf-8') as inFile:
#         for line in inFile:
#             wordList.append(line.strip().rstrip('\n'))
#     dictPL = {}
#     for nr, w in enumerate(wordList):
#         wSize = len(w)
#         if wSize in dictPL.keys():
#             dictPL[wSize].append(w)
#         else:
#             dictPL[wSize] = [w]
#     wordList = [v for k, v in sorted(dictPL.items(),
#                 key=lambda x: x[0], reverse=True)]
#     # wordList.sort()
#     return wordList


def letterValues(filename):
    '''
    returns: dict with letter Values for Scrabble
    '''
    inFile = open(filename, 'r', encoding='utf-8')
    # inFile = codecs.open(filename, 'r', encoding='utf-8', buffering=0)
    ltrVals = {}
    for line in inFile:
        line = line.rstrip('\n').rstrip('\r').lower()
        Linenr = line.split(':')
        for l in Linenr[1].split(','):
            ltrVals[l] = int(Linenr[0])
    return ltrVals


def getFrequencyDict(sequence):
    """
    Returns a dictionary where the keys are elements of the sequence
    and the values are integer counts, for the number of times that
    an element is repeated in the sequence.

    sequence: string or list
    return: dictionary
    """
    # freqs: dictionary (element_type -> int)
    freq = {}
    for x in sequence:
        freq[x] = freq.get(x, 0) + 1
    return freq


def getWordScore(word, n, scrabble_letter_values):
    """
    Returns the score for a word. Assumes the word is a valid word.

    The score for a word is the sum of the points for letters in the
    word, multiplied by the length of the word, PLUS 50 points if all n
    letters are used on the first turn.

    Letters are scored as in Scrabble; A is worth 1, B is worth 3, C is
    worth 3, D is worth 2, E is worth 1, and so on (see scrabble_letter_values)

    word: string (lowercase letters)
    n: integer (HAND_SIZE; i.e., hand size required for additional points)
    returns: int >= 0
    """
    score = 0
    for l in word:
        score += scrabble_letter_values[l]
    score *= len(word)
    if len(word) == n:
        score += 50
    return score


def calculateHandlen(hand):
    """
    Returns the length (number of letters) in the current hand.

    hand: dictionary (string-> int)
    returns: integer
    """
    result = 0
    for x, y in hand.items():
        result += y
    return result


def isValidW(word, hand):
    """
    Returns True if word is in the wordList and is entirely
    composed of letters in the hand. Otherwise, returns False.

    Does not mutate hand or wordList.

    word: string
    hand: dictionary (string -> int)
    wordList: list of lowercase strings
    """
    lettersList = getFrequencyDict(word)
    for x, y in lettersList.items():
        if x not in hand.keys() or hand[x] < y or len(word) <= 1:
            return False
    return True


def compChooseWord(hand, wordList, n, scrabble_letter_values):
    """
    Given a hand and a wordList, find the word that gives
    the maximum value score, and return it.

    This word should be calculated by considering all the words
    in the wordList.

    If no words in the wordList can be made from the hand, return None.

    hand: dictionary (string -> int)
    wordList: list (string)
    n: integer (HAND_SIZE; i.e., hand size required for additional points)

    returns: string or None
    """
    maxScore = 0
    bestWord = None
    bestWords = []
    for word in wordList:
        # If you can construct the word from your hand
        # (hint: you can use isValidWord, or - since you don't really need to
        # test if the word is in the wordList - you can make a similar function
        # that omits that test)
        if isValidW(word, hand):
            score = getWordScore(word, n, scrabble_letter_values)
            bestWords.append((word, score))
            if score >= maxScore:
                maxScore = score
                bestWord = word
                # bestWords.append((word, maxScore))
    return bestWords


def cleanWordList(wordlist):
    st = len(wordlist)
    print('zaladowano: %d' % st)
    newList = []
    errors = []
    for nr, w in enumerate(wordlist):
        if nr % int(len(wordlist) / 10000) == 0:
            print('\r%.2f%%' % (100 * nr / len(wordlist)), end='')
        boo = True
        if len(w) < 3:
            boo = False
        if len(w) == 3:
            if w[0] == w[1] == w[2]:
                boo = False
        if ' ' in w:
            boo = False
        if boo:
            newList.append(w)
        else:
            errors.append(w)
    with open('slowa-bledne.txt', 'w', encoding='utf-8') as newFile:
        for l in errors:
            newFile.write(','.join(l) + '\n')
    wordlist = newList
    wordlist2 = []
    duplicate = 0
    a = []
    print('\n')
    print(len(wordlist))
    for nr, w in enumerate(wordlist):
        if nr % int(len(wordlist) / 10000) == 0:
            print('\r%.2f%%' % (100 * nr / len(wordlist)), end='')
        if w not in wordlist2[-1000:]:
            wordlist2.append(w)
        else:
            duplicate += 1
    print('\n%d duplikatow.' % duplicate)
    print('zostalo: %d' % (len(wordlist2)))
    print('usunieot: %d' % (st - len(wordlist2)))
    return wordlist2


def merge(*iters):
    result = []
    for i in iters:
        result += i
    return result


def game(wordlist, ltrVals):
    wyraz = random.sample(LETTERS, 7)
    print([x for x in wyraz])
    hand = getFrequencyDict(wyraz)
    n = len(wyraz)
    words = compChooseWord(hand, wordlist, n, ltrVals)
    print(words)


if __name__ == '__main__':
    ltrVals = letterValues(PUNKTACJA_FILENAME)
    wordlist = loadWords(WORDLIST_FILENAME)
    wordlist2 = list(reversed([list(reversed(x)) for x in wordlist]))
    # game(wordlist, ltrVals)
    # wordlist = cleanWordList(wordlist)
    # print('wszystkie slowa: %d' % (len(wordlist)))
    # zapisz posortowane
    # wordlist = [x[0].lower() for x in wordlist]
    # sortList = sorted(wordlist, key=lambda x: getWordScore(
    #     x.lower(), len(x) + 1, ltrVals), reverse=True)
    # with open('slowa-wszystkie6.txt', 'w', encoding='utf-8') as newFile:
    #     for l in sortList:
    #         newFile.write(l + '\n')
    # swordlist = []
    # for word in wordlist:
    #     boo = True
    #     for l in word.lower():
    #         if word.count(l) > lettersDict[l]:
    #             boo = False
    #             break
    #     if boo:
    #         swordlist.append(word)
    with open('slowa-scrabble.txt', 'w', encoding='utf-8') as newFile:
        for l in wordlist2:
            newFile.write(','.join(l) + '\n')
