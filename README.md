# 台灣親子好生活

面向台灣 0–6 歲家庭的實用內容網站。重點不是製造更多育兒焦慮，而是把可信資料整理成日常可執行的步驟與清單。

## 本地驗證

```bash
python3 -m pip install -r requirements.txt
python3 scripts/validate_content.py
bundle exec jekyll build
```

網站由 GitHub Actions 部署至 GitHub Pages。文章必須通過內容 schema、來源、圖片尺寸與授權資料檢查。

## 內容方向

12 類：幼兒飲食、作息睡眠、成長發展、健康照顧、居家安全、遊戲探索、親子共讀、情緒陪伴、托育入園、親子出遊、家庭生活、用品挑選。
