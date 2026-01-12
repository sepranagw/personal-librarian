# Getting Started

## 1. Open a bash or powershell terminal

## 2. Create your virtual environment
```bash
python -m venv pa_venv
```

## 3. Activate newly created virtual environment
#### Linux/Mac
```bash
source pa_venv/bin/activate
```
#### Windows 
```powershell
pa_venv\Scripts\activate
```

## 4. Install dependencies
```bash
pip install -r requirements.txt
```

## 5. Set up environment variables
Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## 6. Run the test script
```bash
python hello_openai_API.py
```
