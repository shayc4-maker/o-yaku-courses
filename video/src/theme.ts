import { continueRender, delayRender, staticFile } from 'remotion';

/*
 * Same families as the site's fonts.css (Assistant + Frank Ruhl Libre), bundled in public/fonts
 * so rendering never depends on reaching Google Fonts. Both are variable fonts (all weights).
 */
const HEBREW = 'U+0307-0308, U+0590-05FF, U+200C-2010, U+20AA, U+25CC, U+FB1D-FB4F';
const LATIN = 'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';

const FACES: [family: string, file: string, range: string][] = [
  ['Assistant', 'assistant-hebrew.woff2', HEBREW],
  ['Assistant', 'assistant-latin.woff2', LATIN],
  ['Frank Ruhl Libre', 'frank-hebrew.woff2', HEBREW],
  ['Frank Ruhl Libre', 'frank-latin.woff2', LATIN],
];

if (typeof document !== 'undefined') {
  const handle = delayRender('Loading fonts');
  Promise.all(
    FACES.map(([family, file, unicodeRange]) =>
      new FontFace(family, `url(${staticFile(`fonts/${file}`)}) format('woff2')`, { weight: '200 900', unicodeRange })
        .load()
        .then((face) => document.fonts.add(face)),
    ),
  )
    .then(() => continueRender(handle))
    .catch((err) => {
      console.error('Font loading failed', err);
      continueRender(handle);
    });
}

export const BODY = "'Assistant', 'Helvetica Neue', system-ui, sans-serif";
export const DISPLAY = "'Frank Ruhl Libre', 'Times New Roman', serif";

// Subset of the site's colors.css tokens.
export const C = {
  clay50: '#FDF3F3',
  clay100: '#FAE4E4',
  clay400: '#E5817F',
  clay500: '#E06064',
  clay600: '#C74C50',
  clay700: '#A23C40',
  stone0: '#FFFFFF',
  stone50: '#FBF9F6',
  stone100: '#F4F1EC',
  stone200: '#E8E3DB',
  stone300: '#D6CFC4',
  stone400: '#B3AAA0',
  stone500: '#8C8479',
  stone700: '#4B4640',
  stone800: '#2E2B27',
  stone900: '#1B1917',
  moss100: '#EDF0E8',
  moss500: '#8B9878',
  moss700: '#5A6650',
};

export const FPS = 30;
export const W = 1920;
export const H = 1080;
