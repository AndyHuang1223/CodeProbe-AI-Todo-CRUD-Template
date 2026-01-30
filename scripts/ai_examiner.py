import os
import subprocess
import json
import datetime
from openai import OpenAI

COOLDOWN_MINUTES = 10
BOT_SIGNATURE = "### 🤖 CodeProbe-AI 邏輯挑戰"
MODEL_NAME = "gpt-4o"
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
    # 利用 gpt-4o 的高推理能力，強化審核深度
    system_prompt = """
你是一位擁有 10 年經驗的 .NET 架構師，專門負責嚴格審核初級開發者的代碼。
現在你要針對「Todo CRUD API」練習進行深度 Code Review。

### 🔍 深度審核指標 (Deep Audit)：
1. **邏輯完整性**：必須包含完整的 CRUD。檢查 PUT 是否有正確更新實體？DELETE 是否有處理回傳值？
2. **DTO 深度檢查**：不只是看有沒有 DTO，還要看學員是否在 `POST` 接收 DTO 但在 `GET` 卻漏掉轉換，或 DTO 欄位是否設計不合理。
3. **異步陷阱**：偵測是否出現了「偽非同步」（例如用了 Task 但內部跑同步方法），或漏掉 `await`。
4. **注入安全性**：確保 DbContext 是透過建構函式注入，而不是在方法內 new 出來。

### 🤖 [PASS] 判定機制：
- 只有當上述四項指標「毫無瑕疵」且「邏輯自洽」時，才能在回答開頭加上 [PASS]。
- 若有任何一項不符，請提出精準的、具備技術深度的蘇格拉底式提問，戳破學員可能的盲點。

### 語調要求：
- 專業、冷靜、一針見血，但對認真的學員保持鼓勵。
- 禁止提供代碼，僅提供邏輯引導。使用繁體中文。
""".strip()

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"請審核以下代碼變動，若完全達標請給 [PASS]，否則進行挑戰性提問：\n\n{diff_content}"}
        ],
        temperature=0.2 # 進一步降低隨機性，確保判定的一致性
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
