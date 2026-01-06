#!/usr/bin/env python3
"""
Vigenère Cipher Tool
GUI: Tkinter
Background color: #1d1d1d
Foreground / controls: #b3b3b3

Save as vigenere_tool.py and run with: python3 vigenere_tool.py
No external dependencies (uses Python standard library)
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import sys

# Colors
BG = "#1d1d1d"
FG = "#b3b3b3"
ENTRY_BG = "#1d1d1d"
ENTRY_FG = "#b3b3b3"
BUTTON_BG = "#1d1d1d"
BUTTON_FG = "#b3b3b3"

# Utility: keep letters only for shifts but preserve non-letters in output

def _shift_char(c, k, encrypt=True):
    """Shift a single alphabetical character c by key character k.
    Preserves case. k is assumed to be alphabetical.
    """
    if not c.isalpha():
        return c
    base = ord('A') if c.isupper() else ord('a')
    c_idx = ord(c.upper()) - ord('A')
    k_idx = ord(k.upper()) - ord('A')
    if encrypt:
        res_idx = (c_idx + k_idx) % 26
    else:
        res_idx = (c_idx - k_idx) % 26
    return chr(base + res_idx)


def vigenere_process(text, key, encrypt=True):
    """Encrypt or decrypt text using Vigenère with the given key.
    Non-letter characters are preserved. Key is repeated over letters only.
    """
    if not key:
        raise ValueError("Key must not be empty")
    # Filter key to letters only; if none, error
    key_letters = ''.join([c for c in key if c.isalpha()])
    if not key_letters:
        raise ValueError("Key must contain at least one alphabetical character")
    result_chars = []
    ki = 0
    klen = len(key_letters)
    for ch in text:
        if ch.isalpha():
            kch = key_letters[ki % klen]
            result_chars.append(_shift_char(ch, kch, encrypt))
            ki += 1
        else:
            result_chars.append(ch)
    return ''.join(result_chars)


class VigenereApp:
    def __init__(self, root):
        self.root = root
        root.title('Vigenère Cipher Tool')
        root.configure(bg=BG)

        # Use a monospace-like font for clarity
        default_font = ('FreeMono', 11)

        # Key frame
        key_frame = tk.Frame(root, bg=BG)
        key_frame.pack(fill='x', padx=12, pady=(12, 6))

        tk.Label(key_frame, text='Key:', bg=BG, fg=FG, font=default_font).pack(side='left')
        self.key_entry = tk.Entry(key_frame, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG, font=default_font)
        self.key_entry.pack(side='left', fill='x', expand=True, padx=(6, 6))

        tk.Button(key_frame, text='Generate Simple Key', command=self._generate_key, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='right')

        # Input text
        tk.Label(root, text='Input:', bg=BG, fg=FG, anchor='w', font=default_font).pack(fill='x', padx=12)
        self.input_text = scrolledtext.ScrolledText(root, height=10, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG, font=default_font)
        self.input_text.pack(fill='both', padx=12, pady=(6, 12), expand=False)

        # Controls
        ctrl_frame = tk.Frame(root, bg=BG)
        ctrl_frame.pack(fill='x', padx=12)

        self.encrypt_btn = tk.Button(ctrl_frame, text='Encrypt →', command=self.encrypt, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font)
        self.encrypt_btn.pack(side='left')

        self.decrypt_btn = tk.Button(ctrl_frame, text='← Decrypt', command=self.decrypt, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font)
        self.decrypt_btn.pack(side='left', padx=(6, 0))

        tk.Button(ctrl_frame, text='Clear', command=self.clear_all, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='right')

        tk.Button(ctrl_frame, text='Load File', command=self.load_file, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='right', padx=(6, 0))
        tk.Button(ctrl_frame, text='Save Result', command=self.save_result, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='right', padx=(6, 0))

        # Output
        tk.Label(root, text='Result:', bg=BG, fg=FG, anchor='w', font=default_font).pack(fill='x', padx=12, pady=(12, 0))
        self.output_text = scrolledtext.ScrolledText(root, height=10, bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=FG, font=default_font)
        self.output_text.pack(fill='both', padx=12, pady=(6, 12), expand=False)

        # Bottom row: copy and about
        bottom = tk.Frame(root, bg=BG)
        bottom.pack(fill='x', padx=12, pady=(0, 12))
        tk.Button(bottom, text='Copy Result', command=self.copy_result, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='left')
        tk.Button(bottom, text='About', command=self.show_about, bg=BUTTON_BG, fg=BUTTON_FG, font=default_font).pack(side='right')

        # Make window a comfortable minimum size
        root.minsize(640, 560)

    def _generate_key(self):
        # Simple convenience: generate a key from the input length using a repeated word
        sample = 'VIGENERE'
        in_text = self.input_text.get('1.0', 'end-1c')
        if not in_text:
            messagebox.showinfo('Generate Key', 'Put some input text first, or enter a custom key.')
            return
        letters_count = sum(1 for c in in_text if c.isalpha())
        if letters_count == 0:
            messagebox.showinfo('Generate Key', 'No alphabetical characters found in input to guide key length.')
            return
        # Repeat sample to cover letters_count
        times = max(1, (letters_count // len(sample)) + 1)
        key = (sample * times)[:max(1, letters_count)]
        self.key_entry.delete(0, 'end')
        self.key_entry.insert(0, key)

    def encrypt(self):
        text = self.input_text.get('1.0', 'end-1c')
        key = self.key_entry.get()
        try:
            res = vigenere_process(text, key, encrypt=True)
        except ValueError as e:
            messagebox.showerror('Error', str(e))
            return
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', res)

    def decrypt(self):
        text = self.input_text.get('1.0', 'end-1c')
        key = self.key_entry.get()
        try:
            res = vigenere_process(text, key, encrypt=False)
        except ValueError as e:
            messagebox.showerror('Error', str(e))
            return
        self.output_text.delete('1.0', 'end')
        self.output_text.insert('1.0', res)

    def clear_all(self):
        self.input_text.delete('1.0', 'end')
        self.output_text.delete('1.0', 'end')
        self.key_entry.delete(0, 'end')

    def load_file(self):
        path = filedialog.askopenfilename(title='Open text file', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = f.read()
        except Exception as ex:
            messagebox.showerror('Error', f'Could not read file:\n{ex}')
            return
        self.input_text.delete('1.0', 'end')
        self.input_text.insert('1.0', data)

    def save_result(self):
        path = filedialog.asksaveasfilename(title='Save result as...', defaultextension='.txt', filetypes=[('Text files', '*.txt'), ('All files', '*.*')])
        if not path:
            return
        try:
            data = self.output_text.get('1.0', 'end-1c')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(data)
        except Exception as ex:
            messagebox.showerror('Error', f'Could not write file:\n{ex}')
            return
        messagebox.showinfo('Saved', f'Result saved to: {path}')

    def copy_result(self):
        res = self.output_text.get('1.0', 'end-1c')
        if not res:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(res)
        messagebox.showinfo('Copied', 'Result copied to clipboard')

    def show_about(self):
        messagebox.showinfo('About', 'Vigenère Cipher Tool\nBackground: #1d1d1d\nControls/foreground: #b3b3b3')


if __name__ == '__main__':
    root = tk.Tk()
    app = VigenereApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # Allow clean exit when run from terminal
        sys.exit(0)
