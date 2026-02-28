import subprocess, sys

p = subprocess.run(['netstat','-ano'], capture_output=True, text=True)
lines = [l.strip() for l in p.stdout.splitlines() if ':5000' in l]
if not lines:
    print('NO_LISTENERS')
    sys.exit(0)
# Extract unique PIDs
pids = sorted({int(l.split()[-1]) for l in lines})
print('FOUND_PIDS:', pids)
for pid in pids:
    try:
        t = subprocess.run(['tasklist','/FI',f'PID eq {pid}','/FO','CSV','/NH'], capture_output=True, text=True)
        out = t.stdout.strip()
        image = ''
        if out:
            parts = [s.strip('"') for s in out.split(',')]
            image = parts[0] if parts else ''
        print(f'PID {pid} -> {image}')
        # attempt to kill the PID
        k = subprocess.run(['taskkill','/PID',str(pid),'/F','/T'], capture_output=True, text=True)
        print(k.stdout.strip() or k.stderr.strip())
    except Exception as e:
        print('ERROR killing', pid, e)

# Show remaining listeners
p2 = subprocess.run(['netstat','-ano'], capture_output=True, text=True)
rem = [l.strip() for l in p2.stdout.splitlines() if ':5000' in l]
print('REMAINING_LISTENERS:')
for l in rem:
    print(l)

