# O-YAKU explainer video

Fully simulated walkthrough built with [Remotion](https://www.remotion.dev) (React → MP4), in the
site's own colors and fonts. ~46s at 1920×1080.

| Scene | What happens |
|---|---|
| Intro | Logo + "כל הידע מהשיעורים והלייבים" |
| Locked | Knowledge base, logged out: the engine is locked → click "התחברות עם Patreon" |
| Check | Short subscription check (connect → active subscription ✓) → header shows "מחובר · מנוי פעיל" |
| Ask | Type "מתי גוזמים זית?" → search |
| Answer | Sources from real knowledge segments; the live source is highlighted → "צפייה בקטע בפטרון" |
| Patreon | Post page, player jumps to the timestamp, clip plays with subtitles |
| Outro | CTA "הצטרפו כמנויים ב-Patreon" |

## Commands

```bash
cd video
npm install
npm run studio   # live preview + timeline scrubbing in the browser
npm run render   # → out/o-yaku-explainer.mp4
```

## Editing

Everything content-related is in `src/content.ts`: the question, the sources, the live timestamp,
captions over the clip.

**Adding the live clip:** trim the clip to the exact segment, put it in `video/public/` (e.g.
`live-clip.mp4`), then in `content.ts` set `live.clipFile: 'live-clip.mp4'`, set `clipSeconds`
to its length, and replace `subtitles` with the real lines. The video length adjusts automatically.

Timing of the site walkthrough (clicks, typing, camera) is in `T` and the `Camera`/`Cursor`
keyframes in `src/scenes/SiteFlow.tsx`. The on-screen captions are at the bottom of
`src/Explainer.tsx`.

## Voice-over

Narration lines live in `narration` in `src/content.ts` (caption, spoken text, `maxSec` window).
Any `public/voice/<cue>.mp3` is picked up automatically; or set `audio` to a different file name.

**AI voice (ElevenLabs):** needs `ELEVENLABS_API_KEY` in the environment (never in the repo) and
network access to `api.elevenlabs.io`.

```bash
npm run voice -- --list-voices        # find your cloned voice's id
npm run voice -- --voice <voice_id>   # generates changed lines, reports length vs. maxSec
npm run render
```

Only lines whose text changed are regenerated (`public/voice/manifest.json`); add `--force` or
`--only intro,ask` to redo specific lines. Default model is `eleven_v3` (`ELEVENLABS_MODEL` to change).
