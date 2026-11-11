import os
import sys

# Prisilni importi na samom vrhu kako bi ih PyInstaller obavezno ugradio u .exe
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import configparser
from PIL import Image, ImageTk

try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except Exception:
    pass

try:
    import pytesseract
except Exception:
    pytesseract = None

# Strogo definiranje putanje za Portable način rada (.ini ide uz EXE)
if getattr(sys, 'frozen', False):
    PROGRAM_DIR = os.path.dirname(sys.executable)
else:
    PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

INI_PATH = os.path.join(PROGRAM_DIR, "postavke.ini")

FORMATE_PAPIRA = {
    "A0": (2384, 3370), "A1": (1684, 2384), "A2": (1191, 1684),
    "A3": (842, 1191),  "A4": (595, 842),   "A5": (420, 595),
    "Letter (US)": (612, 792), "Legal (US)": (612, 1008), "Ledger/Tabloid (US)": (792, 1224)
}

class PremiumPDFStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium PDF Book Studio v3.0 (Portable)")
        self.root.geometry("780x580")
        self.root.configure(bg="#0F172A") # Izrazito tamna moderna tema
        self.root.resizable(False, False)
        
        # Varijable
        self.odabrane_datoteke_lista = []
        self.izlazni_pdf_putanja = tk.StringVar()
        self.odabrani_format = tk.StringVar(value="A4")
        self.kvaliteta_kompresije = tk.IntVar(value=75)
        self.ocr_ukljucen = tk.BooleanVar(value=False)
        self.trenutni_status = tk.StringVar(value="Sustav spreman. Učitajte skenove.")
        
        self.ucitaj_postavke()
        self.kreiraj_sucelje()

    def ucitaj_postavke(self):
        if os.path.exists(INI_PATH):
            try:
                config = configparser.ConfigParser()
                config.read(INI_PATH, encoding='utf-8')
                if 'Postavke' in config:
                    sekcija = config['Postavke']
                    self.odabrani_format.set(sekcija.get('FormatPapira', 'A4'))
                    self.kvaliteta_kompresije.set(sekcija.getint('KvalitetaKompresije', 75))
                    self.ocr_ukljucen.set(sekcija.getboolean('OcrUkljucen', False))
            except Exception:
                pass

    def spremi_postavke(self):
        try:
            config = configparser.ConfigParser()
            config['Postavke'] = {
                'FormatPapira': self.odabrani_format.get(),
                'KvalitetaKompresije': str(self.kvaliteta_kompresije.get()),
                'OcrUkljucen': str(self.ocr_ukljucen.get())
            }
            with open(INI_PATH, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
        except Exception:
            pass

    def kreiraj_sucelje(self):
        BG_MAIN = "#0F172A"
        BG_PANEL = "#1E293B"
        TEXT_CYAN = "#38BDF8"
        TEXT_WHITE = "#F8FAFC"
        BTN_ACCENT = "#0284C7"
        BTN_GREEN = "#10B981"
        
        stil = ttk.Style()
        stil.theme_use('default')
        stil.configure("TProgressbar", thickness=15, troughcolor=BG_PANEL, background=TEXT_CYAN)

        tk.Label(self.root, text="📚 Premium PDF Book Studio v3.0", font=("Segoe UI", 18, "bold"), bg=BG_MAIN, fg=TEXT_CYAN).pack(pady=(15, 5))
        
        glavni_okvir = tk.Frame(self.root, bg=BG_MAIN)
        glavni_okvir.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        lijeva_strana = tk.Frame(glavni_okvir, bg=BG_MAIN, width=380)
        lijeva_strana.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        okvir_unos = tk.LabelFrame(lijeva_strana, text=" 1. Izvor skeniranih stranica ", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_CYAN, bd=1, relief=tk.SOLID, padx=10, pady=10)
        okvir_unos.pack(fill=tk.X, pady=5)
        
        tk.Button(okvir_unos, text="📁 Učitaj cijelu mapu", command=self.dodaj_mapu, font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, activebackground=BTN_ACCENT, activeforeground=TEXT_WHITE).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(okvir_unos, text="🖼️ Odaberi datoteke", command=self.dodaj_datoteke, font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, activebackground=BTN_ACCENT, activeforeground=TEXT_WHITE).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        okvir_izlaz = tk.LabelFrame(lijeva_strana, text=" 2. Odredište knjige (.pdf) ", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_CYAN, bd=1, relief=tk.SOLID, padx=10, pady=10)
        okvir_izlaz.pack(fill=tk.X, pady=5)
        
        tk.Entry(okvir_izlaz, textvariable=self.izlazni_pdf_putanja, font=("Segoe UI", 10), bg=BG_PANEL, fg=TEXT_WHITE, bd=1, relief=tk.SOLID, insertbackground=TEXT_WHITE).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=3)
        tk.Button(okvir_izlaz, text="Spremi kao...", command=self.definiraj_izlaz, font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, activebackground=BTN_ACCENT).pack(side=tk.RIGHT)
        
        okvir_postavke = tk.LabelFrame(lijeva_strana, text=" 3. Studijske Postavke i Optimizacija ", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_CYAN, bd=1, relief=tk.SOLID, padx=15, pady=15)
        okvir_postavke.pack(fill=tk.X, pady=5)
        
        tk.Label(okvir_postavke, text="Format papira:", bg=BG_MAIN, fg=TEXT_WHITE).grid(row=0, column=0, sticky=tk.W, pady=2)
        om = tk.OptionMenu(okvir_postavke, self.odabrani_format, *list(FORMATE_PAPIRA.keys()))
        om.config(font=("Segoe UI", 9, "bold"), bg=BG_PANEL, fg=TEXT_WHITE, bd=0, highlightthickness=0, activebackground=BTN_ACCENT)
        om["menu"].config(bg=BG_PANEL, fg=TEXT_WHITE)
        om.grid(row=1, column=0, sticky=tk.W, pady=5)
        
        tk.Label(okvir_postavke, text="Kvaliteta / Kompresija:", bg=BG_MAIN, fg=TEXT_WHITE).grid(row=0, column=1, sticky=tk.W, padx=20)
        self.lbl_kvaliteta = tk.Label(okvir_postavke, text=f"{self.kvaliteta_kompresije.get()}%", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_CYAN)
        self.lbl_kvaliteta.grid(row=0, column=1, sticky=tk.E)
        
        klizac = tk.Scale(okvir_postavke, from_=1, to=100, variable=self.kvaliteta_kompresije, orient=tk.HORIZONTAL, length=150, showvalue=False, bg=BG_MAIN, fg=TEXT_WHITE, highlightthickness=0, troughcolor=BG_PANEL, command=self.osvjezi_slider)
        klizac.grid(row=1, column=1, padx=20, pady=5)
        
        tk.Label(okvir_postavke, text="OCR prepoznavanje teksta:", bg=BG_MAIN, fg=TEXT_WHITE).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(10, 2))
        tk.Checkbutton(okvir_postavke, text="Ugradi pretraživi tekstualni sloj (OCR)", variable=self.ocr_ukljucen, bg=BG_MAIN, fg=TEXT_WHITE, selectcolor=BG_MAIN, activebackground=BG_MAIN, activeforeground=TEXT_WHITE).grid(row=3, column=0, columnspan=2, sticky=tk.W)

        desna_strana = tk.LabelFrame(glavni_okvir, text=" Stranice Knjige (Redoslijed) ", font=("Segoe UI", 10, "bold"), bg=BG_MAIN, fg=TEXT_CYAN, bd=1, relief=tk.SOLID, padx=10, pady=10)
        desna_strana.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.lista_box = tk.Listbox(desna_strana, bg=BG_PANEL, fg=TEXT_WHITE, selectbackground=BTN_ACCENT, bd=0, font=("Segoe UI", 9))
        self.lista_box.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.lista_box.bind('<<ListboxSelect>>', self.prikazi_thumbnail)
        
        self.lbl_thumb = tk.Label(desna_strana, text="[Nema prikaza]", bg=BG_PANEL, fg="#64748B", height=6, width=15, relief=tk.SOLID, bd=1)
        self.lbl_thumb.pack(fill=tk.X, pady=5)

        self.btn_pokreni = tk.Button(self.root, text="⚡ GENERIRAJ OPTIMIZIRANI PORTABLE PDF", font=("Segoe UI", 12, "bold"), bg=BTN_GREEN, fg=TEXT_WHITE, bd=0, activebackground="#059669", command=self.procesiraj_knjigu)
        self.btn_pokreni.pack(fill=tk.X, padx=20, pady=(5, 5), ipady=8)
        
        status_bar = tk.Label(self.root, textvariable=self.trenutni_status, bd=1, relief=tk.SUNKEN, anchor=tk.W, bg=BG_PANEL, fg="#94A3B8", font=("Segoe UI", 9, "italic"))
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def osvjezi_slider(self, val):
        self.lbl_kvaliteta.config(text=f"{val}%")

    def dodaj_mapu(self):
        putanja = filedialog.askdirectory()
        if putanja:
            ekstenzije = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.jp2', '.heic')
            self.odabrane_datoteke_lista = [
                os.path.join(putanja, f) for f in os.listdir(putanja) if f.lower().endswith(ekstenzije)
            ]
            self.odabrane_datoteke_lista.sort()
            self.osvjezi_listu_gui()
            if self.odabrane_datoteke_lista:
                self.izlazni_pdf_putanja.set(os.path.join(putanja, f"{os.path.basename(putanja)}_knjiga.pdf"))

    def dodaj_datoteke(self):
        datoteke = filedialog.askopenfilenames(
            title="Odaberi skenirane stranice",
            filetypes=[("Sve podržane slike", "*.jpg *.jpeg *.png *.bmp *.gif *.jp2 *.heic")]
        )
        if datoteke:
            self.odabrane_datoteke_lista = list(datoteke)
            self.odabrane_datoteke_lista.sort()
            self.osvjezi_listu_gui()
            if self.odabrane_datoteke_lista:
                self.izlazni_pdf_putanja.set(os.path.join(os.path.dirname(self.odabrane_datoteke_lista), "nova_knjiga.pdf"))

    def osvjezi_listu_gui(self):
        self.lista_box.delete(0, tk.END)
        for f in self.odabrane_datoteke_lista:
            self.lista_box.insert(tk.END, os.path.basename(f))
        self.trenutni_status.set(f"Učitano {len(self.odabrane_datoteke_lista)} stranica.")

    def prikazi_thumbnail(self, event):
        try:
            indeks = self.lista_box.curselection()
            if not indeks:
                return
            putanja_slike = self.odabrane_datoteke_lista[indeks[0]]
            
            img = Image.open(putanja_slike)
            img.thumbnail((120, 90))
            
            self.photo_thumb = ImageTk.PhotoImage(img)
