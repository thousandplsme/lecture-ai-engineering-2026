"""第3回の実測ログを保存する。リポジトリ直下で uv run python scripts/run_lec03.py。"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "lectures/03/results"
RESULTS.mkdir(parents=True, exist_ok=True)
os.chdir(ROOT)
if not os.environ.get("GEMINI_API_KEY"):
    raise SystemExit("GEMINI_API_KEY が未設定です。Codespaces secret を確認してください。")

path = ROOT / "app/agent.py"
before = "- 回答の最後に、関係する回（第N回）を示す。"
after = "- 回答の最後に、関係する回（第N回）を示し、理解を確かめる確認問題を1問出す。"
source = path.read_text(encoding="utf-8")
if source.count(before) != 1:
    raise SystemExit("指示が開始時点と異なります。再実行せず状況を確認してください。")
(RESULTS / "instructions_before.txt").write_text(source.split('INSTRUCTIONS = ', 1)[1].split('"""', 2)[1].lstrip("\\\n"), encoding="utf-8")

def run(name, *args):
    print(f"\n===== {name} =====", flush=True)
    result = subprocess.run([sys.executable, *args], text=True,
                            encoding="utf-8", errors="replace",
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(result.stdout, flush=True)
    (RESULTS / name).write_text(result.stdout, encoding="utf-8")
    if result.returncode:
        raise SystemExit(f"{name} でエラー。出力をCodexへ伝えてください。")

run("tests.txt", "-m", "pytest", "-q")
run("tools.txt", "-m", "app.agent", "--list-tools")
run("homework_levels.txt", "-m", "app.agent", "--trace",
    "AIE2026の講座の宿題にある「3レベル」とは何ですか？")
question = "LoRAとQLoRAの違いは？"
run("before.txt", "-m", "app.agent", "--trace", question)
run("quiz.txt", "-m", "app.agent", "--trace", "第2回の内容から確認問題を1問出して")
path.write_text(source.replace(before, after), encoding="utf-8")
(RESULTS / "instruction_change.txt").write_text("変更前: " + before + "\n変更後: " + after + "\n質問: " + question + "\n", encoding="utf-8")
try:
    run("after.txt", "-m", "app.agent", "--trace", question)
except BaseException:
    path.write_text(source, encoding="utf-8")
    raise
print("\n完了。結果を確認し、before.txt・after.txt・quiz.txt・homework_levels.txt・tests.txt の出力をCodexへ伝えてください。")
