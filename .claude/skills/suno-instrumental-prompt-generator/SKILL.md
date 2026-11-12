---
name: suno-instrumental-prompt-generator
description: Generate Suno AI prompts for instrumental music based on reference songs. Use when the user wants to create instrumental music on Suno and provides reference songs or artists to emulate. Researches reference tracks to extract genre, instrumentation, tempo, mood, and era details, then builds properly formatted Suno prompts following v3.5 constraints (200 character limit).
---

# Suno instrumental prompt generator

Generate professional Suno v3.5 prompts for instrumental music by researching reference songs and extracting their sonic characteristics. Optimized for the 200 character prompt limit.

## Workflow

### 1. Gather reference songs

Ask the user for 1-3 reference songs or artists. Get specific track names when possible, not just artists.

Example questions:
- "What songs should I use as reference for this instrumental?"
- "Can you give me 1-3 specific tracks that capture the vibe you're going for?"

### 2. Research each reference song

For each reference track, use web_search and web_fetch to find detailed information:

**Core attributes to extract:**
- **Genre/subgenre**: Be specific (e.g., "synthwave" not just "electronic")
- **Era/decade**: When released or what era it evokes
- **Key instruments**: 2-3 most defining instruments/sounds
- **Tempo**: BPM if available
- **Mood**: 1-2 emotional qualities (dark, uplifting, melancholic, ethereal)
- **Production style**: 1-2 defining production elements (lo-fi, reverb-heavy, crisp)

**Research strategy:**
1. Search for "[song name] [artist] genre instrumentation"
2. Look for music databases (AllMusic, Discogs), reviews, production notes
3. Search for "[song name] tempo BPM" for tempo details
4. If limited info, search for artist's signature sound

### 3. Synthesize keywords from research

Extract the MOST ESSENTIAL common threads across reference songs:
- Primary genre/subgenre (pick ONE most accurate)
- Top 2-3 instruments that define the sound
- Tempo range (pick one BPM or descriptor)
- Primary mood (pick ONE or TWO max)
- Key production element (pick ONE if space allows)

Prioritize keywords by importance:
1. Genre (always include)
2. Instrumentation (always include, 2-3 instruments max)
3. Tempo (include if defining characteristic)
4. Mood (include if space allows)
5. Production style (include only if space remains)

### 4. Build the Suno v3.5 prompt

**CRITICAL CONSTRAINT: 200 character maximum**

Construct an ultra-concise prompt using this priority order:

**Format:**
```
[genre], [tempo if critical], [instrument 1], [instrument 2], [instrument 3], [mood], instrumental
```

**Character budget breakdown:**
- Genre/style: 15-25 chars
- Instruments: 40-60 chars (2-3 instruments)
- Tempo: 0-15 chars (only if defining)
- Mood: 10-20 chars (1-2 words)
- "instrumental": 12 chars (ALWAYS include to prevent vocals)

**Optimization tactics:**
- Use abbreviations: "synth" not "synthesizer", "perc" not "percussion"
- Combine when possible: "808 bass" not "808 drums and bass"
- Drop articles: "analog synth" not "an analog synth"
- Use commas, not conjunctions: "dark, moody" not "dark and moody"
- Skip era markers unless critical to sound
- Always end with ", instrumental" to block vocals

**Example prompts (with character counts):**

```
synthwave, 110 BPM, analog synths, 808 bass, reverb drums, nostalgic, instrumental
[79 chars]

downtempo chillout, electric piano, soft percussion, warm bass, serene, instrumental
[86 chars]

progressive trance, 138 BPM, lush pads, rolling bassline, soaring leads, euphoric, instrumental
[96 chars]

dark techno, pounding kicks, distorted bass, metallic perc, industrial, instrumental
[84 chars]

lo-fi hip hop, dusty vinyl, mellow keys, subtle drums, jazzy, chill, instrumental
[80 chars]
```

### 5. Present the complete prompt

Provide the user with:
1. **Research summary** - 2-3 sentences on what you found
2. **Suno v3.5 prompt** - The 200-char optimized prompt with character count
3. **Alternative variations** - 1-2 variants emphasizing different aspects (all under 200 chars)
4. **Note about upgrade** - Mention that v4/v4.5 allows more sophisticated prompts with Custom Mode

## Output format

```
## Research summary

[2-3 sentence summary of reference songs' characteristics]

## Suno v3.5 prompt

**Main prompt** (XXX chars):
[Concise prompt under 200 characters]

**Alternative 1** (XXX chars):
[Variant with different emphasis]

**Alternative 2** (XXX chars):
[Another variant]

## Notes for v3.5

- Character count is critical—prompt MUST be under 200 chars
- Always include "instrumental" at end to prevent vocals
- [Any genre-specific tips or iteration suggestions]

## Upgrade path

When you move to Suno v4/v4.5, you'll be able to use Custom Mode with:
- Unlimited prompt length in Style field
- Structural meta tags in Lyrics field
- Exclude Styles field for vocal prevention
- Advanced controls (Style Influence, Weirdness, Audio Influence)
```

## Tips for v3.5 constraints

**Prioritization within 200 chars:**
1. Genre is non-negotiable (always include)
2. 2-3 key instruments define the sound (always include)
3. "instrumental" at end is mandatory (always include)
4. Tempo only if it's a defining characteristic
5. Mood only if character budget allows
6. Production details only if essential AND space remains

**When you have too many characters:**
- Drop least essential instrument
- Remove tempo unless critical (e.g., techno needs BPM)
- Shorten genre name ("synthwave" → "synth")
- Remove mood descriptors
- Use shorter instrument names ("keys" instead of "electric piano")

**When mixing multiple reference styles:**
- Pick the ONE most dominant genre
- Include instruments from both that don't conflict
- Use hybrid genre terms if accurate ("trip-hop", "electro-jazz")

**Genre-specific shortcuts:**
- Electronic: genre + BPM often sufficient with 2-3 synth types
- Acoustic: focus heavily on instruments, less on genre
- Orchestral: lead with "orchestral" + primary sections (strings, brass)
- Hip-hop: drums + bass + melodic element (keys, sample type)

## Common pitfalls to avoid

- **Forgetting "instrumental"**: Always include it or you'll get vocals
- **Over-describing**: "warm analog synthesizer pads with tape saturation" → "analog synth pads, warm"
- **Wasting characters on filler**: Avoid "featuring", "with a", "that has"
- **Going over 200 chars**: Count before finalizing
- **Being too vague**: "electronic music" doesn't work; "dark techno, 130 BPM" does
- **Listing too many instruments**: 2-3 max, pick the most defining ones
