# Project File Structure & Organization

## 📂 Complete Project Layout

```
scam-honeypot-AI/
│
├── 📄 00_START_HERE.md                 ⭐ Read this first!
│
├── 📄 README.md                        📖 Project overview & quick start
│
├── 🐍 main.py                          🚀 Server startup (python main.py)
│
├── 🧪 test_api.py                      ✅ Test suite (python test_api.py)
│
├── 📚 Documentation/
│   ├── IMPLEMENTATION.md               📖 Complete technical docs
│   ├── API_EXAMPLES.md                 🔗 Real-world examples
│   ├── DEPLOYMENT.md                   🚀 Production deployment
│   ├── QUICK_REFERENCE.md              ⚡ Quick lookup guide
│   ├── CHANGES.md                      📝 What was changed
│   └── SUBMISSION_CHECKLIST.md         ✅ Pre-submission checklist
│
├── 🍯 honeypot/                        Core application
│   ├── AI.py                           🤖 AI agent (Gemini)
│   ├── app.py                          ⚙️ FastAPI setup
│   ├── store.py                        💾 Session management
│   ├── utils.py                        🔧 Intelligence extraction
│   │
│   └── routers/
│       └── chat.py                     💬 Main /chat endpoint
│
├── ⚙️ Configuration/
│   ├── requirements.txt                📦 Python dependencies
│   ├── .env (create locally)           🔐 Environment variables
│   ├── Procfile                        🚀 Heroku/Render config
│   ├── runtime.txt                     🐍 Python version
│   └── pyproject.toml                  📦 Project metadata
│
├── 📋 License & Git
│   ├── LICENSE                         📜 License file
│   ├── .gitignore                      🚫 Git ignore config
│   └── .git/                           📦 Git repository
│
└── 📊 Output
    └── Session data (in-memory)        💾 Conversation storage
```

---

## 📖 Documentation Map

### For Quick Start
1. **00_START_HERE.md** - Read this first! (3 min read)
2. **README.md** - Overview and quick start (5 min read)
3. **QUICK_REFERENCE.md** - API quick lookup (2 min read)

### For Implementation Details
1. **IMPLEMENTATION.md** - Complete technical guide (20 min read)
2. **API_EXAMPLES.md** - Real-world examples (15 min read)
3. Code comments in honeypot/ files

### For Deployment & Operations
1. **DEPLOYMENT.md** - Deployment guide (15 min read)
2. **SUBMISSION_CHECKLIST.md** - Pre-submission (10 min read)
3. **CHANGES.md** - What was implemented (10 min read)

### For Testing
1. **test_api.py** - Run automated tests
2. **API_EXAMPLES.md** - Manual test examples

---

## 🔄 File Dependencies

```
main.py
  ↓
honeypot/app.py
  ├── honeypot/routers/chat.py
  │   ├── honeypot/AI.py (Gemini API)
  │   ├── honeypot/utils.py
  │   └── honeypot/store.py
  │
  └── Uvicorn Server

test_api.py
  ├── honeypot.app
  └── requests library
```

---

## 📊 Code Statistics

### Core Application
```
honeypot/
├── AI.py               ~120 lines  (AI agent logic)
├── app.py              ~10 lines   (FastAPI setup)
├── store.py            ~90 lines   (Session management)
├── utils.py            ~130 lines  (Intelligence extraction)
└── routers/chat.py     ~150 lines  (Main endpoint)
                        ____________
Total:                  ~500 lines
```

### Tests
```
test_api.py            ~250 lines  (Comprehensive tests)
```

### Documentation
```
README.md              ~300 lines
IMPLEMENTATION.md      ~400 lines
API_EXAMPLES.md        ~500+ lines
DEPLOYMENT.md          ~350+ lines
QUICK_REFERENCE.md     ~200 lines
CHANGES.md             ~200 lines
SUBMISSION_CHECKLIST   ~300 lines
00_START_HERE.md       ~300 lines
                       ____________
Total:                 ~2300+ lines
```

**Documentation to Code Ratio: 4.6:1** (Extremely well documented)

---

## 🎯 What Each File Does

### Application Files

#### `main.py`
- **Purpose**: Server startup
- **When to use**: `python main.py` to run locally
- **Output**: FastAPI server on port 8000

#### `honeypot/AI.py`
- **Purpose**: AI agent for scam analysis
- **Key function**: `analyze_and_reply(text, history)`
- **Uses**: Google Gemini 2.5 Flash
- **Returns**: `{is_scam, reply, confidence}`

#### `honeypot/app.py`
- **Purpose**: FastAPI application initialization
- **Sets up**: Routes, health check endpoint
- **Returns**: FastAPI app instance

#### `honeypot/routers/chat.py`
- **Purpose**: Main API endpoint handler
- **Endpoint**: POST `/chat`
- **Handles**: Authentication, validation, orchestration
- **Returns**: `{status, reply}` or error

#### `honeypot/store.py`
- **Purpose**: Session & conversation storage
- **Manages**: Session state, message history, intelligence
- **Key functions**: 
  - `get_or_create_session(id)`
  - `update_session(id, intel)`
  - `should_send_report(id)`

#### `honeypot/utils.py`
- **Purpose**: Intelligence extraction
- **Key function**: `extract_intelligence(text)`
- **Extracts**: UPI, phone, bank, links, keywords
- **Returns**: Dictionary of extracted data

### Testing

#### `test_api.py`
- **Purpose**: Comprehensive test suite
- **Tests**:
  - Ping requests
  - Single scam messages
  - Multi-turn conversations
  - Final report triggers
