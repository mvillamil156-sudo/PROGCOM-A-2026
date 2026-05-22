import math,random,csv,tkinter as tk
from tkinter import ttk,filedialog,messagebox
from threading import Thread

P={'pw':400,'pc':250,'pv':25,'pe':0.20,'bc':350,'bv':10,'bec':0.95,'bed':0.95,'bmin':0.15,'bmax':0.95,'bcr':0.5,'ic':1500,'iv':12,'ii':0.97,'td':0.08,'pr':0.18,'ps':0.06,'ha':25,'co2':0.4,'lat':7.0,'pmin':2,'pmax':30,'pp':2,'bkmin':0,'bkmax':40,'bkp':5}

def consumo():
    random.seed(42);d=[0.25,0.20,0.18,0.18,0.22,0.45,0.80,1.20,0.90,0.60,0.55,0.65,0.70,0.60,0.55,0.60,0.75,1.10,1.30,1.50,1.20,0.90,0.65,0.40];f=[0.35,0.28,0.22,0.20,0.22,0.35,0.60,0.90,1.10,1.00,0.90,0.95,1.00,0.85,0.80,0.85,0.90,1.05,1.20,1.40,1.30,1.10,0.85,0.55]
    return[max(0.1,(f if n%7>=5 else d)[h]*(1+0.08*math.sin(2*math.pi*(int(n/30.44)-6)/12))*random.gauss(1,.08)) for n in range(365) for h in range(24)]

def irrad():
    random.seed(99);r=[];lr=math.radians(P['lat'])
    for d in range(365):
        dr=math.radians(23.45*math.sin(math.radians(360*(284+d)/365)));am=12-math.degrees(math.acos(max(-1,min(1,-math.tan(lr)*math.tan(dr)))))/15;fn=random.triangular(.5,1,.85)
        for h in range(24):
            hs=h+.5;om=math.radians(15*(hs-12));ct=max(0,math.sin(lr)*math.sin(dr)+math.cos(lr)*math.cos(dr)*math.cos(om))
            r.append(0 if hs<=am or hs>=24-am else max(0,1000*ct*fn*random.triangular(.6,1,.75 if h>=13 else .88)))
    return r

def simular(np,bk,ch,ih):
    ppk=np*P['pw']/1000;soc=.5 if bk>0 else 0;es=ec=rc=rv=ha=0
    for h in range(8760):
        g=(ih[h]/1000)*ppk*P['ii'];d=ch[h];es+=g;ec+=d;bal=g-d
        if bk>0:
            if bal>=0:
                mc=max(0,min(bal,bk*P['bcr'],(P['bmax']-soc)*bk));soc+=mc*P['bec']/bk;rv+=bal-mc;ha+=1
            else:
                md=max(0,min(-bal,bk*P['bcr'],(soc-P['bmin'])*bk));soc-=md/(P['bed']*bk);dr=-bal-md;rc+=dr
                if dr<.01:ha+=1
        else:
            if bal>=0:rv+=bal;ha+=1
            else:rc+=abs(bal)
    fs=max(0,min(1,1-rc/ec));return{'es':es,'ec':ec,'rc':rc,'rv':rv,'fs':fs,'aut':ha/8760*100,'co2':(ec-rc)*P['co2']}

def frc(t,n):return(t*(1+t)**n)/((1+t)**n-1) if t else 1/n
def econ(np,bk,s):
    cp=np*P['pc'];cb=bk*P['bc'];ci=P['ic'];ci2=(cp+cb)*.15
    cae=cp*frc(P['td'],P['pv'])+(cb*frc(P['td'],P['bv'])if bk else 0)+ci*frc(P['td'],P['iv'])+ci2*frc(P['td'],P['ha'])+cp*.01+s['rc']*P['pr']-s['rv']*P['ps']
    inv=cp+cb+ci+ci2;ah=s['ec']*P['pr']-cae;return{'inv':inv,'cae':cae,'ah':ah,'pb':inv/ah if ah>0 else 999}

def optimizar(ch,ih,cb=None):
    ops=list(range(int(P['pmin']),int(P['pmax'])+1,int(P['pp'])));obs=list(range(int(P['bkmin']),int(P['bkmax'])+1,int(P['bkp'])));res=[]
    for i,(np,bk) in enumerate([(a,b) for a in ops for b in obs]):
        s=simular(np,bk,ch,ih);e=econ(np,bk,s);res.append({'p':np,'b':bk,'kw':np*P['pw']/1000,**s,**e})
        if cb:cb(i/len(ops)/len(obs)*100)
    return sorted(res,key=lambda x:x['cae'])

