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
from tkinter import filedialog, messagebox, ttk
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
        self.root.title("Premium PDF Book Studio v2.2 (Portable)")
        self.root.geometry("650x580")
        self.root.configure(bg="#1E293B")  # Duboka tamno-plava moderna pozadina
        self.root.resizable(False, False)
        
        self.izvor_tip = tk.StringVar(value="mapa")
        self.odabrani_putokaz = tk.StringVar(value="Nije odabrano nista...")
        self.odabrane_datoteke_lista = []
        self.izlazni_pdf = tk.StringVar()
        
        self.odabrani_format = tk.StringVar(value="A4")
        self.kvaliteta_kompresije = tk.IntVar(value=60)
        self.ocr_ukljucen = tk.BooleanVar(value=False)
        
        self.ucitaj_postavke()
        self.postavi_stilove()
        self.kreiraj_sucelje()

    def ucitaj_postavke(self):
        if os.path.exists(INI_PATH):
            try:
                import configparser
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
            import configparser
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

    def postavi_stilove(self):
        self.stil = ttk.Style()
        self.stil.theme_use('clam')
        
        # Kompletan ugrađeni Dark Mode dizajn bez vanjskih paketa
        BOJA_POZADINE = "#1E293B"
        BOJA_PANELA = "#0F172A"
        BOJA_TEKSTA = "#F8FAFC"
        
        self.stil.configure(".", background=BOJA_POZADINE, foreground=BOJA_TEKSTA)
        self.stil.configure("TFrame", background=BOJA_POZADINE)
        self.stil.configure("TLabel", background=BOJA_POZADINE, foreground=BOJA_TEKSTA, font=("Segoe UI", 10))
        self.stil.configure("Naslov.TLabel", font=("Segoe UI", 15, "bold"), foreground="#38BDF8")
        
        self.stil.configure("TEntry", fieldbackground=BOJA_PANELA, foreground="white", insertcolor="white", borderwidth=1, focusthickness=0)
        self.stil.configure("TCombobox", fieldbackground=BOJA_PANELA, foreground="white", selectbackground="#334155")
        self.stil.configure("TCheckbutton", background=BOJA_POZADINE, foreground=BOJA_TEKSTA)
        
        # Stilovi gumba s modernim zaobljenim dojmom i bojama
        self.stil.configure("TButton", font=("Segoe UI", 10, "bold"), background="#334155", foreground="white", borderwidth=0, padding=6)
        self.stil.map("TButton", background=[("active", "#475569")])
        
        self.stil.configure("Glavni.TButton", font=("Segoe UI", 12, "bold"), background="#0EA5E9", foreground="white", borderwidth=0, padding=12)
        self.stil.map("Glavni.TButton", background=[("active", "#0284C7")])

    def kreiraj_sucelje(self):
        okvir = ttk.Frame(self.root, padding=25)
        okvir.pack(fill=tk.BOTH, expand=True)
        
        # Naslov programa
        ttk.Label(okvir, text="📚 Premium PDF Book Studio", style="Naslov.TLabel").pack(anchor=tk.W, pady=(0, 15))
        
        # --- INFOGRAFIKA (Prekrasan vizualni panel kreiran čistim elementima) ---
        panel_toka = tk.Frame(okvir, bg="#0F172A", bd=1, relief=tk.SOLID)
        panel_toka.pack(fill=tk.X, pady=(0, 20))
        
        lbl_ulaz = tk.Label(panel_toka, text="📖 ULAZNI FORMATI\n[ JPG, JP2, PNG, HEIC, BMP ]", bg="#0F172A", fg="#38BDF8", font=("Segoe UI", 9, "bold"), justify=tk.CENTER)
        lbl_ulaz.pack(side=tk.LEFT, expand=True, pady=15)
        
        lbl_strelica = tk.Label(panel_toka, text="  ➔  ➔  ➔  ", bg="#0F172A", fg="#F59E0B", font=("Segoe UI", 18, "bold"))
        lbl_strelica.pack(side=tk.LEFT)
        
        lbl_izlaz = tk.Label(panel_toka, text="📄 IZLAZNI DOKUMENT\n[ Optimizirani PDF ]", bg="#0F172A", fg="#10B981", font=("Segoe UI", 9, "bold"), justify=tk.CENTER)
        lbl_izlaz.pack(side=tk.RIGHT, expand=True, pady=15)
        
        # --- 1. KORAK: ODABIR ULAZA ---
        ttk.Label(okvir, text="1. Odaberite izvor (Cijela mapa ili pojedinacne slike):", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 6))
        okvir_gumbiju = ttk.Frame(okvir)
        okvir_gumbiju.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(okvir_gumbiju, text="📂 Ucitaj cijelu mapu...", command=self.odaberi_mapu).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        ttk.Button(okvir_gumbiju, text="🖼️ Odaberi datoteke...", command=self.odaberi_datoteke_pojedinacno).pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        ttk.Label(okvir, textvariable=self.odabrani_putokaz, font=("Segoe UI", 9, "italic"), foreground="#94A3B8").pack(anchor=tk.W, pady=(0, 15))
        
        # --- 2. KORAK: ODABIR IZLAZA ---
        ttk.Label(okvir, text="2. Lokacija i naziv novog PDF dokumenta:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 6))
        okvir_izlaz = ttk.Frame(okvir)
        okvir_izlaz.pack(fill=tk.X, pady=(0, 20))
        
        polje_izlaz = ttk.Entry(okvir_izlaz, textvariable=self.izlazni_pdf, font=("Segoe UI", 10))
        polje_izlaz.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        ttk.Button(okvir_izlaz, text="Spremi kao...", command=self.odaberi_pdf).pack(side=tk.RIGHT)
        
        # --- 3. KORAK: NAPREDNE POSTAVKE ---
        okvir_postavke = tk.LabelFrame(okvir, text=" Napredne Postavke ", bg="#1E293B", fg="#38BDF8", font=("Segoe UI", 9, "bold"), padx=15, pady=15, bd=1, relief=tk.SOLID)
        okvir_postavke.pack(fill=tk.X, pady=(0, 25))
        
        # Format papira
        okvir_format = ttk.Frame(okvir_postavke)
        okvir_format.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        ttk.Label(okvir_format, text="Format papira:").pack(anchor=tk.W, pady=2)
        izbornik_formata = ttk.Combobox(okvir_format, textvariable=self.odabrani_format, values=list(FORMATE_PAPIRA.keys()), state="readonly")
        izbornik_formata.pack(fill=tk.X)
        
        # Kompresija
        okvir_kompresija = ttk.Frame(okvir_postavke)
        okvir_kompresija.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        ttk.Label(okvir_kompresija, text="Kvaliteta slika (1-100):").pack(anchor=tk.W, pady=2)
        okvir_klizaca = ttk.Frame(okvir_kompresija)
        okvir_klizaca.pack(fill=X)
        klizac = ttk.Scale(okvir_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, command=self.azuriraj_oznaku_kvalitete)
        klizac.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.oznaka_kvalitete = ttk.Label(okvir_klizaca, text=f"{self.kvaliteta_kompresije.get()}%", font=("Segoe UI", 10, "bold"), width=4)
        self.oznaka_kvalitete.pack(side=RIGHT)
        
        # OCR
        okvir_ocr = ttk.Frame(okvir_postavke)
        okvir_ocr.pack(side=tk.RIGHT, fill=tk.X, pady=(12, 0))
        ttk.Checkbutton(okvir_ocr, text="Ukljuci OCR sloj", variable=self.ocr_ukljucen).pack(anchor=tk.E)
        
        # --- 4. GLAVNI GUMB (Prekrasna tirkizno-plava boja) ---
        self.gumb_pokreni = ttk.Button(okvir, text="⚡ POKRENI OPTIMIZIRANU PRETvorBU KNJIGE", style="Glavni.TButton", command=self.pokreni_pretvorbu)
        self.gumb_pokreni.pack(fill=tk.X)

    def azuriraj_oznaku_kvalitete(self, *args):
        self.oznaka_kvalitete.config(text=f"{int(self.kvaliteta_kompresije.get())}%")

    def odaberi_mapu(self):
        mapa = filedialog.askdirectory()
        if mapa:
            self.izvor_tip.set("mapa")
            self.odabrane_datoteke_lista = []
            self.odabrani_putokaz.set(f"Odabrana mapa: {mapa}")
            self.izlazni_pdf.set(os.path.join(mapa, "skenirana_knjiga_studio.pdf"))

    def odaberi_datoteke_pojedinacno(self):
        ekstenzije = [("Sve podrzane slike", "*.jpg *.jpeg *.png *.bmp *.jp2 *.gif *.heic")]
        datoteke = filedialog.askopenfilenames(filetypes=ekstenzije)
        if datoteke:
            self.izvor_tip.set("datoteke")
            self.odabrane_datoteke_lista = list(datoteke)
            self.odabrane_datoteke_lista.sort()
            prva_direktorij = os.path.dirname(self.odabrane_datoteke_lista[0])
            self.odabrani_putokaz.set(f"Odabrano: {len(self.odabrane_datoteke_lista)} slika.")
            self.izlazni_pdf.set(os.path.join(prva_direktorij, "izabrane_stranice_studio.pdf"))

    def odaberi_pdf(self):
        datoteka = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF datoteke", "*.pdf")])
        if datoteka:
            self.izlazni_pdf.set(datoteka)


