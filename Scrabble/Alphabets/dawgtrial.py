import dawg
import gaddag
import timeit
#set is faster

s = '''
import dawg;

with open('collins.txt','r') as inFile:
    wordy = [x.strip() for x in inFile.readlines()];
    words = set(wordy);

normaldawg = dawg.DAWG(wordy);
complete = dawg.CompletionDAWG(wordy);
'''

print(timeit.timeit('"banana" in normaldawg',
                    setup=s,
                    number=100000))
print(timeit.timeit('"banana" in words',
                    setup=s,
                    number=100000))
