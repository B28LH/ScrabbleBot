import timeit

import dawg
import gaddag

with open('collins.txt', 'r') as inFile:
    wordy = [x.strip() for x in inFile.readlines()]
    words = set(wordy);

normalgaddag = gaddag.GADDAG(words)
normaldawg = dawg.DAWG(wordy)
complete = dawg.CompletionDAWG(wordy)

# print(normalgaddag.root["b"]['a'])
# So we can do single letter word follows GOOD

s = '''
import dawg;
import gaddag;

with open('collins.txt','r') as inFile:
    wordy = [x.strip() for x in inFile.readlines()];
    words = set(wordy);

normalgaddag = gaddag.GADDAG(words);
normaldawg = dawg.DAWG(wordy);
complete = dawg.CompletionDAWG(wordy);
'''


def timest(stmt):
    print(stmt, timeit.timeit(stmt, setup=s, number=1000))


timest("complete.keys('ba')")
timest("normalgaddag.starts_with('ba')")
# timest('normalgaddag.ends_with("pretty")')
# timest('complete.prefixes("creatored")')
timest('"creative" in normalgaddag')
timest('"creative" in normaldawg')
timest('"creative" in words')
