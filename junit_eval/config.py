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

# GPT grader configuration
_C.GPT_GRADER = CN()
_C.GPT_GRADER.ENABLED = False
_C.GPT_GRADER.API_KEY = None
_C.GPT_GRADER.MODEL = "gpt-3.5-turbo"
_C.GPT_GRADER.MAX_TOKENS = 1000
_C.GPT_GRADER.TEMPERATURE = 0.5
_C.GPT_GRADER.INSTRUCTION_FILE = "instructions.md"
_C.GPT_GRADER.SYSTEM_PROMPT = "You are a helpful grading assistant. You provide short and concise feedback on the submission based on the provided criteria."
_C.GPT_GRADER.MAX_RETRY_TIME = 30*60 # 30 minutes

cfg = _C
