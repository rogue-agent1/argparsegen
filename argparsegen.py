#!/usr/bin/env python3
"""argparsegen - Generate argparse boilerplate from a spec. Zero deps."""
import sys, json, os

def generate_from_spec(spec):
    name = spec.get("name", "cli")
    desc = spec.get("description", "")
    commands = spec.get("commands", {})
    global_args = spec.get("args", [])
    
    lines = [
        "#!/usr/bin/env python3",
        f'"""Generated CLI: {name}"""',
        "import argparse, sys",
        "",
        "def main():",
        f'    parser = argparse.ArgumentParser(description="{desc}")',
    ]
    
    # Global args
    for arg in global_args:
        lines.append(f"    {_gen_arg(arg)}")
    
    if commands:
        lines.append('    sub = parser.add_subparsers(dest="command", required=True)')
        lines.append("")
        
        for cmd_name, cmd_spec in commands.items():
            cmd_desc = cmd_spec.get("description", "")
            lines.append(f'    p_{cmd_name} = sub.add_parser("{cmd_name}", help="{cmd_desc}")')
            for arg in cmd_spec.get("args", []):
                lines.append(f"    {_gen_arg(arg, f'p_{cmd_name}')}")
            lines.append("")
    
    lines.append("    args = parser.parse_args()")
    lines.append("")
    
    if commands:
        for i, cmd_name in enumerate(commands):
            prefix = "if" if i == 0 else "elif"
            lines.append(f'    {prefix} args.command == "{cmd_name}":')
            lines.append(f'        print(f"Running {cmd_name} with {{args}}")')
            lines.append(f"        # TODO: implement {cmd_name}")
    
    lines.extend(["", 'if __name__ == "__main__":', "    main()", ""])
    return "\n".join(lines)

def _gen_arg(arg, parser="parser"):
    name = arg["name"]
    typ = arg.get("type", "str")
    help_text = arg.get("help", "")
    default = arg.get("default")
    required = arg.get("required", False)
    action = arg.get("action")
    choices = arg.get("choices")
    
    if name.startswith("-"):
        parts = [f'"{name}"']
        if arg.get("short"): parts.append(f'"{arg["short"]}"')
    else:
        parts = [f'"{name}"']
    
    if action:
        parts.append(f'action="{action}"')
    elif typ != "str":
        parts.append(f"type={typ}")
    
    if default is not None: parts.append(f"default={repr(default)}")
    if help_text: parts.append(f'help="{help_text}"')
    if required and name.startswith("-"): parts.append("required=True")
    if choices: parts.append(f"choices={choices}")
    
    return f"{parser}.add_argument({', '.join(parts)})"

def cmd_generate(args):
    if not args:
        print("Usage: argparsegen generate <spec.json>")
        print("       argparsegen generate --interactive")
        sys.exit(1)
    
    if args[0] == "--interactive":
        spec = interactive_build()
    else:
        with open(args[0]) as f:
            spec = json.load(f)
    
    code = generate_from_spec(spec)
    
    out = None
    for i, a in enumerate(args):
        if a in ("-o","--output") and i+1 < len(args):
            out = args[i+1]
    
    if out:
        with open(out, "w") as f: f.write(code)
        os.chmod(out, 0o755)
        print(f"✅ Generated {out}")
    else:
        print(code)

def interactive_build():
    print("🔧 Interactive CLI builder\n")
    name = input("CLI name: ").strip() or "cli"
    desc = input("Description: ").strip()
    
    spec = {"name": name, "description": desc, "commands": {}, "args": []}
    
    while True:
        cmd = input("\nAdd command (empty to finish): ").strip()
        if not cmd: break
        cmd_desc = input(f"  {cmd} description: ").strip()
        cmd_args = []
        while True:
            arg = input(f"  Add arg to {cmd} (empty to finish): ").strip()
            if not arg: break
            arg_help = input(f"    {arg} help: ").strip()
            cmd_args.append({"name": arg, "help": arg_help})
        spec["commands"][cmd] = {"description": cmd_desc, "args": cmd_args}
    
    return spec

def cmd_example(args):
    """Print an example spec."""
    example = {
        "name": "mytool",
        "description": "My awesome tool",
        "args": [
            {"name": "--verbose", "short": "-v", "action": "store_true", "help": "Enable verbose output"}
        ],
        "commands": {
            "run": {
                "description": "Run the tool",
                "args": [
                    {"name": "input", "help": "Input file"},
                    {"name": "--output", "short": "-o", "help": "Output file", "default": "out.txt"}
                ]
            },
            "config": {
                "description": "Show configuration",
                "args": [
                    {"name": "--format", "choices": "['json','yaml','toml']", "default": "json", "help": "Output format"}
                ]
            }
        }
    }
    print(json.dumps(example, indent=2))

CMDS = {"generate": cmd_generate, "gen": cmd_generate, "example": cmd_example}

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h","--help"):
        print("argparsegen - Generate argparse boilerplate from spec")
        print("Commands: generate <spec.json> [-o output.py], example")
        sys.exit(0)
    cmd = args[0]
    if cmd not in CMDS: print(f"Unknown: {cmd}"); sys.exit(1)
    CMDS[cmd](args[1:])
