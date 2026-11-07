# Recreating an idea without copying it

## What to keep vs. change

| Keep (the idea) | Change (the look) |
|---|---|
| Hook angle (POV, problem, gift, dupe, "things I wish I knew") | Exact words: rewrite every line |
| Slide count, ±1, and what each slide does | The person: age, ethnicity, hair, clothes, body type, or show just hands |
| Selling angle / main benefit | Setting: bathroom → bedroom vanity, kitchen → car, and so on |
| Overall vibe (cosy, clean girl, chaotic, luxe) | Props, colour palette, time of day, lighting |
| Product: **identical** | Camera angle, crop, flat lay vs. in hand vs. in use |

Change at least two things in the right column on every slide, and always rewrite the text. A good test: if the original creator saw yours, they'd recognise the *format* but not their own post.

## The product lock
The product is the one thing that must not drift. Every prompt with the product in it should:
- attach the clean product photo as a reference,
- say plainly that the product must match the reference exactly, and name the details that tend to drift: shape, cap/pump/lid, colours, label layout, logo, text on the pack, material (matte/gloss/frosted), and realistic size,
- avoid asking the model to "redesign", "stylise" or "reimagine" the product,
- keep the product large enough in frame to check (around ≥15% of the image on product slides).

## Prompt template (one per slide)

```
Using the attached product photo as an exact reference, create a vertical 2:3 portrait photo.

Scene: <who, doing what, where>. <lighting, time of day>. <props>.
Product: the <product name> from the reference image, <how it appears: held in left hand / on the shelf / being applied>. It must look identical to the reference: same <shape>, <colour>, <cap/pump>, <label layout and logo>. Do not change or add text on the packaging.
Style: <casual iPhone photo, natural light, slightly imperfect framing, realistic skin texture | clean editorial> — should look like a real TikTok creator's photo, not an ad.
Composition: subject centred, keep the top 20% fairly clean for text overlay.
Do not add any captions, text, watermarks, or other brand logos.
```

For slides 2+ in the same chat, start with: "Same person and setting as the previous image, new shot: ..." so the slideshow looks like one shoot.

## Making it look like a real post
Real TikTok slideshows look like phone photos: natural light, a bit of clutter, real skin texture, slightly off-centre. Over-polished studio images perform worse and look like ads. Ask for "casual iPhone photo" unless the winner was clearly editorial.

## Text-writing tips
- Slide 1 hook: under 10 words, about the viewer ("POV:", "you need this if...", "stop scrolling if...").
- Middle slides: one benefit each, concrete and taken from the product listing.
- Last slide: soft CTA ("linked in the orange basket", "the shop link is on this post").
- Benefits only: no invented personal results or medical claims.

## Make it look genuine (the user's feedback, 7 Nov)
Staged, tidy, product-centred images read as AI ads. Every photo prompt should ask for:
- a genuine, unedited phone photo a normal person posted: candid, slightly tilted, imperfect framing, mixed home lighting (lamp, phone flash), a little grain;
- an ordinary lived-in background with some mess (unmade bed, mug, charger, clothes on a chair);
- a person or hand in shot where it makes sense: mirror selfies with the phone covering the face for clothes, a hand holding the product close to the camera for small items.
**The product must be clearly visible and in focus** (about a third of the frame): open lids fully, show the actual item, not just its box. Clothing is worn, never laid flat.
Never copy the face, hair or room of a model in the listing photo.

## On-screen text
Use TikTok Sans (in `fonts/`, used automatically) with emoji, lower-case and casual, the way a creator types ("my dad every single christmas 😭🙄"). Default size 52–56. Use `box` (black on white rounded boxes) on screenshots and busy photos, `outline` on photos with a plain area. Keep text off faces and off the product.

## True product size (the user's feedback, 7 Nov)
AI photos get scale wrong (plushes drawn pillow-sized when they're hand-sized; Celebrations minis drawn like full-size bars when each is only 4-5cm, thumb-sized). Food minis, keyrings, jewellery and figures are the usual offenders. For every product:
1. Find its real size: the listing title ("100ml", "250ml", "21.6cm", "keychain"), the listing's dimension pictures, and the original creator's photos where it sits next to a hand.
2. Start every photo prompt with a SIZE line, e.g. "SIZE: about 20cm tall, roughly the length of an adult's hand, only a bit bigger than a drink can." Add a familiar object for scale (a hand, a can, a mug, a phone).
3. When checking the result, compare the product with hands and furniture. If the scale is off, regenerate.
Write the size into `_build/plan.md` for each product.

## Screenshot hooks (chat, email, comments)
No extra text box on top: the screenshot is the hook. Mix light and dark mode chats. Put comment threads over the video (`"bg": "raw/slide-2.png"` in screens.json) like the TikTok app does. Set `"no_text": true` on that slide in slides.json.
