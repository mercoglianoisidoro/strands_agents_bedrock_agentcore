"""
Simple Terminal Interface for AI Agent Communication
"""

import asyncio
import sys
from typing import Optional
from colorama import init, Fore, Style, Back
import io
from contextlib import redirect_stdout

try:
    from rich.console import Console
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Initialize colorama for cross-platform colors
init(autoreset=True)


class Terminal:
    """Minimal terminal interface for agent interaction"""

    def __init__(self, agent, use_markdown: bool = True, show_streaming: bool = True) -> None:
        self.agent = agent
        self.running = True
        self.use_markdown = use_markdown and RICH_AVAILABLE
        self.show_streaming = show_streaming
        if self.use_markdown:
            self.console = Console(width=None, legacy_windows=False)

    def print_user_input(self, user_input: str) -> None:
        """Print user input with styling"""
        print(f"{Fore.CYAN}{Style.BRIGHT}You: {Style.RESET_ALL}{Fore.CYAN}{user_input}{Style.RESET_ALL}")

    def print_agent_output(self, response: str) -> None:
        """Print agent response with styling"""
        if self.use_markdown:
            print(f"\n\n\n{Fore.RED}{Style.BRIGHT}Agent:{Style.RESET_ALL}\n")
            markdown = Markdown(response)
            self.console.print(markdown, justify="left")
            print("\n\n")
        else:
            print(f"\n\n\n{Fore.RED}{Style.BRIGHT}Agent: {Style.RESET_ALL}{Fore.RED}{response}{Style.RESET_ALL}\n\n")

    def get_input_prompt(self, is_first_line: bool) -> str:
        """Get styled input prompt"""
        if is_first_line:
            return f"{Fore.CYAN}{Style.BRIGHT}You: {Style.RESET_ALL}{Fore.CYAN}{Style.RESET_ALL}"
        else:
            return f"{Fore.CYAN}... {Style.RESET_ALL}"

    def display_welcome(self) -> None:
        """Display colorful welcome message with OS-specific instructions"""
        import platform
        
        # Determine OS-specific key names
        os_name = platform.system()
        if os_name == "Darwin":  # macOS
            newline_key = "⌥+Enter (Option+Enter)"
            exit_key = "⌘+D or Ctrl+C"
        elif os_name == "Windows":
            newline_key = "Alt+Enter"
            exit_key = "Ctrl+C or Ctrl+D"
        else:  # Linux and others
            newline_key = "Alt+Enter"
            exit_key = "Ctrl+C or Ctrl+D"
        
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}")
        print(f"{Fore.YELLOW}{Style.BRIGHT}🤖  AI AGENT TERMINAL SIMULATOR  🤖")
        print(f"{Fore.CYAN}{Style.BRIGHT}{'='*50}")
        print(f"{Fore.GREEN}Welcome! You can now chat with the AI agent.")
        print(f"{Fore.WHITE}• Type or paste your message and press Enter")
        print(f"{Fore.WHITE}• Press {newline_key} to add newlines")
        print(f"{Fore.WHITE}• Type 'exit' or 'quit' to end the session")
        print(f"{Fore.WHITE}• Press {exit_key} for graceful exit")
        print(f"{Fore.CYAN}{'-'*50}{Style.RESET_ALL}")

    async def process_input(self, user_input: str) -> str:
        """Send input to agent and get response.
        
        Args:
            user_input: The user's input message to send to the agent
            
        Returns:
            The agent's response as a string
            
        Note:
            Captures and styles streaming output in dim gray during execution.
            Returns error message if agent execution fails.
        """
        try:
            # Capture stdout to style the streamed output in dim gray.
            # Strands agents automatically stream their responses to stdout during execution
            # for real-time feedback. We capture it and display it in dim gray, then show
            # the final formatted response normally.
            captured_output = io.StringIO()

            if self.show_streaming:
                class GrayStdout:
                    def write(self, text):
                        if text.strip():  # Only colorize non-empty text
                            sys.__stdout__.write(f"{Fore.BLACK}{Style.DIM}{text}{Style.RESET_ALL}")
                        else:
                            sys.__stdout__.write(text)
                    def flush(self):
                        sys.__stdout__.flush()
                    def isatty(self):
                        return sys.__stdout__.isatty()
                    def fileno(self):
                        return sys.__stdout__.fileno()

                original_stdout = sys.stdout
                sys.stdout = GrayStdout()
                try:
                    response = self.agent(user_input)
                finally:
                    sys.stdout = original_stdout
            else:
                # Hide streaming output completely
                with redirect_stdout(captured_output):
                    response = self.agent(user_input)

            return str(response)
        except KeyboardInterrupt:
            raise  # Re-raise to allow graceful shutdown
        except Exception as e:
            import traceback
            error_msg = f"Agent execution error: {str(e)}"
            if hasattr(e, '__cause__') and e.__cause__:
                error_msg += f"\nCaused by: {str(e.__cause__)}"
            print(f"\n{Fore.RED}Error details:\n{traceback.format_exc()}{Style.RESET_ALL}")
            return error_msg

    async def get_user_input(self) -> str:
        """Get input from user with multiline support using prompt_toolkit.
        
        Returns:
            User input string, or 'exit'/'quit' for termination, or 'EMPTY_INPUT' if empty
            
        Note:
            Uses prompt_toolkit for proper paste handling and multi-line support.
            Press Alt+Enter to insert newlines within input.
        """
        from prompt_toolkit import PromptSession
        from prompt_toolkit.key_binding import KeyBindings
        
        try:
            # Create key bindings for multi-line input
            kb = KeyBindings()
            
            @kb.add('escape', 'enter')
            def _(event):
                """Alt+Enter to insert newline"""
                event.current_buffer.insert_text('\n')
            
            # Use prompt_toolkit which handles paste properly
            session = PromptSession()
            result = await session.prompt_async(
                "You: ",  # Plain text prompt for prompt_toolkit
                multiline=False,
                key_bindings=kb
            )
            
            # Check for exit commands
            if result.lower().strip() in ['exit', 'quit']:
                return result.lower().strip()
            
            return result if result.strip() else "EMPTY_INPUT"

        except (EOFError, KeyboardInterrupt):
            print(f"\n{Fore.RED}Interrupted. Exiting...{Style.RESET_ALL}")
            return "exit"

    async def execute_first_message(self, first_message: str) -> None:
        """Execute the first message if provided"""
        print(f"{Fore.CYAN}{Style.DIM}▶ Executing initial message...{Style.RESET_ALL}\n")
        self.print_user_input(first_message)
        response = await self.process_input(first_message)
        self.print_agent_output(response)

    async def start(self, first_message: Optional[str] = None) -> None:
        """Start the terminal session"""
        self.display_welcome()
        if first_message:
            await self.execute_first_message(first_message)

        try:
            while self.running:
                user_input = await self.get_user_input()

                if user_input.lower().strip() in ['exit', 'quit']:
                    print(f"{Fore.GREEN}{Style.BRIGHT}Goodbye! Thanks for using the AI Agent Terminal! 👋{Style.RESET_ALL}")
                    break

                # Handle different input types
                if user_input == "EMPTY_INPUT":
                    print(f"{Fore.YELLOW}Empty input. Please enter some text.{Style.RESET_ALL}\n")
                elif user_input.strip():
                    # Show what was received for multiline
                    if '\n' in user_input:
                        print(f"{Fore.CYAN}Processing multiline input...{Style.RESET_ALL}")

                    response = await self.process_input(user_input)
                    self.print_agent_output(response)
                else:
                    print(f"{Fore.YELLOW}Please enter some text.{Style.RESET_ALL}\n")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print(f"\n{Fore.GREEN}{Style.BRIGHT}Goodbye! Thanks for using the AI Agent Terminal! 👋{Style.RESET_ALL}")
        except Exception as e:
            print(f"\n{Fore.RED}Error occurred: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Exiting gracefully...{Style.RESET_ALL}")
        finally:
            self.running = False