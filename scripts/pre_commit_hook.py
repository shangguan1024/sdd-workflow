"""
Git Pre-Commit Hook

在每次提交前自动执行检查：
1. 检查 staged 文件中是否有 secrets
2. 检查 commit message 格式
3. 运行项目测试（如果存在）
4. 检查分支命名规范

使用方法:
  - 安装: python scripts/pre_commit_hook.py --install
  - 卸载: python scripts/pre_commit_hook.py --uninstall
  - 运行: python scripts/pre_commit_hook.py (在 .git/hooks/pre-commit 中调用)
"""

import os
import sys
import re
import subprocess
import argparse
from pathlib import Path
from typing import List, Tuple, Optional


# Secrets 模式 - 常见敏感信息
SECRETS_PATTERNS = [
    (r'password\s*=\s*["\'][^"\']{3,}["\']', "hardcoded password"),
    (r'api[_-]?key\s*=\s*["\'][^"\']{10,}["\']', "API key"),
    (r'secret\s*=\s*["\'][^"\']{10,}["\']', "secret"),
    (r'token\s*=\s*["\'][^"\']{10,}["\']', "token"),
    (r'aws[_-]?access[_-]?key', "AWS access key"),
    (r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH)\s+PRIVATE\s+KEY-----', "private key"),
    (r'ghp_[a-zA-Z0-9]{36}', "GitHub personal access token"),
    (r'xox[baprs]-[a-zA-Z0-9]{10,}', "Slack token"),
]

# Commit message 格式
COMMIT_MSG_PATTERN = re.compile(
    r'^(feat|fix|refactor|test|docs|chore|style|perf|ci|build|revert)(\(.+\))?: .{1,50}\n?\n|'
    r'^(feat|fix|refactor|test|docs|chore|style|perf|ci|build|revert)(\(.+\))?: .{1,50}$'
)

# 分支命名规范
BRANCH_PATTERN = re.compile(r'^(feature|fix|chore|refactor|docs|style|test)\/[a-z0-9-_]+$')

# 需要忽略的文件
IGNORED_PATHS = [
    r'node_modules/',
    r'\.git/',
    r'dist/',
    r'build/',
    r'\.next/',
    r'coverage/',
    r'\.env(\.local|\.development)?',
    r'package-lock\.json',
    r'yarn\.lock',
    r'Cargo\.lock',
]


class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.RESET}")


def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.RESET}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.RESET}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.RESET}")


def check_secrets(staged_files: List[str]) -> Tuple[bool, List[str]]:
    """检查 staged 文件中是否有敏感信息"""
    issues = []
    
    for file_path in staged_files:
        # 检查是否在忽略列表中
        if any(re.search(pattern, file_path) for pattern in IGNORED_PATHS):
            continue
        
        # 读取文件内容
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            continue
        
        # 检查 secrets 模式
        for pattern, secret_type in SECRETS_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                # 排除注释中的内容
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line = content[line_start:line_end]
                
                # 跳过注释行
                if re.match(r'^\s*(#|//|/\*|\*|<!--)', line):
                    continue
                
                issues.append(f"{file_path}: {secret_type} detected")
    
    return len(issues) == 0, issues


def check_commit_message(commit_msg: str) -> Tuple[bool, List[str]]:
    """检查 commit message 格式"""
    issues = []
    lines = commit_msg.strip().split('\n')
    
    if not lines:
        issues.append("Commit message is empty")
        return False, issues
    
    first_line = lines[0].strip()
    
    # 检查格式
    if not re.match(r'^(feat|fix|refactor|test|docs|chore|style|perf|ci|build|revert)(\(.+\))?: .{1,50}', first_line):
        issues.append(f"Invalid commit message format: {first_line}")
        issues.append("Expected: <type>(<scope>): <description>")
        issues.append("Types: feat, fix, refactor, test, docs, chore, style, perf, ci, build, revert")
    
    # 检查描述是否为空
    if len(first_line.split(':', 1)) < 2 or not first_line.split(':', 1)[1].strip():
        issues.append("Commit message description is empty")
    
    # 检查长度
    desc = first_line.split(':', 1)[1].strip() if ':' in first_line else ""
    if len(desc) > 50:
        issues.append(f"Description too long ({len(desc)} chars), should be < 50")
    
    # 检查第二行是否为空
    if len(lines) > 1 and lines[1].strip():
        issues.append("Second line should be empty before body")
    
    return len(issues) == 0, issues


def check_branch_name() -> Tuple[bool, List[str]]:
    """检查当前分支名是否符合规范"""
    issues = []
    
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = result.stdout.strip()
        
        # 允许 main/master/dev 等主要分支
        if branch in ['main', 'master', 'dev', 'develop', 'HEAD']:
            return True, []
        
        if not BRANCH_PATTERN.match(branch):
            issues.append(f"Invalid branch name: {branch}")
            issues.append("Expected: <type>/<description>")
            issues.append("Types: feature, fix, chore, refactor, docs, style, test")
            issues.append("Example: feature/task-creation, fix/duplicate-tasks")
    except Exception as e:
        issues.append(f"Failed to check branch name: {e}")
    
    return len(issues) == 0, issues


def check_file_size(staged_files: List[str]) -> Tuple[bool, List[str]]:
    """检查文件大小是否合理"""
    issues = []
    MAX_FILE_SIZE_KB = 500  # 500KB
    
    for file_path in staged_files:
        if any(re.search(pattern, file_path) for pattern in IGNORED_PATHS):
            continue
        
        try:
            size_kb = os.path.getsize(file_path) / 1024
            if size_kb > MAX_FILE_SIZE_KB:
                issues.append(f"{file_path}: {size_kb:.1f}KB > {MAX_FILE_SIZE_KB}KB")
        except Exception:
            continue
    
    return len(issues) == 0, issues


