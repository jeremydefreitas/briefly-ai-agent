// Exercise stream parsing and live activity with a minimal DOM, without a browser.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");
const { webcrypto } = require("node:crypto");

class Element {
  constructor(tag = "div") {
    this.tagName = tag.toUpperCase();
    this.listeners = {};
    this.children = [];
    this.className = "";
    this.style = {};
    this.value = "";
    this.scrollHeight = 30;
    this.classList = {
      contains: (name) => this.className.split(" ").includes(name),
      add: (name) => {
        this.className += ` ${name}`;
      },
      remove: (name) => {
        this.className = this.className
          .split(" ")
          .filter((item) => item !== name)
          .join(" ");
      },
    };
  }
  append(...items) {
    for (const item of items) {
      item.parent = this;
      this.children.push(item);
    }
  }
  replaceChildren(...items) {
    this.children = [];
    this.append(...items);
  }
  remove() {
    if (this.parent)
      this.parent.children = this.parent.children.filter(
        (item) => item !== this,
      );
  }
  querySelector(selector) {
    return this.children.find((item) =>
      item.classList.contains(selector.slice(1)),
    );
  }
  get firstElementChild() {
    return this.children[0];
  }
  get lastElementChild() {
    return this.children.at(-1);
  }
  setAttribute() {}
  addEventListener(name, callback) {
    this.listeners[name] = callback;
  }
  click() {
    this.clicked = true;
  }
  focus() {}
}

