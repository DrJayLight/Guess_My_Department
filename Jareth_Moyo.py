
from Tkinter import *
import ttk
import re
import urllib2
import time
import docclass
from threading import Timer
from bs4 import BeautifulSoup

mainlink='http://www.sehir.edu.tr'
# regular expression for catching colleges
colReg=r'([A-Z\s]+)'
# regular expression for filtering unwanted data from colleges
filReg=r'\w+\s+\w+\s+\w+'
# expressions for finding all profs in each department
profReg=r'Prof.[-]?[\s]?(.[^-]*)'
raReg=r'RA[.]?-(.[^-]*)'
instReg=r'Inst.[-]?[\s]?(.[^-]*)'
indrReg=r'Dr.-(.[^-]*)'
lecReg=r'Lecturer-(.[^-]*)'
# regular expression for catching departments in each college
depReg=r'-(.[^-]*)-Name-'
# regular expression for catching professors
prof2Reg=r'[\w.]+\s+(.*)'


class Fetcher():
    def __init__(self,url):
        self.url=url

    def fetch(self):
        c=urllib2.urlopen(self.url)
        self.soup=BeautifulSoup(c.read())
        # here we are trying to get all professors and their respective departments
        # they will be grouped under the colleges
        all_data=self.soup.find_all('div',{'id':'icsayfa_icerik'})
        data2=all_data[0].text.strip().split('\n')
        data3=[x.strip() for x in data2 if x != '']
        delimeter='-'
        data4=delimeter.join(data3)
        data5=data4.split('ACADEMIC STAFF-')[1]
        colls=re.findall(colReg,data5)
        eff_colls=[x for x in colls if re.match(filReg,x)]  # a list of all colleges/schools
        grouped_by_colleges={}  # the key is the school/college, value is data in that school/college
        for i in range(len(eff_colls)-1,-1,-1):
            curr_col = eff_colls[i]
            eff_str=data5.split(curr_col)
            data5=eff_str[0]  # these are the remaining colleges not yet processed
            grouped_by_colleges[curr_col]=eff_str[1]
        dep_profs={}  # will contain professors in each department
        for item,val in grouped_by_colleges.items():
            if val[0:5]=='-Name':  # then the school is the department
                all_profs=self.find_all_profs(val)
                all_profs=[x.encode('windows-1252').decode('utf-8') for x in all_profs]
                dep_profs[item]=all_profs
            else:
                deps=re.findall(depReg,val)
                grouped_by_deps={}  # the key is the department, value is data in that department
                for i in range(len(deps)-1,-1,-1):
                    curr_dep=deps[i]
                    eff=val.split(curr_dep)
                    val=eff[0]
                    grouped_by_deps[curr_dep]=eff[1]
                for it2,val2 in grouped_by_deps.items():
                    all_profs=self.find_all_profs(val2)
                    all_profs=[x.encode('windows-1252').decode('utf-8') for x in all_profs]
                    dep_profs[it2]=all_profs
        self.dep_profs=dep_profs
        return dep_profs.keys()

    def find_all_profs(self,val):
        a=re.findall(profReg,val)
        b=re.findall(raReg,val)
        c=re.findall(instReg,val)
        d=re.findall(indrReg,val)
        e=re.findall(lecReg,val)
        all_profs=a+b+c+d+e
        return all_profs  # a list of all professors in a given department

    def prof_data_fetcher(self):
        tables=self.soup.find_all('div',{'id':'icsayfa_sag'})[0]
        alldeps=self.dep_profs.keys()
        alldeps2=[]
        # certain exceptions need to be handled
        for it in alldeps:
            try:
                alldeps2.append(it.split('-')[1])
            except:
                alldeps2.append(it.split('-')[0])
        deps=tables.find_all('h3',{'class':'ms-rteElement-H3B'})
        deps2=[x.text for x in deps for y in alldeps2 if re.match(y,x.text)]  # contains all departments in order
        departments=deps2
        profs_rawdata=tables.find_all('table',{'class':'MsoTableGrid ms-rteTable-6'})
        profs_data={}  # contains profs name as key and a value as a list of words of his publication details
        dep_profs={}  # will contain professors in each department
        for index,item in enumerate(profs_rawdata):
            dep_profs.setdefault(deps2[index],[])
            links=item.find_all('a')
            for link in links:
                templink=link.get('href')
                actlink=mainlink+templink  # merge the relative link to the actual link
                c=urllib2.urlopen(actlink)
                soup=BeautifulSoup(c.read())
                details=soup.find_all('div',{'id':'ctl00_m_g_54fdb314_3665_4555_9b75_a72a3453acf8_ctl00_div_egitim'})
                prof=link.text
                try:
                    prof=prof.split('\n')[1]
                    prof=prof[2:]  # to avoid all spaces
                except:
                    prof=re.match(prof2Reg,prof).group(1)
                prof=prof.encode('windows-1252').decode('utf-8')
                profs_data[prof]=details[0].text
                dep_profs[deps2[index]].append(prof)
        return dep_profs, profs_data


