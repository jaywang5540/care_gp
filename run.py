#!/usr/bin/env python3
"""
Medicare GP Assistant 启动脚本
"""

import uvicorn
import os
import argparse
import sys

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Medicare GP Assistant 启动脚本")
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="服务器端口 (默认: 8000)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        default=True,
        help="启用热重载 (默认: True)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1,
        help="工作进程数 (默认: 1)"
    )
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 打印启动信息
    print("\n" + "=" * 60)
    print("🏥 Medicare GP Assistant")
    print("AI辅助Medicare Benefits Schedule账单系统")
    print("=" * 60)
    print(f"📍 服务地址: http://{args.host}:{args.port}")
    print(f"📖 API文档: http://{args.host}:{args.port}/docs")
    print(f"🎨 测试界面: http://{args.host}:{args.port}/")
    print(f"🔄 热重载: {'开启' if args.reload else '关闭'}")
    print("=" * 60)
    print("按 Ctrl+C 停止服务器\n")
    
    try:
        # 启动服务器
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=1 if args.reload else args.workers,  # 热重载模式下只能使用1个worker
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n\n服务器已停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()