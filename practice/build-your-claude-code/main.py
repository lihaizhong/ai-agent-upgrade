#!/usr/bin/env python3
"""
Main entry point for the Coding Agent

Usage:
    python main.py

This script provides a menu to select which loop implementation to run.
"""

import importlib
import sys
from pathlib import Path


def get_available_loops() -> list[tuple[str, str]]:
    """
    Scan the code directory for all s*-loop.py files
    Returns a list of (module_name, display_name) tuples
    """
    code_dir = Path(__file__).parent / "code"
    loop_files = sorted(code_dir.glob("s*-loop.py"))

    loops = []
    for loop_file in loop_files:
        module_name = loop_file.stem  # e.g., "s01-loop"
        display_name = module_name.replace("-", " ").title()  # e.g., "S01 Loop"
        loops.append((module_name, display_name))

    return loops


def import_loop_module(module_name: str):
    """
    Dynamically import a loop module from the code directory
    """
    code_dir = Path(__file__).parent / "code"
    # Add code directory to sys.path if not already there
    if str(code_dir) not in sys.path:
        sys.path.insert(0, str(code_dir))

    return importlib.import_module(module_name)


def display_menu(loops: list[tuple[str, str]]) -> str | None:
    """
    Display a menu of available loops and return the selected module name
    """
    print("\033[33m" + "=" * 50 + "\033[0m")
    print("\033[33m  Coding Agent - Loop Selection\033[0m")
    print("\033[33m" + "=" * 50 + "\033[0m")
    print()

    if not loops:
        print("\033[31mNo loop implementations found in 'code' directory!\033[0m")
        return None

    for idx, (module_name, display_name) in enumerate(loops, 1):
        print(f"  \033[36m{idx}.\033[0m {display_name}")

    print()
    print("  \033[36m0.\033[0m Exit")
    print()

    try:
        choice = input("\033[36mSelect a loop [0-{}]: \033[0m".format(len(loops)))
        choice = choice.strip()

        if choice == "0":
            return None

        try:
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(loops):
                return loops[choice_idx][0]
            else:
                print("\033[31mInvalid selection!\033[0m")
                return None
        except ValueError:
            print("\033[31mInvalid input!\033[0m")
            return None
    except (EOFError, KeyboardInterrupt):
        return None


def main():
    """Main entry point with loop selection menu"""
    loops = get_available_loops()

    if not loops:
        print("\033[31mError: No loop files found in 'code' directory!\033[0m")
        print("Please create s*-loop.py files in the code directory.")
        return

    selected_module = display_menu(loops)

    if selected_module is None:
        print("\nGoodbye!")
        return

    print(f"\n\033[33mLoading {selected_module}...\033[0m\n")

    try:
        loop_module = import_loop_module(selected_module)
        # Run the module's main function if it exists
        if hasattr(loop_module, "main"):
            loop_module.main()
        else:
            # Fallback: just execute the module
            # This will run the __main__ block in the loop file
            print(
                f"\033[33mNote: {selected_module} does not have a main() function.\033[0m"
            )
            print("You can run it directly with:")
            print(f"  python code/{selected_module}.py")
    except Exception as e:
        print(f"\033[31mError loading module: {e}\033[0m")


if __name__ == "__main__":
    main()
