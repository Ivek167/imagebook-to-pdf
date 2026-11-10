import os
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as tb  # Moderna biblioteka za GUI teme
from ttkbootstrap.constants import *
from PIL import Image

try:
    import pi_heif
    pi_heif.register_heif_opener()
    HEIC_SUPPORT = True
except ImportError:
    HEIC_SUPPORT = False

# Dimenzije optimizirane za ekrane
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

class PDFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Konverter Skeniranih Knjiga u PDF v1.2")
        self.root.geometry("600x480")
        self.root.resizable(False, False)
        
        self.ulazna_mapa = tk.StringVar()
        self.izlazni_pdf = tk.StringVar()
        self.odabrani_format = tk.StringVar(value="A4")
        self.kvaliteta_kompresije = tk.IntVar(value=60)
        
        self.kreiraj_sucelje()

    def kreiraj_sucelje(self):
        # Glavni kontejner s marginama
        okvir = tb.Frame(self.root, padding=25)
        okvir.pack(fill=BOTH, expand=True)
        
        # Naslov aplikacije
        naslov = tb.Label(okvir, text="📚 Pretvarač Knjiga u PDF", font=("Segoe UI", 16, "bold"), bootstyle=DEFAULT)
        naslov.pack(anchor=W, pady=(0, 20))
        
        # 1. Ulazna mapa
        okvir_ulaz = tb.Frame(okvir)
        okvir_ulaz.pack(fill=X, pady=8)
        tb.Label(okvir_ulaz, text="1. Mapa sa skeniranim slikama:", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        
        polje_ulaz = tb.Entry(okvir_ulaz, textvariable=self.ulazna_mapa, font=("Segoe UI", 10))
        polje_ulaz.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        tb.Button(okvir_ulaz, text="Pregledaj...", bootstyle=SECONDARY, command=self.odaberi_mapu).pack(side=RIGHT)
        
        # 2. Izlazni PDF
        okvir_izlaz = tb.Frame(okvir)
        okvir_izlaz.pack(fill=X, pady=8)
        tb.Label(okvir_izlaz, text="2. Gdje spremiti PDF datoteku:", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        
        polje_izlaz = tb.Entry(okvir_izlaz, textvariable=self.izlazni_pdf, font=("Segoe UI", 10))
        polje_izlaz.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        tb.Button(okvir_izlaz, text="Spremi kao...", bootstyle=SECONDARY, command=self.odaberi_pdf).pack(side=RIGHT)
        
        # Redak za Format i Kompresiju (jedan pored drugog za ljepši izgled)
        okvir_postavke = tb.Frame(okvir)
        okvir_postavke.pack(fill=X, pady=15)
        
        # 3. Format papira
        okvir_format = tb.Frame(okvir_postavke)
        okvir_format.pack(side=LEFT, fill=X, expand=True, padx=(0, 20))
        tb.Label(okvir_format, text="3. Format papira:", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        izbornik_formata = tb.Combobox(okvir_format, textvariable=self.odabrani_format, values=list(FORMATE_PAPIRA.keys()), state="readonly", font=("Segoe UI", 10))
        izbornik_formata.pack(fill=X)
        
        # 4. Kompresija
        okvir_kompresija = tb.Frame(okvir_postavke)
        okvir_kompresija.pack(side=RIGHT, fill=X, expand=True)
        tb.Label(okvir_kompresija, text="4. Kvaliteta slika (1-100):", font=("Segoe UI", 10)).pack(anchor=W, pady=2)
        
        okvir_klizaca = tb.Frame(okvir_kompresija)
        okvir_klizaca.pack(fill=X)
        klizac = tb.Scale(okvir_klizaca, from_=1, to=100, variable=self.kvaliteta_kompresije, bootstyle=SUCCESS, command=self.azuriraj_oznaku_kvalitete)
        klizac.pack(side=LEFT, fill=X, expand=True, padx=(0, 10))
        self.oznaka_kvalitete = tb.Label(okvir_klizaca, text="60%", font=("Segoe UI", 10, "bold"), width=4)
        self.oznaka_kvalitete.pack(side=RIGHT)
        
        # 5. Gumb za pokretanje (Glavna akcija u uočljivoj boji)
        self.gumb_pokreni = tb.Button(okvir, text="KREIRAJ OPTIMIZIRANI PDF", bootstyle=SUCCESS, padding=12, command=self.pokreni_pretvorbu)
        self.gumb_pokreni.pack(fill=X, pady=(30, 0))

    def azuriraj_oznaku_kvalitete(self, *args):
        self.oznaka_kvalitete.config(text=f"{int(self.kvaliteta_kompresije.get())}%")

    def odaberi_mapu(self):
        mapa = filedialog.askdirectory()
        if mapa:
            self.ulazna_mapa.set(mapa)
            if not self.izlazni_pdf.get():
                self.izlazni_pdf.set(os.path.join(mapa, "skenirana_knjiga_opt.pdf"))

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
            
        ekstenzije = ('.jpg', '.jpeg', '.png', '.bmp', '.jp2', '.gif', '.heic')
        slikovne_datoteke = [f for f in os.listdir(mapa) if f.lower().endswith(ekstenzije)]
        slikovne_datoteke.sort()
        
        if not slikovne_datoteke:
            messagebox.showwarning("Nema slika", "U odabranoj mapi nema podržanih slika!")
            return
            
        sirina_papira, visina_papira = FORMATE_PAPIRA[self.odabrani_format.get()]
        lista_slika_za_pdf = []
        
        try:
            for datoteka in slikovne_datoteke:
                putanja_slike = os.path.join(mapa, datoteka)
                img = Image.open(putanja_slike)
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.thumbnail((sirina_papira, visina_papira), Image.Resampling.LANCZOS)
                
                pozadina = Image.new('RGB', (sirina_papira, visina_papira), (255, 255, 255))
                offset = ((sirina_papira - img.width) // 2, (visina_papira - img.height) // 2)
                pozadina.paste(img, offset)
                
                lista_slika_za_pdf.append(pozadina)
                
            if lista_slika_za_pdf:
                prva_stranica = lista_slika_za_pdf[0]
                ostale_stranice = lista_slika_za_pdf[1:]
                
                prva_stranica.save(
                    izlaz,
                    save_all=True,
                    append_images=ostale_stranice,
                    quality=int(self.kvaliteta_kompresije.get()),
                    optimize=True,
                    progressive=True
                )
                messagebox.showinfo("Uspjeh", f"Knjiga je uspješno optimizirana!\nSpremljeno na: {izlaz}")
        except Exception as e:
            messagebox.showerror("Greška pri konverziji", f"Došlo je do greške: {str(e)}")

if __name__ == "__main__":
    # Koristimo 'cyborg' temu za moderan tamni izgled aplikacije
    root = tb.Window(themename="cyborg")
    app = PDFConverterApp(root)
    root.mainloop()
