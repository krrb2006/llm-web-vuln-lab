#!/usr/bin/env node
/** Observe harmless DOM markers in the eight local D teaching samples.
 *
 * A new headless Chrome profile is used. The only target is loopback; marker
 * input changes an HTML data attribute and performs no network request.
 * Reports are D observations for independent review, not truth labels.
 */

import { spawn, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, realpathSync, rmSync, writeFileSync, mkdirSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'http://127.0.0.1:4280';
const browserPath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const marker = "<script>document.documentElement.dataset.labXss='yes'</script>";
const jsLink = "javascript:void(document.documentElement.dataset.labXss='yes')";
const stored = ['S017', 'S018', 'S021', 'S022'];
const sleep = (ms) => new Promise((done) => setTimeout(done, ms));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function resetSample(sample) {
  const result = spawnSync('python', [join(root, 'environment', 'init_lab_db.py'), '--reset-sample', sample], {
    cwd: root, encoding: 'utf8', timeout: 90000,
  });
  assert(result.status === 0, `${sample}: sample reset failed: ${result.stderr ?? ''}`);
}

async function post(sample, endpoint, fields) {
  const target = `${base}/lab_cases/${sample}/${endpoint}`;
  const response = await fetch(target, {
    method: 'POST', body: new URLSearchParams(fields), redirect: 'manual',
    headers: { 'User-Agent': 'D-browser-reference/1.0' },
  });
  return {
    method: 'POST', path: `/lab_cases/${sample}/${endpoint}`,
    fields, status: response.status, location: response.headers.get('location'),
    response_sha256: createHash('sha256').update(Buffer.from(await response.arrayBuffer())).digest('hex'),
  };
}

class ChromePage {
  constructor() { this.nextId = 1; this.pending = new Map(); }

  async start() {
    assert(existsSync(browserPath), `Chrome missing: ${browserPath}`);
    this.profile = mkdtempSync(join(tmpdir(), 'd-lab-chrome-'));
    this.process = spawn(browserPath, [
      '--headless=new', '--disable-gpu', '--disable-extensions', '--disable-background-networking',
      '--no-first-run', '--no-default-browser-check', '--no-proxy-server',
      '--remote-debugging-port=0', `--user-data-dir=${this.profile}`, 'about:blank',
    ], { stdio: 'ignore' });
    const activePort = join(this.profile, 'DevToolsActivePort');
    for (let i = 0; i < 100 && !existsSync(activePort); i++) await sleep(100);
    assert(existsSync(activePort), 'Chrome DevTools port did not start');
    const port = readFileSync(activePort, 'utf8').split(/\r?\n/)[0];
    const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    const target = targets.find((item) => item.type === 'page');
    assert(target?.webSocketDebuggerUrl, 'Chrome page target missing');
    this.ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((done, reject) => {
      this.ws.addEventListener('open', done, { once: true });
      this.ws.addEventListener('error', reject, { once: true });
    });
    this.ws.addEventListener('message', (event) => {
      const message = JSON.parse(event.data);
      if (!message.id) return;
      const entry = this.pending.get(message.id);
      if (!entry) return;
      this.pending.delete(message.id);
      if (message.error) entry.reject(new Error(JSON.stringify(message.error)));
      else entry.resolve(message.result);
    });
    await this.send('Page.enable');
    await this.send('Runtime.enable');
    this.version = (await this.send('Browser.getVersion')).product;
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`CDP timeout: ${method}`));
      }, 15000);
      this.pending.set(id, {
        resolve: (value) => { clearTimeout(timer); resolve(value); },
        reject: (error) => { clearTimeout(timer); reject(error); },
      });
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }

  async evaluate(expression) {
    const result = await this.send('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    if (result.exceptionDetails) throw new Error(`Browser evaluation error: ${result.exceptionDetails.text}`);
    return result.result.value;
  }

  async open(url) {
    await this.send('Page.navigate', { url });
    for (let attempt = 0; attempt < 60; attempt++) {
      await sleep(100);
      try {
        const state = await this.evaluate('({url:location.href,ready:document.readyState})');
        if (state.url === url && state.ready === 'complete') return;
      } catch { /* navigation can replace the execution context */ }
    }
    throw new Error(`Browser did not finish navigation: ${url}`);
  }

  async snapshot() {
    return this.evaluate(`({
      location:location.href,
      title:document.title,
      html_data_lab_xss:document.documentElement.getAttribute('data-lab-xss'),
      script_element_count:document.querySelectorAll('script').length,
      rendered_dom:document.documentElement.outerHTML
    })`);
  }

  async clickPreviewLink() {
    const rect = await this.evaluate(`(() => {
      const a = document.querySelector('p > a[href]');
      if (!a) throw new Error('preview link missing');
      const r = a.getBoundingClientRect();
      return {href:a.getAttribute('href'),x:r.x+r.width/2,y:r.y+r.height/2};
    })()`);
    for (const type of ['mousePressed', 'mouseReleased']) {
      await this.send('Input.dispatchMouseEvent', {
        type, x: rect.x, y: rect.y, button: 'left', clickCount: 1,
      });
    }
    await sleep(300);
    return rect.href;
  }

  stop() {
    try { this.ws?.close(); } catch { /* cleanup */ }
    if (this.process?.pid) {
      // Terminate only the browser tree started above; Chrome can leave child
      // processes holding the temporary profile open after its parent exits.
      spawnSync('taskkill', ['/PID', String(this.process.pid), '/T', '/F'], {
        encoding: 'utf8', timeout: 10000,
      });
    }
    if (this.profile && existsSync(this.profile)) {
      const directory = realpathSync(this.profile);
      const tempRoot = realpathSync(tmpdir());
      assert(directory.toLowerCase().startsWith((tempRoot + '\\d-lab-chrome-').toLowerCase()),
        `Refusing to remove profile outside the named temporary directory: ${directory}`);
      try {
        rmSync(directory, { recursive: true, force: true, maxRetries: 15, retryDelay: 300 });
      } catch (error) {
        console.error(`WARNING: temporary Chrome profile could not be removed: ${error.message}`);
      }
    }
  }
}

