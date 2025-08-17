    1 Electronic Health Records EZ Pass: 
      This code is the start of a universal EZ pass for electronic health records coming from multiple
      difference healthcare networks.  We start with an Automated PDF Processor for Electronic Health Records
    2
    3 ## Overview
    4
    5 The "EHR EZ Pass" is a Python-based desktop application designed to streamline the processing
      of PDF documents, particularly within an Electronic Health Record (EHR) system context. Built
      with a user-friendly graphical interface using `customtkinter`, this tool automates the
      extraction of text from PDF files, intelligently routes them based on processing outcomes, and
      ensures proper archiving.
    6
    7 ## Core Functionality
    8
    9 *   **Automated PDF Text Extraction:** Monitors a specified "Input PDF Folder" for new PDF
      documents. For each PDF, it attempts to extract all embedded text content.
   10 *   **Intelligent Document Routing:**
   11     *   **Successful Extraction:** If text is successfully extracted, the content is saved as a
      `.txt` file in an "Output Text Folder" (e.g., for integration into an EHR system). The original
      PDF is then automatically moved to an "Archive Folder".
   12     *   **No Text Found / Failed Extraction:** In cases where a PDF contains no extractable
      text or if the text extraction process encounters an error, the original PDF is copied to a
      "Failed Text Extraction Folder" for manual review. Crucially, even in these scenarios, the
      original PDF is still moved to the "Archive Folder" to maintain a complete record.
   13 *   **Intuitive Graphical User Interface (GUI):**
   14     *   **Real-time Status Updates:** Provides a dedicated status window to display live
      progress and logs during PDF processing.
   15     *   **Processing Summary:** Presents a clear summary of each batch, including the total
      number of files processed, successful extractions, files with no text, and failed extractions.
   16     *   **Configurable Folder Paths:** Users can easily define and update the input, output,
      archive, and failed extraction directories through a dedicated "Settings" window. These
      settings are persistently saved in a `config.json` file.
   17 *   **Robustness and Performance:**
   18     *   **Multi-threading:** The PDF processing runs in a separate thread, ensuring the GUI
      remains responsive and usable during lengthy operations.
   19     *   **Error Handling & Retries:** Includes robust error handling for file operations and
      incorporates retry mechanisms for moving/copying files, enhancing reliability against transient
      system issues.
   20
   21 ## Typical Use Case
   22
   23 This application is ideal for healthcare environments or administrative workflows that involve
      handling a large volume of incoming PDF documents (e.g., faxes, scanned patient records,
      external reports). It helps automate the initial step of digitizing and organizing these
      documents, making them ready for further processing or direct integration into an EHR system
      like VistA (as suggested by internal folder naming conventions such as "CPRS documents for
      provider to sign" and "VistA imaging").
   24
   25 ## Technologies Used
   26
   27 *   **Python:** The core programming language.
   28 *   **`customtkinter`:** For building the modern and responsive graphical user interface.
   29 *   **`PyMuPDF` (fitz):** For efficient PDF parsing and text extraction.
   30 *   **Standard Python Libraries:** `os`, `shutil`, `json`, `threading` for file system
      operations, configuration management, and concurrency.
   31
   32 ## Setup and Installation
   33
   34 To set up and run this application, follow these steps:
   35
   36 1.  **Clone the Repository:**

      git clone <repository_url>
      cd EHR-EZ-Pass

   1     *(Replace `<repository_url>` with the actual URL of your GitHub repository once created.)*
   2
   3 2.  **Create a Virtual Environment (Recommended):**

      python -m venv .venv


   1
   2 3.  **Activate the Virtual Environment:**
   3     *   **Windows:**

          .venv\Scripts\activate

   1     *   **macOS/Linux:**

          source .venv/bin/activate

   1
   2 4.  **Install Dependencies:**

      pip install -r requirements.txt

   1
   2 5.  **Run the Application:**

      python main.py


   1
   2 ## Configuration
   3
   4 The application uses a `config.json` file to store folder paths. A default `config.json` will be
     created if it doesn't exist. You can modify these paths through the application's "Settings"
     window or by directly editing the `config.json` file.
   5
   6 **Example `config.json`:**

  {
      "input_pdf_folder": "Rightfax folder",
      "output_text_folder": "CPRS documents for provider to sign",
      "archive_folder": "PDF files to be archived in vistaimaging",
      "failed_text_extraction_folder": "failed text extraction folder"
  }


   1 *(Note: The folder names above are relative to the application's root directory. You can use
     absolute paths if preferred.)*
   2
   3 ## Project Structure

  EHR EZ Pass/
  ├── config.json             # Configuration file for folder paths
  ├── gui.py                  # Graphical User Interface (GUI) logic
  ├── main.py                 # Application entry point
  ├── pdf_processor.py        # Core PDF processing logic
  ├── .venv/                  # Python virtual environment (created during setup)
  ├── <Your Input PDF Folder>/ # e.g., Rightfax folder
  ├── <Your Output Text Folder>/ # e.g., CPRS documents for provider to sign
  ├── <Your Archive Folder>/   # e.g., PDF files to be archived in vistaimaging
  └── <Your Failed Extraction Folder>/ # e.g., failed text extraction folder


   1
   2 ## Contributing
   3
   4 Contributions are welcome - no such thing as a bad idea
   5
   6 ## License
   7
   8 Open source-  help yourself and build from this better 