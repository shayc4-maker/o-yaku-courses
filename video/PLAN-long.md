# Long version — plan (build after the site is finished)

Goal: a ~2 minute walkthrough that keeps the current knowledge-base flow (Patreon connect →
question → answer with sources → live clip) and adds a quick pass over the rest of the site.
Build it once the real pages are final, so every simulated screen matches the live site.

| # | Scene | What it shows | ~len |
|---|---|---|---|
| 1 | Intro | Logo + one-line promise | 4s |
| 2 | Knowledge base | Current flow, shortened: connect → ask → sources | 25s |
| 3 | Live clip | Current edit with the lesson's own sound | 20s |
| 4 | Lesson library | Browse lessons by species/season, open one | 15s |
| 5 | Articles | Scroll an article (e.g. olive development log) | 12s |
| 6 | Shop | Grid → product → add to cart | 15s |
| 7 | Ceramics order | Pick pot shape/size/glaze (PotPreview) → order form | 18s |
| 8 | Outro | CTA + o-yaku.com | 6s |

Notes
- Reuse: `BrowserFrame`, `Camera`, `Cursor`, `Caption`, the `d()` pause mapping and the
  narration cue system. Each new scene is its own file in `src/scenes/` and its own
  composition section, so the short version keeps working unchanged.
- Screens: mirror the real components (Shop.tsx, Ceramics.tsx/PotPreview.tsx, Articles.tsx,
  Knowledge.tsx) with real content from the database where it exists.
- Sound: record narration per scene (lossless), mix in DaVinci, attach with `soundtrack`.
- Background music: needed — quiet, calm track under the whole video (also worth adding to the
  short version). Royalty-free with a commercial license. Duck it under the narration and almost
  mute it during the live clip. In DaVinci: its own track in the mix. Without a DaVinci mix: the
  `music` prop already ducks automatically (lower under voice, near-silent in the clip).
- Formats: 16:9 for the site/YouTube; consider a 9:16 cut per scene for social.
