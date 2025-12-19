k=1024
m=k*k
g=m*k
t=g*k
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
    nnn=float(nnn)
    if nn==0:
        retb(cc,int(nnn),n)
    if nn==1:
        retb(cc,int(float(nnn)*float(k)),n)
    if nn==2:
        retb(cc,int(float(nnn)*float(m)),n)
    if nn==3:
        retb(cc,int(float(nnn)*float(g)),n)



        
