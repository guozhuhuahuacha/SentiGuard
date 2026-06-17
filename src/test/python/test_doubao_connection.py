#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试豆包 API 连接
"""
import os
import sys
import json
from dotenv import load_dotenv

# 把项目根目录加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# 加载环境变量
load_dotenv()


def test_basic_connection():
    """测试基本的 API 连接"""
    print("=" * 60)
    print("豆包 API 连接测试")
    print("=" * 60)

    # 1. 检查 API Key 和 Base URL
    print("\n[1] 检查配置...")
    api_key = os.getenv("DOUBAO_API_KEY") or os.getenv("ARK_API_KEY")
    base_url = os.getenv("DOUBAO_BASE_URL") or os.getenv("ARK_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"

    if not api_key:
        print("  ❌ API Key 未设置")
        return False

    print(f"  ✅ API Key: 已设置 (长度: {len(api_key)})")
    print(f"  ✅ Base URL: {base_url}")

    # 2. 测试网络连接
    print("\n[2] 测试网络连接...")
    try:
        import httpx
        from urllib.parse import urlparse

        # 测试基本连接
        parsed = urlparse(base_url)
        host = parsed.netloc
        print(f"  连接到: {host}")

        # 简单的 ping 测试（使用 httpx）
        timeout = httpx.Timeout(30.0, connect=10.0)
        client = httpx.Client(timeout=timeout, verify=False)

        # 尝试访问基础 URL
        try:
            response = client.get(base_url, timeout=10)
            print(f"  ✅ HTTP 连接成功: {response.status_code}")
        except Exception as e:
            print(f"  ⚠️  基础 URL 访问失败: {e}")
            print(f"  这是正常的，因为 API 需要认证")

        client.close()

    except Exception as e:
        print(f"  ❌ 网络连接测试失败: {e}")
        import traceback
        traceback.print_exc()

    # 3. 测试 OpenAI SDK 连接
    print("\n[3] 测试 OpenAI SDK 连接...")
    try:
        from openai import OpenAI

        client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=30.0,
        )

        # 尝试列出模型（很多 API 不支持这个，但可以测试连接）
        print("  尝试调用 API (简单测试)...")
        try:
            # 使用一个简单的 chat completion 测试
            response = client.chat.completions.create(
                model="doubao-seed-2-0-mini-260428",
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=5,
                temperature=0,
            )
            print(f"  ✅ API 调用成功!")
            print(f"  回复: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"  ⚠️  API 调用失败: {e}")
            print(f"\n可能的原因:")
            print(f"  1. API Key 无效")
            print(f"  2. 模型名称不正确")
            print(f"  3. 网络/防火墙问题")
            print(f"  4. SSL 证书问题")
            return False

    except Exception as e:
        print(f"  ❌ OpenAI SDK 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_doubao_client():
    """测试 DoubaoLLM 客户端"""
    print("\n" + "=" * 60)
    print("测试 DoubaoLLM 客户端")
    print("=" * 60)

    try:
        from src.main.python.llms.doubao_client import DoubaoLLM

        print("\n[1] 初始化 DoubaoLLM...")
        llm = DoubaoLLM(model_name="doubao-seed-2-0-mini-260428")
        print("  ✅ 初始化成功")

        print("\n[2] 测试简单对话...")
        response = llm.chat("你好，请回复'测试成功'")
        print(f"  ✅ 对话成功: {response}")

        return True

    except Exception as e:
        print(f"  ❌ DoubaoLLM 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def try_with_different_ssl_options():
    """尝试不同的 SSL 配置"""
    print("\n" + "=" * 60)
    print("尝试不同的 SSL 配置选项")
    print("=" * 60)

    api_key = os.getenv("DOUBAO_API_KEY") or os.getenv("ARK_API_KEY")
    base_url = os.getenv("DOUBAO_BASE_URL") or os.getenv("ARK_BASE_URL") or "https://ark.cn-beijing.volces.com/api/v3"

    if not api_key:
        print("  ❌ API Key 未设置")
        return

    try:
        from openai import OpenAI
        import httpx

        # 测试 1: 关闭 SSL 验证
        print("\n[选项 1] 关闭 SSL 验证...")
        try:
            # 创建自定义 httpx 客户端，禁用 SSL 验证
            custom_client = httpx.Client(verify=False, timeout=30.0)
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                http_client=custom_client,
            )
            response = client.chat.completions.create(
                model="doubao-seed-2-0-mini-260428",
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=5,
                temperature=0,
            )
            print(f"  ✅ 成功 (禁用 SSL 验证)!")
            print(f"  回复: {response.choices[0].message.content}")
            custom_client.close()
            return True
        except Exception as e:
            print(f"  ❌ 失败: {e}")

        # 测试 2: 使用更长的超时时间
        print("\n[选项 2] 使用更长的超时时间...")
        try:
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=60.0,
            )
            response = client.chat.completions.create(
                model="doubao-seed-2-0-mini-260428",
                messages=[{"role": "user", "content": "你好"}],
                max_tokens=5,
                temperature=0,
            )
            print(f"  ✅ 成功 (60秒超时)!")
            print(f"  回复: {response.choices[0].message.content}")
            return True
        except Exception as e:
            print(f"  ❌ 失败: {e}")

        return False

    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("豆包 API 诊断工具")
    print("=" * 60)

    # 测试 1: 基本连接
    basic_ok = test_basic_connection()

    # 测试 2: DoubaoLLM
    if basic_ok:
        client_ok = test_doubao_client()
    else:
        print("\n跳过 DoubaoLLM 测试，因为基本连接失败")
        client_ok = False

    # 测试 3: 其他 SSL 选项
    if not basic_ok or not client_ok:
        try:
            try_with_different_ssl_options()
        except Exception as e:
            print(f"\n⚠️  替代配置测试也失败: {e}")

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)
    print("\n提示: 如果遇到 SSL 错误，可以尝试:")
    print("  1. 检查网络连接")
    print("  2. 检查代理设置")
    print("  3. 检查防火墙")
    print("  4. 使用环境变量设置代理:")
    print("     export HTTP_PROXY=http://...")
    print("     export HTTPS_PROXY=http://...")
