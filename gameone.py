import enchant
import random
import time
from threading import Thread

d = enchant.Dict("en_US")
all_rules = " A word can be changed in six ways: Rearranging the letters, adding/removing a letter, adding/removing a letter and rearranging, or modifying one letter. Options for changing bear include bare, beard, bar, bread, bra, hear. The meaning of the word must change, so bike --> bikes is not allowed, though plurals can be used. Losing can come from improper changing, not adding a real word, or running out of time. Good Luck!"
rules_endless = "The goal of the game is to get the highest score. Each successful word change gives you a point." + all_rules
rules_two = "The goal of the game is to outlast the opponent by changing the words. Player 1 starts, player 2 gives next word, and so on." + all_rules
rules_levels = "The goal of the game is to modify a given word to another given word in a finite number of moves. Words can be changed by rearranging letters, or modifying one letter. Plurals are allowed. Good Luck!"
alphabet = ['a','b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
timer_lst = [8.0, True]


""" Options (Not for Levels) """
using_plurals = True
using_uns_add = True
using_uns_sub = False
using_add = False
using_sub = False
using_mod = False
features = [using_plurals, using_uns_add, using_uns_sub, using_add, using_sub, using_mod] #lists only way to store nonlocal data types

""" Gameplay """
def game():
    print "Hello There! You are playing ModWord"
    play(raw_input("1 or 2 players? "))

def play(num):
    if num == '1':
        return one(raw_input('endless or levels? '))
    elif num == '2':
        return two()
    else:
        play(raw_input("Enter 1 or 2 please "))

def rules(who):
    rules = raw_input("Would you care for the rules? ")
    if "y" in rules:
        print who
        raw_input('Press enter to continue ')

def timer(phrase):
    answer = None
    def check():
        time.sleep(timer_lst[0])
        if answer != None:
            return
        print "| Too slow, press enter to leave |"
        timer_lst[1] = False

    if timer_lst[0] > 4:
        timer_lst[0] -= 0.25
    Thread(target = check).start()
    if timer_lst[1]:
        answer = raw_input(phrase)
    return timer_lst[1] and answer

def one(option):
    if option == 'levels':
        rules(rules_levels)
        return turns()
    elif option != 'endless':
        return one(raw_input('Enter endless or levels please '))
    else:
        rules(rules_endless)
        word = randomword()
        return rounds(timer, word, 'one')

def two():
    rules(rules_two)
    word = raw_input("Player One enter the starting word! ")
    return rounds(raw_input, word, 'two')

def rounds(f, word, version, end = None, max = None):
    count = 0
    prev = None
    seen = []
    no_more = False
    while possible(word, prev) and word not in seen:
        seen.append(word)
        option = can_change(word, seen)
        if not option:
            break
        prev = word
        word = f(word + " --> " )
        if not word:
            break
        if version == 'levels':
            if word == end or max <= count:
                break
        count += 1
    if version == 'levels':
        end_print(word, seen, str(option), version, count, word == end, max)
        return word == end, count
    end_print(word, seen, str(option), version, count)

def end_print(word, seen, option, version, count, win = None, max = None):
    if word is not False: #if timer doesn't end the game
        if not d.check(word):
            print word + " is not a word"
        elif not plurals_check(convert_one_to_list(word), convert_one_to_list(seen[-1])) and version != 'levels':
            print "Need to change meaning of word"
        elif word in seen:
            print word + " has already been played"
        elif count > max and version == 'levels':
            print "Out of turns!"
        elif version == 'levels' and not win:
            print "Improper rearrangement/modification"
        elif version != 'levels':
            print "Improper addition/subtraction/rearrangement/modification"
    if option and version == 'one' or version == 'two':
        print option + " could have been played"
    else:
        if version == 'one':
            print "No other options exist, congrats you have beat the game!"
        elif version == 'two':
            print "Sorry Player " + str((count) % 2 + 1) + ", there are no options!"

    if version == 'one':
        print "Score: " + str(count)
    elif version == 'two':
        print "Player " + str((count + 1) % 2 + 1) + " wins!"

""" Conversions """
def convert_to_list(first, second):
    list_f = []
    list_s = []
    for i in range(len(first)):
        list_f.append(first[i])
    for i in range(len(second)):
        list_s.append(second[i])
    return list_f, list_s

def convert_one_to_list(first):
    list_f = []
    for i in range(len(first)):
        list_f.append(first[i])
    return list_f

def convert_to_word(word):
    if isinstance(word, basestring):
        return word
    ans = ''
    for i in word:
        ans += i
    return ans

def randomword():
    possibility = 'notaword'
    while not d.check(possibility) or not can_change(possibility):
        possibility = random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet) + random.choice(alphabet)
    return possibility