- **Run**: `python test_api.py`

### Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| 00_START_HERE.md | Quick overview | Everyone |
| README.md | Project intro & start | Everyone |
| IMPLEMENTATION.md | Technical deep dive | Developers |
| API_EXAMPLES.md | Real-world examples | API users |
| DEPLOYMENT.md | Production deployment | DevOps/Ops |
| QUICK_REFERENCE.md | Quick lookup | API users |
| CHANGES.md | What was implemented | Project leads |
| SUBMISSION_CHECKLIST.md | Pre-submission | Submitters |

---

## 🚀 Quick Navigation

### "I want to..."

**Start the server**
```bash
python main.py
```
→ See output at http://localhost:8000

**Test the API**
```bash
python test_api.py
```
→ Runs comprehensive test suite

**Understand the system**
```
Open: IMPLEMENTATION.md (20 min)
```

**Learn the API**
```
Open: QUICK_REFERENCE.md (2 min)
Open: API_EXAMPLES.md (15 min)
```

**Deploy to production**
```
Open: DEPLOYMENT.md (15 min)
```

**Submit to GUVI**
```
Open: SUBMISSION_CHECKLIST.md (10 min)
```

**Understand changes**
```
Open: CHANGES.md (10 min)
```

---

## 📦 Dependencies

### Python Packages (requirements.txt)
```
fastapi==0.104.1          # Web framework
uvicorn[standard]==0.24.0 # Server
pydantic==2.5.0           # Validation
python-dotenv==1.0.0      # .env support
google-generativeai==0.3.0 # Gemini API
httpx==0.25.1             # Async HTTP
```

### External APIs
```
Google Gemini 2.5 Flash   # AI model
GUVI Evaluation Endpoint  # Report callback
```

### Environment Variables
```
GEMINI_API_KEY           # (Required)
API_KEY                  # (Required)
```

---

## 🔐 Security Files

### Protected Files
```
.env                 (Create locally, never commit)
requirements.txt     (Safe to commit)
```

### Git Configuration
```
.gitignore          (Prevents committing .env)
```

---

## 📊 File Size Summary

```
main.py                     <1 KB   (Very small)
test_api.py                ~10 KB   (Medium)
honeypot/AI.py             ~5 KB    (Small)
honeypot/app.py            <1 KB    (Tiny)
honeypot/store.py          ~4 KB    (Small)
honeypot/utils.py          ~6 KB    (Small)
honeypot/routers/chat.py   ~7 KB    (Small)
requirements.txt            <1 KB   (Tiny)
                            _______
Total Code:               ~33 KB   (Very manageable)

Documentation:           ~200 KB   (Comprehensive)
Total Project:           ~233 KB   (Lightweight)
```

---

## 🎯 File Selection Guide

### For Understanding the System
1. Read: **00_START_HERE.md**
2. Read: **README.md**
3. Read: **IMPLEMENTATION.md**
4. Review: honeypot/*.py files

### For Using the API
1. Reference: **QUICK_REFERENCE.md**
2. Examples: **API_EXAMPLES.md**
3. Test: **test_api.py**

### For Deploying
1. Follow: **DEPLOYMENT.md**
2. Setup: **.env** file
3. Configure: **requirements.txt**

### For Submitting to GUVI
1. Verify: **SUBMISSION_CHECKLIST.md**
2. Review: **CHANGES.md**
3. Test: **test_api.py**

---

## 📝 File Update Status

```
✅ honeypot/AI.py              ENHANCED (Multi-turn support)
✅ honeypot/app.py             VERIFIED (No changes needed)
✅ honeypot/store.py           ENHANCED (Persistence features)
✅ honeypot/utils.py           ENHANCED (Better extraction)
✅ honeypot/routers/chat.py    REFACTORED (Report logic)
✅ main.py                      VERIFIED (No changes needed)
✅ test_api.py                  CREATED (New test suite)
✅ README.md                    CREATED (Comprehensive)
✅ IMPLEMENTATION.md            CREATED (Technical docs)
✅ API_EXAMPLES.md              CREATED (Usage examples)
✅ DEPLOYMENT.md                CREATED (Deploy guide)
✅ QUICK_REFERENCE.md           CREATED (Quick lookup)
✅ CHANGES.md                   CREATED (Summary)
✅ SUBMISSION_CHECKLIST.md      CREATED (Pre-submission)
✅ 00_START_HERE.md             CREATED (Quick overview)
```

---

## 🔄 Workflow

### Development Workflow
```
1. Edit code in honeypot/
2. Run: python test_api.py
3. Check output
4. Commit if working
```

### Testing Workflow
```
1. Start server: python main.py
2. In another terminal: python test_api.py
3. Review test results
4. Fix issues if needed
```

### Deployment Workflow
```
1. Create .env locally
2. Test locally: python test_api.py
3. Push to GitHub
4. Deploy to Render/Heroku
5. Set environment variables
6. Verify health check
7. Test with GUVI platform
```

---

## 📚 Reading Order (Recommended)

1. **This file** (File Structure) - 10 min
2. **00_START_HERE.md** - 3 min
3. **README.md** - 5 min
4. **QUICK_REFERENCE.md** - 2 min
5. **API_EXAMPLES.md** - 15 min
6. **IMPLEMENTATION.md** - 20 min
7. **DEPLOYMENT.md** - 15 min
8. **Review code** - 20 min

**Total Reading Time**: ~90 minutes
**Total Hands-On**: ~30 minutes

---

**Version**: 1.0  
**Last Updated**: February 2026  
**Status**: ✅ Complete & Organized
