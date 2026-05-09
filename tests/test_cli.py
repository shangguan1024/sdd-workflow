"""
CLI Tests
Test CLI command parsing and execution
"""


from pathlib import Path


class TestCLIImports:
    """Test CLI imports correctly"""
    
    def test_cli_imports(self):
        """Test CLI can be imported"""
        from src.cli import CLI
        assert CLI is not None
    
    def test_command_classes(self):
        """Test all Command classes exist"""
        from src.cli import (
            Command,
            InitCommand,
            StartCommand,
            ResumeCommand,
            StatusCommand,
            CompleteCommand,
            HelpCommand,
        )
        
        assert Command is not None
        assert InitCommand is not None
        assert StartCommand is not None
        assert ResumeCommand is not None
        assert StatusCommand is not None
        assert CompleteCommand is not None
        assert HelpCommand is not None


class TestCommandParsing:
    """Test CLI command parsing"""
    
    def setup_method(self):
        """Setup CLI instance"""
        from src.cli import CLI
        self.cli = CLI()
    
    def test_parse_init_command(self):
        """Test parsing init command"""
        from src.cli import InitCommand
        
        command = self.cli.parse(["init"])
        assert isinstance(command, InitCommand)
    
    def test_parse_start_command(self):
        """Test parsing start command"""
        from src.cli import StartCommand
        
        command = self.cli.parse(["start", "test-feature"])
        assert isinstance(command, StartCommand)
        assert command.args["feature"] == "test-feature"
    
    def test_parse_resume_command(self):
        """Test parsing resume command"""
        from src.cli import ResumeCommand
        
        command = self.cli.parse(["resume", "test-feature"])
        assert isinstance(command, ResumeCommand)
        assert command.args["feature"] == "test-feature"
    
    def test_parse_resume_without_feature(self):
        """Test parsing resume without feature"""
        from src.cli import ResumeCommand
        
        command = self.cli.parse(["resume"])
        assert isinstance(command, ResumeCommand)
        assert command.args.get("feature") is None
    
    def test_parse_status_command(self):
        """Test parsing status command"""
        from src.cli import StatusCommand
        
        command = self.cli.parse(["status", "test-feature"])
        assert isinstance(command, StatusCommand)
        assert command.args["feature"] == "test-feature"
    
    def test_parse_complete_command(self):
        """Test parsing complete command"""
        from src.cli import CompleteCommand
        
        command = self.cli.parse(["complete", "test-feature"])
        assert isinstance(command, CompleteCommand)
        assert command.args["feature"] == "test-feature"
    
    def test_parse_complete_without_feature(self):
        """Test parsing complete without feature"""
        from src.cli import CompleteCommand
        
        command = self.cli.parse(["complete"])
        assert isinstance(command, CompleteCommand)
        assert command.args.get("feature") is None
    
    def test_parse_help_command(self):
        """Test parsing help command"""
        from src.cli import HelpCommand
        
        command = self.cli.parse(["help"])
        assert isinstance(command, HelpCommand)
    
    def test_parse_empty_args(self):
        """Test parsing empty args returns help"""
        from src.cli import HelpCommand
        
        command = self.cli.parse([])
        assert isinstance(command, HelpCommand)
    
    def test_parse_unknown_command_raises_error(self):
        """Test unknown command raises CLIError"""
        from src.cli import CLIError
        
        try:
            self.cli.parse(["unknown"])
            assert False, "Should have raised CLIError"
        except CLIError:
            pass


class TestCommandStructure:
    """Test Command structure"""
    
    def test_command_base_class(self):
        """Test Command base class"""
        from src.cli import Command
        
        cmd = Command("test", {"arg": "value"})
        
        assert cmd.name == "test"
        assert cmd.args["arg"] == "value"
    
    def test_init_command_args(self):
        """Test InitCommand arguments"""
        from src.cli import InitCommand
        
        cmd = InitCommand(
            path=Path("/tmp"),
            template="rust",
            force=True,
            no_git=True,
        )
        
        assert cmd.args["path"] == Path("/tmp")
        assert cmd.args["template"] == "rust"
        assert cmd.args["force"] == True
        assert cmd.args["no_git"] == True
    
    def test_start_command_args(self):
        """Test StartCommand arguments"""
        from src.cli import StartCommand
        
        cmd = StartCommand(
            feature="test-feature",
            capability="understanding",
            no_interactive=True,
        )
        
        assert cmd.args["feature"] == "test-feature"
        assert cmd.args["capability"] == "understanding"
        assert cmd.args["no_interactive"] == True
    
    def test_status_command_verbose(self):
        """Test StatusCommand verbose flag"""
        from src.cli import StatusCommand
        
        cmd = StatusCommand(feature="test", verbose=True)
        
        assert cmd.args["feature"] == "test"
        assert cmd.args["verbose"] == True


class TestCLICommands:
    """Test CLI command list"""
    
    def test_available_commands(self):
        """Test CLI has all expected commands"""
        from src.cli import CLI
        
        cli = CLI()
        
        assert "init" in cli.COMMANDS
        assert "start" in cli.COMMANDS
        assert "resume" in cli.COMMANDS
        assert "status" in cli.COMMANDS
        assert "complete" in cli.COMMANDS
        assert "help" in cli.COMMANDS
    
    def test_commands_count(self):
        """Test CLI has 6 commands"""
        from src.cli import CLI
        
        cli = CLI()
        
        assert len(cli.COMMANDS) == 6


class TestCLIError:
    """Test CLI error handling"""
    
    def test_cli_error_class(self):
        """Test CLIError class exists"""
        from src.cli import CLIError
        
        assert CLIError is not None
    
    def test_cli_error_message(self):
        """Test CLIError message"""
        from src.cli import CLIError
        
        error = CLIError("Test error")
        
        assert str(error) == "Test error"
