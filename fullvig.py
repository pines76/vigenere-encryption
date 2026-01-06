import tkinter as tk
from tkinter import font
import random

# ---------- VIGENERE LOGIC ----------
def vigenere_cipher(text, key, decrypt=False):
    result = []
    key = key.lower()
    key_index = 0

    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            k = ord(key[key_index % len(key)]) - ord('a')
            if decrypt:
                k = -k
            shifted = (ord(char) - base + k) % 26 + base
            result.append(chr(shifted))
            key_index += 1
        else:
            result.append(char)

    return "".join(result)


# ---------- TERMINAL APP ----------
class RetroVigenereTerminal:
    def __init__(self, root):
        self.root = root
        self.key = "KEY"
        self.theme = 'RED'
        self.cursor_visible = True

        # ---- ROOT WINDOW ----
        root.title("RETRO VIGENERE TERMINAL")
        root.configure(bg="black")
        root.attributes("-fullscreen", True)

        # ---- FONT ----
        self.font = font.Font(family="Courier", size=14)

        # ---- CRT OVERLAY (SCANLINES) ----
        self.overlay = tk.Canvas(
            root,
            bg="black",
            highlightthickness=0
        )
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        # ---- MAIN TEXT TERMINAL ----
        self.text = tk.Text(
            root,
            bg="black",
            fg="#ff3333",
            insertbackground="#ff3333",
            font=self.font,
            borderwidth=0,
            highlightthickness=0,
            wrap="word"
        )
        self.text.pack(fill="both", expand=True)
        self.text.focus_set()

        # ---- CRT EFFECTS ----
        self.draw_scanlines()
        self.flicker()

        # ---- BOOT SCREEN ----
        self.boot_screen()
        self.text.insert("end", "> ")

        # ---- BLINKING BLOCK CURSOR ----
        self.blink_cursor()

        # ---- KEY BINDINGS ----
        self.text.bind("<Return>", self.process_command)
        self.text.bind("<Escape>", lambda e: root.destroy())

    # ---------- BOOT SCREEN ----------
    def boot_screen(self):
        self.header = (
            "RETRO VIGENERE ENCRYPTION SYSTEM v1.0\n"
            "------------------------------------\n"
            "MODE: TERMINAL\n"
            "DISPLAY: CRT\n\n"
            "COMMANDS:\n"
            " KEY <word>    SET ENCRYPTION KEY\n"
            " ENC <text>    ENCRYPT\n"
            " DEC <text>    DECRYPT\n"
            " THEME <color> CHANGE THEME (RED/GREEN/AMBER)\n"
            " CLEAR         CLEAR OUTPUT\n"
            " ESC           EXIT\n\n"
            f"CURRENT KEY: {self.key}\n\n"
        )
        self.text.insert("end", self.header)

    # ---------- COMMAND HANDLER ----------
    def process_command(self, event):
        line_start = self.text.index("insert linestart")
        line_end = self.text.index("insert lineend")
        command = self.text.get(line_start, line_end).strip()

        if command.startswith(">"):
            command = command[1:].strip()

        self.text.insert("end", "\n")
        cmd_upper = command.upper()

        def insert_prompt():
            self.text.insert("end", "> ")
            self.text.see("end")

        # ---- SET KEY ----
        if cmd_upper.startswith("KEY "):
            new_key = command.split(maxsplit=1)[1]
            if new_key.isalpha():
                self.key = new_key
                self.type_write(f"KEY SET TO: {self.key}", callback=insert_prompt)
            else:
                self.type_write("ERROR: KEY MUST CONTAIN LETTERS ONLY", callback=insert_prompt)

        # ---- ENCRYPT ----
        elif cmd_upper.startswith("ENC "):
            encrypted = vigenere_cipher(command[4:], self.key)
            self.type_write(f"ENCRYPTED: {encrypted}", callback=insert_prompt)

        # ---- DECRYPT ----
        elif cmd_upper.startswith("DEC "):
            decrypted = vigenere_cipher(command[4:], self.key, decrypt=True)
            self.type_write(f"DECRYPTED: {decrypted}", callback=insert_prompt)

        # ---- THEME ----
        elif cmd_upper.startswith("THEME "):
            color = command.split()[1].upper()
            if color in ['RED', 'GREEN', 'AMBER']:
                self.theme = color
                self.apply_theme()
                self.type_write(f"THEME CHANGED TO {color}", callback=insert_prompt)
            else:
                self.type_write("UNKNOWN THEME", callback=insert_prompt)

        # ---- CLEAR ----
        elif cmd_upper == "CLEAR":
            self.text.delete("1.0", "end")
            self.text.insert("end", self.header)
            self.text.insert("end", "> ")

        else:
            self.type_write("UNKNOWN COMMAND", callback=insert_prompt)

        return "break"

    # ---------- TYPING EFFECT ----------
    def type_write(self, message, delay=25, callback=None):
        self.message_chars = list(message + "\n")
        self._type_next_char(delay, callback)

    def _type_next_char(self, delay, callback):
        if self.message_chars:
            self.text.insert("end", self.message_chars.pop(0))
            self.text.see("end")
            self.root.after(delay, lambda: self._type_next_char(delay, callback))
        else:
            if callback:
                callback()

    # ---------- THEME HANDLING ----------
    def apply_theme(self):
        if self.theme == 'RED':
            fg = "#ff3333"
            scanline = "#110000"
        elif self.theme == 'GREEN':
            fg = "#33ff33"
            scanline = "#001100"
        elif self.theme == 'AMBER':
            fg = "#ffcc33"
            scanline = "#331a00"

        self.text.config(fg=fg, insertbackground=fg)
        self.overlay.delete("scanline")
        width = self.root.winfo_screenwidth()
        height = self.root.winfo_screenheight()
        for y in range(0, height, 3):
            self.overlay.create_line(
                0, y, width, y,
                fill=scanline,
                tags="scanline"
            )

    # ---------- CRT SCANLINES ----------
    def draw_scanlines(self):
        self.apply_theme()

    # ---------- CRT FLICKER ----------
    def flicker(self):
        if self.theme == 'RED':
            intensity = random.choice(["#ff3333", "#ff2222", "#ff4444"])
        elif self.theme == 'GREEN':
            intensity = random.choice(["#33ff33", "#22ff22", "#44ff44"])
        elif self.theme == 'AMBER':
            intensity = random.choice(["#ffcc33", "#e6b22c", "#ffdd44"])
        self.text.config(fg=intensity, insertbackground=intensity)
        self.root.after(random.randint(80, 160), self.flicker)

    # ---------- BLINKING BLOCK CURSOR ----------
    def blink_cursor(self):
        if self.cursor_visible:
            self.text.config(insertwidth=14)
            self.cursor_visible = False
        else:
            self.text.config(insertwidth=0)
            self.cursor_visible = True
        self.root.after(500, self.blink_cursor)


# ---------- RUN ----------
if __name__ == "__main__":
    root = tk.Tk()
    app = RetroVigenereTerminal(root)
    root.mainloop()
