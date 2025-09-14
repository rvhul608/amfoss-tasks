T=int(input())
for i in range(0,T):
    x,y=map(int,input().split())
    if x>=y:
        print(y)
    else:
        print(x)
