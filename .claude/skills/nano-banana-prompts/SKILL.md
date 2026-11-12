---
name: nano-banana-prompts
description: Generate optimized image prompts for Nano Banana (Gemini 2.5 Flash Image). Use when the user requests image generation with Gemini/Nano Banana, needs help crafting image prompts for conversational AI image generation, or asks for guidance on Gemini image creation. Covers narrative prompting, photorealistic scenes, stylized illustrations, editing workflows, and model-specific constraints.
---

# Nano Banana Image Prompting

Generate high-quality prompts for Nano Banana (Gemini 2.5 Flash Image)—Google's conversational image generation model.

## Core Principles

**Describe scenes, don't list keywords.** Use narrative, descriptive sentences. The model understands context and intent better than keyword lists.

**Be specific and explicit.** Detail subject, environment, style, lighting, and mood. Specificity = control.

**Iterate and refine.** Multi-turn refinement is expected. Request targeted tweaks: "Change lighting to warmer," "Make the character more serious."

**State purpose and context.** Example: "Create a logo for a minimalist skincare brand." Intent steers creative output.

**Use photographic and artistic terminology.** Mention camera angle, lens type, color schemes, art style ("in watercolor," "as an anime character").

**Semantic positives over negatives.** Describe what you want ("deserted city street at dawn") rather than what you don't ("no cars").

## Prompt Templates

### Photorealistic Scenes

```
A photorealistic [shot type] of [subject], [action/expression], set in [environment]. Illuminated by [lighting], creating a [mood] atmosphere. Captured with [camera/lens details], emphasizing [texture/detail]. [Aspect ratio/orientation].
```

**Example:**
> A photorealistic close-up portrait of an elderly Japanese ceramicist, inspecting a freshly glazed tea bowl, set in a rustic workshop with soft golden hour light, captured on an 85mm lens for blurred background. The mood is serene and masterful.

### Stylized Illustrations & Stickers

```
A [style] sticker of a [subject], featuring [key characteristics] and [color palette]. [Line style/shading]. Transparent background.
```

**Example:**
> A kawaii-style sticker of a happy red panda, with bold outlines and pastel pink accents. Transparent background.

### Text-Heavy Images (Logos, Posters)

```
Create a [image type] for [brand/concept] with the text "[your text]" in a [font style]. The design should be [style], in a [color scheme].
```

**Example:**
> Create a minimalist logo for "The Daily Grind" with clean, modern sans-serif text and earth tone palette.

### Product Mockups

```
A high-resolution, studio-lit photograph of [product] on [surface/background]. [Lighting setup], [camera angle]. Focus on [feature/detail]. [Aspect ratio].
```

**Example:**
> A high-resolution photo of a matte black ceramic mug on a marble countertop, lit with a softbox, shot from a low angle to show its handle detail, 4:5 aspect.

### Minimalist Compositions

```
A minimalist composition with a single [subject] in the [frame location]. Background is [color]. Soft, subtle lighting. [Aspect ratio].
```

**Example:**
> A single red maple leaf in the bottom right on a white background, soft shadows, landscape format.

## Editing & Multi-Image Workflows

Nano Banana excels at conversational editing. Use these patterns:

**Local edits:**
> Using the provided image of my cat, add a small wizard hat that fits the lighting and pose.

**Inpainting:**
> Change only the blue sofa to vintage brown leather; keep everything else identical.

**Style transfer:**
> Transform the photo into impressionist style, keep the composition.

**Compositional blend:**
> Combine the subject from image 1 with the background of image 2. Scene: a toy robot in a child's bedroom.

**Multi-turn refinement:**
- Make one change at a time
- Re-upload edited image for further tweaks
- For likeness preservation: specify "maintain facial features" or "keep logo unchanged"

## Model-Specific Constraints

**Text rendering:**
- Limit overlaid text to under 25 characters for accuracy
- Shorter text = more reliable rendering

**Aspect ratios:**
- Most reliable: 1:1, standard portrait/landscape
- Specify if needed (16:9, 4:5, etc.) but expect best results with common ratios

**Editing scope:**
- Adjust one element per prompt for best results
- Avoid editing too many aspects simultaneously

## Common Pitfalls

**Vague prompts:** "Make it better" results in unpredictable output. Be specific.

**Keyword stuffing:** Flowing descriptive text > bullet lists.

**Over-editing:** Best to adjust one element per prompt iteration.

## Example Workflow

**Initial prompt:**
> A photorealistic medium shot of a vintage 1960s Mustang in cherry red, parked on a coastal highway at sunset, dramatic side lighting casting long shadows. Shot on 35mm film with slight grain, emphasizing the chrome details and curves.

**Refinement 1:**
> Make the sunset more vibrant with deeper oranges and purples.

**Refinement 2:**
> Add a surfer with a board walking past the car in the background, slightly out of focus.

## Advanced Example

> Create a 1/7 scale commercialized figure of the character from the provided illustration, realistic style, placed on a computer desk with a circular transparent acrylic base. On the desk's monitor, display a screenshot of the ZBrush modeling software showing the figure. Next to the monitor, include a Bandai-style toy box with the original artwork.

---

**Key takeaway:** Clear narrative descriptions + specific constraints + iterative refinement = consistently excellent results.
