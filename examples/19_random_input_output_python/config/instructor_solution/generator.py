import random


def generating_random_number(lower, upper):
    return random.randint(lower, upper)


n = generating_random_number(1, 20)

print(n)
for i in range(n):
    print(generating_random_number(1, 100))
