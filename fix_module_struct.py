#!/usr/bin/env python3
# ABI-match do struct module com os modulos do /vendor (compilados com CFI on).
#
# Com CONFIG_CFI_CLANG, o struct module ganha o campo 'cfi_check' logo apos
# 'num_syms' e ANTES de init/exit. Os modulos stock foram compilados com CFI on
# (tem o campo). Nosso kernel compila com CFI off (stub) -> sem o campo ->
# ao ler o struct module do modulo, todos os campos apos num_syms (incluindo
# init e exit) saem deslocados 8 bytes -> mod->init aponta errado -> a funcao
# init vira no-op -> os platform drivers nunca sao registrados -> sem audio/wifi.
# (name/syms vem ANTES do cfi_check, por isso o modulo "carrega" com nome certo
#  e sem erro de simbolo, mascarando o bug.)
#
# Fix: manter o campo cfi_check no struct module mesmo com CFI off (padding),
# pra o layout bater com os modulos e mod->init ser lido no offset correto.
import re, sys

f = 'include/linux/module.h'
s = open(f).read()

pat = re.compile(r'#ifdef CONFIG_CFI_CLANG\s*\n\s*cfi_check_fn\s+cfi_check;\s*\n#endif')
m = pat.search(s)
if not m:
    print("ERRO: bloco '#ifdef CONFIG_CFI_CLANG cfi_check_fn cfi_check;' nao encontrado")
    sys.exit(1)

new = ("#ifdef CONFIG_CFI_CLANG\n"
       "\tcfi_check_fn cfi_check;\n"
       "#else\n"
       "\tvoid *cfi_check;\t/* ABI padding: casa com modulos compilados com CFI */\n"
       "#endif")

s = s[:m.start()] + new + s[m.end():]
open(f, 'w').write(s)
print("OK: cfi_check agora sempre presente no struct module (ABI match com modulos CFI)")
print("--- trecho aplicado ---")
print(new)
