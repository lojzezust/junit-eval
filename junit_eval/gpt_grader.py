import argparse
import os
import os.path as osp
import json

import openai
from tqdm.auto import tqdm
from .config import cfg
import backoff

class GPTGrader():
    def __init__(self, api_key, system_prompt, instruction_file, max_tokens=100, temperature=0.5, engine="gpt-3.5-turbo"):
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.engine = engine

        # Read grading criteria
        with open(instruction_file, 'r') as f:
            self.instructions = f.read()

        self.client = None

    def from_config(cfg):
        return GPTGrader(
            api_key=cfg.GPT_GRADER.API_KEY,
            system_prompt=cfg.GPT_GRADER.SYSTEM_PROMPT,
            instruction_file=cfg.GPT_GRADER.INSTRUCTION_FILE,
            max_tokens=cfg.GPT_GRADER.MAX_TOKENS,
            temperature=cfg.GPT_GRADER.TEMPERATURE,
            engine=cfg.GPT_GRADER.MODEL
        )

    def grade(self, assignment_file):
        # Lazy load (to support multiprocessing)
        if self.client is None:
            self.client = openai.OpenAI(api_key=self.api_key)

        with open(assignment_file, 'r') as f:
            assignment = f.read()

        prompt = f"{self.instructions}\n\n{assignment}"

        try:
            response = self.client.chat.completions.create(
                model=self.engine,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            return response.choices[0].message.content


        return None

def gpt_grade_submissions(grader, submissions_dir, output_dir, overwrite, max_retry_time=30*60):
    os.makedirs(output_dir, exist_ok=True)
    all_submissions = sorted(f for f in os.listdir(submissions_dir) if f.endswith('.java'))

    caught_exceptions = (openai.RateLimitError, openai.APIConnectionError, openai.APIStatusError)
    grade_fn = backoff.on_exception(backoff.expo, caught_exceptions, max_time=max_retry_time)(grader.grade) # Retry for certain time

    for submission_filename in tqdm(all_submissions, desc="Processing submissions"):
        submission_path = osp.join(submissions_dir, submission_filename)
        submission_base = osp.splitext(submission_filename)[0]
        gpt_report_path = osp.join(output_dir, f"{submission_base}_gpt.txt")
        if osp.exists(gpt_report_path) and not overwrite:
            tqdm.write(f"Using cached GPT report for {submission_base}")
        else:
            gpt_output = grade_fn(submission_path)
            if gpt_output is not None:
                with open(gpt_report_path, 'w') as report_file:
                    report_file.write(gpt_output)


def get_parser(parser=None):
    if parser is None:
        parser = argparse.ArgumentParser(description="Use GPT API to grade assignments.")

    parser.add_argument('config', type=str, help='Path to the configuration file. See `https://github.com/lojzezust/junit-eval/blob/main/configs/example.yaml` for an example configuration.')
    parser.add_argument('--overwrite', action='store_true', help='Enforces running on all submissions, even if the ones already processed.')

    return parser

def main(args):
    cfg.merge_from_file(args.config)
    cfg.freeze()

    print(cfg)

    grader = GPTGrader.from_config(cfg)
    gpt_grade_submissions(grader,
        submissions_dir=cfg.SUBMISSIONS_DIR,
        output_dir=cfg.OUTPUT_DIR,
        overwrite=args.overwrite,
        max_retry_time=cfg.GPT_GRADER.MAX_RETRY_TIME)


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(args)
