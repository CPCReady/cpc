# Copyright (C) 2025 David CH.F (destroyer)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
CPCReady Interactive Console - Warp style
Using curses for fixed layout with scrollable output
"""

import curses
import subprocess
import shlex
import os
from collections import deque
from pathlib import Path
import click
from cpcready.utils.click_custom import CustomCommand


class WarpConsole:
    """Warp-style console with fixed prompt and scrollable output"""
    
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.output_lines = deque(maxlen=1000)
        self.command_history = []
        self.history_index = -1
        self.current_input = ""
        self.cursor_pos = 0
        self.scroll_offset = 0  # Offset for scrolling output
        
        # Initialize colors
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
        
        # Welcome message
        self.add_output("Welcome to CPCReady Interactive Console!", curses.color_pair(1) | curses.A_BOLD)
        self.add_output("Type 'help' for assistance, 'exit' to quit", curses.color_pair(5))
        self.add_output("Press F2 to view/copy all output as plain text", curses.color_pair(5))
        self.add_output("")
    
    def add_output(self, text, color=None):
        """Add line to output buffer"""
        if color is None:
            color = curses.color_pair(5)
        for line in text.split('\n'):
            self.output_lines.append((line, color))
        # Auto-scroll to bottom when new content is added
        self.scroll_offset = 0
    
    def draw_output_area(self, height, width):
        """Draw output area (top part) with scrollbar"""
        # Reserve last column for scrollbar
        content_width = width - 2
        
        # Clear output area
        for i in range(height - 3):
            self.stdscr.move(i, 0)
            self.stdscr.clrtoeol()
        
        # Draw border
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(height - 4, 0, "─" * width)
        self.stdscr.attroff(curses.color_pair(1))
        
        # Calculate visible area
        visible_lines = height - 4
        total_lines = len(self.output_lines)
        
        # Adjust scroll offset if needed
        max_scroll = max(0, total_lines - visible_lines)
        self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))
        
        # Calculate which lines to show
        end_index = total_lines - self.scroll_offset
        start_index = max(0, end_index - visible_lines)
        
        # Draw scroll indicator if not at bottom
        if self.scroll_offset > 0:
            scroll_info = f" ↑ {self.scroll_offset} more lines above "
            scroll_x = (content_width - len(scroll_info)) // 2
            self.stdscr.attron(curses.color_pair(4) | curses.A_REVERSE)
            try:
                self.stdscr.addstr(0, scroll_x, scroll_info)
            except curses.error:
                pass
            self.stdscr.attroff(curses.color_pair(4) | curses.A_REVERSE)
        
        # Draw output lines
        for i, idx in enumerate(range(start_index, end_index)):
            if i >= visible_lines:
                break
            line, color = self.output_lines[idx]
            try:
                # Truncate if too long
                if len(line) > content_width - 1:
                    line = line[:content_width - 4] + "..."
                self.stdscr.attron(color)
                self.stdscr.addstr(i, 0, line)
                self.stdscr.attroff(color)
            except curses.error:
                pass
        
        # Draw scrollbar on the right
        if total_lines > visible_lines:
            scrollbar_height = visible_lines
            scrollbar_x = width - 1
            
            # Calculate scrollbar position
            scroll_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
            thumb_position = int((scrollbar_height - 3) * (1 - scroll_ratio)) + 1  # Reserve space for arrows
            
            # Draw scroll up arrow at top
            try:
                self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                self.stdscr.addstr(0, scrollbar_x, "▲")
                self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
            
            # Draw scrollbar track and thumb
            self.stdscr.attron(curses.color_pair(1))
            for i in range(1, scrollbar_height - 1):
                try:
                    if i == thumb_position:
                        # Thumb (current position)
                        self.stdscr.attron(curses.color_pair(4) | curses.A_REVERSE)
                        self.stdscr.addstr(i, scrollbar_x, "█")
                        self.stdscr.attroff(curses.color_pair(4) | curses.A_REVERSE)
                    else:
                        # Track
                        self.stdscr.addstr(i, scrollbar_x, "│")
                except curses.error:
                    pass
            self.stdscr.attroff(curses.color_pair(1))
            
            # Draw scroll down arrow at bottom
            try:
                self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
                self.stdscr.addstr(scrollbar_height - 1, scrollbar_x, "▼")
                self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
            except curses.error:
                pass
    
    def draw_prompt_area(self, height, width):
        """Draw prompt area (bottom 3 lines)"""
        prompt_y = height - 3
        
        # Clear prompt area
        for i in range(3):
            self.stdscr.move(prompt_y + i, 0)
            self.stdscr.clrtoeol()
        
        # Get current directory
        current_dir = os.getcwd()
        home = os.path.expanduser("~")
        if current_dir.startswith(home):
            current_dir = "~" + current_dir[len(home):]
        
        # Draw prompt line 1: directory
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(prompt_y, 0, f"CPCReady {current_dir}")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        
        # Draw prompt line 2: input line
        self.stdscr.attron(curses.color_pair(4) | curses.A_BOLD)
        self.stdscr.addstr(prompt_y + 1, 0, "$ ")
        self.stdscr.attroff(curses.color_pair(4) | curses.A_BOLD)
        
        # Draw current input
        display_input = self.current_input
        if len(display_input) > width - 3:
            display_input = display_input[-(width - 6):] + "..."
        
        self.stdscr.attron(curses.color_pair(5))
        self.stdscr.addstr(prompt_y + 1, 2, display_input)
        self.stdscr.attroff(curses.color_pair(5))
    
    def execute_command(self, command_line):
        """Execute command and add output"""
        if not command_line.strip():
            return True
        
        # Add to history
        self.command_history.append(command_line)
        self.add_output(f"$ {command_line}", curses.color_pair(4) | curses.A_BOLD)
        
        try:
            parts = shlex.split(command_line)
        except ValueError as e:
            self.add_output(f"Error: {e}", curses.color_pair(3))
            return True
        
        if not parts:
            return True
        
        cmd = parts[0]
        
        # Exit command
        if cmd in ('exit', 'quit', 'q'):
            return False
        
        # Help command
        if cmd in ('help', '?'):
            self.show_help()
            return True
        
        # Clear command
        if cmd == 'clear':
            self.output_lines.clear()
            self.add_output("Output cleared", curses.color_pair(2))
            return True
        
        # Copy command
        if cmd == 'copy':
            try:
                # Get all output as plain text
                all_text = '\n'.join(line for line, _ in self.output_lines)
                
                # Try to copy to clipboard using pbcopy (macOS) or xclip (Linux)
                try:
                    subprocess.run(['pbcopy'], input=all_text.encode(), check=True)
                    self.add_output("✓ Output copied to clipboard (pbcopy)", curses.color_pair(2))
                except FileNotFoundError:
                    try:
                        subprocess.run(['xclip', '-selection', 'clipboard'], input=all_text.encode(), check=True)
                        self.add_output("✓ Output copied to clipboard (xclip)", curses.color_pair(2))
                    except FileNotFoundError:
                        # Fallback: save to temp file
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
                            f.write(all_text)
                            temp_path = f.name
                        self.add_output(f"Clipboard tool not found. Output saved to: {temp_path}", curses.color_pair(4))
                        self.add_output("You can manually copy from this file", curses.color_pair(4))
            except Exception as e:
                self.add_output(f"Error copying: {e}", curses.color_pair(3))
            return True
        
        # CD command
        if cmd == 'cd':
            if len(parts) > 1:
                try:
                    path = os.path.expanduser(parts[1])
                    os.chdir(path)
                    self.add_output(f"Changed to: {os.getcwd()}", curses.color_pair(2))
                except FileNotFoundError:
                    self.add_output(f"Directory not found: {parts[1]}", curses.color_pair(3))
                except Exception as e:
                    self.add_output(f"Error: {e}", curses.color_pair(3))
            else:
                os.chdir(os.path.expanduser("~"))
                self.add_output(f"Changed to: {os.getcwd()}", curses.color_pair(2))
            return True
        
        # CPC commands
        cpc_commands = ['save', 'cat', 'disc', 'drive', 'run', 'version', 'rvm', 
                       'emu', 'm4', 'list', 'era', 'user', 'ren', 'model', 'mode', 'filextr']
        
        if cmd in cpc_commands:
            # Execute CPC command
            try:
                result = subprocess.run(
                    ['cpc'] + parts,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.stdout:
                    for line in result.stdout.rstrip().split('\n'):
                        self.add_output(line, curses.color_pair(5))
                
                if result.stderr:
                    for line in result.stderr.rstrip().split('\n'):
                        self.add_output(line, curses.color_pair(3))
                
                if result.returncode != 0:
                    self.add_output(f"Command failed with exit code {result.returncode}", curses.color_pair(3))
            
            except subprocess.TimeoutExpired:
                self.add_output("Command timed out (30s limit)", curses.color_pair(3))
            except FileNotFoundError:
                self.add_output("Error: 'cpc' command not found", curses.color_pair(3))
            except Exception as e:
                self.add_output(f"Error: {e}", curses.color_pair(3))
            
            return True
        
        # System command
        try:
            result = subprocess.run(
                parts,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout:
                for line in result.stdout.rstrip().split('\n'):
                    self.add_output(line, curses.color_pair(5))
            
            if result.stderr:
                for line in result.stderr.rstrip().split('\n'):
                    self.add_output(line, curses.color_pair(3))
            
            if result.returncode != 0:
                self.add_output(f"Command failed with exit code {result.returncode}", curses.color_pair(3))
        
        except subprocess.TimeoutExpired:
            self.add_output("Command timed out (30s limit)", curses.color_pair(3))
        except FileNotFoundError:
            self.add_output(f"Command not found: {cmd}", curses.color_pair(3))
        except Exception as e:
            self.add_output(f"Error: {e}", curses.color_pair(3))
        
        return True
    
    def show_help(self):
        """Show help"""
        self.add_output("", curses.color_pair(5))
        self.add_output("CPCReady Interactive Console Help", curses.color_pair(1) | curses.A_BOLD)
        self.add_output("", curses.color_pair(5))
        self.add_output("CPC Commands:", curses.color_pair(4))
        self.add_output("  save, cat, disc, drive, run, version, rvm, emu, m4", curses.color_pair(5))
        self.add_output("  list, era, user, ren, model, mode, filextr", curses.color_pair(5))
        self.add_output("", curses.color_pair(5))
        self.add_output("System Commands:", curses.color_pair(4))
        self.add_output("  cd <dir>  - Change directory", curses.color_pair(5))
        self.add_output("  <cmd>     - Execute any system command", curses.color_pair(5))
        self.add_output("", curses.color_pair(5))
        self.add_output("Console Commands:", curses.color_pair(4))
        self.add_output("  help      - Show this help", curses.color_pair(5))
        self.add_output("  clear     - Clear output", curses.color_pair(5))
        self.add_output("  copy      - Copy all output to clipboard", curses.color_pair(5))
        self.add_output("  exit/quit - Exit console", curses.color_pair(5))
        self.add_output("", curses.color_pair(5))
        self.add_output("Keyboard Shortcuts:", curses.color_pair(4))
        self.add_output("  F2               - Show all output as plain text (for copying)", curses.color_pair(5))
        self.add_output("  PageUp/PageDown  - Scroll output (10 lines)", curses.color_pair(5))
        self.add_output("  Ctrl+Up/Down     - Scroll output (1 line)", curses.color_pair(5))
        self.add_output("  Mouse Wheel      - Scroll output (3 lines)", curses.color_pair(5))
        self.add_output("  Click Scrollbar  - Jump to position or scroll", curses.color_pair(5))
        self.add_output("  Up/Down          - Navigate command history", curses.color_pair(5))
        self.add_output("  Ctrl+C           - Cancel current input", curses.color_pair(5))
        self.add_output("  Ctrl+D           - Exit console", curses.color_pair(5))
        self.add_output("", curses.color_pair(5))
        self.add_output("Text Selection:", curses.color_pair(4))
        self.add_output("  Press F2 to exit curses and show plain text", curses.color_pair(5))
        self.add_output("  Select and copy text normally with your mouse", curses.color_pair(5))
        self.add_output("  Press ENTER to return to interactive mode", curses.color_pair(5))
        self.add_output("", curses.color_pair(5))
    
    def run(self):
        """Main loop"""
        self.stdscr.clear()
        curses.curs_set(1)  # Show cursor
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)  # Enable mouse
        
        running = True
        while running:
            height, width = self.stdscr.getmaxyx()
            
            # Draw screen
            self.draw_output_area(height, width)
            self.draw_prompt_area(height, width)
            
            # Position cursor
            cursor_x = min(2 + len(self.current_input), width - 1)
            self.stdscr.move(height - 2, cursor_x)
            
            # Refresh
            self.stdscr.refresh()
            
            # Get input
            try:
                key = self.stdscr.getch()
                
                # Enter key
                if key == 10 or key == curses.KEY_ENTER:
                    running = self.execute_command(self.current_input)
                    self.current_input = ""
                    self.cursor_pos = 0
                    self.history_index = -1
                
                # Backspace
                elif key == curses.KEY_BACKSPACE or key == 127 or key == 8:
                    if self.current_input:
                        self.current_input = self.current_input[:-1]
                
                # Page Up - scroll up (10 lines)
                elif key == curses.KEY_PPAGE:
                    self.scroll_offset = min(self.scroll_offset + 10, len(self.output_lines))
                
                # Page Down - scroll down (10 lines)
                elif key == curses.KEY_NPAGE:
                    self.scroll_offset = max(self.scroll_offset - 10, 0)
                
                # Ctrl+Up - scroll up (1 line)
                elif key == 566:  # Ctrl+Up in curses
                    self.scroll_offset = min(self.scroll_offset + 1, len(self.output_lines))
                
                # Ctrl+Down - scroll down (1 line)
                elif key == 525:  # Ctrl+Down in curses
                    self.scroll_offset = max(self.scroll_offset - 1, 0)
                
                # Up arrow - history (only if not scrolling)
                elif key == curses.KEY_UP:
                    if self.command_history and self.scroll_offset == 0:
                        if self.history_index == -1:
                            self.history_index = len(self.command_history) - 1
                        elif self.history_index > 0:
                            self.history_index -= 1
                        
                        if 0 <= self.history_index < len(self.command_history):
                            self.current_input = self.command_history[self.history_index]
                    else:
                        # Scroll up if we're already scrolling
                        self.scroll_offset = min(self.scroll_offset + 1, len(self.output_lines))
                
                # Down arrow - history (only if not scrolling)
                elif key == curses.KEY_DOWN:
                    if self.scroll_offset == 0:
                        if self.history_index != -1:
                            self.history_index += 1
                            if self.history_index >= len(self.command_history):
                                self.history_index = -1
                                self.current_input = ""
                            else:
                                self.current_input = self.command_history[self.history_index]
                    else:
                        # Scroll down if we're scrolling
                        self.scroll_offset = max(self.scroll_offset - 1, 0)
                
                # Ctrl+C
                elif key == 3:
                    self.current_input = ""
                    self.add_output("^C", curses.color_pair(4))
                
                # Ctrl+D
                elif key == 4:
                    running = False
                
                # F2 - Toggle selection mode
                elif key == curses.KEY_F2:
                    # Exit curses temporarily to show plain text
                    curses.endwin()
                    
                    # Show all output as plain text
                    print("\n" + "="*70)
                    print("TEXT SELECTION MODE - All output displayed below")
                    print("Select and copy text with your mouse as usual")
                    print("="*70 + "\n")
                    
                    for line, _ in self.output_lines:
                        print(line)
                    
                    print("\n" + "="*70)
                    print("Press ENTER to return to interactive mode...")
                    print("="*70)
                    
                    # Wait for user
                    input()
                    
                    # Reinitialize curses
                    self.stdscr.clear()
                    self.stdscr.refresh()
                    
                    self.add_output("", curses.color_pair(5))
                    self.add_output("Returned to interactive mode", curses.color_pair(1))
                    self.add_output("", curses.color_pair(5))
                
                # Mouse event
                elif key == curses.KEY_MOUSE:
                    try:
                        _, mx, my, _, bstate = curses.getmouse()
                        visible_lines = height - 4
                        
                        # Check if click is on scroll up arrow
                        if mx == width - 1 and my == 0:
                            self.scroll_offset = min(self.scroll_offset + 1, len(self.output_lines))
                        
                        # Check if click is on scroll down arrow
                        elif mx == width - 1 and my == visible_lines - 1:
                            self.scroll_offset = max(self.scroll_offset - 1, 0)
                        
                        # Check if click is in scrollbar area (middle part)
                        elif mx == width - 1 and 0 < my < visible_lines - 1:
                            total_lines = len(self.output_lines)
                            if total_lines > visible_lines:
                                # Calculate scroll position from mouse Y (accounting for arrows)
                                scroll_ratio = 1 - ((my - 1) / (visible_lines - 2))
                                max_scroll = total_lines - visible_lines
                                self.scroll_offset = int(scroll_ratio * max_scroll)
                        
                        # Mouse wheel events (platform-independent check)
                        # On macOS/Linux, scroll wheel may use different button codes
                        elif bstate & getattr(curses, 'BUTTON4_PRESSED', 0x80000):  # Scroll up
                            self.scroll_offset = min(self.scroll_offset + 3, len(self.output_lines))
                        elif bstate & getattr(curses, 'BUTTON5_PRESSED', 0x8000000):  # Scroll down
                            self.scroll_offset = max(self.scroll_offset - 3, 0)
                    
                    except curses.error:
                        pass
                
                # Regular character
                elif 32 <= key <= 126:
                    self.current_input += chr(key)
            
            except KeyboardInterrupt:
                running = False


def main_curses(stdscr):
    """Curses main function"""
    console = WarpConsole(stdscr)
    console.run()


@click.command(cls=CustomCommand)
def interactive():
    """
    Interactive console with Warp-style layout
    
    Features:
    - Fixed prompt at bottom
    - Scrollable output area at top
    - Command history with Up/Down arrows
    - Native curses implementation
    """
    try:
        curses.wrapper(main_curses)
    except KeyboardInterrupt:
        pass
    print("\nGoodbye! 👋")


if __name__ == "__main__":
    interactive()
