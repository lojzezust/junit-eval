import os
import os.path as osp
from pathlib import Path
import shutil
import subprocess
import tempfile
import argparse
from tqdm.auto import tqdm
import re

from .config import cfg

class JUnitEval():
    def __init__(self, submissions_dir, class_name, unit_tests_dir, output_dir, libs_dir,
                 resources_dir=None,
                 java_compile_cmd=cfg.JAVA_COMPILE_CMD,
                 java_run_cmd=cfg.JAVA_RUN_CMD,
                 success_regex=cfg.SUCCESS_REGEX,
                 failure_regex=cfg.FAILURE_REGEX):
        self.submissions_dir = submissions_dir
        self.class_name = class_name
        self.unit_tests_dir = unit_tests_dir
        self.output_dir = output_dir
        self.libs_dir = libs_dir
        self.resources_dir = resources_dir
        self.java_compile_cmd = java_compile_cmd
        self.java_run_cmd = java_run_cmd
        self.success_regex = re.compile(success_regex)
        self.failure_regex = re.compile(failure_regex)

    @classmethod
    def from_config(cls, cfg):
        return cls(
            submissions_dir=cfg.SUBMISSIONS_DIR,
            class_name=cfg.CLASS_NAME,
            unit_tests_dir=cfg.UNIT_TESTS_DIR,
            output_dir=cfg.OUTPUT_DIR,
            libs_dir=cfg.LIBS_DIR,
            resources_dir=cfg.RESOURCES_DIR,
            java_compile_cmd=cfg.JAVA_COMPILE_CMD,
            java_run_cmd=cfg.JAVA_RUN_CMD,
            success_regex=cfg.SUCCESS_REGEX,
            failure_regex=cfg.FAILURE_REGEX
        )

    def compile_java_file(self, file_path, classpath):
        compile_cmd = [self.java_compile_cmd, '-encoding', 'utf8', '-cp', classpath, file_path]
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        return result.returncode == 0, result.stderr

    def run_java_class(self, class_name, classpath, working_dir):
        cur_dir = os.getcwd()
        os.chdir(working_dir)
        run_cmd = [self.java_run_cmd, '-Dfile.encoding=UTF8', '-cp', classpath,
                   'org.junit.runner.JUnitCore', class_name]
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        os.chdir(cur_dir)
        return result.returncode == 0, result.stdout + result.stderr

    def process_submission(self, submission_file):
        submission_name = osp.basename(submission_file)
        submission_base = osp.splitext(submission_name)[0]

        # Collect all JAR files in the libs directory
        libs = [str(p.absolute()) for p in Path(self.libs_dir).glob('*.jar')]


        # Create a temporary directory for this submission
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy submission to temporary directory
            temp_submission_path = osp.join(temp_dir, f"{self.class_name}.java")
            shutil.copy(submission_file, temp_submission_path)

            class_path = os.pathsep.join(libs + [temp_dir])

            # Copy resources (all files/folders inside resources dir)
            if self.resources_dir is not None:
                shutil.copytree(self.resources_dir, temp_dir, dirs_exist_ok=True)

            # Compile the submission
            compile_success, compile_errors = self.compile_java_file(temp_submission_path, class_path)

            # Prepare the report
            report_lines = [f"Submission: {submission_name}\n"]

            if not compile_success:
                report_lines.append("Submission Compilation Failed")
                report_lines.append(compile_errors)
            else:
                # Copy all unit test files to the temporary directory
                for test_file in os.listdir(self.unit_tests_dir):
                    shutil.copy(osp.join(self.unit_tests_dir, test_file), temp_dir)

                # Compile unit tests
                test_files = sorted(f for f in os.listdir(self.unit_tests_dir) if 'Test' in f and f.endswith('.java')) # TODO: better naming scheme?
                test_report_lines = []
                successful_tests = 0
                failed_tests_output = []
                for test_file in test_files:
                    test_path = osp.join(temp_dir, test_file)
                    success, compile_errors = self.compile_java_file(test_path, class_path)
                    test_report_lines.append(f"\n---- Test: {test_file} ----\n")
                    if not success:
                        test_report_lines.append(f"Test {test_file} Compilation Failed")
                        test_report_lines.append(compile_errors)
                        report_lines.append(f"Test {test_file}: Compilation error")
                        continue


                    # Run unit test
                    test_class = osp.splitext(test_file)[0]
                    run_success, output = self.run_java_class(test_class, class_path, temp_dir)
                    if run_success:
                        # Store successful test results
                        successful_tests += 1
                        match = self.success_regex.search(output)
                        if match:
                            n = int(match.group(1))
                            report_lines.append(f"Test {test_file}: {n}/{n} (100%)")
                        else:
                            report_lines.append(f"Test {test_file}: 100%")
                        test_report_lines.append("OK")
                    else:
                        # Collect failed test results (number of failed, error messages)
                        match = self.failure_regex.search(output)
                        if match:
                            run = int(match.group(1))
                            nok = int(match.group(2))
                            ok = run - nok
                            report_lines.append(f"Test {test_file}: {ok}/{run} ({ok/(run)*100:.1f}%)")
                        else:
                            report_lines.append(f"Test {test_file}: ?/?")

                        test_report_lines.append("FAILED. Errors:\n")
                        test_report_lines.append(output)


                # Record the results
                report_lines.insert(1, "---- Overall results ----\n")
                report_lines.insert(2, f"Number of Successful Tests: {successful_tests}/{len(test_files)}\n")
                report_lines.extend(test_report_lines)

            # Write the report to a file
            report_path = osp.join(self.output_dir, f"{submission_base}.txt")
            with open(report_path, 'w') as report_file:
                report_file.write("\n".join(report_lines))

    def process_all_submissions(self):
        # Ensure output directory exists
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

        all_submissions = [f for f in os.listdir(self.submissions_dir) if f.endswith('.java')]
        for submission_file in tqdm(all_submissions, "Processing submissions"):
            self.process_submission(osp.join(self.submissions_dir, submission_file))

def main():
    parser = argparse.ArgumentParser(description="Run Java unit tests on submissions.")
    parser.add_argument('config', type=str, help='Path to the configuration file. See `configs/example.yaml` for an example.')

    args = parser.parse_args()

    cfg.merge_from_file(args.config)
    cfg.freeze()

    print(cfg)

    evaluator = JUnitEval.from_config(cfg)
    evaluator.process_all_submissions()

if __name__ == "__main__":
    main()
