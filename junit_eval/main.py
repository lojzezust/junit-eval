import argparse
import junit_eval.gpt_grader as gpt_grader
import junit_eval.junit as junit
import junit_eval.merge as merge


def main():
    parser = argparse.ArgumentParser(description="Tool for evaluating Java submissions.")
    subparsers = parser.add_subparsers(dest='cmd', help='Sub-command to use', required=True)
    junit_parser = subparsers.add_parser('junit', description="Runs JUnit tests on Java submissions.")
    gpt_parser = subparsers.add_parser('gpt', description="Uses GPT API to grade Java submissions.")
    merge_parser = subparsers.add_parser('merge', description="Merge result files.")

    junit_parser = junit.get_parser(junit_parser)
    junit_parser.set_defaults(func=junit.main)

    gpt_parser = gpt_grader.get_parser(gpt_parser)
    gpt_parser.set_defaults(func=gpt_grader.main)

    merge_parser = merge.get_parser(merge_parser)
    merge_parser.set_defaults(func=merge.main)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
