#!/usr/bin/env python3
"""
NextGen25 提案PDF导出工具
提供多种页面格式选项，确保内容完整显示
"""

import asyncio
from pathlib import Path
from datetime import datetime
import sys

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("📦 需要安装 Playwright")
    print("请运行以下命令:")
    print("  pip install playwright")
    print("  playwright install chromium")
    exit(1)


async def export_proposal(format_choice="wide"):
    """
    导出提案为PDF
    
    Args:
        format_choice: 页面格式选择
            - "a4": 标准A4纵向
            - "a4-landscape": A4横向
            - "wide": 宽页面（11x14英寸）- 推荐
            - "extra-wide": 超宽页面（适合屏幕阅读）
    """
    
    # 文件路径
    html_file = Path("initial-proposal.html")
    if not html_file.exists():
        print(f"❌ 找不到文件: {html_file}")
        return
    
    # 格式配置
    formats = {
        "a4": {
            "name": "A4纵向",
            "format": "A4",
            "scale": 0.7,
            "viewport": {"width": 1200, "height": 1600}
        },
        "a4-landscape": {
            "name": "A4横向",
            "format": "A4",
            "landscape": True,
            "scale": 0.8,
            "viewport": {"width": 1600, "height": 1200}
        },
        "wide": {
            "name": "宽页面(推荐)",
            "width": "11in",
            "height": "14in",
            "scale": 0.75,
            "viewport": {"width": 1440, "height": 900}
        },
        "extra-wide": {
            "name": "超宽页面",
            "width": "13in",
            "height": "16in",
            "scale": 0.65,
            "viewport": {"width": 1600, "height": 1200}
        }
    }
    
    if format_choice not in formats:
        format_choice = "wide"  # 默认使用推荐格式
    
    config = formats[format_choice]
    
    # 输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    output_file = Path(f"NextGen25_Proposal_{timestamp}.pdf")
    
    print("="*60)
    print("🚀 开始导出PDF...")
    print(f"📄 源文件: {html_file}")
    print(f"📐 页面格式: {config['name']}")
    print(f"📑 输出到: {output_file}")
    print("="*60)
    
    async with async_playwright() as p:
        # 启动浏览器
        print("🌐 启动浏览器...")
        browser = await p.chromium.launch(headless=True)
        
        # 创建页面
        page = await browser.new_page()
        
        # 设置视口
        await page.set_viewport_size(config["viewport"])
        
        # 强制使用屏幕媒体样式
        await page.emulate_media(media="screen")
        
        # 加载HTML
        print("📖 加载HTML页面...")
        file_url = f"file://{html_file.absolute()}"
        await page.goto(file_url, wait_until="networkidle")
        
        # 等待加载
        await page.wait_for_timeout(3000)
        
        # 构建PDF选项
        pdf_options = {
            "path": str(output_file),
            "print_background": True,
            "margin": {
                "top": "10mm",
                "right": "10mm",
                "bottom": "10mm",
                "left": "10mm"
            },
            "display_header_footer": False,
            "scale": config.get("scale", 1.0),
            "prefer_css_page_size": False
        }
        
        # 添加格式特定选项
        if "format" in config:
            pdf_options["format"] = config["format"]
        if "width" in config:
            pdf_options["width"] = config["width"]
        if "height" in config:
            pdf_options["height"] = config["height"]
        if "landscape" in config:
            pdf_options["landscape"] = config["landscape"]
        
        # 生成PDF
        print(f"🎨 生成PDF（缩放: {config.get('scale', 1.0)*100:.0f}%）...")
        await page.pdf(**pdf_options)
        
        await browser.close()
    
    # 检查文件大小
    file_size = output_file.stat().st_size / (1024 * 1024)  # MB
    
    print("="*60)
    print("✅ PDF导出成功!")
    print(f"📊 文件大小: {file_size:.2f} MB")
    print(f"📍 文件位置: {output_file.absolute()}")
    
    if file_size > 10:
        print("⚠️  文件较大，可能因为包含了渐变背景")
        print("💡 提示：可以使用在线PDF压缩工具")
    
    return output_file


def main():
    print("="*60)
    print("🏥 Medicare GP Assistant - PDF导出工具")
    print("="*60)
    print("\n请选择页面格式:")
    print("1. A4纵向 (标准打印)")
    print("2. A4横向 (更宽的布局)")
    print("3. 宽页面 (推荐 - 11x14英寸)")
    print("4. 超宽页面 (最佳屏幕阅读)")
    print()
    
    # 获取用户选择
    choice_map = {
        "1": "a4",
        "2": "a4-landscape", 
        "3": "wide",
        "4": "extra-wide"
    }
    
    # 如果有命令行参数，直接使用
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in choice_map:
            format_choice = choice_map[arg]
        elif arg in formats:
            format_choice = arg
        else:
            print(f"使用默认格式: 宽页面")
            format_choice = "wide"
    else:
        # 交互式选择
        choice = input("请输入选项 (1-4) [默认: 3]: ").strip() or "3"
        format_choice = choice_map.get(choice, "wide")
    
    # 运行导出
    asyncio.run(export_proposal(format_choice))
    
    print("\n💡 提示：")
    print("- 如果内容被截断，尝试使用'超宽页面'选项")
    print("- 横向布局适合投影展示")
    print("- 纵向布局适合打印")
    print("- 可以通过命令行参数快速选择: python export_proposal.py 3")


if __name__ == "__main__":
    main()