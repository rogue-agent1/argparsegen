# argparsegen

Generate Python argparse CLI boilerplate from a JSON spec. Zero dependencies.

## Usage

```bash
argparsegen example > spec.json       # Generate example spec
argparsegen generate spec.json        # Print generated code
argparsegen generate spec.json -o cli.py  # Write to file
```

## Spec Format

```json
{
  "name": "mytool",
  "description": "My tool",
  "commands": {
    "run": {
      "description": "Run it",
      "args": [
        {"name": "input", "help": "Input file"},
        {"name": "--output", "short": "-o", "default": "out.txt"}
      ]
    }
  }
}
```

## Requirements

- Python 3.6+ (stdlib only)
