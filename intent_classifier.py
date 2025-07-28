from typing import List, Dict, Any
import httpx
import json
from pydantic import BaseModel


class IntentResult(BaseModel):
    intent: List[str]
    reason: str


class IntentClassifier:
    """
    Intelligent Intent Classifier component that analyzes user messages
    to determine their intent using LLM API calls.
    """
    
    INTENT_LABELS = {
        "PROBLEM_DEFINITION", 
        "CONSTRAINT_ADDITION", 
        "REFINEMENT", 
        "QUESTION", 
        "UNCLEAR"
    }
    
    PROMPT_TEMPLATE = """# 命令
あなたは、ユーザーの発言の「意図」を分析する専門家です。以下の手順に従って、ユーザー発言を分析し、結果をJSON形式で出力してください。

# 手順
1. ユーザー発言を注意深く読み、その発言が何を目的としているかを分析します。
2. 分析した結果、最も合致する意図ラベルを下記の「ラベル定義」から選択します。意図が複数含まれる場合は、リスト形式で最大2つまで選択してください。
3. なぜそのラベルを選択したのか、理由を簡潔に記述します。
4. 最終的な結果を、指定されたJSON形式で出力します。

# ラベル定義
- PROBLEM_DEFINITION: ユーザーが解決したい中心的な課題を定義している。
- CONSTRAINT_ADDITION: 予算、期間などの制約や条件を追加している。
- REFINEMENT: 既存の要求をより具体的に、または修正している。
- QUESTION: 単純な質問をしている。
- UNCLEAR: 上記のいずれにも明確に分類できない。

# お手本 (Examples)
- 発言: 「AIで議事録を自動要約したいんだけど、何かいい方法ある？」
  - JSON: {"intent": ["PROBLEM_DEFINITION", "QUESTION"], "reason": "ユーザーは『議事録の自動要約』という中心課題を提示し、同時に質問している。"}
- 発言: 「いいね。ただし、利用するモデルはオープンソースのものに限定してほしい。」
  - JSON: {"intent": ["CONSTRAINT_ADDITION"], "reason": "『オープンソースに限定』という明確な制約を追加している。"}

# 分析対象
ユーザー発言: \"\"\"
{user_message}
\"\"\"

# 出力フォーマット
{"intent": [String], "reason": String}

# 出力"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "gpt-3.5-turbo"):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.client = httpx.AsyncClient()
    
    async def classify_intent(self, user_message: str) -> IntentResult:
        """
        Classify the intent of a user message.
        
        Args:
            user_message: The user's message to classify
            
        Returns:
            IntentResult containing intent labels and reasoning
        """
        prompt = self.PROMPT_TEMPLATE.format(user_message=user_message)
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 200
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = await self.client.post(
                self.api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"].strip()
            
            # Parse JSON response
            try:
                parsed = json.loads(content)
                return IntentResult(
                    intent=parsed["intent"],
                    reason=parsed["reason"]
                )
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback to UNCLEAR if parsing fails
                return IntentResult(
                    intent=["UNCLEAR"],
                    reason=f"Failed to parse LLM response: {str(e)}"
                )
                
        except httpx.RequestError as e:
            # Fallback to UNCLEAR if API call fails
            return IntentResult(
                intent=["UNCLEAR"],
                reason=f"API request failed: {str(e)}"
            )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()