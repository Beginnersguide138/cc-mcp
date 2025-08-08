# 📚 CC-MCP 正しい使い方ガイド

## ⚠️ 重要な注意事項

**CC-MCPは「セッション管理」を基盤とした対話一貫性維持システムです。**
正しく使わないと、毎回新規セッションが作成され、コンテキストが失われます。

---

## 🚫 よくある間違った使い方

```python
# ❌ 間違い：セッションIDなしで使用
await process_user_message("AIアシスタントを作りたい")
# → 新しいセッションが自動作成される

await process_user_message("予算は50万円です")  
# → また新しいセッションが作成され、前の文脈が失われる！

await process_user_message("どんな技術を使えばいい？")
# → さらに新しいセッション...前の会話内容は全て忘れられている
```

**結果**: 各メッセージが独立したセッションで処理され、会話の一貫性が完全に失われます。

---

## ✅ 正しい使い方（必須手順）

### 📋 基本的なワークフロー

```python
# ✅ 正解：明示的なセッション管理

# 1️⃣ セッションを開始（必須！）
session_info = await start_session()
session_id = session_info["session_id"]
print(f"セッション開始: {session_id}")

# 2️⃣ 同じセッションIDで対話を継続
await process_user_message(
    message="AIアシスタントを作りたい",
    session_id=session_id  # 必ずセッションIDを指定
)

await process_user_message(
    message="予算は50万円です",
    session_id=session_id  # 同じセッションIDを使用
)

await process_user_message(
    message="どんな技術を使えばいい？",
    session_id=session_id  # 継続してセッションIDを使用
)

# 3️⃣ セッションを終了（推奨）
await end_session(session_id=session_id)
```

---

## 🎯 MCPクライアント（Cline等）での実践的な使い方

### 1. 新しいタスクを開始する時

```javascript
// Step 1: 必ず最初にセッションを開始
const session = await cc_mcp.start_session();
const sessionId = session.session_id;

// Step 2: セッションIDを保持して使用
await cc_mcp.process_user_message({
    message: "ユーザーのメッセージ",
    session_id: sessionId
});
```

### 2. 長期対話での使用パターン

```javascript
class CCMCPManager {
    constructor() {
        this.currentSessionId = null;
    }
    
    // 対話開始時
    async startConversation() {
        const result = await cc_mcp.start_session();
        this.currentSessionId = result.session_id;
        console.log(`✅ CC-MCPセッション開始: ${this.currentSessionId}`);
        return this.currentSessionId;
    }
    
    // メッセージ処理
    async processMessage(message) {
        if (!this.currentSessionId) {
            await this.startConversation();
        }
        
        return await cc_mcp.process_user_message({
            message: message,
            session_id: this.currentSessionId  // 必ずセッションIDを使用
        });
    }
    
    // 対話終了時
    async endConversation() {
        if (this.currentSessionId) {
            await cc_mcp.end_session({
                session_id: this.currentSessionId
            });
            console.log(`✅ CC-MCPセッション終了: ${this.currentSessionId}`);
            this.currentSessionId = null;
        }
    }
}
```

---

## 📝 Clineでの推奨実装例

### タスク実行時の正しいフロー

```typescript
// Clineのタスク実行コンテキストで
async function executeTaskWithCCMCP(userTask: string) {
    let sessionId: string | null = null;
    
    try {
        // 1. セッション開始（タスクの最初に必ず実行）
        const sessionResult = await useMcpTool(
            "cc-mcp",
            "start_session",
            {}
        );
        sessionId = sessionResult.session_id;
        console.log(`CC-MCP Session Started: ${sessionId}`);
        
        // 2. ユーザーメッセージの処理
        const processResult = await useMcpTool(
            "cc-mcp",
            "process_user_message",
            {
                message: userTask,
                session_id: sessionId  // 必須！
            }
        );
        
        // 3. 後続の対話でも同じセッションIDを使用
        // ... 対話が続く限り、同じsessionIdを使用 ...
        
        // 4. デバッグ情報の取得（必要に応じて）
        const debugInfo = await useMcpTool(
            "cc-mcp",
            "get_debug_info",
            {
                message: userTask,
                session_id: sessionId
            }
        );
        
    } finally {
        // 5. タスク完了時にセッション終了
        if (sessionId) {
            await useMcpTool(
                "cc-mcp",
                "end_session",
                {
                    session_id: sessionId
                }
            );
            console.log(`CC-MCP Session Ended: ${sessionId}`);
        }
    }
}
```