""" Word Switching """
def possible(w, p):
    """ Checks if word can be obtained from prev """
    if p is None:
        return d.check(w)
    word, prev = convert_to_list(w, p)
    if d.check(w) and plurals_check(word, prev):
        ans = add(word[:], prev[:]) or subtract(word[:], prev[:]) or modify(word[:], prev[:]) or unscramble(word[:], prev[:]) or uns_add(word[:], prev[:]) or uns_sub(word[:], prev[:])
        return ans
    else:
        return False

def unscramble(first, second):
    if len(first) != len(second): # length differs
        return False

    def helper(first, second):
        if not first and not second:
            return True
        letter = first.pop()
        if letter in second:
            second.remove(letter)
            return helper(first, second)
        else:
            return False
    return helper(first, second)

def all_adds(word, prev, f, helper):
    if len(word) - 1 != len(prev):
        return False
    new = word[:]
    ans = helper()
    if ans is not False:
        new.pop(ans)
    return f(new, prev)

def add(word, prev):
    if not features[3]: # not using add
        return False
    def helper():
        count = 0
        while count < len(prev):
            if prev[count] != word[count]:
                return count
            count += 1
        return False

    return all_adds(word, prev, lambda x, y: x == y, helper)

def subtract(word, prev):
    if not features[4]: # not using sub
        return False
    return add(prev, word)

def modify(word, prev):
    if not features[5] or len(word) != len(prev): # not using mod
        return False
    count = 0
    while count < len(prev):
        if prev[count] != word[count]:
            break
        count += 1
    return word[count + 1:] == prev[count + 1:] and word[:count] == prev[:count]

def uns_add(word, prev):
    if not features[1]: # not using uns_add
        return False
    def helper():
        for letter in alphabet:
            if word.count(letter) != prev.count(letter) and word.count(letter) != 0:
                return word.index(letter)
        return False
    return all_adds(word, prev, unscramble, helper)

def uns_sub(word, prev):
    if not features[2]: # not using uns_sub
        return False
    return uns_add(prev, word)

""" Can Make Words """
def can_change(word, seen = []):
    """ Checks if a word can be modified """
    word = convert_one_to_list(word)
    return can_add(word, seen) or can_sub(word, seen) or can_mod(word, seen) or can_uns(word, seen) or can_uns_add(word, seen) or can_uns_sub(word, seen)

def can_uns(word, seen):
    def insert_all_positions(lst, value):
        for i in range(len(lst) + 1):
            yield lst[:i] + [value] + lst[i:]

    def possibilities(lst):
        if not lst:
            yield []
        else:
            for p in possibilities(lst[1:]):
                for x in insert_all_positions(p, lst[0]):
                    yield x

    words_list = [convert_to_word(x) for x in possibilities(word)]
    word = convert_to_word(word)
    for entry in words_list:
        if d.check(entry):
            if entry != word and entry not in seen:
                return entry
    return False

def can_rest(word, seen, length, func):
    for i in range(length):
        words = func(word, i)
        for w in words:
            ans = convert_to_word(w)
            if d.check(ans):
                if ans not in seen and plurals_check(w, word):
                    return ans
    return False

def can_add(word, seen):
    if not features[3]: # not using add
        return False
    length, func = len(word) + 2, lambda word, i: [word[:i] + [letter] + word[i:] for letter in alphabet]
    return can_rest(word, seen, length, func)

def remove_index(word, i):
    """ Returns item as a list """
    return [word[:i] + word[i + 1:]]

def can_sub(word, seen):
    if not features[4]:
        return False
    return can_rest(word, seen, len(word), remove_index)

def can_mod(word, seen):
    if not features[5]: # not using mod
        return False
    length, func = len(word), lambda word, i: [word[:i] + [letter] + word[i + 1:] for letter in alphabet if letter != word[i]]
    return can_rest(word, seen, length, func)

