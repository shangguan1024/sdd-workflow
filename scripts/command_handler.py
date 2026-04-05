#!/usr/bin/env python3
"""
SDD-Workflow Command Handler
Processes simplified commands like 'sdd start', 'sdd resume', etc.
"""

import sys
import os
from pathlib import Path
from datetime import datetime


class SDDCommandHandler:
    """Handles simplified SDD-Workflow commands"""

    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "PROJECT_STATE.md"
        self.task_plan = self.project_root / "task_plan.md"
        self.nexus_map = self.project_root / ".nexus-map"
        self.features_dir = self.project_root / "docs" / "features"
        self.constitution_file = self.project_root / "CONSTITUTION.md"

    def handle_command(self, command: str, args: list = None):
        """Handle simplified sdd commands"""
        if args is None:
            args = []

        command = command.lower().strip()

        if command == "init":
            return self._handle_init()
        elif command == "check-init":
            return self._handle_check_init()
        elif command == "start":
            return self._handle_start(args)
        elif command == "resume":
            return self._handle_resume(args)
        elif command == "status":
            return self._handle_status()
        elif command == "list-features":
            return self._handle_list_features()
        elif command == "graph":
            return self._handle_graph()
        elif command == "help":
            return self._handle_help()
        else:
            return f"Unknown command: {command}\nAvailable: init, check-init, start, resume, status, list-features, graph, help"

    def _handle_init(self):
        """Handle 'sdd init' command - Initialize project structure"""
        response = []
        response.append("🚀 Initializing SDD-Workflow Project...")
        response.append("")

        dirs_to_create = [
            "docs/specs",
            "docs/plans",
            "docs/adr",
            "docs/snapshots",
            "docs/reviews",
            "docs/features",
            "docs/knowledge",
            "docs/modules",
            "docs/superpowers/specs",
            "docs/superpowers/plans",
        ]

        for d in dirs_to_create:
            path = self.project_root / d
            path.mkdir(parents=True, exist_ok=True)
            response.append(f"  ✓ Created: {d}/")

        if not self.state_file.exists():
            self._create_default_state()
            response.append(f"  ✓ Created: PROJECT_STATE.md")

        if not self.constitution_file.exists():
            self._create_constitution()
            response.append(f"  ✓ Created: CONSTITUTION.md")

        self.nexus_map.mkdir(exist_ok=True)
        (self.nexus_map / "arch").mkdir(exist_ok=True)
        (self.nexus_map / "concepts").mkdir(exist_ok=True)
        (self.nexus_map / "raw").mkdir(exist_ok=True)
        response.append(f"  ✓ Created: .nexus-map/")

        response.append("")
        response.append("✅ SDD-Workflow Initialized")
        response.append("")
        response.append("Next: sdd start <feature-name>")

        return "\n".join(response)

    def _handle_check_init(self):
        """Handle 'sdd check-init' command - Check initialization status"""
        response = []
        response.append("🔍 SDD-Workflow Initialization Check")
        response.append("")

        checks = [
            ("Directory structure", self._check_dirs()),
            ("Constitution", self.constitution_file.exists()),
            ("Memory artifacts", self._check_memory_artifacts()),
        ]

        all_pass = True
        for name, passed in checks:
            status = "✓" if passed else "✗"
            response.append(f"  {status} {name}")
            if not passed:
                all_pass = False

        response.append("")
        if all_pass:
            response.append("✅ Project already initialized")
        else:
            response.append("⚠️ Project not fully initialized")
            response.append("Run 'sdd init' to initialize")

        return "\n".join(response)

    def _check_dirs(self):
        """Check if required directories exist"""
        required = ["docs/specs", "docs/plans", "docs/reviews"]
        return all((self.project_root / d).exists() for d in required)

    def _check_memory_artifacts(self):
        """Check if memory artifacts exist"""
        artifacts = ["PROJECT_STATE.md", "AGENTS.md", "task_plan.md"]
        return all((self.project_root / f).exists() for f in artifacts)

    def _create_default_state(self):
        """Create default PROJECT_STATE.md"""
        timestamp = self._get_current_timestamp()
        content = f"""# Project State - {timestamp}

## Overview
- **Languages**: Not detected yet
- **Frameworks**: Not detected yet
- **Complexity**: Simple
- **Development Mode**: Single-agent

## Development Status
- **Current Phase**: Initialized
- **Last Updated**: {timestamp}
- **Active Features**: None

## Memory Artifacts
- **task_plan.md**: Main progress tracking
- **findings.md**: Research discoveries
- **progress.md**: Session logging
- **.nexus-map/**: Architecture knowledge graph

## Skills Used
- sdd-workflow: ✅ Active
"""
        self.state_file.write_text(content)

    def _create_constitution(self):
        """Create CONSTITUTION.md"""
        content = """# Project Constitution

## Core Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Open/Closed**: Open for extension, closed for modification
3. **Liskov Substitution**: Subtypes must be substitutable
4. **Interface Segregation**: Many specific interfaces > one general
5. **Dependency Inversion**: Depend on abstractions

## Quality Gates

- All code must compile before commit
- Tests must pass before Phase completion
- Review artifacts required for Phase 5
- Memory artifacts required for Phase 6

## Workflow Compliance

All features must follow SDD-Workflow phases:
1. Requirements Analysis & Design
2. Implementation Planning
3. Module Development
4. Integration & Testing
5. Code Quality Review
6. Memory Persistence
"""
        self.constitution_file.write_text(content)

    def _handle_start(self, args):
        """Handle 'sdd start <feature>' command"""
        if not args:
            return "Usage: sdd start <feature-name>\nExample: sdd start custom-format"

        feature_name = args[0].lower().strip()
        response = []
        response.append(f"🚀 Starting SDD-Workflow for Feature: {feature_name}")
        response.append("")
        response.append("Loading required skills:")
        response.append("- using-superpowers")
        response.append("- sdd-workflow")
        response.append("- brainstorming")
        response.append("- writing-plans")
        response.append("- test-driven-development")
        response.append("")
        response.append("Initializing project state detection...")
        response.append(f"Creating feature directory: docs/features/{feature_name}/")
        response.append("")

        feature_dir = self.features_dir / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)

        status_file = feature_dir / "status.toml"
        if not status_file.exists():
            timestamp = self._get_current_timestamp()
            status_content = f'''current_phase = 1
status = "initialized"
started = "{timestamp}"
last_updated = "{timestamp}"
'''
            status_file.write_text(status_content)
            response.append(f"  ✓ Created: docs/features/{feature_name}/status.toml")

        response.append("")
        response.append("[SDD-Workflow will execute Phase 1: Requirements Analysis]")
        response.append("[Use 'sdd resume' to continue after interruption]")

        return "\n".join(response)

    def _handle_resume(self, args):
        """Handle 'sdd resume [feature]' command"""
        if args:
            feature_name = args[0].lower().strip()
            return self._resume_feature(feature_name)

        return self._show_feature_list()

    def _resume_feature(self, feature_name):
        """Resume a specific feature"""
        feature_dir = self.features_dir / feature_name
        status_file = feature_dir / "status.toml"

        if not status_file.exists():
            return f"❌ Feature '{feature_name}' not found.\nRun 'sdd start {feature_name}' first."

        response = []
        response.append(f"🔄 Resuming SDD-Workflow for Feature: {feature_name}")
        response.append("")

        try:
            status_content = status_file.read_text()
            phase = self._extract_phase(status_content)
            response.append(f"  Current Phase: {phase}")
            response.append("")
            response.append("Loading development context from memory artifacts...")
            response.append("[SDD-Workflow will continue from the last checkpoint]")
            response.append("")
            response.append("Next steps:")
            response.append("1. Review task_plan.md for pending tasks")
            response.append("2. Run 'sdd status' for detailed progress")
            response.append("3. Continue development from last phase")
        except Exception as e:
            return f"❌ Error reading feature status: {e}"

        return "\n".join(response)

    def _show_feature_list(self):
        """Show list of all features"""
        response = []
        response.append("📋 SDD Feature List")
        response.append("")

        if not self.features_dir.exists():
            response.append("No features found.")
            response.append("Run 'sdd start <feature-name>' to create one.")
            return "\n".join(response)

        features = list(self.features_dir.iterdir())
        if not features:
            response.append("No features found.")
            response.append("Run 'sdd start <feature-name>' to create one.")
            return "\n".join(response)

        response.append("Active Features:")
        response.append("═" * 50)

        for feat in features:
            if feat.is_dir():
                status_file = feat / "status.toml"
                phase = "unknown"
                status = "unknown"
                if status_file.exists():
                    content = status_file.read_text()
                    phase = self._extract_phase(content)
                    status = self._extract_status(content)

                response.append(f"  • {feat.name:<20} [Phase {phase}: {status}]")

        response.append("")
        response.append("Usage:")
        response.append("  sdd resume <feature-name>   # Resume specific feature")
        response.append("  sdd start <feature-name>    # Start new feature")

        return "\n".join(response)

    def _extract_phase(self, content):
        """Extract phase number from status.toml"""
        for line in content.split("\n"):
            if line.startswith("current_phase"):
                return line.split("=")[1].strip()
        return "?"

    def _extract_status(self, content):
        """Extract status from status.toml"""
        for line in content.split("\n"):
            if line.startswith("status"):
                return line.split("=")[1].strip().strip('"')
        return "?"

    def _handle_status(self):
        """Handle 'sdd status' command"""
        response = []
        response.append("📊 SDD-Workflow Project Status")
        response.append("")

        if self.state_file.exists():
            try:
                content = self.state_file.read_text()
                lines = [
                    l
                    for l in content.split("\n")
                    if l.strip() and not l.strip().startswith("#")
                ]
                for line in lines[:15]:
                    response.append(f"  {line}")
            except Exception:
                response.append("  Error reading PROJECT_STATE.md")
        else:
            response.append("  ⚠️ No PROJECT_STATE.md found")

        response.append("")

        if self.task_plan.exists():
            response.append("Task Plan Status:")
            response.append("═" * 50)
            try:
                content = self.task_plan.read_text()
                status_lines = [
                    l.strip() for l in content.split("\n") if "**Status**" in l
                ]
                for line in status_lines:
                    response.append(f"  {line}")
            except Exception:
                response.append("  Error reading task_plan.md")
        else:
            response.append("  ⚠️ No task_plan.md found")

        response.append("")
        response.append("Features:")
        response.append("═" * 50)

        if self.features_dir.exists():
            features = [f for f in self.features_dir.iterdir() if f.is_dir()]
            if features:
                for feat in features:
                    status_file = feat / "status.toml"
                    if status_file.exists():
                        content = status_file.read_text()
                        phase = self._extract_phase(content)
                        status = self._extract_status(content)
                        response.append(f"  • {feat.name:<20} Phase {phase}: {status}")
            else:
                response.append("  No features found")
        else:
            response.append("  No features directory found")

        response.append("")

        if self.nexus_map.exists():
            response.append("Knowledge Graph: ✓ Available (.nexus-map/)")
        else:
            response.append("Knowledge Graph: ✗ Not generated")

        return "\n".join(response)

    def _handle_list_features(self):
        """Handle 'sdd list-features' command"""
        return self._show_feature_list()

    def _handle_graph(self):
        """Handle 'sdd graph' command"""
        response = []
        response.append("🧠 SDD-Workflow Knowledge Graph")
        response.append("")

        if self.nexus_map.exists():
            response.append("Existing knowledge graph found at .nexus-map/")
            response.append("")
            try:
                for item in self.nexus_map.iterdir():
                    if item.is_dir():
                        response.append(f"  📁 {item.name}/")
                    else:
                        response.append(f"  📄 {item.name}")
            except Exception:
                response.append("Error listing .nexus-map/")
        else:
            response.append("No knowledge graph found.")
            response.append("Run 'sdd init' to initialize.")

        return "\n".join(response)

    def _handle_help(self):
        """Handle 'sdd help' command"""
        help_text = """📖 SDD-Workflow Commands

  sdd init              Initialize project structure
  sdd check-init        Check initialization status
  sdd start <feature>   Start new feature development
  sdd resume [feature]   Resume feature (or show list)
  sdd status            Show project status
  sdd list-features     List all features
  sdd graph             Show knowledge graph
  sdd help              Show this help

Examples:
  sdd init
  sdd start custom-format
  sdd resume
  sdd resume custom-format
  sdd status
"""
        return help_text

    def _get_current_timestamp(self):
        """Get current timestamp"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: sdd <command> [args...]")
        print("Run 'sdd help' for available commands")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    handler = SDDCommandHandler()
    result = handler.handle_command(command, args)
    print(result)


if __name__ == "__main__":
    main()
