import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging
from database import add_assessment, get_assessment_by_input

logger = logging.getLogger(__name__)

class ComplianceAuditor:
    def __init__(self):
        logger.info("Initializing ComplianceAuditor")
        self.model_name = "bert-base-chinese"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.max_length = 512
        self.issue_categories = {
            0: "财务合规",
            1: "运营风险",
            2: "信息安全",
            3: "人力资源合规",
            4: "环境与安全",
            5: "公司治理",
            6: "反洗钱合规",
            7: "数据隐私",
            8: "供应链管理",
            9: "产品质量与安全"
        }
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, num_labels=len(self.issue_categories))
        self.regulations = {
            "财务合规": {
                "《企业会计准则》": ["第1号-存货", "第6号-无形资产", "第22号-金融工具确认和计量"],
                "《中华人民共和国公司法》": ["第166条", "第167条", "第168条"],
                "《企业内部控制基本规范》": ["第三章 内部控制要素"]
            },
            "运营风险": {
                "《中华人民共和国安全生产法》": ["第二十一条", "第二十二条", "第二十三条"],
                "《企业内部控制应用指引第9号——业务外包》": ["全文"]
            },
            "信息安全": {
                "《中华人民共和国网络安全法》": ["第二十一条", "第二十二条", "第二十三条"],
                "《信息安全技术 网络安全等级保护基本要求》": ["全文"]
            },
            "人力资源合规": {
                "《中华人民共和国劳动法》": ["第三章", "第四章", "第五章"],
                "《中华人民共和国劳动合同法》": ["第二章", "第三章"]
            },
            "环境与安全": {
                "《中华人民共和国环境保护法》": ["第二章", "第三章"],
                "《中华人民共和国安全生产法》": ["第二章", "第三章"]
            },
            "公司治理": {
                "《中华人民共和国公司法》": ["第四章", "第六章"],
                "《上市公司治理准则》": ["全文"]
            },
            "反洗钱合规": {
                "《中华人民共和国反洗钱法》": ["第二章", "第三章"],
                "《金融机构反洗钱规定》": ["全文"]
            },
            "数据隐私": {
                "《中华人民共和国个人信息保护法》": ["第二章", "第三章"],
                "《数据安全法》": ["第二章", "第三章"]
            },
            "供应链管理": {
                "《中华人民共和国招标投标法》": ["第三章", "第四章"],
                "《供应链安全管理指南》": ["全文"]
            },
            "产品质量与安全": {
                "《中华人民共和国产品质量法》": ["第二章", "第三章"],
                "《中华人民共和国食品安全法》": ["第四章", "第五章"]
            }
        }
        logger.info("ComplianceAuditor initialized successfully")

    def preprocess_text(self, text):
        chinese_chars = ''.join([char for char in text if '\u4e00' <= char <= '\u9fff'])
        return chinese_chars[:self.max_length]

    def analyze(self, text):
        try:
            logger.info(f"Analyzing text of length: {len(text)}")
            preprocessed_text = self.preprocess_text(text)
            logger.info(f"Preprocessed text length: {len(preprocessed_text)}")
            
            # Check if the assessment exists in the database
            cached_result = get_assessment_by_input(preprocessed_text)
            if cached_result:
                logger.info("Result found in database")
                return cached_result

            inputs = self.tokenizer(preprocessed_text, return_tensors="pt", padding=True, truncation=True, max_length=self.max_length)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
            
            top_3_indices = torch.topk(outputs.logits, k=3, dim=1).indices[0].tolist()
            issues = [self.issue_categories[idx] for idx in top_3_indices]
            
            detailed_result = self.generate_detailed_result(issues)
            
            # Store the new assessment in the database
            add_assessment(preprocessed_text, detailed_result["identified_issues"], detailed_result["relevant_regulations"])

            logger.info(f"Analysis result: {detailed_result}")
            return detailed_result
        except RuntimeError as e:
            logger.error(f"Runtime error during model inference: {str(e)}", exc_info=True)
            return {"error": "分析过程中出现错误，请稍后重试或尝试较短的文本"}
        except Exception as e:
            logger.error(f"Error during compliance analysis: {str(e)}", exc_info=True)
            raise

    def generate_detailed_result(self, issues):
        detailed_result = {
            "identified_issues": [],
            "relevant_regulations": [],
            "explanations": [],
            "recommendations": []
        }

        for issue in issues:
            detailed_result["identified_issues"].append(issue)
            regulations = self.regulations.get(issue, {})
            for regulation, clauses in regulations.items():
                detailed_result["relevant_regulations"].append(f"{regulation}: {', '.join(clauses)}")
            
            explanation = self.generate_explanation(issue)
            detailed_result["explanations"].append(explanation)
            
            recommendation = self.generate_audit_recommendation(issue)
            detailed_result["recommendations"].append(recommendation)

        return detailed_result

    def generate_explanation(self, issue):
        explanations = {
            "财务合规": "财务合规涉及确保公司的财务报告和会计实践符合相关法律法规和会计准则。",
            "运营风险": "运营风险包括可能影响公司日常运营的各种内部和外部因素。",
            "信息安全": "信息安全关注保护公司的数据和IT系统免受未经授权的访问、使用、披露、中断、修改或破坏。",
            "人力资源合规": "人力资源合规涉及遵守劳动法律法规，确保公平的雇佣实践和员工权益保护。",
            "环境与安全": "环境与安全合规涉及遵守环境保护法规和确保工作场所安全。",
            "公司治理": "公司治理涉及公司的领导、控制和指导机制，确保公司运作透明、负责任。",
            "反洗钱合规": "反洗钱合规涉及实施措施以防止、检测和报告洗钱活动。",
            "数据隐私": "数据隐私合规涉及保护个人信息和确保数据处理符合隐私法规。",
            "供应链管理": "供应链管理合规涉及确保供应商和采购过程符合法律和道德标准。",
            "产品质量与安全": "产品质量与安全合规涉及确保产品符合质量标准和安全规定。"
        }
        return explanations.get(issue, "需要进一步调查以确定具体的合规问题。")

    def generate_audit_recommendation(self, issue):
        recommendations = {
            "财务合规": "建议进行定期的内部财务审计，确保遵守最新的会计准则和财务报告要求。",
            "运营风险": "建议实施全面的风险管理系统，定期评估和更新运营风险缓解策略。",
            "信息安全": "建议实施强有力的信息安全政策，进行定期的安全审计和员工培训。",
            "人力资源合规": "建议定期审查人力资源政策，确保符合最新的劳动法规，并提供员工合规培训。",
            "环境与安全": "建议制定全面的环境和安全管理计划，定期进行合规检查和员工安全培训。",
            "公司治理": "建议定期审查公司治理结构，确保董事会的独立性和有效性，完善信息披露机制。",
            "反洗钱合规": "建议加强客户尽职调查程序，实施交易监控系统，并定期更新反洗钱政策。",
            "数据隐私": "建议实施数据保护影响评估，加强数据处理的透明度，并确保获得适当的数据处理同意。",
            "供应链管理": "建议实施供应商行为准则，进行定期的供应商审核，并建立透明的采购流程。",
            "产品质量与安全": "建议加强质量控制流程，实施产品追溯系统，并定期进行产品安全测试。"
        }
        return recommendations.get(issue, "建议进行深入的合规评估，以制定针对性的改进措施。")
