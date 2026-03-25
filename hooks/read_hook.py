import json
import sys


def main() -> None:
    try:
        # Read the full content from standard input
        input_data = sys.stdin.read()

        if not input_data:
            return

        # Parse the JSON tool call data
        tool_args = json.loads(input_data)

        # Extract the file path (mirroring your JS logic)
        tool_input = tool_args.get("tool_input", {})
        read_path = tool_input.get("file_path") or tool_input.get("path") or ""

        # Check if the .env file is being targeted
        if ".env" in read_path:
            print("You cannot read the .env file", file=sys.stderr)
            sys.exit(2)

    except json.JSONDecodeError:
        # Optional: handle cases where stdin isn't valid JSON
        print("Invalid input format", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
