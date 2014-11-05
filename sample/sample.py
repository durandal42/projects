import random

def sample(input, k):
    result = [None] * k
    for i,word in enumerate(input):
        if i < k: result[i] = word
        else:
            i = random.randrange(i+1)
            if i < k: result[i] = word
    return result

print [line.upper().strip() for line in
       sample(open("TWL06.txt"), 10)]
