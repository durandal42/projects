class TrieNode:
    def __init__(self):
        self.children = {}

    def insert(self, word):
        if not word:
            self.children[' '] = None  # terminates a valid word
            return
        c = word[0]
        if c not in self.children:
            self.children[c] = TrieNode()
        self.children[c].insert(word[1:])

    def __contains__(self, c):
        return c in self.children

    def __getitem__(self, c):
        return self.children[c]

class Trie:
    root = TrieNode()    
    def __init__(self, words):
        print 'loading words...'
        num_words = 0
        for word in words:
            word = word.strip().upper()
            if len(word) < 3: continue
            self.root.insert(word)
            num_words += 1
        print 'finished loading', num_words, 'legal words.'
