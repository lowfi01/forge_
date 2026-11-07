#!/usr/bin/env python3
"""Concurrency-safe local worklog writer. Standard library only."""
from __future__ import annotations
import argparse, contextlib, datetime as dt, hashlib, json, os, random, re, shutil, sys, tempfile, time, uuid
from pathlib import Path
KEY_RE = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$')
def version(data): return hashlib.sha256(data).hexdigest()[:16]
def norm(p): return os.path.normcase(os.path.normpath(os.path.abspath(str(p))))
class WorklogError(Exception):
    def __init__(self,message,code=3): self.code=code; super().__init__(message)
def fail(msg,code=3): raise WorklogError(msg,code)
def retry(fn):
    delay=.025
    for i in range(10):
        try: return fn()
        except PermissionError:
            if i==9: raise
            time.sleep(delay); delay=min(delay*1.8,.5)
def read_bytes(p): return retry(lambda:Path(p).read_bytes())
def atomic_bytes(path,data):
    path=Path(path); retry(lambda:path.parent.mkdir(parents=True,exist_ok=True)); fd,tmp=retry(lambda:tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=str(path.parent)))
    try:
        with os.fdopen(fd,'wb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
        retry(lambda:os.replace(tmp,path))
    except BaseException:
        with contextlib.suppress(OSError): retry(lambda:os.unlink(tmp))
        raise
def safe_path(root,path):
    p=Path(path)
    if p.is_symlink(): fail(f'Refusing symlink: {p}')
    try: p.resolve().relative_to(root.resolve())
    except (ValueError,OSError): fail(f'Path escapes worklog folder: {p}')
    return p
def validate_folder(raw):
    p=Path(raw)
    if not p.is_absolute() or not p.is_dir(): fail('--folder must be an existing absolute directory')
    return p.resolve()
class Guard:
    def __init__(self,folder): self.folder=folder
    def __enter__(self):
        d=self.folder/'.locks'
        if d.is_symlink():fail('Refusing symlink lock directory')
        retry(lambda:d.mkdir(exist_ok=True)); lp=d/'.guard'
        if lp.is_symlink(): fail('Refusing symlink lock file')
        self.f=retry(lambda:open(lp,'a+b')); deadline=time.monotonic()+20
        while True:
            try:
                if os.name=='nt':
                    import msvcrt
                    self.f.seek(0); msvcrt.locking(self.f.fileno(),msvcrt.LK_NBLCK,1)
                else:
                    import fcntl
                    fcntl.flock(self.f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
                return self
            except (OSError,BlockingIOError):
                if time.monotonic()>=deadline: self.f.close(); fail('Worklog busy; guard not acquired in 20 seconds',5)
                time.sleep(random.uniform(.025,.09))
    def __exit__(self,*_):
        try:
            if os.name=='nt':
                import msvcrt
                self.f.seek(0); msvcrt.locking(self.f.fileno(),msvcrt.LK_UNLCK,1)
            else:
                import fcntl
                fcntl.flock(self.f.fileno(),fcntl.LOCK_UN)
        except OSError: pass
        self.f.close()
def find_file(folder,key):
    rx=re.compile(r'^'+re.escape(key)+r'\s*[-–—]\s',re.I); matches=[]
    for n in retry(lambda:os.listdir(folder)):
        if n.lower().endswith('.md') and rx.match(n):
            p=safe_path(folder,folder/n)
            if p.exists(): matches.append(p)
    if len(matches)>1: fail('More than one file for key; ask the user which is the worklog: '+', '.join(x.name for x in matches))
    return matches[0] if matches else None
def utf8(path):
    try: return read_bytes(path).decode('utf-8-sig')
    except UnicodeDecodeError: fail('File is not UTF-8; write it with the Write tool (UTF-8), not Set-Content or a pipe')
def check_key(key):
    if not KEY_RE.fullmatch(key): fail('Invalid key; use a safe canonical key such as repo-123 (not org/repo#123)')
def names_key(text,key):
    return bool(re.search(r'(?im)^(?:key|jira):\s*[\'\"]?'+re.escape(key)+r"[\'\"]?\s*$",text) or re.search(r'(?im)^#\s*'+re.escape(key)+r':',text))
def sections(text):
    if '## Session Log' not in text:return []
    return [s.rstrip('\n')+'\n' for s in re.findall(r'(?ms)^### .*?(?=^### |\Z)',text.split('## Session Log',1)[1])]
def section_date(section):
    m=re.match(r'### (\d{4}-\d{2}-\d{2})',section)
    return m.group(1) if m else None
def history_check(old,new,operation_date=None):
    before,after=sections(old),sections(new)
    if not before:return
    today=operation_date or dt.datetime.now().strftime('%Y-%m-%d')
    # Strip script receipts for comparison; receipts are transport metadata, not history.
    clean=lambda s: re.sub(r'(?m)^<!-- worklog-operation:[0-9a-f]{32} -->\n?', '', s)
    actual=[clean(s) for s in after]
    hits=[i for i,s in enumerate(before) if section_date(s)==today]
    if len(hits)>1:fail('History conflict: multiple operation-date Session Log sections')
    if hits:
        calendar_today=dt.datetime.now().strftime('%Y-%m-%d')
        offset=int(bool(actual and section_date(actual[0])==calendar_today and not any(section_date(s)==calendar_today for s in before)))
        if len(actual)!=len(before)+offset:
            fail('History conflict: dated Session Log sections were added, removed, or reordered')
        for i,old_section in enumerate(before):
            current=actual[i+offset]
            if i==hits[0]:
                if not current.startswith(clean(old_section)):
                    fail('History conflict: the operation-date entry may only be appended to in place')
            elif current!=clean(old_section):
                fail('History conflict: earlier Session Log entries must remain byte-identical and in order')
    else:
        if len(actual)!=len(before)+1 or actual[1:]!=[clean(s) for s in before] or not actual or section_date(actual[0])!=today:
            fail('History conflict: new operation-date section must be prepended')
def base_path(cp): return Path(str(cp)+'.base')
def get_base(cp,key,folder):
    try: m=json.loads(utf8(base_path(cp)))
    except Exception: fail('Not a checkout copy; run checkout first')
    if not isinstance(m,dict) or set(m)!={'key','folder','base'} or m['key']!=key or m['folder']!=norm(folder) or not (m['base']=='none' or re.fullmatch('[0-9a-f]{16}',str(m['base']))): fail('Malformed or mismatched checkout sidecar; run checkout again')
    return m
def receipt(op): return f'<!-- worklog-operation:{op} -->'
def op_load(folder,op):
    if not re.fullmatch('[0-9a-f]{32}',op):fail('Invalid operation UUID')
    p=safe_path(folder,folder/'.operations'/(op+'.json'))
    try:o=json.loads(utf8(p))
    except Exception:fail('Unknown or malformed operation')
    if (not isinstance(o,dict) or o.get('version')!=1 or o.get('id')!=op or o.get('folder')!=norm(folder)
        or not isinstance(o.get('pending'),list) or any(x not in ('ticket','epic','daily') for x in o['pending'])
        or len(set(o['pending']))!=len(o['pending']) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(o.get('date','')))
        or not re.fullmatch(r'\d{2}:\d{2}',str(o.get('time',''))) or not isinstance(o.get('body'),str)
        or not isinstance(o.get('heading'),str) or not isinstance(o.get('folder'),str)):
        fail('Malformed operation sidecar')
    return p,o
def op_save(p,o):atomic_bytes(p,(json.dumps(o,ensure_ascii=False,sort_keys=True)+'\n').encode())
def has_receipt(path,op):return path.exists() and receipt(op) in utf8(path)
def valid_name(name,key):
    if (not name or not name.startswith(key+' - ') or not name.endswith('.md') or name[:-3].endswith((' ','.'))
        or any(ord(c)<32 or c in '<>:"/\\|?*' for c in name) or Path(name).name!=name):
        fail(f"Unsafe --name. Use '{key} - Fix login.md' (no reserved characters or paths)")
def cmd_checkout(a):
    check_key(a.key); folder=validate_folder(a.folder); d=Path(a.to_dir)
    if not d.is_absolute():fail('--to-dir must be absolute')
    retry(lambda:d.mkdir(parents=True,exist_ok=True))
    with Guard(folder):
        src=find_file(folder,a.key); base=version(read_bytes(src)) if src else 'none'; cp=d/(a.key+'-'+uuid.uuid4().hex[:8]+'.md')
        if src:retry(lambda:shutil.copyfile(src,cp))
        atomic_bytes(base_path(cp),json.dumps({'key':a.key,'folder':norm(folder),'base':base}).encode())
    print(json.dumps({'path':str(src) if src else None,'base':base,'copy':str(cp),'next':'Read the copy, edit it, then commit' if src else "Write the new file's full text to the copy, then commit with --name"}))
def do_commit(folder,key,copy,name,operation=None,stage=None):
    check_key(key); folder=validate_folder(folder); cp=Path(copy)
    with Guard(folder):
        op_path=o=None
        if operation:
            op_path,o=op_load(folder,operation)
            if stage not in ('ticket','epic') or o.get(stage+'_key')!=key:fail('Operation stage/key mismatch')
            target=find_file(folder,key)
            if target and has_receipt(target,operation):
                if stage in o['pending']:
                    o['pending'].remove(stage);op_save(op_path,o)
                print(json.dumps({'path':str(target),'base':version(read_bytes(target)),'recovered':True}));return
            if stage not in o['pending']:fail('Operation stage is already complete')
            if not o['pending'] or o['pending'][0]!=stage:fail('Operation stages must be committed in order: '+', '.join(o['pending']))
        if not cp.is_absolute() or cp.is_symlink() or not cp.is_file():fail('--file must be an absolute regular checkout copy')
        m=get_base(cp,key,folder); new=utf8(cp)
        if not new.strip():fail('Checkout copy is empty')
        if not names_key(new,key):fail('Copy does not name this key (wrong copy?)')
        if m['base']=='none':
            if not name:fail('--name is required for a new key')
            valid_name(name,key)
        target=find_file(folder,key)
        current=version(read_bytes(target)) if target else 'none'
        if current!=m['base']:fail('Conflict: file changed since checkout; check out again and redo the update',6)
        if target is None:target=folder/name
        old=read_bytes(target).decode('utf-8-sig') if target.exists() else ''
        history_check(old,new,o['date'] if operation else None)
        if operation:new=new.rstrip()+'\n\n'+receipt(operation)+'\n'
        data=(new.rstrip()+'\n').encode('utf-8');atomic_bytes(target,data)
        if operation:o['pending'].remove(stage);op_save(op_path,o)
    for p in (cp,base_path(cp)):
        with contextlib.suppress(OSError):p.unlink()
    print(json.dumps({'path':str(target),'base':version(data)}))
def cmd_commit(a):do_commit(a.folder,a.key,a.file,a.name,a.operation,a.stage)
def body_check(body):
    if len(body.strip())>2000:fail('Daily body exceeds 2000 characters; move detail to the ticket file')
    for f in ('**What:**','**Why:**','**Outcome:**','**Next:**'):
        if f not in body:fail('Daily body is missing '+f)
def daily_write(folder,heading,body,session=None,operation=None,when=None):
    if not heading.strip() or '\n' in heading or '\r' in heading:fail('--heading must be one non-empty line')
    body_check(body); when=when or dt.datetime.now(); daily=folder/'daily'
    if daily.is_symlink():fail('Refusing symlink daily directory')
    retry(lambda:daily.mkdir(exist_ok=True)); path=safe_path(folder,daily/(when.strftime('%Y-%m-%d')+'.md'))
    with Guard(folder):
        op_path=o=None
        if operation:
            op_path,o=op_load(folder,operation)
            if heading!=o['heading'] or body.strip()!=o['body'] or session!=o.get('session'):
                fail('Daily heading, body, and session must match the frozen begin operation')
            when=dt.datetime.strptime(o['date']+' '+o['time'],'%Y-%m-%d %H:%M')
            path=safe_path(folder,daily/(o['date']+'.md'))
            if has_receipt(path,operation):
                if 'daily' in o['pending']:
                    o['pending'].remove('daily');op_save(op_path,o)
                return path,True
            if 'daily' not in o['pending']:fail('Operation daily stage is already complete')
            if o['pending'][0]!='daily':fail('Operation stages must be committed in order: '+', '.join(o['pending']))
        old=utf8(path) if path.exists() else ''
        if not old.strip():old=f'# {when:%Y-%m-%d}\n'
        block=f"\n### {when:%H:%M} · {heading}"+(f' · {session}' if session else '')+f"\n{body.strip()}\n"
        if operation:block+=receipt(operation)+'\n'
        atomic_bytes(path,(old.rstrip()+'\n'+block).encode('utf-8'))
        if operation:
            o['pending'].remove('daily');op_save(op_path,o)
    return path,False
def cmd_daily(a):
    folder=validate_folder(a.folder); body=utf8(a.body_file); p,_=daily_write(folder,a.heading,body,a.session,a.operation);print(str(p))
def cmd_begin(a):
    folder=validate_folder(a.folder); key=a.key; epic=a.epic
    if key:check_key(key)
    if epic:check_key(epic)
    if key and epic and key.casefold()==epic.casefold():fail('Ticket and epic keys must be different')
    if not a.heading.strip() or '\n' in a.heading or '\r' in a.heading:fail('--heading must be one non-empty line')
    body=utf8(a.body_file);body_check(body);now=dt.datetime.now();op=uuid.uuid4().hex;od=folder/'.operations'
    if od.is_symlink():fail('Refusing symlink operations directory')
    retry(lambda:od.mkdir(exist_ok=True));pending=(['ticket'] if key else [])+(['epic'] if epic else [])+['daily']
    o={'version':1,'id':op,'folder':norm(folder),'date':now.strftime('%Y-%m-%d'),'time':now.strftime('%H:%M'),'heading':a.heading,'session':a.session,'body':body.strip(),'key':key,'ticket_key':key,'epic_key':epic,'pending':pending}
    with Guard(folder):op_save(od/(op+'.json'),o)
    print(json.dumps({'operation':op,'pending':pending,'date':o['date'],'time':o['time']}))
def cmd_status(a):
    folder=validate_folder(a.folder)
    with Guard(folder):
        if a.operation:
            _,o=op_load(folder,a.operation);done=[]
            for st in ('ticket','epic'):
                k=o.get(st+'_key');p=find_file(folder,k) if k and st in o['pending'] else None
                if p and has_receipt(p,o['id']):done.append(st)
            dp=folder/'daily'/(o['date']+'.md')
            if 'daily' in o['pending'] and has_receipt(dp,o['id']):done.append('daily')
            print(json.dumps({'operation':o['id'],'completed':done,'pending':[x for x in o['pending'] if x not in done]}));return
        ops=[];od=folder/'.operations'
        if od.exists():
            for p in sorted(od.iterdir()):
                if p.suffix=='.json':
                    try:o=json.loads(utf8(p));ops.append({'operation':o['id'],'pending':o['pending']})
                    except Exception:ops.append({'operation':p.stem,'error':'malformed'})
        print(json.dumps({'operations':ops}))
def main(argv=None):
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8',errors='replace')
    if hasattr(sys.stderr,'reconfigure'):sys.stderr.reconfigure(encoding='utf-8',errors='replace')
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('checkout');q.add_argument('--folder',required=True);q.add_argument('--key',required=True);q.add_argument('--to-dir',required=True);q.set_defaults(fn=cmd_checkout)
    q=s.add_parser('commit');q.add_argument('--folder',required=True);q.add_argument('--key',required=True);q.add_argument('--file',required=True);q.add_argument('--name');q.add_argument('--operation');q.add_argument('--stage',choices=['ticket','epic']);q.set_defaults(fn=cmd_commit)
    q=s.add_parser('append-daily');q.add_argument('--folder',required=True);q.add_argument('--heading',required=True);q.add_argument('--body-file',required=True);q.add_argument('--session');q.add_argument('--operation');q.set_defaults(fn=cmd_daily)
    q=s.add_parser('begin');q.add_argument('--folder',required=True);q.add_argument('--key');q.add_argument('--epic');q.add_argument('--heading',required=True);q.add_argument('--body-file',required=True);q.add_argument('--session');q.set_defaults(fn=cmd_begin)
    q=s.add_parser('status');q.add_argument('--folder',required=True);q.add_argument('--operation');q.set_defaults(fn=cmd_status)
    a=p.parse_args(argv)
    try:a.fn(a);return 0
    except WorklogError as e:print(str(e),file=sys.stderr);return e.code
    except Exception as e:print(f'worklog: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
