import { Config } from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setOverwriteOutput(true);
// Cloud sessions ship a Playwright headless shell; locally Remotion downloads its own if this path is missing.
const HEADLESS = '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
try {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  if (require('fs').existsSync(HEADLESS)) Config.setBrowserExecutable(HEADLESS);
} catch {
  /* not available — use Remotion's default browser */
}
