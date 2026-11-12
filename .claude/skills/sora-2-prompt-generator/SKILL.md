---
name: sora-2-prompt-generator
description: Generate optimized video prompts for OpenAI's Sora 2 text-to-video model. Use when the user requests video generation prompts, wants to create video concepts, needs help describing shots for Sora, or asks for cinematography guidance. Covers prompt anatomy, visual cues, camera techniques, lighting, motion control, and dialogue integration based on official Sora 2 best practices.
---

# Sora 2 Prompt Generator

Generate effective video prompts for Sora 2 by treating each prompt like briefing a cinematographer. The model fills in missing details, so detailed prompts give control while lighter prompts enable creative freedom.

## Core Principle: Control vs Creativity

**Detailed prompts** = more control and consistency
**Lighter prompts** = creative freedom and surprising variations

The same prompt generates different results each time—this is intentional. Iterate and collaborate with the model.

## Choosing Your Approach

### Short Prompts (1-2 sentences)
Use when you want creative interpretation and are open to surprises.

**Structure:** Style + Subject/Setting + Action + Dialogue (optional)

Example:
> In a 90s documentary-style interview, an old Swedish man sits in a study and says, "I still remember when I was young."

**For more examples:** See `references/short-prompts.md`

### Detailed Prompts (structured sections)
Use when you need precise cinematography, specific look/feel, or controlled production values.

**Structure:**
- **Style:** Era/genre/format, visual texture, film characteristics
- **Cinematography:** Shot type, camera movement, lens, depth of field
- **Lighting:** Quality, direction, color temperature, sources
- **Mood:** Emotional tone, atmosphere
- **Actions:** Sequential beats with specific counts/timing
- **Dialogue:** Character lines (keep concise)
- **Background:** Ambient sound, environmental details

**For complete examples:** See `references/detailed-prompts.md`

## Writing Effective Prompts

### 1. Be specific, not generic

| Weak | Strong |
|------|--------|
| Beautiful street at night | Wet asphalt, zebra crosswalk, neon signs reflected in puddles |
| Person moves quickly | Cyclist pedals three times, brakes, stops |
| Brightly lit room | Soft window light with warm lamp fill, cool rim from hallway |

### 2. Anchor with style first
Style guides all other choices. Examples: "1970s film," "IMAX scene," "16mm B&W," "hand-painted animation."

### 3. Control motion with beats
Movement is hardest—keep it simple. One camera move + one subject action per shot.

**Structure actions as beats:**
- Actor takes four steps
- Pauses at window
- Pulls curtain

### 4. Name your colors
Specify 3-5 colors for palette consistency: "amber, cream, walnut, teal"

### 5. Light with direction and quality
Not "brightly lit" but "soft window light camera left, warm tungsten bounce, cool rim from hallway"

**For comprehensive cues:** See `references/visual-cues.md`

## Dialogue Integration

Place dialogue directly in the prompt, below visual description. Keep lines concise and natural.

**Single speaker:**
> Robot (quietly): "Almost lost it… but I got it!"

**Multiple speakers:**
> Detective: "You're lying. I can hear it in your silence."
> Suspect: "Or maybe I'm just tired of talking."
> Detective: "Either way, you'll talk before the night's over."

## API Parameters

Resolution, duration, and model MUST be set via API parameters—they cannot be requested in prose.

**Critical:** If user asks for "longer video" or "higher resolution," explain these require API parameter changes, not prompt changes.

**For full API details:** See `references/api-parameters.md`

### Quick reference:
- **model:** `sora-2` or `sora-2-pro`
- **size:** `1280x720`, `720x1280` (both models); `1024x1792`, `1792x1024` (pro only)
- **seconds:** `"4"`, `"8"`, `"12"` (shorter = more reliable)
- **input_reference:** Optional image for style control

## Workflow

1. **Understand user's vision** - What's the core idea? What style/mood?
2. **Choose detail level** - Creative freedom or precise control?
3. **If short prompt:** Style + subject + action + dialogue
4. **If detailed prompt:** Use structured template with all sections
5. **Specify API parameters separately** - Model, resolution, duration
6. **Iterate as needed** - Small tweaks can shift outcomes dramatically

## Common Patterns

**Documentary interview:**
> In a [era] documentary-style interview, [subject] [location] and says, "[dialogue]"

**Nature/wildlife:**
> [Animal] [action with beats] in [environment with specific details], [lighting/weather]

**Urban moment:**
> [Character] [action] through [specific location], [time of day], [environmental texture]

**Cinematic drama:**
Follow detailed template with full cinematography, lighting, and mood specifications

## Remixing Existing Videos

When user wants to modify an existing Sora result:
1. Pin the original video
2. Describe ONLY the change: "same shot, switch to 85mm lens" or "same shot, add orange monster in background"
3. Keep other details implicit—don't restate the entire prompt

## Key Reminders

- Shorter videos (4-8s) follow instructions more reliably
- One camera move and one subject action per shot
- Count/beat actions for timing: "takes four steps, pauses, turns"
- Style is the most powerful control lever
- Name specific colors, not moods ("amber" not "warm")
- Describe light by direction and quality
- The same prompt yields different results—iterate

## References

- `short-prompts.md` - Examples of minimal, creative prompts
- `detailed-prompts.md` - Examples of structured, cinematic prompts  
- `visual-cues.md` - Comprehensive guide to camera, lighting, and style techniques
- `api-parameters.md` - API parameter requirements and constraints
