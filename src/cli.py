"""
SDD-Workflow CLI Entry (Layer 0)
命令行解析和用户交互
"""

import sys
from pathlib import Path
from typing import Optional, List


class Command:
    """命令基类"""
    
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args


class InitCommand(Command):
    """sdd init 命令"""
    
    def __init__(
        self,
        path: Optional[Path] = None,
        template: str = "standard",
        force: bool = False,
        no_git: bool = False,
    ):
        super().__init__("init", {
            "path": path,
            "template": template,
            "force": force,
            "no_git": no_git,
        })


class StartCommand(Command):
    """sdd start 命令"""
    
    def __init__(
        self,
        feature: str,
        capability: Optional[str] = None,
        no_interactive: bool = False,
    ):
        super().__init__("start", {
            "feature": feature,
            "capability": capability,
            "no_interactive": no_interactive,
        })


class ResumeCommand(Command):
    """sdd resume 命令"""
    
    def __init__(self, feature: Optional[str] = None):
        super().__init__("resume", {"feature": feature})


class StatusCommand(Command):
    """sdd status 命令"""
    
    def __init__(self, feature: Optional[str] = None, verbose: bool = False):
        super().__init__("status", {"feature": feature, "verbose": verbose})


class CompleteCommand(Command):
    """sdd complete 命令"""
    
    def __init__(self):
        super().__init__("complete", {})


class HelpCommand(Command):
    """sdd help 命令"""
    
    def __init__(self):
        super().__init__("help", {})


class CLI:
    """CLI 入口，负责命令解析"""
    
    COMMANDS = ["init", "start", "resume", "status", "complete", "help"]
    
    def __init__(self):
        self.commands = {
            "init": self._parse_init,
            "start": self._parse_start,
            "resume": self._parse_resume,
            "status": self._parse_status,
            "complete": self._parse_complete,
            "help": self._parse_help,
        }
    
    def parse(self, args: List[str]) -> Command:
        """
        解析命令行参数
        
        Args:
            args: 命令行参数列表 (不含程序名)
            
        Returns:
            Command 对象
            
        Raises:
            CLIError: 参数解析失败
        """
        if not args:
            return HelpCommand()
        
        cmd_name = args[0]
        
        if cmd_name not in self.COMMANDS:
            raise CLIError(f"Unknown command: {cmd_name}. Available: {', '.join(self.COMMANDS)}")
        
        return self.commands[cmd_name](args[1:])
    
    def _parse_init(self, args: List[str]) -> InitCommand:
        """解析 init 命令"""
        import argparse
        
        parser = argparse.ArgumentParser(prog="sdd init")
        parser.add_argument("--path", type=Path)
        parser.add_argument("--template", default="standard")
        parser.add_argument("--force", action="store_true")
        parser.add_argument("--no-git", action="store_true")
        
        parsed, remaining = parser.parse_known_args(args)
        
        return InitCommand(
            path=parsed.path,
            template=parsed.template,
            force=parsed.force,
            no_git=parsed.no_git,
        )
    
    def _parse_start(self, args: List[str]) -> StartCommand:
        """解析 start 命令"""
        import argparse
        
        parser = argparse.ArgumentParser(prog="sdd start")
        parser.add_argument("feature", type=str)
        parser.add_argument("--capability")
        parser.add_argument("--no-interactive", action="store_true")
        
        parsed, remaining = parser.parse_known_args(args)
        
        return StartCommand(
            feature=parsed.feature,
            capability=parsed.capability,
            no_interactive=parsed.no_interactive,
        )
    
    def _parse_resume(self, args: List[str]) -> ResumeCommand:
        """解析 resume 命令"""
        import argparse
        
        parser = argparse.ArgumentParser(prog="sdd resume")
        parser.add_argument("feature", nargs="?", type=str)
        
        parsed, remaining = parser.parse_known_args(args)
        
        return ResumeCommand(feature=parsed.feature)
    
    def _parse_status(self, args: List[str]) -> StatusCommand:
        """解析 status 命令"""
        import argparse
        
        parser = argparse.ArgumentParser(prog="sdd status")
        parser.add_argument("feature", nargs="?", type=str)
        parser.add_argument("--verbose", "-v", action="store_true")
        
        parsed, remaining = parser.parse_known_args(args)
        
        return StatusCommand(feature=parsed.feature, verbose=parsed.verbose)
    
    def _parse_complete(self, args: List[str]) -> CompleteCommand:
        """解析 complete 命令"""
        return CompleteCommand()
    
    def _parse_help(self, args: List[str]) -> HelpCommand:
        """解析 help 命令"""
        return HelpCommand()
    
    def execute(self, command: Command) -> int:
        """
        执行命令
        
        Args:
            command: 解析后的命令对象
            
        Returns:
            退出码 (0 表示成功)
        """
        from .director import Director
        
        if isinstance(command, HelpCommand):
            self._print_help()
            return 0
        
        if isinstance(command, InitCommand):
            director = Director()
            result = director.initialize(command)
            self._print_result(result)
            return 0 if result.success else 1
        
        if isinstance(command, StartCommand):
            director = Director()
            result = director.start_feature(command)
            self._print_result(result)
            return 0 if result.success else 1
        
        if isinstance(command, ResumeCommand):
            director = Director()
            result = director.resume_feature(command)
            self._print_result(result)
            return 0 if result.success else 1
        
        if isinstance(command, StatusCommand):
            director = Director()
            result = director.show_status(command)
            self._print_result(result)
            return 0 if result.success else 1
        
        if isinstance(command, CompleteCommand):
            director = Director()
            result = director.complete(command)
            self._print_result(result)
            return 0 if result.success else 1
        
        raise CLIError(f"Unknown command type: {type(command)}")
    
    def _print_result(self, result: "Result"):
        """打印执行结果"""
        if result.success:
            print(f"✅ {result.message}")
        else:
            print(f"❌ {result.message}")
        
        if result.details:
            for detail in result.details:
                print(f"  {detail}")
    
    def _print_help(self):
        """打印帮助信息"""
        help_text = """
SDD-Workflow v2.0
==================

Usage: sdd <command> [options]

Commands:
  init <path>           Initialize SDD workflow in a project
  start <feature>        Start developing a new feature
  resume [feature]      Resume an interrupted workflow
  status               Show current project status
  complete             Complete current workflow
  help                 Show this help message

Options:
  --path <path>         Project path (default: current directory)
  --template <tmpl>     Project template (standard, rust, python, etc.)
  --capability <name>   Specify capability to use
  --verbose             Show detailed output

Examples:
  sdd init
  sdd init --path ./my-project --template rust
  sdd start my-feature
  sdd start custom-log --capability brainstorm-ai-assisted
  sdd resume
  sdd status --verbose

For more information, see: https://github.com/shangguan1024/sdd-workflow
"""
        print(help_text)


class CLIError(Exception):
    """CLI 错误"""
    pass


class Result:
    """命令执行结果"""
    
    def __init__(
        self,
        success: bool,
        message: str,
        details: Optional[List[str]] = None,
    ):
        self.success = success
        self.message = message
        self.details = details or []


def main():
    """CLI 入口点"""
    cli = CLI()
    
    try:
        # 跳过程序名
        args = sys.argv[1:]
        command = cli.parse(args)
        exit_code = cli.execute(command)
        sys.exit(exit_code)
    except CLIError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
