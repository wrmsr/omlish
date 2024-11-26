"""
Build File Syntax

A simplified build file format (build.ninja) is used. Here’s an example:

  ninja
  Copy code
  # Define rules
  rule cc
    command = gcc -c $in -o $out

  rule link
    command = gcc $in -o $out

  # Build targets
  build main.o : cc main.c
  build utils.o : cc utils.c
  build app : link main.o utils.o
  default app

==

How It Works
 1) Rules:
     - Define reusable build commands, e.g., gcc -c $in -o $out.
 2) Build Targets:
     - Specify outputs, dependencies, and the rule to use.
 3) Execution Flow:
     - If the target doesn't exist or is older than any dependency, it rebuilds.
     - Dependencies are built recursively before the target.

==

Usage
 1) Save the Python script as ninja_clone.py.
 2) Create a build file named build.ninja with the syntax above.
 3) Run the build script:
      python ninja_clone.py build.ninja
 4) Build a specific target:
      python ninja_clone.py build.ninja main.o

==

Limitations

 - No support for advanced Ninja features like pools, phony targets, or real-time build output formatting.
 - Assumes a simple command-replacement model with $in and $out.
 - Dependencies must be explicitly declared in the build file.

This implementation demonstrates the essence of Ninja's dependency-based build execution while being simple and
self-contained.
"""
import os
import sys
import subprocess
from collections import defaultdict


class NinjaClone:
    def __init__(self, build_file):
        self.build_file = build_file
        self.rules = {}
        self.targets = {}
        self.load_build_file()

    def log(self, message):
        print(f"[ninja] {message}")

    def load_build_file(self):
        """Parses the build file for rules and targets."""
        current_rule = None
        with open(self.build_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # Ignore comments and empty lines
                if line.startswith("rule"):
                    _, rule_name = line.split(maxsplit=1)
                    current_rule = rule_name
                    self.rules[rule_name] = {}
                elif current_rule and line.startswith("  "):
                    key, value = line.strip().split(" = ", 1)
                    self.rules[current_rule][key] = value
                elif line.startswith("build"):
                    parts = line.split()
                    target = parts[1]
                    dependencies = parts[3:] if " : " in line else []
                    self.targets[target] = {
                        "rule": parts[2],
                        "dependencies": dependencies,
                    }

    def get_file_timestamp(self, path):
        try:
            return os.path.getmtime(path)
        except FileNotFoundError:
            return -1

    def needs_rebuild(self, target):
        """Determines if the target needs to be rebuilt."""
        if target not in self.targets:
            raise ValueError(f"Target '{target}' not found.")
        target_time = self.get_file_timestamp(target)
        dependencies = self.targets[target]["dependencies"]

        # Check if target is older than any dependency or doesn't exist
        for dep in dependencies:
            if self.get_file_timestamp(dep) > target_time:
                return True
        return target_time == -1

    def build_target(self, target):
        """Recursively builds the target if needed."""
        if target not in self.targets:
            raise ValueError(f"Unknown target: {target}")
        if not self.needs_rebuild(target):
            self.log(f"'{target}' is up to date.")
            return

        # Build dependencies first
        for dep in self.targets[target]["dependencies"]:
            if dep in self.targets:  # Only build declared targets
                self.build_target(dep)

        # Execute the rule
        rule_name = self.targets[target]["rule"]
        if rule_name not in self.rules:
            raise ValueError(f"Rule '{rule_name}' not defined.")
        command = self.rules[rule_name]["command"].replace("$out", target)
        for dep in self.targets[target]["dependencies"]:
            command = command.replace("$in", dep, 1)
        self.log(f"Building '{target}' using rule '{rule_name}'.")
        self.log(f"Command: {command}")
        result = subprocess.run(command, shell=True)
        if result.returncode != 0:
            self.log(f"Error: Failed to build '{target}'.")
            sys.exit(result.returncode)

    def build(self, target):
        """Public method to start the build."""
        self.build_target(target)


def main():
    if len(sys.argv) < 2:
        print("Usage: python ninja_clone.py <build_file> [target]")
        sys.exit(1)

    build_file = sys.argv[1]
    target = sys.argv[2] if len(sys.argv) > 2 else "default"

    ninja = NinjaClone(build_file)
    ninja.build(target)


if __name__ == "__main__":
    main()
