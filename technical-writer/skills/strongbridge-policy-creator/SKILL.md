---
name: strongbridge-policy-creator
description: Create Strongbridge policies using the standard template format. Use when the user asks to draft, create, or write a new policy for Strongbridge.
---
# Strongbridge Policy Creator

This skill drafts new Strongbridge policies based on the standard organizational template.

## When to Use

Use this skill when the user asks to:
- Draft a new policy for Strongbridge
- Create a policy document following Strongbridge formatting
- Write an organizational policy

## Steps

1. **Research and Contextualize**: Before drafting, search the Obsidian vault for relevant research or existing policy requirements (`SB-Hermes/` directory). 
2. **Understand the Policy Subject**: Identify the topic and scope. Ask clarifying questions if necessary.
3. **Review the Template**: Reference `Acceptable_Use_Policy_-_SB-AU-001.docx` for structural consistency.
4. **Draft the Policy**: Use the standard template structure:
   - Title
   - Effective Date
   - Version History Table
   - Numbered Sections (1. Purpose, 2. Scope, [Topic-specific], Consequences, Acknowledgment, Review and Updates)
   - Sign-off Block
5. **Save and Distribute**: Save the finalized Markdown file directly to the Obsidian vault at `/documentation/policies/`. Post a summary and request for approval in #clin9-documentation tagging the relevant stakeholders.
6. **Support Multiple Formats**: When requested, convert the markdown draft to a `.docx` document using the `docx` skill tools to ensure compatibility with client review processes.

## Reviewing and rewriting an existing policy

When asked to review or improve a policy that already exists, treat the
source as authoritative where readable, and use the standard template as
the fallback.

1. **Retrieve the source.** Open the source `.docx` (or wherever the
   policy was delivered) and read it. If it is inaccessible (e.g. an
   attachment returns HTTP 403, or the file is missing from the vault),
   do **not** guess or fill in its contents.
2. **Extract what is readable.** Capture title, change history, section
   headings, the sign-off block, and any stated obligations. Record which
   parts were readable and which were missing.
3. **Reconstruct from the standard template.** Build the rewritten policy
   using the `strongbridge-policy-creator` template structure: Title;
   Effective Date; Version History table; numbered sections 1. Purpose
   .. 10. Review and Updates; Consequences of Violating the Policy;
   Acknowledgment of Policy; Sign-off block.
4. **Reconcile with approved controls.** Where this guidance is more
   specific than the existing policy (for example, the engagement's
   documented authentication posture), state it explicitly and mark it
   as superseding the older policy for its scope.
5. **Flag the source note.** State clearly that the source document was
   unreadable or was reconstructed, so reviewers can treat the
   reconstruction as needing confirmation.
6. **Save and distribute.** Save the working draft to the shared Obsidian
   vault and present it for sign-off; never leave finalized text stranded
   in a Slack thread.

### Pitfalls
- Do not silently confirm the original policy's content when the source
  was unreadable; state the reconstruction explicitly.
- Keep the version-history and sign-off block identical in shape to the
  template — reviewers check those first.

## Gotchas

- Do not hallucinate company-specific legal jargon; keep the policy language clear, professional, and standard for corporate policies unless the user provides specific clauses.
- Ensure the formatting precisely matches the provided Strongbridge template, especially the version history table and approval block.