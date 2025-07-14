#!/usr/bin/env python3
"""
SpeedHome Selenium Test Runner

A convenient script to run different test suites with various configurations.
"""

import argparse
import subprocess
import sys
import os
from datetime import datetime

class TestRunner:
    """Test runner for SpeedHome Selenium tests"""
    
    def __init__(self):
        self.base_command = ["pytest"]
        self.report_dir = "reports"
        
        # Ensure reports directory exists
        os.makedirs(self.report_dir, exist_ok=True)
    
    def run_smoke_tests(self, browser="chrome", headless=False):
        """Run smoke tests for critical functionality"""
        print("🔥 Running Smoke Tests...")
        
        command = self.base_command + [
            "-m", "smoke",
            "--browser", browser,
            "--html=reports/smoke_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_regression_tests(self, browser="chrome", headless=False):
        """Run regression tests"""
        print("🔄 Running Regression Tests...")
        
        command = self.base_command + [
            "-m", "regression",
            "--browser", browser,
            "--html=reports/regression_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_integration_tests(self, browser="chrome", headless=False):
        """Run integration tests"""
        print("🔗 Running Integration Tests...")
        
        command = self.base_command + [
            "-m", "integration",
            "--browser", browser,
            "--html=reports/integration_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_tenant_tests(self, browser="chrome", headless=False):
        """Run tenant-specific tests"""
        print("👤 Running Tenant Tests...")
        
        command = self.base_command + [
            "-m", "tenant",
            "--browser", browser,
            "--html=reports/tenant_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_landlord_tests(self, browser="chrome", headless=False):
        """Run landlord-specific tests"""
        print("🏢 Running Landlord Tests...")
        
        command = self.base_command + [
            "-m", "landlord",
            "--browser", browser,
            "--html=reports/landlord_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_all_tests(self, browser="chrome", headless=False, parallel=False):
        """Run all tests"""
        print("🚀 Running All Tests...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        command = self.base_command + [
            "--browser", browser,
            f"--html=reports/full_report_{timestamp}.html",
            "--self-contained-html",
            f"--junitxml=reports/junit_{timestamp}.xml",
            "-v"
        ]
        
        if headless:
            command.append("--headless")
        
        if parallel:
            command.extend(["-n", "auto"])
        
        return self._execute_command(command)
    
    def run_specific_test(self, test_path, browser="chrome", headless=False):
        """Run specific test file or method"""
        print(f"🎯 Running Specific Test: {test_path}")
        
        command = self.base_command + [
            test_path,
            "--browser", browser,
            "--html=reports/specific_test_report.html",
            "--self-contained-html",
            "-v", "-s"
        ]
        
        if headless:
            command.append("--headless")
        
        return self._execute_command(command)
    
    def run_cross_browser_tests(self, test_suite="smoke"):
        """Run tests across multiple browsers"""
        print("🌐 Running Cross-Browser Tests...")
        
        browsers = ["chrome", "firefox", "edge"]
        results = {}
        
        for browser in browsers:
            print(f"\n--- Testing with {browser.upper()} ---")
            
            if test_suite == "smoke":
                result = self.run_smoke_tests(browser, headless=True)
            elif test_suite == "regression":
                result = self.run_regression_tests(browser, headless=True)
            elif test_suite == "integration":
                result = self.run_integration_tests(browser, headless=True)
            else:
                result = self.run_all_tests(browser, headless=True)
            
            results[browser] = result
        
        # Summary
        print("\n" + "="*50)
        print("CROSS-BROWSER TEST SUMMARY")
        print("="*50)
        
        for browser, result in results.items():
            status = "✅ PASSED" if result == 0 else "❌ FAILED"
            print(f"{browser.upper()}: {status}")
        
        return results
    
    def run_performance_tests(self, browser="chrome"):
        """Run performance-focused tests"""
        print("⚡ Running Performance Tests...")
        
        command = self.base_command + [
            "-m", "not slow",  # Exclude slow tests for performance run
            "--browser", browser,
            "--headless",
            "--html=reports/performance_report.html",
            "--self-contained-html",
            "-v"
        ]
        
        return self._execute_command(command)
    
    def run_ci_tests(self):
        """Run tests suitable for CI environment"""
        print("🤖 Running CI Tests...")
        
        command = self.base_command + [
            "-m", "smoke or regression",
            "--browser", "chrome",
            "--headless",
            "--html=reports/ci_report.html",
            "--self-contained-html",
            "--junitxml=reports/ci_junit.xml",
            "--maxfail=3",
            "-v"
        ]
        
        return self._execute_command(command)
    
    def _execute_command(self, command):
        """Execute pytest command and return exit code"""
        print(f"Executing: {' '.join(command)}")
        print("-" * 50)
        
        try:
            result = subprocess.run(command, check=False)
            return result.returncode
        except Exception as e:
            print(f"Error executing command: {e}")
            return 1
    
    def show_test_info(self):
        """Show information about available tests"""
        print("📊 SpeedHome Test Suite Information")
        print("=" * 50)
        
        # Collect test information
        command = ["pytest", "--collect-only", "-q"]
        
        try:
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                test_files = [line for line in lines if line.startswith('tests/')]
                
                print(f"Total test files found: {len(test_files)}")
                print("\nTest files:")
                for test_file in test_files:
                    print(f"  - {test_file}")
                
                # Show markers
                print("\nAvailable test markers:")
                markers = ["smoke", "regression", "integration", "tenant", "landlord", "slow"]
                for marker in markers:
                    print(f"  - {marker}")
                
            else:
                print("Could not collect test information")
                
        except Exception as e:
            print(f"Error collecting test info: {e}")

def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(
        description="SpeedHome Selenium Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --smoke                    # Run smoke tests
  python run_tests.py --all --browser firefox    # Run all tests with Firefox
  python run_tests.py --integration --headless   # Run integration tests headless
  python run_tests.py --cross-browser smoke      # Run smoke tests across browsers
  python run_tests.py --specific tests/test_tenant_authentication.py
        """
    )
    
    # Test suite options
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--regression", action="store_true", help="Run regression tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--tenant", action="store_true", help="Run tenant tests")
    parser.add_argument("--landlord", action="store_true", help="Run landlord tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--ci", action="store_true", help="Run CI-suitable tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    
    # Specific test options
    parser.add_argument("--specific", type=str, help="Run specific test file or method")
    parser.add_argument("--cross-browser", type=str, choices=["smoke", "regression", "integration", "all"],
                       help="Run tests across multiple browsers")
    
    # Browser options
    parser.add_argument("--browser", type=str, default="chrome", 
                       choices=["chrome", "firefox", "edge"],
                       help="Browser to use (default: chrome)")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    
    # Information options
    parser.add_argument("--info", action="store_true", help="Show test suite information")
    
    args = parser.parse_args()
    
    # Create test runner
    runner = TestRunner()
    
    # Handle information request
    if args.info:
        runner.show_test_info()
        return 0
    
    # Determine which tests to run
    exit_code = 0
    
    if args.smoke:
        exit_code = runner.run_smoke_tests(args.browser, args.headless)
    elif args.regression:
        exit_code = runner.run_regression_tests(args.browser, args.headless)
    elif args.integration:
        exit_code = runner.run_integration_tests(args.browser, args.headless)
    elif args.tenant:
        exit_code = runner.run_tenant_tests(args.browser, args.headless)
    elif args.landlord:
        exit_code = runner.run_landlord_tests(args.browser, args.headless)
    elif args.all:
        exit_code = runner.run_all_tests(args.browser, args.headless, args.parallel)
    elif args.ci:
        exit_code = runner.run_ci_tests()
    elif args.performance:
        exit_code = runner.run_performance_tests(args.browser)
    elif args.specific:
        exit_code = runner.run_specific_test(args.specific, args.browser, args.headless)
    elif args.cross_browser:
        results = runner.run_cross_browser_tests(args.cross_browser)
        exit_code = max(results.values()) if results else 1
    else:
        # Default to smoke tests if no option specified
        print("No test suite specified. Running smoke tests by default.")
        print("Use --help to see all available options.")
        exit_code = runner.run_smoke_tests(args.browser, args.headless)
    
    # Print final result
    print("\n" + "="*50)
    if exit_code == 0:
        print("✅ TESTS COMPLETED SUCCESSFULLY")
    else:
        print("❌ TESTS FAILED")
    print("="*50)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())