def can_uns_add(word, seen):
    if not features[1]: # not using uns_add
        return False
    count = 0
    while count < len(alphabet):
        ans = can_uns([alphabet[count]] + word, seen)
        if ans:
            return convert_to_word(ans)
        count += 1
    return False

def can_uns_sub(word, seen):
    if not features[2]: # not using uns_add
        return False
    count = 0
    while count < len(word):
        ans = remove_index(word, count)[0]
        if ans:
            return convert_to_word(ans)
    return False

def plurals_check(word, prev):
    return plurals_code(word, prev) and plurals_code(prev, word)

def plurals_code(word, prev):
    #takes in lists
    if not features[0]:
        return True
    end = word[-1]
    shortened = word[:-1]
    if shortened == prev:
        if end == 'd' and shortened[-1] == 'e':
            return False
        elif end == 's' or end == 'y':
            return False
    return True

""" Levels """
def turns():
    s, e =  randomword(), randomword()
    route = [s, e]
    start, end = convert_to_list(s, e)
    cannot_be = [start, end]
    route = turns_needed(route, start, end, 1, cannot_be)
    if not isinstance(route, list):
        return turns()
    for i in range(1, 5): # get rid of word changing possibilities
        features[i] = False
    print "Start: " + s
    print "End: " + e
    print "You have " + str(len(route) + 1) + " turns"
    win, count = rounds(raw_input, s, 'levels', e, len(route))
    if win:
        left = str(len(route) - count)
        if left == '1':
            print "Congrats, you won with 1 turn left!"
        else:
            print "Congrats, you won with " + left + " turns left!"
    else:
        print "One possibility is " + str(route)

def turns_needed(route, start, end, index, cannot_be):
    """ Fastest way of getting from start to end """
    if len(start) == len(end):
        return same_len_algorithm(route, start, end, index, cannot_be)
    else:
        return "error"

def change_helper(route, start, end, index, cannot_be, changed, i):
    other_way = route[:]
    if i == index: # end_word changed
        if changed == start:
            return route
        else:
            route.insert(index, convert_to_word(changed))
            return min(turns_needed(route, start, changed, i, [changed] + cannot_be), turns_needed(other_way, start, end, i, [changed] + cannot_be), key = lambda x: len(x) if isinstance(x, list) else 30)
    else: #start_word changed
        if changed == end:
            return route
        else:
            route.insert(index, convert_to_word(changed))
            return min(turns_needed(route, changed, end, i, [changed] + cannot_be), turns_needed(other_way, start, end, index, [changed] + cannot_be), key = lambda x: len(x) if isinstance(x, list) else 30)

def same_len_algorithm(route, start, end, index, cannot_be):
    answer = unscramble(start[:], end[:])
    if answer:
        #print "unsc " + str(route)
        return route
    changed, i = change_one(route, start, end, index, cannot_be)
    if changed:
        return change_helper(route, start, end, index, cannot_be, changed, i)
    changed, i = change_any(route, start, end, index, cannot_be)
    if changed:
        return change_helper(route, start, end, index, cannot_be, changed, i)
    #print "no possib"
    return 'No Possibilities' # large number

def change_one(route, start, end, index, cannot_be):
    """ Checks if words of same length can create new word by switching one letter """
    for i in range(len(start)):
        s, e = start[:], end[:]
        if start[i] != end[i]:
            s[i] = end[i]
            if d.check(convert_to_word(s)) and s not in cannot_be:
                return s, index + 1
        if start[i] != end[i]:
            e[i] = start[i]
            if d.check(convert_to_word(e)) and e not in cannot_be:
                return e, index
    return False, False

def change_any(route, start, end, index, cannot_be):
    """ Checks if words of same length can create new word by switching one letter """
    #print str(cannot_be) + " start change_an" + convert_to_word(start) + convert_to_word(end)
    for i in range(len(start)):
        for m in range(len(start)):
            s, e = start[:], end[:]
            if start[m] != end[i]:
                s[m] = end[i]
                if d.check(convert_to_word(s)) and s not in cannot_be:
                    #print "first end-chnage any"
                    return s, index + 1
            if end[m] != start[i]:
                e[m] = start[i]
                if d.check(convert_to_word(e)) and e not in cannot_be:
                    #print "second end_change any"
                    return e, index
    return False, False

game()
