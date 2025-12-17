# How to install project

python3.12 -m venv .venv 

source .venv/bin/activate

pip install -r requirements.txt


# How to install & run the project
## ❗ Prerequisite (MANDATORY)

This project requires exactly Python 3.12.x \
Other Python versions will not work (OpenCV compatibility).

Verify:
```bash
python --version
```

### macOS
```bash

# 1. Clone the repository
git clone <repo-url>
cd <project-folder>

# 2. Create virtual environment (Python 3.12.x)
python3.12 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python src/main.py
```

If python3.12 is not found, install Python 3.12.x from:
https://www.python.org/downloads/

### Linux
```bash
# 1. Clone the repository
git clone <repo-url>
cd <project-folder>

# 2. Create virtual environment (Python 3.12.x)
python3.12 -m venv .venv

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python src/main.py
```

On Ubuntu/Debian you may need:

sudo apt install python3.12 python3.12-venv

### Windows (PowerShell)

```powershell
# 1. Clone the repository
git clone <repo-url>
cd <project-folder>

# 2. Create virtual environment (Python 3.12.x)
py -3.12 -m venv .venv

# 3. Activate virtual environment
.venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the app
python src\main.py
```

If activation is blocked:

Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

### Notes

.venv/ is OS-specific — do not commit or share it

Always verify Python version before creating the venv

If OpenCV fails to install, check Python version first

Optional (developers): build executable\
```bash
pip install pyinstaller
python3 -m PyInstaller --onedir --windowed --clean --noconfirm --paths=app --name AlgorytmyPrzetObrazAPK app/main.py

# OR
pyinstaller --onedir --windowed --clean --noconfirm --paths=app --name AlgorytmyPrzetObrazAPK app/main.py

```
