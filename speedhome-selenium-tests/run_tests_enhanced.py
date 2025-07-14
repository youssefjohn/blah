#!/usr/bin/env python3
"""
Enhanced test runner for SpeedHome Selenium tests
Provides multiple execution modes and comprehensive reporting
"""
import os
import sys
import argparse
import subprocess
import time
from datetime import datetime

class SpeedHomeTestRunner:
    """Enhanced test runner for SpeedHome Selenium test suite"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.reports_dir = os.path.join(self.base_dir, "reports")
        self.screenshots_dir = os.path.join(self.reports_dir, "screenshots")
        
        # Ensure directories exist
        os.makedirs(self.reports_dir, exist_ok=True)
        os.makedirs(self.screenshots_dir, exist_ok=True)
    
    def run_tests(self, test_suite=None, browser="chrome", headless=True, parallel=False, 
                  markers=None, verbose=True, html_report=True):
        """
        Run tests with specified configuration
        
        Args:
            test_suite: Specific test file or directory to run
            browser: Browser to use (chrome, firefox, edge)
            headless: Run in headless mode
            parallel: Run tests in parallel
            markers: Pytest markers to filter tests
            verbose: Verbose output
            html_report: Generate HTML report
        """
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test suite
        if test_suite:
            cmd.append(test_suite)
        else:
            cmd.append("tests/")
        
        # Add browser option
        cmd.extend(["--browser", browser])
        
        # Add headless option
        if headless:
            cmd.append("--headless")
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add markers
        if markers:
            cmd.extend(["-m", markers])
        
        # Add verbosity
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add HTML report
        if html_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = os.path.join(self.reports_dir, f"report_{timestamp}.html")
            cmd.extend(["--html", html_file, "--self-contained-html"])
        
        # Add JUnit XML report
        xml_file = os.path.join(self.reports_dir, "junit_results.xml")
        cmd.extend(["--junitxml", xml_file])
        
        # Add other useful options
        cmd.extend([
            "--tb=short",  # Short traceback format
            "--strict-markers",  # Strict marker checking
            "--disable-warnings",  # Disable warnings for cleaner output
        ])
        
        print(f"🚀 Running SpeedHome Selenium Tests")
        print(f"📁 Test Suite: {test_suite or 'All tests'}")
        print(f"🌐 Browser: {browser}")
        print(f"👁️  Headless: {headless}")
        print(f"⚡ Parallel: {parallel}")
        print(f"🏷️  Markers: {markers or 'All'}")
        print(f"📊 HTML Report: {html_report}")
        print("-" * 50)
        
        # Set environment variables
        env = os.environ.copy()
        env["BROWSER"] = browser
        env["HEADLESS"] = str(headless).lower()
        
        # Run tests
        start_time = time.time()
        try:
            result = subprocess.run(cmd, cwd=self.base_dir, env=env, 
                                  capture_output=False, text=True)
            
            end_time = time.time()
            duration = end_time - start_time
            
            print("-" * 50)
            print(f"⏱️  Test Duration: {duration:.2f} seconds")
            
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print(f"❌ Tests failed with exit code: {result.returncode}")
            
            # Show report locations
            if html_report:
                print(f"📊 HTML Report: {html_file}")
            print(f"📋 JUnit XML: {xml_file}")
            print(f"📸 Screenshots: {self.screenshots_dir}")
            
            return result.returncode
            
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
            return 130
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return 1

def main():
    """Main entry point for test runner"""
    parser = argparse.ArgumentParser(
        description="Enhanced SpeedHome Selenium Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --smoke                    # Run smoke tests
  %(prog)s --regression --parallel    # Run regression tests in parallel
  %(prog)s --all --browser firefox    # Run all tests with Firefox
  %(prog)s --auth --no-headless       # Run auth tests with visible browser
  %(prog)s tests/test_simple_homepage.py  # Run specific test file
        """
    )
    
    # Test suite options
    suite_group = parser.add_mutually_exclusive_group()
    suite_group.add_argument("--smoke", action="store_true",
                           help="Run smoke tests only")
    suite_group.add_argument("--regression", action="store_true",
                           help="Run regression tests")
    suite_group.add_argument("--integration", action="store_true",
                           help="Run integration tests")
    suite_group.add_argument("--auth", action="store_true",
                           help="Run authentication tests")
    suite_group.add_argument("--search", action="store_true",
                           help="Run search and filtering tests")
    suite_group.add_argument("--booking", action="store_true",
                           help="Run booking and viewing tests")
    suite_group.add_argument("--all", action="store_true",
                           help="Run all tests")
    
    # Browser options
    parser.add_argument("--browser", choices=["chrome", "firefox", "edge"],
                       default="chrome", help="Browser to use for testing")
    
    # Execution options
    parser.add_argument("--no-headless", action="store_true",
                       help="Run with visible browser (not headless)")
    parser.add_argument("--parallel", action="store_true",
                       help="Run tests in parallel")
    parser.add_argument("--no-html", action="store_true",
                       help="Skip HTML report generation")
    parser.add_argument("--quiet", action="store_true",
                       help="Quiet output (less verbose)")
    
    # Specific test file
    parser.add_argument("test_file", nargs="?",
                       help="Specific test file to run")
    
    args = parser.parse_args()
    
    # Initialize test runner
    runner = SpeedHomeTestRunner()
    
    # Determine test suite
    test_suite = None
    markers = None
    
    if args.test_file:
        test_suite = args.test_file
    elif args.smoke:
        markers = "smoke"
    elif args.regression:
        markers = "regression"
    elif args.integration:
        markers = "integration"
    elif args.auth:
        test_suite = "tests/test_authentication_flows.py"
    elif args.search:
        test_suite = "tests/test_property_search_advanced.py"
    elif args.booking:
        test_suite = "tests/test_property_booking_flows.py"
    elif args.all:
        test_suite = "tests/"
    else:
        # Default to smoke tests
        markers = "smoke"
        print("No specific test suite specified, running smoke tests by default")
    
    # Run tests
    exit_code = runner.run_tests(
        test_suite=test_suite,
        browser=args.browser,
        headless=not args.no_headless,
        parallel=args.parallel,
        markers=markers,
        verbose=not args.quiet,
        html_report=not args.no_html
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

