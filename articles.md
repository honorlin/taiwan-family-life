---
layout: default
title: 最新文章
permalink: /articles/
description: 台灣 0–6 歲育兒實用文章與清單
---
<section class="page-hero"><div class="wrap"><p class="eyebrow"><span></span>親子生活知識庫</p><h1>把育兒難題，拆成做得到的小步驟</h1><p class="lead">台灣情境、可靠來源、清楚界線。先找到你今天最需要的一篇。</p></div></section><section><div class="wrap"><div class="article-grid">{% for post in site.posts %}<article class="article-card" id="{{ post.category }}"><a class="article-image" href="{{ post.url | relative_url }}"><img src="{{ post.image | relative_url }}" alt="{{ post.image_alt | escape }}" width="1200" height="630" loading="lazy"></a><div class="article-body"><span class="article-category">{{ post.category_name }}</span><h2><a href="{{ post.url | relative_url }}">{{ post.title }}</a></h2><p>{{ post.description }}</p><div class="article-meta"><time>{{ post.date | date: "%Y年%m月%d日" }}</time><a href="{{ post.url | relative_url }}">閱讀 →</a></div></div></article>{% endfor %}</div></div></section>
