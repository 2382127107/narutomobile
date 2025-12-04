import platform
from pathlib import Path
import os
import shutil
import sys

import json

from maa.resource import Resource

from configure import configure_ocr_model  # type: ignore
from utils import working_dir  # type: ignore

install_path = working_dir / Path("install")
version = len(sys.argv) > 1 and sys.argv[1] or "v0.0.1"

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore


def get_dotnet_platform_tag():
    """自动检测当前平台并返回对应的平台标签"""

    os_type = platform.system()
    os_arch = platform.machine()

    print(f"检测到操作系统: {os_type}, 架构: {os_arch}")

    if os_type == "Windows":

        # 在Windows ARM64环境中，platform.machine()可能错误返回AMD64
        # 我们需要检查处理器标识符来确定真实架构
        processor_identifier = os.environ.get("PROCESSOR_IDENTIFIER", "")

        # 检查是否为ARM64处理器
        if "ARMv8" in processor_identifier or "ARM64" in processor_identifier:
            print(f"检测到ARM64处理器: {processor_identifier}")
            os_arch = "ARM64"

        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "AMD64": "win-x64",
            "x86_64": "win-x64",
            "ARM64": "win-arm64",
            "aarch64": "win-arm64",
        }

        platform_tag = arch_mapping.get(os_arch, f"win-{os_arch.lower()}")

    elif os_type == "Darwin":  # macOS
        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "x86_64": "osx-x64",
            "arm64": "osx-arm64",
            "aarch64": "osx-arm64",
        }

        platform_tag = arch_mapping.get(os_arch, f"osx-{os_arch.lower()}")

    elif os_type == "Linux":
        # 映射platform.machine()到pip的平台标签
        arch_mapping = {
            "x86_64": "linux-x64",
            "aarch64": "linux-arm64",
            "arm64": "linux-arm64",
        }

        platform_tag = arch_mapping.get(os_arch, f"linux-{os_arch.lower()}")

    else:
        raise ValueError(f"不支持的操作系统: {os_type}")

    print(f"使用平台标签: {platform_tag}")
    return platform_tag


def install_maafw():
    if not (working_dir / "deps" / "bin").exists():
        print('Please download the MaaFramework to "deps" first.')
        print('请先下载 MaaFramework 到 "deps"。')
        sys.exit(1)

    shutil.copytree(
        working_dir / "deps" / "bin",
        install_path / "runtimes" / get_dotnet_platform_tag() / "native",
        ignore=shutil.ignore_patterns(
            "*MaaDbgControlUnit*",
            "*MaaThriftControlUnit*",
            "*MaaRpc*",
            "*MaaHttp*",
        ),
        dirs_exist_ok=True,
    )

    shutil.copytree(
        working_dir / "deps" / "share" / "MaaAgentBinary",
        install_path / "MaaAgentBinary",
        dirs_exist_ok=True,
    )


def install_resource():
    configure_ocr_model()
    shutil.copytree(
        working_dir / "assets" / "resource",
        install_path / "resource",
        dirs_exist_ok=True,
    )

    shutil.copy2(
        working_dir / "assets" / "interface.json",
        install_path,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    interface["version"] = version
    if "beta" in version:
        interface["welcome"] = "你正在使用的是公测版，这不是一个稳定版本！"
    if "ci" in version:
        interface["welcome"] = "欢迎使用内部测试版本，包含最不稳定但是最新的功能。"

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


def install_chores():
    for file in ["README.md", "LICENSE", "requirements.txt", "CONTACT"]:
        shutil.copy2(
            working_dir / file,
            install_path,
        )

    shutil.copytree(
        working_dir / "docs",
        install_path / "docs",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("*.yaml"),
    )

    shutil.copy2(
        working_dir / "docs" / "cover.ico", install_path / "Assets" / "logo.ico"
    )

    if platform.system() == "Linux":
        shutil.copy2(
            working_dir / "tools" / "ci" / "deploy_python_env_linux.sh",
            install_path / "deploy_python_env_linux.sh",
        )


def install_agent():
    shutil.copytree(
        working_dir / "agent",
        install_path / "agent",
        dirs_exist_ok=True,
    )

    with open(install_path / "interface.json", "r", encoding="utf-8") as f:
        interface = json.load(f)

    if sys.platform.startswith("win"):
        interface["agent"]["child_exec"] = r"{PROJECT_DIR}/python/python.exe"
    elif sys.platform.startswith("darwin"):
        interface["agent"]["child_exec"] = r"{PROJECT_DIR}/python/bin/python3"
    elif sys.platform.startswith("linux"):
        interface["agent"]["child_exec"] = r"python3"

    interface["agent"]["child_args"] = ["-u", r"{PROJECT_DIR}/agent/main.py"]

    with open(install_path / "interface.json", "w", encoding="utf-8") as f:
        json.dump(interface, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    install_maafw()
    install_resource()
    install_chores()
    install_agent()

    print(f"Install to {install_path} successfully.")
