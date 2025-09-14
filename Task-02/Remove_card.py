T = int(input())
for m in range(T):
    N=int(input())
    count=0
    a=list(map(int,input().split()))
    for i in range(N):
        count1=0
        for j in range(N):
            if a[i]==a[j]:
                count1+=1
        if count1>count:
            count=count1
    print(N-count)
