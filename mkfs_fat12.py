import struct
import sys
import math

SECTOR_SIZE = 512
MEDIA_DESCRIPTOR = 0xF0
NUM_FATS = 2
ROOT_ENTRIES = 512
RESERVED_SECTORS = 1
MAX_FAT12_CLUSTERS = 4084

def choose_sectors_per_cluster(total_sectors):
    """
    Escolhe o menor sectors/cluster que não ultrapasse o limite FAT12
    """
    for spc in [1, 2, 4, 8, 16]:
        data_sectors = total_sectors - 100  # margem
        clusters = data_sectors // spc
        if clusters <= MAX_FAT12_CLUSTERS:
            return spc
    raise RuntimeError("Disco demasiado grande para FAT12")

def calc_sectors_per_fat(clusters):
    """
    Cada entrada FAT12 ocupa 12 bits
    """
    fat_bytes = math.ceil((clusters + 2) * 1.5)
    return math.ceil(fat_bytes / SECTOR_SIZE)

def write_sector(f, sector, data):
    f.seek(sector * SECTOR_SIZE)
    f.write(data)

def mkfs_fat12(filename, size_mb):
    total_bytes = size_mb * 1024 * 1024
    total_sectors = total_bytes // SECTOR_SIZE

    spc = choose_sectors_per_cluster(total_sectors)

    root_dir_sectors = (ROOT_ENTRIES * 32 + SECTOR_SIZE - 1) // SECTOR_SIZE

    # estimativa inicial
    data_sectors = total_sectors - RESERVED_SECTORS - root_dir_sectors
    clusters = data_sectors // spc
    sectors_per_fat = calc_sectors_per_fat(clusters)

    # recalcular com FATs
    data_sectors = total_sectors - RESERVED_SECTORS - NUM_FATS * sectors_per_fat - root_dir_sectors
    clusters = data_sectors // spc
    sectors_per_fat = calc_sectors_per_fat(clusters)

    print("FAT12 parameters:")
    print(" size:", size_mb, "MB")
    print(" sectors:", total_sectors)
    print(" sectors/cluster:", spc)
    print(" clusters:", clusters)
    print(" sectors/FAT:", sectors_per_fat)

    with open(filename, "wb+") as f:
        f.seek(total_bytes - 1)
        f.write(b"\x00")

        # ---------------- BOOT SECTOR ----------------
        boot = bytearray(SECTOR_SIZE)
        boot[0:3] = b'\xEB\x3C\x90'
        boot[3:11] = b'MKFSFAT '

        struct.pack_into("<H", boot, 11, SECTOR_SIZE)
        boot[13] = spc
        struct.pack_into("<H", boot, 14, RESERVED_SECTORS)
        boot[16] = NUM_FATS
        struct.pack_into("<H", boot, 17, ROOT_ENTRIES)
        struct.pack_into("<H", boot, 19, total_sectors)
        boot[21] = MEDIA_DESCRIPTOR
        struct.pack_into("<H", boot, 22, sectors_per_fat)

        struct.pack_into("<H", boot, 24, 63)   # fake geometry
        struct.pack_into("<H", boot, 26, 255)

        boot[510:512] = b'\x55\xAA'
        write_sector(f, 0, boot)

        # ---------------- FATs ----------------
        fat = bytearray(SECTOR_SIZE)
        fat[0] = MEDIA_DESCRIPTOR
        fat[1] = 0xFF
        fat[2] = 0xFF

        fat_start = RESERVED_SECTORS
        write_sector(f, fat_start, fat)
        write_sector(f, fat_start + sectors_per_fat, fat)

        # ---------------- ROOT DIRECTORY ----------------
        root_start = RESERVED_SECTORS + NUM_FATS * sectors_per_fat
        zero = bytes(SECTOR_SIZE)

        for i in range(root_dir_sectors):
            write_sector(f, root_start + i, zero)

    print("Imagem FAT12 criada com sucesso.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python mini_mkfs_fat12.py <imagem.img> <tamanho_MB>")
        sys.exit(1)

    mkfs_fat12(sys.argv[1], int(sys.argv[2]))

