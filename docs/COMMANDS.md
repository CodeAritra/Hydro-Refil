# EXACT OPERATIONAL COMMANDS (WINDOWS CMD / POWERSHELL)

---

## 1. Initial Setup

### Clone and Enter Project Root
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform"
```

### Environment Configuration
```powershell
Copy-Item .env.example .env
```

---

## 2. Backend (FastAPI + Python 3.12)

### Install Dependencies
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\backend"
pip install -r requirements.txt
```

### Run Pytest Test Suite
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\backend"
python -m pytest tests/ -v
```

### Start Development Server
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\backend"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
- API will be live at: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

## 3. Frontend (React 19 + TypeScript + Vite)

### Install Dependencies
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\frontend\Hydro Refil"
npm install
```

### Run Production Build Validation
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\frontend\Hydro Refil"
npm run build
```

### Start Frontend Dev Server
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\frontend\Hydro Refil"
npm run dev
```
- Web Application will be live at: `http://localhost:5173`

---

## 4. One-Liner Dual-Server Startup (PowerShell)

To launch both backend and frontend concurrently in two separate terminal tabs:

**Terminal 1 (Backend):**
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\backend"; python -m uvicorn main:app --reload --port 8000
```

**Terminal 2 (Frontend):**
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform\frontend\Hydro Refil"; npm run dev
```

---

## 5. Git Version Control Verification
```powershell
cd "c:\Users\nirno\Codes\rtrwh-platform"
git status
git add .
git commit -m "feat: complete production-quality RTRWH platform for SIH"
```
