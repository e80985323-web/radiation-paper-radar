# Radiation Paper Radar

面向辐射探测、闪烁体、半导体探测器、中子/伽马/X 射线探测、能谱、标定、成像和读出的公开文献雷达。

## 本地预览

在仓库根目录运行：

```powershell
python -m http.server 8000
```

然后打开 <http://localhost:8000/>。不要直接双击 `index.html`，因为浏览器会阻止 `fetch()` 读取本地 JSON。

## 写入一份新的公开日报

把本地 `research-paper-daily-push` skill 生成的 `reviewed_articles.json` 传给公开数据构建脚本：

```powershell
python scripts/build_public_data.py `
  --input "C:\path\to\reviewed_articles.json" `
  --site-root .
```

脚本只写入 `data/reports/YYYY-MM-DD.json` 和 `data/index.json`。它不复制 Zotero PDF、本地路径、研究画像或通知凭据。

## GitHub Pages

仓库包含 `.github/workflows/deploy-pages.yml`。在 GitHub 的 **Settings → Pages** 中将 **Source** 设置为 **GitHub Actions**，之后推送到 `main` 就会自动部署。

## 公开内容边界

页面只展示经过复核的精炼中文总结、评分、标签、术语解释、研究启发以及 DOI/原文链接。论文全文、个人笔记、私人研究画像和任何 Token/UID 不应提交到这个公开仓库。
