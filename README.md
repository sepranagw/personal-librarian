# Getting Started

## 1. Open a bash or powershell terminal

## 2. Clone the repository and go into the root directory
```bash
git clone https://github.com/sepranagw/personal-librarian.git
cd personal-librarian
```

## 3. Create your virtual environment
```bash
python -m venv pa_venv
```

## 4. Activate newly created virtual environment
#### Linux/Mac
```bash
source pa_venv/bin/activate
```
#### Windows 
```powershell
pa_venv\Scripts\activate
```

## 5. Install dependencies
```bash
pip install -r requirements.txt
```

## 6. Set up environment variables
Create a `.env` file in the project root and add your OpenAI API key:
```
OPENAI_API_KEY=your-api-key-here
```

## 7. Run the test script
```bash
python hello_openai_API.py
```
## 8. You should see a tech-themed haiku appear on the command line
