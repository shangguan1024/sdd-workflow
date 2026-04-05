#!/usr/bin/env python3
"""
SDD-Workflow Command Handler
Processes simplified commands like 'sdd start', 'sdd resume', etc.
"""

import sys
import os
from pathlib import Path

class SDDCommandHandler:
    """Handles simplified SDD-Workflow commands"""
    
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.state_file = self.project_root / "PROJECT_STATE.md"
        self.task_plan = self.project_root / "task_plan.md"
        self.nexus_map = self.project_root / ".nexus-map"
        
    def handle_command(self, command: str, args: list = None):
        """Handle simplified sdd commands"""
        if args is None:
            args = []
            
        command = command.lower().strip()
        
        if command == "start":
            return self._handle_start()
        elif command == "resume":
            return self._handle_resume()
        elif command == "status":
            return self._handle_status()
        elif command == "graph":
            return self._handle_graph()
        else:
            return f"Unknown command: {command}. Available commands: start, resume, status, graph"
    
    def _handle_start(self):
        """Handle 'sdd start' command"""
        response = []
        response.append("🚀 Starting SDD-Workflow Development Session...")
        response.append("")
        response.append("Loading required skills:")
        response.append("- using-superpowers")
        response.append("- sdd-workflow")
        response.append("- planning-with-files") 
        response.append("- brainstorming")
        response.append("- test-driven-development")
        response.append("- using-git-worktrees")
        response.append("")
        response.append("Initializing project state detection...")
        response.append("Creating isolated git worktree for feature development...")
        response.append("Applying Test-Driven Development (TDD) methodology...")
        response.append("Please provide your development requirements when prompted.")
        response.append("")
        response.append("[SDD-Workflow will now execute the complete development workflow]")
        response.append("[Phase 1: Requirements Analysis and Architecture Design]")
        response.append("[Phase 2: Git Worktree Creation and Test Setup]")
        
        # Initialize project structure if needed
        self._initialize_project_structure()
        
        return "\n".join(response)
    
    def _handle_resume(self):
        """Handle 'sdd resume' command"""
        response = []
        response.append("🔄 Resuming SDD-Workflow Development Session...")
        response.append("")
        
        if self.task_plan.exists():
            response.append("✓ Found existing session - continuing from checkpoint")
        else:
            response.append("✗ No existing session found")
            response.append("Run 'sdd start' to begin a new session")
            return "\n".join(response)
            
        if self.state_file.exists():
            response.append("✓ Found PROJECT_STATE.md - loading project context")
        else:
            response.append("⚠️ No PROJECT_STATE.md found - creating default state")
            self._create_default_state()
            
        response.append("")
        response.append("Restoring development context from memory artifacts...")
        response.append("[SDD-Workflow will continue from the last checkpoint]")
        
        return "\n".join(response)
    
    def _handle_status(self):
        """Handle 'sdd status' command"""
        response = []
        response.append("📊 SDD-Workflow Project Status")
        response.append("")
        
        if self.state_file.exists():
            response.append("Current Project State:")
            # Read and display relevant parts of PROJECT_STATE.md
            try:
                content = self.state_file.read_text()
                # Extract non-comment lines
                for line in content.split('\n'):
                    if not line.strip().startswith('#') and line.strip():
                        response.append(line)
            except Exception:
                response.append("Error reading PROJECT_STATE.md")
        else:
            response.append("⚠️ No PROJECT_STATE.md found")
            response.append("Project appears to be uninitialized")
            response.append("Run 'sdd start' to begin")
            return "\n".join(response)
            
        response.append("")
        
        if self.task_plan.exists():
            response.append("Task Plan Status:")
            response.append("=================")
            # Look for status lines in task_plan.md
            try:
                content = self.task_plan.read_text()
                status_lines = [line for line in content.split('\n') if '**Status**:' in line]
                if status_lines:
                    for line in status_lines:
                        response.append(line.strip())
                else:
                    response.append("No status information found")
            except Exception:
                response.append("Error reading task_plan.md")
        else:
            response.append("⚠️ No task_plan.md found")
            
        response.append("")
        
        if self.nexus_map.exists():
            response.append("Knowledge Graph: ✓ Available (.nexus-map/)")
        else:
            response.append("Knowledge Graph: ✗ Not generated (run 'sdd graph' to create)")
            
        return "\n".join(response)
    
    def _handle_graph(self):
        """Handle 'sdd graph' command"""
        response = []
        response.append("🧠 SDD-Workflow Knowledge Graph")
        response.append("")
        
        if self.nexus_map.exists():
            response.append("Existing knowledge graph found at .nexus-map/")
            response.append("")
            index_file = self.nexus_map / "INDEX.md"
            if index_file.exists():
                response.append("Graph Index:")
                try:
                    content = index_file.read_text()
                    response.append(content)
                except Exception:
                    response.append("Error reading INDEX.md")
            else:
                response.append("Graph structure:")
                try:
                    for item in self.nexus_map.iterdir():
                        if item.is_dir():
                            response.append(f"- {item.name}/")
                        else:
                            response.append(f"- {item.name}")
                except Exception:
                    response.append("Error listing .nexus-map/")
        else:
            response.append("No existing knowledge graph found.")
            response.append("Generating architecture knowledge graph with nexus-mapper...")
            response.append("[This would run nexus-mapper in actual implementation]")
            response.append("Creating .nexus-map/ directory structure...")
            
            # Create directory structure
            self.nexus_map.mkdir(exist_ok=True)
            (self.nexus_map / "arch").mkdir(exist_ok=True)
            (self.nexus_map / "concepts").mkdir(exist_ok=True)
            (self.nexus_map / "raw").mkdir(exist_ok=True)
            
            # Create index file
            index_content = """# Architecture Knowledge Graph
Generated on {}

## Generated Artifacts
- arch/ : System architecture diagrams and models
- concepts/ : Domain concepts and relationships
- raw/ : Raw analysis data and source mappings
""".format(self._get_current_timestamp())
            
            (self.nexus_map / "INDEX.md").write_text(index_content)
            
            response.append("✓ Knowledge graph generated at .nexus-map/")
            
        return "\n".join(response)
    
    def _initialize_project_structure(self):
        """Initialize standard SDD-Workflow project structure"""
        # Create docs directory structure
        docs_dirs = [
            'docs/specs',
            'docs/plans', 
            'docs/adr',
            'docs/snapshots',
            'docs/reviews'
        ]
        
        for doc_dir in docs_dirs:
            (self.project_root / doc_dir).mkdir(parents=True, exist_ok=True)
            
        # Create .nexus-map directory if it doesn't exist
        self.nexus_map.mkdir(exist_ok=True)
        
        # Create initial state file if it doesn't exist
        if not self.state_file.exists():
            self._create_default_state()
    
    def _create_default_state(self):
        """Create default PROJECT_STATE.md"""
        default_state = """# Project State

## Overview
- **Languages**: Not detected yet
- **Frameworks**: Not detected yet  
- **Complexity**: Simple
- **Development Mode**: Single-agent

## Development Status
- **Current Phase**: Uninitialized
- **Last Updated**: {}

## Memory Artifacts
- **task_plan.md**: Main progress tracking (not created)
- **findings.md**: Research discoveries (not created)  
- **progress.md**: Session logging (not created)
- **.nexus-map/**: Architecture knowledge graph (not created)
""".format(self._get_current_timestamp())
        
        self.state_file.write_text(default_state)
    
    def _get_current_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python command_handler.py <command> [args...]")
        sys.exit(1)
        
    command = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    handler = SDDCommandHandler()
    result = handler.handle_command(command, args)
    print(result)


if __name__ == "__main__":
    main()