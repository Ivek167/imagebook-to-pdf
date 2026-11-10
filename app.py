import os
import sys

try:
    if getattr(sys, 'frozen', False):
        PROGRAM_DIR = os.path.dirname(sys.executable)
    else:
        PROGRAM_DIR = os.path.dirname(os.path.abspath(__file__))

    import tkinter as tk
    from tkinter import filedialog, messagebox
    import configparser
    from PIL import Image

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
            self.root.title("Premium PDF Book Studio v2.6 (Portable)")
            self.root.geometry("620x520")
            self.root.configure(bg="#1E293B")
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
            BG_TAMNA = "#1E293B"
            BG_PANEL = "#0F172A"
            PLAVA_TEKST = "#38BDF8"
            ZELENA_GUMB = "#0EA5E9"
            ZELENA_GUMB_HOVER = "#0284C7"
            SIVA_GUMB = "#334155"
            SIVA_GUMB_HOVER = "#475569"
            TEKST_BIJELI = "#F8FAFC"
            
            tk.Label(self.root, text="📚 Premium PDF Book Studio", font=("Segoe UI", 16, "bold"), bg=BG_TAMNA, fg=PLAVA_TEKST).pack(pady=(15, 5))
            
            panel_toka = tk.Frame(self.root, bg=BG_PANEL, bd=1, relief=tk.SOLID)
            panel_toka.pack(fill=tk.X, padx=20, pady=(0, 15))
            
            tk.Label(panel_toka, text="📖 ULAZNI FORMATI\n[ JPG, JP2, PNG, BMP, GIF ]", bg=BG_PANEL, fg=PLAVA_TEKST, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, expand=True, pady=10)
            tk.Label(panel_toka, text="  ➔  ➔  ➔  ", bg=BG_PANEL, fg="#F59E0B", font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
            tk.Label(panel_toka, text="📄 IZLAZNI FILE\n[ Optimizirani PDF ]", bg=BG_PANEL, fg="#10B981", font=("Segoe UI", 9, "bold")).pack(side=tk.RIGHT, expand=True, pady=10)
            
            okvir_ulaz = tk.LabelFrame(self.root, text=" 1. Odabir izvornih slika ", font=("Segoe UI", 10, "bold"), bg=BG_TAMNA, fg=PLAVA_TEKST, padx=10, pady=10, bd=1, relief=tk.SOLID)
            okvir_ulaz.pack(fill=tk.X, padx=20, pady=5)
            
            btn_mapa = tk.Button(okvir_ulaz, text="📂 Ucitaj cijelu mapu...", command=self.odaberi_mapu, font=("Segoe UI", 10, "bold"), bg=SIVA_GUMB, fg=TEKST_BIJELI, bd=0, activebackground=SIVA_GUMB_HOVER, activeforeground=TEKST_BIJELI)
            btn_mapa.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            
            btn_file = tk.Button(okvir_ulaz, text="🖼️ Odaberi datoteke...", command=self.odaberi_datoteke_pojedinacno, font=("Segoe UI", 10, "bold"), bg=SIVA_GUMB, fg=TEKST_BIJELI, bd=0, activebackground=SIVA_GUMB_HOVER, activeforeground=TEKST_BIJELI)
            btn_file.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            
            lbl_putanja = tk.Label(okvir_ulaz, textvariable=self.odabrani_putokaz, font=("Segoe UI", 9, "italic"), bg=BG_TAMNA, fg="#94A3B8")
            lbl_putanja.pack(anchor=tk.W, padx=5, pady=(8, 0))
            
            okvir_izlaz = tk.LabelFrame(self.root, text=" 2. Odrediste PDF datoteke ", font=("Segoe UI", 10, "bold"), bg=BG_TAMNA, fg=PLAVA_TEKST, padx=10, pady=10, bd=1, relief=tk.SOLID)
            okvir_izlaz.pack(fill=tk.X, padx=20, pady=5)
            
            polje_izlaz = tk.Entry(okvir_izlaz, textvariable=self.izlazni_pdf, font=("Segoe UI", 10), bg=BG_PANEL, fg=TEKST_BIJELI, insertbackground=TEKST_BIJELI, bd=1, relief=tk.SOLID)
            polje_izlaz.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, ipady=3)
            
            btn_spremas = tk.Button(okvir_izlaz, text="Spremi kao...", command=self.odaberi_pdf, font=("Segoe UI", 9, "bold"), bg=SIVA_GUMB, fg=TEKST_BIJELI, bd=0, activebackground=SIVA_GUMB_HOVER, activeforeground=TEKST_BIJELI)
            btn_spremas.pack(side=tk.RIGHT, padx=5)
            
            okvir_postavke = tk.LabelFrame(self.root, text=" Napredne Postavke ", font=("Segoe UI", 10, "bold"), bg=BG_TAMNA, fg=PLAVA_TEKST, padx=15, pady=15, bd=1, relief=tk.SOLID)
            okvir_postavke.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(okvir_postavke, text="Format papira:", bg=BG_TAMNA, fg=TEKST_BIJELI).grid(row=0, column=0, sticky=tk.W, padx=5)
            izbornik = tk.OptionMenu(okvir_postavke, self.odabrani_format, *list(FORMATE_PAPIRA.keys()))
            izbornik.config(font=("Segoe UI", 9, "bold"), bg=SIVA_GUMB, fg=TEKST_BIJELI, bd=0, activebackground=SIVA_GUMB_HOVER, activeforeground=TEKST_BIJELI, highlightthickness=0)
            izbornik["menu"].config(bg=BG_PANEL, fg=TEKST_BIJELI)
            izbornik.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            
            tk.Label(okvir_postavke, text="Kvaliteta (1-100):", bg=BG_TAMNA, fg=TEKST_BIJELI).grid(row=0, column=1, sticky=tk.W, padx=25)
            red_klizaca = tk.Frame(okvir_postavke, bg=BG_TAMNA)
            red_klizaca.grid(row=1, column=1, sticky=tk.W, padx=25)
            klizac = tk.Scale(red_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, orient=tk.HORIZONTAL, length=130, showvalue=False, bg=BG_TAMNA, fg=TEKST_BIJELI, highlightthickness=0, troughcolor=BG_PANEL, command=self.azuriraj_oznaku_kvalitete)
            klizac.pack(side=tk.LEFT)
            self.oznaka_kvalitete = tk.Label(red_klizaca, text=f"{self.kvaliteta_kompresije.get()}%", font=("Segoe UI", 10, "bold"), bg=BG_TAMNA, fg=TEKST_BIJELI, width=4)
            self.oznaka_kvalitete.pack(side=tk.LEFT, padx=5)
            
            tk.Label(okvir_postavke, text="Tekstualni sloj:", bg=BG_TAMNA, fg=TEKST_BIJELI).grid(row=0, column=2, sticky=tk.W, padx=20)
            chk_ocr = tk.Checkbutton(okvir_postavke, text="Ukljuci OCR sloj", variable=self.ocr_ukljucen, bg=BG_TAMNA, fg=TEKST_BIJELI, selectcolor=BG_PANEL, activebackground=BG_TAMNA, activeforeground=TEKST_BIJELI, highlightthickness=0)
            chk_ocr.grid(row=1, column=2, sticky=tk.W, padx=20)
            
            btn_pokreni = tk.Button(self.root, text="⚡ POKRENI OPTIMIZIRANU PRETVORBU KNJIGE", font=("Segoe UI", 12, "bold"), bg=ZELENA_GUMB, fg=TEKST_BIJELI, bd=0, activebackground=ZELENA_GUMB_HOVER, activeforeground=TEKST_BIJELI, command=self.pokreni_pretvorbu)
            btn_pokreni.pack(fill=tk.X, padx=20, pady=15, ipady=8)

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
            datoteke = filedialog.askopenfilenames(title="Odaberite slike", filetypes=[("Sve podrzane slike", "*.jpg *.jpeg *.png *.bmp *.jp2 *.gif")])
            if datoteke:
                self.izvor_tip.set("datoteke")
                self.odabrane_datoteke_lista = list(datoteke)
                self.odabrane_datoteke_lista.sort()
                prvi_direktorij = os.path.dirname(self.odabrane_datoteke_lista)
                self.odabrani_putokaz.set(f"Odabrano: {len(self.odabrane_datoteke_lista)} slika.")
                self.izlazni_pdf.set(os.path.join(prvi_direktorij, "izabrane_stranice_studio.pdf"))

        def odaberi_pdf(self):
            datoteka = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF datoteke", "*.pdf")])
            if datoteka:
                self.izlazni_pdf.set(datoteka)

        def pokreni_pretvorbu(self):
            izlaz = self.izlazni_pdf.get()
            if not izlaz:
                messagebox.showerror("Greska", "Molimo definirajte lokaciju izlaznog PDF-a!")
                return
                
            slike_za_obradu = []
            if self.izvor_tip.get() == "mapa":
