def generate_total_sum(arr):
    sum = 0
    for i in arr:
        sum += i

    return sum


n = int(input())
arr = []

for i in range(n):
    ele = int(input())
    arr.append(ele)

print(generate_total_sum(arr))