async function main() {
  const elements = new Map();
  const element = (id) => {
    if (!elements.has(id)) elements.set(id, new Element());
    return elements.get(id);
  };
  const context = vm.createContext({
    document: {
      getElementById: element,
      createElement: (tag) => new Element(tag),
      createTextNode: (text) =>
        Object.assign(new Element("#text"), { textContent: text }),
    },
    crypto: webcrypto,
    TextDecoder,
    Date,
    Map,
    URL,
    setInterval: () => {},
    fetch: async () => ({
      ok: true,
      json: async () => ({
        servers: [
          { name: "filesystem", status: "connected", tool_count: 13 },
          {
            name: "tavily",
            status: "unavailable",
            tool_count: 0,
            mode: "keyless",
          },
          { name: "open-meteo", status: "connected", tool_count: 2 },
        ],
      }),
    }),
  });
  const html = fs.readFileSync("static/index.html", "utf8");
  vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1], context);
  await context.refreshServers();
  assert.match(
    element("mcp-status").children[0].children[1].textContent,
    /Connected/,
  );
  assert.match(
    element("mcp-status").children[1].children[1].textContent,
    /Unavailable/,
  );
  assert.match(
    element("mcp-status").children[2].children[1].textContent,
    /Weather · Connected/,
  );

  let controller;
  const response = new Response(
    new ReadableStream({
      start(value) {
        controller = value;
      },
    }),
  );
  const pending = context.readChatStream(response);
  const encoder = new TextEncoder();
  controller.enqueue(
    encoder.encode(
      JSON.stringify({
        type: "tool_start",
        server: "filesystem",
        tool: "read_text_file",
        message: "Reading file.",
      }) + "\n",
    ),
  );
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(element("mcp-status").children[0].className, /active/);
  assert.equal(element("activity-log").children.length, 1);
  assert.match(element("live-tags").children[0].className, /running/);
  assert.equal(
    element("live-tags").children[0].children[1].textContent,
    "Reading a file",
  );
  console.log(
    "PASS: tool activity and active badge update before the final response",
  );

  const rest = [
    {
      type: "tool_end",
      server: "filesystem",
      tool: "read_text_file",
      message: "Read complete.",
    },
    { type: "response", message: "Response ready.", response: "Hello 👋" },
  ];
  const bytes = encoder.encode(
    rest.map((event) => JSON.stringify(event)).join("\n") + "\n",
  );
  for (const byte of bytes) controller.enqueue(Uint8Array.of(byte));
  controller.close();
  assert.equal(await pending, "Hello 👋");
  assert.doesNotMatch(element("mcp-status").children[0].className, /active/);
  assert.match(element("live-tags").children[0].className, /done/);
  assert.equal(
    element("live-tags").children[0].children[1].textContent,
    "File read",
  );
  assert.equal(
    element("live-tags").lastElementChild.children[1].textContent,
    "Response ready",
  );
  console.log("PASS: split JSON lines and multibyte UTF-8 decode correctly");

  const errorResponse = new Response(
    JSON.stringify({ type: "error", message: "Please retry." }) + "\n",
  );
  await assert.rejects(context.readChatStream(errorResponse), /Please retry/);
  assert.match(element("activity-log").lastElementChild.className, /error/);
  assert.match(element("live-tags").lastElementChild.className, /failed/);
  console.log(
    "PASS: streamed errors are shown and propagate to chat retry handling",
  );

  const news = context.buildChatRequest(
    "Give me a briefing on European politics today, focusing on diplomacy.",
    new Date("2026-10-13T12:00:00Z"),
  );
  assert.match(news, /Tavily search/);
  assert.match(news, /at most 3 search calls with 5 results each/);
  assert.match(news, /include_raw_content false/);
  assert.match(news, /at most 1 extract call/);
  assert.match(news, /explaining any gaps instead of continuing to search/);
  assert.match(news, /2026-10-13T12:00:00.000Z/);
  assert.match(news, /European politics/);
  assert.match(news, /publication dates/);
  assert.match(news, /distinguish third-party sources from official sources/);
  assert.match(news, /Do not save files unless asked/);
  const weather = context.buildChatRequest(
    "Give me a weather briefing for Los Angeles today in about 200 words.",
  );
  assert.match(weather, /Open-Meteo geocoding and forecast/);
  assert.match(weather, /about 200 words/);
  assert.match(
    weather,
    /## Conditions, ## Rain & wind, ## Travel notes, and ## Sources/,
  );
  assert.match(weather, /Do not invent/);
  assert.doesNotMatch(html, /id="briefing-form"|id="generate"|class="setup"/);
  console.log(
    "PASS: freeform prompts retain research budgets, date, source and weather guidance without a hidden generator",
  );

  const rendered = new Element();
  context.renderBrief(
    rendered,
    "# Briefing\n\n- **A development** [Source](https://example.com/news)\n- Another\n\n| Topic | Impact |\n| --- | --- |\n| News | High |\n<script>alert(1)</script>\n[Bad](javascript:alert(1))",
  );
  const flatten = (node) => [node, ...node.children.flatMap(flatten)];
  const nodes = flatten(rendered);
  assert(nodes.some((node) => node.tagName === "H2"));
  assert(nodes.some((node) => node.tagName === "TABLE"));
  const links = nodes.filter((node) => node.tagName === "A");
  assert.equal(links.length, 1);
  assert.equal(links[0].href, "https://example.com/news");
  assert(!nodes.some((node) => node.tagName === "SCRIPT"));
  console.log(
    "PASS: headings, lists, tables, and safe links render without HTML execution",
  );

  const forecast = new Element();
  context.renderBrief(
    forecast,
    "# Los Angeles\nAs of 13 October\n\n**Conditions**\n| Metric | Value |\n| --- | --- |\n| Temperature | 22 °C |\n\n## Rain & wind\n- *Light winds*; no rain reported.\n\n## Travel notes\nTake a ~~heavy~~ light jacket.\n\n## Sources\n[Forecast](https://example.com/weather)\n\n```html\n<script>unsafe()</script>\n```",
  );
  const forecastNodes = flatten(forecast);
  assert.equal(
    forecastNodes.filter((node) => node.className.includes("weather-section"))
      .length,
    3,
  );
  assert.equal(
    forecastNodes.filter((node) => node.className === "section-icon").length,
    3,
  );
  assert.equal(
    forecastNodes.filter((node) => node.className.includes("source-section"))
      .length,
    1,
  );
  assert(forecastNodes.some((node) => node.className === "as-of"));
  assert(
    forecastNodes.some(
      (node) => node.tagName === "EM" && node.textContent === "Light winds",
    ),
  );
  assert(
    forecastNodes.some(
      (node) => node.tagName === "DEL" && node.textContent === "heavy",
    ),
  );
  assert(
    forecastNodes.some(
      (node) =>
        node.tagName === "PRE" &&
        node.textContent === "<script>unsafe()</script>",
    ),
  );
  assert(!forecastNodes.some((node) => node.tagName === "SCRIPT"));
  const prose = new Element();
  context.renderBrief(
    prose,
    "A wrapped paragraph\ncontinues on the next line.\n\nA second paragraph.",
  );
  assert.equal(prose.children.length, 2);
  const report = new Element();
  context.renderBrief(
    report,
    "# Specific finding\nAs of today\nA one-sentence takeaway.\n\n## At a glance\n- A key fact.\n\n## Key developments\n1. **A headline** Context [1]\n\n## Why it matters\nAn implication.\n\n## Sources\n[1]: https://example.com/report",
  );
  const reportNodes = flatten(report);
  assert(reportNodes.some((node) => node.className === "standfirst"));
  assert(
    reportNodes.some((node) => node.className.includes("summary-section")),
  );
  assert(
    reportNodes.some((node) => node.className.includes("developments-section")),
  );
  assert(
    reportNodes.some(
      (node) =>
        node.tagName === "A" && node.href === "https://example.com/report",
    ),
  );
  context.logActivity({ type: "request_start", message: "New request" });
  context.logActivity({
    type: "tool_start",
    server: "tavily",
    tool: "tavily_search",
    message: "Search",
  });
  context.logActivity({
    type: "tool_error",
    server: "tavily",
    tool: "tavily_search",
    message: "Failed",
  });
  context.logActivity({
    type: "response",
    message: "A response with limitations",
    response: "Search failed.",
  });
  assert.match(element("live-tags").children[0].className, /failed/);
  assert.doesNotMatch(element("live-tags").children[0].className, /done/);
  console.log(
    "PASS: report hierarchy, reference links, weather sections, and honest live activity states",
  );

  let outgoing;
  context.fetch = async (url, options) => {
    if (url === "/mcp/status")
      return { ok: true, json: async () => ({ servers: [] }) };
    outgoing = JSON.parse(options.body);
    return new Response(
      JSON.stringify({
        type: "response",
        message: "Ready",
        response: "# Briefing\nA concise result.",
      }) + "\n",
    );
  };
  await context.submitRequest(news, "Europe politics briefing", false);
  const firstSession = outgoing.session_id;
  assert.equal(outgoing.query, news);
  assert.equal(element("copy-briefing").disabled, false);
  assert.equal(element("follow-ups").hidden, false);
  await context.submitRequest(
    "Explain the implications",
    "Explain the implications",
    false,
  );
  assert.equal(outgoing.session_id, firstSession);
  element("new-chat").listeners.click();
  await context.submitRequest("New briefing", "New briefing", false);
  assert.notEqual(outgoing.session_id, firstSession);
  console.log(
    "PASS: generation uses existing streaming API, follow-ups reuse memory, and reset changes session",
  );

  let copied, downloaded, downloadLink;
  context.navigator = {
    clipboard: {
      writeText: async (value) => {
        copied = value;
      },
    },
  };
  context.Blob = Blob;
  context.URL = class extends URL {
    static createObjectURL(blob) {
      downloaded = blob;
      return "blob:test-download";
    }
    static revokeObjectURL() {}
  };
  context.setTimeout = (callback) => callback();
  context.document.createElement = (tag) => {
    const node = new Element(tag);
    if (tag === "a") downloadLink = node;
    return node;
  };
  await element("copy-briefing").listeners.click();
  element("download-briefing").listeners.click();
  assert.equal(copied, "# Briefing\nA concise result.");
  assert.equal(await downloaded.text(), copied);
  assert.equal(downloadLink.clicked, true);
  assert.match(downloadLink.download, /^briefing-.*\.txt$/);
  element("follow-save").listeners.click();
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(outgoing.query, /using the filesystem tool/);
  assert.match(outgoing.query, /Confirm success only if the tool succeeds/);
  console.log(
    "PASS: copy/download preserve response text and workspace save is an explicit tool request",
  );

  outgoing = undefined;
  element("example-tech").listeners.click();
  assert.match(
    element("query").value,
    /Give me a briefing on this week's artificial intelligence/,
  );
  assert.equal(
    outgoing,
    undefined,
    "Choosing an example must not send a request",
  );
  element("query").value += " Focus on Europe.";
  const edited = element("query").value;
  element("chat-form").listeners.submit({ preventDefault() {} });
  await new Promise((resolve) => setImmediate(resolve));
  assert.match(outgoing.query, /Focus on Europe/);
  assert.match(outgoing.query, /at most 3 search calls/);
  assert(outgoing.query.startsWith(edited));
  console.log(
    "PASS: examples prefill editable text without sending; submit uses the edited prompt",
  );
  for (const id of ["example-politics", "example-weather"]) {
    outgoing = undefined;
    element(id).listeners.click();
    assert.match(element("query").value, /briefing/);
    assert.equal(outgoing, undefined);
  }
  outgoing = undefined;
  element("query").value = " ";
  element("chat-form").listeners.submit({ preventDefault() {} });
  assert.equal(outgoing, undefined);
  console.log(
    "PASS: all examples prefill briefing prompts and empty chat input is not submitted",
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
