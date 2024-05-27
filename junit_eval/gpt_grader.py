from openai import OpenAI

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

        self.client = OpenAI(api_key=self.api_key)

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
        with open(assignment_file, 'r') as f:
            assignment = f.read()

        prompt = f"{self.instructions}\n\n{assignment}"

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
