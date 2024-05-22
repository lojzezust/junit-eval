from yacs.config import CfgNode as CN

_C = CN()

_C.CLASS_NAME = "Main"
_C.SUBMISSIONS_DIR = "submissions"
_C.UNIT_TESTS_DIR = "tests"
_C.RESOURCES_DIR = None
_C.OUTPUT_DIR = "output"
_C.LIBS_DIR = "lib"
_C.JAVA_COMPILE_CMD = "javac"
_C.JAVA_RUN_CMD = "java"
_C.DEFAULT_JAVA_CP = "."
_C.SUCCESS_REGEX = r"OK \((\d+) tests\)"
_C.FAILURE_REGEX = r"Tests run: (\d+),  Failures: (\d+)"

# Output configuration
_C.OUTPUT = CN()
_C.OUTPUT.SUMMARY = True # Summarized test results
_C.OUTPUT.DETAILED = True # Detailed test results (with errors)

cfg = _C
