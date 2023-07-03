import time
import threading
import curses
from datetime import timedelta
import microphone
import re

from difflib import SequenceMatcher

def longest_common_substring(s1, s2):
    match = SequenceMatcher(None, s1, s2).find_longest_match(0, len(s1), 0, len(s2))
    return s1[match.a: match.a + match.size]

class WordThread(threading.Thread):
    def __init__(self, i, words, seconds):
        threading.Thread.__init__(self)
        self.seconds = seconds
        self.i = i
        self.words = words
        self.start()

    def run(self):
        words = microphone.get_microphone_input_for(seconds=self.seconds)
        self.words[self.i] = words

def replace_full_stops(text):
    # Find all occurrences of a full stop followed by zero or more spaces and a lowercase letter
    matches = re.finditer(r'\.\s*([a-z])', text)

    # Iterate over the matches in reverse order (so we don't mess up the indexes)
    for match in reversed(list(matches)):
        # If the next non-whitespace character is lowercase, replace the full stop with a comma
        start, end = match.span()
        text = text[:start] + ',' + text[start+1:]

    return text

def main(stdscr):
    seconds = 2.0
    # Clear screen
    stdscr.clear()
    start_time = time.time()
    time.sleep(0.1)
    words = {}
    words2 = {}
    anchors = {}

    i = 0
    ii=0
    while True:
        run_time = time.time() - start_time
        run_time_str = str(timedelta(seconds=int(run_time)))
        words_str = ' '.join([' '.join(words[j].split()) for j in sorted(words.keys())])
        words_str = replace_full_stops(words_str)

        # words2_str = ' '.join([' '.join(words2[j].split()) for j in sorted(words2.keys())])
        # words2_str = replace_full_stops(words2_str)

        # if i in words and i in words2:
        #     anchors[i] = longest_common_substring(words[i], words2[i])

        # anchors_str = ' '.join([' '.join(anchors[j].split()) for j in sorted(anchors.keys())])
        # anchors_str = replace_full_stops(anchors_str)

        stdscr.addstr(0, 0, f"Runtime: {run_time_str}")
        stdscr.addstr(1, 0, f"Words: {words_str}")
        # stdscr.addstr(10, 0, f"Words2: {words2_str}")
        # stdscr.addstr(15, 0, f"Anchors: {anchors_str}")
        stdscr.refresh()

        if run_time - seconds*i >= 0:
            WordThread(i, words, seconds)
            i += 1

        # if run_time - seconds*ii - seconds / 2 >= 0:
        #     WordThread(ii, words2, seconds)
        #     ii += 1

        time.sleep(0.1)



if __name__ == "__main__":
    curses.wrapper(main)
