
class Board():
    def __init__(self, design=official):  # takes the design and expands it into a full board
        r, c = design.shape
        global width
        self.data = np.pad(design, ((0, r - 1), (0, c - 1)), 'reflect')
        self.alpha = AlphaArray(self.data)
        self.size = width = len(self.data)
        self.design = design

    def __str__(self):
        Indicies = list(map(str, range(self.size)))
        output = ''
        if self.size < 10:
            output += '    ' + '|'.join(Indicies)
        else:
            output += '    ' + '|'.join([x[0] if int(x) > 9 else ' ' for x in Indicies]) + '\n'
            output += '    ' + '|'.join([x[1] if int(x) > 9 else x for x in Indicies]) + '\n'
        for i, x in enumerate(self.data):
            if i < 10: i = str(i) + ' '
            output += str(i) + ' |' + ' '.join(x) + '\n'
        return output

    def __repr__(self):
        return str(self)

    def __setitem__(self, index, value):
        self.data[index] = value
        self.alpha = AlphaArray(self.data)

    def __getitem__(self, index):
        return self.data[index]

    def Layer(self, across, coords, word):
        xC, yC = coords
        WordLen = len(word)
        if across == 2:
            assert yC + WordLen <= self.size, "Too large"
            self.data[xC, yC:yC + WordLen] = list(word)
        else:  # down
            assert xC + WordLen <= self.size, "Too large"
            self.data[xC:xC + WordLen, yC] = list(word)
        self.alpha = AlphaArray(self.data)