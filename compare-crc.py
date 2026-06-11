import glob, subprocess, os
our = {}
sv = 'kernel/out/Module.symvers'
if os.path.exists(sv):
    for line in open(sv):
        p = line.split('\t')
        if len(p) >= 2:
            try:
                our[p[1]] = int(p[0], 16)
            except Exception:
                pass
print("nosso kernel exporta %d simbolos com CRC" % len(our))
ml = our.get('module_layout')
print("module_layout CRC (nosso):", hex(ml) if ml is not None else "AUSENTE")
allok = True
for ko in sorted(glob.glob('stock-*.ko')):
    out = subprocess.run(['modprobe', '--dump-modversions', ko], capture_output=True, text=True).stdout
    total = match = miss = 0
    misses = []
    for line in out.splitlines():
        pp = line.split()
        if len(pp) >= 2:
            try:
                crc = int(pp[0], 16)
            except Exception:
                continue
            sym = pp[1]
            total += 1
            if our.get(sym) == crc:
                match += 1
            else:
                miss += 1
                misses.append(sym)
    st = "TODOS BATEM (carrega!)" if miss == 0 else ("%d DIVERGEM" % miss)
    if miss:
        allok = False
    print("%s: %d simbolos, %d batem, %d divergem -> %s" % (ko, total, match, miss, st))
    if misses:
        print("   divergem:", misses[:25])
print("=== VEREDITO: %s ===" % ("TODOS OS MODULOS CARREGAM -> PODE FLASHAR!" if allok else "HA DIVERGENCIA -> NAO flashar ainda"))
