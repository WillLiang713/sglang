#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从魔塔社区(ModelScope)下载模型的脚本,支持断点续传和完整性校验"""

import argparse
import os
import sys
from modelscope import snapshot_download
from modelscope.hub.api import HubApi

DEFAULT_MODEL = "qwen/Qwen3-0.6B"
DEFAULT_DIR = "./models"


def resolve_model_dir(model_id, local_dir):
    """模型实际落盘目录(直接使用原始 model_id,不做字符转义)"""
    return os.path.join(local_dir, model_id)


def verify_model(model_id, local_dir):
    """校验模型文件完整性"""
    try:
        model_files = HubApi().get_model_files(model_id)
        model_dir = resolve_model_dir(model_id, local_dir)

        if not os.path.exists(model_dir):
            print(f"  ❌ 未找到模型目录: {model_dir}")
            return False

        print(f"  🔍 正在校验 {len(model_files)} 个文件...")

        for i, file_info in enumerate(model_files, 1):
            file_path = os.path.join(model_dir, file_info["Path"])
            if not os.path.exists(file_path) or (
                file_info.get("Size", 0) > 0
                and os.path.getsize(file_path) != file_info["Size"]
            ):
                print(f"  ❌ [{i}/{len(model_files)}] 文件问题: {file_info['Path']}")
                return False

        print("  ✅ 所有文件校验通过")
        return True
    except Exception as e:
        print(f"  ❌ 校验失败: {e}")
        return False


def download_model(model_id, local_dir=DEFAULT_DIR, verify=True):
    """从ModelScope下载模型,支持断点续传"""
    os.makedirs(local_dir, exist_ok=True)

    print("\n" + "=" * 60)
    print(f"  📥 模型下载")
    print("=" * 60)
    print(f"  模型ID:   {model_id}")
    print(f"  存储路径: {os.path.abspath(local_dir)}")
    print(f"  完整性校验: {'是' if verify else '否'}")
    print("=" * 60 + "\n")

    target_dir = resolve_model_dir(model_id, local_dir)
    os.makedirs(target_dir, exist_ok=True)
    model_path = snapshot_download(model_id, local_dir=target_dir)
    print(f"\n  ✅ 模型下载完成: {model_path}")

    if verify:
        print()
        if not verify_model(model_id, local_dir):
            print("\n  ⚠️  模型文件可能不完整,建议重新运行下载命令")
            return None
        print("\n  🎉 模型下载并校验完成!")
    else:
        print("\n  🎉 模型下载完成! (已跳过校验)")

    return model_path


def build_parser():
    """构建命令行参数解析器"""
    examples = """
使用示例:
  # 下载默认模型 (qwen/Qwen3-0.6B)
  python download_model.py

  # 下载指定模型
  python download_model.py --model qwen/Qwen3-8B

  # 下载模型到指定目录
  python download_model.py --model qwen/Qwen3-8B --dir /data/models

  # 下载模型并跳过校验
  python download_model.py --model qwen/Qwen3-8B --no-verify

  # 仅校验已下载的模型
  python download_model.py --model qwen/Qwen3-8B --verify-only

"""

    parser = argparse.ArgumentParser(
        description="📦 从魔塔社区(ModelScope)下载模型 — 支持断点续传和完整性校验",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-m", "--model",
        type=str,
        default=DEFAULT_MODEL,
        metavar="MODEL_ID",
        help=f"模型ID,格式为 '组织/模型名' (默认: {DEFAULT_MODEL})",
    )

    parser.add_argument(
        "-d", "--dir",
        type=str,
        default=DEFAULT_DIR,
        metavar="DIR",
        help=f"模型本地存储目录 (默认: {DEFAULT_DIR})",
    )

    parser.add_argument(
        "--no-verify",
        action="store_true",
        default=False,
        help="下载后跳过完整性校验",
    )

    parser.add_argument(
        "--verify-only",
        action="store_true",
        default=False,
        help="仅校验已下载模型的完整性,不下载",
    )


    return parser


if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()


    # 仅校验模式
    if args.verify_only:
        print(f"\n  🔍 校验模型: {args.model}")
        print(f"  📁 存储路径: {os.path.abspath(args.dir)}\n")
        sys.exit(0 if verify_model(args.model, args.dir) else 1)

    # 下载模型
    result = download_model(args.model, args.dir, verify=not args.no_verify)
    sys.exit(0 if result else 1)

