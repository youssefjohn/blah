# SpeedHome Selenium Test Suite

A comprehensive Selenium test suite for the SpeedHome property rental application, covering all tenant and landlord user journeys with end-to-end integration testing.

## 📋 Table of Contents

- [Overview](#overview)
- [Test Architecture](#test-architecture)
- [Setup Instructions](#setup-instructions)
- [Running Tests](#running-tests)
- [Test Categories](#test-categories)
- [Configuration](#configuration)
- [Reporting](#reporting)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## 🎯 Overview

This test suite provides comprehensive coverage of the SpeedHome application including:

### **Tenant User Journeys**
- ✅ Authentication (registration, login, logout)
- ✅ Property search and filtering
- ✅ Viewing request scheduling and management
- ✅ Property favorites management
- ✅ Application submission and tracking
- ✅ Dashboard interactions and profile management

### **Landlord User Journeys**
- ✅ Property management (add, edit, delete, status changes)
- ✅ Viewing request management with expandable details
- ✅ Application handling and responses
- ✅ Dashboard navigation and notifications

### **Integration Workflows**
- ✅ Complete viewing request lifecycle
- ✅ Property lifecycle from creation to tenant interaction
- ✅ Cross-role data consistency verification
- ✅ Notification workflows
- ✅ End-to-end application processes

## 🏗️ Test Architecture

### **Page Object Model (POM)**
```
pages/
├── base_page.py           # Base page with common functionality
├── header_page.py         # Navigation and authentication
├── home_page.py           # Property search and browsing
├── property_detail_page.py # Property details and booking
├── user_dashboard_page.py  # Tenant dashboard
└── landlord_dashboard_page.py # Landlord dashboard
```

### **Test Organization**
```
tests/
├── test_tenant_authentication.py    # Tenant auth tests
├── test_tenant_property_search.py   # Search and filtering
├── test_tenant_viewing_requests.py  # Viewing management
├── test_landlord_property_management.py # Property CRUD
├── test_landlord_viewing_requests.py    # Request handling
└── test_integration_workflows.py        # End-to-end tests
```

### **Utilities and Configuration**
```
utils/
├── base_test.py           # Base test class
├── driver_factory.py     # WebDriver management
└── test_data_generator.py # Test data creation

config/
└── test_config.py        # Environment configuration
```

## 🚀 Setup Instructions

### **1. Prerequisites**
- Python 3.8 or higher
- Chrome, Firefox, or Edge browser
- Git

### **2. Clone Repository**
```bash
git clone <repository-url>
cd speedhome-selenium-tests
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Configure Environment**
Create a `.env` file in the root directory:
```env
# Application URLs
BASE_URL=http://localhost:5174
API_BASE_URL=http://localhost:5001

# Test Credentials
TENANT_EMAIL=tenant@test.com
TENANT_PASSWORD=testpass123
LANDLORD_EMAIL=landlord@test.com
LANDLORD_PASSWORD=testpass123

# Test Configuration
DEFAULT_TIMEOUT=10
BROWSER=chrome
HEADLESS=false
```

### **5. Verify Setup**
```bash
# Run a simple smoke test
pytest tests/test_tenant_authentication.py::TestTenantAuthentication::test_login_success -v
```

## 🧪 Running Tests

### **Basic Test Execution**

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_tenant_property_search.py

# Run specific test method
pytest tests/test_tenant_authentication.py::TestTenantAuthentication::test_login_success

# Run with specific browser
pytest --browser=firefox

# Run in headless mode
pytest --headless
```

### **Test Categories**

```bash
# Run smoke tests (critical functionality)
pytest -m smoke

# Run regression tests
pytest -m regression

# Run integration tests
pytest -m integration

# Run tenant-specific tests
pytest -m tenant

# Run landlord-specific tests
pytest -m landlord

# Exclude slow tests
pytest -m "not slow"
```

### **Parallel Execution**

```bash
# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run with specific number of workers
pytest -n 4
```

### **Advanced Options**

```bash
# Run with custom timeout
pytest --timeout=20

# Run with custom base URL
pytest --base-url=http://staging.speedhome.com

# Stop on first failure
pytest -x

# Run last failed tests
pytest --lf

# Run with verbose output
pytest -v -s
```

## 📊 Test Categories

### **🔥 Smoke Tests**
Critical functionality that must work:
```bash
pytest -m smoke
```
- User authentication
- Basic property search
- Core navigation

### **🔄 Regression Tests**
Tests for previously fixed bugs:
```bash
pytest -m regression
```
- Form validation fixes
- Status update persistence
- Cross-browser compatibility

### **🔗 Integration Tests**
End-to-end workflows:
```bash
pytest -m integration
```
- Complete viewing request lifecycle
- Property management workflows
- Cross-role data consistency

### **👤 Role-Specific Tests**

**Tenant Tests:**
```bash
pytest -m tenant
```

**Landlord Tests:**
```bash
pytest -m landlord
```

## ⚙️ Configuration

### **Browser Configuration**
Supported browsers: `chrome`, `firefox`, `edge`

```bash
# Chrome (default)
pytest --browser=chrome

# Firefox
pytest --browser=firefox

# Edge
pytest --browser=edge

# Headless mode
pytest --headless
```

### **Environment Configuration**
Update `config/test_config.py` for different environments:

```python
class TestConfig:
    # Development
    BASE_URL = "http://localhost:5174"
    
    # Staging
    # BASE_URL = "http://staging.speedhome.com"
    
    # Production
    # BASE_URL = "http://speedhome.com"
```

### **Test Data Configuration**
Modify `utils/test_data_generator.py` to customize test data:

```python
def generate_property_data(self):
    return {
        'title': f'Test Property {self.fake.random_int(1000, 9999)}',
        'location': self.fake.city(),
        'price': self.fake.random_int(1000, 5000),
        # ... more fields
    }
```

## 📈 Reporting

### **HTML Reports**
Generated automatically in `reports/report.html`:
```bash
pytest --html=reports/custom_report.html
```

### **JUnit XML**
For CI/CD integration:
```bash
pytest --junitxml=reports/junit.xml
```

### **Allure Reports**
For advanced reporting:
```bash
# Generate Allure results
pytest --alluredir=reports/allure-results

# Serve Allure report
allure serve reports/allure-results
```

### **Screenshots on Failure**
Automatic screenshots saved to `reports/screenshots/` when tests fail.

### **Logs**
Detailed logs saved to `reports/pytest.log`.

## 🔧 Troubleshooting

### **Common Issues**

**1. WebDriver Issues**
```bash
# Update WebDriver
pip install --upgrade webdriver-manager

# Check browser version
google-chrome --version
firefox --version
```

**2. Element Not Found**
- Increase timeout in `config/test_config.py`
- Check if element selectors have changed
- Verify page is fully loaded

**3. Authentication Failures**
- Verify test credentials in `.env` file
- Check if test users exist in the application
- Ensure application is running

**4. Slow Tests**
```bash
# Run with increased timeout
pytest --timeout=30

# Run specific slow tests
pytest -m slow --timeout=60
```

### **Debug Mode**
```bash
# Run with debug output
pytest -v -s --tb=long

# Run single test with debug
pytest tests/test_file.py::test_method -v -s --pdb
```

### **Environment Issues**
```bash
# Check Python version
python --version

# Check installed packages
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## 🚀 CI/CD Integration

### **GitHub Actions Example**
```yaml
name: Selenium Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --browser=chrome --headless -m "not slow"
    
    - name: Upload test results
      uses: actions/upload-artifact@v2
      if: always()
      with:
        name: test-results
        path: reports/
```

### **Jenkins Pipeline Example**
```groovy
pipeline {
    agent any
    
    stages {
        stage('Setup') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }
        
        stage('Test') {
            steps {
                sh 'pytest --browser=chrome --headless --junitxml=reports/junit.xml'
            }
        }
        
        stage('Report') {
            steps {
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: 'reports',
                    reportFiles: 'report.html',
                    reportName: 'Selenium Test Report'
                ])
            }
        }
    }
}
```

## 📝 Test Development Guidelines

### **Writing New Tests**

1. **Follow Page Object Model**
```python
def test_new_functionality(self):
    # Use page objects
    self.home_page.search_properties("apartment")
    self.property_detail_page.schedule_viewing(booking_data)
    
    # Assert expected outcomes
    assert self.user_dashboard_page.has_viewing_requests()
```

2. **Use Descriptive Test Names**
```python
def test_tenant_can_schedule_viewing_with_valid_data(self):
def test_landlord_receives_notification_when_viewing_confirmed(self):
def test_property_status_change_persists_after_page_refresh(self):
```

3. **Add Appropriate Markers**
```python
@pytest.mark.smoke
@pytest.mark.tenant
def test_critical_tenant_functionality(self):
    pass
```

4. **Handle Test Data**
```python
def test_with_generated_data(self):
    property_data = self.data_generator.generate_property_data()
    # Use generated data in test
```

### **Best Practices**

- ✅ Use explicit waits instead of sleep()
- ✅ Clean up test data after tests
- ✅ Make tests independent and idempotent
- ✅ Use meaningful assertions with clear messages
- ✅ Handle both positive and negative test cases
- ✅ Add comments for complex test logic

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-test-suite`
3. **Write tests following guidelines**
4. **Run test suite**: `pytest`
5. **Submit pull request**

### **Code Review Checklist**
- [ ] Tests follow Page Object Model
- [ ] Appropriate markers are used
- [ ] Tests are independent
- [ ] Clear assertions with messages
- [ ] Documentation is updated

## 📞 Support

For issues and questions:
- Create GitHub issue
- Check troubleshooting section
- Review test logs in `reports/pytest.log`

---

**Happy Testing! 🎉**