class App(tk.Tk):
    def __init__(self):
        super().__init__();self.title("Solar Optimizer");self.geometry("860x580");self.configure(bg="#111");self.res=self.ch=self.ih=None;self._build()
    def _build(self):
        s=ttk.Style();s.theme_use('clam')
        for w,bg,fg in[('TFrame','#111','#eee'),('TLabel','#111','#eee'),('TEntry','#111','#0df'),('TButton','#1a3a5c','#0df'),('TLabelframe','#111','#eee'),('TLabelframe.Label','#111','#0df')]:s.configure(w,background=bg,foreground=fg,fieldbackground='#1a1a2e',font=('Consolas',9))
        s.configure('Treeview',background='#1a1a2e',foreground='#eee',fieldbackground='#1a1a2e',font=('Consolas',8));s.configure('Treeview.Heading',background='#1a3a5c',foreground='#0df',font=('Consolas',8,'bold'))
        nb=ttk.Notebook(self);nb.pack(fill='both',expand=True,padx=6,pady=6)
        # Tab params
        t1=ttk.Frame(nb);nb.add(t1,text=' ⚙ Parámetros ');self.vars={}
        campos=[('pw','Panel W'),('pc','Panel USD'),('pv','Vida panel a'),('bc','Bat USD/kWh'),('bv','Vida bat a'),('ic','Inversor USD'),('pr','Precio red'),('ps','Precio venta'),('td','Tasa desc.'),('ha','Horizonte a'),('lat','Latitud°'),('co2','CO2 kg/kWh'),('pmin','Min paneles'),('pmax','Max paneles'),('pp','Paso paneles'),('bkmin','Min bat kWh'),('bkmax','Max bat kWh'),('bkp','Paso bat')]
        for i,(k,l) in enumerate(campos):
            ttk.Label(t1,text=l).grid(row=i%9,column=(i//9)*2,sticky='w',padx=4,pady=2);v=tk.StringVar(value=str(P[k]));ttk.Entry(t1,textvariable=v,width=9).grid(row=i%9,column=(i//9)*2+1,padx=4,pady=2);self.vars[k]=v
        bf=ttk.Frame(t1);bf.grid(row=10,column=0,columnspan=6,pady=8)
        for txt,cmd in[('▶ Optimizar',self._run),('💾 Guardar CSV',self._save),('📂 Cargar CSV',self._load)]:ttk.Button(bf,text=txt,command=cmd).pack(side='left',padx=5)
        self.prog=ttk.Progressbar(t1,length=350);self.prog.grid(row=11,column=0,columnspan=6,pady=2)
        self.st=ttk.Label(t1,text='Listo.');self.st.grid(row=12,column=0,columnspan=6)
        # Tab resultados
        t2=ttk.Frame(nb);nb.add(t2,text=' 📊 Resultados ')
        self.lopt=ttk.Label(t2,text='— ejecuta primero —',foreground='#555');self.lopt.pack(pady=4)
        cols=('p','b','kw','fs','rc','rv','co2','inv','cae','ah','pb');hdrs=('Pan','Bat kWh','kWp','Solar%','Red kWh','Venta kWh','CO2 kg','Inv $','CAE $/a','Ahorro $/a','Payback a')
        self.tree=ttk.Treeview(t2,columns=cols,show='headings',height=14)
        [self.tree.heading(c,text=h) or self.tree.column(c,width=78,anchor='center') for c,h in zip(cols,hdrs)]
        sb=ttk.Scrollbar(t2,orient='horizontal',command=self.tree.xview);self.tree.configure(xscrollcommand=sb.set);self.tree.pack(fill='both',expand=True);sb.pack(fill='x')
    def _sync(self):
        for k,v in self.vars.items():
            try:P[k]=float(v.get()) if '.' in v.get() else int(v.get())
            except:pass
    def _run(self):
        self._sync();self.st.config(text='Generando...')
        def go():
            self.ch=consumo();self.ih=irrad();self.res=optimizar(self.ch,self.ih,lambda p:self.prog.configure(value=p) or self.st.config(text=f'{p:.0f}%'));self.after(0,self._show)
        Thread(target=go,daemon=True).start()
    def _show(self):
        o=self.res[0];self.lopt.config(text=f"☀{o['p']}pan {o['kw']:.1f}kWp  🔋{o['b']}kWh  F.Solar:{o['fs']*100:.1f}%  CO2:{o['co2']:.0f}kg  Inv:${o['inv']:,.0f}  CAE:${o['cae']:,.0f}/a  Ahorro:${o['ah']:,.0f}  PB:{o['pb']:.1f}a",foreground='#0df')
        [self.tree.delete(w) for w in self.tree.get_children()]
        [self.tree.insert('','end',values=(r['p'],r['b'],f"{r['kw']:.1f}",f"{r['fs']*100:.1f}",f"{r['rc']:.0f}",f"{r['rv']:.0f}",f"{r['co2']:.0f}",f"{r['inv']:,.0f}",f"{r['cae']:,.0f}",f"{r['ah']:,.0f}",f"{r['pb']:.1f}")) for r in self.res[:15]]
        self.st.config(text=f'✅ {len(self.res)} combinaciones.')
    def _save(self):
        if not self.res:return messagebox.showwarning('','Optimiza primero.')
        fp=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')])
        if fp:
            with open(fp,'w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=self.res[0].keys());w.writeheader();w.writerows(self.res)
            messagebox.showinfo('','Guardado: '+fp)
    def _load(self):
        fp=filedialog.askopenfilename(filetypes=[('CSV','*.csv')])
        if fp:
            with open(fp,newline='',encoding='utf-8') as f:rows=list(csv.DictReader(f))
            for r in rows:
                for k in r:
                    try:r[k]=float(r[k])
                    except:pass
            self.res=sorted(rows,key=lambda x:x['cae']);self._show();messagebox.showinfo('',f'{len(self.res)} resultados cargados.')

App().mainloop()
