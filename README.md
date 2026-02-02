# 🚀 CodeProbe-AI：實戰評量練習

本專案是一個 Todo CRUD API 的實作練習場，內建 AI 考官將輔助你驗證技術邏輯（以 PR 留言提出問題的方式進行）。

---

## 🎯 你需要完成什麼（必做）

- **CRUD**：完整實作待辦事項的新增、查詢、更新與刪除
- **DTO 模式**：API 不得直接回傳資料庫模型（Entity）
- **非同步處理**：所有資料庫 I/O 操作須使用 `async/await`
- **錯誤處理**：當 ID 不存在時，請正確回傳 `404 Not Found`

---

## ✅ API 需求（Endpoints）

請在 [src/TodoApi](src/TodoApi) 目錄下完成以下功能，並發起 Pull Request：

- **[C] Create**：`POST /api/todo`（支援標題、到期日輸入）
- **[R] Read**
  - `GET /api/todo`（清單）
  - `GET /api/todo/{id}`（單筆）
- **[U] Update**：`PUT /api/todo/{id}`（支援標題與完成狀態更新）
- **[D] Delete**：`DELETE /api/todo/{id}`

---

## 🤖 評量流程與規則（PR Review）

### 流程

1. **Fork** 本專案並建立自己的開發分支（[點我一鍵 Fork](https://github.com/AndyHuang1223/CodeProbe-AI-Todo-CRUD-Template/fork)）
2. **發起 PR**：完成後發起 PR 回到本倉庫（請勿點擊 Merge）
3. **AI 挑戰**：AI 會在 PR 下方提出 3 個針對性問題
   - 你可以直接回覆討論，或修正代碼後再次提交
4. **通過標籤**：當 AI 認可你的理解後，會自動貼上 `Review-Passed` 標籤

### 規則（避免短時間重複觸發）

- **冷卻時間**：每 10 分鐘僅觸發一次 AI 審核
  - 行為：若距離上一次 CodeProbe-AI 留言未滿冷卻時間，本次不會再次呼叫 AI 留言
  - 判定方式：以 PR 內含固定簽名「### 🤖 CodeProbe-AI 邏輯挑戰」的留言時間為依據
  - 設定/腳本位置：[scripts/ai_examiner.py](scripts/ai_examiner.py)
- **重點在理解**：若使用 AI 輔助生成代碼，請確保你能解釋其原理與取捨

---

## 技術棧（Tech Stack）

- Framework: .NET 8 Web API
- Database: Entity Framework Core with SQLite (In-Memory/File) 或 SQL Server
- Testing: AI-Powered Socratic Review
- Environment: Visual Studio 2022 / VS Code

---

## 如何開始（Getting Started）

1. Fork 本倉庫到你的 GitHub 帳號（[點我一鍵 Fork](https://github.com/AndyHuang1223/CodeProbe-AI-Todo-CRUD-Template/fork)）
2. 建立功能分支：`git checkout -b feature/my-todo-impl`
3. 開始撰寫代碼並確保可編譯與運行
4. 提交 PR 回到本倉庫
5. 等待 AI 留言並回覆討論（必要時再提交修正）

---

## 注意事項

本測驗僅作為「實作與邏輯驗證」使用。當 AI 考官判定通過後，請勿點擊 Merge。請保持 PR 開啟狀態供查閱，或直接關閉 PR 即可。
