import os
import shutil
import fitz # PyMuPDF
import time

class PDFProcessor:
    def __init__(self, input_pdf_folder, output_text_folder, archive_folder, failed_text_extraction_folder, status_callback=None):
        self.input_pdf_folder = input_pdf_folder
        self.output_text_folder = output_text_folder
        self.archive_folder = archive_folder
        self.failed_text_extraction_folder = failed_text_extraction_folder
        self.status_callback = status_callback

        self._create_folders()

    def _send_status(self, message):
        if self.status_callback:
            self.status_callback(message)
        print(message)

    def _create_folders(self):
        try:
            os.makedirs(self.output_text_folder, exist_ok=True)
            os.makedirs(self.archive_folder, exist_ok=True)
            os.makedirs(self.failed_text_extraction_folder, exist_ok=True)
            self._send_status(f"Ensured output folder '{self.output_text_folder}' exists.")
            self._send_status(f"Ensured archive folder '{self.archive_folder}' exists.")
            self._send_status(f"Ensured failed text extraction folder '{self.failed_text_extraction_folder}' exists.")
        except Exception as e:
            self._send_status(f"Error creating folders: {e}")
            raise

    def _move_file_with_retry(self, src_path, dest_path, operation="move", file_description="file"):
        max_retries = 5
        op_func = shutil.move if operation == "move" else shutil.copy2
        op_word = "moved" if operation == "move" else "copied"

        for i in range(max_retries):
            try:
                op_func(src_path, dest_path)
                self._send_status(f"Successfully {op_word} {file_description}: {os.path.basename(src_path)} to {os.path.basename(dest_path)}")
                return True
            except Exception as e:
                if i < max_retries - 1:
                    self._send_status(f"Attempt {i+1}/{max_retries} to {operation} {file_description} {os.path.basename(src_path)} failed: {e}. Retrying in 0.5 seconds...")
                    time.sleep(0.5)
                else:
                    self._send_status(f"Failed to {operation} {file_description} {os.path.basename(src_path)} after {max_retries} attempts: {e}. It remains in its original location.")
                    return False

    def process_pdf(self, pdf_path):
        base_name = os.path.basename(pdf_path)
        text_file_name = os.path.splitext(base_name)[0] + ".txt"
        
        doc = None
        result_type = "failed" # Default to failed
        error_details = ""

        self._send_status(f"Attempting to process: {base_name}")

        try:
            # Open PDF
            self._send_status(f"Opening PDF: {pdf_path}")
            doc = fitz.open(pdf_path)
            self._send_status(f"Successfully opened PDF: {base_name}")

            # Extract text
            full_text = ""
            self._send_status(f"Starting text extraction for {base_name}...")
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                full_text += page.get_text()
                self._send_status(f"Extracted text from page {page_num + 1} of {base_name}. Current text length: {len(full_text)}.")
            self._send_status(f"Finished text extraction for {base_name}. Total text length: {len(full_text)}.")

            # Determine where to save the text file and if it should be written
            should_write_text_file = True
            if not full_text.strip():
                self._send_status(f"No significant text extracted from {base_name}.")
                result_type = "no_text"
                should_write_text_file = False
                target_text_folder = None # No text file to write
            else:
                self._send_status(f"Text extracted from {base_name}. Text file will go to output folder.")
                target_text_folder = self.output_text_folder
                result_type = "success"

            if should_write_text_file:
                target_text_file_path = os.path.join(target_text_folder, text_file_name)

                # Write text to file
                self._send_status(f"Attempting to write text to: {os.path.basename(target_text_file_path)}")
                try:
                    with open(target_text_file_path, "w", encoding="utf-8") as text_file:
                        text_file.write(full_text)
                    self._send_status(f"Successfully wrote text to: {os.path.basename(target_text_file_path)}")
                except Exception as write_e:
                    self._send_status(f"Error writing text file {os.path.basename(target_text_file_path)}: {write_e}")
                    result_type = "failed"
                    error_details = str(write_e)
                    # If text file writing fails, we still try to archive the original PDF
                    # and return 'failed'
                    
        except Exception as e:
            error_details = str(e)
            self._send_status(f"An unexpected error occurred while processing {base_name}: {error_details}")
            result_type = "failed"
            # No text file is written to failed_text_extraction_folder in case of error,
            # only the original PDF is copied there in the finally block.

        finally:
            if doc:
                self._send_status(f"Closing PDF document: {base_name}")
                doc.close()

            # Handle original PDF movement based on result_type
            if result_type == "no_text" or result_type == "failed":
                # Copy original PDF to failed_text_extraction_folder
                failed_pdf_path = os.path.join(self.failed_text_extraction_folder, base_name)
                copied_to_failed = self._move_file_with_retry(pdf_path, failed_pdf_path, operation="copy", file_description="failed PDF copy")
                if not copied_to_failed:
                    self._send_status(f"WARNING: Could not copy original PDF {base_name} to failed text extraction folder.")
            
            # Always attempt to move original PDF to archive
            archive_path = os.path.join(self.archive_folder, base_name)
            original_pdf_moved = self._move_file_with_retry(pdf_path, archive_path, operation="move", file_description="original PDF")
            
            if not original_pdf_moved:
                self._send_status(f"WARNING: Original PDF {base_name} could not be archived. It remains in the source folder.")
                if result_type != "failed": # If it was success or no_text but couldn't archive
                    result_type = "failed_archive" # New status for archiving failure
                    error_details = "Could not archive original PDF."

        return (result_type, base_name, error_details)