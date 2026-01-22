# src/context_engine/main.py

"""Entry point for the Context Engineering Engine.

The engine receives raw user input (a string), parses it into a structured
`Command` object, runs the processing pipeline and returns the final output.
"""

from .commands import parse_command, Command
from .pipeline import (
    classify_request,
    validate_input,
    load_context,
    process_request,
    validate_output,
)


def handle_user_input(user_input: str) -> str:
    """Process a raw user input and return a formatted response.

    Steps:
    1. Parse the shortcut command.
    2. Classify the request type.
    3. Validate the raw data (e.g., anonymity checks).
    4. Load the appropriate resources (normativas, taxonomia, templates).
    5. Run the core processing logic.
    6. Validate the generated output.
    """
    # 1. Parse
    command: Command = parse_command(user_input)
    if command.error:
        return command.error_message

    # 2. Classification
    request_type = classify_request(command)

    # 3. Validation of input data
    validation_errors = validate_input(command)
    if validation_errors:
        return "\n".join(validation_errors)

    # 4. Load context/resources
    context = load_context(request_type)

    # 5. Core processing
    raw_output = process_request(command, context)

    # 6. Output validation
    output_errors = validate_output(raw_output)
    if output_errors:
        return "\n".join(output_errors)

    return raw_output


if __name__ == "__main__":
    # Simple REPL for manual testing
    while True:
        try:
            user_input = input("Enter command (or 'quit'): ")
            if user_input.lower() in {"quit", "exit"}:
                break
            print(handle_user_input(user_input))
        except KeyboardInterrupt:
            break
