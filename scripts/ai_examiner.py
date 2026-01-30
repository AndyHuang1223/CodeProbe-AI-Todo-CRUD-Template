import os
import subprocess
import json
import datetime
from openai import OpenAI

COOLDOWN_MINUTES = 10
BOT_SIGNATURE = "### 🤖 CodeProbe-AI 邏輯挑戰"
MODEL_NAME = "gpt-4o-mini"
PASS_LABEL = "Review-Passed"

api_key = os.getenv("OPENAI_API_KEY")
pr_number = os.getenv("PR_NUMBER")
base_ref = os.getenv("BASE_REF")

client = OpenAI(api_key=api_key)

def get_diff():
    try:
        if not pr_number or not base_ref:
            return ""

        subprocess.run(["git", "fetch", "origin", base_ref], check=True)
        subprocess.run(
            ["git", "fetch", "origin", f"+refs/pull/{pr_number}/head:refs/remotes/origin/pr/{pr_number}"],
            check=True,
        )

        diff = subprocess.check_output(
            ["git", "diff", f"origin/{base_ref}...origin/pr/{pr_number}", "--", ":(glob)**/*.cs"],
            encoding="utf-8",
        )
        return diff
    except Exception:
        return ""

def check_cooldown():
    try:
        result = subprocess.check_output(
            ["gh", "pr", "view", pr_number, "--json", "comments"],
            encoding="utf-8",
        )
        data = json.loads(result)
        comments = data.get("comments", [])
        bot_comments = [c for c in comments if BOT_SIGNATURE in c.get("body", "")]

        if not bot_comments:
            return True

        last_comment_str = bot_comments[-1]["createdAt"]
        last_time = datetime.datetime.strptime(last_comment_str, "%Y-%m-%dT%H:%M:%SZ")
        now_utc = datetime.datetime.utcnow()
        return (now_utc - last_time).total_seconds() / 60 >= COOLDOWN_MINUTES
    except Exception:
        return True

def ask_ai(diff_content):
    system_prompt = """
你是一位專門訓練轉職菜鳥的 .NET 導師。目前的專案是「Todo CRUD API」。

【任務】：
1. 針對學員的代碼變動提出 3 個蘇格拉底式問題（針對 DTO、Async/Await、404 處理等）。
2. 如果學員在對話中展現了正確理解，請在回答最開頭加上 [PASS] 關鍵字。

【禁止】：不給代碼，語氣鼓勵但具備挑戰性，使用繁體中文。
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"這是代碼變動：\n{diff_content}"},
        ],
        temperature=0.7,
    )
    return response.choices[0].message.content

def post_comment_and_label(content):
    is_passed = "[PASS]" in content
    clean_content = content.replace("[PASS]", "").strip()
    body = f"{BOT_SIGNATURE}\n\n{clean_content}\n\n---\n*💡 提示：冷卻時間 {COOLDOWN_MINUTES} 分鐘。*"

    with open("comment.md", "w", encoding="utf-8") as f:
        f.write(body)

    subprocess.run(["gh", "pr", "comment", pr_number, "--body-file", "comment.md"], check=True)

    if is_passed:
        subprocess.run(["gh", "label", "create", PASS_LABEL, "--color", "0E8A16", "--force"], check=False)
        subprocess.run(["gh", "pr", "edit", pr_number, "--add-label", PASS_LABEL], check=True)

def main():
    diff = get_diff()
    if not diff.strip() or not check_cooldown():
        return
    ai_response = ask_ai(diff)
    post_comment_and_label(ai_response)

if __name__ == "__main__":
    main()
