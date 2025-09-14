T=int(input())
for i in range(0,T):
    n,x,y=map(int,input().split())
    n=n+1
    z=n*y
    if x<=z:
        print("YES")
    else:
        print("NO")
