import timeit

import dawg
import gaddag

with open('collins.txt', 'r') as inFile:
    wordy = [x.strip() for x in inFile.readlines()]
    words = set(wordy);

normalgaddag = gaddag.GADDAG(words)
normaldawg = dawg.DAWG(wordy)
complete = dawg.CompletionDAWG(wordy)

print(normalgaddag.root["b"]['a'])
quit()
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

# print(timeit.timeit('normalgaddag.starts_with("ba")',
#                     setup=s,
#                     number=1000))
# print(timeit.timeit('complete.keys("ba")',
#                     setup=s,
#                     number=1000))

print(timeit.timeit('normalgaddag.ends_with("pretty")',
                    setup=s,
                    number=1000))
# print(timeit.timeit('complete.prefixes("creatored")',
#                     setup=s,
#                     number=1000))

print(timeit.timeit('"creative" in normalgaddag',
                    setup=s,
                    number=1000))
print(timeit.timeit('"creative" in normaldawg',
                    setup=s,
                    number=1000))
print(timeit.timeit('"creative" in words',
                    setup=s,
                    number=1000))
