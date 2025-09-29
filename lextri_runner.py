import sys
import re
from typing import List
from rich.console import Console


def validate_arguments(args: List[str]) -> List[str]:
    """Validate and sanitize command-line arguments for security.
    
    Args:
        args: Raw command-line arguments
        
    Returns:
        List of validated and sanitized arguments
        
    Raises:
        ValueError: If arguments contain potentially dangerous patterns
    """
    validated_args = []
    
    # Define patterns that could be dangerous
    dangerous_patterns = [
        r'[;&|`$(){}\[\]<>]',  # Shell metacharacters
        r'\.\./',              # Path traversal
        r'^-',                 # Suspicious flags
    ]
    
    for arg in args:
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, arg):
                raise ValueError(f"Potentially dangerous argument detected: {arg}")
        
        # Sanitize: limit length and allowed characters
        if len(arg) > 100:
            raise ValueError(f"Argument too long: {arg[:20]}...")
            
        # Allow only alphanumeric, hyphens, underscores, and dots
        if not re.match(r'^[a-zA-Z0-9._-]+$', arg):
            raise ValueError(f"Invalid characters in argument: {arg}")
            
        validated_args.append(arg)
    
    return validated_args


def main() -> None:
    """Entry point for the LEX TRI runner.

    This function prints a simple header and reports whether any command‑line arguments were supplied.  In a full implementation,
    you would augment this script to gather tri‑temporal traces and produce diagnostic reports or guarded fixes.
    """
    console = Console()
    console.rule("[bold green]LEX TRI — Temporal Agent")
    console.print("Mode: Diagnostics")
    console.print("Analyzing VT/TT/DT traces...")
    
    if len(sys.argv) == 1:
        console.print("No anomalies found.")
    else:
        try:
            # Validate arguments for security
            raw_args = sys.argv[1:]
            validated_args = validate_arguments(raw_args)
            console.print(f"Validated args: {validated_args}")
        except ValueError as e:
            console.print(f"[red]Security error: {e}[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            sys.exit(1)


if __name__ == "__main__":
    main()