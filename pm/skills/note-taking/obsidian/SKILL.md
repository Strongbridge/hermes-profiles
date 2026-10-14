---
name: obsidian
description: Read, search, create, and edit notes in the Obsidian vault.
version: 1.0.0
author: Teknium (teknium1), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, Notes, Markdown, Vault]
    related_skills: []
---

# Obsidian Vault

Use this skill for filesystem-first Obsidian vault work: reading notes, listing notes, searching note files, creating notes, appending content, and adding wikilinks.

## Vault path

Use a known or resolved vault path before calling file tools.

The documented vault-path convention is the `OBSIDIAN_VAULT_PATH` environment variable, for example from `${HERMES_HOME:-~/.hermes}/.env`. If it is unset, use `~/Documents/Obsidian Vault`.

File tools do not expand shell variables. Do not pass paths containing `$OBSIDIAN_VAULT_PATH` to `read_file`, `write_file`, `patch`, or `search_files`; resolve the vault path first and pass a concrete absolute path. Vault paths may contain spaces, which is another reason to prefer file tools over shell commands.

If the vault path is unknown, `terminal` is acceptable for resolving `OBSIDIAN_VAULT_PATH` or checking whether the fallback path exists. Once the path is known, switch back to file tools.

## Read a note

Use `read_file` with the resolved absolute path to the note. Prefer this over `cat` because it provides line numbers and pagination.

## List notes

Use `search_files` with `target: "files"` and the resolved vault path. Prefer this over `find` or `ls`.

- To list all markdown notes, use `pattern: "*.md"` under the vault path.
- To list a subfolder, search under that subfolder's absolute path.

## Search

Use `search_files` for both filename and content searches. Prefer this over `grep`, `find`, or `ls`.

- For filenames, use `search_files` with `target: "files"` and a filename `pattern`.
- For note contents, use `search_files` with `target: "content"`, the content regex as `pattern`, and `file_glob: "*.md"` when you want to restrict matches to markdown notes.

## Create a note

Use `write_file` with the resolved absolute path and the full markdown content. Prefer this over shell heredocs or `echo` because it avoids shell quoting issues and returns structured results.

## Filing a new project into the vault

Use this when a new project record must be captured in the CLIN9 vault (e.g., a new O&M project under a Power Platform system owner). The vault is the source of truth; the dashboard is a downstream sync when credentials are present.

### Procedure

1. **Resolve the vault root.** New project notes live in `SB-Hermes/` under the Obsidian root. Parent folders (e.g., `FRA-DevOps-CLIN9/`) are NOT visible in Obsidian.
2. **Check for an existing record.** Search the vault content for the project owner/system/app name before creating. Do not create a duplicate for the same project.
3. **Create the note** with `write_file` at `SB-Hermes/<Project Name>.md`, using the established field block: `Category`, `Not CLIN9`, `System owner`, `Scope`, `Primary tracking`, `Last updated`.
4. **Record the project in the status report.** Append a row to the Section 1 table of `FRADevOps - Project Status Report.md` using the format `||| <Title> | <Status> | <Last Modified> |`.
5. **Push to the dashboard** when `GOOGLE_APPLICATION_CREDENTIALS` is set; otherwise the vault record stands.

### Pitfalls
- **File under `SB-Hermes/`, not the vault root parent.** Project notes in parent folders are invisible to Obsidian.
- **Search before creating** to avoid a duplicate record for the same project.

## Append to a note

Prefer a native file-tool workflow when it is not awkward:

- Read the target note with `read_file`.
- Use `patch` for an anchored append when there is stable context, such as adding a section after an existing heading or appending before a known trailing block.
- Use `write_file` when rewriting the whole note is clearer than constructing a fragile patch.

For an anchored append with `patch`, replace the anchor with the anchor plus the new content.

For a simple append with no stable context, `terminal` is acceptable if it is the clearest safe option.

## Targeted edits

Use `patch` for focused note changes when the current content gives you stable context. Prefer this over shell text rewriting.

## Wikilinks

Obsidian links notes with `[[Note Name]]` syntax. When creating notes, use these to link related content.
