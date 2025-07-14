# 🚀 SpeedHome Selenium Test Suite - Quick Installation Guide

## 📦 **What You Received**

This complete Selenium test suite includes:
- ✅ **74+ Test Scenarios** covering all SpeedHome functionality
- ✅ **Updated Configuration** for your latest repository (port 5173)
- ✅ **Enhanced Test Runner** with multiple execution modes
- ✅ **Professional Page Object Model** structure
- ✅ **Cross-browser Support** (Chrome, Firefox, Edge)
- ✅ **Comprehensive Reporting** (HTML, JUnit XML, Screenshots)

## ⚡ **Quick Setup (5 Minutes)**

### **1. Extract & Navigate**
```bash
# Extract the zip file
unzip speedhome-selenium-tests-final.zip
cd speedhome-selenium-tests/
```

### **2. Install Dependencies**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Or with user flag if needed
pip install --user -r requirements.txt
```

### **3. Configure Environment**
```bash
# Copy environment template
cp .env.example .env

# Edit .env if needed (default settings should work)
nano .env
```

### **4. Start Your SpeedHome Applications**
```bash
# Terminal 1: Start Frontend (port 5173)
cd your-speedhome-repo/speedhome-frontend
npm install
npm run dev

# Terminal 2: Start Backend (port 5001)
cd your-speedhome-repo/speedhome-backend
python src/main.py
```

### **5. Run Tests**
```bash
# Quick smoke test (30 seconds)
python run_tests_enhanced.py --smoke

# All tests (5-10 minutes)
python run_tests_enhanced.py --all

# Specific categories
python run_tests_enhanced.py --auth      # Authentication tests
python run_tests_enhanced.py --search    # Search functionality
python run_tests_enhanced.py --booking   # Booking flows
```

## 🎯 **Test Categories Available**

### **Smoke Tests** (`--smoke`)
Critical functionality verification:
- Homepage loading
- Basic navigation
- Login/register modals
- Essential interactions

### **Authentication Tests** (`--auth`)
Complete login/register flows:
- Modal functionality
- Form validation
- User sessions
- Role management

### **Search Tests** (`--search`)
Advanced property search:
- Location filtering
- Price range filtering
- Property type filtering
- Combined filters

### **Booking Tests** (`--booking`)
End-to-end booking flows:
- Viewing requests
- Form validation
- Booking confirmation
- Application processes

## 📊 **View Test Results**

After running tests, check:
- **HTML Report**: `reports/report_TIMESTAMP.html`
- **Screenshots**: `reports/screenshots/`
- **JUnit XML**: `reports/junit_results.xml`

## 🔧 **Configuration**

### **Default Settings (.env)**
```env
BASE_URL=http://localhost:5173    # Updated for your repo
API_BASE_URL=http://localhost:5001
BROWSER=chrome
HEADLESS=true
DEFAULT_TIMEOUT=10
```

### **Test Users**
Create these users in your SpeedHome app:
- **Tenant**: `tenant@test.com` / `testpass123`
- **Landlord**: `landlord@test.com` / `testpass123`

## 🚀 **Advanced Usage**

### **Cross-browser Testing**
```bash
python run_tests_enhanced.py --smoke --browser firefox
python run_tests_enhanced.py --smoke --browser edge
```

### **Parallel Execution**
```bash
python run_tests_enhanced.py --all --parallel
```

### **Visible Browser (Debugging)**
```bash
python run_tests_enhanced.py --smoke --no-headless
```

### **Specific Test Files**
```bash
python run_tests_enhanced.py tests/test_simple_homepage.py
python run_tests_enhanced.py tests/test_authentication_flows.py
```

## 🎉 **You're Ready!**

Your SpeedHome Selenium test suite is now:
- ✅ **Fully compatible** with your latest repository
- ✅ **Production ready** with comprehensive coverage
- ✅ **Easy to maintain** with Page Object Model
- ✅ **CI/CD ready** for automated pipelines

**Happy Testing! 🚀**

---

## 📞 **Support**

If you encounter any issues:
1. Check that both frontend (5173) and backend (5001) are running
2. Verify test user accounts exist in your database
3. Review the HTML reports for detailed error information
4. Check screenshots in `reports/screenshots/` for visual debugging

The test suite is designed to be robust and self-documenting!

