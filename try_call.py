import json
import sys

from reviewer import summarize_diff

diff_text = open(sys.argv[1], encoding="utf-8").read()
print(json.dumps(summarize_diff(diff_text), indent=2, ensure_ascii=False))