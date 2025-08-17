import tkinter
import tkinter.messagebox
import customtkinter
import os
import tkinter.filedialog
import json
import threading
from pdf_processor import PDFProcessor

class PDFProcessingThread(threading.Thread):
    def __init__(self, pdf_processor_instance, status_callback, input_pdf_folder, summary_update_callback):
        super().__init__()
        self.pdf_processor = pdf_processor_instance
        self.status_callback = status_callback
        self.input_pdf_folder = input_pdf_folder
        self.summary_update_callback = summary_update_callback

    def run(self):
        self.status_callback(f"Starting PDF processing from: {self.input_pdf_folder}...")
        
        try:
            all_files = os.listdir(self.input_pdf_folder)
            pdf_files_to_process = [f for f in all_files if f.lower().endswith('.pdf')]
        except FileNotFoundError:
            self.status_callback(f"Error: Input folder '{self.input_pdf_folder}' not found.")
            tkinter.messagebox.showerror("Folder Error", f"Input folder '{self.input_pdf_folder}' not found.")
            self.summary_update_callback() # Update summary even on error
            return
        except Exception as e:
            self.status_callback(f"Error listing files in input folder: {e}")
            tkinter.messagebox.showerror("File Listing Error", f"Error listing files: {e}")
            self.summary_update_callback() # Update summary even on error
            return

        if not pdf_files_to_process:
            self.status_callback(f"No PDF files found in '{self.input_pdf_folder}'.")
            self.status_callback("Processing complete.")
            self.summary_update_callback() # Update summary
            return

        self.status_callback(f"Found {len(pdf_files_to_process)} PDF files to process.")
        
        processed_count = 0
        no_text_count = 0
        failed_count = 0
        total_files = len(pdf_files_to_process)

        for i, item in enumerate(pdf_files_to_process):
            pdf_path = os.path.join(self.input_pdf_folder, item)
            self.status_callback(f"Processing file {i+1}/{total_files}: {item}")
            
            result_tuple = self.pdf_processor.process_pdf(pdf_path)
            
            status_type = result_tuple[0]
            
            if status_type == "success":
                processed_count += 1
            elif status_type == "no_text":
                no_text_count += 1
            elif status_type == "failed" or status_type == "failed_archive":
                failed_count += 1
        
        self.status_callback("\n--- Processing Complete ---")
        self.status_callback(f"Total Files Processed: {total_files}")
        self.status_callback(f"Successfully Extracted Text: {processed_count} files (Text to '{self.pdf_processor.output_text_folder}')")
        self.status_callback(f"No Text Extracted: {no_text_count} files (Text logs to '{self.pdf_processor.failed_text_extraction_folder}')")
        self.status_callback(f"Failed to Process: {failed_count} files (Error logs to '{self.pdf_processor.failed_text_extraction_folder}')")
        self.status_callback(f"All original PDFs moved to: '{self.pdf_processor.archive_folder}' (if successful)")
        self.status_callback("---------------------------")
        self.summary_update_callback(total_files, processed_count, no_text_count, failed_count) # Update summary after processing

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Processor")
        self.geometry(f"{800}x{600}")

        self._initialized = False # Flag to indicate if GUI is fully initialized

        # Configure grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=0) # Folder paths row
        self.grid_rowconfigure(1, weight=1) # Status textbox row
        self.grid_rowconfigure(2, weight=0) # Process button row
        self.grid_rowconfigure(3, weight=0) # Settings button row
        self.grid_rowconfigure(4, weight=1) # Summary display row

        # --- Status Textbox ---
        self.status_textbox = customtkinter.CTkTextbox(self, width=700, height=300)
        self.status_textbox.grid(row=1, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")
        self.status_textbox.insert("end", "GUI initialized. Ready to process PDFs.\n")
        self.status_textbox.configure(state="disabled")

        # --- Summary Textbox ---
        self.summary_textbox = customtkinter.CTkTextbox(self, width=700, height=200)
        self.summary_textbox.grid(row=4, column=0, columnspan=2, padx=20, pady=(10, 20), sticky="nsew")
        self.summary_textbox.insert("end", "Summary will be displayed here after processing.\n")
        self.summary_textbox.configure(state="disabled")

        # --- Folder Paths Display ---
        self.folder_frame = customtkinter.CTkFrame(self)
        self.folder_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        self.folder_frame.grid_columnconfigure(1, weight=1)

        self.input_pdf_folder = "Rightfax folder"
        self.output_text_folder = "CPRS documents for provider to sign"
        self.archive_folder = "PDF files to be archived in vistaimaging"
        self.failed_text_extraction_folder = "failed text extraction folder"

        customtkinter.CTkLabel(self.folder_frame, text="Input Folder:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.input_pdf_folder).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Output Text Folder:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.output_text_folder).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Archive Folder:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.archive_folder).grid(row=2, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Failed Extraction Folder:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.failed_text_extraction_folder).grid(row=3, column=1, padx=5, pady=2, sticky="w")

        # --- Process Button ---
        self.process_button = customtkinter.CTkButton(self, text="Process PDFs", command=self.process_pdfs)
        self.process_button.grid(row=2, column=0, columnspan=2, padx=20, pady=(10, 5))

        # --- Settings Button ---
        self.settings_button = customtkinter.CTkButton(self, text="Settings", command=self.open_settings_window)
        self.settings_button.grid(row=3, column=0, columnspan=2, padx=20, pady=(5, 10))
        
        # Load settings
        self.load_settings()

        # --- PDF Processor Initialization ---
        try:
            self.pdf_processor = PDFProcessor(
                input_pdf_folder=self.input_pdf_folder,
                output_text_folder=self.output_text_folder,
                archive_folder=self.archive_folder,
                failed_text_extraction_folder=self.failed_text_extraction_folder,
                status_callback=self.update_status_textbox
            )
            self.update_status_textbox("PDFProcessor initialized successfully. Folders checked.")
        except Exception as e:
            error_message = f"Error initializing PDFProcessor or creating folders: {e}"
            self.update_status_textbox(error_message)
            tkinter.messagebox.showerror("Initialization Error", error_message)
            self.pdf_processor = None # Set to None to prevent further errors

        self._initialized = True # Set flag to True after all components are initialized

    def process_pdfs(self):
        if self.pdf_processor:
            self.update_status_textbox("Starting PDF processing...")
            self.process_button.configure(state="disabled") # Disable button during processing
            self.settings_button.configure(state="disabled")
            
            # Clear previous status and summary
            self.status_textbox.delete("1.0", "end")
            self.summary_textbox.delete("1.0", "end")

            processing_thread = PDFProcessingThread(
                pdf_processor_instance=self.pdf_processor,
                status_callback=self.update_status_textbox,
                input_pdf_folder=self.input_pdf_folder,
                summary_update_callback=self.update_summary_display
            )
            processing_thread.start()
            self.after(100, self.check_thread_status, processing_thread) # Start checking thread status
        else:
            tkinter.messagebox.showerror("Error", "PDFProcessor not initialized. Check settings.")

    def check_thread_status(self, thread):
        if thread.is_alive():
            self.after(100, self.check_thread_status, thread)
        else:
            self.process_button.configure(state="normal") # Re-enable button after processing
            self.settings_button.configure(state="normal")
            self.update_status_textbox("PDF processing finished.")

    def load_settings(self):
        config_file = "config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    settings = json.load(f)
                    self.input_pdf_folder = settings.get("input_pdf_folder", self.input_pdf_folder)
                    self.output_text_folder = settings.get("output_text_folder", self.output_text_folder)
                    self.archive_folder = settings.get("archive_folder", self.archive_folder)
                    self.failed_text_extraction_folder = settings.get("failed_text_extraction_folder", self.failed_text_extraction_folder)
                    self.update_folder_display()
                    self.update_status_textbox("Settings loaded from config.json.")
            except Exception as e:
                self.update_status_textbox(f"Error loading settings: {e}")
                tkinter.messagebox.showerror("Settings Error", f"Error loading settings: {e}")
        else:
            self.update_status_textbox("config.json not found. Using default folder paths.")

    def save_settings(self):
        config_file = "config.json"
        settings = {
            "input_pdf_folder": self.input_pdf_folder,
            "output_text_folder": self.output_text_folder,
            "archive_folder": self.archive_folder,
            "failed_text_extraction_folder": self.failed_text_extraction_folder,
        }
        try:
            with open(config_file, "w") as f:
                json.dump(settings, f, indent=4)
            self.update_status_textbox("Settings saved to config.json.")
        except Exception as e:
            self.update_status_textbox(f"Error saving settings: {e}")
            tkinter.messagebox.showerror("Settings Error", f"Error saving settings: {e}")

    def update_status_textbox(self, message):
        if hasattr(self, '_initialized') and self._initialized:
            self.status_textbox.configure(state="normal")
            self.status_textbox.insert("end", message + "\n")
            self.status_textbox.configure(state="disabled")
            self.status_textbox.see("end")
        else:
            # If not yet initialized, print to console or log
            print(f"[GUI Init] {message}")

    def update_summary_display(self, total_files=0, processed_count=0, no_text_count=0, failed_count=0):
        self.summary_textbox.configure(state="normal")
        self.summary_textbox.delete("1.0", "end")
        
        summary_text = "--- Processing Summary ---\n"
        summary_text += f"Total Files Processed: {total_files}\n"
        summary_text += f"Successfully Extracted Text: {processed_count} files\n"
        summary_text += f"No Text Extracted: {no_text_count} files\n"
        summary_text += f"Failed to Process: {failed_count} files\n"
        summary_text += "---------------------------\n"

        self.summary_textbox.insert("end", summary_text)
        self.summary_textbox.configure(state="disabled")

    def update_folder_display(self):
        # Update the labels in the folder_frame
        for widget in self.folder_frame.winfo_children():
            widget.destroy() # Clear existing labels

        customtkinter.CTkLabel(self.folder_frame, text="Input Folder:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.input_pdf_folder).grid(row=0, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Output Text Folder:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.output_text_folder).grid(row=1, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Archive Folder:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.archive_folder).grid(row=2, column=1, padx=5, pady=2, sticky="w")

        customtkinter.CTkLabel(self.folder_frame, text="Failed Extraction Folder:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        customtkinter.CTkLabel(self.folder_frame, text=self.failed_text_extraction_folder).grid(row=3, column=1, padx=5, pady=2, sticky="w")

    def open_settings_window(self):
        if not hasattr(self, "settings_window") or self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsWindow(self)
            self.settings_window.focus()
        else:
            self.settings_window.focus()

class SettingsWindow(customtkinter.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Settings")
        self.geometry("600x400")
        self.transient(self.master) # Make it appear on top of the main window
        self.grab_set() # Make it modal

        self.grid_columnconfigure(1, weight=1)

        self.entries = {}
        self.create_setting_row("Input PDF Folder:", "input_pdf_folder", 0)
        self.create_setting_row("Output Text Folder:", "output_text_folder", 1)
        self.create_setting_row("Archive Folder:", "archive_folder", 2)
        self.create_setting_row("Failed Extraction Folder:", "failed_text_extraction_folder", 3)

        # Save and Cancel buttons
        self.save_button = customtkinter.CTkButton(self, text="Save", command=self.save_and_close)
        self.save_button.grid(row=4, column=0, padx=10, pady=20)

        self.cancel_button = customtkinter.CTkButton(self, text="Cancel", command=self.destroy)
        self.cancel_button.grid(row=4, column=1, padx=10, pady=20)

    def create_setting_row(self, label_text, key, row_num):
        customtkinter.CTkLabel(self, text=label_text).grid(row=row_num, column=0, padx=10, pady=10, sticky="w")
        
        entry = customtkinter.CTkEntry(self, width=350)
        entry.grid(row=row_num, column=1, padx=10, pady=10, sticky="ew")
        entry.insert(0, getattr(self.master, key)) # Populate with current value
        self.entries[key] = entry

        browse_button = customtkinter.CTkButton(self, text="Browse", command=lambda: self.browse_folder(key))
        browse_button.grid(row=row_num, column=2, padx=10, pady=10)

    def browse_folder(self, key):
        initial_dir = self.entries[key].get()
        if not os.path.isdir(initial_dir):
            initial_dir = os.getcwd() # Fallback to current working directory

        folder_selected = tkinter.filedialog.askdirectory(initialdir=initial_dir)
        if folder_selected:
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, folder_selected)

    def save_and_close(self):
        # Update master's folder paths
        self.master.input_pdf_folder = self.entries["input_pdf_folder"].get()
        self.master.output_text_folder = self.entries["output_text_folder"].get()
        self.master.archive_folder = self.entries["archive_folder"].get()
        self.master.failed_text_extraction_folder = self.entries["failed_text_extraction_folder"].get()
        
        # Update the main window's displayed paths
        self.master.update_folder_display()
        
        # Save settings to file
        self.master.save_settings()

        # Re-initialize PDFProcessor with new paths
        try:
            self.master.pdf_processor = PDFProcessor(
                input_pdf_folder=self.master.input_pdf_folder,
                output_text_folder=self.master.output_text_folder,
                archive_folder=self.master.archive_folder,
                failed_text_extraction_folder=self.master.failed_text_extraction_folder,
                status_callback=self.master.update_status_textbox
            )
            self.master.update_status_textbox("PDFProcessor re-initialized with new settings.")
        except Exception as e:
            error_message = f"Error re-initializing PDFProcessor with new settings: {e}"
            self.master.update_status_textbox(error_message)
            tkinter.messagebox.showerror("Initialization Error", error_message)
            self.master.pdf_processor = None

        self.destroy() # Close the settings window

if __name__ == "__main__":
    app = App()
    app.mainloop()