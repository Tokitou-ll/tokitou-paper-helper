import os
import json
from pathlib import Path

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

def prepare_analysis_rules(output_dir):
    """准备论文分析规则"""
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 定义分析规则
        rules = {
            "code_implementation": {
                # 官方实现的模式
                "official_patterns": [
                    r"official.*?implementation",
                    r"official.*?code",
                    r"source.*?code.*?available",
                    r"code.*?available.*?at",
                    r"implementation.*?available",
                    r"github.*?repository",
                    r"open.*?source",
                    r"code.*?released",
                    r"code.*?published",
                    r"code.*?provided",
                    r"implementation.*?released",
                    r"implementation.*?published",
                    r"implementation.*?provided"
                ],
                
                # 非官方实现的模式
                "unofficial_patterns": [
                    r"based.*?on.*?implementation",
                    r"adapted.*?from",
                    r"modified.*?version",
                    r"inspired.*?by",
                    r"unofficial.*?implementation",
                    r"reimplementation",
                    r"our.*?implementation",
                    r"implementation.*?based.*?on",
                    r"code.*?based.*?on",
                    r"following.*?implementation"
                ],
                
                # 代码相关的指标
                "code_indicators": [
                    r"github\.com",
                    r"gitlab\.com",
                    r"bitbucket\.org",
                    r"code.*?available",
                    r"implementation.*?available",
                    r"source.*?code",
                    r"python",
                    r"pytorch",
                    r"tensorflow",
                    r"keras",
                    r"implementation.*?details",
                    r"code.*?repository",
                    r"software.*?package",
                    r"library",
                    r"framework"
                ]
            },
            
            "method_innovation": {
                # 创新方法的模式
                "novel_patterns": [
                    r"novel",
                    r"new",
                    r"propose",
                    r"proposed",
                    r"innovative",
                    r"first",
                    r"contribution",
                    r"introduce",
                    r"introduced",
                    r"original"
                ],
                
                # 改进的模式
                "improvement_patterns": [
                    r"improve",
                    r"improved",
                    r"enhancement",
                    r"enhanced",
                    r"better",
                    r"superior",
                    r"outperform",
                    r"outperforms",
                    r"advance",
                    r"advancement",
                    r"boost",
                    r"boosted",
                    r"increase",
                    r"increased"
                ]
            }
        }
        
        # 保存规则到JSON文件
        rules_file = os.path.join(output_dir, "analysis_rules.json")
        with open(rules_file, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
            
        print("\n分析规则准备完成！")
        print(f"规则文件：{rules_file}")
        
        return True, rules_file
        
    except Exception as e:
        print(f"准备分析规则时出错: {str(e)}")
        return False, None

if __name__ == "__main__":
    prepare_analysis_rules() 