const state = {
  index: null,
  report: null,
  selectedDate: null,
  query: "",
  activeTag: "全部",
};

const elements = {
  dateSelect: document.querySelector("#date-select"),
  searchInput: document.querySelector("#search-input"),
  topicMenu: document.querySelector("#topic-menu"),
  topicCurrent: document.querySelector("#topic-current"),
  tagFilters: document.querySelector("#tag-filters"),
  tagPreview: document.querySelector("#tag-preview"),
  resetButton: document.querySelector("#reset-button"),
  appendixStats: document.querySelector("#appendix-stats"),
  featuredPaper: document.querySelector("#featured-paper"),
  resultCount: document.querySelector("#result-count"),
  paperGrid: document.querySelector("#paper-grid"),
  emptyState: document.querySelector("#empty-state"),
  ideasSection: document.querySelector("#ideas-section"),
  ideasList: document.querySelector("#ideas-list"),
  updatedAt: document.querySelector("#updated-at"),
  errorBanner: document.querySelector("#error-banner"),
};

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function safeHref(value) {
  const text = String(value ?? "");
  return /^https?:\/\//i.test(text) ? text : "#";
}

function openPaperLink(href) {
  const target = safeHref(href);
  if (target === "#") return;
  window.location.assign(target);
}

function bindCardNavigation(container) {
  container.addEventListener("click", (event) => {
    const target = event.target instanceof Element ? event.target : null;
    const card = target?.closest(".featured-card, .paper-card");
    if (!card || !container.contains(card) || target.closest("a, button, summary, details")) return;
    openPaperLink(card.dataset.paperHref);
  });
  container.addEventListener("keydown", (event) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    const card = event.target instanceof Element ? event.target.closest(".featured-card, .paper-card") : null;
    if (!card || event.target !== card || !container.contains(card)) return;
    event.preventDefault();
    openPaperLink(card.dataset.paperHref);
  });
}

function formatDate(dateText) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(dateText || "")) return dateText || "—";
  const date = new Date(`${dateText}T00:00:00+08:00`);
  return new Intl.DateTimeFormat("zh-CN", { year: "numeric", month: "long", day: "numeric" }).format(date);
}

function showError(message) {
  elements.errorBanner.hidden = false;
  elements.errorBanner.textContent = message;
}

function clearError() {
  elements.errorBanner.hidden = true;
  elements.errorBanner.textContent = "";
}

async function fetchJson(path) {
  const response = await fetch(`./${path}`, { cache: "no-store" });
  if (!response.ok) throw new Error(`${path} (${response.status})`);
  return response.json();
}

function reportEntries() {
  return Array.isArray(state.index?.reports) ? state.index.reports : [];
}

function setupDateSelect() {
  const reports = reportEntries();
  elements.dateSelect.innerHTML = reports.map((item) => (
    `<option value="${escapeHtml(item.date)}">${escapeHtml(formatDate(item.date))} · ${escapeHtml(item.article_count)} 篇</option>`
  )).join("");
  state.selectedDate = state.index?.latest_date || reports[0]?.date || null;
  elements.dateSelect.value = state.selectedDate || "";
}

function allTags() {
  const tags = new Set();
  for (const article of state.report?.articles || []) {
    for (const tag of article.tags || []) tags.add(tag);
  }
  return ["全部", ...Array.from(tags).sort((a, b) => a.localeCompare(b, "zh-CN"))];
}

