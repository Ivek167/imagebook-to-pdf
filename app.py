import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image

# Pokušaj uvoza podrške za HEIC (mobiteli)
try:
    import pi_heif
    pi_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False

# Dimenzije papira u pikselima pri standardnih 300 DPI za precizan ispis
FORMATE_PAPIRA = {
    "A5": (1748, 2480),
    "A4": (2480, 3508),
    "A3": (3508, 4960),
    "A2": (4960, 7016),
    "A1": (7016, 9933),
    "A0": (9933, 14043),
    "Letter (US)": (2550, 3300),
    "Legal (US)": (2550, 4200),
    "Ledger/Tabloid (US)": (3300, 4650)
}

class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konverter Skeniranih Knjiga u PDF v1.0")
        self.root.geometry("550x400")
        self.root.resizable(False, False)
        
        # Varijable
        self.ulazna_mapa = tk.StringVar()
        self.izlazni_pdf = tk.StringVar()
        self.odabrani_format = tk.StringVar(value="A4")
        self.kvaliteta_kompresije = tk.IntVar(value=75)
        
        self.kreiraj_sucelje()

    def kreiraj_sucelje(self):
        # Glavni okvir
        okvir = ttk.Frame(self.root, padding="20")
        okvir.pack(fill=tk.BOTH, expand=True)
        
        # 1. Odabir ulazne mape
        ttk.Label(okvir, text="1. Mapa sa skeniranim slikama knjige:").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(okvir, textvariable=self.ulazna_mapa, width=50).grid(row=1, column=0, padx=(0, 10))
        ttk.Button(okvir, text="Pregledaj...", command=self.odaberi_mapu).grid(row=1, column=1)
        
        # 2. Odabir izlaznog PDF-a
        ttk.Label(okvir, text="2. Gdje spremiti PDF datoteku:").grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        ttk.Entry(okvir, textvariable=self.izlazni_pdf, width=50).grid(row=3, column=0, padx=(0, 10))
        ttk.Button(okvir, text="Spremi kao...", command=self.odaberi_pdf).grid(row=3, column=1)
        
        # 3. Format papira
        ttk.Label(okvir, text="3. Format papira u PDF-u:").grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        izbornik_formata = ttk.Combobox(okvir, textvariable=self.odabrani_format, values=list(FORMATE_PAPIRA.keys()), state="readonly", width=20)
        izbornik_formata.grid(row=5, column=0, sticky=tk.W)
        
        # 4. Kompresija / Kvaliteta
        ttk.Label(okvir, text="4. Kvaliteta kompresije slika (1-100):").grid(row=6, column=0, sticky=tk.W, pady=(15, 5))
        
        okvir_klizaca = ttk.Frame(okvir)
        okvir_klizaca.grid(row=7, column=0, columnspan=2, sticky=tk.W)
        
        klizac = ttk.Scale(okvir_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, orient=tk.HORIZONTAL, length=300, command=self.azuriraj_oznaku_kvalitete)
        klizac.pack(side=tk.LEFT, padx=(0, 10))
        
        self.oznaka_kvalitete = ttk.Label(okvir_klizaca, text="75%")
        self.oznaka_kvalitete.pack(side=tk.LEFT)
        
        # 5. Gumb za pokretanje
        self.gumb_pokreni = ttk.Button(okvir, text="KREIRAJ PDF KNJIGU", command=self.pokreni_pretvorbu, padding=10)
        self.gumb_pokreni.grid(row=8, column=0, columnspan=2, pady=(25, 0))

    def azuriraj_oznaku_kvalitete(self, *args):
        self.oznaka_kvalitete.config(text=f"{int(self.kvaliteta_kompresije.get())}%")

    def odaberi_mapu(self):
        mapa = filedialog.askdirectory()
        if mapa:
            self.ulazna_mapa.set(mapa)
            if not self.izlazni_pdf.get():
                self.izlazni_pdf.set(os.path.join(mapa, "skenirana_knjiga.pdf"))

    def odaberi_pdf(self):
        datoteka = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF datoteke", "*.pdf")])
        if datoteka:
            self.izlazni_pdf.set(datoteka)

    def pokreni_pretvorbu(self):
        mapa = self.ulazna_mapa.get()
        izlaz = self.izlazni_pdf.get()
        
        if not mapa or not os.path.exists(mapa):
            messagebox.showerror("Greška", "Molimo odaberite ispravnu mapu sa slikama!")
            return
        if not izlaz:
            messagebox.showerror("Greška", "Molimo definirajte gdje želite spremiti PDF!")
            return
            
        # Podržane ekstenzije prema vašem zahtjevu
        ekstenzije = ('.jpg', '.jpeg', '.png', '.bmp', '.jp2', '.gif', '.heic')
        
        slikovne_datoteke = [f for f in os.listdir(mapa) if f.lower().endswith(ekstenzije)]
        slikovne_datoteke.sort() # Sortiranje radi redoslijeda stranica knjige
        
        if not slikovne_datoteke:
            messagebox.showwarning("Nema slika", "U odabranoj mapi nema podržanih slika!")
            return
            
        sirina_papira, visina_papira = FORMATE_PAPIRA[self.odabrani_format.get()]
        lista_slika_za_pdf = []
        
        try:
            for i, datoteka in enumerate(slikovne_datoteke):
                putanja_slike = os.path.join(mapa, datoteka)
                img = Image.open(putanja_slike)
                
                # Konverzija u RGB mod (obavezno za PDF)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Prilagođavanje veličini odabranog papira uz očuvanje omjera (Aspect Ratio)
                img.thumbnail((sirina_papira, visina_papira), Image.Resampling.LANCZOS)
                
                # Stvaranje bijele pozadine odabranog formata papira
                pozadina = Image.new('RGB', (sirina_papira, visina_papira), (255, 255, 255))
                # Centriranje slike na papiru
                offset = ((sirina_papira - img.width) // 2, (visina_papira - img.height) // 2)
                pozadina.paste(img, offset)
                
                lista_slika_za_pdf.append(pozadina)
                
            # Spremanje u PDF s odabranom razinom kompresije
            if lista_slika_za_pdf:
                prva_stranica = lista_slika_za_pdf[0]
                ostale_stranice = lista_slika_za_pdf[1:]
                
                prva_stranica.save(
                    izlaz,
                    save_all=True,
                    append_images=ostale_stranice,
                    quality=int(self.kvaliteta_kompresije.get()),
                    optimize=True
                )
                messagebox.showinfo("Uspjeh", f"Knjiga je uspješno pretvorena!\nSpremljeno na: {izlaz}")
        except Exception as e:
            messagebox.showerror("Greška pri konverziji", f"Došlo je do greške: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFConverterApp(root)
    root.mainloop()
