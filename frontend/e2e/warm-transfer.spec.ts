import { test, expect, Page, APIRequestContext } from '@playwright/test';

// Helpers
async function joinRoom(page: Page, identity: string, roomName: string) {
  await page.goto('/');
  await page.getByLabel('Your Name').fill(identity);
  await page.getByLabel('Room Name').fill(roomName);
  await page.getByRole('button', { name: 'Join Room' }).click();
  await expect(page.getByText(`Room: ${roomName}`)).toBeVisible();
}

test.describe('Warm Transfer PRD flow', () => {
  test('Join → Initiate transfer → Briefing room → Complete', async ({ page, request }) => {
    const room = 'e2e-room-' + Math.random().toString(36).slice(2, 6);

    await joinRoom(page, 'Agent A', room);

    // Initiate
    const genBtn = page.getByRole('button', { name: 'Generate Transfer Summary' });
    await genBtn.click();

  await expect(genBtn).toBeEnabled();
  // Wait for briefing card and transfer id (less ambiguous than generic 'Mock Summary')
  await expect(page.getByText('Briefing Room Created')).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText('Transfer ID:', { exact: false })).toBeVisible();

    // Briefing room appears
  const briefingCard = page.getByText('Briefing Room Created');
  await expect(briefingCard).toBeVisible();

    // Join as Agent A (briefing)
    await page.getByRole('button', { name: 'Join as Agent A' }).click();
    await expect(page.getByText('Room:')).toBeVisible();

    // Switch back by re-joining main room (use homepage flow)
    await page.goto('/');
    await joinRoom(page, 'Agent A', room);

  // Complete transfer (enter Agent B identity)
  // Use placeholder since label isn't programmatically associated with input
  await page.getByPlaceholder('Agent B').fill('Agent B');
    await page.getByRole('button', { name: 'Complete Transfer' }).click();

    // Alert may appear with message; just ensure no crash
    // Poll backend for participants to ensure Agent A potentially leaves
    const resp = await request.get(`http://localhost:8000/participants?room_name=${room}`);
    expect(resp.ok()).toBeTruthy();

    // Verify a transfer record exists in backend for this room
    const transfers = await request.get(`http://localhost:8000/transfers?room_name=${room}&limit=1`);
    expect(transfers.ok()).toBeTruthy();
    const tjson = await transfers.json();
    expect(Array.isArray(tjson.transfers) && tjson.transfers.length >= 1).toBeTruthy();
  });

  test('Agent start/say/stop basic', async ({ request }: { request: APIRequestContext }) => {
    const room = 'e2e-agent-' + Math.random().toString(36).slice(2, 6);
    // Start agent
    const start = await request.post('http://localhost:8000/agent/start', {
      data: { room_name: room, identity: 'ai-agent' },
    });
    expect(start.ok()).toBeTruthy();

    // Say
    const say = await request.post('http://localhost:8000/agent/say', {
      data: { room_name: room, text: 'Hello E2E test' },
    });
    expect(say.ok()).toBeTruthy();

    // Participants should include agent
    const parts = await request.get(`http://localhost:8000/participants?room_name=${room}`);
    expect(parts.ok()).toBeTruthy();
    const json = await parts.json();
    expect(Array.isArray(json.participants)).toBeTruthy();
  });

  test('AI voice endpoint returns wav', async ({ request }) => {
    const r = await request.post('http://localhost:8000/ai-voice', {
      data: { prompt: 'Just say hello', voice: null },
    });
    expect(r.ok()).toBeTruthy();
    const ct = r.headers()['content-type'] || r.headers()['Content-Type'];
    expect(ct).toContain('audio/wav');
    const body = await r.body();
    expect(body.byteLength).toBeGreaterThan(1000);
  });
});
