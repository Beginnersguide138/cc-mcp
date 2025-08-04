"""
Keyword Extraction Engine for CC-MCP Server
TF-IDFベースのキーワード抽出システム
"""
import re
import math
from typing import List, Dict, Set
from collections import Counter, defaultdict
import logging

logger = logging.getLogger(__name__)

class KeywordExtractionEngine:
    """
    キーワード抽出エンジン
    TF-IDF (Term Frequency-Inverse Document Frequency) を使用して
    対話の重要なターンから象徴的なキーワードを統計的に抽出する
    """
    
    def __init__(self):
        # 全対話セッションのメッセージコーパス（IDF計算用）
        self._document_corpus: List[str] = []
        # 単語の文書頻度カウント
        self._document_frequency: Dict[str, int] = defaultdict(int)
        # 総文書数
        self._total_documents = 0
        
        # 日本語のストップワード（一般的で意味の薄い単語）
        self._stop_words: Set[str] = {
            'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 
            'も', 'する', 'から', 'な', 'こと', 'として', 'い', 'や', 'れる', 'など', 'なっ', 'ない', 
            'この', 'ため', 'その', 'あっ', 'よう', 'また', 'もの', 'という', 'あり', 'まで', 'られ',
            'なる', 'へ', 'か', 'だ', 'これ', 'によって', 'により', 'おり', 'より', 'による', 'ず',
            'なり', 'られる', 'において', 'ば', 'なかっ', 'なく', 'しかし', 'について', 'せ', 'だっ',
            'その他', 'ここ', 'そこ', 'それ', 'どこ', 'いつ', 'なぜ', 'どう', 'どの', 'どんな',
            'です', 'ます', 'である', 'でした', 'だった', 'ください', 'ちょっと', 'ちゃん',
            'さん', 'くん', 'ちゃん', 'みたい', 'みたいな', 'っぽい', '感じ', 'ような',
            'と思い', 'と思う', 'と思います', 'けど', 'でも', 'しかし', 'ただし'
        }
        
        # 英語のストップワード
        self._stop_words.update({
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be', 'been', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
            'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
        })
        
        logger.info("KeywordExtractionEngine initialized")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        テキストをトークン（単語）に分割する
        
        Args:
            text: 入力テキスト
            
        Returns:
            List[str]: トークン化された単語のリスト
        """
        # 文字の正規化と小文字化
        text = text.lower().strip()
        
        # 日本語と英語の単語を抽出（記号、数字、空白は除く）
        # ひらがな、カタカナ、漢字、英字を含む1文字以上の文字列を抽出
        tokens = re.findall(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fafa-zA-Z]+', text)
        
        # ストップワードを除去し、長さが2文字以上の単語のみを残す
        filtered_tokens = [
            token for token in tokens 
            if len(token) >= 2 and token not in self._stop_words
        ]
        
        return filtered_tokens
    
    def _calculate_tf(self, tokens: List[str]) -> Dict[str, float]:
        """
        Term Frequency (単語頻度) を計算する
        
        Args:
            tokens: トークン化された単語のリスト
            
        Returns:
            Dict[str, float]: 各単語のTF値
        """
        token_counts = Counter(tokens)
        total_tokens = len(tokens)
        
        if total_tokens == 0:
            return {}
        
        # TF = (単語の出現回数) / (総単語数)
        tf_scores = {
            token: count / total_tokens 
            for token, count in token_counts.items()
        }
        
        return tf_scores
    
    def _calculate_idf(self, token: str) -> float:
        """
        Inverse Document Frequency (逆文書頻度) を計算する
        
        Args:
            token: 単語
            
        Returns:
            float: IDF値
        """
        if self._total_documents == 0:
            return 0.0
        
        # 文書頻度（その単語を含む文書数）
        doc_freq = self._document_frequency.get(token, 0)
        
        if doc_freq == 0:
            return 0.0
        
        # IDF = log(総文書数 / その単語を含む文書数)
        idf_score = math.log(self._total_documents / doc_freq)
        
        return idf_score
    
    def _update_corpus(self, text: str) -> None:
        """
        コーパスを更新して文書頻度を再計算する
        
        Args:
            text: 新しいドキュメント
        """
        self._document_corpus.append(text)
        self._total_documents += 1
        
        # この文書に含まれるユニークな単語の文書頻度を更新
        tokens = self._tokenize(text)
        unique_tokens = set(tokens)
        
        for token in unique_tokens:
            self._document_frequency[token] += 1
    
    def extract_keywords(self, text: str, top_k: int = 5) -> List[Dict[str, float]]:
        """
        テキストからキーワードを抽出する
        
        Args:
            text: 分析対象のテキスト
            top_k: 抽出する上位キーワード数
            
        Returns:
            List[Dict[str, float]]: キーワードとスコアのリスト
            [{"keyword": "単語", "score": 0.123}, ...]
        """
        if not text.strip():
            return []
        
        # コーパスに追加
        self._update_corpus(text)
        
        # トークン化
        tokens = self._tokenize(text)
        
        if not tokens:
            return []
        
        # TF計算
        tf_scores = self._calculate_tf(tokens)
        
        # TF-IDF計算
        tfidf_scores = {}
        for token, tf_score in tf_scores.items():
            idf_score = self._calculate_idf(token)
            tfidf_scores[token] = tf_score * idf_score
        
        # スコア順にソートしてトップK個を取得
        sorted_keywords = sorted(
            tfidf_scores.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:top_k]
        
        # 結果をフォーマット
        result = [
            {"keyword": keyword, "score": score}
            for keyword, score in sorted_keywords
            if score > 0  # スコアが0より大きいもののみ
        ]
        
        logger.info(f"Extracted {len(result)} keywords from text: {text[:50]}...")
        
        return result
    
    def get_corpus_stats(self) -> Dict[str, int]:
        """
        コーパスの統計情報を取得する
        
        Returns:
            Dict[str, int]: 統計情報
        """
        return {
            "total_documents": self._total_documents,
            "unique_terms": len(self._document_frequency),
            "avg_document_length": (
                sum(len(self._tokenize(doc)) for doc in self._document_corpus) / max(self._total_documents, 1)
            )
        }
    
    def reset_corpus(self) -> None:
        """
        コーパスをリセットする（テスト用）
        """
        self._document_corpus.clear()
        self._document_frequency.clear()
        self._total_documents = 0
        logger.info("Corpus reset")
