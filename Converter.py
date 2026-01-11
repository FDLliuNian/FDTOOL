#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
建筑文件转换器  星白本地定制版
"""
import os
import sys
from pathlib import Path
from package.MCStructureManage import Codecs, CommonStructure

def print_banner():
    """打印彩色横幅"""
    banner = [
        "\033[91m╔════════════════════════════════════════════════════╗\033[0m",
        "\033[38;5;208m║ ███████╗██████╗ ████████╗ ██████╗  ██████╗ ██╗     ║\033[0m",
        "\033[93m║ ██╔════╝██╔══██╗╚══██╔══╝██╔═══██╗██╔═══██╗██║     ║\033[0m",
        "\033[92m║ █████╗  ██║  ██║   ██║   ██║   ██║██║   ██║██║     ║\033[0m",
        "\033[96m║ ██╔══╝  ██║  ██║   ██║   ██║   ██║██║   ██║██║     ║\033[0m",
        "\033[94m║ ██║     ███████║   ██║   ╚██████╔╝╚██████╔╝███████╗║\033[0m",
        "\033[95m║ ╚═╝     ╚══════╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝║\033[0m",
        "\033[35m╚════════════════════════════════════════════════════╝\033[0m"
    ]
    
    for line in banner:
        print(line)

class ProgressBar:
    """进度条显示类"""
    def __init__(self, total, width=50):
        self.total = total
        self.width = width
        self.current = 0
        self.success = 0
        self.failed = 0
        
    def update(self, success=True):
        """更新进度"""
        self.current += 1
        if success:
            self.success += 1
        else:
            self.failed += 1
        self.display()
        
    def display(self):
        """显示进度条"""
        percent = self.current / self.total
        filled_length = int(self.width * percent)
        bar = '█' * filled_length + '─' * (self.width - filled_length)
        
        status = f"{self.current}/{self.total}"
        if self.failed > 0:
            status += f" (✓{self.success} ✗{self.failed})"
        
        print(f"\r┣{bar}┫ {percent:.1%} {status}", end='')
        
    def complete(self):
        """完成进度条显示"""
        print()


CODEC_MENU = {
    1: (Codecs.BDX, 'bdx'),
    2: (Codecs.MCSTRUCTURE, 'mcstructure'),
    3: (Codecs.SCHEMATIC, 'schematic'),
    4: (Codecs.MIANYANG_V1, 'json'),
    5: (Codecs.MIANYANG_V2, 'json'),
    6: (Codecs.MIANYANG_V3, 'building'),
    7: (Codecs.GANGBAN_V1, 'json'),
    8: (Codecs.GANGBAN_V2, 'json'),
    9: (Codecs.GANGBAN_V3, 'json'),
    10: (Codecs.GANGBAN_V4, 'json'),
    11: (Codecs.GANGBAN_V5, 'json'),
    12: (Codecs.GANGBAN_V6, 'json'),
    13: (Codecs.GANGBAN_V7, 'reb'),
    14: (Codecs.RUNAWAY, 'json'),
    15: (Codecs.KBDX, 'kbdx'),
    16: (Codecs.FUHONG_V1, 'json'),
    17: (Codecs.FUHONG_V2, 'json'),
    18: (Codecs.FUHONG_V3, 'json'),
    19: (Codecs.FUHONG_V4, 'json'),
    20: (Codecs.FUHONG_V5, 'fhbuild'),
    21: (Codecs.QINGXU_V1, 'json'),
    22: (Codecs.TIMEBUILDER_V1, 'json'),
    23: (Codecs.FunctionCommand, 'zip'),
    24: (Codecs.TextCommand, 'txt'),
}
for k, (codec, ext) in ((25, (Codecs.Schem_V1, 'schem')),
                        (26, (Codecs.Schem_V2, 'schem')),
                        (27, (Codecs.Schem_V3, 'schem'))):
    try:
        CODEC_MENU[k] = (codec, ext)
    except AttributeError:
        pass


def print_codec_menu():
    """打印编码器选择菜单"""
    print("\n" + "═" * 40)
    print("            编码器选择")
    print("═" * 40)
    
    # 分两列显示编码器
    menu_items = []
    for num, (codec, ext) in CODEC_MENU.items():
        if num > 24:
            continue
        name = codec.__name__.replace("Codecs.", "")
        menu_items.append(f"{num:>2}. {name:<20} (.{ext})")
    
    # 分两列打印
    mid = len(menu_items) // 2 + len(menu_items) % 2
    for i in range(mid):
        left = menu_items[i]
        right = menu_items[i + mid] if i + mid < len(menu_items) else ""
        print(f"{left:<40}{right}")
    
    print("═" * 40)


def choose_codec():
    """选择编码器"""
    print_codec_menu()
    while True:
        try:
            c = input("请输入编码器编号（1~24）：").strip()
            if not c:
                continue
            c = int(c)
            if 1 <= c <= 24 and c in CODEC_MENU:
                codec, ext = CODEC_MENU[c]
                name = codec.__name__.replace("Codecs.", "")
                print(f"✓ 已选择：{name} -> .{ext}")
                return codec, ext
            print("编号无效，请重新输入！")
        except ValueError:
            print("请输入有效的数字！")


ALLOW_EXT = {
    'bdx', 'mcstructure', 'schem', 'schematic',
    'json', 'kbdx', 'fhbuild', 'reb', 'building',
}


def list_current_dir_files(root: Path):
    """列出当前目录的有效文件"""
    files = [f for f in root.glob("*")
             if f.is_file() and f.suffix.lower().lstrip('.') in ALLOW_EXT]
    files.sort(key=lambda x: x.name.lower())
    return files


def print_file_table(files):
    """以表格形式打印文件列表"""
    print("\n" + "─" * 60)
    print(f"发现 {len(files)} 个有效文件：")
    print("─" * 60)
    
    # 计算列宽
    max_name_len = max(len(f.name) for f in files) if files else 0
    col_width = min(max_name_len + 5, 40)
    
    # 分三列显示
    cols = 3
    rows = (len(files) + cols - 1) // cols
    
    for row in range(rows):
        line = ""
        for col in range(cols):
            idx = row + col * rows
            if idx < len(files):
                fp = files[idx]
                num = idx + 1
                # 限制文件名显示长度
                name = fp.name
                if len(name) > col_width - 6:
                    name = name[:col_width - 9] + "..."
                line += f"{num:>3}. {name:<{col_width}}"
        print(line)
    print("─" * 60)


def choose_files_interactive(files):
    """交互式选择文件"""
    print_file_table(files)
    
    while True:
        raw = input("\n请选择：\n"
                    "  输入序号（空格或逗号分隔）\n"
                    "  输入 'all' 转换全部文件\n"
                    "  输入 'q' 退出\n"
                    ">>> ").strip().lower()
        
        if raw == 'q':
            sys.exit(0)
        elif raw == 'all':
            print("✓ 选择全部文件")
            return files
        
        try:
            chosen = []
            for seg in raw.replace(",", " ").split():
                i = int(seg)
                if 1 <= i <= len(files):
                    chosen.append(files[i - 1])
                else:
                    raise IndexError
            if chosen:
                print(f"✓ 选择 {len(chosen)} 个文件")
                return chosen
        except (ValueError, IndexError):
            pass
        print("选择无效，请重新输入！")


def convert_file(file_path: Path, input_dir: Path, target_codec, target_ext: str):
    """转换单个文件"""
    try:
        output_dir = input_dir / "Converter"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"{file_path.stem}.{target_ext}"

        struct = CommonStructure.from_buffer(str(file_path))
        struct.save_as(str(output_file), target_codec)

        return True, output_file.name
    except Exception as e:
        return False, str(e)


def main():
    """主函数"""
    # 打印彩色横幅
    print_banner()
    
    # 原来的标题
    print("\033[93m╔══════════════════════════════════════════════╗\033[0m")
    print("\033[93m║        建筑文件转换器 · 流年本地特供版       ║\033[0m")
    print("\033[93m╚══════════════════════════════════════════════╝\033[0m")
    
    input_dir = Path(__file__).resolve().parent
    print(f"\n📁 工作目录：{input_dir}")
    
    # 选择编码器
    target_codec, target_ext = choose_codec()
    
    # 列出文件
    all_files = list_current_dir_files(input_dir)
    if not all_files:
        print("\n⚠  当前目录未找到任何支持的后缀文件！")
        print("支持的后缀：", ", ".join(sorted(ALLOW_EXT)))
        return
    
    # 选择文件
    todo = choose_files_interactive(all_files)
    
    # 创建输出目录
    output_dir = input_dir / "Converter"
    output_dir.mkdir(exist_ok=True)
    
    print(f"\n{'═' * 60}")
    print(f"开始转换 {len(todo)} 个文件")
    print(f"输出目录：{output_dir}")
    print("═" * 60)
    
    # 初始化进度条
    progress = ProgressBar(len(todo))
    print("\n转换进度：")
    progress.display()
    
    # 转换文件
    results = []
    for fp in todo:
        success, info = convert_file(fp, input_dir, target_codec, target_ext)
        progress.update(success)
        results.append((fp.name, success, info))
    
    progress.complete()
    
    # 显示结果摘要
    print(f"\n{'═' * 60}")
    print("转换结果摘要：")
    print("═" * 60)
    
    success_count = sum(1 for _, success, _ in results if success)
    failed_count = len(results) - success_count
    
    if success_count > 0:
        print(f"✓ 成功：{success_count} 个")
        for name, success, info in results:
            if success:
                print(f"  · {name} -> {info}")
    
    if failed_count > 0:
        print(f"\n✗ 失败：{failed_count} 个")
        for name, success, info in results:
            if not success:
                print(f"  · {name}: {info}")
    
    print(f"\n{'═' * 60}")
    print(f"转换完成！文件已保存到：{output_dir}")
    print("流年本地特供版 · 感谢使用！")
    print("═" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠  用户中断操作")
    except Exception as e:
        print(f"\n❌  程序出错：{e}")
    finally:
        input("\n按 Enter 键退出...")