import json, os, subprocess, sys, time
status_path, log_path = sys.argv[1], sys.argv[2]
cmd = sys.argv[3:]
def write_status(payload):
    tmp = status_path + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(payload, f)
    os.replace(tmp, status_path)
base = {'pid': os.getpid(), 'childPid': None, 'startedAt': int(time.time())}
write_status(dict(base, running=True, exitCode=None, beat=int(time.time())))
env = dict(os.environ)
env['PYTHONUNBUFFERED'] = '1'
with open(log_path, 'ab', buffering=0) as log:
    proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT, env=env)
    base['childPid'] = proc.pid
    while proc.poll() is None:
        write_status(dict(base, running=True, exitCode=None, beat=int(time.time())))
        time.sleep(10)
    rc = proc.returncode
write_status(dict(base, running=False, exitCode=rc, beat=int(time.time())))
