#!/usr/bin/env python3
# Move o bloco SYSVIPC (sysvsem/sysvshm) do MEIO do struct task_struct
# para o FIM (logo antes de 'struct thread_struct thread;').
# Motivo: habilitamos CONFIG_SYSVIPC (preciso pro IPC_NS do Droidspaces), mas o
# stock tem SYSVIPC=off. Os modulos do /vendor foram compilados com o layout
# stock (sem sysvsem) e acessam current->cred/comm/nsproxy em offsets fixos.
# Inserir sysvsem no meio desloca esses campos -> corrupcao em runtime (com
# MODVERSIONS off nao e' pego). Movendo pro fim, todos os campos que os modulos
# acessam mantem os offsets do stock, e o kernel ainda tem SYSVIPC funcional.
import re, sys

f = 'include/linux/sched.h'
s = open(f).read()

pat = re.compile(r'\n[ \t]*#ifdef CONFIG_SYSVIPC\b[^\n]*\n(?:[^\n]*\n)*?[ \t]*#endif[^\n]*\n')
block = None
span = None
for m in pat.finditer(s):
    if 'sysvsem' in m.group(0):
        block = m.group(0)
        span = m.span()
        break

if not block:
    print("ERRO: bloco SYSVIPC com sysvsem nao encontrado em sched.h")
    sys.exit(1)

# remove do lugar original
s = s[:span[0]] + '\n' + s[span[1]:]

# acha o campo thread_struct (deve ser o ultimo do task_struct)
tm = re.search(r'\n([ \t]*)struct thread_struct[ \t]+thread;', s)
if not tm:
    print("ERRO: campo 'struct thread_struct thread;' nao encontrado")
    sys.exit(1)

ins = '\n' + block.strip('\n') + '\n'
s = s[:tm.start()] + ins + s[tm.start():]

open(f, 'w').write(s)
print("OK: bloco SYSVIPC movido para antes de thread_struct")
print("--- bloco movido ---")
print(block.strip())
