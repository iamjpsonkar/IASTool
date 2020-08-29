import PIL,os,sys,traceback,json,cv2,copy,pyautogui,webcolors

from tkinter import *
from tkinter import filedialog as fd
from tkinter.font import Font
from tkinter import messagebox,filedialog,simpledialog
from tkinter.colorchooser import *


from PIL import Image, ImageDraw, ImageGrab,ImageTk,Image

from subprocess import call
import _thread as nth

from time import sleep
from webcolors import *
from builtins import FileExistsError


def get_n2c(s):
    x=name_to_rgb(s)
    kk=(x[0],x[1],x[2])
    return kk


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]




def cnvrtdir(s):
    cfile = ''
    for i in s:
        if i == '\\':
            cfile += '/'
        else:
            cfile += i
    return cfile



def getter(widget, fname):
    x = root.winfo_rootx() + widget.winfo_x()
    y = root.winfo_rooty() + widget.winfo_y()
    x1 = x + widget.winfo_width()
    y1 = y + widget.winfo_height()
    ImageGrab.grab().crop((x, y, x1, y1)).save(fname)


class MainApplication(Frame):
    def __init__(self, parent, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)

        self.add_var()
        self.add_menubar()
        self.add_leftUI()
        self.add_canvas()
        self.add_rightUI()


        root.state('zoomed')
        root.bind('<Motion>', self.zview)
        root.bind("<Control-z>", self.start_zoom)
        self.parent = parent

    def add_var(self):
        self.x =200
        self.curimg = None
        self.curadir = cnvrtdir(str(os.path.dirname(os.path.realpath(__file__))))
        try:
            os.mkdir('output')
        except FileExistsError:
            self.odir = self.curadir + "/output/"
        self.curfdir = None
        self.jsonall = {}
        self.imgfiles = []
        self.ftop = -1
        self.adcord = []
        self.allcp = {}
        self.zv=False
        self.ljfile=''
        self.curjdir=''
        self.cdraw = False
        self.hl=0
        self.editdraw=False
        self.deldraw=False
        self.ptedit=False
        self.indraw1=False
        self.indraw2=False
        self.npp=False
        self.adpx1=-1
        self.adpy1=-1
        self.adpx2=-1
        self.adpy2=-1
        self.delpoly=False
        self.zimg=None
        self.iastf={}
        self.defaulc={}



    def add_menubar(self):
        self.menubar = Menu(root)

        self.filemenu = Menu(self.menubar, tearoff=0)

        self.filemenu.add_command(label="Open Image", command=lambda: self.openi(),accelerator="O")
        root.bind("<o>",self.openi)

        self.filemenu.add_command(label="Open Folder", command=lambda: self.openf(),accelerator="Ctrl+O")
        root.bind("<Control-o>", self.openf)



        self.filemenu.add_command(label="Save JSON", command=lambda: self.saveij(),accelerator="Ctrl+J")
        root.bind("<Control-j>", self.saveij)

        self.filemenu.add_command(label="Save Annotated Image", command=lambda: self.saveia(),accelerator="Ctrl+A")
        root.bind("<Control-a>", self.saveia)

        self.filemenu.add_command(label="Save Segmented Image", command=lambda: self.saveis(),accelerator="Ctrl+S")
        root.bind("<Control-s>", self.saveis)

        self.filemenu.add_command(label="Save all", command=lambda: self.saveiall(),accelerator="S")
        root.bind("<s>", self.saveiall)

        self.menubar.add_cascade(label="File", menu=self.filemenu)



        self.editmenu = Menu(self.menubar, tearoff=0)

        self.editmenu.add_command(label="Clear Image", command=lambda: self.clear_image(),accelerator="Ctrl+Del")
        root.bind("<Control-Delete>", self.clear_image)

        self.editmenu.add_command(label="Edit Point", command=lambda: self.edit_point(),accelerator="Ctrl+E")
        root.bind("<Control-e>", self.edit_point)

        self.editmenu.add_command(label="Insert Point", command=lambda: self.insert_point(),accelerator="Ctrl+I")
        root.bind("<Control-i>", self.insert_point)

        self.editmenu.add_command(label="Delete Point", command=lambda: self.delete_point(),accelerator="Del")
        root.bind("<Delete>", self.delete_point)

        self.editmenu.add_command(label="Delete Polygon", command=lambda: self.delete_polygon(),accelerator="Del+P")
        root.bind("<Delete><p>", self.delete_polygon)

        self.menubar.add_cascade(label="Edit", menu=self.editmenu)



        self.viewmenu = Menu(self.menubar, tearoff=0)

        self.viewmenu.add_command(label="Show Current JSON", command=lambda: self.showcurjson())

        self.viewmenu.add_command(label="Show Editable", command=lambda: self.showeditable(),accelerator="Alt+E")
        root.bind("<Alt-e>", self.showeditable)



        self.viewmenu.add_command(label="Show Full JSON", command=lambda: self.showj(), accelerator="Alt+j")
        root.bind("<Alt-j>", self.showj)

        self.viewmenu.add_command(label="Show Current Annotation", command=lambda: self.showa(),accelerator="Alt+A")
        root.bind("<Alt-a>", self.showa)

        self.viewmenu.add_command(label="Show Current Segmentation", command=lambda: self.shows(),accelerator="Alt+S")
        root.bind("<Alt-s>", self.shows)

        self.viewmenu.add_command(label="Hide/Show Labels", command=lambda: self.hidelb(),accelerator="Alt+L")
        root.bind("<Alt-l>", self.hidelb)

        self.menubar.add_cascade(label="View", menu=self.viewmenu)

        
        root.config(menu=self.menubar)

    def add_canvas(self):
        self.cv = Canvas(root, width=900, height=600, bg='white', bd=0, highlightthickness=0)
        self.cv.place(relx=0.5, rely=0.5, anchor=CENTER)

    def add_leftUI(self):

        self.stdflt = Button(text="-", command=self.set_default, bg='red')
        self.stdflt.place(x=5, y=10, width=20, height=20)
        self.caction = Label(root, text="Default State", width=15, bg="white", bd=3, relief="solid")
        self.caction.place(x=30, y=10)
        locx = 40
        self.nbtn = Button(text="Next Image", command=self.nextimg)
        self.nbtn.place(x=20, y=locx, width=120, height=25)
        locx+=40

        self.pbtn = Button(text="Previous Image", command=self.previmg)
        self.pbtn.place(x=20, y=locx, width=120, height=25)
        locx+=40

        self.cpbtn = Button(text="Create Polygon", command=self.create_poly)
        self.cpbtn.place(x=20, y=locx, width=120, height=25)
        locx += 40

        self.labz = Label(root, text="Transparency")
        self.labz.place(x=20, y=locx)
        locx += 20

        self.w = Scale(root, from_=0, to=255, orient=HORIZONTAL, command=lambda value: self.shows())
        self.w.set(205)
        self.w.place(x=20, y=locx)
        locx += 80

        

    def add_rightUI(self):
        self.LB1t = Label(root, text="Zoom View (Ctrl+z)")
        self.LB1t.place(x=1205, y=5)
        self.zcv = Canvas(root, width=200, height=200, bg='white', bd=3, relief="solid")
        self.zcv.place(x=1150, y=25)
        self.LB1t=Label(root,text="Current IAST data")
        self.LB1t.place(x=1205, y=245)
        self.Lb1 = Listbox(root,width=30,bd=3,relief="solid")
        x = Scrollbar(self.Lb1, orient="vertical")
        self.Lb1.config(yscrollcommand=x.set)
        x.config(command=self.Lb1.yview)
        self.Lb1.place(x=1160, y=270)

    def show_current_DPIT(self):
        self.Lb1.delete(0, END)

        val=1
        for d in self.defaulc:
            ss="  "+str(d)+"   :  "+str(self.defaulc[d][1])
            self.Lb1.insert(val,ss)
            val+=1
            ss = "------------------------------------------"
            self.Lb1.insert(val, ss)
            val += 1
        self.Lb1.update()

    def set_default(self):
        k=0
        self.adcord = []
        self.cdraw = False
        self.hl = 0
        self.editdraw = False
        self.deldraw = False
        self.ptedit = False
        self.indraw1 = False
        self.indraw2 = False
        self.npp = False
        self.adpx1 = -1
        self.adpy1 = -1
        self.adpx2 = -1
        self.adpy2 = -1
        self.delpoly = False
        self.zimg = None
        self.zv=False
        self.caction.config(text="Default State")
        self.cpbtn.config(text="Create Polygon")



    def start_zoom(self,_event=None):
        if self.zv==True:
            self.zv=False
        else:
            self.zv=True


    def previmg(self, _event=None):
        if self.ftop != -1:
            self.jsonall[self.curimg] = copy.deepcopy(self.allcp)
            if self.ftop == 0:
                self.ftop = len(self.imgfiles) - 1
            else:
                self.ftop -= 1
            self.curimg = self.imgfiles[self.ftop]
            if self.curimg in self.jsonall:
                self.allcp = copy.deepcopy(self.jsonall[self.curimg])
                self.adcord = []
            else:
                self.allcp = {}
                self.adcord = []
            self.load_default()
            self.display_image()

    def nextimg(self, _event=None):
        if self.ftop != -1:
            self.jsonall[self.curimg] = copy.deepcopy(self.allcp)
            if self.ftop == len(self.imgfiles) - 1:
                self.ftop = 0
            else:
                self.ftop += 1
            self.curimg = copy.deepcopy(self.imgfiles[self.ftop])
            self.adcord = []
            self.load_default()
            self.display_image()

    def create_1(self):
        messagebox.showinfo("Current Status"," We are Currently working on this feature.")

    def create_poly(self, _event=None):
        if self.curimg!=None:
            if self.cdraw==True:
                self.caction.config(text='Default State')
                self.cpbtn.config(text="Create Polygon")
                self.cdraw=False
                #self.zv=False
            else:
                if self.curimg not in self.jsonall:
                    self.jsonall[self.curimg]={}
                self.jsonall[self.curimg]=copy.deepcopy(self.allcp)
                self.set_default()

                self.caction.config(text='Create Polygon')
                self.cpbtn.config(text="Done")
                #self.zv=True
                self.cdraw=True

    def openj(self, _event=None):
        fdir = filedialog.askopenfilename(title="Select file", filetypes=(
            ("JSON files", "*.json"), ("all files", "*.*")))
        if fdir != '':
            k = fdir.rfind('/')
            self.curjdir = fdir[0:k]
            self.ljfile = fdir[k + 1:]


            #print("openj")
            self.load_j()
        else:
            return

    def openi(self, _event=None):
        self.adcord = []
        self.allcp = {}
        self.cdraw = False
        fdir = filedialog.askopenfilename(title="Select file", filetypes=(
            ("Image files", "*.png *.jpg *.jpeg *.PNG *.JPG *.JPEG"), ("all files", "*.*")))
        if fdir != '':
            k = fdir.rfind('/')
            self.curfdir = fdir[0:k]
            self.curimg = fdir[k + 1:]
            self.ftop = -1
            self.display_image()
            self.load_default()
            #print("openi")
        else:
            return
    

    def openf(self, _event=None):
        self.adcord = []
        self.allcp = {}
        self.cdraw = False
        dir = filedialog.askdirectory()
        if dir != '' or dir != None:
            self.curfdir = dir
            self.imgfiles = []
            for file in os.listdir(self.curfdir):
                if file.endswith(".jpeg") or file.endswith(".jpg") or file.endswith(".png") or file.endswith(
                        ".JPEG") or file.endswith(".JPG") or file.endswith(".PNG"):
                    self.imgfiles.append(file)
            self.ftop = 0
            self.curimg = self.imgfiles[self.ftop]
            self.display_image()
        #print("openf")

    def saveij(self,_event=None):
        jfname=None
        while jfname==None:
            jfname = simpledialog.askstring("Input", "Please Enter a name for JSON file?", parent=root)
        djson = {}
        for d in self.jsonall:
            # print("d===", d)
            if d!='default':
                if d not in djson:
                    djson[d] = {}
                for d1 in self.jsonall[d]:
                    # print("d1===", d1)
                    for k in range(len(self.jsonall[d][d1][0])):
                        d3 = {}
                        # print(self.jsonall[d][d1][1][0])
                        d3['color'] = self.jsonall[d][d1][1]
                        d3['x-value'] = []
                        d3['y-value'] = []
                        for i in range(0, len(self.jsonall[d][d1][0][k]), 2):
                            d3['x-value'].append(self.jsonall[d][d1][0][k][i])
                            d3['y-value'].append(self.jsonall[d][d1][0][k][i + 1])
                        djson[d]['{}-{}'.format(d1, k)] = d3
        with open("{}/{}.json".format(self.odir,jfname), "w") as write_file:
            json.dump(djson, write_file)



    def saveia(self, _event=None):
        if self.curimg != None:
            self.showa()
            getter(self.cv, self.odir + "Annotated_" + self.curimg)

        #print("saveia")

    def saveis(self, _event=None):
        if self.curimg != None:
            self.shows()
            getter(self.cv, self.odir + "Segmented_" + self.curimg)
        #print("saveis")

    def saveiall(self, _event=None):
        self.saveia()
        self.saveis()
        self.saveij()



    def cline(self,_event=None):
        self.crline=True
        k=0



    def clean_image(self,_event=None):
        self.display_image()

    def clear_image(self,_event=None):
        self.adcord = []
        self.allcp = {}
        self.cdraw = False
        self.display_image()

    def edit_point(self,_event=None):
        if self.curimg!=None:
            self.showeditable()
            if self.caction['text'] == 'Edit Point':
                self.caction.config(text='Default State')
                self.editdraw=False
                #self.zv=False
            else:
                self.caction.config(text='Edit Point')
                self.set_default()
                self.editdraw=True
                #self.zv=True

    def insert_point(self, _event=None):
        if self.curimg!=None:
            self.showeditable()
            if self.indraw1==False:
                self.caction.config(text="Insert Points")
                self.indraw1=True
            else:
                self.caction.config(text="Default State")
                self.indraw1=False



    def delete_point(self,_event=None):
        if self.curimg!=None:
            self.showeditable()
            if self.deldraw==False:
                self.caction.config(text="Delete Point")
                self.deldraw=True
            else:
                self.caction.config(text="Default State")
                self.deldraw=False

    def del_point(self,x,y,_event=None):
        fp = 0
        for pn in self.allcp:
            for k in range(len(self.allcp[pn][0])):
                for p in range(0, len(self.allcp[pn][0][k]), 2):
                    if -3 < self.allcp[pn][0][k][p] - x < 3 and -3 < self.allcp[pn][0][k][p + 1] - y < 3:
                        self.pn = pn
                        self.pk = k
                        self.pp = p
                        fp = 1
                        break
        if fp == 1:

            del self.allcp[self.pn][0][self.pk][self.pp]
            del self.allcp[self.pn][0][self.pk][self.pp]
            self.showeditable()




    def showeditable(self,_event=None):
        self.clean_image()
        r=4
        for pname in self.allcp:
            for i in self.allcp[pname][0]:
                self.cv.create_polygon(i, outline='black', fill='', width=2)
                for j in range(0,len(i),2):
                    x=i[j]
                    y=i[j+1]
                    self.cv.create_oval(x - r, y - r, x + r, y + r, fill="red")
        self.cv.update()

    def hidelb(self,_event=None):
        if self.curimg!=None:
            if self.hl==1:
                for d in self.allcp:
                    for j in self.allcp[d][0]:
                        self.cv.create_text(j[0], j[1] - 15, fill='red', font="25", text=d)
                        self.cv.update()
                self.hl=0
            else:
                self.showeditable()
                self.hl=1



    def current_polygon_fill(self,x,_event=None):
        self.cv.delete("all")
        x=self.w.get()

        self.clean_image()



        for pname in self.allcp:
            poly = PIL.Image.new('RGBA', (self.iw, self.ih))
            pdraw = PIL.ImageDraw.Draw(poly)
            clr = get_n2c(self.allcp[pname][1])
            for i in self.allcp[pname][0]:
                pdraw.polygon(i, fill=(clr[0],clr[1],clr[2],x), outline=(clr[0],clr[1],clr[2],x))

            self.pimg.paste(poly, mask=poly)

            self.img = ImageTk.PhotoImage(self.pimg)
            # self.cv = Canvas(self.cv, width=iw,height=ih, bg='white')
            self.cv.config(width=self.iw, height=self.ih)
            self.cv.pack()

            self.cv.create_image(0, 0, image=self.img, anchor='nw')

            self.cv.pack()
            self.cv.place(relx=0.5, rely=0.5, anchor=CENTER)


    def showj(self,_event=None):
        djson={}
        for d in self.jsonall:
            #print("d===", d)
            if 0<1:
                if d not in djson:
                    djson[d]={}
                for d1 in self.jsonall[d]:
                    #print("d1===", d1)
                    for k in range(len(self.jsonall[d][d1][0])):
                        d3={}
                        #print(self.jsonall[d][d1][1][0])
                        d3['color']=self.jsonall[d][d1][1]
                        d3['x-value']=[]
                        d3['y-value']=[]
                        for i in range(0,len(self.jsonall[d][d1][0][k]),2):
                            d3['x-value'].append(self.jsonall[d][d1][0][k][i])
                            d3['y-value'].append(self.jsonall[d][d1][0][k][i+1])
                        djson[d]['{}-{}'.format(d1,k)]=d3
        messagebox.showinfo("Json File Data",json.dumps(djson))
            #print(json.dumps(djson))

    def showa(self,_event=None):
        self.clean_image()

        for pname in self.allcp:
            #print(self.allcp[pname])
            for i in self.allcp[pname][0]:
                self.cv.create_polygon(i, outline=self.allcp[pname][1],fill='',width=2)

    def shows(self,_event=None):

        self.cv.delete("all")
        self.clean_image()
        x=self.w.get()
        for pname in self.allcp:
            poly = PIL.Image.new('RGBA', (self.iw, self.ih))
            pdraw = PIL.ImageDraw.Draw(poly)
            clr=get_n2c(self.allcp[pname][1])
            for i in self.allcp[pname][0]:
                pdraw.polygon(i, fill=(clr[0],clr[1],clr[2],x), outline=(clr[0],clr[1],clr[2],x))

            self.pimg.paste(poly, mask=poly)

            self.img = ImageTk.PhotoImage(self.pimg)
            # self.cv = Canvas(self.cv, width=iw,height=ih, bg='white')
            self.cv.config(width=self.iw, height=self.ih)
            self.cv.pack()

            self.cv.create_image(0, 0, image=self.img, anchor='nw')

            self.cv.pack()
            self.cv.place(relx=0.5, rely=0.5, anchor=CENTER)

    def display_image(self,_event=None):
        if self.curimg!=None and self.curfdir!=None and self.curadir!=None:
            os.chdir(self.curfdir)

            imgd = PIL.Image.open(self.curimg)
            imgd = imgd.convert("RGBA")
            self.iw=0
            self.ih=0

            #print(imgd.size)
            if imgd.size[0] > imgd.size[1]:

                self.iw = 900
                wpercent = (self.iw / float(imgd.size[0]))
                self.ih = int((float(imgd.size[1]) * float(wpercent)))
                imgd = imgd.resize((self.iw, self.ih), PIL.Image.ANTIALIAS)
            else:

                self.ih = 600
                wpercent = (self.ih / float(imgd.size[1]))
                self.iw = int((float(imgd.size[0]) * float(wpercent)))
                imgd = imgd.resize((self.ih, self.iw), PIL.Image.ANTIALIAS)

            self.pimg=imgd
            self.img = ImageTk.PhotoImage(imgd)

            self.cv.config(width=self.iw,height=self.ih)
            self.cv.pack()
            self.imdraw = ImageDraw.Draw(self.pimg)

            self.cv.bind('<1>', self.getorigin)
            # self.imgcan=Canvas(self.cv,width=int(self.img.width()/900)*100, height=int(self.img.height()/600)*100, bg='white')

            self.cv.create_image(0, 0, image=self.img, anchor='nw')

            self.cv.pack()
            self.cv.place(relx=0.5, rely=0.5, anchor=CENTER)


            os.chdir(self.curadir)



    def getorigin(self, eventorigin):


        if self.cdraw:
            x0 = eventorigin.x
            y0 = eventorigin.y
            #print("cdraw= ",self.cdraw)
            self.add_point(x0, y0)
        elif self.editdraw:
            ex=eventorigin.x
            ey= eventorigin.y
            self.editp(ex,ey)
        elif self.ptedit:
            ex=eventorigin.x
            ey= eventorigin.y
            self.ptp(ex,ey)

        elif self.deldraw:
            ex=eventorigin.x
            ey= eventorigin.y
            self.del_point(ex,ey)

        elif self.indraw1:
            self.adpx1 = eventorigin.x
            self.adpy1 = eventorigin.y
            fp=0
            for pn in self.allcp:
                for k in range(len(self.allcp[pn][0])):
                    for p in range(0, len(self.allcp[pn][0][k]), 2):
                        if -3 < self.allcp[pn][0][k][p] - self.adpx1 < 3 and -3 < self.allcp[pn][0][k][p + 1] - self.adpy1 < 3:
                            fp=1
                            break


            if fp==1:
                messagebox.showinfo("point start ", "{}   {}".format(self.adpx1,self.adpy1))
                self.indraw2=True
                self.indraw1=False




        elif self.indraw2:
            self.adpx2 = eventorigin.x
            self.adpy2 = eventorigin.y
            fp = 0
            for pn in self.allcp:
                for k in range(len(self.allcp[pn][0])):
                    for p in range(0, len(self.allcp[pn][0][k]), 2):
                        if -3 < self.allcp[pn][0][k][p] - self.adpx2 < 3 and -3 < self.allcp[pn][0][k][p + 1] - self.adpy2 < 3:
                            fp = 1
                            break
            if fp==1:
                self.indraw2=False
                messagebox.showinfo("point end ", "{}   {}".format(self.adpx2, self.adpy2))
                self.inp_p(self.adpx1,self.adpy1,self.adpx2,self.adpy2)

        elif self.npp:
            ex=eventorigin.x
            ey= eventorigin.y
            self.cr_np(ex,ey)
            self.indraw1=True

        elif self.delpoly:
            ex = eventorigin.x
            ey = eventorigin.y
            self.del_poly(ex, ey)



    def add_point(self, clickx, clicky,_event=None):
        r = 4
        if len(self.adcord) > 0:
            a = self.adcord[0]
            b = self.adcord[1]
            xd = a - clickx
            yd = b - clicky
            if -3 < xd < 3 and -3 < yd < 3:
                ox = self.adcord[-2]
                oy = self.adcord[-1]
                self.cv.create_line(ox, oy, a, b)
                self.adcord.append(a)
                self.adcord.append(b)
                pname = simpledialog.askstring("Input", "Please Enter the name of this Label?", parent=root)
                #print(self.adcord)
                pcolor=None
                if pname != None:
                    if pname not in self.allcp:
                        while pcolor==None:
                            pcolor = self.getcolor()
                            self.allcp[pname] = [[], '']
                            self.defaulc[pname]=[[],closest_colour(pcolor[0])]
                            self.show_current_DPIT()
                            self.allcp[pname][0].append(self.adcord)
                            self.allcp[pname][1] = closest_colour(pcolor[0])
                            self.cv.create_text(self.adcord[0],self.adcord[1]-15,fill='red',font="25",text=pname)
                            self.cv.update()
                            self.adcord = []
                    else:
                        self.allcp[pname][0].append(self.adcord)
                        #print("===>> ",self.allcp)
                        self.adcord = []
                        messagebox.showinfo("Label", "{}".format(pname))
                        return
            else:
                ox = self.adcord[-2]
                oy = self.adcord[-1]
                self.adcord.append(clickx)
                self.adcord.append(clicky)

                self.cv.create_oval(clickx - r, clicky - r, clickx + r, clicky + r, fill="red")

                self.cv.create_line(ox, oy, clickx, clicky)

        else:
            self.adcord.append(clickx)
            self.adcord.append(clicky)
            self.cv.create_oval(clickx - r, clicky - r, clickx + r, clicky + r, fill="green")

    def add_point1(self, clickx, clicky,_event=None):
        r = 4
        if len(self.adcord) > 0:
            for i in range(0, len(self.adcord), 2):
                a = self.adcord[i]
                b = self.adcord[i + 1]
                xd = a - clickx
                yd = b - clicky
                if -3 < xd < 3 and -3 < yd < 3:
                    ox = self.adcord[-2]
                    oy = self.adcord[-1]
                    self.cv.create_line(ox, oy, a, b)
                    self.adcord.append(a)
                    self.adcord.append(b)
                    pname = simpledialog.askstring("Input", "Please Enter the name of this Label?", parent=root)
                    pcolor=None
                    if pname != None:
                        if pname not in self.allcp:
                            while pcolor==None:
                                pcolor = self.getcolor()
                            self.allcp[pname] = [[], '']
                            self.allcp[pname][0].append(self.adcord)
                            self.allcp[pname][1] = pcolor
                            self.cv.create_text(self.adcord[0],self.adcord[1]-15,fill='red',font="25",text=pname)
                            self.cv.update()
                        else:
                            self.allcp[pname][0].append(self.adcord)
                        #print(self.adcord)
                        self.adcord = []
                        messagebox.showinfo("Label", "{}".format(pname))
                        #print(self.allcp)
                    else:
                        pass

                    break
            if len(self.adcord)>0:
                ox = self.adcord[-2]
                oy = self.adcord[-1]
                self.adcord.append(clickx)
                self.adcord.append(clicky)

                self.cv.create_oval(clickx - r, clicky - r, clickx + r, clicky + r, fill="red")

                self.cv.create_line(ox, oy, clickx, clicky)
        else:
            self.adcord.append(clickx)
            self.adcord.append(clicky)
            self.cv.create_oval(clickx - r, clicky - r, clickx + r, clicky + r, fill="red")

    def editp(self,x,y,_event=None):
        fp=0
        for pn in self.allcp:
            for k in range(len(self.allcp[pn][0])):
                for p in range(0,len(self.allcp[pn][0][k]),2):
                    if -3<self.allcp[pn][0][k][p]-x<3 and -3<self.allcp[pn][0][k][p+1]-y<3:
                        self.pn=pn
                        self.pk=k
                        self.pp=p
                        fp=1
                        break
        if fp==1:
            self.clean_image()
            #px=self.allcp[self.pn][0][self.pk][self.pp]
            #py=self.allcp[self.pn][0][self.pk][self.pp+1]
            px,py=0,1
            for i in range(0,len(self.allcp[self.pn][0][self.pk]),2):
                if px==self.pp:
                    px = i
                    py = i + 1
                elif i==self.pp:
                    self.cv.create_oval(self.allcp[self.pn][0][self.pk][px] - r,
                                        self.allcp[self.pn][0][self.pk][py] - r,
                                        self.allcp[self.pn][0][self.pk][px] + r,
                                        self.allcp[self.pn][0][self.pk][py] + r, fill="red")
                    px = i
                    py = i + 1


                else:
                    r=4
                    self.cv.create_line(self.allcp[self.pn][0][self.pk][px],self.allcp[self.pn][0][self.pk][py],self.allcp[self.pn][0][self.pk][i],self.allcp[self.pn][0][self.pk][i+1],width=2)
                    self.cv.create_oval(self.allcp[self.pn][0][self.pk][px] - r, self.allcp[self.pn][0][self.pk][py] - r, self.allcp[self.pn][0][self.pk][px]+ r, self.allcp[self.pn][0][self.pk][py] + r, fill="red")
                    px=i
                    py=i+1
            self.cv.update()
            self.ptedit=True
            self.editdraw=False

    def ptp(self,x,y,_event=None):
        self.allcp[self.pn][0][self.pk][self.pp]=x
        self.allcp[self.pn][0][self.pk][self.pp+1]=y
        self.showeditable()
        self.ptedit=False
        self.editdraw=True




    def inp_p(self,x1,y1,x2,y2):
        fp = 0
        for pn in self.allcp:
            for k in range(len(self.allcp[pn][0])):
                for p in range(0, len(self.allcp[pn][0][k]), 2):
                    cpx=self.allcp[pn][0][k][p]
                    cpy=self.allcp[pn][0][k][p+1]
                    if p==len(self.allcp[pn][0][k])-2:
                        npx=self.allcp[pn][0][k][0]
                        npy=self.allcp[pn][0][k][1]
                    else:
                        npx = self.allcp[pn][0][k][p+2]
                        npy = self.allcp[pn][0][k][p+3]
                    if -3 < cpx - x1 < 3 and -3 < cpy - y1 < 3 and -3 < npx - x2 < 3 and -3 < npy - y2 < 3:
                        self.pn = pn
                        self.pk = k
                        self.pp = p
                        fp = 1
                        self.npp=True
                        #self.zv=True
                        break
                    elif -3 < cpx - x2 < 3 and -3 < cpy - y2 < 3 and -3 < npx - x1 < 3 and -3 < npy - y1 < 3:
                        self.pn = pn
                        self.pk = k
                        self.pp = p
                        fp = 1
                        self.npp=True
                        #self.zv=True
                        break


    def cr_np(self,x,y,_event=None):
        self.allcp[self.pn][0][self.pk].insert(self.pp+2,x)
        self.allcp[self.pn][0][self.pk].insert(self.pp+3,y)
        self.npp=False
        #self.zv=False
        self.showeditable()




    def del_point(self,x,y,_event=None):
        fp = 0
        for pn in self.allcp:
            for k in range(len(self.allcp[pn][0])):
                for p in range(0, len(self.allcp[pn][0][k]), 2):
                    if -3 < self.allcp[pn][0][k][p] - x < 3 and -3 < self.allcp[pn][0][k][p + 1] - y < 3:
                        self.pn = pn
                        self.pk = k
                        self.pp = p
                        fp = 1
                        break
        if fp == 1:
            #print(self.allcp[self.pn][0][self.pk])
            del self.allcp[self.pn][0][self.pk][self.pp]
            del self.allcp[self.pn][0][self.pk][self.pp]
            #print(self.allcp[self.pn][0][self.pk])
            self.showeditable()

        else:
            self.delete_point()


    def zview(self,event=None):
        if self.zv:
            #self.zcv.delete("all")
            v=24
            cx, cy = pyautogui.position()
            r=4
            x = cx-v
            y = cy-v
            x1 = cx+v
            y1 = cy+v
            self.zimg = ImageGrab.grab().crop((x, y, x1, y1))
            self.zimg=self.zimg.resize((200,200))
            self.zimg = ImageTk.PhotoImage(self.zimg)
            self.zcv.create_image(105, 105, image=self.zimg, anchor='center')
            self.zcv.create_oval(100 - r, 100 - r, 100 + r, 100 + r,width=2)

            self.zcv.update()
        else:
            self.zcv.delete("all")
            self.zcv.update()



    def delete_polygon(self,_event=None):
        if self.curimg!=None:
            self.showeditable()
            if self.delpoly==False:
                self.caction.config(text="Delete Polygon")
                self.delpoly=True
            else:
                self.caction.config(text="Default State")
                self.delpoly=False


    def del_poly(self,x,y,_event=None):
        fp = 0
        for pn in self.allcp:
            for k in range(len(self.allcp[pn][0])):
                for p in range(0, len(self.allcp[pn][0][k]), 2):
                    if -3 < self.allcp[pn][0][k][p] - x < 3 and -3 < self.allcp[pn][0][k][p + 1] - y < 3:
                        self.pn = pn
                        self.pk = k
                        self.pp = p
                        fp = 1
                        break
        if fp==1:
            del self.allcp[self.pn][0][self.pk]
            self.showeditable()



    def getcolor(self,_event=None):
        color = askcolor()
        return color



    def load_j(self):
        os.chdir(self.curjdir)
        with open(self.ljfile, "r") as read_file:
            data = json.load(read_file)
        #print(data)
        for d in data:
            #print(d)
            allcp={}
            for d1 in data[d]:
                lname=d1[0:d1.rfind('-')]
                if lname not in allcp:
                    allcp[lname]=[[],data[d][d1]['color']]


                ar=[]
                for i in range(len(data[d][d1]['x-value'])):
                    ar.append(data[d][d1]['x-value'][i])
                    ar.append(data[d][d1]['y-value'][i])
                allcp[lname][0].append(ar)
            if d not in self.jsonall:
                self.jsonall[d]={}

            self.jsonall[d]=allcp
            #print(allcp)
        if self.curimg in self.jsonall:
            self.allcp=self.jsonall[self.curimg]
            self.adcord=[]

        os.chdir(self.curadir)

    def create_IAST(self):


        label='NA'

        while label !='done':
            label = simpledialog.askstring("Input", "Please Enter the name of Label?", parent=root)
            if label!='done':
                color=closest_colour(askcolor()[0])
                if label not in self.iastf:
                    self.iastf[label] = ''
                self.iastf[label] = color

        dfname = simpledialog.askstring("Input", "Please Enter a name for DPIT file?", parent=root)
        with open("{}/{}_{}.json".format(self.odir,"DPIT", dfname), "w") as write_file:
            json.dump(self.iastf, write_file)

    def load_IAST(self,_event=None):
        fdir = filedialog.askopenfilename(title="Select file", filetypes=(
            ("DPIT files", "DPIT_*.json"), ("all files", "*.*")))
        if fdir != '':
            k = fdir.rfind('/')
            dpitdir = fdir[0:k]
            dpitfile = fdir[k + 1:]
            os.chdir(dpitdir)
            with open(dpitfile, "r") as read_file:
                data = json.load(read_file)
            allcp={}
            for d in data:
                allcp[d]=data[d]
            #print(allcp)

            for d in allcp:
                if d not in self.defaulc:
                    self.defaulc[d]=[[],'']
                self.defaulc[d][1]=allcp[d]
            #print("==>",self.defaulc)
        self.load_default()

        os.chdir(self.curadir)

    def load_default(self):
        for d in self.defaulc:
            if d not in self.allcp:
                self.allcp[d]=copy.deepcopy([[],self.defaulc[d][1]])
        self.show_current_DPIT()





    def showallcp(self):
        messagebox.showinfo("ALLCP Data",self.allcp)
        messagebox.showinfo("Defaulc Data", self.defaulc)


    def showcurjson(self):
        djson = {}
        d=self.curimg
        if d in self.jsonall:
            if d not in djson:
                djson[d] = {}
            for d1 in self.jsonall[d]:
                for k in range(len(self.jsonall[d][d1][0])):
                    d3 = {}
                    d3['color'] = self.jsonall[d][d1][1]
                    d3['x-value'] = []
                    d3['y-value'] = []
                    for i in range(0, len(self.jsonall[d][d1][0][k]), 2):
                        d3['x-value'].append(self.jsonall[d][d1][0][k][i])
                        d3['y-value'].append(self.jsonall[d][d1][0][k][i + 1])
                        djson[d]['{}-{}'.format(d1, k)] = d3
            messagebox.showinfo("Json File Data", json.dumps(djson))
            result = messagebox.askquestion("Save", "Do you want to save this json file?", icon='warning')
            if result == 'yes':
                jfname = None
                while jfname == None:
                    jfname = simpledialog.askstring("Input", "Please Enter a name for JSON file?", parent=root)

                with open("{}/{}.json".format(self.odir, jfname), "w") as write_file:
                    json.dump(djson, write_file)
            else:
                print("I'm Not Deleted Yet")
        else:
            messagebox.showinfo("Json File Data", "Sorry NO JSON find for this Image")


if __name__ == "__main__":
    root = Tk()
    root.title("IAStool  ~ Image Annotation & Segmentation Tool")
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
