from csv import reader
from collections import Counter
from decimal import Decimal

spese = Counter()

with open("spese.csv", encoding="utf-8") as f:
    for line in reader(f):
        spese.update({d:Decimal(c) for d,c,_ in zip(filter(None, line[2::3]), line[3::3], line[4::3])})

for key in sorted(spese, key=spese.get):
    print(key, spese[key])
    
