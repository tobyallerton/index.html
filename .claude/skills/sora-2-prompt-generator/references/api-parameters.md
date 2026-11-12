# Sora 2 API Parameters

These parameters control the video container and MUST be set explicitly in the API call. They cannot be requested in prose within the prompt.

## Required Parameters

### model
- Type: string
- Values: `sora-2` or `sora-2-pro`
- Description: Model version to use
  - `sora-2`: Standard model
  - `sora-2-pro`: Pro model with additional resolution options

### size
- Type: string
- Format: `{width}x{height}`
- Supported resolutions:
  - **sora-2**: `1280x720`, `720x1280`
  - **sora-2-pro**: `1280x720`, `720x1280`, `1024x1792`, `1792x1024`
- Description: Video resolution/aspect ratio

### seconds
- Type: string
- Values: `"4"`, `"8"`, `"12"`
- Default: `"4"`
- Description: Clip duration in seconds

## Optional Parameters

### input_reference
- Type: image file (JPEG, PNG, WEBP)
- Description: Reference image for style transfer or shot control
- Note: Image must match target resolution
- Use case: When user provides reference image or requests specific visual style

## Key Points

1. **These parameters define the video container** - resolution, duration, and model quality
2. **They will NOT change based on prose in the prompt** - phrases like "make it longer" or "higher resolution" have no effect
3. **Set them explicitly in the API call** - your prompt controls content (subject, motion, lighting, style)
4. **Resolution affects quality** - higher resolutions generate better detail, texture, and motion consistency
5. **Length affects reliability** - shorter clips (4-8s) follow instructions more reliably than longer clips

## When to Use Each Duration

- **4 seconds**: Best for single actions, simple motions, maximum instruction reliability
- **8 seconds**: Good for slightly more complex sequences, still reliable
- **12 seconds**: Use when user explicitly needs longer clips; may be less reliable
