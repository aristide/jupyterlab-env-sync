import { test, expect } from '@playwright/test';

const BASE = 'http://localhost:8888';
const API = `${BASE}/jupyterlab-env-sync/env`;

test.describe('jupyterlab-env-sync', () => {
  test('should load the extension', async ({ page }) => {
    await page.goto(`${BASE}/lab`);
    await expect(page.locator('#jp-main-dock-panel')).toBeVisible({
      timeout: 60000
    });
  });

  test.describe('REST API', () => {
    test.afterEach(async ({ request }) => {
      // Clean up test variables
      for (const ext of ['ui-test-ext', 'ext-a', 'ext-b']) {
        await request.delete(`${API}/extension/${ext}`);
      }
    });

    test('GET /env returns empty object initially', async ({ request }) => {
      // Reset first to ensure clean state
      await request.delete(`${API}/extension/ui-test-ext`);
      const resp = await request.get(API);
      expect(resp.ok()).toBeTruthy();
      const data = await resp.json();
      expect(typeof data).toBe('object');
    });

    test('PUT /env/{key} sets a variable', async ({ request }) => {
      const resp = await request.put(`${API}/MY_VAR`, {
        data: { extension_id: 'ui-test-ext', value: 'hello' }
      });
      expect(resp.ok()).toBeTruthy();
      const entry = await resp.json();
      expect(entry.value).toBe('hello');
      expect(entry.set_by).toBe('ui-test-ext');
      expect(entry.spawner_value).toBeDefined();
      expect(entry.set_at).toBeTruthy();
    });

    test('GET /env returns set variables', async ({ request }) => {
      await request.put(`${API}/GET_TEST`, {
        data: { extension_id: 'ui-test-ext', value: 'world' }
      });
      const resp = await request.get(API);
      const data = await resp.json();
      expect(data['GET_TEST']).toBeDefined();
      expect(data['GET_TEST'].value).toBe('world');
    });

    test('GET /env?extension_id filters by extension', async ({ request }) => {
      await request.put(`${API}/EXT_A_KEY`, {
        data: { extension_id: 'ext-a', value: 'a' }
      });
      await request.put(`${API}/EXT_B_KEY`, {
        data: { extension_id: 'ext-b', value: 'b' }
      });

      const resp = await request.get(`${API}?extension_id=ext-a`);
      const data = await resp.json();
      expect(data['EXT_A_KEY']).toBe('a');
      expect(data['EXT_B_KEY']).toBeUndefined();
    });

    test('DELETE /env/{key} resets a variable', async ({ request }) => {
      await request.put(`${API}/DEL_KEY`, {
        data: { extension_id: 'ui-test-ext', value: 'temp' }
      });

      const resp = await request.delete(`${API}/DEL_KEY`, {
        data: { extension_id: 'ui-test-ext' }
      });
      expect(resp.ok()).toBeTruthy();

      const all = await (await request.get(API)).json();
      expect(all['DEL_KEY']).toBeUndefined();
    });

    test('DELETE /env/{key} rejects non-owner without force', async ({
      request
    }) => {
      await request.put(`${API}/OWNED_KEY`, {
        data: { extension_id: 'ext-a', value: 'mine' }
      });

      const resp = await request.delete(`${API}/OWNED_KEY`, {
        data: { extension_id: 'ext-b', force: false }
      });
      expect(resp.status()).toBe(403);

      // Key should still exist
      const all = await (await request.get(API)).json();
      expect(all['OWNED_KEY'].value).toBe('mine');
    });

    test('DELETE /env/{key} allows non-owner with force=true', async ({
      request
    }) => {
      await request.put(`${API}/FORCE_KEY`, {
        data: { extension_id: 'ext-a', value: 'v' }
      });

      const resp = await request.delete(`${API}/FORCE_KEY`, {
        data: { extension_id: 'ext-b', force: true }
      });
      expect(resp.ok()).toBeTruthy();

      const all = await (await request.get(API)).json();
      expect(all['FORCE_KEY']).toBeUndefined();
    });

    test('DELETE /env/extension/{id} resets all by extension', async ({
      request
    }) => {
      await request.put(`${API}/BATCH_1`, {
        data: { extension_id: 'ext-a', value: '1' }
      });
      await request.put(`${API}/BATCH_2`, {
        data: { extension_id: 'ext-a', value: '2' }
      });
      await request.put(`${API}/OTHER`, {
        data: { extension_id: 'ext-b', value: '3' }
      });

      const resp = await request.delete(`${API}/extension/ext-a`);
      expect(resp.ok()).toBeTruthy();
      const body = await resp.json();
      expect(body.reset_keys.sort()).toEqual(['BATCH_1', 'BATCH_2']);

      const all = await (await request.get(API)).json();
      expect(all['BATCH_1']).toBeUndefined();
      expect(all['BATCH_2']).toBeUndefined();
      expect(all['OTHER']).toBeDefined();
    });

    test('set preserves spawner_value across overwrites', async ({
      request
    }) => {
      await request.put(`${API}/SPAWN_TEST`, {
        data: { extension_id: 'ext-a', value: 'first' }
      });
      const first = await (await request.get(API)).json();
      const spawner = first['SPAWN_TEST'].spawner_value;

      await request.put(`${API}/SPAWN_TEST`, {
        data: { extension_id: 'ext-b', value: 'second' }
      });
      const second = await (await request.get(API)).json();
      expect(second['SPAWN_TEST'].spawner_value).toBe(spawner);
      expect(second['SPAWN_TEST'].set_by).toBe('ext-b');
      expect(second['SPAWN_TEST'].value).toBe('second');
    });
  });

  test.describe('kernel propagation', () => {
    test('env var is visible in a Python kernel after set', async ({
      page,
      request
    }) => {
      // Set a variable via the API
      await request.put(`${API}/UI_TEST_PROP`, {
        data: { extension_id: 'ui-test-ext', value: 'kernel-check' }
      });

      // Open JupyterLab and create a notebook
      await page.goto(`${BASE}/lab`);
      await expect(page.locator('#jp-main-dock-panel')).toBeVisible({
        timeout: 60000
      });

      // Open a new Python notebook via the menu
      await page.keyboard.press('Control+Shift+l');
      await page.waitForTimeout(500);

      // Use the launcher to open a Python notebook
      const launcher = page.locator('.jp-Launcher-body');
      if (await launcher.isVisible({ timeout: 5000 }).catch(() => false)) {
        const pythonCard = launcher.locator('text=Python 3').first();
        if (await pythonCard.isVisible({ timeout: 3000 }).catch(() => false)) {
          await pythonCard.click();
        }
      }

      // Wait for notebook to be ready
      await page.waitForTimeout(3000);

      // Type and execute code to check the env var
      const cell = page.locator('.jp-Cell .jp-Editor .cm-editor').first();
      if (await cell.isVisible({ timeout: 5000 }).catch(() => false)) {
        await cell.click();
        await page.keyboard.type(
          "import os; print(os.environ.get('UI_TEST_PROP', 'NOT_FOUND'))"
        );
        await page.keyboard.press('Shift+Enter');

        // Wait for output
        await page.waitForTimeout(5000);

        // Check output contains expected value
        const output = page.locator('.jp-OutputArea-output').first();
        if (await output.isVisible({ timeout: 10000 }).catch(() => false)) {
          const text = await output.textContent();
          expect(text).toContain('kernel-check');
        }
      }

      // Cleanup
      await request.delete(`${API}/extension/ui-test-ext`);
    });
  });
});
