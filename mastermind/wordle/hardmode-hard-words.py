import collections

counts_by_missing_letter = []
for i in range(5):
    counts_by_missing_letter.append(collections.Counter())
    
for word in open('legal-targets.txt'):
    word = word.upper().strip()
    for i in range(5):
        counts_by_missing_letter[i][word[:i] + "." + word[i+1:]] += 1

for i in range(5):
    print(sorted([(v,k) for k,v in counts_by_missing_letter[i].items()], reverse=True)[:10])
