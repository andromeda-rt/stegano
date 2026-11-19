# ElectroBlue Stego

**Educational steganography tool** — hide any file (PDF, EXE, APK, ZIP, documents…) inside images and audio.

Built with **Python + CustomTkinter**  
Author: **[AndromedaHK](https://github.com/andromeda-rt)** (`andromeda-rt`)

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
![Version](https://img.shields.io/badge/Version-1.3-cyan)

---

## What is this?

**Steganography** is the practice of hiding data inside other data so that the presence of the secret is not obvious.

ElectroBlue Stego lets you embed almost any file into:

| Carrier | Method | Result |
|---------|--------|--------|
| **PNG image** | LSB (Least Significant Bit) on RGB | Lossless, recommended |
| **JPEG image** | LSB then save as JPEG | Possible, but risky (compression can destroy data) |
| **WAV audio** | LSB on PCM samples | Real steganography, high capacity |
| **MP3 / MPEG Audio** | Payload appended at the end of the file | File stays fully playable |

The carrier (image or song) looks and plays normally. Only someone who knows the tool (and has the file) can extract the hidden content.

---

## What can you hide?

- **PDF** documents  
- **EXE / APK**  
- **ZIP** (and other archives)  
- Office files, text, or basically **any binary file**

The app automatically compresses the payload (zlib) when it helps, then stores the smaller version.

---

## How it works

### 1. Prepare the secret file
1. Read the file
2. Compress it with zlib (level 9)
3. Keep whichever is smaller (compressed or original)
4. Build a small header:
   - Magic signature (`ELBLUE2` / `ELBAUD1` / `ELBMP3!`)
   - Flags (compressed or not)
   - Original filename
   - Sizes + **SHA-256** checksum of the original data

### 2. Hide it

**Images (PNG / JPEG)**  
Each bit of the header + payload is written into the least significant bit of the R, G and B channels of the image. The human eye cannot see the difference.

**WAV**  
Same idea applied to the raw audio samples (LSB).

**MP3 / MPEG Audio**  
The payload is **appended** after the audio data. Almost all players and apps ignore trailing bytes, so the music still plays. This is a practical technique (not classic in-frame steganography).

### 3. Extract
1. Detect the magic signature
2. Read the header
3. Decompress if needed
4. Verify SHA-256
5. Restore the original file with its original name

---

## Features

- Modern **Electro Blue** dark theme
- Real-time capacity estimation + compression ratio
- Progress bar for long operations
- Automatic compression
- Integrity check (SHA-256)
- Clear warnings about WhatsApp / social media compression
- One-click Windows `.exe` build (`build.bat`)

---

## Important warnings

### WhatsApp & messaging apps
If you send the stego file as a normal **photo** or **voice note**, the platform recompresses it and **destroys** the hidden data.

**Always send it as a Document** (📎 → Document).

### JPEG
Even at quality 100, JPEG is lossy. Prefer **PNG** whenever possible.

### MP3 / MPEG
The method used is payload-append. The audio remains playable; extraction works as long as the file is not re-encoded.

---

## Installation & Usage

### Run from source
```bash
pip install -r requirements.txt
python stego_app.py
```

### Build single .exe (Windows)
Double-click **`build.bat`**  
or:

```bash
pip install customtkinter Pillow pyinstaller
pyinstaller --onefile --windowed --name "ElectroBlueStego" stego_app.py
```

Output: `dist/ElectroBlueStego.exe`

---

## Requirements

- Python 3.10+
- `customtkinter`
- `Pillow`
- `pyinstaller` (only for building)

---

## Project structure

```
ElectroBlueStego/
├── stego_app.py      # Main application
├── requirements.txt
├── build.bat         # One-click build
└── README.md
```

---

## Disclaimer

This project is intended for **educational and research purposes**.  
The author is not responsible for misuse.

---

## Author

**AndromedaHK**  
GitHub: [github.com/andromeda-rt](https://github.com/andromeda-rt)

---

## License

MIT License
