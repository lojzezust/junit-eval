from setuptools import setup, find_packages

setup(
    name='junit-eval',
    version='0.1.7',
    packages=find_packages(),
    install_requires=[
        'yacs',
        'tqdm',
        'openai',
        'backoff'
    ],
    entry_points={
        'console_scripts': [
            'junit-eval=junit_eval.main:main'
        ],
    },
    url='https://github.com/lojzezust/junit-eval',  # Replace with your repo URL
    author='Lojze Zust',
    author_email='lojze.zust@gmail.com',
    description='Simple CLI tool for batch evaluation of JUnit 4 tests',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
)
