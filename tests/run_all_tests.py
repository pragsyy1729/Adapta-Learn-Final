#!/usr/bin/env python3
"""
Comprehensive API Test Runner for AdaptaLearn Backend
This script runs all API test modules and generates a summary report.
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_single_test(test_file):
    """Run a single test file and return results"""
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest',
            test_file,
            '-v',
            '--tb=short'
        ], capture_output=True, text=True, cwd=os.getcwd())

        # Try to read the JSON report
        report_data = {}
        # Note: JSON report disabled due to pytest version compatibility
        # if os.path.exists('temp_report.json'):
        #     try:
        #         with open('temp_report.json', 'r') as f:
        #             report_data = json.load(f)
        #     except:
        #         pass
        #     finally:
        #         os.remove('temp_report.json')

        return {
            'file': test_file,
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'report': report_data
        }
    except Exception as e:
        return {
            'file': test_file,
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'report': {}
        }

def main():
    """Main test runner function"""
    print("🚀 Starting AdaptaLearn API Test Suite")
    print("=" * 50)

    # Get all test files
    tests_dir = Path(__file__).parent / 'tests'
    test_files = list(tests_dir.glob('test_*_apis.py'))

    if not test_files:
        print("❌ No test files found in tests/ directory")
        return 1

    print(f"📋 Found {len(test_files)} test files:")
    for test_file in test_files:
        print(f"  • {test_file.name}")
    print()

    # Run all tests
    results = []
    total_passed = 0
    total_failed = 0
    total_errors = 0

    for test_file in sorted(test_files):
        print(f"🔍 Running {test_file.name}...")
        result = run_single_test(str(test_file))
        results.append(result)

        # Parse results from return code (simplified without JSON report)
        if result['returncode'] == 0:
            total_passed += 1  # Assume all tests passed if return code is 0
            total_failed += 0
            total_errors += 0
        else:
            # Count failures from output (rough estimate)
            if 'FAILED' in result['stdout']:
                failed_count = result['stdout'].count('FAILED')
                total_failed += failed_count
            if 'ERROR' in result['stdout']:
                error_count = result['stdout'].count('ERROR')
                total_errors += error_count

        if result['returncode'] != 0:
            print(f"   📄 Output: {result['stdout'][-200:]}...")
            if result['stderr']:
                print(f"   ⚠️  Error: {result['stderr'][-200:]}...")
        print()

    # Generate summary report
    print("=" * 50)
    print("📊 TEST SUMMARY REPORT")
    print("=" * 50)

    successful_tests = sum(1 for r in results if r['returncode'] == 0)
    failed_tests = len(results) - successful_tests

    print(f"Total Test Files: {len(results)}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {failed_tests}")
    print()

    if total_passed > 0 or total_failed > 0 or total_errors > 0:
        print("Individual Test Results:")
        print(f"  ✅ Tests Passed: {total_passed}")
        print(f"  ❌ Tests Failed: {total_failed}")
        print(f"  ⚠️  Test Errors: {total_errors}")
        print()

    # Detailed results for failed tests
    failed_results = [r for r in results if r['returncode'] != 0]
    if failed_results:
        print("❌ FAILED TEST DETAILS:")
        for result in failed_results:
            print(f"  • {result['file']}")
            if result['stderr']:
                print(f"    Error: {result['stderr'].strip()}")
        print()

    # Save detailed report
    report_data = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': len(results),
            'successful': successful_tests,
            'failed': failed_tests,
            'total_passed': total_passed,
            'total_failed': total_failed,
            'total_errors': total_errors
        },
        'results': results
    }

    report_file = 'test_report.json'
    with open(report_file, 'w') as f:
        json.dump(report_data, f, indent=2)

    print(f"📄 Detailed report saved to: {report_file}")

    # Final status
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"⚠️  {failed_tests} test file(s) failed. Check the report for details.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
