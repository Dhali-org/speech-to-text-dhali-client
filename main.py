import time
import threading
import curses
from datetime import timedelta
import microphone
import re

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
    i = 0
    while True:
        run_time = time.time() - start_time
        run_time_str = str(timedelta(seconds=int(run_time)))
        words_str = ' '.join([' '.join(words[j].split()) for j in sorted(words.keys())])
        words_str = replace_full_stops(words_str)

        stdscr.addstr(0, 0, f"Runtime: {run_time_str}")
        stdscr.addstr(1, 0, f"Words: {words_str}")
        stdscr.refresh()

        if run_time - seconds*i >= 0:
            WordThread(i, words, seconds)
            i += 1
        time.sleep(0.1)

if __name__ == "__main__":
    curses.wrapper(main)
