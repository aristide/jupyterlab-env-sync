import { test, expect } from '@playwright/test';

test('should load the extension', async ({ page }) => {
  await page.goto('http://localhost:8888/lab');
  // Verify JupyterLab loads successfully
  await expect(page.locator('#jp-main-dock-panel')).toBeVisible({
    timeout: 60000
  });
});
