import os
import sys

# Pokretanje unutar try/except bloka kako bismo prisilno uhvatili svaku potencijalnu grešku
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
            self.root.title("Premium PDF Book Studio v2.5 (Portable)")
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
            tk.Label(self.root, text="📚 Premium PDF Book Studio", font=("Arial", 14, "bold")).pack(pady=10)
            
            # 1. Ulaz
            okvir_ulaz = tk.LabelFrame(self.root, text=" 1. Odabir izvornih slika ", padx=10, pady=10)
            okvir_ulaz.pack(fill=tk.X, padx=15, pady=5)
            
            tk.Button(okvir_ulaz, text="📂 Ucitaj cijelu mapu...", command=self.odaberi_mapu, width=20).pack(side=tk.LEFT, padx=5)
            tk.Button(okvir_ulaz, text="🖼️ Odaberi datoteke...", command=self.odaberi_datoteke_pojedinacno, width=20).pack(side=tk.LEFT, padx=5)
            tk.Label(okvir_ulaz, textvariable=self.odabrani_putokaz, font=("Arial", 9, "italic"), fg="gray").pack(anchor=tk.W, padx=5, pady=5)
            
            # 2. Izlaz
            okvir_izlaz = tk.LabelFrame(self.root, text=" 2. Odrediste PDF datoteke ", padx=10, pady=10)
            okvir_izlaz.pack(fill=tk.X, padx=15, pady=5)
            
            tk.Entry(okvir_izlaz, textvariable=self.izlazni_pdf, width=50).pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
            tk.Button(okvir_izlaz, text="Spremi kao...", command=self.odaberi_pdf).pack(side=tk.RIGHT, padx=5)
            
            # 3. Postavke
            okvir_postavke = tk.LabelFrame(self.root, text=" Postavke i Optimizacija ", padx=10, pady=10)
            okvir_postavke.pack(fill=tk.X, padx=15, pady=10)
            
            tk.Label(okvir_postavke, text="Format papira:").grid(row=0, column=0, sticky=tk.W, padx=5)
            izbornik = tk.OptionMenu(okvir_postavke, self.odabrani_format, *list(FORMATE_PAPIRA.keys()))
            izbornik.grid(row=1, column=0, sticky=tk.W, padx=5)
            
            tk.Label(okvir_postavke, text="Kvaliteta (1-100):").grid(row=0, column=1, sticky=tk.W, padx=20)
            red_klizaca = tk.Frame(okvir_postavke)
            red_klizaca.grid(row=1, column=1, sticky=tk.W, padx=20)
            klizac = tk.Scale(red_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, orient=tk.HORIZONTAL, length=120, showvalue=False, command=self.azuriraj_oznaku_kvalitete)
            klizac.pack(side=tk.LEFT)
            self.oznaka_kvalitete = tk.Label(red_klizaca, text=f"{self.kvaliteta_kompresije.get()}%", font=("Arial", 9, "bold"))
            self.oznaka_kvalitete.pack(side=tk.LEFT, padx=5)
            
            tk.Label(okvir_postavke, text="Tekstualni sloj:").grid(row=0, column=2, sticky=tk.W, padx=20)
            tk.Checkbutton(okvir_postavke, text="Ukljuci OCR sloj", variable=self.ocr_ukljucen).grid(row=1, column=2, sticky=tk.W, padx=20)
            
            # 4. Gumb
            tk.Button(self.root, text="⚡ POKRENI OPTIMIZIRANU PRETVORBU KNJIGE", font=("Arial", 11, "bold"), bg="#4CAF50", fg="white", command=self.pokreni_pretvorbu).pack(fill=tk.X, padx=15, pady=15)

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
                prvi_direktorij = os.path.dirname(self.odabrane_datoteke_lista[0])
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
                    
                    prva_slika = lista_finalnih_slika[0]
                    ostale_slike = lista_finalnih_slika[1:]
                    
                    prva_slika.save(
                        izlaz,
                        save_all=True,
                        append_images=ostale_slike,
                        quality=int(self.kvaliteta_kompresije.get()),
                        optimize=True
                    )
                    messagebox.showinfo("Uspjeh!", "PDF knjiga je uspjesno kreirana!\nPostavke su spremljene u 'postavke.ini'.")
            except Exception as e:
                messagebox.showerror("Greska", f"Doslo je do pogreske: {str(e)}")

    if __name__ == "__main__":
        root = tk.Tk()
        app = PDFConverterApp(root)
        root.mainloop()

except Exception as e:
    # Ako se program sruši bilo kada, terminal NEĆE nestati, nego će ispisati grešku i čekati pritisak tipke
    print("\n[CRITICAL ERROR] Aplikacija se srusila pri pokretanju!")
