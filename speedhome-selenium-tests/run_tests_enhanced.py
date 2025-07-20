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
                  markers=None, keyword=None, verbose=True, html_report=True):
        """
        Run tests with specified configuration
        """
        
        # Build pytest command
        cmd = ["python3", "-m", "pytest"]
        
        if test_suite:
            cmd.append(test_suite)
        else:
            cmd.append("tests/")
        
        cmd.extend(["--browser", browser])
        
        if headless:
            cmd.append("--headless")
        
        if parallel:
            cmd.extend(["-n", "auto"])
        
        if markers:
            cmd.extend(["-m", markers])

        if keyword:
            cmd.extend(["-k", keyword])
        
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        if html_report:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_file = os.path.join(self.reports_dir, f"report_{timestamp}.html")
            cmd.extend(["--html", html_file, "--self-contained-html"])
        
        xml_file = os.path.join(self.reports_dir, "junit_results.xml")
        cmd.extend(["--junitxml", xml_file])
        
        cmd.extend([
            "--tb=short",
            "--strict-markers",
            "--disable-warnings",
        ])
        
        print(f"🚀 Running SpeedHome Selenium Tests")
        print(f"📁 Test Suite: {test_suite or 'All tests'}")
        print(f"🌐 Browser: {browser}")
        print(f"👁️  Headless: {headless}")
        print(f"⚡ Parallel: {parallel}")
        if markers:
            print(f"🏷️  Markers: {markers}")
        if keyword:
            print(f"🔑 Keyword: {keyword}")
        print(f"📊 HTML Report: {html_report}")
        print("-" * 50)
        
        env = os.environ.copy()
        env["BROWSER"] = browser
        env["HEADLESS"] = str(headless).lower()
        
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
  %(prog)s --smoke                                  # Run smoke tests
  %(prog)s --regression --parallel                   # Run regression tests in parallel
  %(prog)s -k "test_login" --no-headless            # Run tests with 'test_login' in their name
  %(prog)s tests/test_simple_homepage.py             # Run specific test file
        """
    )
    
    suite_group = parser.add_mutually_exclusive_group()
    suite_group.add_argument("--smoke", action="store_true", help="Run smoke tests only")
    suite_group.add_argument("--regression", action="store_true", help="Run regression tests")
    suite_group.add_argument("--all", action="store_true", help="Run all tests")
    
    parser.add_argument("-k", "--keyword", help="Pytest keyword expression to select tests")
    parser.add_argument("--browser", choices=["chrome", "firefox", "edge"], default="chrome", help="Browser to use for testing")
    parser.add_argument("--no-headless", action="store_true", help="Run with visible browser (not headless)")
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--no-html", action="store_true", help="Skip HTML report generation")
    parser.add_argument("--quiet", action="store_true", help="Quiet output (less verbose)")
    parser.add_argument("test_file", nargs="?", help="Specific test file to run")
    
    args = parser.parse_args()
    
    # --- AUTOMATED DATABASE SEEDING ---
    print("🌱 Seeding database with test data...")
    try:
        seeder_path = os.path.join(os.path.dirname(__file__), 'scripts', 'seed_database.py')
        subprocess.run([sys.executable, seeder_path], check=True)
        print("✅ Database seeded successfully.")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"❌ CRITICAL: Failed to seed database. Aborting tests. Error: {e}")
        sys.exit(1)
    print("-" * 50)
    # --- END OF SEEDING SECTION ---

    runner = SpeedHomeTestRunner()
    
    test_suite = None
    markers = None
    keyword = args.keyword

    # --- UPDATED LOGIC TO PRIORITIZE FILTERS ---
    if args.test_file:
        test_suite = args.test_file
    elif keyword:
        # If a keyword is provided, we don't use markers
        markers = None
    elif args.smoke:
        markers = "smoke"
    elif args.regression:
        markers = "regression"
    elif args.all:
        test_suite = "tests/"
    else:
        # Default to smoke tests if no other filter is provided
        markers = "smoke"
        print("No specific test suite specified, running smoke tests by default")
    
    exit_code = runner.run_tests(
        test_suite=test_suite,
        browser=args.browser,
        headless=not args.no_headless,
        parallel=args.parallel,
        markers=markers,
        keyword=keyword,
        verbose=not args.quiet,
        html_report=not args.no_html
    )
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