function renderTagFilters() {
  const tags = allTags();
  const buttonMarkup = (tag, className) => (
    `<button class="${className} ${tag === state.activeTag ? "active" : ""}" type="button" data-tag="${escapeHtml(tag)}" aria-pressed="${tag === state.activeTag}">${escapeHtml(tag)}</button>`
  );
  const selectTag = (event) => {
    state.activeTag = event.currentTarget.dataset.tag || "全部";
    elements.topicMenu.open = false;
    renderTagFilters();
    renderArticles();
    document.querySelector("#papers")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };
  elements.topicCurrent.textContent = state.activeTag;
  elements.tagFilters.innerHTML = tags.map((tag) => buttonMarkup(tag, "tag-filter")).join("");
  elements.tagPreview.innerHTML = tags.slice(1, 6).map((tag) => buttonMarkup(tag, "topic-preview-filter")).join("");
  elements.tagFilters.querySelectorAll("[data-tag]").forEach((button) => button.addEventListener("click", selectTag));
  elements.tagPreview.querySelectorAll("[data-tag]").forEach((button) => button.addEventListener("click", selectTag));
}

function reportMetadata() {
  return state.report?.metadata || {};
}

function summarizeWindow(windowText) {
  const text = String(windowText || "");
  if (!text) return "—";
  if (text.includes("最近7天")) return "近 7 日 · 自动扩展";
  if (text.includes("近24小时")) return "近 24 小时优先";
  return text;
}

function renderAppendix() {
  const metadata = reportMetadata();
  const articles = state.report?.articles || [];
  const topScore = Math.max(...articles.map((item) => Number(item.recommendation_score) || 0), 0);
  const windowText = metadata.window || "";
  const windowSummary = summarizeWindow(windowText);
  const stats = [
    ["最终精选", `${articles.length} 篇`],
    ["最高推荐分", `${topScore} / 100`],
    ["候选筛选", `${metadata.screened_count ?? "—"} 篇`],
    ["本期检索范围", windowSummary],
  ];
  elements.appendixStats.innerHTML = `
    <p class="appendix-summary">${stats.map(([label, value]) => `<span><b>${escapeHtml(label)}</b> ${escapeHtml(value)}</span>`).join("")}</p>
    ${windowText && windowText !== windowSummary ? `<p class="appendix-detail">完整说明：${escapeHtml(windowText)}</p>` : ""}
  `;
}

function searchableText(article) {
  return [
    article.title,
    article.chinese_title,
    article.journal,
    article.why_worth_reading,
    ...(article.tags || []),
    ...(article.core_findings || []),
  ].join(" ").toLocaleLowerCase("zh-CN");
}

function paperVisualVariant(article) {
  const tags = (article.tags || []).join(" ");
  if (/符合测量/.test(tags)) return "coincidence";
  if (/读出电子学|SiPM/.test(tags)) return "readout";
  if (/半导体探测器|异质结|钙钛矿|硅探测器/.test(tags)) return "semiconductor";
  if (/标定|校正|响应|栅格/.test(tags)) return "calibration";
  if (/成像|微通道|闪烁屏|X射线/.test(tags)) return "imaging";
  if (/闪烁体/.test(tags)) return "scintillator";
  return "detector";
}

