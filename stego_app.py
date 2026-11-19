#!/usr/bin/env python3
"""
ElectroBlue Stego - Steganography App
Ascunde fișiere (PDF, EXE, APK, ZIP, orice tip) în imagini PNG/JPEG și în audio (WAV / MP3 / MPEG Audio)
Temă: Electro Blue | Compresie automată | Progress bar
Autor: AndromedaHK
Versiune: 1.2
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import struct
import hashlib
import zlib
import threading
import wave

# ==================== CONFIG ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLORS = {
    "bg": "#0a0e17",
    "card": "#111827",
    "accent": "#00d4ff",
    "accent_hover": "#00a8cc",
    "accent_dark": "#0090b3",
    "text": "#e0f7ff",
    "text_dim": "#7dd3fc",
    "success": "#22d3ee",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "border": "#1e3a5f",
}

MAGIC_IMG = b"ELBLUE2"
MAGIC_WAV = b"ELBAUD1"
MAGIC_MP3 = b"ELBMP3!"
AUTHOR = "AndromedaHK"
APP_NAME = "ElectroBlue Stego"
VERSION = "1.3"


class ElectroBlueStego(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME}  •  by {AUTHOR}")
        self.geometry("820x780")
        self.minsize(740, 700)
        self.configure(fg_color=COLORS["bg"])

        self.cover_path = None
        self.payload_path = None
        self.stego_path = None
        self.audio_path = None
        self.audio_stego_path = None
        self.is_busy = False
        self.output_format = ctk.StringVar(value="png")

        self._build_ui()

    def _build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(14, 4))

        ctk.CTkLabel(
            header, text="⚡ ElectroBlue Stego",
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=COLORS["accent"]
        ).pack(side="left")

        ctk.CTkLabel(
            header, text=f"v{VERSION}  •  by {AUTHOR}",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
        ).pack(side="left", padx=(12, 0), pady=(6, 0))

        # Tabs
        self.tabs = ctk.CTkTabview(self, fg_color=COLORS["bg"],
                                   segmented_button_selected_color=COLORS["accent"],
                                   segmented_button_selected_hover_color=COLORS["accent_hover"],
                                   segmented_button_unselected_color=COLORS["card"],
                                   text_color="#001018")
        self.tabs.pack(fill="both", expand=True, padx=16, pady=6)

        self.tab_img = self.tabs.add("🖼️  Imagine")
        self.tab_audio = self.tabs.add("🎧  Audio")

        self._build_image_tab()
        self._build_audio_tab()

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=6)

        self.status = ctk.CTkLabel(
            footer, text="Gata.", font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
        )
        self.status.pack(side="left")

        ctk.CTkLabel(
            footer, text=f"Created by {AUTHOR}",
            font=ctk.CTkFont(size=11), text_color="#4b5563"
        ).pack(side="right")

    # ==================== IMAGE TAB ====================
    def _build_image_tab(self):
        tab = self.tab_img

        embed = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        embed.pack(fill="x", pady=(8, 8), padx=4)

        ctk.CTkLabel(embed, text="🔒  ASCUNDE FIȘIER ÎN IMAGINE",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Imagine:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.cover_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.cover_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_cover).pack(side="right")

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Fișier de ascuns:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.payload_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.payload_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_payload).pack(side="right")

        fmt_row = ctk.CTkFrame(embed, fg_color="transparent")
        fmt_row.pack(fill="x", padx=16, pady=(6, 2))
        ctk.CTkLabel(fmt_row, text="Format ieșire:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        ctk.CTkRadioButton(fmt_row, text="PNG (recomandat)", variable=self.output_format,
                           value="png", text_color=COLORS["text"],
                           fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]).pack(side="left", padx=8)
        ctk.CTkRadioButton(fmt_row, text="JPEG (riscant)", variable=self.output_format,
                           value="jpeg", text_color=COLORS["text"],
                           fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]).pack(side="left", padx=8)

        self.capacity_label = ctk.CTkLabel(embed, text="Capacitate: —",
                                           font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"])
        self.capacity_label.pack(anchor="w", padx=16, pady=(6, 0))

        self.compress_info = ctk.CTkLabel(embed, text="",
                                          font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"])
        self.compress_info.pack(anchor="w", padx=16, pady=(0, 4))

        self.progress = ctk.CTkProgressBar(embed, height=7, progress_color=COLORS["accent"], fg_color="#1e293b")
        self.progress.pack(fill="x", padx=16, pady=(2, 2))
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(embed, text="", font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"])
        self.progress_label.pack(anchor="w", padx=16, pady=(0, 6))

        self.embed_btn = ctk.CTkButton(
            embed, text="🔒  ASCUNDE ÎN IMAGINE",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_embed_image
        )
        self.embed_btn.pack(fill="x", padx=16, pady=(0, 14))

        extract = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                               border_width=1, border_color=COLORS["border"])
        extract.pack(fill="x", pady=(0, 8), padx=4)

        ctk.CTkLabel(extract, text="🔓  EXTRAGE DIN IMAGINE",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(extract, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Imagine stego:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.stego_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.stego_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_stego).pack(side="right")

        self.extract_btn = ctk.CTkButton(
            extract, text="🔓  EXTRAGE DIN IMAGINE",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_extract_image
        )
        self.extract_btn.pack(fill="x", padx=16, pady=(10, 14))

        warn = ctk.CTkFrame(tab, fg_color="#1a1500", corner_radius=10, border_width=1, border_color="#5c4a00")
        warn.pack(fill="x", padx=4, pady=(0, 6))
        ctk.CTkLabel(warn, text="⚠️  WhatsApp: trimite ca DOCUMENT (nu ca poză) ca să nu se piardă datele.",
                     font=ctk.CTkFont(size=12), text_color="#fde68a").pack(padx=12, pady=10)

    # ==================== AUDIO TAB ====================
    def _build_audio_tab(self):
        tab = self.tab_audio

        embed = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        embed.pack(fill="x", pady=(8, 8), padx=4)

        ctk.CTkLabel(embed, text="🎧  ASCUNDE FIȘIER ÎN AUDIO (WAV / MP3)",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Fișier audio:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.audio_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_audio).pack(side="right")

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Fișier de ascuns:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.audio_payload_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_payload_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_audio_payload).pack(side="right")

        self.audio_info = ctk.CTkLabel(embed, text="Suport: WAV (LSB real)  •  MP3 / MPEG Audio (payload la final)",
                                       font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"])
        self.audio_info.pack(anchor="w", padx=16, pady=(8, 4))

        self.audio_progress = ctk.CTkProgressBar(embed, height=7, progress_color=COLORS["accent"], fg_color="#1e293b")
        self.audio_progress.pack(fill="x", padx=16, pady=(2, 2))
        self.audio_progress.set(0)
        self.audio_progress_label = ctk.CTkLabel(embed, text="", font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"])
        self.audio_progress_label.pack(anchor="w", padx=16, pady=(0, 6))

        self.audio_embed_btn = ctk.CTkButton(
            embed, text="🎧  ASCUNDE ÎN AUDIO",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_embed_audio
        )
        self.audio_embed_btn.pack(fill="x", padx=16, pady=(0, 14))

        extract = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                               border_width=1, border_color=COLORS["border"])
        extract.pack(fill="x", pady=(0, 8), padx=4)

        ctk.CTkLabel(extract, text="🔓  EXTRAGE DIN AUDIO",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(extract, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        ctk.CTkLabel(row, text="Audio stego:", width=120, anchor="w",
                     text_color=COLORS["text"]).pack(side="left")
        self.audio_stego_label = ctk.CTkLabel(row, text="Niciun fișier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_stego_label.pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(row, text="Alege...", width=80, height=28,
                      fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
                      command=self.select_audio_stego).pack(side="right")

        self.audio_extract_btn = ctk.CTkButton(
            extract, text="🔓  EXTRAGE DIN AUDIO",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_extract_audio
        )
        self.audio_extract_btn.pack(fill="x", padx=16, pady=(10, 14))

        info = ctk.CTkFrame(tab, fg_color="#0c1929", corner_radius=10, border_width=1, border_color=COLORS["border"])
        info.pack(fill="x", padx=4, pady=(0, 6))
        ctk.CTkLabel(
            info,
            text="WAV = steganografie reală (LSB)\nMP3 = datele se adaugă la final (melodia rămâne playable, funcționează bine pe WhatsApp ca Document)",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"], justify="left"
        ).pack(padx=12, pady=10)

    # ==================== SELECTORS ====================
    def select_cover(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Imagini", "*.png *.jpg *.jpeg"), ("Toate", "*.*")])
        if path:
            self.cover_path = path
            self.cover_label.configure(text=os.path.basename(path))
            self._update_capacity()

    def select_payload(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Fișiere comune", "*.pdf *.exe *.apk *.zip *.doc *.docx *.txt"),
            ("PDF", "*.pdf"),
            ("Executabile", "*.exe *.apk"),
            ("Arhive", "*.zip *.rar *.7z"),
            ("Toate fișierele", "*.*")
        ])
        if path:
            self.payload_path = path
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.payload_label.configure(text=f"{os.path.basename(path)}  ({size_mb:.2f} MB)")
            self._update_capacity()

    def select_stego(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Imagini", "*.png *.jpg *.jpeg"), ("Toate", "*.*")])
        if path:
            self.stego_path = path
            self.stego_label.configure(text=os.path.basename(path))

    def select_audio(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3 *.mpeg *.mpg *.m4a"), ("MP3 / MPEG", "*.mp3 *.mpeg *.mpg"), ("WAV", "*.wav"), ("Toate", "*.*")])
        if path:
            self.audio_path = path
            self.audio_label.configure(text=os.path.basename(path))

    def select_audio_payload(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Fișiere comune", "*.pdf *.exe *.apk *.zip *.doc *.docx *.txt"),
            ("PDF", "*.pdf"),
            ("Executabile", "*.exe *.apk"),
            ("Arhive", "*.zip *.rar *.7z"),
            ("Toate fișierele", "*.*")
        ])
        if path:
            self.payload_path = path
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.audio_payload_label.configure(text=f"{os.path.basename(path)}  ({size_mb:.2f} MB)")

    def select_audio_stego(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Audio", "*.wav *.mp3 *.mpeg *.mpg *.m4a"), ("MP3 / MPEG", "*.mp3 *.mpeg *.mpg"), ("WAV", "*.wav"), ("Toate", "*.*")])
        if path:
            self.audio_stego_path = path
            self.audio_stego_label.configure(text=os.path.basename(path))

    # ==================== CAPACITY ====================
    def _update_capacity(self):
        self.compress_info.configure(text="")
        if not self.cover_path:
            self.capacity_label.configure(text="Capacitate: —")
            return
        try:
            img = Image.open(self.cover_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            w, h = img.size
            capacity = (w * h * 3) // 8 - 600
            capacity_mb = capacity / (1024 * 1024)
            msg = f"Capacitate: {capacity_mb:.2f} MB"

            if self.payload_path:
                with open(self.payload_path, "rb") as f:
                    data = f.read()
                comp = zlib.compress(data, 9)
                ratio = (1 - len(comp) / len(data)) * 100 if data else 0
                self.compress_info.configure(
                    text=f"După compresie: {len(comp)/(1024*1024):.2f} MB  (~{ratio:.0f}% economie)",
                    text_color=COLORS["text_dim"]
                )
                if len(comp) > capacity:
                    msg += "  ❌ Prea mare"
                    self.capacity_label.configure(text_color=COLORS["danger"])
                else:
                    msg += f"  ✓ Încape (~{len(comp)/capacity*100:.1f}%)"
                    self.capacity_label.configure(text_color=COLORS["success"])
            else:
                self.capacity_label.configure(text_color=COLORS["text_dim"])
            self.capacity_label.configure(text=msg)
        except Exception as e:
            self.capacity_label.configure(text=f"Eroare: {e}", text_color=COLORS["danger"])

    # ==================== HELPERS ====================
    def _set_busy(self, busy: bool):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        for btn in [self.embed_btn, self.extract_btn, self.audio_embed_btn, self.audio_extract_btn]:
            btn.configure(state=state)

    def _update_progress(self, bar, label, value, text=""):
        bar.set(value)
        label.configure(text=text)
        self.update_idletasks()

    def _bytes_to_bits(self, data: bytes):
        for byte in data:
            for i in range(7, -1, -1):
                yield (byte >> i) & 1

    def _bits_to_bytes(self, bits):
        result = bytearray()
        byte = 0
        count = 0
        for bit in bits:
            byte = (byte << 1) | bit
            count += 1
            if count == 8:
                result.append(byte)
                byte = 0
                count = 0
        return bytes(result)

    def _prepare_payload(self, path):
        with open(path, "rb") as f:
            original = f.read()
        filename = os.path.basename(path).encode("utf-8")
        if len(filename) > 255:
            raise ValueError("Nume fișier prea lung")
        compressed = zlib.compress(original, 9)
        if len(compressed) < len(original):
            store = compressed
            flags = 1
        else:
            store = original
            flags = 0
        checksum = hashlib.sha256(original).digest()
        return original, filename, store, flags, checksum

    # ==================== IMAGE EMBED ====================
    def start_embed_image(self):
        if self.is_busy: return
        if not self.cover_path or not self.payload_path:
            messagebox.showwarning("Lipsă", "Selectează imaginea și fișierul.")
            return
        if self.output_format.get() == "jpeg":
            if not messagebox.askyesno("Atenție JPEG",
                "Salvarea ca JPEG este riscantă!\nDatele se pot pierde din cauza compresiei.\n\n"
                "Recomandat: folosește PNG.\n\nVrei totuși să continui cu JPEG?"):
                return
        self._set_busy(True)
        threading.Thread(target=self._embed_image_worker, daemon=True).start()

    def _embed_image_worker(self):
        try:
            self.after(0, lambda: self.status.configure(text="Se procesează imaginea...", text_color=COLORS["accent"]))
            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.1, "Se citește..."))

            original, filename, store, flags, checksum = self._prepare_payload(self.payload_path)

            header = (MAGIC_IMG + bytes([flags]) + bytes([len(filename)]) + filename +
                      struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
            full_data = header + store

            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.25, "Se pregătește imaginea..."))

            img = Image.open(self.cover_path).convert("RGB")
            pixels = list(img.getdata())
            capacity = (len(pixels) * 3) // 8
            if len(full_data) > capacity:
                self.after(0, lambda: messagebox.showerror("Prea mare", "Fișierul (chiar comprimat) nu încape în imagine."))
                self.after(0, lambda: self._finish_error())
                return

            bits = list(self._bytes_to_bits(full_data))
            new_pixels = []
            bit_idx = 0
            total = len(pixels)
            step = max(1, total // 20)

            for i, (r, g, b) in enumerate(pixels):
                if bit_idx < len(bits):
                    r = (r & 0xFE) | bits[bit_idx]; bit_idx += 1
                if bit_idx < len(bits):
                    g = (g & 0xFE) | bits[bit_idx]; bit_idx += 1
                if bit_idx < len(bits):
                    b = (b & 0xFE) | bits[bit_idx]; bit_idx += 1
                new_pixels.append((r, g, b))
                if i % step == 0:
                    p = 0.25 + (i / total) * 0.55
                    self.after(0, lambda v=p, pct=int(i/total*100): self._update_progress(
                        self.progress, self.progress_label, v, f"Se ascunde... {pct}%"))

            stego = Image.new("RGB", img.size)
            stego.putdata(new_pixels)

            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.9, "Se salvează..."))
            self.after(0, lambda: self._save_image(stego, original, store, flags))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Eroare", str(e)))
            self.after(0, lambda: self._finish_error())

    def _save_image(self, stego, original, store, flags):
        try:
            fmt = self.output_format.get()
            if fmt == "png":
                path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")],
                                                    initialfile="stego_image.png")
            else:
                path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")],
                                                    initialfile="stego_image.jpg")
            if not path:
                self.status.configure(text="Anulat.", text_color=COLORS["text_dim"])
                self._update_progress(self.progress, self.progress_label, 0, "")
                self._set_busy(False)
                return

            if fmt == "png":
                stego.save(path, "PNG")
            else:
                stego.save(path, "JPEG", quality=100)

            ratio = (1 - len(store)/len(original))*100 if original else 0
            msg = f"Compresie ~{ratio:.0f}%" if flags else "Fără compresie"
            self._update_progress(self.progress, self.progress_label, 1.0, "Gata!")
            self.status.configure(text=f"✓ Salvat: {os.path.basename(path)}  |  {msg}", text_color=COLORS["success"])
            messagebox.showinfo("Succes", f"Fișier ascuns!\n\n{msg}\nSalvat: {os.path.basename(path)}\n\n"
                                 "⚠️ Trimite ca DOCUMENT pe WhatsApp!")
        except Exception as e:
            messagebox.showerror("Eroare salvare", str(e))
        finally:
            self._set_busy(False)
            self.after(2500, lambda: self._update_progress(self.progress, self.progress_label, 0, ""))

    # ==================== IMAGE EXTRACT ====================
    def start_extract_image(self):
        if self.is_busy: return
        if not self.stego_path:
            messagebox.showwarning("Lipsă", "Selectează imaginea stego.")
            return
        self._set_busy(True)
        threading.Thread(target=self._extract_image_worker, daemon=True).start()

    def _extract_image_worker(self):
        try:
            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.3, "Se citește..."))
            img = Image.open(self.stego_path).convert("RGB")
            pixels = list(img.getdata())
            bits = []
            for r, g, b in pixels:
                bits.extend([r & 1, g & 1, b & 1])
            data = self._bits_to_bytes(bits)

            if data[:7] not in (b"ELBLUE2", b"ELBLUE1"):
                self.after(0, lambda: messagebox.showerror("Eroare", "Nu conține date ElectroBlue."))
                self.after(0, lambda: self._finish_error())
                return

            if data[:7] == b"ELBLUE2":
                flags = data[7]
                nlen = data[8]
                name = data[9:9+nlen].decode("utf-8")
                ssize = struct.unpack(">Q", data[17+nlen:25+nlen])[0]
                checksum = data[25+nlen:57+nlen]
                stored = data[57+nlen:57+nlen+ssize]
                payload = zlib.decompress(stored) if flags & 1 else stored
            else:
                nlen = data[7]
                name = data[8:8+nlen].decode("utf-8")
                size = struct.unpack(">Q", data[8+nlen:16+nlen])[0]
                checksum = data[16+nlen:48+nlen]
                payload = data[48+nlen:48+nlen+size]

            if hashlib.sha256(payload).digest() != checksum:
                self.after(0, lambda: messagebox.showwarning("Atenție", "Checksum invalid – fișierul poate fi corupt."))

            self.after(0, lambda: self._save_extracted(name, payload, self.progress, self.progress_label))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Eroare", str(e)))
            self.after(0, lambda: self._finish_error())

    # ==================== AUDIO EMBED ====================
    def start_embed_audio(self):
        if self.is_busy: return
        if not self.audio_path or not self.payload_path:
            messagebox.showwarning("Lipsă", "Selectează fișierul audio și fișierul de ascuns.")
            return
        self._set_busy(True)
        threading.Thread(target=self._embed_audio_worker, daemon=True).start()

    def _embed_audio_worker(self):
        try:
            ext = os.path.splitext(self.audio_path)[1].lower()
            self.after(0, lambda: self.status.configure(text="Se procesează audio...", text_color=COLORS["accent"]))
            self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.15, "Se pregătește..."))

            original, filename, store, flags, checksum = self._prepare_payload(self.payload_path)

            if ext == ".wav":
                self._embed_wav(original, filename, store, flags, checksum)
            elif ext in (".mp3", ".mpeg", ".mpg", ".m4a"):
                self._embed_mp3(original, filename, store, flags, checksum)
            else:
                raise ValueError("Format audio nesuportat. Folosește WAV, MP3 sau MPEG Audio.")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Eroare", str(e)))
            self.after(0, lambda: self._finish_error_audio())

    def _embed_wav(self, original, filename, store, flags, checksum):
        self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.3, "WAV: se citește..."))

        with wave.open(self.audio_path, "rb") as wr:
            params = wr.getparams()
            frames = wr.readframes(wr.getnframes())

        header = (MAGIC_WAV + bytes([flags]) + bytes([len(filename)]) + filename +
                  struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
        full = header + store

        if len(full) * 8 > len(frames):
            self.after(0, lambda: messagebox.showerror("Prea mare", "Fișierul nu încape în acest WAV."))
            self.after(0, lambda: self._finish_error_audio())
            return

        audio = bytearray(frames)
        bits = list(self._bytes_to_bits(full))
        for i, bit in enumerate(bits):
            audio[i] = (audio[i] & 0xFE) | bit

        self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.85, "Se salvează WAV..."))
        self.after(0, lambda: self._save_wav(params, bytes(audio), original, store, flags))

    def _save_wav(self, params, frames, original, store, flags):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")],
                                                initialfile="stego_audio.wav")
            if not path:
                self._finish_error_audio()
                return
            with wave.open(path, "wb") as ww:
                ww.setparams(params)
                ww.writeframes(frames)
            ratio = (1 - len(store)/len(original))*100 if original else 0
            self._update_progress(self.audio_progress, self.audio_progress_label, 1.0, "Gata!")
            self.status.configure(text=f"✓ WAV salvat: {os.path.basename(path)}", text_color=COLORS["success"])
            messagebox.showinfo("Succes", f"Ascuns în WAV!\nEconomie ~{ratio:.0f}%\n\nTrimite ca Document pe WhatsApp.")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
        finally:
            self._set_busy(False)
            self.after(2500, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0, ""))

    def _embed_mp3(self, original, filename, store, flags, checksum):
        self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.4, "MP3: se pregătește..."))

        with open(self.audio_path, "rb") as f:
            mp3_data = f.read()

        header = (MAGIC_MP3 + bytes([flags]) + bytes([len(filename)]) + filename +
                  struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
        trailer = header + store + MAGIC_MP3 + struct.pack(">I", len(header) + len(store))

        out = mp3_data + trailer

        self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.85, "Se salvează MP3..."))
        self.after(0, lambda: self._save_mp3(out, original, store, flags))

    def _save_mp3(self, data, original, store, flags):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3", "*.mp3")],
                                                initialfile="stego_audio.mp3")
            if not path:
                self._finish_error_audio()
                return
            with open(path, "wb") as f:
                f.write(data)
            ratio = (1 - len(store)/len(original))*100 if original else 0
            self._update_progress(self.audio_progress, self.audio_progress_label, 1.0, "Gata!")
            self.status.configure(text=f"✓ MP3 salvat: {os.path.basename(path)}", text_color=COLORS["success"])
            messagebox.showinfo("Succes", f"Ascuns în MP3!\nEconomie ~{ratio:.0f}%\n\n"
                                 "Melodia rămâne playable.\nTrimite ca Document pe WhatsApp.")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
        finally:
            self._set_busy(False)
            self.after(2500, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0, ""))

    # ==================== AUDIO EXTRACT ====================
    def start_extract_audio(self):
        if self.is_busy: return
        if not self.audio_stego_path:
            messagebox.showwarning("Lipsă", "Selectează fișierul audio stego.")
            return
        self._set_busy(True)
        threading.Thread(target=self._extract_audio_worker, daemon=True).start()

    def _extract_audio_worker(self):
        try:
            ext = os.path.splitext(self.audio_stego_path)[1].lower()
            self.after(0, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0.3, "Se extrage..."))

            if ext == ".wav":
                self._extract_wav()
            elif ext in (".mp3", ".mpeg", ".mpg", ".m4a"):
                self._extract_mp3()
            else:
                raise ValueError("Format nesuportat")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Eroare", str(e)))
            self.after(0, lambda: self._finish_error_audio())

    def _extract_wav(self):
        with wave.open(self.audio_stego_path, "rb") as wr:
            frames = wr.readframes(wr.getnframes())

        bits = [(b & 1) for b in frames]
        data = self._bits_to_bytes(bits)

        if data[:7] != MAGIC_WAV:
            self.after(0, lambda: messagebox.showerror("Eroare", "Nu conține date ElectroBlue (WAV)."))
            self.after(0, lambda: self._finish_error_audio())
            return

        flags = data[7]
        nlen = data[8]
        name = data[9:9+nlen].decode("utf-8")
        ssize = struct.unpack(">Q", data[17+nlen:25+nlen])[0]
        checksum = data[25+nlen:57+nlen]
        stored = data[57+nlen:57+nlen+ssize]
        payload = zlib.decompress(stored) if flags & 1 else stored

        if hashlib.sha256(payload).digest() != checksum:
            self.after(0, lambda: messagebox.showwarning("Atenție", "Checksum invalid."))

        self.after(0, lambda: self._save_extracted(name, payload, self.audio_progress, self.audio_progress_label))

    def _extract_mp3(self):
        with open(self.audio_stego_path, "rb") as f:
            data = f.read()

        idx = data.rfind(MAGIC_MP3)
        if idx == -1 or idx + 11 > len(data):
            self.after(0, lambda: messagebox.showerror("Eroare", "Nu conține date ElectroBlue (MP3)."))
            self.after(0, lambda: self._finish_error_audio())
            return

        size = struct.unpack(">I", data[idx+7:idx+11])[0]
        start = idx - size
        if start < 0:
            raise ValueError("Date corupte")
        block = data[start:idx]

        if block[:7] != MAGIC_MP3:
            raise ValueError("Header invalid")

        flags = block[7]
        nlen = block[8]
        name = block[9:9+nlen].decode("utf-8")
        ssize = struct.unpack(">Q", block[17+nlen:25+nlen])[0]
        checksum = block[25+nlen:57+nlen]
        stored = block[57+nlen:57+nlen+ssize]
        payload = zlib.decompress(stored) if flags & 1 else stored

        if hashlib.sha256(payload).digest() != checksum:
            self.after(0, lambda: messagebox.showwarning("Atenție", "Checksum invalid."))

        self.after(0, lambda: self._save_extracted(name, payload, self.audio_progress, self.audio_progress_label))

    # ==================== COMMON ====================
    def _save_extracted(self, filename, payload, bar, label):
        try:
            path = filedialog.asksaveasfilename(initialfile=filename, filetypes=[("Toate", "*.*")])
            if not path:
                self.status.configure(text="Anulat.", text_color=COLORS["text_dim"])
                self._update_progress(bar, label, 0, "")
                self._set_busy(False)
                return
            with open(path, "wb") as f:
                f.write(payload)
            self._update_progress(bar, label, 1.0, "Gata!")
            self.status.configure(text=f"✓ Extras: {filename} ({len(payload):,} bytes)", text_color=COLORS["success"])
            messagebox.showinfo("Succes", f"Extras:\n{filename}\n{len(payload):,} bytes")
        except Exception as e:
            messagebox.showerror("Eroare", str(e))
        finally:
            self._set_busy(False)
            self.after(2500, lambda: self._update_progress(bar, label, 0, ""))

    def _finish_error(self):
        self.status.configure(text="Eroare", text_color=COLORS["danger"])
        self._update_progress(self.progress, self.progress_label, 0, "")
        self._set_busy(False)

    def _finish_error_audio(self):
        self.status.configure(text="Eroare", text_color=COLORS["danger"])
        self._update_progress(self.audio_progress, self.audio_progress_label, 0, "")
        self._set_busy(False)


if __name__ == "__main__":
    app = ElectroBlueStego()
    app.mainloop()
