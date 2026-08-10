import sys
import os
import argparse
from dotenv import load_dotenv

# Add src folder to sys.path to allow absolute imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from cli_agent.crew import CLIAgentCrew
from cli_agent.utils import CLIFormatter
from cli_agent.ui import run_tui

def run_cli():
    # Load environment variables
    load_dotenv()
    
    # Check if OLLAMA API key is set
    if not os.getenv("OLLAMA_API_KEY"):
        CLIFormatter.print_error(
            "OLLAMA_API_KEY was not found in your environment.\n"
            "Please configure your .env file or export the API key before running the CLI agent."
        )
        return

    parser = argparse.ArgumentParser(description="AI Command Line Agent Interface")
    parser.add_argument("--classic", action="store_true", help="Launch classic console input loop instead of TUI")
    args, unknown = parser.parse_known_args()

    if not args.classic:
        # Launch modern full-screen TUI
        run_tui()
        return

    # Print welcome screen for classic mode
    CLIFormatter.print_welcome()
    
    # Initialize the Crew
    try:
        agent_crew = CLIAgentCrew()
    except Exception as e:
        CLIFormatter.print_error(f"Failed to initialize CrewAI Agent system: {str(e)}")
        return

    # CLI Loop
    while True:
        try:
            # Get user input
            user_request = input("\nUser command > ").strip()
            
            if not user_request:
                continue
                
            if user_request.lower() in ["exit", "quit", "q"]:
                CLIFormatter.print_info("Exiting CLI Agent. Goodbye!")
                break
                
            CLIFormatter.print_info(f"Analyzing and processing task: '{user_request}'...")
            
            # Kickoff the CrewAI agents
            result = agent_crew.crew().kickoff(inputs={"user_request": user_request})
            
            # Extract outputs from tasks
            routing_out = ""
            execution_out = ""
            
            if hasattr(result, "tasks_output") and len(result.tasks_output) >= 2:
                routing_out = result.tasks_output[0].raw
                execution_out = result.tasks_output[1].raw
            else:
                execution_out = result.raw if hasattr(result, "raw") else str(result)
                routing_out = "Direct routing completed."
            
            # Format and present to the user via the output layer
            CLIFormatter.print_routing(routing_out)
            CLIFormatter.print_execution(execution_out)
            CLIFormatter.print_result_summary(result)
            
        except KeyboardInterrupt:
            console_msg = "\nExiting CLI Agent. Goodbye!"
            print(console_msg)
            break
        except Exception as e:
            CLIFormatter.print_error(f"An unexpected error occurred during execution: {str(e)}")

if __name__ == "__main__":
    run_cli()

