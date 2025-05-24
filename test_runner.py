import difflib
import os
import subprocess


def run_test_cases():
    """Run compiler on all test cases and compare outputs."""

    # Base directory for test cases
    test_base_dir = "testcases - phase2"

    # Results storage
    results = []

    # Process each test case
    for i in range(1, 11):  # T01 to T10
        test_name = f"T{i:02d}"
        test_dir = os.path.join(test_base_dir, test_name)

        if not os.path.exists(test_dir):
            print(f"Warning: Test directory {test_dir} not found")
            continue

        print(f"\n{'=' * 60}")
        print(f"Running test case: {test_name}")
        print(f"{'=' * 60}")

        # Paths
        input_file = os.path.join(test_dir, "input.txt")
        expected_parse_tree = os.path.join(test_dir, "parse_tree.txt")
        expected_syntax_errors = os.path.join(test_dir, "syntax_errors.txt")

        # Create output directory
        output_dir = os.path.join(test_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        # Output files (compiler generates these with fixed names)
        output_parse_tree = os.path.join(output_dir, "parse_tree.txt")
        output_syntax_errors = os.path.join(output_dir, "syntax_errors.txt")

        # Run the compiler
        try:
            cmd = [
                "python", "compiler.py",
                "--input-file", input_file,
                "--output-dir", output_dir
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error running compiler: {result.stderr}")
                print(f"Stdout: {result.stdout}")
                results.append({
                    'test': test_name,
                    'status': 'FAILED',
                    'error': f'Compiler execution failed: {result.stderr}',
                    'parse_tree_match': False,
                    'syntax_errors_match': False
                })
                continue

        except Exception as e:
            print(f"Exception running compiler: {e}")
            results.append({
                'test': test_name,
                'status': 'FAILED',
                'error': str(e),
                'parse_tree_match': False,
                'syntax_errors_match': False
            })
            continue

        # Compare outputs
        parse_tree_match = compare_files(output_parse_tree, expected_parse_tree, f"{test_name} Parse Tree")

        # Check syntax errors - the file should always exist after compilation
        syntax_errors_match = compare_files(output_syntax_errors, expected_syntax_errors, f"{test_name} Syntax Errors")

        # Store results
        results.append({
            'test': test_name,
            'status': 'PASSED' if parse_tree_match and syntax_errors_match else 'FAILED',
            'parse_tree_match': parse_tree_match,
            'syntax_errors_match': syntax_errors_match
        })

    # Generate report
    generate_report(results)


def compare_files(generated_file, expected_file, description):
    """Compare two files and report differences."""

    if not os.path.exists(generated_file):
        print(f"❌ {description}: Generated file not found")
        return False

    if not os.path.exists(expected_file):
        print(f"❌ {description}: Expected file not found")
        return False

    with open(generated_file, 'r', encoding='utf-8') as f:
        generated_content = f.read()

    with open(expected_file, 'r', encoding='utf-8') as f:
        expected_content = f.read()

    # Normalize line endings and strip trailing whitespace
    generated_lines = [line.rstrip() for line in generated_content.splitlines()]
    expected_lines = [line.rstrip() for line in expected_content.splitlines()]

    # Remove empty lines at the end
    while generated_lines and generated_lines[-1] == '':
        generated_lines.pop()
    while expected_lines and expected_lines[-1] == '':
        expected_lines.pop()

    if generated_lines == expected_lines:
        print(f"✅ {description}: MATCH")
        return True
    else:
        print(f"❌ {description}: MISMATCH")

        # Show first few differences
        diff = difflib.unified_diff(
            expected_lines,
            generated_lines,
            fromfile='Expected',
            tofile='Generated',
            lineterm='',
            n=3
        )

        diff_lines = list(diff)
        max_lines = 50

        if len(diff_lines) > max_lines:
            print(f"Showing first {max_lines} lines of differences:")
            for line in diff_lines[:max_lines]:
                print(line)
            print(f"... and {len(diff_lines) - max_lines} more lines")
        else:
            for line in diff_lines:
                print(line)

        # Show line counts
        print(f"\nExpected: {len(expected_lines)} lines")
        print(f"Generated: {len(generated_lines)} lines")

        return False


def generate_report(results):
    """Generate a comprehensive accuracy report."""

    print("\n" + "=" * 80)
    print("FINAL REPORT")
    print("=" * 80)

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['status'] == 'PASSED')
    parse_tree_matches = sum(1 for r in results if r.get('parse_tree_match', False))
    syntax_error_matches = sum(1 for r in results if r.get('syntax_errors_match', False))

    print(f"\nTotal Test Cases: {total_tests}")
    print(f"Passed: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)")
    print(
        f"Failed: {total_tests - passed_tests}/{total_tests} ({(total_tests - passed_tests) / total_tests * 100:.1f}%)")

    print(f"\nParse Tree Accuracy: {parse_tree_matches}/{total_tests} ({parse_tree_matches / total_tests * 100:.1f}%)")
    print(
        f"Syntax Error Accuracy: {syntax_error_matches}/{total_tests} ({syntax_error_matches / total_tests * 100:.1f}%)")

    print("\nDetailed Results:")
    print("-" * 80)
    print(f"{'Test Case':<12} {'Status':<10} {'Parse Tree':<15} {'Syntax Errors':<15}")
    print("-" * 80)

    for result in results:
        parse_tree_status = "✅ Match" if result.get('parse_tree_match', False) else "❌ Mismatch"
        syntax_error_status = "✅ Match" if result.get('syntax_errors_match', False) else "❌ Mismatch"

        if 'error' in result:
            print(f"{result['test']:<12} {result['status']:<10} {'ERROR':<15} {'ERROR':<15}")
            print(f"  └─ Error: {result['error']}")
        else:
            print(f"{result['test']:<12} {result['status']:<10} {parse_tree_status:<15} {syntax_error_status:<15}")

    # Save report to file
    with open("test_report.txt", "w") as f:
        f.write("COMPILER TEST REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Total Test Cases: {total_tests}\n")
        f.write(f"Passed: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)\n")
        f.write(
            f"Failed: {total_tests - passed_tests}/{total_tests} ({(total_tests - passed_tests) / total_tests * 100:.1f}%)\n\n")
        f.write(
            f"Parse Tree Accuracy: {parse_tree_matches}/{total_tests} ({parse_tree_matches / total_tests * 100:.1f}%)\n")
        f.write(
            f"Syntax Error Accuracy: {syntax_error_matches}/{total_tests} ({syntax_error_matches / total_tests * 100:.1f}%)\n\n")

        f.write("Detailed Results:\n")
        f.write("-" * 80 + "\n")
        for result in results:
            f.write(f"{result['test']}: {result['status']}\n")
            if 'error' in result:
                f.write(f"  Error: {result['error']}\n")
            else:
                f.write(f"  Parse Tree: {'Match' if result.get('parse_tree_match', False) else 'Mismatch'}\n")
                f.write(f"  Syntax Errors: {'Match' if result.get('syntax_errors_match', False) else 'Mismatch'}\n")
            f.write("\n")

    print(f"\nReport saved to: test_report.txt")

    # Also save a CSV for easier analysis
    with open("test_results.csv", "w") as f:
        f.write("Test Case,Status,Parse Tree Match,Syntax Errors Match,Notes\n")
        for result in results:
            notes = result.get('error', '') if 'error' in result else ''
            f.write(
                f"{result['test']},{result['status']},{result.get('parse_tree_match', False)},{result.get('syntax_errors_match', False)},\"{notes}\"\n")

    print(f"CSV results saved to: test_results.csv")


if __name__ == "__main__":
    run_test_cases()
