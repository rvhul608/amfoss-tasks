T=int(input())
for i in range(0,T):
    x,y=map(int,input().split())
    n=(x-1)//10+1
    m=(y-1)//10+1
    
    if m>n:
        print(m-n)
    elif n>m:
        print(n-m)
    else:
        print(0)
