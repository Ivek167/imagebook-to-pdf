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
        self.root.title("Premium PDF Book Studio v2.2 (Portable)")
        self.root.geometry("600x480")
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
        glavni_okvir = ttk.Frame(self.root, padding="20")
        glavni_okvir.pack(fill=tk.BOTH, expand=True)
        
        # Vizualni flowchart (tekstualni)
        panel = ttk.LabelFrame(glavni_okvir, text=" Tijek rada aplikacije ")
        panel.pack(fill=tk.X, pady=(0, 15), ipady=5)
        
        okvir_toka = ttk.Frame(panel)
        okvir_toka.pack(anchor=tk.CENTER)
        ttk.Label(okvir_toka, text="📖 ULAZ\n[JPG, JP2, PNG, BMP, GIF]", font=("Segoe UI", 9, "bold"), justify=tk.CENTER).pack(side=tk.LEFT, padx=10)
        ttk.Label(okvir_toka, text=" ➔ ➔ ➔ ", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=15)
        ttk.Label(okvir_toka, text="📄 IZLAZ\n[Optimizirani PDF]", font=("Segoe UI", 9, "bold"), justify=tk.CENTER).pack(side=tk.LEFT, padx=10)
        
        # 1. Odabir ulaza
        okvir_ulaz = ttk.LabelFrame(glavni_okvir, text=" 1. Odabir izvornih slika ")
        okvir_ulaz.pack(fill=tk.X, pady=5, ipady=5)
        
        okvir_gumba = ttk.Frame(okvir_ulaz)
        okvir_gumba.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(okvir_gumba, text="📂 Ucitaj cijelu mapu...", command=self.odaberi_mapu).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(okvir_gumba, text="🖼️ Odaberi datoteke...", command=self.odaberi_datoteke_pojedinacno).pack(side=tk.LEFT)
        
        ttk.Label(okvir_ulaz, textvariable=self.odabrani_putokaz, font=("Segoe UI", 9, "italic")).pack(anchor=tk.W, padx=5, pady=2)
        
        # 2. Odabir izlaza
        okvir_izlaz = ttk.LabelFrame(glavni_okvir, text=" 2. Odrediste PDF datoteke ")
        okvir_izlaz.pack(fill=tk.X, pady=5, ipady=5)
        
        polje_izlaz = ttk.Entry(okvir_izlaz, textvariable=self.izlazni_pdf)
        polje_izlaz.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(okvir_izlaz, text="Spremi kao...", command=self.odaberi_pdf).pack(side=tk.RIGHT, padx=5)
        
        # 3. Postavke
        okvir_postavke = ttk.LabelFrame(glavni_okvir, text=" Postavke i Optimizacija ")
        okvir_postavke.pack(fill=tk.X, pady=10, ipady=5)
        
        ttk.Label(okvir_postavke, text="Format papira:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        izbornik = ttk.Combobox(okvir_postavke, textvariable=self.odabrani_format, values=list(FORMATE_PAPIRA.keys()), state="readonly", width=15)
        izbornik.grid(row=1, column=0, sticky=tk.W, padx=5)
        
        ttk.Label(okvir_postavke, text="Kvaliteta (1-100):").grid(row=0, column=1, sticky=tk.W, padx=15, pady=2)
        red_klizaca = ttk.Frame(okvir_postavke)
        red_klizaca.grid(row=1, column=1, sticky=tk.W, padx=15)
        klizac = ttk.Scale(red_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, orient=tk.HORIZONTAL, length=120, command=self.azuriraj_oznaku_kvalitete)
        klizac.pack(side=tk.LEFT)
        self.oznaka_kvalitete = ttk.Label(red_klizaca, text=f"{self.kvaliteta_kompresije.get()}%", font=("Segoe UI", 9, "bold"))
        self.oznaka_kvalitete.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(okvir_postavke, text="Tekstualni sloj:").grid(row=0, column=2, sticky=tk.W, padx=15, pady=2)
        ttk.Checkbutton(okvir_postavke, text="Ukljuci OCR sloj", variable=self.ocr_ukljucen).grid(row=1, column=2, sticky=tk.W, padx=15)
        
        # 4. Gumb za pokretanje
        self.gumb_pokreni = ttk.Button(glavni_okvir, text="⚡ POKRENI KREIRANJE PORTABLE PDF-a", command=self.pokreni_pretvorbu)
        self.gumb_pokreni.pack(fill=tk.X, pady=(15, 0))

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
        ekstenzije = [("Sve podrzane slike", "*.jpg *.jpeg *.png *.bmp *.jp2 *.gif")]
        datoteke = filedialog.askopenfilenames(filetypes=ekstenzije)
        if datoteke:
            self.izvor_tip.set("datoteke")
            self.odabrane_datoteke_lista = list(datoteke)
            self.odabrane_datoteke_lista.sort()
            prva_direktorij = os.path.dirname(self.odabrane_datoteke_lista)
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
            messagebox.showerror("Greska", "Molimo definirajte lokaciju izlaznog PDF-a!")
            return
            
        slike_za_obradu = []
        if self.izvor_tip.get() == "mapa":
            putanja_mape = self.odabrani_putokaz.get().replace("Odabrana mapa: ", "")
            if not os.path.exists(putanja_mape):
                messagebox.showerror("Greska", "Molimo odaberite ispravnu mapu!")
                return
            ekstenzije = ('.jpg', '.jpeg', '.png', '.bmp', '.jp2', '.gif')
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
                
                prva_slika = lista_finalnih_slika
                ostale = lista_finalnih_slika[1:]
                
                prva_slika.save(
                    izlaz,
                    save_all=True,
                    append_images=ostale,
                    quality=int(self.kvaliteta_kompresije.get()),
                    optimize=True
                )
                messagebox.showinfo("Uspjeh!", f"PDF je uspjesno kreiran!\n\nPostavke su spremljene u 'postavke.ini'.")
        except Exception as e:
            messagebox.showerror("Greska pri konverziji", f"Doslo je do pogreske: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