function renderPaperVisual(article) {
  const variant = paperVisualVariant(article);
  const drawings = {
    imaging: `
      <svg viewBox="0 0 120 88" focusable="false">
        <rect class="art-stroke" x="14" y="12" width="46" height="60" rx="6"></rect>
        <path class="art-faint" d="M20 60 29 49l9 7 10-19 7 10"></path>
        <circle class="art-accent-fill" cx="48" cy="36" r="3"></circle>
        <path class="art-stroke" d="M76 24h28M76 33h20M76 42h13"></path>
        <path class="art-accent-line" d="M76 58c6-8 12-8 18 0s12 8 18 0"></path>
        <path class="art-faint" d="M78 65h24"></path>
      </svg>`,
    semiconductor: `
      <svg viewBox="0 0 120 88" focusable="false">
        <rect class="art-stroke" x="12" y="16" width="46" height="55" rx="6"></rect>
        <path class="art-faint" d="M24 16v55M36 16v55M48 16v55M12 29h46M12 42h46M12 55h46"></path>
        <circle class="art-accent-fill" cx="24" cy="29" r="3"></circle>
        <circle class="art-accent-fill" cx="48" cy="55" r="3"></circle>
        <path class="art-accent-line" d="M77 21v45M70 29l7-8 7 8M70 57l7 9 7-9"></path>
        <path class="art-stroke" d="M88 28h19M88 44h13M88 59h19"></path>
      </svg>`,
    calibration: `
      <svg viewBox="0 0 120 88" focusable="false">
        <path class="art-stroke" d="M16 69V15M16 69h91"></path>
        <path class="art-faint" d="M29 69V23M43 69V23M57 69V23M71 69V23M85 69V23M99 69V23"></path>
        <path class="art-accent-line" d="M19 60c12-4 17-22 28-19 10 3 12 14 20 8 10-8 16-26 37-30"></path>
        <circle class="art-accent-fill" cx="67" cy="49" r="3"></circle>
        <path class="art-stroke" d="M83 19h20v20M103 19 83 39"></path>
      </svg>`,
    coincidence: `
      <svg viewBox="0 0 120 88" focusable="false">
        <rect class="art-stroke" x="13" y="16" width="29" height="18" rx="4"></rect>
        <rect class="art-stroke" x="13" y="54" width="29" height="18" rx="4"></rect>
        <path class="art-faint" d="M49 25h56M49 63h56"></path>
        <path class="art-accent-line" d="M51 25h10l4-9 7 19 6-10h18M51 63h10l4-9 7 19 6-10h18"></path>
        <path class="art-stroke" d="M88 14v60"></path>
        <path class="art-accent-line" d="M88 35v18"></path>
        <circle class="art-accent-fill" cx="88" cy="44" r="3"></circle>
      </svg>`,
    readout: `
      <svg viewBox="0 0 120 88" focusable="false">
        <rect class="art-stroke" x="12" y="19" width="35" height="49" rx="6"></rect>
        <circle class="art-accent-fill" cx="23" cy="31" r="2.7"></circle>
        <circle class="art-accent-fill" cx="35" cy="43" r="2.7"></circle>
        <circle class="art-accent-fill" cx="23" cy="55" r="2.7"></circle>
        <path class="art-faint" d="M50 31h11M50 43h11M50 55h11"></path>
        <path class="art-stroke" d="M61 31h8l5 10 6-20 7 36 6-18h11"></path>
        <path class="art-accent-line" d="M61 55h13"></path>
        <circle class="art-accent-fill" cx="102" cy="39" r="3"></circle>
      </svg>`,
    scintillator: `
      <svg viewBox="0 0 120 88" focusable="false">
        <path class="art-stroke" d="m18 25 21-9 19 11-21 10zM18 25v28l19 12V37M58 27v28L37 65"></path>
        <path class="art-accent-line" d="M72 20c8 8-5 14 5 23 8 7-2 13 6 23"></path>
        <path class="art-accent-line" d="M91 18c-5 6 5 10 0 16M103 31c-6 6 5 11-1 18"></path>
        <circle class="art-accent-fill" cx="76" cy="43" r="3"></circle>
        <path class="art-faint" d="M69 70h36"></path>
      </svg>`,
    detector: `
      <svg viewBox="0 0 120 88" focusable="false">
        <circle class="art-stroke" cx="43" cy="44" r="27"></circle>
        <circle class="art-faint" cx="43" cy="44" r="17"></circle>
        <circle class="art-accent-fill" cx="43" cy="44" r="4"></circle>
        <path class="art-accent-line" d="M75 21h28M75 44h19M75 67h28"></path>
        <circle class="art-accent-fill" cx="75" cy="21" r="3"></circle>
        <circle class="art-accent-fill" cx="94" cy="44" r="3"></circle>
      </svg>`,
  };
  return `<div class="paper-art paper-art-${variant}" aria-hidden="true">${drawings[variant]}</div>`;
}

function filteredArticles() {
  const query = state.query.trim().toLocaleLowerCase("zh-CN");
  return (state.report?.articles || []).filter((article) => {
    const tagMatch = state.activeTag === "全部" || (article.tags || []).includes(state.activeTag);
    const queryMatch = !query || searchableText(article).includes(query);
    return tagMatch && queryMatch;
  });
}

