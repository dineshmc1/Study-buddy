# LLM Study Buddy

An advanced Large Language Model (LLM) designed to act as a personalized study buddy, leveraging user-uploaded notes for tailored learning experiences, active recall, and a unique "teaching mode" for comprehensive knowledge assessment.

## Features

### Learning Mode
- Contextual teaching based on uploaded notes
- Dynamic questioning with various question types
- Adaptive difficulty adjustment
- Elaborative feedback
- Active recall prompts
- Progress tracking

### Teaching Mode
- Feynman Technique simulation
- Real-time gap identification
- Targeted follow-up questions
- Constructive criticism
- Badge award system
- Detailed feedback

### Document Processing
- Support for multiple file types (PDF, images, text)
- OCR capabilities
- Automatic topic extraction
- Semantic understanding
- Vector-based storage and retrieval

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
- Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: `sudo apt-get install tesseract-ocr`
- macOS: `brew install tesseract`

3. Install Ollama:
- Follow instructions at https://ollama.ai/download
- Pull the required model:
```bash
ollama pull llama2:8b
```

4. Run the application:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Endpoints

### POST /upload
Upload study notes for processing
- Accepts: PDF, images (PNG, JPG), text files
- Returns: List of extracted topics

### POST /study
Handle study requests
- Parameters:
  - topic: The topic to study
  - mode: "learning" or "teaching"
  - context: Optional additional context
- Returns: Learning/teaching content and progress/badges

## Usage Example

1. Upload your study notes:
```python
import requests

files = {'file': open('notes.pdf', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)
topics = response.json()['topics']
```

2. Start a learning session:
```python
data = {
    'topic': topics[0],
    'mode': 'learning'
}
response = requests.post('http://localhost:8000/study', json=data)
content = response.json()['content']
```

3. Try teaching mode:
```python
data = {
    'topic': topics[0],
    'mode': 'teaching'
}
response = requests.post('http://localhost:8000/study', json=data)
feedback = response.json()['content']
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 