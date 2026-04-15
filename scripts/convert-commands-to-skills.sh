#!/usr/bin/env bash
#
# Convert .claude/commands/*.md files into portable skills/<name>/SKILL.md.
#
# Input:  .claude/commands/<name>.md — first line is the description,
#         remaining lines are the skill body. The legacy $ARGUMENTS token
#         is replaced with a more portable {{input}} marker.
# Output: skills/<name>/SKILL.md — YAML frontmatter (name, description)
#         followed by the body.
#
# This script is idempotent: running it again overwrites existing skills.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CMD_DIR="$REPO_ROOT/.claude/commands"
SKILL_DIR="$REPO_ROOT/skills"

if [[ ! -d "$CMD_DIR" ]]; then
    echo "error: commands directory not found at $CMD_DIR" >&2
    exit 1
fi

mkdir -p "$SKILL_DIR"

count=0
for cmd_file in "$CMD_DIR"/*.md; do
    [[ -e "$cmd_file" ]] || continue
    name="$(basename "$cmd_file" .md)"
    description="$(head -n 1 "$cmd_file")"
    body="$(tail -n +2 "$cmd_file")"

    # Strip leading blank lines from body.
    body="$(printf '%s' "$body" | sed '/./,$!d')"

    # Replace $ARGUMENTS with a portable placeholder.
    body="${body//\$ARGUMENTS/\{\{input\}\}}"

    target_dir="$SKILL_DIR/$name"
    mkdir -p "$target_dir"

    {
        printf -- '---\n'
        printf 'name: %s\n' "$name"
        printf 'description: %s\n' "$description"
        printf -- '---\n\n'
        printf '%s\n' "$body"
    } > "$target_dir/SKILL.md"

    count=$((count + 1))
    echo "  converted: $name"
done

echo ""
echo "Converted $count command(s) into skills at: $SKILL_DIR"
