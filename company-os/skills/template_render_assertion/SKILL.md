# Assert a template change on a real rendered image

## Turn the requirement into checks

- Write the requirement as pixel checks before you change code.

- List each element the change must show or hide.

- Name the exact colour, position, border, and background for each element.

- Keep a check for every element, so a passing render alone cannot hide a missing element.

## Render and assert before confirming

- Render the changed template through the real render path that ships the video.

- Write an automated test that reads pixels from that rendered image and asserts each check.

- Run the test after the change and keep the result with the change.

- Treat a render with no error as unproven, since a clean render can still miss a background or a border.

- Treat an eye check alone as unproven, since a faint background or a missing block can pass a quick look.

- Check preview separately when you also change preview code, and never use a preview result as proof for the shipped render.

- Fix the template or the test when a check fails, then rerun the full test set before you confirm anything.

## Report only what the test proved

- Report the test name, the number of checks, and the pass result alongside the version change.

- Name any requirement the test does not yet cover, instead of calling the change complete.

- Keep the test file with the template change, so a later change can rerun the same checks.

- Return to the template when a later review finds a requirement the test missed, and add a check for that requirement before you confirm again.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.

## Alternatives for better results

- Add a regression check for a template that shares the changed style, so a fix for one template does not break a neighbour.

- Keep the old rendered image beside the new one when you compare a visual change, and let the test decide the disputed pixels.
