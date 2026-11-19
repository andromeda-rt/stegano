#!/usr/bin/env python3
"""
ElectroBlue Stego - Steganography App
Hide any file (PDF, EXE, APK, ZIP...) in images (PNG/JPEG) and audio (WAV / MP3 / MPEG)
Theme: Electro Blue | Auto compression | Progress bar | RO/EN
Author: AndromedaHK
Version: 1.4
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
VERSION = "1.4"

# ==================== i18n ====================
T = {
    "ro": {
        "tab_image": "Imagine",
        "tab_audio": "Audio",
        "embed_img": "ASCUNDE FISIER IN IMAGINE",
        "extract_img": "EXTRAGE DIN IMAGINE",
        "embed_aud": "ASCUNDE FISIER IN AUDIO (WAV / MP3)",
        "extract_aud": "EXTRAGE DIN AUDIO",
        "lbl_image": "Imagine:",
        "lbl_payload": "Fisier de ascuns:",
        "lbl_stego": "Imagine stego:",
        "lbl_audio": "Fisier audio:",
        "lbl_audio_stego": "Audio stego:",
        "lbl_format": "Format iesire:",
        "btn_choose": "Alege...",
        "btn_embed_img": "ASCUNDE IN IMAGINE",
        "btn_extract_img": "EXTRAGE DIN IMAGINE",
        "btn_embed_aud": "ASCUNDE IN AUDIO",
        "btn_extract_aud": "EXTRAGE DIN AUDIO",
        "radio_png": "PNG (recomandat)",
        "radio_jpeg": "JPEG (riscant)",
        "capacity": "Capacitate: —",
        "none": "Niciun fisier",
        "audio_info": "Suport: WAV (LSB real)  •  MP3 / MPEG Audio (payload la final)",
        "whatsapp": "WhatsApp: trimite ca DOCUMENT (nu ca poza) ca sa nu se piarda datele.",
        "audio_help": "WAV = steganografie reala (LSB)\nMP3 = datele se adauga la final (melodia ramane playable)",
        "status_ready": "Gata.",
        "lang": "EN",
        "created": "Created by",
        "warn_missing": "Selecteaza fisierele necesare.",
        "warn_jpeg": "Salvarea ca JPEG este riscanta!\nDatele se pot pierde.\n\nRecomandat: PNG.\n\nContinui cu JPEG?",
        "err_capacity": "Fisierul (chiar comprimat) nu incape.",
        "success_img": "Fisier ascuns!\n\nTrimite ca DOCUMENT pe WhatsApp!",
        "success_aud": "Ascuns in audio!\n\nTrimite ca DOCUMENT pe WhatsApp.",
        "not_electro": "Nu contine date ElectroBlue.",
        "checksum_warn": "Checksum invalid – fisierul poate fi corupt.",
        "processing": "Se proceseaza...",
        "done": "Gata!",
    },
    "en": {
        "tab_image": "Image",
        "tab_audio": "Audio",
        "embed_img": "HIDE FILE IN IMAGE",
        "extract_img": "EXTRACT FROM IMAGE",
        "embed_aud": "HIDE FILE IN AUDIO (WAV / MP3)",
        "extract_aud": "EXTRACT FROM AUDIO",
        "lbl_image": "Image:",
        "lbl_payload": "File to hide:",
        "lbl_stego": "Stego image:",
        "lbl_audio": "Audio file:",
        "lbl_audio_stego": "Stego audio:",
        "lbl_format": "Output format:",
        "btn_choose": "Choose...",
        "btn_embed_img": "HIDE IN IMAGE",
        "btn_extract_img": "EXTRACT FROM IMAGE",
        "btn_embed_aud": "HIDE IN AUDIO",
        "btn_extract_aud": "EXTRACT FROM AUDIO",
        "radio_png": "PNG (recommended)",
        "radio_jpeg": "JPEG (risky)",
        "capacity": "Capacity: —",
        "none": "No file selected",
        "audio_info": "Support: WAV (real LSB)  •  MP3 / MPEG Audio (payload at end)",
        "whatsapp": "WhatsApp: send as DOCUMENT (not as photo) so data is not lost.",
        "audio_help": "WAV = real steganography (LSB)\nMP3 = data is appended at the end (track stays playable)",
        "status_ready": "Ready.",
        "lang": "RO",
        "created": "Created by",
        "warn_missing": "Please select the required files.",
        "warn_jpeg": "Saving as JPEG is risky!\nData may be lost.\n\nRecommended: PNG.\n\nContinue with JPEG?",
        "err_capacity": "File (even compressed) does not fit.",
        "success_img": "File hidden!\n\nSend as DOCUMENT on WhatsApp!",
        "success_aud": "Hidden in audio!\n\nSend as DOCUMENT on WhatsApp.",
        "not_electro": "Does not contain ElectroBlue data.",
        "checksum_warn": "Checksum invalid – file may be corrupt.",
        "processing": "Processing...",
        "done": "Done!",
    },
}


class ElectroBlueStego(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.lang = "ro"
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
        self.apply_language()

    def t(self, key):
        return T[self.lang].get(key, key)

    def toggle_language(self):
        self.lang = "en" if self.lang == "ro" else "ro"
        self.apply_language()

    def apply_language(self):
        # Tabs – CTkTabview has limited rename support; set via internal buttons if possible
        try:
            # Update segmented button texts
            seg = self.tabs._segmented_button
            seg.configure(values=[f"  {self.t('tab_image')}  ", f"  {self.t('tab_audio')}  "])
        except Exception:
            pass

        self.lbl_embed_img.configure(text="🔒  " + self.t("embed_img"))
        self.lbl_extract_img.configure(text="🔓  " + self.t("extract_img"))
        self.lbl_embed_aud.configure(text="🎧  " + self.t("embed_aud"))
        self.lbl_extract_aud.configure(text="🔓  " + self.t("extract_aud"))

        self.lbl_image.configure(text=self.t("lbl_image"))
        self.lbl_payload.configure(text=self.t("lbl_payload"))
        self.lbl_stego.configure(text=self.t("lbl_stego"))
        self.lbl_audio.configure(text=self.t("lbl_audio"))
        self.lbl_audio_payload.configure(text=self.t("lbl_payload"))
        self.lbl_audio_stego.configure(text=self.t("lbl_audio_stego"))
        self.lbl_format.configure(text=self.t("lbl_format"))

        self.btn_choose_cover.configure(text=self.t("btn_choose"))
        self.btn_choose_payload.configure(text=self.t("btn_choose"))
        self.btn_choose_stego.configure(text=self.t("btn_choose"))
        self.btn_choose_audio.configure(text=self.t("btn_choose"))
        self.btn_choose_audio_payload.configure(text=self.t("btn_choose"))
        self.btn_choose_audio_stego.configure(text=self.t("btn_choose"))

        self.embed_btn.configure(text="🔒  " + self.t("btn_embed_img"))
        self.extract_btn.configure(text="🔓  " + self.t("btn_extract_img"))
        self.audio_embed_btn.configure(text="🎧  " + self.t("btn_embed_aud"))
        self.audio_extract_btn.configure(text="🔓  " + self.t("btn_extract_aud"))

        self.radio_png.configure(text=self.t("radio_png"))
        self.radio_jpeg.configure(text=self.t("radio_jpeg"))

        if not self.cover_path:
            self.cover_label.configure(text=self.t("none"))
        if not self.payload_path:
            self.payload_label.configure(text=self.t("none"))
            self.audio_payload_label.configure(text=self.t("none"))
        if not self.stego_path:
            self.stego_label.configure(text=self.t("none"))
        if not self.audio_path:
            self.audio_label.configure(text=self.t("none"))
        if not self.audio_stego_path:
            self.audio_stego_label.configure(text=self.t("none"))

        self.capacity_label.configure(text=self.t("capacity"))
        self.audio_info.configure(text=self.t("audio_info"))
        self.whatsapp_label.configure(text="⚠️  " + self.t("whatsapp"))
        self.audio_help_label.configure(text=self.t("audio_help"))
        self.status.configure(text=self.t("status_ready"), text_color=COLORS["text_dim"])
        self.lang_btn.configure(text=self.t("lang"))
        self.footer_author.configure(text=f"{self.t('created')} {AUTHOR}")

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

        self.lang_btn = ctk.CTkButton(
            header, text="EN", width=50, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_language
        )
        self.lang_btn.pack(side="right")

        # Tabs
        self.tabs = ctk.CTkTabview(
            self, fg_color=COLORS["bg"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_color=COLORS["card"],
            text_color="#001018"
        )
        self.tabs.pack(fill="both", expand=True, padx=16, pady=6)

        self.tab_img = self.tabs.add("  Imagine  ")
        self.tab_audio = self.tabs.add("  Audio  ")

        self._build_image_tab()
        self._build_audio_tab()

        # Footer
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=6)

        self.status = ctk.CTkLabel(
            footer, text="Gata.", font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
        )
        self.status.pack(side="left")

        self.footer_author = ctk.CTkLabel(
            footer, text=f"Created by {AUTHOR}",
            font=ctk.CTkFont(size=11), text_color="#4b5563"
        )
        self.footer_author.pack(side="right")

    # ==================== IMAGE TAB ====================
    def _build_image_tab(self):
        tab = self.tab_img

        embed = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        embed.pack(fill="x", pady=(8, 8), padx=4)

        self.lbl_embed_img = ctk.CTkLabel(
            embed, text="🔒  ASCUNDE FISIER IN IMAGINE",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["accent"]
        )
        self.lbl_embed_img.pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_image = ctk.CTkLabel(row, text="Imagine:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_image.pack(side="left")
        self.cover_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.cover_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_cover = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_cover
        )
        self.btn_choose_cover.pack(side="right")

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_payload = ctk.CTkLabel(row, text="Fisier de ascuns:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_payload.pack(side="left")
        self.payload_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.payload_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_payload = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_payload
        )
        self.btn_choose_payload.pack(side="right")

        fmt_row = ctk.CTkFrame(embed, fg_color="transparent")
        fmt_row.pack(fill="x", padx=16, pady=(6, 2))
        self.lbl_format = ctk.CTkLabel(fmt_row, text="Format iesire:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_format.pack(side="left")
        self.radio_png = ctk.CTkRadioButton(
            fmt_row, text="PNG (recomandat)", variable=self.output_format, value="png",
            text_color=COLORS["text"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        )
        self.radio_png.pack(side="left", padx=8)
        self.radio_jpeg = ctk.CTkRadioButton(
            fmt_row, text="JPEG (riscant)", variable=self.output_format, value="jpeg",
            text_color=COLORS["text"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"]
        )
        self.radio_jpeg.pack(side="left", padx=8)

        self.capacity_label = ctk.CTkLabel(embed, text="Capacitate: —", font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"])
        self.capacity_label.pack(anchor="w", padx=16, pady=(6, 0))
        self.compress_info = ctk.CTkLabel(embed, text="", font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"])
        self.compress_info.pack(anchor="w", padx=16, pady=(0, 4))

        self.progress = ctk.CTkProgressBar(embed, height=7, progress_color=COLORS["accent"], fg_color="#1e293b")
        self.progress.pack(fill="x", padx=16, pady=(2, 2))
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(embed, text="", font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"])
        self.progress_label.pack(anchor="w", padx=16, pady=(0, 6))

        self.embed_btn = ctk.CTkButton(
            embed, text="🔒  ASCUNDE IN IMAGINE",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_embed_image
        )
        self.embed_btn.pack(fill="x", padx=16, pady=(0, 14))

        extract = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                               border_width=1, border_color=COLORS["border"])
        extract.pack(fill="x", pady=(0, 8), padx=4)

        self.lbl_extract_img = ctk.CTkLabel(
            extract, text="🔓  EXTRAGE DIN IMAGINE",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["accent"]
        )
        self.lbl_extract_img.pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(extract, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_stego = ctk.CTkLabel(row, text="Imagine stego:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_stego.pack(side="left")
        self.stego_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.stego_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_stego = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_stego
        )
        self.btn_choose_stego.pack(side="right")

        self.extract_btn = ctk.CTkButton(
            extract, text="🔓  EXTRAGE DIN IMAGINE",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_extract_image
        )
        self.extract_btn.pack(fill="x", padx=16, pady=(10, 14))

        warn = ctk.CTkFrame(tab, fg_color="#1a1500", corner_radius=10, border_width=1, border_color="#5c4a00")
        warn.pack(fill="x", padx=4, pady=(0, 6))
        self.whatsapp_label = ctk.CTkLabel(
            warn, text="⚠️  WhatsApp: trimite ca DOCUMENT...",
            font=ctk.CTkFont(size=12), text_color="#fde68a"
        )
        self.whatsapp_label.pack(padx=12, pady=10)

    # ==================== AUDIO TAB ====================
    def _build_audio_tab(self):
        tab = self.tab_audio

        embed = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                             border_width=1, border_color=COLORS["border"])
        embed.pack(fill="x", pady=(8, 8), padx=4)

        self.lbl_embed_aud = ctk.CTkLabel(
            embed, text="🎧  ASCUNDE FISIER IN AUDIO",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["accent"]
        )
        self.lbl_embed_aud.pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_audio = ctk.CTkLabel(row, text="Fisier audio:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_audio.pack(side="left")
        self.audio_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_audio = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_audio
        )
        self.btn_choose_audio.pack(side="right")

        row = ctk.CTkFrame(embed, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_audio_payload = ctk.CTkLabel(row, text="Fisier de ascuns:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_audio_payload.pack(side="left")
        self.audio_payload_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_payload_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_audio_payload = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_audio_payload
        )
        self.btn_choose_audio_payload.pack(side="right")

        self.audio_info = ctk.CTkLabel(
            embed, text="Suport: WAV / MP3", font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"]
        )
        self.audio_info.pack(anchor="w", padx=16, pady=(8, 4))

        self.audio_progress = ctk.CTkProgressBar(embed, height=7, progress_color=COLORS["accent"], fg_color="#1e293b")
        self.audio_progress.pack(fill="x", padx=16, pady=(2, 2))
        self.audio_progress.set(0)
        self.audio_progress_label = ctk.CTkLabel(embed, text="", font=ctk.CTkFont(size=11), text_color=COLORS["text_dim"])
        self.audio_progress_label.pack(anchor="w", padx=16, pady=(0, 6))

        self.audio_embed_btn = ctk.CTkButton(
            embed, text="🎧  ASCUNDE IN AUDIO",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_embed_audio
        )
        self.audio_embed_btn.pack(fill="x", padx=16, pady=(0, 14))

        extract = ctk.CTkFrame(tab, fg_color=COLORS["card"], corner_radius=12,
                               border_width=1, border_color=COLORS["border"])
        extract.pack(fill="x", pady=(0, 8), padx=4)

        self.lbl_extract_aud = ctk.CTkLabel(
            extract, text="🔓  EXTRAGE DIN AUDIO",
            font=ctk.CTkFont(size=14, weight="bold"), text_color=COLORS["accent"]
        )
        self.lbl_extract_aud.pack(anchor="w", padx=16, pady=(12, 8))

        row = ctk.CTkFrame(extract, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=3)
        self.lbl_audio_stego = ctk.CTkLabel(row, text="Audio stego:", width=120, anchor="w", text_color=COLORS["text"])
        self.lbl_audio_stego.pack(side="left")
        self.audio_stego_label = ctk.CTkLabel(row, text="Niciun fisier", text_color=COLORS["text_dim"], anchor="w")
        self.audio_stego_label.pack(side="left", fill="x", expand=True, padx=6)
        self.btn_choose_audio_stego = ctk.CTkButton(
            row, text="Alege...", width=80, height=28,
            fg_color=COLORS["accent_dark"], hover_color=COLORS["accent"], command=self.select_audio_stego
        )
        self.btn_choose_audio_stego.pack(side="right")

        self.audio_extract_btn = ctk.CTkButton(
            extract, text="🔓  EXTRAGE DIN AUDIO",
            font=ctk.CTkFont(size=13, weight="bold"), height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            text_color="#001018", command=self.start_extract_audio
        )
        self.audio_extract_btn.pack(fill="x", padx=16, pady=(10, 14))

        info = ctk.CTkFrame(tab, fg_color="#0c1929", corner_radius=10, border_width=1, border_color=COLORS["border"])
        info.pack(fill="x", padx=4, pady=(0, 6))
        self.audio_help_label = ctk.CTkLabel(
            info, text="WAV = LSB\nMP3 = payload la final",
            font=ctk.CTkFont(size=12), text_color=COLORS["text_dim"], justify="left"
        )
        self.audio_help_label.pack(padx=12, pady=10)

    # ==================== SELECTORS ====================
    def select_cover(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All", "*.*")])
        if path:
            self.cover_path = path
            self.cover_label.configure(text=os.path.basename(path))
            self._update_capacity()

    def select_payload(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Common", "*.pdf *.exe *.apk *.zip *.doc *.docx *.txt"),
            ("PDF", "*.pdf"), ("Executables", "*.exe *.apk"),
            ("Archives", "*.zip *.rar *.7z"), ("All files", "*.*")
        ])
        if path:
            self.payload_path = path
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.payload_label.configure(text=f"{os.path.basename(path)}  ({size_mb:.2f} MB)")
            self._update_capacity()

    def select_stego(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg"), ("All", "*.*")])
        if path:
            self.stego_path = path
            self.stego_label.configure(text=os.path.basename(path))

    def select_audio(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Audio", "*.wav *.mp3 *.mpeg *.mpg *.m4a"),
            ("MP3 / MPEG", "*.mp3 *.mpeg *.mpg"), ("WAV", "*.wav"), ("All", "*.*")
        ])
        if path:
            self.audio_path = path
            self.audio_label.configure(text=os.path.basename(path))

    def select_audio_payload(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Common", "*.pdf *.exe *.apk *.zip *.doc *.docx *.txt"),
            ("PDF", "*.pdf"), ("All files", "*.*")
        ])
        if path:
            self.payload_path = path
            size_mb = os.path.getsize(path) / (1024 * 1024)
            self.audio_payload_label.configure(text=f"{os.path.basename(path)}  ({size_mb:.2f} MB)")

    def select_audio_stego(self):
        if self.is_busy: return
        path = filedialog.askopenfilename(filetypes=[
            ("Audio", "*.wav *.mp3 *.mpeg *.mpg *.m4a"), ("All", "*.*")
        ])
        if path:
            self.audio_stego_path = path
            self.audio_stego_label.configure(text=os.path.basename(path))

    # ==================== CAPACITY ====================
    def _update_capacity(self):
        self.compress_info.configure(text="")
        if not self.cover_path:
            self.capacity_label.configure(text=self.t("capacity"))
            return
        try:
            img = Image.open(self.cover_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
            w, h = img.size
            capacity = (w * h * 3) // 8 - 600
            capacity_mb = capacity / (1024 * 1024)
            msg = f"{'Capacitate' if self.lang == 'ro' else 'Capacity'}: {capacity_mb:.2f} MB"

            if self.payload_path:
                with open(self.payload_path, "rb") as f:
                    data = f.read()
                comp = zlib.compress(data, 9)
                ratio = (1 - len(comp) / len(data)) * 100 if data else 0
                self.compress_info.configure(
                    text=f"{'Dupa compresie' if self.lang == 'ro' else 'After compression'}: "
                         f"{len(comp)/(1024*1024):.2f} MB  (~{ratio:.0f}%)",
                    text_color=COLORS["text_dim"]
                )
                if len(comp) > capacity:
                    msg += "  ❌"
                    self.capacity_label.configure(text_color=COLORS["danger"])
                else:
                    msg += f"  ✓ (~{len(comp)/capacity*100:.1f}%)"
                    self.capacity_label.configure(text_color=COLORS["success"])
            else:
                self.capacity_label.configure(text_color=COLORS["text_dim"])
            self.capacity_label.configure(text=msg)
        except Exception as e:
            self.capacity_label.configure(text=f"Error: {e}", text_color=COLORS["danger"])

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
            raise ValueError("Filename too long")
        compressed = zlib.compress(original, 9)
        if len(compressed) < len(original):
            store, flags = compressed, 1
        else:
            store, flags = original, 0
        checksum = hashlib.sha256(original).digest()
        return original, filename, store, flags, checksum

    # ==================== IMAGE EMBED / EXTRACT ====================
    def start_embed_image(self):
        if self.is_busy: return
        if not self.cover_path or not self.payload_path:
            messagebox.showwarning("!", self.t("warn_missing"))
            return
        if self.output_format.get() == "jpeg":
            if not messagebox.askyesno("JPEG", self.t("warn_jpeg")):
                return
        self._set_busy(True)
        threading.Thread(target=self._embed_image_worker, daemon=True).start()

    def _embed_image_worker(self):
        try:
            self.after(0, lambda: self.status.configure(text=self.t("processing"), text_color=COLORS["accent"]))
            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.1, "..."))

            original, filename, store, flags, checksum = self._prepare_payload(self.payload_path)
            header = (MAGIC_IMG + bytes([flags]) + bytes([len(filename)]) + filename +
                      struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
            full_data = header + store

            img = Image.open(self.cover_path).convert("RGB")
            pixels = list(img.getdata())
            if len(full_data) > (len(pixels) * 3) // 8:
                self.after(0, lambda: messagebox.showerror("!", self.t("err_capacity")))
                self.after(0, lambda: self._finish_error())
                return

            bits = list(self._bytes_to_bits(full_data))
            new_pixels, bit_idx = [], 0
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
                    self.after(0, lambda v=p: self._update_progress(self.progress, self.progress_label, v, f"{int(v*100)}%"))

            stego = Image.new("RGB", img.size)
            stego.putdata(new_pixels)
            self.after(0, lambda: self._save_image(stego, original, store, flags))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self._finish_error())

    def _save_image(self, stego, original, store, flags):
        try:
            fmt = self.output_format.get()
            ext = ".png" if fmt == "png" else ".jpg"
            path = filedialog.asksaveasfilename(
                defaultextension=ext,
                filetypes=[("PNG", "*.png")] if fmt == "png" else [("JPEG", "*.jpg")],
                initialfile="stego_image" + ext
            )
            if not path:
                self.status.configure(text=self.t("status_ready"), text_color=COLORS["text_dim"])
                self._update_progress(self.progress, self.progress_label, 0, "")
                self._set_busy(False)
                return
            if fmt == "png":
                stego.save(path, "PNG")
            else:
                stego.save(path, "JPEG", quality=100)
            self._update_progress(self.progress, self.progress_label, 1.0, self.t("done"))
            self.status.configure(text=f"✓ {os.path.basename(path)}", text_color=COLORS["success"])
            messagebox.showinfo("OK", self.t("success_img"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._set_busy(False)
            self.after(2000, lambda: self._update_progress(self.progress, self.progress_label, 0, ""))

    def start_extract_image(self):
        if self.is_busy: return
        if not self.stego_path:
            messagebox.showwarning("!", self.t("warn_missing"))
            return
        self._set_busy(True)
        threading.Thread(target=self._extract_image_worker, daemon=True).start()

    def _extract_image_worker(self):
        try:
            self.after(0, lambda: self._update_progress(self.progress, self.progress_label, 0.3, "..."))
            img = Image.open(self.stego_path).convert("RGB")
            bits = []
            for r, g, b in img.getdata():
                bits.extend([r & 1, g & 1, b & 1])
            data = self._bits_to_bytes(bits)

            if data[:7] not in (b"ELBLUE2", b"ELBLUE1"):
                self.after(0, lambda: messagebox.showerror("!", self.t("not_electro")))
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
                self.after(0, lambda: messagebox.showwarning("!", self.t("checksum_warn")))

            self.after(0, lambda: self._save_extracted(name, payload, self.progress, self.progress_label))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self._finish_error())

    # ==================== AUDIO ====================
    def start_embed_audio(self):
        if self.is_busy: return
        if not self.audio_path or not self.payload_path:
            messagebox.showwarning("!", self.t("warn_missing"))
            return
        self._set_busy(True)
        threading.Thread(target=self._embed_audio_worker, daemon=True).start()

    def _embed_audio_worker(self):
        try:
            ext = os.path.splitext(self.audio_path)[1].lower()
            self.after(0, lambda: self.status.configure(text=self.t("processing"), text_color=COLORS["accent"]))
            original, filename, store, flags, checksum = self._prepare_payload(self.payload_path)

            if ext == ".wav":
                self._embed_wav(original, filename, store, flags, checksum)
            elif ext in (".mp3", ".mpeg", ".mpg", ".m4a"):
                self._embed_mp3(original, filename, store, flags, checksum)
            else:
                raise ValueError("Unsupported audio format")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self._finish_error_audio())

    def _embed_wav(self, original, filename, store, flags, checksum):
        with wave.open(self.audio_path, "rb") as wr:
            params = wr.getparams()
            frames = wr.readframes(wr.getnframes())
        header = (MAGIC_WAV + bytes([flags]) + bytes([len(filename)]) + filename +
                  struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
        full = header + store
        if len(full) * 8 > len(frames):
            self.after(0, lambda: messagebox.showerror("!", self.t("err_capacity")))
            self.after(0, lambda: self._finish_error_audio())
            return
        audio = bytearray(frames)
        for i, bit in enumerate(self._bytes_to_bits(full)):
            audio[i] = (audio[i] & 0xFE) | bit
        self.after(0, lambda: self._save_wav(params, bytes(audio)))

    def _save_wav(self, params, frames):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV", "*.wav")],
                                                initialfile="stego_audio.wav")
            if not path:
                self._finish_error_audio()
                return
            with wave.open(path, "wb") as ww:
                ww.setparams(params)
                ww.writeframes(frames)
            self._update_progress(self.audio_progress, self.audio_progress_label, 1.0, self.t("done"))
            self.status.configure(text=f"✓ {os.path.basename(path)}", text_color=COLORS["success"])
            messagebox.showinfo("OK", self.t("success_aud"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._set_busy(False)
            self.after(2000, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0, ""))

    def _embed_mp3(self, original, filename, store, flags, checksum):
        with open(self.audio_path, "rb") as f:
            mp3_data = f.read()
        header = (MAGIC_MP3 + bytes([flags]) + bytes([len(filename)]) + filename +
                  struct.pack(">Q", len(original)) + struct.pack(">Q", len(store)) + checksum)
        trailer = header + store + MAGIC_MP3 + struct.pack(">I", len(header) + len(store))
        out = mp3_data + trailer
        self.after(0, lambda: self._save_mp3(out))

    def _save_mp3(self, data):
        try:
            path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3", "*.mp3")],
                                                initialfile="stego_audio.mp3")
            if not path:
                self._finish_error_audio()
                return
            with open(path, "wb") as f:
                f.write(data)
            self._update_progress(self.audio_progress, self.audio_progress_label, 1.0, self.t("done"))
            self.status.configure(text=f"✓ {os.path.basename(path)}", text_color=COLORS["success"])
            messagebox.showinfo("OK", self.t("success_aud"))
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._set_busy(False)
            self.after(2000, lambda: self._update_progress(self.audio_progress, self.audio_progress_label, 0, ""))

    def start_extract_audio(self):
        if self.is_busy: return
        if not self.audio_stego_path:
            messagebox.showwarning("!", self.t("warn_missing"))
            return
        self._set_busy(True)
        threading.Thread(target=self._extract_audio_worker, daemon=True).start()

    def _extract_audio_worker(self):
        try:
            ext = os.path.splitext(self.audio_stego_path)[1].lower()
            if ext == ".wav":
                self._extract_wav()
            elif ext in (".mp3", ".mpeg", ".mpg", ".m4a"):
                self._extract_mp3()
            else:
                raise ValueError("Unsupported format")
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
            self.after(0, lambda: self._finish_error_audio())

    def _extract_wav(self):
        with wave.open(self.audio_stego_path, "rb") as wr:
            frames = wr.readframes(wr.getnframes())
        data = self._bits_to_bytes([(b & 1) for b in frames])
        if data[:7] != MAGIC_WAV:
            self.after(0, lambda: messagebox.showerror("!", self.t("not_electro")))
            self.after(0, lambda: self._finish_error_audio())
            return
        flags, nlen = data[7], data[8]
        name = data[9:9+nlen].decode("utf-8")
        ssize = struct.unpack(">Q", data[17+nlen:25+nlen])[0]
        checksum = data[25+nlen:57+nlen]
        stored = data[57+nlen:57+nlen+ssize]
        payload = zlib.decompress(stored) if flags & 1 else stored
        if hashlib.sha256(payload).digest() != checksum:
            self.after(0, lambda: messagebox.showwarning("!", self.t("checksum_warn")))
        self.after(0, lambda: self._save_extracted(name, payload, self.audio_progress, self.audio_progress_label))

    def _extract_mp3(self):
        with open(self.audio_stego_path, "rb") as f:
            data = f.read()
        idx = data.rfind(MAGIC_MP3)
        if idx == -1 or idx + 11 > len(data):
            self.after(0, lambda: messagebox.showerror("!", self.t("not_electro")))
            self.after(0, lambda: self._finish_error_audio())
            return
        size = struct.unpack(">I", data[idx+7:idx+11])[0]
        start = idx - size
        if start < 0:
            raise ValueError("Corrupt data")
        block = data[start:idx]
        if block[:7] != MAGIC_MP3:
            raise ValueError("Invalid header")
        flags, nlen = block[7], block[8]
        name = block[9:9+nlen].decode("utf-8")
        ssize = struct.unpack(">Q", block[17+nlen:25+nlen])[0]
        checksum = block[25+nlen:57+nlen]
        stored = block[57+nlen:57+nlen+ssize]
        payload = zlib.decompress(stored) if flags & 1 else stored
        if hashlib.sha256(payload).digest() != checksum:
            self.after(0, lambda: messagebox.showwarning("!", self.t("checksum_warn")))
        self.after(0, lambda: self._save_extracted(name, payload, self.audio_progress, self.audio_progress_label))

    def _save_extracted(self, filename, payload, bar, label):
        try:
            path = filedialog.asksaveasfilename(initialfile=filename, filetypes=[("All", "*.*")])
            if not path:
                self.status.configure(text=self.t("status_ready"), text_color=COLORS["text_dim"])
                self._update_progress(bar, label, 0, "")
                self._set_busy(False)
                return
            with open(path, "wb") as f:
                f.write(payload)
            self._update_progress(bar, label, 1.0, self.t("done"))
            self.status.configure(text=f"✓ {filename} ({len(payload):,} B)", text_color=COLORS["success"])
            messagebox.showinfo("OK", f"{filename}\n{len(payload):,} bytes")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self._set_busy(False)
            self.after(2000, lambda: self._update_progress(bar, label, 0, ""))

    def _finish_error(self):
        self.status.configure(text="Error", text_color=COLORS["danger"])
        self._update_progress(self.progress, self.progress_label, 0, "")
        self._set_busy(False)

    def _finish_error_audio(self):
        self.status.configure(text="Error", text_color=COLORS["danger"])
        self._update_progress(self.audio_progress, self.audio_progress_label, 0, "")
        self._set_busy(False)


if __name__ == "__main__":
    app = ElectroBlueStego()
    app.mainloop()
    
