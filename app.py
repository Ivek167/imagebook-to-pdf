import os
import sys

if getattr(sys, 'frozen', False):
    PROGRAM_DIR = os.path.dirname(sys.executable)
else:
    PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

os.environ["TMPDIR"] = PROGRAM_DIR
os.environ["TEMP"] = PROGRAM_DIR
os.environ["TMP"] = PROGRAM_DIR

import tkinter as tk
from tkinter import filedialog, messagebox
import configparser
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from PIL import Image

try:
    import pi_heif
    pi_heif.register_heif_opener()
except ImportError:
    pass

FORMATE_PAPIRA = {
    "A5": (420, 595),
    "A4": (595, 842),
    "A3": (842, 1191),
    "A2": (1191, 1684),
    "A1": (1684, 2384),
    "A0": (2384, 3370),
    "Letter (US)": (612, 792),
    "Legal (US)": (612, 1008),
    "Ledger/Tabloid (US)": (792, 1224)
}

INI_PATH = os.path.join(PROGRAM_DIR, "postavke.ini")

class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Premium PDF Book Studio v2.1 (Portable)")
        self.root.geometry("650x580")
        self.root.resizable(False, False)
        
        self.izvor_tip = tk.StringVar(value="mapa")
        self.odabrani_putokaz = tk.StringVar(value="Nije odabrano nista...")
        self.odabrane_datoteke_lista = []
        self.izlazni_pdf = tk.StringVar()
        
        self.odabrani_format = tk.StringVar(value="A4")
        self.kvaliteta_kompresije = tk.IntVar(value=60)
        self.ocr_ukljucen = tk.BooleanVar(value=False)
        
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
                    self.kvaliteta_kompresije.set(sekcija.getint('KvalitetaKompresije', 60))
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
        okvir = tb.Frame(self.root, padding=25)
        okvir.pack(fill=BOTH, expand=True)
        
        panel = tb.LabelFrame(okvir, text=" Tijek Pretvorbe Knjige ", padding=15, bootstyle=PRIMARY)
        panel.pack(fill=X, pady=(0, 15))
        
        okvir_toka = tb.Frame(panel)
        okvir_toka.pack(anchor=CENTER)
        
        tb.Label(okvir_toka, text="ULAZNI FORMATI\n[ JPG, JP2, PNG, HEIC, BMP ]", 
                 font=("Segoe UI", 10, "bold"), justify=CENTER, bootstyle=INFO).pack(side=LEFT, padx=10)
        
        tb.Label(okvir_toka, text=" >>> ", font=("Segoe UI", 20, "bold"), bootstyle=WARNING).pack(side=LEFT, padx=20)
        
        tb.Label(okvir_toka, text="IZLAZNI DOKUMENT\n[ Optimizirani PDF ]", 
                 font=("Segoe UI", 10, "bold"), justify=CENTER, bootstyle=SUCCESS).pack(side=LEFT, padx=10)
        
        okvir_ulaz = tb.LabelFrame(okvir, text=" 1. Odabir ulaznih slika ", padding=15)
        okvir_ulaz.pack(fill=X, pady=8)
        
        okvir_gumbiju = tb.Frame(okvir_ulaz)
        okvir_gumbiju.pack(fill=X, pady=(0, 10))
        
        tb.Button(okvir_gumbiju, text="Ucitaj cijelu mapu...", bootstyle=INFO, width=22, command=self.odaberi_mapu).pack(side=LEFT, padx=(0, 10))
        tb.Button(okvir_gumbiju, text="Odaberi datoteke...", bootstyle=PRIMARY, width=22, command=self.odaberi_datoteke_pojedinacno).pack(side=LEFT)
        
        tb.Label(okvir_ulaz, textvariable=self.odabrani_putokaz, font=("Segoe UI", 9, "italic"), bootstyle=MUTED).pack(anchor=W)
        
        okvir_izlaz = tb.LabelFrame(okvir, text=" 2. Odrediste PDF datoteke ", padding=15)
        okvir_izlaz.pack(fill=X, pady=8)
        
        polje_izlaz = tb.Entry(okvir_izlaz, textvariable=self.izlazni_pdf, font=("Segoe UI", 10))
        polje_izlaz.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        tb.Button(okvir_izlaz, text="Spremi kao...", bootstyle=SECONDARY, command=self.odaberi_pdf).pack(side=RIGHT)
        
        okvir_postavke = tb.Frame(okvir)
        okvir_postavke.pack(fill=X, pady=15)
        
        okvir_format = tb.Frame(okvir_postavke)
        okvir_format.pack(side=LEFT, fill=X, expand=True, padx=(0, 15))
        tb.Label(okvir_format, text="Format papira:", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        izbornik_formata = tb.Combobox(okvir_format, textvariable=self.odabrani_format, values=list(FORMATE_PAPIRA.keys()), state="readonly")
        izbornik_formata.pack(fill=X)
        
        okvir_kompresija = tb.Frame(okvir_postavke)
        okvir_kompresija.pack(side=LEFT, fill=X, expand=True, padx=(0, 15))
        tb.Label(okvir_kompresija, text="Kvaliteta slika (1-100):", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        okvir_klizaca = tb.Frame(okvir_kompresija)
        okvir_klizaca.pack(fill=X)
        klizac = tb.Scale(okvir_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, bootstyle=SUCCESS, command=self.azuriraj_oznaku_kvalitete)
        klizac.pack(side=LEFT, fill=X, expand=True, padx=(0, 5))
        self.oznaka_kvalitete = tb.Label(okvir_klizaca, text=f"{self.kvaliteta_kompresije.get()}%", font=("Segoe UI", 10, "bold"), width=4)
        self.oznaka_kvalitete.pack(side=RIGHT)
        
        okvir_ocr = tb.Frame(okvir_postavke)
        okvir_ocr.pack(side=RIGHT, fill=X, pady=(15, 0))
        tb.Checkbutton(okvir_ocr, text="Uključi OCR tekstualni sloj", variable=self.ocr_ukljucen, bootstyle="round-toggle").pack(anchor=E)
        
        self.gumb_pokreni = tb.Button(okvir, text="POKRENI KREIRANJE PREMIUM PDF-a", bootstyle=SUCCESS, padding=12, command=self.pokreni_pretvorbu)
        self.gumb_pokreni.pack(fill=X, pady=(20, 0))

    def azuriraj_oznaku_kvalitete(self, *args):
        self.oznaka_kvalitete.config(text=f"{int(self.kvaliteta_kompresije.get())}%")

    def odaberi_mapu(self):
        mapa = filedialog.askdirectory()
        if mapa:
            self.izvor_tip.set("mapa")
            self.odabrane_datoteke_lista = []
            self.odabrani_putokaz.set(f"Odabrana mapa: {mapa}")
            if not self.izlazni_pdf.get():
                self.izlazni_pdf.set(os.path.join(mapa, "skenirana_knjiga_studio.pdf"))

    def odaberi_datoteke_pojedinacno(self):
        ekstenzije = [("Sve podrzane slike", "*.jpg *.jpeg *.png *.bmp *.jp2 *.gif *.heic")]
        datoteke = filedialog.askopenfilenames(filetypes=ekstenzije)
        if datoteke:
            self.izvor_tip.set("datoteke")
            self.odabrane_datoteke_lista = list(datoteke)
            self.odabrane_datoteke_lista.sort()
            prva_direktorij = os.path.dirname(self.odabrane_datoteke_lista[0])
            self.odabrani_putokaz.set(f"Odabrano pojedinacno: {len(self.odabrane_datoteke_lista)} slika.")
            if not self.izlazni_pdf.get():
                self.izlazni_pdf.set(os.path.join(prva_direktorij, "izabrane_stranice_studio.pdf"))

    def odaberi_pdf(self):
        datoteka = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF datoteke", "*.pdf")])
        if datoteka:
            self.izlazni_pdf.set(datoteka)

    def pokreni_pretvorbu(self):
        izlaz = self.izlazni_pdf.get()
        if not izlaz:
            messagebox.showerror("Greška", "Molimo definirajte lokaciju izlaznog PDF-a!")
            return
            
        slike_za_obradu = []
        if self.izvor_tip.get() == "mapa":
            putanja_mape = self.odabrani_putokaz.get().replace("Odabrana mapa: ", "")
            if not os.path.exists(putanja_mape):
                messagebox.showerror("Greška", "Molimo odaberite ispravnu mapu!")
                return
            ekstenzije = ('.jpg', '.jpeg', '.png', '.bmp', '.jp2', '.gif', '.heic')
            slike_za_obradu = [os.path.join(putanja_mape, f) for f in os.listdir(putanja_mape) if f.lower().endswith(ekstenzije)]
            slike_za_obradu.sort()
        else:
            slike_za_obradu = self.odabrane_datoteke_lista

        if not slike_za_obradu:
            messagebox.showwarning("Nema slika", "Nema odabranih slika za pretvorbu!")
            return
            
        sirina_papira, visina_papira = FORMATE_PAPIRA[self.odabrani_format.get()]
        lista_finalnih_slika = []
        
        try:
            for putanja in slike_za_obradu:
                img = Image.open(putanja)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((sirina_papira, visina_papira), Image.Resampling.LANCZOS)
                
                pozadina = Image.new('RGB', (sirina_papira, visina_papira), (255, 255, 255))
                offset = ((sirina_papira - img.width) // 2, (visina_papira - img.height) // 2)
                pozadina.paste(img, offset)
                
                lista_finalnih_slika.append(pozadina)
                
            if lista_finalnih_slika:
                self.spremi_postavke()
                
                prva_slika = lista_finalnih_slika[0]
                ostale = lista_finalnih_slika[1:]
                
                prva_slika.save(
                    izlaz,
                    save_all=True,
                    append_images=ostale,
                    quality=int(self.kvaliteta_kompresije.get()),
                    optimize=True
                )
