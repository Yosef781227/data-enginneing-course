"""Generate Gemini CLI slash commands (.gemini/commands/*.toml) from .claude/commands/*.md.
Run again after editing a Claude command:  .venv/bin/python scripts/sync_gemini_commands.py"""
import json
import re
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
src, dst = LAB / ".claude" / "commands", LAB / ".gemini" / "commands"
dst.mkdir(parents=True, exist_ok=True)
for md in sorted(src.glob("*.md")):
    text = md.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    front, body = (m.group(1), text[m.end():]) if m else ("", text)
    desc = re.search(r"^description:\s*(.+)$", front, re.M)
    body = body.replace("$ARGUMENTS", "{{args}}").strip() + "\n"
    toml = f"description = {json.dumps(desc.group(1).strip() if desc else md.stem)}\n" \
           f'prompt = """\n{body.replace(chr(92), chr(92) * 2).replace(chr(34) * 3, chr(39) * 3)}"""\n'
    (dst / f"{md.stem}.toml").write_text(toml)
    print("wrote", dst.name + "/" + md.stem + ".toml")
