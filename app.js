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
  historyList: document.querySelector("#history-list"),
  featuredPaper: document.querySelector("#featured-paper"),
  resultCount: document.querySelector("#result-count"),
  reportStatus: document.querySelector("#report-status"),
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
    `<option value="${escapeHtml(item.date)}">${escapeHtml(formatDate(item.date))} · ${escapeHtml(item.article_count)}</option>`
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

function sourceSummary(metadata) {
  const labels = {
    crossref: "Crossref",
    europepmc: "Europe PMC",
    semanticscholar: "Semantic Scholar",
    openalex: "OpenAlex",
    biorxiv: "bioRxiv",
  };
  return Object.entries(metadata.source_counts || {})
    .filter(([, count]) => Number(count) > 0)
    .map(([name, count]) => `${labels[name] || name} ${count}`)
    .join(" · ") || "—";
}

function evidenceStatus(article) {
  const needsVerification = Array.isArray(article.needs_verification) ? article.needs_verification : [];
  if (needsVerification.length) {
    return `<span class="evidence-status needs-review" title="仍需核实：${escapeHtml(needsVerification.join("；"))}">待核实</span>`;
  }
  if (article.score_status === "evidence_reviewed") {
    return `<span class="evidence-status reviewed" title="摘要、DOI 与可靠来源已复核">已复核</span>`;
  }
  return `<span class="evidence-status" title="当前内容主要依据公开摘要">摘要依据</span>`;
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
  const pendingCount = articles.filter((article) => Array.isArray(article.needs_verification) && article.needs_verification.length > 0).length;
  const reviewedLabel = pendingCount ? `${articles.length - pendingCount} 已复核 · ${pendingCount} 待核实` : "本期均已复核";
  const candidatePath = [metadata.retrieved_count, metadata.screened_count, articles.length]
    .map((value) => value ?? "—")
    .join(" → ");
  const stats = [
    ["数据状态", reviewedLabel],
    ["候选路径", candidatePath],
    ["最高分", `${topScore} / 100`],
    ["检索窗口", windowSummary],
    ["来源", sourceSummary(metadata)],
  ];
  const warnings = Array.isArray(metadata.warnings) ? metadata.warnings : [];
  elements.appendixStats.innerHTML = `
    <div class="provenance-grid">${stats.map(([label, value]) => `<div class="provenance-item"><span class="provenance-label">${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`).join("")}</div>
    <p class="provenance-note">评分用于阅读排序；具体数值与结论请以原文为准。每张卡片均保留 DOI / 原文入口。</p>
    ${warnings.length ? `<details class="provenance-notes"><summary>查看本期检索说明</summary>${renderList(warnings)}</details>` : ""}
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

function renderDetails(article, extraFindings = [], englishTitle = "") {
  const content = renderDetailContent(article);
  const findingsMarkup = extraFindings.length ? `<h4>更多摘要要点</h4>${renderList(extraFindings)}` : "";
  const englishMarkup = englishTitle ? `<h4>英文题名</h4><p class="paper-title-en">${escapeHtml(englishTitle)}</p>` : "";
  if (!content && !findingsMarkup && !englishMarkup) return "";
  return `<details class="details"><summary>展开完整解读</summary><div class="details-content">${findingsMarkup}${englishMarkup}${content}</div></details>`;
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
        <div class="featured-bottom"><span class="featured-score">推荐 ${escapeHtml(score)} 分</span>${evidenceStatus(article)}<a class="featured-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">阅读原文 <span aria-hidden="true">↗</span></a></div>
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
  const findings = (article.core_findings || []).slice(0, 2);
  const extraFindings = (article.core_findings || []).slice(2);
  const tags = article.tags || [];
  const visibleTags = tags.slice(0, 3);
  const extraTagCount = Math.max(tags.length - visibleTags.length, 0);
  return `
    <article class="paper-card" role="link" tabindex="0" data-paper-href="${escapeHtml(href)}" aria-label="打开论文：${escapeHtml(title)}">
      <h3>${escapeHtml(title)}</h3>
      <div class="paper-meta"><span>${escapeHtml(article.journal || "期刊待核实")}</span><span>${escapeHtml(article.publication_date || "日期待核实")}</span><span>${escapeHtml(article.article_type || "论文")}</span></div>
      ${tags.length ? `<div class="tag-row">${visibleTags.map((tag) => `<span class="tag">${escapeHtml(tag)}</span>`).join("")}${extraTagCount ? `<span class="tag-more">+${extraTagCount}</span>` : ""}</div>` : ""}
      ${article.why_worth_reading ? `<p class="why">${escapeHtml(article.why_worth_reading)}</p>` : ""}
      ${renderList(findings, "finding-list")}
      ${renderDetails(article, extraFindings, englishTitle)}
      <div class="paper-footer"><div class="paper-footer-leading"><span class="score">${escapeHtml(score)} 分</span>${topBadge}${evidenceStatus(article)}</div><a class="paper-link" href="${escapeHtml(href)}" target="_blank" rel="noopener noreferrer">打开 DOI / 原文 ↗</a></div>
    </article>`;
}

function renderArticles() {
  const articles = filteredArticles();
  elements.resultCount.textContent = String(state.report?.articles?.length || 0);
  elements.emptyState.hidden = articles.length > 0;
  renderFeaturedArticle(articles[0]);
  elements.paperGrid.innerHTML = articles.slice(1).map(renderPaperCard).join("");
}

function renderHistory() {
  const reports = reportEntries();
  elements.historyList.innerHTML = reports.length ? reports.map((item) => {
    const active = item.date === state.selectedDate;
    return `
      <button class="history-row${active ? " active" : ""}" type="button" data-history-date="${escapeHtml(item.date)}" aria-pressed="${active}">
        <span class="history-date"><strong>${escapeHtml(formatDate(item.date))}</strong><small>${escapeHtml(item.date)}</small></span>
        <span class="history-stats"><b>${escapeHtml(item.article_count)}</b><span>精选</span><span>最高 ${escapeHtml(item.top_score ?? "—")}</span></span>
        <span class="history-action">${active ? "当前日报" : "查看"}<span aria-hidden="true">→</span></span>
      </button>`;
  }).join("") : `<p class="history-empty">暂无历史日报。</p>`;
}

function renderIdeas() {
  const ideas = state.report?.research_ideas || [];
  elements.ideasSection.hidden = ideas.length === 0;
  elements.ideasList.innerHTML = ideas.map((idea) => `
    <article class="idea">
      <p>${escapeHtml(idea)}</p>
    </article>`).join("");
}

function renderReportChrome() {
  elements.updatedAt.textContent = state.report?.published_at ? `更新于 ${new Date(state.report.published_at).toLocaleString("zh-CN")}` : "—";
  const articles = state.report?.articles || [];
  const pendingCount = articles.filter((article) => Array.isArray(article.needs_verification) && article.needs_verification.length > 0).length;
  elements.reportStatus.textContent = pendingCount ? `${pendingCount} 篇待核实` : "摘要与来源已复核";
  elements.reportStatus.classList.toggle("needs-review", pendingCount > 0);
  document.title = "Research Paper Daily";
}

function renderAll() {
  clearError();
  renderReportChrome();
  renderAppendix();
  renderTagFilters();
  renderArticles();
  renderHistory();
  renderIdeas();
}

async function loadReport(date) {
  const entry = reportEntries().find((item) => item.date === date);
  if (!entry) throw new Error(`找不到 ${date} 的日报`);
  state.selectedDate = date;
  state.report = await fetchJson(`data/${entry.path}`);
  state.query = "";
  elements.searchInput.value = "";
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
elements.historyList.addEventListener("click", (event) => {
  const target = event.target instanceof Element ? event.target.closest("[data-history-date]") : null;
  if (!target) return;
  const date = target.dataset.historyDate;
  if (!date || date === state.selectedDate) return;
  elements.dateSelect.value = date;
  loadReport(date)
    .then(() => document.querySelector("#papers")?.scrollIntoView({ behavior: "smooth", block: "start" }))
    .catch((error) => showError(`日报读取失败：${error.message}`));
});
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
