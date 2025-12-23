import struct
import sys
import os

def read_u8(b, o):  return b[o]
def read_u16(b, o): return struct.unpack_from("<H", b, o)[0]
def read_u32(b, o): return struct.unpack_from("<I", b, o)[0]

def fat_report(img):
    with open(img, "rb") as f:
        boot = f.read(512)

    if len(boot) != 512:
        print("Erro: não foi possível ler o sector de boot.")
        return

    bytes_per_sector   = read_u16(boot, 11)
    sectors_per_cluster = read_u8(boot, 13)
    reserved_sectors   = read_u16(boot, 14)
    num_fats           = read_u8(boot, 16)
    root_entries       = read_u16(boot, 17)
    total_sectors_16   = read_u16(boot, 19)
    media              = read_u8(boot, 21)
    sectors_per_fat_16 = read_u16(boot, 22)
    sectors_per_track  = read_u16(boot, 24)
    heads              = read_u16(boot, 26)
    total_sectors_32   = read_u32(boot, 32)

    total_sectors = total_sectors_16 if total_sectors_16 != 0 else total_sectors_32
    disk_bytes = total_sectors * bytes_per_sector
    disk_kb = disk_bytes // 1024

    print("=== RELATÓRIO DO DISCO FAT ===")
    print(f"Imagem: {img}")
    print()
    print(f"Bytes por sector     : {bytes_per_sector}")
    print(f"Sectores por cluster : {sectors_per_cluster}")
    print(f"Sectores reservados  : {reserved_sectors}")
    print(f"Número de FATs       : {num_fats}")
    print(f"Entradas root dir    : {root_entries}")
    print(f"Sectores por FAT     : {sectors_per_fat_16}")
    print(f"Sectores por track   : {sectors_per_track}")
    print(f"Cabeças (heads)      : {heads}")
    print(f"Media descriptor     : 0x{media:02X}")
    print()
    print(f"Total de sectores    : {total_sectors}")
    print(f"Tamanho do disco     : {disk_kb}K")
    print()
    print("Assinatura boot      :", "OK" if boot[510:512] == b'\x55\xAA' else "INVÁLIDA")

print("\033c\033[40;37m\n")
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python fat_report.py <imagem.img>")
        sys.exit(1)

    if not os.path.exists(sys.argv[1]):
        print("Erro: ficheiro não existe.")
        sys.exit(1)

    fat_report(sys.argv[1])

