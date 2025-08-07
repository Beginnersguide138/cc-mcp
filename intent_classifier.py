from typing import List, Dict, Any
import requests
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
  - JSON: {{"intent": ["PROBLEM_DEFINITION", "QUESTION"], "reason": "ユーザーは『議事録の自動要約』という中心課題を提示し、同時に質問している。"}}
- 発言: 「いいね。ただし、利用するモデルはオープンソースのものに限定してほしい。」
  - JSON: {{"intent": ["CONSTRAINT_ADDITION"], "reason": "『オープンソースに限定』という明確な制約を追加している。"}}

# 分析対象
ユーザー発言: \"\"\"
{user_message}
\"\"\"

# 出力
以下のJSON形式で必ず応答してください：
{{"intent": [String], "reason": String}}

JSON:"""
    
    def __init__(self, api_url: str, api_key: str, model: str = "gpt-3.5-turbo"):
        # Ensure the URL includes the chat/completions endpoint
        if not api_url.endswith('/chat/completions'):
            if api_url.endswith('/'):
                self.api_url = api_url + 'chat/completions'
            else:
                self.api_url = api_url + '/chat/completions'
        else:
            self.api_url = api_url
        self.api_key = api_key
        self.model = model
    
    def classify_intent(self, user_message: str) -> IntentResult:
        """
        Classify the intent of a user message.
        
        Args:
            user_message: The user's message to classify
            
        Returns:
            IntentResult containing intent labels and reasoning
        """
        import logging
        logger = logging.getLogger(__name__)
        
        prompt = self.PROMPT_TEMPLATE.format(user_message=user_message)
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.1
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Debug logging
        logger.info(f"🔧 Intent Classification Debug:")
        logger.info(f"  API URL: {self.api_url}")
        logger.info(f"  Model: {self.model}")
        logger.info(f"  API Key: {'***' if self.api_key else '(empty)'}")
        logger.info(f"  User Message: {user_message}")
        
        try:
            # Use requests instead of httpx with increased timeout
            logger.info(f"📡 Sending request to Ollama...")
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30,  # Further increased timeout for Ollama's large model
                verify=False if self.api_url.startswith('http://') else True
            )
            logger.info(f"✅ Response received: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"🔍 Full Response JSON: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # Handle Ollama's specific response structure
            message = result["choices"][0]["message"]
            content = message.get("content", "").strip()
            reasoning = message.get("reasoning", "").strip()
            
            logger.info(f"📝 LLM Response Content: {content}")
            logger.info(f"📝 LLM Response Reasoning: {reasoning}")
            
            # Try to parse JSON from content first, then from reasoning
            response_text = content if content else reasoning
            
            # Parse JSON response
            try:
                if response_text:
                    # Try to extract JSON from the response
                    if response_text.startswith("{"):
                        parsed = json.loads(response_text)
                    else:
                        # Look for JSON within the text
                        import re
                        json_match = re.search(r'\{[^}]*"intent"[^}]*\}', response_text)
                        if json_match:
                            parsed = json.loads(json_match.group())
                        else:
                            raise json.JSONDecodeError("No JSON found", response_text, 0)
                    
                    logger.info(f"✅ JSON parsing successful: {parsed}")
                    return IntentResult(
                        intent=parsed["intent"],
                        reason=parsed["reason"]
                    )
                else:
                    raise json.JSONDecodeError("Empty response", "", 0)
                    
            except (json.JSONDecodeError, KeyError) as e:
                # Fallback to UNCLEAR if parsing fails
                logger.error(f"❌ JSON parsing failed: {e}")
                logger.error(f"   Raw response: {response_text}")
                return IntentResult(
                    intent=["UNCLEAR"],
                    reason=f"Failed to parse LLM response: {str(e)}"
                )
                
        except requests.exceptions.Timeout as e:
            # Handle timeout errors
            logger.error(f"❌ Request timeout: {e}")
            return IntentResult(
                intent=["UNCLEAR"],
                reason=f"Request timeout: {str(e)}"
            )
        except requests.exceptions.ConnectionError as e:
            # Handle connection errors
            logger.error(f"❌ Connection error: {e}")
            return IntentResult(
                intent=["UNCLEAR"],
                reason=f"Connection error: {str(e)}"
            )
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors
            logger.error(f"❌ HTTP error: {e}")
            error_text = ""
            try:
                error_text = e.response.text if hasattr(e.response, 'text') else str(e)
            except:
                error_text = str(e)
            return IntentResult(
                intent=["UNCLEAR"],
                reason=f"HTTP error {e.response.status_code}: {error_text}"
            )
        except Exception as e:
            # Catch any other exceptions
            logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
            return IntentResult(
                intent=["UNCLEAR"],
                reason=f"Unexpected error: {type(e).__name__}: {str(e)}"
            )