#fetcher=Fetcher('http://www.sehir.edu.tr/en/Pages/Academic/AcademicStaff/Home0710-3235.aspx')
#fetcher.fetch()
#fetcher.prof_data_fetcher():


class App:
    def __init__(self,master):
        master.title('A JCK PRODUCTION')
        frame1=Frame(master)
        frame1.pack()
        frame2=Frame(master)
        frame2.pack(anchor=W)
        frame3=Frame(frame2)
        frame3.pack(side=LEFT)
        frame4=Frame(frame2)
        frame4.pack(padx=20)
        frame5=Frame(frame3)
        frame5.pack(side=LEFT)
        frame6=Frame(frame4)
        frame6.pack(pady=10)
        frame7=Frame(master)
        frame7.pack(anchor=W)
        self.frame3=frame3
        self.frame4=frame4
        self.frame6=frame6
        L1=Label(frame1, text='Guess My Department', bg='blue',fg='White',width=45,font='Veronica 23 bold')
        L1.pack()
        L2=Label(frame1,text='Provide SEHIR Faculty List URL:',font='Times 13 bold')
        L2.pack(anchor=W,padx=15,pady=5)
        self.T1=Text(frame1, width=100, height=1,font='Veronica 11')
        self.T1.pack(anchor=W,padx=18,pady=2)
        s1 = ttk.Style()
        s1.configure('B1.TButton',background='blue',foreground='blue',width=20,highlightthickness='20',
                    font=('Helvetica', 16, 'bold'))
        self.B1=ttk.Button(frame1,text='Fetch Faculty Profiles',style='B1.TButton',
                           command=self.process_update)
        self.B1.pack(anchor=W,padx=16,pady=5)
        self.T2=Text(frame1,width=100,height=6,font='Veronica 11')
        scroll_1=ttk.Scrollbar(frame1,command=self.T2.yview)
        scroll_1.pack(side=RIGHT,fill=Y)
        self.T2.config(yscrollcommand=scroll_1.set)
        self.T2.pack(anchor=W,padx=18,pady=2)
        L3=Label(frame5,text='Choose the\nClassification\nMethod:',font='Times 13 bold',justify=LEFT)
        L3.pack(anchor=W,padx=15,pady=5)
        v=IntVar()
        v.set(1)
        self.rb1=Radiobutton(frame3,text='Naive Bayes.',variable=v,value=1,font='Times 10 bold',
                             command=self.naive_selection)
        self.rb1.pack(pady=5)
        self.rb2=Radiobutton(frame3,text='Fisher           ',variable=v,value=2,font='Times 10 bold',
                             command=self.fisher_selection)
        self.rb2.pack()
        L4= Label(frame5,text='Select a\nProfessor',font='Times 13 bold',justify=LEFT)
        L4.pack(anchor=W,padx=15,pady=5)
        self.combo()
        L5=Label(frame6,text='Set the Thresholds:',font='Times 13 bold')
        L5.pack(anchor=W,padx=19)
        self.lb=Listbox(frame6,width=55,height=5)
        self.lb.pack(side=LEFT,padx=20)
        s2 = ttk.Style()
        s2.configure('B2.TButton',background='red',foreground='red',width=15,highlightthickness='20',
                    font=('Helvetica', 11, 'bold'))
        self.B2=ttk.Button(frame6,text='Remove\nSelected',style='B2.TButton',command=self.remove_option)
        self.B2.pack()
        self.combo2()
        self.T3=Text(frame4,width=5,height=1,font='Veronica 12',fg='darkgreen')
        self.T3.pack(side=LEFT,padx=20)
        s3 = ttk.Style()
        s3.configure('B3.TButton',background='blue',foreground='blue',width=5,highlightthickness='20',
                    font=('Helvetica', 11, 'italic'))
        self.B3=ttk.Button(frame4,text='Set',style='B3.TButton',command=self.set_option)
        self.B3.pack(pady=5)
        L6=Label(frame7,text='\n'*5,fg='white')
        L6.pack()
        s4 = ttk.Style()
        s4.configure('B4.TButton',background='blue',foreground='blue',width=50,highlightthickness='20',
                    font=('Helvetica', 13, 'bold'))
        self.B4=ttk.Button(frame7,text='Guess the Department of the Selected Professor',style='B4.TButton',
                           command=self.guess_the_prof)
        self.B4.pack(padx=17,pady=5)
        L7=Label(frame7,text='Predicted Department:',font='Times 13 bold')
        L7.pack(anchor=W,padx=15,pady=10)
        self.label=Label(frame7,width=40,font='Helvetica 15 bold')
        self.label.pack(anchor=W,padx=15)
        self.process='notdone'
        self.method='naive'

    def combo(self):
        self.box_value=StringVar()
        self.box=ttk.Combobox(self.frame3, textvariable=self.box_value,width=20)
        self.box['values']=('None')
        self.box.current(0)
        self.box.bind("<<ComboboxSelected>>")
        self.box.pack(side=RIGHT,padx=0)

    def combo2(self):
        self.box_value2=StringVar()
        self.box2=ttk.Combobox(self.frame4, textvariable=self.box_value2,width=50)
        self.box2['values']=('None')
        self.box2.current(0)
        self.box2.bind("<<ComboboxSelected>>")
        self.box2.pack(side=LEFT,padx=20)

    def process_update(self):
        inpt=self.T1.get('1.0','end-1c')
        fetcher=Fetcher(inpt)
        status=[' (Pending...)',' (In progress...)',' (Done)']
        self.status=status
        self.T2.insert('1.0','Fetching Department and Professor List'+status[1])
        self.T2.update()
        output_deps=fetcher.fetch()  # These are the output departments
        ind=0
        output_deps2=[x[0]+x.lower()[1:] for x in output_deps]
        self.output_deps2=output_deps2
        self.T2.delete('1.0','2.0')
        self.T2.insert('1.0','Fetching Department and Professor List'+status[2]+'\n')
        for dep in output_deps2:
            self.T2.insert(END,dep+status[0]+'\n')
            ind+=1
        self.T2.update()
        self.t=Timer(5.0,self.status_update)
        self.t.start()
        result_tuple=fetcher.prof_data_fetcher()  # contains dep_profs, profs_data
        self.dep_profs=result_tuple[0]
        departs=self.dep_profs.keys()  # all departments, for setting thresholds
        departments=[x[0]+x.lower()[1:] for x in departs]
        departments.sort()
        self.profs_data=result_tuple[1]
        profs=self.profs_data.keys()
        profs.sort()
        self.box['values']=profs  # updating the first combo box with professors
        self.box.current(len(profs)-1)
        self.box2['values']=departments
        self.box2.current(len(departments)-1)
        self.process='done'
        print 'done'

    def set_option(self):
        thresh=self.box2.get()
        threshnum=self.T3.get('1.0','end-1c')
        self.lb.insert(END, '%s-%s'%(threshnum,thresh))

    def remove_option(self):  # removing items in a listbox
        self.lb.delete(ANCHOR)

    def guess_the_prof(self):
        if self.method=='naive':
            cl=docclass.naivebayes(docclass.getwords)
            prof_sel=self.box.get() # This is the professor whose department we want to guess
            doc_of_prof=self.profs_data[prof_sel]
            self.trainer(prof_sel,cl)
            all_thresh=self.lb.get(0,END)
            thresholds=[]
            for item in all_thresh:
                merged=item.split('-')
                threshnum=float(merged[0])
                thresh=merged[1]
                thresholds.append((thresh,threshnum))
            for thr,num in thresholds:
                cl.setthreshold(thr,num)
            self.pdep= cl.classify(doc_of_prof,default='unknown')
        else:
            cl=docclass.fisherclassifier(docclass.getwords)
            prof_sel=self.box.get() # This is the professor whose department we want to guess
            doc_of_prof=self.profs_data[prof_sel]
            self.trainer(prof_sel,cl)
            all_thresh=self.lb.get(0,END)
            thresholds=[]
            for item in all_thresh:
                merged=item.split('-')
                threshnum=float(merged[0])
                thresh=merged[1]
                thresholds.append((thresh,threshnum))
            for thr,num in thresholds:
                cl.setminimum(thr,num)
            self.pdep= cl.classify(doc_of_prof,default='unknown')
        self.verdict()

    def verdict(self):
        curr_prof=self.box.get()
        depart='unknown'
        for dep in self.dep_profs:
            if curr_prof in self.dep_profs[dep]:
                depart=dep
                break
        print depart
        print self.pdep
        if depart==self.pdep:
            self.label.config(text=depart,bg='green',justify=LEFT)
            self.label.update()
        else:
            self.label.config(text='%s (Correct Answer:%s)'%(self.pdep,depart),bg='red',width=60,justify=LEFT)
            self.label.update()

    def trainer(self,member,cl):
        dep='unknown'
        for prof in self.profs_data:
            if prof is not member:
                for dpt in self.dep_profs:  # professors in each department
                    if prof in self.dep_profs[dpt]:
                        dep = dpt
                        break
                cl.train(self.profs_data[prof],dep)

    def naive_selection(self):
        self.method='naive'

    def fisher_selection(self):
        self.method='fisher'


    def status_update(self):
        status=self.status
        while self.process!= 'done':
            for i in range(len(self.output_deps2)):
                dep=self.output_deps2[i]
                self.T2.delete(str(float(i+2)),str(float(i+3)))
                self.T2.insert(str(float(i+2)),dep+status[1]+'\n')
                self.T2.update()
                time.sleep(5)
                self.T2.delete(str(float(i+2)),str(float(i+3)))
                self.T2.insert(str(float(i+2)),dep+status[2]+'\n')
                time.sleep(5)
                if self.process=='done':
                    self.t.cancel()
                    for i in range(len(self.output_deps2)):
                        dep=self.output_deps2[i]
                        self.T2.delete(str(float(i+2)),str(float(i+3)))
                        self.T2.insert(str(float(i+2)),dep+status[2]+'\n')
                    break












root=Tk()
app=App(root)
root.mainloop()
