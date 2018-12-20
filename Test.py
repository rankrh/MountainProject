import numpy as np


l1 = [1, 2, 3, 4, 5, 6, 7]

cossims = np.array([[-1] * len(l1)] * len(l1))
print(cossims)

cossims[0][1] = 2

print(cossims)