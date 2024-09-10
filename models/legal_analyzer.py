import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from collections import OrderedDict
import logging

logger = logging.getLogger(__name__)

class LegalAnalyzer:
    def __init__(self):
        logger.info("Initializing LegalAnalyzer")
        self.model_name = "bert-base-chinese"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.max_length = 500
        self.cache = OrderedDict()
        self.cache_size = 100
        self.issue_categories = {
            0: "合同纠纷",
            1: "知识产权侵权",
            2: "消费者权益",
            3: "劳动争议",
            4: "侵权责任",
        }
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=len(self.issue_categories))
        self.laws = {
            "合同纠纷": ["《中华人民共和国合同法》", "《中华人民共和国民法典》"],
            "知识产权侵权": ["《中华人民共和国著作权法》", "《中华人民共和国专利法》"],
            "消费者权益": ["《中华人民共和国消费者权益保护法》"],
            "劳动争议": ["《中华人民共和国劳动法》", "《中华人民共和国劳动合同法》"],
            "侵权责任": ["《中华人民共和国侵权责任法》", "《中华人民共和国民法典》"],
        }
        logger.info("LegalAnalyzer initialized successfully")

    def preprocess_text(self, text):
        # Remove non-Chinese characters and limit length
        chinese_chars = ''.join([char for char in text if '\u4e00' <= char <= '\u9fff'])
        return chinese_chars[:self.max_length]

    def analyze(self, text):
        try:
            logger.info(f"Analyzing text of length: {len(text)}")
            preprocessed_text = self.preprocess_text(text)
            logger.info(f"Preprocessed text length: {len(preprocessed_text)}")
            
            # Check cache
            if preprocessed_text in self.cache:
                logger.info("Result found in cache")
                return self.cache[preprocessed_text]

            inputs = self.tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            predicted_category = torch.argmax(outputs.logits, dim=1).item()
            issue = self.issue_categories[predicted_category]
            relevant_laws = self.laws[issue]

            result = {
                "legal_issues": [issue],
                "relevant_laws": relevant_laws
            }

            # Update cache
            self.cache[preprocessed_text] = result
            if len(self.cache) > self.cache_size:
                self.cache.popitem(last=False)

            logger.info(f"Analysis result: {result}")
            return result
        except RuntimeError as e:
            logger.error(f"Runtime error during model inference: {str(e)}", exc_info=True)
            return {"error": "分析过程中出现错误，请稍后重试或尝试较短的文本"}
        except Exception as e:
            logger.error(f"Error during legal analysis: {str(e)}", exc_info=True)
            raise
