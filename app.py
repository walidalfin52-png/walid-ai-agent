import os, sqlite3, secrets
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from openai import OpenAI
APP_NAME='WALID AI OFFICE'; DB_PATH=os.environ.get('DATABASE_PATH','walid_office.db')
app=Flask(__name__); app.secret_key=os.environ.get('SECRET_KEY',secrets.token_hex(32))
OWNER_PASSWORD=os.environ.get('OWNER_PASSWORD','ubah-password-ini'); MODEL=os.environ.get('OPENAI_MODEL','gpt-4o-mini')
AGENTS=[('Direktur Operasional','Mengatur prioritas, koordinasi, dan ringkasan operasional.'),('Sekretaris','Menyusun surat, email, notulen, dan jadwal.'),('Manajer Proyek','Memecah proyek menjadi tahapan, tenggat, dan tindak lanjut.'),('Keuangan','Membantu pencatatan, anggaran, dan analisis keuangan.'),('Pemasaran','Menyusun strategi pemasaran, konten, dan kampanye.'),('Penjualan','Membantu prospek, penawaran, dan tindak lanjut pelanggan.'),('Riset & Analisis','Mengumpulkan, membandingkan, dan merangkum informasi.'),('Administrasi','Mengelola dokumen, daftar, dan pekerjaan administrasi.')]
def db():
 c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c
def init_db():
 with db() as c:
  c.execute('CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL,agent TEXT NOT NULL,status TEXT NOT NULL,result TEXT DEFAULT "",created_at TEXT NOT NULL,updated_at TEXT NOT NULL)')
  c.execute('CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY AUTOINCREMENT,message TEXT NOT NULL,created_at TEXT NOT NULL)')
def log(msg):
 with db() as c:c.execute('INSERT INTO activity(message,created_at) VALUES(?,?)',(msg,datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
def owner(fn):
 @wraps(fn)
 def w(*a,**k): return fn(*a,**k) if session.get('owner') else redirect(url_for('login'))
 return w
@app.route('/login',methods=['GET','POST'])
def login():
 if request.method=='POST':
  if secrets.compare_digest(request.form.get('password',''),OWNER_PASSWORD): session['owner']=True; log('Owner masuk'); return redirect(url_for('index'))
  flash('Password tidak sesuai.')
 return render_template('login.html',app_name=APP_NAME)
@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/')
@owner
def index():
 with db() as c:
  tasks=c.execute('SELECT * FROM tasks ORDER BY id DESC LIMIT 30').fetchall(); acts=c.execute('SELECT * FROM activity ORDER BY id DESC LIMIT 10').fetchall(); counts={r['status']:r['n'] for r in c.execute('SELECT status,COUNT(*) n FROM tasks GROUP BY status')}
 return render_template('index.html',app_name=APP_NAME,agents=AGENTS,tasks=tasks,activities=acts,counts=counts)
@app.post('/tasks/new')
@owner
def new_task():
 title=request.form.get('title','').strip(); desc=request.form.get('description','').strip(); agent=request.form.get('agent','')
 if not title or not desc or agent not in [a[0] for a in AGENTS]: flash('Lengkapi semua kolom.'); return redirect(url_for('index'))
 now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 with db() as c:c.execute('INSERT INTO tasks(title,description,agent,status,created_at,updated_at) VALUES(?,?,?,"Menunggu",?,?)',(title,desc,agent,now,now))
 log('Tugas baru: '+title); flash('Tugas berhasil dibuat.'); return redirect(url_for('index'))
@app.post('/tasks/<int:tid>/run')
@owner
def run_task(tid):
 with db() as c:t=c.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
 if not t: flash('Tugas tidak ditemukan.'); return redirect(url_for('index'))
 key=os.environ.get('OPENAI_API_KEY','').strip()
 if not key: flash('OPENAI_API_KEY belum diatur di hosting.'); return redirect(url_for('index'))
 role=next((d for n,d in AGENTS if n==t['agent']),'')
 try:
  r=OpenAI(api_key=key).responses.create(model=MODEL,instructions=f'Anda adalah {t["agent"]} di WALID AI OFFICE. {role} Jawab dalam Bahasa Indonesia, praktis dan terstruktur. Jangan mengaku melakukan tindakan eksternal.',input=f'Judul: {t["title"]}\nInstruksi: {t["description"]}')
  now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  with db() as c:c.execute('UPDATE tasks SET result=?,status="Menunggu Persetujuan",updated_at=? WHERE id=?',(r.output_text,now,tid))
  log(f'Draf tugas #{tid} selesai; menunggu persetujuan Owner'); flash('Draf AI selesai. Tinjau sebelum menyetujui.')
 except Exception as e: log(f'Eksekusi #{tid} gagal: {type(e).__name__}'); flash('Gagal menjalankan AI. Periksa API key dan pengaturan akun.')
 return redirect(url_for('index'))
@app.post('/tasks/<int:tid>/<action>')
@owner
def decision(tid,action):
 if action not in ('approve','reject'): return redirect(url_for('index'))
 status='Disetujui' if action=='approve' else 'Perlu Revisi'; now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
 with db() as c:cur=c.execute('UPDATE tasks SET status=?,updated_at=? WHERE id=? AND status="Menunggu Persetujuan"',(status,now,tid))
 if cur.rowcount: log(f'Owner mengubah tugas #{tid}: {status}'); flash('Status tugas diperbarui.')
 else: flash('Tugas belum siap diproses.')
 return redirect(url_for('index'))
@app.route('/tasks/<int:tid>')
@owner
def detail(tid):
 with db() as c:t=c.execute('SELECT * FROM tasks WHERE id=?',(tid,)).fetchone()
 return render_template('task.html',app_name=APP_NAME,task=t) if t else redirect(url_for('index'))
@app.route('/health')
def health():return {'status':'ok','app':APP_NAME}
init_db()
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',8080)))
