# PDF Master - Flask PDF Tools Application

A beautiful and powerful web application for performing various PDF operations including merge, split, rotate, extract, compress, and get PDF information.

## Features

- **Merge PDFs**: Combine multiple PDF files into a single document
- **Split PDF**: Split PDF into individual pages or custom page ranges
- **Rotate PDF**: Rotate pages in your PDF document (90°, 180°, 270°)
- **Extract Pages**: Extract specific pages from a PDF document
- **Compress PDF**: Reduce PDF file size while maintaining quality
- **PDF Info**: Get detailed information about your PDF file

## Technologies Used

- **Backend**: Flask (Python)
- **PDF Processing**: PyPDF2
- **Frontend**: HTML5, CSS3, JavaScript
- **UI Framework**: Custom CSS with modern design

## Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd "C:\Users\sruja\Documents\DataScience\20_Cursor_ai_DataScience_tutorial"
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Run the Flask application**:
   ```bash
   python app.py
   ```

2. **Open your web browser** and navigate to:
   ```
   http://localhost:5000
   ```

3. **Use the application**:
   - Select a tool from the navigation menu
   - Upload your PDF file(s)
   - Configure the operation settings
   - Click the action button to process
   - Download the result

## Project Structure

```
.
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── merge.html        # Merge PDFs page
│   ├── split.html        # Split PDF page
│   ├── rotate.html       # Rotate PDF page
│   ├── extract.html      # Extract pages page
│   ├── compress.html     # Compress PDF page
│   └── info.html         # PDF info page
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # Main JavaScript file
├── uploads/              # Temporary upload directory (auto-created)
└── outputs/              # Temporary output directory (auto-created)
```

## API Endpoints

- `GET /` - Home page
- `GET /merge` - Merge PDFs page
- `POST /merge` - Merge PDFs endpoint
- `GET /split` - Split PDF page
- `POST /split` - Split PDF endpoint
- `GET /rotate` - Rotate PDF page
- `POST /rotate` - Rotate PDF endpoint
- `GET /extract` - Extract pages page
- `POST /extract` - Extract pages endpoint
- `GET /compress` - Compress PDF page
- `POST /compress` - Compress PDF endpoint
- `GET /info` - PDF info page
- `POST /info` - PDF info endpoint

## Security Notes

- Files are automatically deleted after processing
- Maximum file size limit: 100MB
- Only PDF files are accepted
- All processing happens server-side

## Browser Compatibility

- Chrome/Edge (recommended)
- Firefox
- Safari
- Opera

## Troubleshooting

1. **Port already in use**: Change the port in `app.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Module not found**: Make sure you've activated your virtual environment and installed all dependencies

3. **File upload fails**: Check file size (max 100MB) and ensure it's a valid PDF

## License

This project is open source and available for personal and commercial use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.