---

## 🔧 セッション管理のベストプラクティス

### 1. セッションのライフサイクル管理

```python
# 推奨パターン：with文を使った自動管理（Python実装例）
class CCMCPSession:
    def __init__(self):
        self.session_id = None
    
    async def __aenter__(self):
        result = await start_session()
        self.session_id = result["session_id"]
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session_id:
            await end_session(self.session_id)
    
    async def process(self, message):
        return await process_user_message(message, self.session_id)

# 使用例
async with CCMCPSession() as session:
    await session.process("AIアシスタントを作りたい")
    await session.process("予算は50万円です")
    # セッション自動終了
```

### 2. セッション状態の保存と復元

```python
# セッション状態のエクスポート
context_data = await export_context(session_id=current_session_id)

# 後で復元
new_session = await start_session()
await import_context(
    json_state=json.dumps(context_data["data"]),
    session_id=new_session["session_id"]
)
```

### 3. マルチセッション管理

```python
# 複数の独立した対話を並行管理
sessions = {}

# ユーザーAのセッション
sessions["user_a"] = (await start_session())["session_id"]
await process_user_message("Webアプリを作りたい", sessions["user_a"])

# ユーザーBのセッション
sessions["user_b"] = (await start_session())["session_id"]
await process_user_message("モバイルアプリを作りたい", sessions["user_b"])

# それぞれ独立してコンテキストを維持
```

---

## 📊 セッション管理チェックリスト

### ✅ 必須項目
- [ ] タスク開始時に`start_session()`を呼んでいる
- [ ] セッションIDを変数に保存している
- [ ] 全ての`process_user_message`呼び出しでセッションIDを指定している
- [ ] タスク終了時に`end_session()`を呼んでいる

### 🎯 推奨項目
- [ ] エラーハンドリングでセッション終了を保証している
- [ ] 長時間の対話では定期的に`export_context`でバックアップ
- [ ] 必要に応じて`get_session_stats`で状態確認
- [ ] `list_sessions`で未終了セッションを監視

---

## 🚨 トラブルシューティング

### 問題1: コンテキストが保持されない
**原因**: セッションIDを指定していない、または毎回異なるセッションIDを使用
**解決**: 同じセッションIDを一貫して使用する

### 問題2: メモリ使用量が増加
**原因**: セッションを終了せずに放置
**解決**: `end_session()`を必ず呼ぶ、または定期的に`list_sessions()`で確認して不要なセッションを削除

### 問題3: 前の会話の文脈が失われる
**原因**: 新しいセッションを開始してしまった
**解決**: `export_context`で前のセッション状態を保存し、新しいセッションに`import_context`で復元

---

## 📚 まとめ

CC-MCPの価値を最大限に引き出すには：

1. **必ず`start_session()`から始める**
2. **セッションIDを一貫して使用する**
3. **タスク完了時は`end_session()`で終了する**

この3つの基本ルールを守ることで、長期対話でも文脈を完璧に維持し、AIの応答品質を飛躍的に向上させることができます。

---

## 🔗 関連ドキュメント

- [README.md](README.md) - CC-MCPの概要
- [README-ja.md](README-ja.md) - 日本語ドキュメント
- [README-zh.md](README-zh.md) - 中国語ドキュメント
- [session_manager.py](session_manager.py) - セッション管理の実装

---

**重要**: このガイドに従ってCC-MCPを使用することで、AIアシスタントの対話品質と一貫性が大幅に向上します。
