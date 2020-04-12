import cProfile

import dawg
import gaddag

with open('collins.txt', 'r') as inFile:
    wordy = [x.strip() for x in inFile.readlines()]
    words = set(wordy)

# print(normalgaddag.root["b"]['a'])
# So we can do single letter word follows GOOD


normalgaddag = gaddag.GADDAG(words)
normaldawg = dawg.DAWG(wordy)
complete = dawg.CompletionDAWG(words)

cProfile.run("complete.keys('b');" * 1000)
complete2 = dawg.CompletionDAWG(wordy)
cProfile.run("complete2.keys('b');" * 1000)

# cProfile.run("normalgaddag.starts_with('b');"*100)
# cProfile.run('normalgaddag.ends_with("pretty")')
# cProfile.run('complete.prefixes("creatored")')
# cProfile.run('"creative" in normalgaddag')
# cProfile.run('"creative" in normaldawg')
# cProfile.run('"creative" in words')
