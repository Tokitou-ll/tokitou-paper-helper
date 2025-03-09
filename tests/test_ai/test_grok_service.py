import asyncio
import os
from services import AIServiceFactory
from utils.config import ConfigManager

def test_basic_chat():
    """测试基本的聊天功能"""
    print("\n=== 测试基本聊天 ===")
    
    # 创建服务实例
    grok_service = AIServiceFactory.create("grok")
    
    # 准备测试消息
    messages = [
        {"role": "user", "content": "你好，请用一句话介绍一下你自己。"}
    ]
    
    # 执行聊天
    response = grok_service.chat_completion(messages)
    print("AI响应:", response["content"])
    print("模型:", response["model"])
    print("Token使用情况:", response["usage"])

def test_chat_with_params():
    """测试带参数的聊天功能"""
    print("\n=== 测试带参数的聊天 ===")
    
    grok_service = AIServiceFactory.create("grok")
    
    messages = [
        {"role": "user", "content": "给我讲个简短的笑话。"}
    ]
    
    # 使用自定义参数
    response = grok_service.chat_completion(
        messages,
        temperature=0.9,
        max_tokens=100
    )
    print("AI响应:", response["content"])

def test_stream_chat():
    """测试流式聊天功能"""
    print("\n=== 测试流式聊天 ===")
    
    grok_service = AIServiceFactory.create("grok")
    
    messages = [
        {"role": "user", "content": "请一个字一个字地介绍下自己。"}
    ]
    
    # 执行流式聊天
    for chunk in grok_service.chat_completion_stream(messages):
        print(chunk["content"], end="", flush=True)
    print()  # 换行

def main():
    """运行所有测试"""
    print("开始AI服务测试...")
    
    try:
        # 基础聊天测试
        test_basic_chat()
        
        # 带参数的聊天测试
        test_chat_with_params()
        
        # 流式聊天测试
        test_stream_chat()
        
        print("\n所有测试完成")
        
    except Exception as e:
        print(f"测试过程中出现错误: {str(e)}")

if __name__ == "__main__":
    main()
