#!/usr/bin/env python3
"""
小绿书封面图生成脚本
使用 GPT-Image-2 模型生成手绘信息图风格封面图

环境变量配置：
  export OPENAI_API_KEY="your-api-key"
  export OPENAI_API_BASE="https://api.openai.com/v1"  # 可选，默认使用 OpenAI

用法:
  python3 generate_cover.py "英文prompt描述" [输出路径] [尺寸]

示例:
  export OPENAI_API_KEY="sk-xxx"
  python3 generate_cover.py "A cute cat" "./output/cover.png"
"""

import os
import sys
import json
import urllib.request
import urllib.error
import ssl
import uuid

def get_env(key, default=None):
    """获取环境变量"""
    return os.environ.get(key, default)

def check_api_config():
    """检查 API 配置，如未配置则提示用户"""
    api_key = get_env("OPENAI_API_KEY")
    if not api_key:
        print("=" * 50, file=sys.stderr)
        print("❌ API Key 未配置！", file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        print("\n📌 首次使用请先配置环境变量：\n", file=sys.stderr)
        print("步骤1：获取 GPT-Image-2 的 API Key（自行解决）", file=sys.stderr)
        print("\n步骤2：在终端执行：", file=sys.stderr)
        print('  export OPENAI_API_KEY="你的API密钥"', file=sys.stderr)
        print("\n步骤3：重新运行此脚本", file=sys.stderr)
        print("\n💡 可选：设置自定义 API 端点", file=sys.stderr)
        print('  export OPENAI_API_BASE="https://your-custom-endpoint.com/v1"', file=sys.stderr)
        print("=" * 50, file=sys.stderr)
        return False
    return True

def generate_image(prompt, output_path=None, size="1024x1366"):
    """调用 GPT-Image-2 API 生成图片"""
    api_key = get_env("OPENAI_API_KEY")
    api_base = get_env("OPENAI_API_BASE", "https://api.openai.com/v1")
    url = f"{api_base.rstrip('/')}/images/generations"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "n": 1,
        "size": size
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, timeout=350, context=ctx) as response:
            result = json.loads(response.read().decode("utf-8"))

        if result.get("data"):
            image_url = result["data"][0]["url"]

            # 下载图片
            ctx2 = ssl.create_default_context()
            img_req = urllib.request.Request(image_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(img_req, timeout=30, context=ctx2) as img_response:
                image_data = img_response.read()

            # 确保输出目录存在
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                output_path = f"cover_{uuid.uuid4().hex[:8]}.png"

            with open(output_path, "wb") as f:
                f.write(image_data)

            print(f"✅ 图片已保存: {output_path}")
            print(f"📎 图片URL: {image_url}")
            return output_path
        else:
            print(f"❌ API 返回异常 - {result}", file=sys.stderr)
            return None

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8") if e.fp else str(e)
        print(f"❌ HTTP 错误 {e.code}: {error_body}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ 生成失败: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 generate_cover.py \"英文prompt\" [输出路径] [尺寸]")
        print("示例: python3 generate_cover.py \"A cute cat\" \"./output/cover.png\"")
        sys.exit(1)

    # 首次运行检查 API 配置
    if not check_api_config():
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    size = sys.argv[3] if len(sys.argv) > 3 else "1024x1366"

    result = generate_image(prompt, output_path, size)
    if result:
        print(result)  # 输出文件路径供脚本调用方捕获
    else:
        sys.exit(1)
