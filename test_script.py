import pandas as pd
import matplotlib.pyplot as plt
import random as rand

counter = 0
drop = 0
kills = 0
listi = []
while True:
    numb = rand.uniform(0, 1)
    kills += 1
    if numb <= (1/362.66):
        counter += 1
        if counter % 3 == 0 and counter != 0:
            drop += 1

    if kills % 50000 == 0:
        listi.append(1/(drop/kills))
        plt.plot(range(0,len(listi)),listi)
        plt.title(f"Odds for ring 1/{1/(drop/kills)}")
        print(f"Odds for ring 1/{1/(drop/kills)}")
        plt.show()
