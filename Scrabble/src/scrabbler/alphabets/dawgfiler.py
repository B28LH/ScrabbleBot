import dawg
import pickle
import data


# ONLY CARE ABOUT COMPLETOR DAWGS


def saveDawg(completeDawgObj, name):
    with open(f'./alphabets/{name}.dawg', 'wb') as f:
        completeDawgObj.write(f)


def loadDawg(name):
    loader = dawg.CompletionDAWG()
    loader.load(f'./alphabets/{name}.dawg')
    return loader

# with open(f'./alphabets/{data.dictfile}.txt', 'r') as infile:
#     data.wordset = set(infile.read().split())
#
# with open(f'./alphabets/{data.dictfile}_set.pkl', 'wb') as infile:
#     pickle.dump(data.wordset, infile, pickle.HIGHEST_PROTOCOL)
# saveDawg(dawg.CompletionDAWG(data.wordset), data.dictfile)
