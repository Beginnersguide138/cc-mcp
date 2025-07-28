# CC-MCP (Context Consistent MCP Server)

**長期的な対話一貫性を維持するためのインテリジェント・コンテキスト管理MCPサーバー**

CC-MCPは、LLM（大規模言語モデル）を活用したAIエージェントにおける長期的な対話の一貫性を保つために設計された、高度なコンテキスト管理システムです。対話の核となる目的、重要な制約条件、決定事項を階層的に管理し、AIエージェントが対話の文脈を見失うことなく一貫した応答を提供します。

## 🚀 主な機能

### 📊 階層型コンテキスト管理
- **Core Context (長期記憶)**: 問題定義の永続的保存
- **Evolving Context (中期記憶)**: 制約条件と詳細化要求の蓄積
- **Turn Context (短期記憶)**: 直近の会話履歴の維持

### 🧠 インテリジェント意図分類
- LLMを活用したユーザーメッセージの自動意図分析
- 5つのカテゴリー（PROBLEM_DEFINITION, CONSTRAINT_ADDITION, REFINEMENT, QUESTION, UNCLEAR）
- 日本語プロンプトによる高精度な分類

### 🔧 動的プロンプト合成
- 全階層のコンテキストを統合した最適プロンプト生成
- 対話の目的と制約を常に維持した応答生成
- デバッグ情報とメタデータの提供

## 🛠️ 技術仕様

### アーキテクチャ
```
[クライアントアプリケーション] <-> [MCPサーバー] <-> [LLM API]
```

### 提供MCPツール
- `process_user_message` - メッセージ処理とコンテキスト管理
- `export_context` - 会話状態のJSON出力
- `import_context` - 会話状態の復元
- `clear_context` - 全コンテキストのクリア
- `get_debug_info` - 詳細なデバッグ情報取得

### 対応LLM API
- Azure OpenAI (推奨)
- OpenAI API
- その他OpenAI互換API

## 📦 インストール

### 前提条件
- Python 3.13+
- uv パッケージマネージャー

### セットアップ
```bash
# リポジトリのクローン
git clone <repository-url>
cd cc-mcp

# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env
# .envファイルを編集してAPI設定を入力
```

### 環境変数設定
```bash
# Azure OpenAI設定例
CLASSIFIER_API_URL=https://your-resource.openai.azure.com/openai/deployments/your-model/chat/completions?api-version=2024-12-01-preview
CLASSIFIER_API_KEY=your-api-key
CLASSIFIER_MODEL=gpt-4

MAIN_API_URL=https://your-resource.openai.azure.com/openai/deployments/your-model/chat/completions?api-version=2024-12-01-preview
MAIN_API_KEY=your-api-key
MAIN_MODEL=gpt-4
```

## 🚀 使用方法

### MCPサーバーの起動
```bash
uv run main.py
```

### デモの実行
```bash
# コア機能のデモンストレーション
uv run demo.py

# テストの実行
uv run test_server.py
```

### MCP ツールの使用例

#### 1. メッセージ処理
```python
# ユーザーメッセージを処理
result = await process_user_message("AIで議事録を自動要約したいです")
print(result["response"])  # AIの応答
print(result["metadata"]["intent_classification"])  # 意図分類結果
```

#### 2. コンテキスト管理
```python
# コンテキストのエクスポート
context_json = await export_context()

# コンテキストのインポート
success = await import_context(context_json)

# コンテキストのクリア
cleared = await clear_context()
```

## 📋 データフロー

1. **受信**: ユーザーメッセージの受信
2. **分類**: インテリジェント意図分類器による分析
3. **格納**: 階層型コンテキストストアへの適切な分類・保存
4. **合成**: プロンプト合成エンジンによる統合プロンプト生成
5. **実行**: メインLLM APIへのリクエスト送信
6. **返信**: 応答とメタデータの返送

## 🧪 テスト

### 機能テスト
```bash
# モック使用のユニットテスト
uv run test_server.py

# 実際のAPI使用のライブテスト（要API設定）
uv run test_live.py

# デバッグ用テスト
uv run debug_test.py
```

### 期待される動作
- ✅ 問題定義の永続的記憶
- ✅ 制約条件の蓄積と適用
- ✅ 会話履歴の適切な維持
- ✅ 一貫したプロンプト合成
- ✅ コンテキストの永続化機能

## 🔧 設定オプション

### APIパラメータ
- `max_completion_tokens`: 応答の最大トークン数
- API認証ヘッダーの自動設定
- エラーハンドリングとフォールバック機能

### コンテキスト管理
- Turn Context の履歴保持数（デフォルト: 3ターン）
- 意図分類の信頼度しきい値
- デバッグ情報の詳細レベル

## 📚 開発者向け情報

### コアコンポーネント
- `intent_classifier.py` - 意図分類ロジック
- `context_store.py` - 階層型コンテキスト管理
- `prompt_synthesis.py` - プロンプト合成エンジン
- `main.py` - FastMCPサーバー実装

### 拡張性
- 新しい意図ラベルの追加
- カスタムプロンプトテンプレート
- 複数セッション対応
- 外部データベース連携

## 🤝 貢献

バグ報告、機能要望、プルリクエストを歓迎します。

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

---

**注意**: 本MCPサーバーは、LLM APIキーが必要です。Azure OpenAI、OpenAI等の適切なAPIアクセス権限を取得してご利用ください。
