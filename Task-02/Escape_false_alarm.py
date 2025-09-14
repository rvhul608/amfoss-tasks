T = int(input())
for i in range(T):
    n, x = map(int, input().split())
    a = list(map(int, input().split()))
    count = 0
    for j in range(n - x + 1):
        count1 = 0
        k = 0
        while k < j:
            if a[k] == 1:
                count1 = 1
            k += 1
        k = j + x
        while k < n:
            if a[k] == 1:
                count1 = 1
            k += 1
        if count1 == 0:
            count = 1
    if x>=n:
        print("YES")
    elif count == 1:
        print("YES")
    else:
        print("NO")