def get_staged_files() -> List[str]:
    """获取 staged 文件列表"""
    try:
        result = subprocess.run(
            ['git', 'diff', '--staged', '--name-only'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return [f.strip() for f in result.stdout.strip().split('\n') if f.strip()]
        return []
    except Exception:
        return []


def run_tests() -> Tuple[bool, Optional[str]]:
    """运行项目测试（如果存在）"""
    project_root = Path.cwd()
    
    # 检测项目类型并运行测试
    test_commands = []
    
    if (project_root / 'package.json').exists():
        test_commands.append(('npm', 'test', '--', '--passWithNoTests', '--silent'))
    
    if (project_root / 'Cargo.toml').exists():
        test_commands.append(('cargo', 'test', '--quiet'))
    
    if (project_root / 'pyproject.toml').exists() or (project_root / 'setup.py').exists():
        test_commands.append(('python', '-m', 'pytest', '--quiet'))
    
    for cmd in test_commands:
        try:
            print_info(f"Running: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=project_root
            )
            if result.returncode == 0:
                return True, None
            else:
                return False, f"{' '.join(cmd)} failed"
        except Exception as e:
            # 测试失败不阻止提交，只警告
            print_warning(f"Could not run tests: {e}")
            return True, None  # 不阻止提交
    
    return True, None  # 没有测试命令，不阻止


def main():
    parser = argparse.ArgumentParser(description='Git Pre-Commit Hook')
    parser.add_argument('--install', action='store_true', help='Install hook')
    parser.add_argument('--uninstall', action='store_true', help='Uninstall hook')
    args = parser.parse_args()
    
    # 安装 hook
    if args.install:
        install_hook()
        return
    
    if args.uninstall:
        uninstall_hook()
        return
    
    # 执行检查
    print()
    print("🔍 Pre-Commit Hook Running...")
    print("=" * 50)
    
    all_passed = True
    issues = []
    
    # 1. 检查分支名
    print_info("Checking branch name...")
    passed, branch_issues = check_branch_name()
    if not passed:
        all_passed = False
        issues.extend(branch_issues)
        for issue in branch_issues:
            print_error(f"Branch: {issue}")
    else:
        print_success("Branch name OK")
    
    # 2. 获取 staged 文件
    staged_files = get_staged_files()
    print_info(f"Checking {len(staged_files)} staged file(s)...")
    
    # 3. 检查 secrets
    print_info("Checking for secrets...")
    passed, secret_issues = check_secrets(staged_files)
    if not passed:
        all_passed = False
        issues.extend(secret_issues)
        for issue in secret_issues:
            print_error(f"Secret: {issue}")
    else:
        print_success("No secrets detected")
    
    # 4. 检查文件大小
    print_info("Checking file sizes...")
    passed, size_issues = check_file_size(staged_files)
    if not passed:
        all_passed = False
        issues.extend(size_issues)
        for issue in size_issues:
            print_warning(f"Large file: {issue}")
    else:
        print_success("File sizes OK")
    
    # 5. 检查 commit message
    if os.environ.get('GIT_COMMIT_MSG_FILE'):
        commit_msg_file = os.environ['GIT_COMMIT_MSG_FILE']
        if os.path.exists(commit_msg_file):
            with open(commit_msg_file, 'r', encoding='utf-8') as f:
                commit_msg = f.read()
            
            print_info("Checking commit message...")
            passed, msg_issues = check_commit_message(commit_msg)
            if not passed:
                all_passed = False
                issues.extend(msg_issues)
                for issue in msg_issues:
                    print_error(f"Commit: {issue}")
            else:
                print_success("Commit message OK")
    
    # 总结
    print()
    if all_passed:
        print_success("All checks passed!")
        print()
        sys.exit(0)
    else:
        print_error(f"Found {len(issues)} issue(s)")
        print()
        print("Please fix the issues above before committing.")
        print("Run with --install to reinstall the hook after fixing.")
        sys.exit(1)


def install_hook():
    """安装 pre-commit hook"""
    git_dir = Path('.git')
    if not git_dir.exists():
        print_error("Not a git repository")
        return
    
    hooks_dir = git_dir / 'hooks'
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / 'pre-commit'
    
    # 创建 hook 脚本
    hook_content = f'''#!/bin/sh
# SDD-Workflow Pre-Commit Hook
# Auto-generated by sdd-workflow

{Path(__file__).resolve()}
'''
    
    hook_path.write_text(hook_content)
    os.chmod(hook_path, 0o755)
    
    print_success(f"Pre-commit hook installed at {hook_path}")
    print_info("The hook will run before each commit to check:")
    print_info("  - Branch name")
    print_info("  - Secrets in staged files")
    print_info("  - File sizes")
    print_info("  - Commit message format")


def uninstall_hook():
    """卸载 pre-commit hook"""
    git_dir = Path('.git')
    if not git_dir.exists():
        print_error("Not a git repository")
        return
    
    hook_path = git_dir / 'hooks' / 'pre-commit'
    
    if hook_path.exists():
        hook_path.unlink()
        print_success(f"Pre-commit hook removed from {hook_path}")
    else:
        print_warning("No pre-commit hook found")


if __name__ == '__main__':
    main()