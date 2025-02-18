import os
import re
import tkinter as tk
from tkinter import filedialog, ttk, font as tkFont, messagebox


class Notepad:
    def __init__(self):
        # Initialize the main application window
        self.root = tk.Tk()
        self.root.title("*Notepad - Untitled")
        self.root.geometry("800x600")

        # Set the icon for the application window
        icon_path = os.path.join(os.path.dirname(__file__), "notepad.ico")
        self.root.wm_iconbitmap(icon_path)

        # Set the program icon
        icon_image = tk.PhotoImage(file=os.path.join(
            os.path.dirname(__file__), "notepad.png"))
        self.root.iconphoto(True, icon_image)

        # Initialize the text area and other UI components
        self.text_space = None
        self.status_label = None
        self.find_and_replace_window = None
        self.setup_ui()

        # Start the main event loop
        self.root.protocol("WM_DELETE_WINDOW", self.on_program_close)
        self.root.mainloop()

    def setup_ui(self):
        """Set up the user interface components."""
        # Configure the grid layout for the main window
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create the main text area
        self.text_space = tk.Text(
            self.root, wrap="word", font=("Arial", 12), undo=True)
        self.text_space.grid(row=0, column=0, sticky="nsew")
        self.text_space.focus_set()

        # Add a scrollbar to the text area
        text_scroll = ttk.Scrollbar(
            self.root, orient="vertical", command=self.text_space.yview)
        text_scroll.grid(row=0, column=1, sticky="ns")
        self.text_space.configure(yscrollcommand=text_scroll.set)

        # Create a status bar at the bottom of the window
        status_bar = tk.Frame(self.root, height=20, bd=1, relief="sunken")
        status_bar.grid(row=1, column=0, sticky="ew")

        # Add a label to the status bar to show the current line and column
        self.status_label = ttk.Label(
            status_bar, text="Line: 1, Col: 1", anchor="w")
        self.status_label.pack(fill=tk.X, padx=5)

        # Bind key and mouse events to update the status bar
        self.text_space.bind("<KeyRelease>", self.update_status_bar)
        self.text_space.bind("<ButtonRelease-1>", self.update_status_bar)

        # Create the menu bar
        self.create_menu_bar()

        # Bind keyboard shortcuts
        self.root.bind("<Control-n>", lambda event: self.new_window())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.text_space.bind("<Control-BackSpace>", self.delete_word)
        self.root.bind("<Control-f>", lambda event: self.find_and_replace())

    def create_menu_bar(self):
        """Create the menu bar and its submenus."""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Create the File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(
            label=f"{'New Window':<30}Ctrl+N", command=self.new_window)
        file_menu.add_command(
            label=f"{'Open':<38}Ctrl+O", command=self.open_file)
        file_menu.add_command(
            label=f"{'Save':<40}Ctrl+S", command=self.save_file)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Create the View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(
            label=f"{'Find & Replace':<30}Ctrl+F", command=self.find_and_replace)
        view_menu.add_command(label="Format", command=self.format_text)
        menu_bar.add_cascade(label="View", menu=view_menu)

        # Create the Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="List Shortcuts",
                              command=self.show_shortcuts)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def on_program_close(self):
        """Handle the closing of the application with unsaved changes."""
        if self.text_space.edit_modified():
            response = messagebox.askyesnocancel(
                "Notepad", "Do you want to save changes?")
            if response is None:
                return
            elif response:
                self.save_file()
        self.root.destroy()

    def delete_word(self, event):
        """Delete the word before the cursor."""
        text_widget = event.widget
        cursor_position = text_widget.index(tk.INSERT)
        start_of_line = text_widget.index(f"{cursor_position} linestart")
        text_before_cursor = text_widget.get(start_of_line, cursor_position)

        # Use regular expression to find the word before the cursor
        match = re.search(r'\S+$', text_before_cursor)

        if match:
            # If a word is found, delete from the match's start to the cursor position
            delete_start = text_widget.index(
                f"{start_of_line} + {len(text_before_cursor) - len(match.group(0))}c")
            text_widget.delete(delete_start, cursor_position)
        else:
            # If no word is found, delete the text from start of line to cursor
            text_widget.delete(start_of_line, cursor_position)

    def update_status_bar(self, event=None):
        """Update the status bar with the current line and column."""
        line, column = self.text_space.index(tk.INSERT).split(".")
        self.status_label.config(text=f"Line: {line}, Col: {column}")

    def new_window(self):
        """Open a new Notepad window."""
        Notepad()

    def save_file(self):
        """Save the current text to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "w") as file:
                    save_text = self.text_space.get(1.0, "end-1c")
                    file.write(save_text)
                self.root.title(f"Notepad - {file_path}")
                self.text_space.edit_modified(False)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def open_file(self):
        """Open a file and load its content into the text area."""
        file_path = filedialog.askopenfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
        )

        if file_path:
            try:
                with open(file_path, "r") as file:
                    self.text_space.delete(1.0, tk.END)
                    self.text_space.insert(tk.END, file.read())
                self.root.title(f"Notepad - {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def find_and_replace(self):
        """Create a Find and Replace dialog."""
        if self.find_and_replace_window and tk.Toplevel.winfo_exists(self.find_and_replace_window):
            self.find_and_replace_window.lift()
            self.find_and_replace_window.focus_force()
            self.find_entry.focus_set()
            return

        self.find_and_replace_window = tk.Toplevel()
        self.find_and_replace_window.title("Find and Replace")
        self.find_and_replace_window.resizable(False, False)
        self.find_and_replace_window.columnconfigure(0, weight=1)
        self.find_and_replace_window.columnconfigure(1, weight=1)
        self.find_and_replace_window.columnconfigure(2, weight=1)

        icon_path = os.path.join(os.path.dirname(__file__), "notepad.ico")
        self.find_and_replace_window.wm_iconbitmap(icon_path)

        style = ttk.Style(self.find_and_replace_window)
        style.theme_use("clam")

        self.find_and_replace_window.config(
            bg=style.lookup('TFrame', 'background'))

        # Create and place the Find label and entry
        find_label = ttk.Label(self.find_and_replace_window, text="Find:")
        find_label.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        self.find_entry = ttk.Entry(self.find_and_replace_window)
        self.find_entry.grid(column=1, row=0, sticky=tk.E, padx=5, pady=5)
        self.find_entry.focus_set()

        # Create and place the Replace label and entry
        replace_label = ttk.Label(
            self.find_and_replace_window, text="Replace:")
        replace_label.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        replace_entry = ttk.Entry(self.find_and_replace_window)
        replace_entry.grid(column=1, row=1, sticky=tk.E, padx=5, pady=5)

        # Create and place the Match Word checkbox
        match_word_var = tk.BooleanVar()
        match_word_check_button = ttk.Checkbutton(
            self.find_and_replace_window, text="Match Exact Word", variable=match_word_var)
        match_word_check_button.grid(
            column=2, row=1, sticky=tk.W, padx=5, pady=5)

        # Function to check if the word matches exactly
        def match_word_check(start_pos, text_to_find):
            end_pos = f"{start_pos} + {len(text_to_find)}c"
            match_text = self.text_space.get(start_pos, end_pos)
            if not (match_text == text_to_find and
                    (start_pos == "1.0" or self.text_space.get(f"{start_pos} - 1c", start_pos).isspace()) and
                    (end_pos == "end" or self.text_space.get(end_pos, f"{end_pos} + 1c").isspace())):
                return False
            return True

        # Function to bring the Find and Replace window to the front and focus on the Find entry
        def lift_and_focus():
            self.find_and_replace_window.lift()
            self.find_entry.focus_set()

        # Function to check if there is no text to find
        def no_text_found():
            text_to_find = self.find_entry.get()
            if not text_to_find:
                messagebox.showwarning("Warning", "No text to find.")
                lift_and_focus()
                return True
            if not self.text_space.search(text_to_find, "1.0", stopindex="end"):
                messagebox.showwarning(
                    "Warning", "Text not found in document.")
                lift_and_focus()
                return True
            return False

        # Function to check if there is no text to replace
        def no_text_to_replace():
            if no_text_found():
                return True
            text_to_replace = replace_entry.get()
            if not text_to_replace:
                messagebox.showwarning("Warning", "No text to replace.")
                lift_and_focus()
                return True
            return False

        # Function to find text in the document
        def find_text():
            if no_text_found():
                return
            self.text_space.tag_remove("found", "1.0", "end")
            text_to_find = self.find_entry.get()
            start_pos = "1.0"
            found = False
            while True:
                start_pos = self.text_space.search(
                    text_to_find, start_pos, stopindex="end")
                if not start_pos:
                    break
                if match_word_var.get() and not match_word_check(start_pos, text_to_find):
                    end_pos = f"{start_pos} + {len(text_to_find)}c"
                    start_pos = end_pos
                    continue
                end_pos = f"{start_pos} + {len(text_to_find)}c"
                self.text_space.tag_add("found", start_pos, end_pos)
                start_pos = end_pos
                found = True
            if not found:
                messagebox.showwarning(
                    "Warning", "Text not found in document.")
                lift_and_focus()
            self.text_space.tag_config(
                "found", background="blue", foreground="white")
            lift_and_focus()

        # Function to replace text in the document
        def replace_text():
            if no_text_to_replace():
                return
            self.text_space.tag_remove("found", "1.0", "end")
            text_to_find = self.find_entry.get()
            text_to_replace = replace_entry.get()
            start_pos = "1.0"
            while True:
                start_pos = self.text_space.search(
                    text_to_find, start_pos, stopindex="end")
                if not start_pos:
                    break
                if match_word_var.get() and not match_word_check(start_pos, text_to_find):
                    end_pos = f"{start_pos} + {len(text_to_find)}c"
                    start_pos = end_pos
                    continue
                end_pos = f"{start_pos} + {len(text_to_find)}c"
                self.text_space.delete(start_pos, end_pos)
                self.text_space.insert(start_pos, text_to_replace)
                self.text_space.tag_add(
                    "replaced", start_pos, f"{start_pos} + {len(text_to_replace)}c")
                start_pos = f"{start_pos} + {len(text_to_replace)}c"
            self.text_space.tag_config(
                "replaced", background="blue", foreground="white")
            lift_and_focus()

        # Create and place the Find and Replace buttons
        find_button = ttk.Button(
            self.find_and_replace_window, text="Find", command=find_text)
        find_button.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)

        replace_button = ttk.Button(
            self.find_and_replace_window, text="Replace", command=replace_text)
        replace_button.grid(column=1, row=2, sticky=tk.EW, padx=5, pady=5)

        # Bind Enter key to Find and Shift+Enter to Replace
        self.find_entry.bind("<Return>", lambda event: find_text())
        replace_entry.bind("<Shift-Return>", lambda event: replace_text())

        # Function to handle the closing of the Find and Replace window
        def on_close():
            if self.text_space.tag_ranges("found"):
                self.text_space.tag_remove("found", "1.0", "end")
            if self.text_space.tag_ranges("replaced"):
                self.text_space.tag_remove("replaced", "1.0", "end")
            self.find_and_replace_window.destroy()

        self.find_and_replace_window.protocol("WM_DELETE_WINDOW", on_close)

    def format_text(self):
        """Format the text in the document."""
        def update_preview():
            selected_font = font_combo.get()
            selected_size = int(size_combo.get())
            preview_pane.config(font=(selected_font, selected_size))

        def apply_formatting():
            selected_font = font_combo.get()
            selected_size = int(size_combo.get())
            self.text_space.config(font=(selected_font, selected_size))
            format_window.destroy()

        # Create the Format Text window
        format_window = tk.Toplevel()
        format_window.title("Format Text")
        format_window.resizable(False, False)
        format_window.columnconfigure(0, weight=1)
        format_window.columnconfigure(1, weight=1)

        icon_path = os.path.join(os.path.dirname(__file__), "notepad.ico")
        format_window.wm_iconbitmap(icon_path)

        # Create and place the font selection combo box
        font_combo = ttk.Combobox(
            format_window, state="readonly", values=sorted(tkFont.families()))
        font_combo.set("Arial")
        font_combo.grid(column=0, row=0, sticky=tk.W, padx=5, pady=5)

        # Create and place the font size selection combo box
        size_combo = ttk.Combobox(
            format_window, state="readonly", values=list(range(8, 41, 2)))
        size_combo.set(12)
        size_combo.grid(column=0, row=1, sticky=tk.W, padx=5, pady=5)

        # Create and place the preview pane
        preview_frame = tk.Frame(format_window, width=300, height=100)
        preview_frame.grid(column=1, row=0, rowspan=3,
                           sticky=tk.E, padx=5, pady=5)
        preview_frame.pack_propagate(False)

        preview_pane = tk.Text(preview_frame, wrap="word", font=("Arial", 12))
        preview_pane.insert(tk.END, "Hello World!")
        preview_pane.config(state="disabled")
        preview_pane.pack(fill=tk.BOTH, expand=True)

        # Bind events to update the preview pane
        font_combo.bind("<<ComboboxSelected>>", lambda event: update_preview())
        size_combo.bind("<<ComboboxSelected>>", lambda event: update_preview())

        # Create and place the Apply button
        apply_button = ttk.Button(
            format_window, text="Apply", command=apply_formatting)
        apply_button.grid(column=0, row=2, sticky=tk.EW, padx=5, pady=5)

    def show_about(self):
        """Show the About dialog."""
        about_window = tk.Toplevel()
        about_window.title("About Notepad")
        about_window.resizable(False, False)

        icon_path = os.path.join(os.path.dirname(__file__), "notepad.ico")
        about_window.wm_iconbitmap(icon_path)

        style = ttk.Style(about_window)
        style.theme_use("clam")

        about_window.config(bg=style.lookup('TFrame', 'background'))

        # Add the About text
        about_text = (
            "Notepad by vanitas-kh\n\n"
            "Version: 1.0\n\n"
            "Description: A simple functional text editor.\n\n"
            "Contact: For more information, visit https://github.com/vanitas-kh/notepad\n\n"
            "License: This software is licensed under the MIT License.\n\n"
            "Acknowledgements: Thanks to the open-source community for their contributions."
        )
        about_label = ttk.Label(
            about_window, text=about_text, justify="left", padding=10)
        about_label.pack()

        # Add a Close button
        close_button = ttk.Button(
            about_window, text="Close", command=about_window.destroy)
        close_button.pack(pady=5)

    def show_shortcuts(self):
        """Show the Shortcuts dialog."""
        shortcuts_window = tk.Toplevel()
        shortcuts_window.title("List of Shortcuts")
        shortcuts_window.resizable(False, False)

        icon_path = os.path.join(os.path.dirname(__file__), "notepad.ico")
        shortcuts_window.wm_iconbitmap(icon_path)

        style = ttk.Style(shortcuts_window)
        style.theme_use("clam")

        shortcuts_window.config(bg=style.lookup('TFrame', 'background'))

        # Add the Shortcuts text
        shortcuts_text = (
            "Shortcuts:\n\n"
            "Ctrl+N\t\t - New Window\n"
            "Ctrl+O\t\t - Open\n"
            "Ctrl+S\t\t - Save\n"
            "Ctrl+Z\t\t - Undo\n"
            "Ctrl+Backspace\t - Delete word\n"
        )
        shortcuts_label = ttk.Label(
            shortcuts_window, text=shortcuts_text, justify="left", padding=10)
        shortcuts_label.pack()

        # Add a Close button
        close_button = ttk.Button(
            shortcuts_window, text="Close", command=shortcuts_window.destroy)
        close_button.pack(pady=5)

        return None


if __name__ == "__main__":
    Notepad()
