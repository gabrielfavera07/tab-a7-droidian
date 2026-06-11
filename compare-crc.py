import glob, subprocess, os
# nosso kernel: simbolos exportados pelo vmlinux (built-in) com CRC
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
print("nosso kernel (vmlinux) exporta %d simbolos" % len(our))
ml = our.get('module_layout')
print("module_layout CRC (nosso):", hex(ml) if ml is not None else "AUSENTE")
allok = True
for ko in sorted(glob.glob('stock-*.ko')):
    out = subprocess.run(['modprobe', '--dump-modversions', ko], capture_output=True, text=True).stdout
    checked = match = miss = skip = 0
    misses = []
    for line in out.splitlines():
        pp = line.split()
        if len(pp) >= 2:
            try:
                crc = int(pp[0], 16)
            except Exception:
                continue
            sym = pp[1]
            if sym in our:          # simbolo do KERNEL -> precisa bater
                checked += 1
                if our[sym] == crc:
                    match += 1
                else:
                    miss += 1
                    misses.append((sym, hex(crc), hex(our[sym])))
            else:                   # exportado por outro modulo (stock<->stock) -> ignora
                skip += 1
    st = "TODOS os simbolos do kernel BATEM (modulo carrega!)" if miss == 0 else ("%d DIVERGEM" % miss)
    if miss:
        allok = False
    print("%s: kernel-syms checados=%d batem=%d DIVERGEM=%d (inter-modulo ignorados=%d) -> %s" % (ko, checked, match, miss, skip, st))
    for m in misses[:25]:
        print("   DIVERGE:", m)
print("=== VEREDITO: %s ===" % ("MODULOS STOCK CARREGAM COM NOSSO KERNEL -> PODE FLASHAR!" if allok else "divergencia REAL em simbolos do kernel -> investigar"))
