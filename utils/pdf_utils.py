import os
import fitz  # PyMuPDF
from typing import Dict, Any, Optional
import re

class PDFProcessor:
    """PDF文件处理器"""
    
    def __init__(self):
        self.temp_dir = os.path.join("output", "analysis", "text")
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def extract_text(self, pdf_path: str) -> Dict[str, str]:
        """
        从PDF文件中提取文本内容
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            包含不同部分文本的字典
        """
        try:
            doc = fitz.open(pdf_path)
            
            # 提取文本内容
            full_text = ""
            for page in doc:
                full_text += page.get_text()
            
            # 解析不同部分
            sections = self._parse_sections(full_text)
            
            # 保存提取的文本
            text_path = os.path.join(self.temp_dir, "extracted_text.txt")
            with open(text_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            return sections
            
        except Exception as e:
            raise Exception(f"PDF文本提取失败: {str(e)}")
    
    def extract_metadata(self, pdf_path: str) -> Dict[str, Any]:
        """
        提取PDF文件的元数据
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            元数据字典
        """
        try:
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            
            # 提取标题和作者
            title = self._extract_title(doc)
            authors = self._extract_authors(doc)
            
            return {
                "title": title,
                "authors": authors,
                "metadata": metadata
            }
            
        except Exception as e:
            raise Exception(f"PDF元数据提取失败: {str(e)}")
    
    def _parse_sections(self, text: str) -> Dict[str, str]:
        """
        解析文本中的不同部分
        
        Args:
            text: 完整文本
            
        Returns:
            不同部分的文本字典
        """
        sections = {
            "abstract": "",
            "introduction": "",
            "implementation": "",
            "experiments": "",
            "code_samples": "",
            "key_sections": ""
        }
        
        # 提取摘要
        abstract_match = re.search(r"Abstract\s*(.*?)(?=\n\s*1[\s.]|Introduction)", 
                                 text, re.DOTALL | re.IGNORECASE)
        if abstract_match:
            sections["abstract"] = abstract_match.group(1).strip()
        
        # 提取实现部分
        impl_match = re.search(r"Implementation\s*(.*?)(?=\n\s*[0-9]+[\s.]|Experiments?|Results?|Conclusion)", 
                             text, re.DOTALL | re.IGNORECASE)
        if impl_match:
            sections["implementation"] = impl_match.group(1).strip()
        
        # 提取实验部分
        exp_match = re.search(r"Experiments?\s*(.*?)(?=\n\s*[0-9]+[\s.]|Conclusion|References?)", 
                            text, re.DOTALL | re.IGNORECASE)
        if exp_match:
            sections["experiments"] = exp_match.group(1).strip()
        
        # 提取代码示例
        code_blocks = re.findall(r"```.*?```|(?:Algorithm|Listing)\s+\d+[:\s].*?(?=\n\n)", 
                               text, re.DOTALL)
        sections["code_samples"] = "\n\n".join(code_blocks)
        
        # 提取关键章节（包括方法论、算法描述等）
        key_sections_text = []
        if sections["implementation"]:
            key_sections_text.append("Implementation:\n" + sections["implementation"])
        if sections["experiments"]:
            key_sections_text.append("Experiments:\n" + sections["experiments"])
        sections["key_sections"] = "\n\n".join(key_sections_text)
        
        return sections
    
    def _extract_title(self, doc) -> Optional[str]:
        """提取论文标题"""
        try:
            # 尝试从元数据中获取
            if doc.metadata.get("title"):
                return doc.metadata["title"]
            
            # 从第一页文本中提取
            first_page = doc[0].get_text()
            # 通常标题是第一页的第一行或前几行
            lines = [line.strip() for line in first_page.split("\n") if line.strip()]
            if lines:
                # 返回第一个看起来像标题的行
                for line in lines[:3]:
                    if len(line) > 10 and not line.startswith(("Abstract", "Introduction")):
                        return line
            
            return None
            
        except Exception:
            return None
    
    def _extract_authors(self, doc) -> Optional[str]:
        """提取作者信息"""
        try:
            # 尝试从元数据中获取
            if doc.metadata.get("author"):
                return doc.metadata["author"]
            
            # 从第一页文本中提取
            first_page = doc[0].get_text()
            text_before_abstract = first_page.split("Abstract")[0]
            
            # 查找看起来像作者列表的行
            lines = text_before_abstract.split("\n")
            for line in lines[1:]:  # 跳过第一行（标题）
                # 作者行通常包含多个名字，用逗号或and分隔
                if "," in line or " and " in line.lower():
                    return line.strip()
            
            return None
            
        except Exception:
            return None 