import json, os, subprocess, sys, tempfile, unittest, time, threading, datetime, re, shutil
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/'skills/worklog/scripts/worklog.py'
BODY='**What:** Changed it.\n**Why:** Needed the answer.\n**Outcome:** Result observed.\n**Next:** none\n→ [PROJ-1](<../PROJ-1 - Example.md>)'
class WorklogTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory(); self.root=Path(self.t.name)/'folder'; self.root.mkdir(); self.scratch=Path(self.t.name)/'scratch'; self.scratch.mkdir(); self.bodyfile=Path(self.t.name)/'body.txt'; self.writebody(BODY)
 def tearDown(self): self.t.cleanup()
 def writebody(self,s): self.bodyfile.write_text(s,encoding='utf-8')
 def runw(self,*args,timeout=40): return subprocess.run([sys.executable,str(SCRIPT),*map(str,args)],capture_output=True,text=True,timeout=timeout)
 def checkout(self,key='PROJ-1'):
  r=self.runw('checkout','--folder',self.root,'--key',key,'--to-dir',self.scratch); self.assertEqual(r.returncode,0,r.stderr); return json.loads(r.stdout)
 def daily(self,heading='PROJ-1 · fix',bodyfile=None,*extra): return self.runw('append-daily','--folder',self.root,'--heading',heading,'--body-file',bodyfile or self.bodyfile,*extra)
 def test_daily_concurrency_150_utf8_and_header(self):
  ps=[]
  for i in range(150):
   b=Path(self.t.name)/f'b{i}'; b.write_text(BODY+f'\nmarker-{i}',encoding='utf-8')
   ps.append(subprocess.Popen([sys.executable,str(SCRIPT),'append-daily','--folder',str(self.root),'--heading',f'PROJ-1 · fix {i}','--body-file',str(b)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True))
  for p in ps:
   out,err=p.communicate(timeout=60); self.assertEqual(p.returncode,0,err)
  files=list((self.root/'daily').glob('*.md')); self.assertEqual(len(files),1); text=files[0].read_text(encoding='utf-8')
  self.assertEqual(text.count('# '+files[0].stem),1); self.assertEqual(text.count('### '),150); self.assertIn('·',text); self.assertIn('→',text); self.assertTrue(all(len(re.findall(rf'^marker-{i}$',text,re.M))==1 for i in range(150)))
 def test_daily_validation_bom_missing_relative_and_missing_folder(self):
  self.writebody('**What:** x\n**Outcome:** y\n**Next:** none'); self.assertEqual(self.daily().returncode,3)
  self.writebody(BODY+'\n'+'x'*2100); self.assertEqual(self.daily().returncode,3)
  cp=Path(self.t.name)/'cp'; cp.write_bytes((BODY.replace('→','arrow')+' café').encode('cp1252')); r=self.daily(bodyfile=cp); self.assertEqual(r.returncode,3); self.assertIn('Write tool',r.stderr)
  self.writebody('\ufeff'+BODY); self.assertEqual(self.daily().returncode,0); self.assertNotIn('\ufeff',(self.root/'daily').glob('*.md').__iter__().__next__().read_text())
  r=self.runw('append-daily','--folder',self.root,'--heading','H'); self.assertEqual(r.returncode,2)
  r=self.runw('checkout','--folder','relative','--key','PROJ-1','--to-dir',self.scratch); self.assertEqual(r.returncode,3)
  missing=self.root/'absent'; r=self.runw('checkout','--folder',missing,'--key','PROJ-1','--to-dir',self.scratch); self.assertEqual(r.returncode,3); self.assertFalse(missing.exists())
 def test_new_key_names_unique_and_two_new_conflict(self):
  a=self.checkout(); b=self.checkout(); self.assertEqual(a['base'],'none'); self.assertIsNone(a['path']); self.assertFalse(Path(a['copy']).exists()); self.assertNotEqual(a['copy'],b['copy'])
  Path(a['copy']).write_text('---\nkey: PROJ-1\n---\n# PROJ-1: title\n',encoding='utf-8')
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy']); self.assertEqual(r.returncode,3)
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy'],'--name','PROJ-1 - bad:name.md'); self.assertEqual(r.returncode,3); self.assertEqual(list(self.root.glob('*.md')),[])
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy'],'--name','PROJ-1 - bad\nname.md'); self.assertEqual(r.returncode,3)
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy'],'--name','PROJ-1 - ../bad.md'); self.assertEqual(r.returncode,3)
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy'],'--name','PROJ-1 - new.md'); self.assertEqual(r.returncode,0,r.stderr); self.assertFalse(Path(a['copy']).exists())
  Path(b['copy']).write_text('key: PROJ-1\n# PROJ-1: title\nB\n',encoding='utf-8'); r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',b['copy'],'--name','PROJ-1 - new.md'); self.assertEqual(r.returncode,6)
 def test_lost_update_old_copy_and_jira(self):
  today=datetime.date.today().isoformat(); p=self.root/'PROJ-1 - Example.md'; p.write_text(f'---\njira: PROJ-1\n---\n# PROJ-1: title\n\n## Session Log\n\n### {today}\n- first\n',encoding='utf8')
  a=self.checkout(); b=self.checkout(); Path(b['copy']).write_text(Path(b['copy']).read_text()+'\nB-entry\n',encoding='utf8')
  self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',b['copy']).returncode,0)
  Path(a['copy']).write_text(Path(a['copy']).read_text()+'\nA-entry\n',encoding='utf8'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy']).returncode,6); self.assertIn('B-entry',p.read_text()); self.assertNotIn('A-entry',p.read_text())
  new=self.checkout(); Path(a['copy']).write_text(Path(a['copy']).read_text()+'again',encoding='utf8'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',a['copy']).returncode,6)
  Path(new['copy']).write_text(Path(new['copy']).read_text()+'\nA-entry\n',encoding='utf8'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',new['copy']).returncode,0); self.assertIn('B-entry',p.read_text()); self.assertIn('A-entry',p.read_text())
 def test_wrong_copy_duplicate_matching_and_bracket_path(self):
  e=self.checkout('PROJ-2'); Path(e['copy']).write_text('key: PROJ-2\n# PROJ-2: title\n',encoding='utf8'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',e['copy']).returncode,3)
  (self.root/'PROJ-30 - one.md').write_text('x'); self.assertEqual(self.checkout('PROJ-3')['base'],'none')
  (self.root/'PROJ-4 – spaced.md').write_text('key: PROJ-4\n# PROJ-4: title'); self.assertNotEqual(self.checkout('PROJ-4')['base'],'none')
  (self.root/'PROJ-5 - one.md').write_text('x'); (self.root/'PROJ-5 - two.md').write_text('x'); r=self.runw('checkout','--folder',self.root,'--key','PROJ-5','--to-dir',self.scratch); self.assertEqual(r.returncode,3); self.assertIn('more than one',r.stderr.lower())
  self.assertEqual(self.runw('checkout','--folder',self.root,'--key','org/repo#12','--to-dir',self.scratch).returncode,3)
  weird=Path(self.t.name)/'has[bracket]'; weird.mkdir(); (weird/'PROJ-6 - x.md').write_text('x'); r=self.runw('checkout','--folder',weird,'--key','PROJ-6','--to-dir',self.scratch); self.assertEqual(r.returncode,0); self.assertNotEqual(json.loads(r.stdout)['base'],'none')
  outside=Path(self.t.name)/'outside'; outside.mkdir(); link=self.root/'.locks'; shutil.rmtree(link); link.symlink_to(outside,target_is_directory=True); r=self.runw('status','--folder',self.root); self.assertEqual(r.returncode,3); self.assertFalse((outside/'.guard').exists()); link.unlink()
 def test_wrong_key_content_and_file_not_checkout(self):
  f=Path(self.t.name)/'stranger'; f.write_text('key: PROJ-1\n# PROJ-1: title'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',f).returncode,3)
  c=self.checkout(); Path(c['copy']).write_text('key: OTHER\n# OTHER: t'); self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',c['copy']).returncode,3)
 def test_contention_64_with_retries_and_negative_control(self):
  base=self.root/'PROJ-1 - shared.md'; base.write_text('key: PROJ-1\n# PROJ-1: Shared\n'); lock=threading.Lock(); outcomes=[]
  def worker(w):
   for i in range(8):
    for retry in range(60):
     c=self.checkout(); p=Path(c['copy']); p.write_text(p.read_text()+f'\nW{w}-{i}\n')
     r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',p)
     if r.returncode==0:break
     if r.returncode!=6:raise AssertionError(r.stderr)
    else:raise AssertionError('conflict retries exhausted')
   with lock:outcomes.append(w)
  ts=[threading.Thread(target=worker,args=(w,)) for w in range(8)]
  [t.start() for t in ts]; [t.join(90) for t in ts]; self.assertEqual(len(outcomes),8)
  text=base.read_text(); self.assertTrue(all(text.count(f'W{w}-{i}')==1 for w in range(8) for i in range(8)))
  # Deterministic negative control: two unguarded readers both replace from the same old snapshot.
  plain=self.root/'naive.txt'; plain.write_text('seed\n'); snapshot=plain.read_text(); barrier=threading.Barrier(2)
  def naive(line):
   value=snapshot+line+'\n'; barrier.wait(); plain.write_text(value)
  tt=[threading.Thread(target=naive,args=(f'N{i}',)) for i in range(2)]; [t.start() for t in tt]; [t.join() for t in tt]; n=plain.read_text(); self.assertFalse(all(f'N{i}' in n for i in range(2)))
 def test_history_enforcement(self):
  today=datetime.date.today().isoformat(); p=self.root/'PROJ-1 - x.md'; p.write_text(f'key: PROJ-1\n# PROJ-1: x\n\n## Session Log\n\n### {today}\n- today\n\n### 2026-10-01\n- old\n')
  c=self.checkout(); s=Path(c['copy']); s.write_text(s.read_text().replace('- today','- edited today\n- new'))
  self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',s).returncode,3)
  c=self.checkout(); s=Path(c['copy']); s.write_text(s.read_text().replace('- today','- today\n- appended'))
  self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',s).returncode,0)
  c=self.checkout(); s=Path(c['copy']); s.write_text(s.read_text().replace('- old','- changed old'))
  self.assertEqual(self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',s).returncode,3)
  import importlib.util
  spec=importlib.util.spec_from_file_location('worklog_history',SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
  operation_date=(datetime.date.today()-datetime.timedelta(days=1)).isoformat(); older=(datetime.date.today()-datetime.timedelta(days=2)).isoformat(); today=datetime.date.today().isoformat()
  old=f'## Session Log\n\n### {operation_date}\n- old date\n\n### {older}\n- older\n'
  new=f'## Session Log\n\n### {today}\n- newer\n\n### {operation_date}\n- old date\n- appended by frozen operation\n\n### {older}\n- older\n'
  mod.history_check(old,new,operation_date)
  old_only=f'## Session Log\n\n### {older}\n- older\n'
  new_day=f'## Session Log\n\n### {today}\n- first entry\n\n### {older}\n- older\n'
  mod.history_check(old_only,new_day,today)
  with self.assertRaises(mod.WorklogError): mod.history_check(old_only,new_day.replace('- older','- rewritten'),today)
 def test_begin_status_frozen_daily_and_receipt_retry(self):
  self.assertEqual(self.runw('begin','--folder',self.root,'--key','PROJ-1','--epic','proj-1','--heading','x','--body-file',self.bodyfile).returncode,3)
  c=self.checkout(); Path(c['copy']).write_text('key: PROJ-1\n# PROJ-1: title\n'); begin=self.runw('begin','--folder',self.root,'--key','PROJ-1','--heading','PROJ-1 · fix','--body-file',self.bodyfile); self.assertEqual(begin.returncode,0,begin.stderr); op=json.loads(begin.stdout)['operation']
  Path(c['copy']).write_text(Path(c['copy']).read_text()+'done\n'); r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',c['copy'],'--name','PROJ-1 - title.md','--operation',op,'--stage','ticket'); self.assertEqual(r.returncode,0,r.stderr)
  status=json.loads(self.runw('status','--folder',self.root,'--operation',op).stdout); self.assertEqual(status['pending'],['daily'])
  # Journal remains pending to simulate crash after replace: retry succeeds even after copy removal.
  journal=self.root/'.operations'/(op+'.json'); o=json.loads(journal.read_text()); o['pending']=['ticket','daily']; journal.write_text(json.dumps(o))
  r=self.runw('commit','--folder',self.root,'--key','PROJ-1','--file',c['copy'],'--operation',op,'--stage','ticket'); self.assertEqual(r.returncode,0,r.stderr); self.assertIn('recovered',r.stdout)
  r=self.daily('WRONG','--body-file') if False else None
  r=self.runw('append-daily','--folder',self.root,'--heading','PROJ-1 · fix','--body-file',self.bodyfile,'--operation',op); self.assertEqual(r.returncode,0,r.stderr); first=(self.root/'daily').glob('*.md'); d=next(first); txt=d.read_text(); self.assertIn('What:',txt)
  o=json.loads(journal.read_text()); o['pending']=['daily']; journal.write_text(json.dumps(o)); r=self.runw('append-daily','--folder',self.root,'--heading','PROJ-1 · fix','--body-file',self.bodyfile,'--operation',op); self.assertEqual(r.returncode,0,r.stderr); self.assertEqual(d.read_text().count('### '),1)
 def test_crash_releases_lock_and_permissions_retry(self):
  # Module-level injection exercises retry behavior more directly than subprocesses.
  import importlib.util
  spec=importlib.util.spec_from_file_location('worklog',SCRIPT); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
  count=[0]
  def flaky():
   count[0]+=1
   if count[0]<3: raise PermissionError('antivirus')
   return 'ok'
  self.assertEqual(mod.retry(flaky),'ok'); self.assertEqual(count[0],3)
  # Wait until the child confirms lock acquisition, then kill it and retry.
  code=f"import sys;sys.path.insert(0,{str(SCRIPT.parent)!r});import worklog;f=worklog.Guard(__import__('pathlib').Path({str(self.root)!r}));f.__enter__();print('READY',flush=True);sys.stdin.read()"
  p=subprocess.Popen([sys.executable,'-c',code],stdout=subprocess.PIPE,text=True); self.assertEqual(p.stdout.readline().strip(),'READY'); p.terminate(); p.wait(timeout=5); p.stdout.close()
  r=self.runw('status','--folder',self.root); self.assertEqual(r.returncode,0,r.stderr)
  # If replacement fails, the previous daily file remains intact and no partial target is visible.
  mod.daily_write(self.root,'PROJ-1 · seed',BODY)
  day=self.root/'daily'/f'{datetime.date.today():%Y-%m-%d}.md'; before=day.read_bytes()
  original=mod.os.replace
  def denied(*_): raise PermissionError('locked by indexer')
  mod.os.replace=denied; mod.time.sleep=lambda _:None
  with self.assertRaises(PermissionError): mod.daily_write(self.root,'PROJ-1 · fail',BODY)
  mod.os.replace=original
  self.assertEqual(day.read_bytes(),before); self.assertFalse(list(day.parent.glob('*.tmp')))
if __name__=='__main__':unittest.main(verbosity=2)
