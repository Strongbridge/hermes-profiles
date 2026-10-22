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

1. **Understand the Policy Subject**: Identify the topic and scope of the new policy the user wants to create. Ask clarifying questions if necessary.
2. **Review the Template**: Fetch and review the reference template `Acceptable_Use_Policy_-_SB-AU-001.docx` using the `skills:get_skill_resources` tool.
3. **Draft the Policy**: Follow the exact structure of the template, which includes:
   - **Title**: Strongbridge [Topic] Policy
   - **Effective Date**: Set to a future or current date, or ask the user.
   - **Version History Table**: Date, Description (Initial version), Version (1.0), Author.
   - **Numbered Sections**: 
     - 1. Purpose
     - 2. Scope
     - [Topic-specific sections structured with bold subheadings]
     - Consequences of Violating the Policy
     - Acknowledgment of Policy
     - Policy Review and Updates
   - **Sign-off Block**: Approved By Name, Title, Date.
4. **Output**: Present the drafted policy in clean Markdown format for the user to review.

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