function save(sample, runtime, version, observations, note) {
  const content = {
    kind: 'reference_browser_dom_observation', review_status: 'pending_independent_review',
    ground_truth: null, observed_at_utc: new Date().toISOString(), sample_id: sample,
    base_url: base, d_source_commit: runtime.d_source.commit, browser_version: version,
    marker_purpose: 'Set only document.documentElement.dataset.labXss; no Cookie access or external request',
    note, observations,
  };
  const destination = join(root, 'evidence', 'truth', sample, 'browser_reference.json');
  mkdirSync(dirname(destination), { recursive: true });
  writeFileSync(destination, JSON.stringify(content, null, 2) + '\n');
  console.log(`${sample}: browser observations saved`);
}

async function checkGuestbook(page, sample, runtime) {
  resetSample(sample);
  const submitted = await post(sample, 'index.php', { body: marker });
  assert(submitted.status === 303, `${sample}: marker write did not redirect`);
  const url = `${base}/lab_cases/${sample}/index.php`;
  await page.open(url);
  const firstRead = await page.snapshot();
  await page.open(url);
  const independentRead = await page.snapshot();
  assert(independentRead.rendered_dom.includes('labXss'), `${sample}: marker absent from read page`);
  save(sample, runtime, page.version, { submitted, first_read: firstRead, separate_read: independentRead },
    'Write was an HTTP POST; reads were two separate browser GET navigations.');
}

async function checkForm(page, sample, runtime) {
  const url = `${base}/lab_cases/${sample}/index.php`;
  await page.open(url);
  const before = await page.snapshot();
  await page.evaluate(`(() => {
    const input = document.querySelector('textarea[name="content"]');
    input.value = ${JSON.stringify(marker)};
    input.form.requestSubmit();
  })()`);
  let after;
  for (let attempt = 0; attempt < 50; attempt++) {
    await sleep(100);
    try {
      after = await page.snapshot();
      if (after.rendered_dom.includes('labXss')) break;
    } catch { /* navigation in progress */ }
  }
  assert(after?.rendered_dom.includes('labXss'), `${sample}: POST result did not show marker`);
  save(sample, runtime, page.version, { before, after_post: after, posted_field: marker },
    'Browser submitted the page form with POST, then rendered the response.');
}

async function checkDraft(page, sample, runtime) {
  resetSample(sample);
  const submitted = await post(sample, 'submit.php', { title: 'Teaching draft', body: marker });
  assert(submitted.status === 303, `${sample}: marker draft write did not redirect`);
  const previewPath = submitted.location;
  assert(/^preview\.php\?id=[1-9][0-9]*$/.test(previewPath), `${sample}: unexpected draft redirect`);
  await page.open(`${base}/lab_cases/${sample}/list.php`);
  const listing = await page.snapshot();
  await page.open(`${base}/lab_cases/${sample}/${previewPath}`);
  const preview = await page.snapshot();
  assert(preview.rendered_dom.includes('labXss'), `${sample}: marker absent from draft preview`);
  save(sample, runtime, page.version, { submitted, listing, separate_preview_read: preview },
    'Write, list, and preview are separate requests; only preview renders stored body.');
}

async function checkLink(page, sample, runtime) {
  const url = `${base}/lab_cases/${sample}/index.php?${new URLSearchParams({ url: jsLink })}`;
  await page.open(url);
  const beforeClick = await page.snapshot();
  const hrefBeforeClick = await page.clickPreviewLink();
  const afterClick = await page.snapshot();
  save(sample, runtime, page.version, { before_click: beforeClick, href_before_click: hrefBeforeClick, after_click: afterClick },
    'A Chrome mouse press/release clicked the local preview link; no external URL was opened.');
}

async function main() {
  const runtime = JSON.parse(readFileSync(join(root, 'environment', 'runtime_check.json'), 'utf8'));
  assert(runtime.summary.total === 37 && runtime.summary.passed === 37 && runtime.summary.failed === 0,
    '37/37 runtime source and syntax checks required');
  const page = new ChromePage();
  try {
    await page.start();
    for (const sample of ['S017', 'S018']) await checkGuestbook(page, sample, runtime);
    for (const sample of ['S019', 'S020']) await checkForm(page, sample, runtime);
    for (const sample of ['S021', 'S022']) await checkDraft(page, sample, runtime);
    for (const sample of ['S023', 'S024']) await checkLink(page, sample, runtime);
  } finally {
    page.stop();
    for (const sample of stored) resetSample(sample);
  }
}

main().catch((error) => { console.error(`ERROR: ${error.message}`); process.exitCode = 1; });
