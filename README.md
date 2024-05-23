
<table align="center">
    <tr>
        <td align="center"><img src="images/icon.png"/></td>
        <td align="left"><b>junit-eval</b>: A simple JUnit evaluation tool for batch processing of multiple implementations. Suitable for automated grading of assignments.</td>
    </tr>
</table>







## Features

- Running multiple test classes on a large number of submissions
- Counting and reporting the number of successful tests and test cases
- Reporting source compilation errors and test compilation errors
- Support for concurrent processing of multiple files
- Experimental and optional feature: submission analysis and comments using OpenAI gpt API

> [!CAUTION]
> No internal sandboxing or security features are currently implemented. Make sure you trust the source code you are trying to evaluate or run it in a sandboxed environment (e.g. virtual machine).

## Getting started

**Step 1**: Install the package using pip
```bash
pip install git+https://github.com/lojzezust/junit-eval.git
```

**Step 2**: Prepare the test and the configuration file for your project

1. Place all the unit tests (and any dependencies) in a single directory. Place resources in a single directory. Place all the required libraries (.jar files) in single directory. Your project might look something like this:
```
.
├── tests/
│   ├── Test01.java
│   └── ...
├── submissions/
│   ├── Name1=email2=...=Main.java
│   └── ...
├── res/
│   └── viri/
│       ├── input1.txt
│       └── ...
├── lib/
│   ├── hamcrest-core-1.3.jar
│   └── junit-4.13.2.jar
└── gpt-instructions.txt
```
2. Create a configuration YAML file. You may use [`configs/example.yaml`](configs/example.yaml) as a template. Most important fields:
    - `SUBMISSIONS_DIR`: root directory of your submissions
    - `CLASS_NAME`: main class name of the submission. Used for renaming submissions file to the correct filename, matching the class name.
    - `UNIT_TESTS_DIR`: location of you JAVA JUnit test files.
    - `RESOURCES_DIR`: location of the resources dir (`res` in above example). The JAVA program will understand paths relative to this directory (e.g. `viri/input1.txt`).
    - `LIBS_DIR`: Libraries required by the tests and/or submissions. These will be used during every compilation and execution.
    - `JAVA_COMPILE_CMD` and `JAVA_RUN_CMD`: Location of `javac` and `java` binaries to use. If the binaries are located on the system path, you can just set these to `javac` and `java`.
    - `OUTPUT.SUMMARY`: enables/disables summaries in the reports (number of points for each test, etc.)
    - `OUTPUT.DETAILED`: enables/disables detailed reports for each of the test files (including error and assertion messages)
    - `GPT_GRADER`: configuration for the optional GPT analysis tool. You need an OpenAI API key to use this feature.


**Step 3**: Run the evaluator

```bash
junit-eval config.yaml
```
> [!TIP]
> Use the `--num-workers` argument to enable parallel processing.



### Manual installation

If you wish to modify the code, clone and install the package in editable mode:
```bash
git clone https://github.com/lojzezust/junit-eval.git

cd junit-eval
pip install -e .
```

## How it works

For each of the submissions in the submission directory the following steps are performed:
1. A temporary directory is created. The following files are copied to the temp location:
    - Submission source code
    - Contents of the tests directory
    - Contents of the resources directory
2. Source file is compiled using `javac`. If compilation is not successful end the process and report the compilation error.
3. Find all test classes (files in the tests directory containing "Test" in the name). For each test class:
    1. Compile the test class against the assignment. In case of compilation failure the test counts as failed and compilation error is reported.  
    **Note**: Not implemented methods/classes will cause compilation errors. It is thus recommended to separate test files into unit-sized chunks that test a single aspect of the assignment.
    2. Run the test cases and report the number of passed tests and the encountered errors.
    3. (Optional) Analyze the source code against a grading criteria using LLMs (GPT API) and add the results to the report
    4. Output the report for the assignment.


## GPT Analysis of Submissions

To use this feature you need an OpenAI API key. 
1. Enable the feature by setting `GPT_GRADER.ENABLED` field to `True`.
2. Enter your API key in the `GPT_GRADER.API_KEY` field.
3. Prepare instructions for grading in a file and link to it in the `GPT_GRADER.INSTRUCTION_FILE` field. The instructions might look something like this.
```text
Score the provided JAVA program using the following criteria. You may use half points. Keep the comments short.

Criteria:
Ex. 1:
(1p) Methods X and X are implemented and perform Y
...

```
4. Run junit-eval as normal. GPT analysis results will be appended to the end of the report.

> [!WARNING]
> Depending on the length of instructions and submissions, and the selected model, token use may be large. It is always recommended to test on a small sample, to preview the expected costs and quality of the responses.

## Limitations

This is a quickly implemented project with a few caveats and limitations:
- No security features are currently implemented.
- Currently limited to single-file programs/submissions.
- Some features are hard-coded to our specific use-case. Feel free to adapt the code if you need.
    - This includes the expectation that submissions are a named a specific way exported by Moodle (`name=email=*.java`). The script extracts the email field which is stored in the final CSV report.