function renderList(items, className = "") {
  if (!items?.length) return "";
  return `<ul class="${className}">${items.map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderDetailContent(article) {
  const terms = article.term_explanations || [];
  const inspiration = article.research_inspiration || {};
  const hasInspiration = Object.keys(inspiration).length > 0;
  if (!terms.length && !hasInspiration) return "";
  const termMarkup = terms.length ? `
    <h4>术语双重解释</h4>
    ${terms.map((term) => `<div class="term"><strong>${escapeHtml(term.term)}</strong><p><em>学术：</em>${escapeHtml(term.academic_explanation)}</p><p><em>大白话：</em>${escapeHtml(term.plain_explanation)}</p></div>`).join("")}
  ` : "";
  const inspirationLabels = {
    experimental_design: "实验设计",
    methods: "方法借鉴",
    key_entities_mechanisms: "关键对象与机制",
    target_system: "目标体系",
    future_direction: "未来方向",
    paper_potential: "论文潜力",
    limitations_validation: "局限与验证",
  };
  const inspirationMarkup = hasInspiration ? `
    <h4>研究启发</h4>
    ${Object.entries(inspiration).map(([key, values]) => `<p><strong>${escapeHtml(inspirationLabels[key] || key)}</strong></p>${renderList(values)}`).join("")}
  ` : "";
  return `${termMarkup}${inspirationMarkup}`;
}

function renderDetails(article) {
  const content = renderDetailContent(article);
  if (!content) return "";
  return `<details class="details"><summary>展开术语解释与研究启发</summary><div class="details-content">${content}</div></details>`;
}

function renderFeaturedDetails(article) {
  const findings = (article.core_findings || []).slice(0, 3);
  const content = renderDetailContent(article);
  if (!findings.length && !content) return "";
  return `
    <details class="featured-details">
      <summary>展开摘要要点、术语解释与研究启发</summary>
      <div class="featured-details-content">
        ${findings.length ? `<section class="featured-detail-group"><h4>摘要要点</h4>${renderList(findings, "featured-finding-list")}</section>` : ""}
        ${content}
      </div>
    </details>`;
}

function renderFeaturedArticle(article) {
  if (!article) {
    elements.featuredPaper.hidden = true;
    elements.featuredPaper.innerHTML = "";
    return;
  }
  const score = Number(article.recommendation_score) || 0;
  const href = safeHref(article.url);
  const title = article.chinese_title || article.title || "未命名论文";
  const summary = article.why_worth_reading || article.core_findings?.[0] || "暂无摘要说明。";
  const journal = article.journal || "期刊待核实";
  const date = article.publication_date || "日期待核实";
  elements.featuredPaper.hidden = false;
  elements.featuredPaper.innerHTML = `
    <article class="featured-card" role="link" tabindex="0" data-paper-href="${escapeHtml(href)}" aria-label="打开论文：${escapeHtml(title)}">
      <div class="featured-copy">
        <h3>${escapeHtml(title)}</h3>
        <p class="featured-summary">${escapeHtml(summary)}</p>
        ${renderFeaturedDetails(article)}
        <div class="featured-meta"><span>${escapeHtml(journal)}</span><span>${escapeHtml(date)}</span><span>${escapeHtml(article.article_type || "论文")}</span></div>
        <div class="featured-bottom"><span class="featured-score">推荐 ${escapeHtml(score)} 分</span><a class="featured-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">阅读原文 <span aria-hidden="true">↗</span></a></div>
      </div>
      <div class="featured-visual" aria-hidden="true">
        <div class="detector-graphic"><span class="detector-core"></span><span class="detector-node node-a"></span><span class="detector-node node-b"></span><span class="detector-node node-c"></span></div>
      </div>
    </article>`;
}

function renderPaperCard(article) {
  const score = Number(article.recommendation_score) || 0;
  const href = safeHref(article.url);
  const title = article.chinese_title || article.title || "未命名论文";
  const englishTitle = article.title && article.title !== title ? article.title : "";
  const topBadge = article.top3_reason ? `<span class="top-badge">重点推荐</span>` : "";
  const findings = (article.core_findings || []).slice(0, 3);
  return `
    <article class="paper-card" role="link" tabindex="0" data-paper-href="${escapeHtml(href)}" aria-label="打开论文：${escapeHtml(title)}">
      <div class="paper-topline"><span class="score">${escapeHtml(score)} 分</span></div>
      <div class="paper-card-intro">
        <div class="paper-card-copy">
          <h3>${escapeHtml(title)}</h3>
          ${englishTitle ? `<div class="paper-title-en">${escapeHtml(englishTitle)}</div>` : ""}
        </div>
        ${renderPaperVisual(article)}
      </div>
      <div class="paper-meta"><span>${escapeHtml(article.journal || "期刊待核实")}</span><span>${escapeHtml(article.publication_date || "日期待核实")}</span><span>${escapeHtml(article.article_type || "论文")}</span></div>
      <div class="tag-row">${(article.tags || []).map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}</div>
      ${article.why_worth_reading ? `<p class="why">${escapeHtml(article.why_worth_reading)}</p>` : ""}
      ${renderList(findings, "finding-list")}
      ${renderDetails(article)}
      <div class="paper-footer">${topBadge}<a class="paper-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">打开 DOI / 原文 ↗</a></div>
    </article>`;
}

function renderArticles() {
  const articles = filteredArticles();
  elements.resultCount.textContent = String(state.report?.articles?.length || 0);
  elements.emptyState.hidden = articles.length > 0;
  renderFeaturedArticle(articles[0]);
  elements.paperGrid.innerHTML = articles.slice(1).map(renderPaperCard).join("");
}

function renderIdeas() {
  const ideas = state.report?.research_ideas || [];
  elements.ideasSection.hidden = ideas.length === 0;
  elements.ideasList.innerHTML = ideas.map((idea, index) => `<div class="idea"><span class="idea-number">0${index + 1}</span>${escapeHtml(idea)}</div>`).join("");
}

function renderReportChrome() {
  const date = state.report?.date || state.selectedDate;
  elements.updatedAt.textContent = state.report?.published_at ? `更新于 ${new Date(state.report.published_at).toLocaleString("zh-CN")}` : "—";
  document.title = date ? `${formatDate(date)} · Research Paper Daily` : "Research Paper Daily";
}

function renderAll() {
  clearError();
  renderReportChrome();
  renderAppendix();
  renderTagFilters();
  renderArticles();
  renderIdeas();
}

async function loadReport(date) {
  const entry = reportEntries().find((item) => item.date === date);
  if (!entry) throw new Error(`找不到 ${date} 的日报`);
  state.selectedDate = date;
  state.report = await fetchJson(`data/${entry.path}`);
  state.activeTag = "全部";
  renderAll();
}

async function start() {
  try {
    state.index = await fetchJson("data/index.json");
    setupDateSelect();
    if (!state.selectedDate) {
      showError("还没有可展示的日报，请先运行一次公开数据构建脚本。");
      return;
    }
    await loadReport(state.selectedDate);
  } catch (error) {
    showError(`日报读取失败：${error.message}。请确认站点已包含 data/index.json，并通过 HTTP 服务访问。`);
  }
}

elements.dateSelect.addEventListener("change", () => loadReport(elements.dateSelect.value).catch((error) => showError(`日报读取失败：${error.message}`)));
elements.searchInput.addEventListener("input", (event) => {
  state.query = event.target.value || "";
  renderArticles();
});
elements.resetButton.addEventListener("click", () => {
  state.query = "";
  state.activeTag = "全部";
  elements.searchInput.value = "";
  renderTagFilters();
  renderArticles();
});

bindCardNavigation(elements.featuredPaper);
bindCardNavigation(elements.paperGrid);

start();
