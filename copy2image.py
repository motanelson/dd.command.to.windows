
import struct
import sys
import os
import math

SECTOR_SIZE = 512
EOF_CLUSTER = 0xFFF

def u8(b,o):  return b[o]
def u16(b,o): return struct.unpack_from("<H", b, o)[0]
def w16(b,o,v): struct.pack_into("<H", b, o, v)
def w32(b,o,v): struct.pack_into("<I", b, o, v)

def format_83(name):
    name = os.path.basename(name).upper()
    if "." in name:
        n,e = name.split(".",1)
    else:
        n,e = name,""
    return (n[:8].ljust(8) + e[:3].ljust(3)).encode("ascii")

class FAT12:
    def __init__(self, img):
        self.f = open(img, "r+b")
        self.read_bpb()
        self.read_fat()

    def read_bpb(self):
        b = self.f.read(SECTOR_SIZE)
        self.bps = u16(b,11)
        self.spc = u8(b,13)
        self.res = u16(b,14)
        self.fats = u8(b,16)
        self.root_entries = u16(b,17)
        self.spf = u16(b,22)

        self.root_sectors = (self.root_entries*32 + self.bps-1)//self.bps
        self.fat_start = self.res * self.bps
        self.root_start = (self.res + self.fats*self.spf) * self.bps
        self.data_start = self.root_start + self.root_sectors*self.bps

    def read_fat(self):
        self.f.seek(self.fat_start)
        self.fat = bytearray(self.f.read(self.spf*self.bps))

    def write_fat(self):
        self.f.seek(self.fat_start)
        self.f.write(self.fat)
        self.f.seek(self.fat_start + self.spf*self.bps)
        self.f.write(self.fat)

    def fat_get(self, n):
        o = n + n//2
        if n & 1:
            return ((self.fat[o] >> 4) | (self.fat[o+1] << 4)) & 0xFFF
        return (self.fat[o] | ((self.fat[o+1] & 0x0F) << 8)) & 0xFFF

    def fat_set(self, n, v):
        o = n + n//2
        if n & 1:
            self.fat[o] = (self.fat[o] & 0x0F) | ((v << 4) & 0xF0)
            self.fat[o+1] = (v >> 4) & 0xFF
        else:
            self.fat[o] = v & 0xFF
            self.fat[o+1] = (self.fat[o+1] & 0xF0) | ((v >> 8) & 0x0F)

    def find_free_clusters(self, count):
        free=[]
        max_clusters = (len(self.fat)*2)//3
        for i in range(2, max_clusters):
            if self.fat_get(i)==0:
                free.append(i)
                if len(free)==count:
                    return free
        raise RuntimeError("Disco cheio")

    def cluster_offset(self, c):
        return self.data_start + (c-2)*self.spc*self.bps

    def find_free_root_entry(self):
        self.f.seek(self.root_start)
        root = self.f.read(self.root_sectors*self.bps)
        for i in range(0,len(root),32):
            if root[i] in (0x00,0xE5):
                return self.root_start+i
        raise RuntimeError("Root directory cheio")

def copy_to_root(img, host_file):
    fs = FAT12(img)
    data = open(host_file,"rb").read()
    size = len(data)

    clusters_needed = math.ceil(size / (fs.spc*fs.bps))
    clusters = fs.find_free_clusters(clusters_needed)

    # escrever dados
    for i,c in enumerate(clusters):
        fs.f.seek(fs.cluster_offset(c))
        fs.f.write(data[i*fs.spc*fs.bps:(i+1)*fs.spc*fs.bps])

    # atualizar FAT
    for i in range(len(clusters)-1):
        fs.fat_set(clusters[i], clusters[i+1])
    fs.fat_set(clusters[-1], EOF_CLUSTER)
    fs.write_fat()

    # criar entrada no root
    entry = bytearray(32)
    entry[0:11] = format_83(host_file)
    entry[11] = 0x20  # ficheiro normal
    w16(entry,26,clusters[0])
    w32(entry,28,size)

    pos = fs.find_free_root_entry()
    fs.f.seek(pos)
    fs.f.write(entry)

    print("Ficheiro copiado com sucesso para o root.")

if __name__=="__main__":
    if len(sys.argv)!=3:
        print("Uso: python fat12_copy_to_root.py disco.img ficheiro")
        sys.exit(1)

    copy_to_root(sys.argv[1], sys.argv[2])
