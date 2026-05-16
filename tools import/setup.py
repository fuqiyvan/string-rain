from cx_Freeze import setup, Executable
import sys
from pathlib import Path


# --- 1. 解析自定义参数 ---
def parse_custom_args():
    """解析自定义命令行参数"""
    filename = None
    # 遍历参数寻找 --filename
    for i, arg in enumerate(sys.argv):
        if arg == "--filename" and i + 1 < len(sys.argv):
            filename = sys.argv[i + 1]
            # 移除自定义参数，避免cx_Freeze报错
            del sys.argv[i:i + 2]
            break

    if not filename:
        print("错误：未指定要打包的文件名。请使用 --filename 参数指定。")
        sys.exit(1)
    return filename


# --- 2. 路径验证与处理 ---
def validate_and_get_paths(file_full_path):
    """验证路径并返回标准化路径（修改：接收完整文件路径）"""
    # 直接解析传入的完整路径，不再拼接当前脚本目录
    script_path = Path(file_full_path).resolve()

    # 验证文件存在性
    if not script_path.exists():
        print(f"错误：找不到文件 '{script_path}'")
        sys.exit(1)

    # 获取当前脚本目录（用于输出目录的基准）
    base_dir = Path(__file__).parent.resolve()
    # 输出目录（统一放在build_output下，用文件的stem命名，更健壮）
    output_dir = base_dir / "build_output" / script_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    return {
        "base_dir": base_dir,
        "script_path": script_path,
        "output_dir": output_dir
    }


# --- 3. 打包配置 ---
def build_setup_config(script_path, output_dir):
    """构建cx_Freeze配置"""
    # Windows下添加GUI基础（无控制台窗口）
    base = None
    if sys.platform == "win32":
        base = "Win32GUI"  # 如果需要控制台窗口，注释此行

    # 可执行文件配置
    executable = Executable(
        str(script_path),
        base=base,
        target_name=script_path.stem + ".exe"  # 输出exe文件名
    )

    # 打包选项
    build_options = {
        "build_exe": str(output_dir),
        "include_msvcr": True,  # 包含VC运行库
        "optimize": 2,  # 代码优化级别（0-2）
        "zip_include_packages": "*",  # 压缩包包含所有包
        "zip_exclude_packages": "",
        # 可选：排除不需要的库以减小体积
        # "excludes": ["tkinter", "unittest", "email", "http"],
    }

    return {
        "name": script_path.stem,
        "version": "1.0",
        "description": f"Python打包程序 - {script_path.name}",
        "options": {"build_exe": build_options},
        "executables": [executable]
    }


# --- 主执行逻辑 ---
def main():
    # 解析参数
    file_full_path = parse_custom_args()
    # 验证路径（传入完整路径）
    paths = validate_and_get_paths(file_full_path)
    # 构建配置
    setup_config = build_setup_config(paths["script_path"], paths["output_dir"])
    # 执行打包
    setup(**setup_config)
    print(f"✅ 打包完成！输出目录：{paths['output_dir']}")


if __name__ == "__main__":
    main()