# -*- coding: utf-8 -*-
# from solver import *
import random
import threading
from functools import partial

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout

from solver import (getFrequencyDict, getWordScore, isValidW, letterValues,
                    loadWords, merge)

__version__ = '0.5'
DEBUG = True
PUNKTACJA = 'pl_punktacja.txt'
DICTIONARY = 'pl_slownik.txt'
LETTERS_DICT = {'a': 9, 'ą': 1, 'b': 2, 'c': 3, 'ć': 1, 'd': 3,
                'e': 7, 'ę': 1, 'f': 1, 'g': 2, 'h': 2, 'i': 8,
                'j': 2, 'k': 3, 'l': 3, 'ł': 2, 'm': 3, 'n': 5,
                'ń': 1, 'o': 6, 'ó': 1, 'p': 3, 'r': 4, 's': 4,
                'ś': 1, 't': 3, 'u': 2, 'w': 4, 'y': 4, 'z': 5,
                'ź': 1, 'ż': 1}
LETTERS = ''.join([k*v for k, v in LETTERS_DICT.items()])


Builder.load_string('''
# -*- coding: utf-8 -*-
<RootWidget>
    canvas:
        Color:
            rgb: (.87,.87,.87)
        Rectangle:
            pos: self.pos
            size: self.size
    opis: opis
    prog: prog
    literki: literki
    size: 100, 50
    BoxLayout:
        padding: 0
        orientation: 'vertical'
        Label:
            id:tytul
            canvas.before:
                Color:
                    rgb: (142/255, 173/255, 83/255)
                Rectangle:
                    pos: self.pos
                    size: self.size
            color: .87,.87,.87,1
            text: 'ScrabbleSolver'
            text_size: self.size
            font_size: self.height -9
            halign: 'center'
            valign: 'middle'
            size_hint: 1, .06
        ProgressBar:
            id: prog
            max: 1
            value: 0
            size_hint: 1, 0.005
        Label:
            color: 1-.85,1-.85,1-.85,1
            text: 'Wpisz literki w pole poniżej:'
            text_size: self.width-20, self.height-20
            halign: 'center'
            valign: 'middle'
            size_hint: 1, .05
        TextInput:
            id: literki
            multiline: False
            background_color: 1,1,1,0
            color: 1-.85,1-.85,1-.85,1
            text: ''
            font_name: 'RobotoMono-Regular'
            font_size: self.height/2
            size_hint: 1, .08
            padding: (self.size[0]/2 - 23*len(self.text),self.height/4,0,0)
        Label:
            color: 1-.85,1-.85,1-.85,1
            id: opis
            text: ''
            text_size: self.width-20, self.height-20
            halign: 'center'
            valign: 'middle'
            size_hint: 1, .5
        BoxLayout:
            size_hint: 1, .15
            Button:
                id: random
                background_color: 142/255, 173/255, 83/255,1
                text: '+7 random'
                text_size: self.width - 10, self.height - 10
                font_size: self.height/5
                valign: 'middle'
                halign: 'center'
                on_press: root.onPressRandom()
            Button:
                id: szukajButton
                text: 'Szukaj'
                text_size: self.width - 10, self.height - 10
                font_size: self.height/5
                valign: 'middle'
                halign: 'center'
                on_press: root.onPress()
                on_release: root.search()
''')


def printDbg(*arg, **kwargs):
    if DEBUG:
        print(*arg, **kwargs)


class chooseWords(threading.Thread):

    def __init__(self, root, wordlist, n, update_bar):
        threading.Thread.__init__(self)
        self.root = root
        self.hand = root.hand
        self.ltrVals = root.ltrVals
        self.opis = root.opis
        self.bestWords = root.bestWords
        self.wordlist = wordlist
        self.n = n
        self.update_bar = update_bar

    def run(self):
        self.update_bar('reset')
        for nr, word in enumerate(self.wordlist):
            if nr % 100 == 0:
                self.update_bar(len(self.wordlist))
            if isValidW(word, self.hand):
                score = getWordScore(word, self.n, self.ltrVals)
                self.bestWords.append((word, score))
        wordsStr = ''
        if self.bestWords:
            for w in reversed(self.bestWords[-10:]):
                wordsStr += '{0}, {1}pt\n'.format(*w)
            self.opis.text = (
                'Najodpowiedniejsze słowa to:\n\n' + wordsStr)
        else:
            self.opis.text = (
                'Nie znaleziono odpowiednikow.\nMam za słaby słownik.')
        self.update_bar('full')
        printDbg(self.bestWords)


class RootWidget(BoxLayout):

    def __init__(self, **kwargs):
        BoxLayout.__init__(self)
        # super(RootWidget, self).__init__(**kwargs)
        self.BAZY = False
        self.wordlist = []
        self.ltrVals = {}
        self.literki.text = 'zwierzę' if DEBUG else ''.join(
            random.sample(LETTERS, 7))
        self.bestWords = []
        self.prog.value = 0
        self.hand = 0
        self.dump = None

    def onPress(self):
        if self.BAZY:
            self.opis.text = 'Przeliczanie konfiguracji liter...'
        else:
            self.opis.text = 'Ładowanie słownika...'

    def onPressRandom(self):
        self.literki.text += ''.join(random.sample(LETTERS, 7))

    def printText(self, text):
        # TODO wrap straight commands to print text in layout
        pass

    def search(self):
        self.bestWords = []
        self.prog.value = 0
        sekwencja = self.literki.text.replace(' ', '')
        if len(sekwencja) < 3:
            self.opis.text = 'Wprowadź 3 lub więcej liter i wyszukaj ' + \
                             'jeszcze raz.'
        else:
            if not self.BAZY:
                self.importFiles()
            self.hand = getFrequencyDict(sekwencja)
            lettersNr = len(sekwencja)
            self.opis.text = 'Obliczanie... \n\nCzekaj'
            wordlists = self.wordlist[:lettersNr - 2]
            crpWordlist = list(merge(*wordlists))
            # TODO implement thread search
            work = chooseWords(self, crpWordlist, lettersNr + 1,
                               lambda x: Clock.schedule_once(
                                   partial(self.update_bar, x)))
            work.start()
            self.prog.value = 1.0

    def importFiles(self):
        self.ltrVals = letterValues(PUNKTACJA)
        self.wordlist = loadWords(DICTIONARY)
        self.BAZY = True
        printDbg('imported {:d} words.'.format(
            len(list(merge(*self.wordlist)))))

    def update_bar(self, wordlistLen, dt=None):
        '''
        Updates progress bar and text window during search.
             wordlistLen: (int)
             returns: (None) updated layout
        '''
        wordsStr = ''
        if wordlistLen == 'full':
            self.prog.value = 1.0
        elif wordlistLen == 'reset':
            self.prog.value = 0
        else:
            self.prog.value = self.prog.value + (100 / wordlistLen)
            # printDbg('%.2f' % (self.prog.value))
            # dumps weaker words
            best = self.bestWords[-10:]
            best = sorted(best, key=lambda x: x[1], reverse=True)
            a = ''.join(['{:12}: {}\n'.format(x, y) for x, y in best])
            if a != self.dump:
                print(a)
                print('_'*16)
                self.dump = a
            for w in best:
                wordsStr += '%s, %dpt\n' % (w[0], w[1])
            self.opis.text = 'Najodpowiedniejsze słowa to:\n\n' + wordsStr


class ScrabbleSolver(App):

    def build(self):
        return RootWidget()

    def on_pause(self):
        return True

    def on_resume(self):
        pass
        # fun fun fun


if __name__ == '__main__':
    ScrabbleSolver().run()
