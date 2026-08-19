# Contributing to HydroRefil

Thank you for your interest in contributing to **HydroRefil**! This project is an open-source, production-grade decision support platform for Rooftop Rainwater Harvesting (RTRWH) and Artificial Groundwater Recharge (AR) assessment.

Whether you are a **Hydrologist / Water Resources Engineer**, **Full-Stack Developer**, **GIS Specialist**, or **Technical Writer**, your contributions are warmly welcomed.

---

## 📋 Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [How Can I Contribute?](#how-can-i-contribute)
3. [Local Development Setup](#local-development-setup)
4. [Hydrology & Engineering Contribution Principles](#hydrology--engineering-contribution-principles)
5. [Git Workflow & Branching Strategy](#git-workflow--branching-strategy)
6. [Testing & Quality Standards](#testing--quality-standards)
7. [Submitting a Pull Request](#submitting-a-pull-request)

---

## 📜 Code of Conduct
Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) to keep this community open and inclusive.

---

## 🛠️ How Can I Contribute?

- **Hydrological Domain:** Adding new validated regional runoff coefficients, soil percolation parameters, or aquifer recharge models.
- **GIS & Meteorological Data:** Adding IMD rainfall stations or spatial datasets for additional Indian districts and states.
- **Frontend / UI:** Enhancing charts, mobile responsiveness, visual cross-sections of recharge pits/sumps, and accessibility.
- **Backend / APIs:** Expanding database connectors, reporting templates, or adding batch site calculation endpoints.
- **Documentation:** Improving developer guides, benchmark verification scenarios, and user walkthroughs.

---

## 💻 Local Development Setup

### Prerequisites
- **Python:** 3.12+
- **Node.js:** v20+ / v22+
- **Git:** 2.30+

### 1. Clone the Repository
```bash
git clone https://github.com/Nirnoy12/Hydro-Refil.git
cd Hydro-Refil
```

### 2. Configure Environment
```bash
cp .env.example .env
```

### 3. Backend Setup (FastAPI + Python)
```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux / macOS:
source .venv/bin/activate

pip install -r requirements.txt
python -m pytest tests/ -v
python -m uvicorn main:app --reload --port 8000
```
- API will be accessible at: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup (React 19 + Vite)
In a separate terminal:
```bash
cd "frontend/Hydro Refil"
npm install
npm run build
npm run dev
```
- Web Application will be accessible at: `http://localhost:5173`

---

## 💧 Hydrology & Engineering Contribution Principles

To maintain scientific integrity and regulatory compliance, all hydrological formula contributions must obey these four core rules:

1. **Deterministic & Unit-Aware:** Never hardcode empirical factors without explicit physical units and source citations.
   - Example: $1\text{ mm of rain over } 1\text{ m}^2 = 1\text{ Litre of water}$.
2. **Dual-Engine Equivalence:** Any calculation added to the Python backend (`backend/domain/hydrology/`) **must also be mirrored** in the client-side TypeScript engine (`frontend/Hydro Refil/src/domain/hydrology.ts`) to ensure offline reliability.
3. **No Black-Box AI for Sizing:** AI/ML must never override physical hydraulic equations. Sizing must remain rule-based, auditable, and traceable to Indian standards (**BIS IS 15797:2008** and **CGWB Manual 2007**).
4. **Safety Guards:** Always maintain physical boundary checks (e.g., water table depth $< 3.0\text{ m}$ BGL prevents in-ground recharge pits to avoid waterlogging).

---

## 🌿 Git Workflow & Branching Strategy

We follow a feature-branch workflow:

1. **Fork or create a feature branch** from `main`:
   ```bash
   git checkout -b feat/add-district-rainfall-normals
   # or for bugfixes:
   git checkout -b fix/recharge-shaft-freeboard
   ```
2. **Commit with Conventional Commit Messages:**
   - `feat: add Tamil Nadu district rainfall normal table`
   - `fix: correct gravel void porosity fraction in trench calculation`
   - `docs: add hydrogeological survey guideline to methodology`
   - `test: add unit test for expansive black cotton soil sizing`

---

## 🧪 Testing & Quality Standards

Before submitting any code, verify all tests pass and the bundle builds cleanly:

```bash
# 1. Run backend unit tests:
cd backend
python -m pytest tests/ -v

# 2. Validate frontend TypeScript & production build:
cd "../frontend/Hydro Refil"
npm run build
```

---

## 📬 Submitting a Pull Request

1. Push your branch to GitHub:
   ```bash
   git push origin feat/your-feature-name
   ```
2. Open a Pull Request on GitHub against the `main` branch.
3. Fill out the [Pull Request Template](.github/PULL_REQUEST_TEMPLATE.md) detailing what changed, the engineering rationale, and test results.
4. Maintainers will review your PR and provide constructive feedback!
