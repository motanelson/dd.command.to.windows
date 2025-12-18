k=1024
m=k*k
g=m*k
cc=b"\x00"
print("\033c\033[40;37m\ngive me the output file name ? ")
kk=b""
mm=b""
gg=b""
def retb(c,value,n):
    a=b""
    a=c*value
    f1=open(n,"wb")
    f1.write(a)
    f1.close()
    
def retk(c,value):
    a=b""
    a=c*value
    return a
def retm(c,value):
    a=b""
    a=c*value
    return a
def retg(c,value):
    a=b""
    a=c*value
    return a
kk=retk(cc,k)
mm=retm(kk,k)
gg=retg(mm,k)
v=b""
n=input()
n=n.strip()
print("\033[40;37m\ngive me the unit 0=bytes 1=k kilo 2=M mega 3=G gigas ? ")
nn=input()
nn=nn.strip()
nn=int(nn)
if nn>-1 and nn<4:
    print("\033[40;37m\ngive me the unit ? ")
    nnn=input()
    nnn=nnn.strip()
    nnn=int(nnn)
    if nn==0:
        retb(cc,nnn,n)
    if nn==1:
        retb(kk,nnn,n)
    if nn==2:
        retb(mm,nnn,n)
    if nn==3:
        retb(gg,nnn,n)



        
