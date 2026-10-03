---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c246678a38a94bf2e839f4ad8865f533_6d4cc89ab0d211f18039525400461939
    ReservedCode1: YSZPh20+SxUbujyUMWnCg3tE6wiSPsrcFzwT7GWiVynIZ8Ga72rE4PTkaS0mKYTIoipUB+IAmaiQRHsXdbKRuMac++vY5Fvq5D0pofgXPD9n1uPbLUylo1H7lQkCVbNc0hS86g+uEAKAUpOtXg9Wnv9HGfVlzb9E1xc/PGL90mKzmDWhOZ7bslEb/jA=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c246678a38a94bf2e839f4ad8865f533_6d4cc89ab0d211f18039525400461939
    ReservedCode2: YSZPh20+SxUbujyUMWnCg3tE6wiSPsrcFzwT7GWiVynIZ8Ga72rE4PTkaS0mKYTIoipUB+IAmaiQRHsXdbKRuMac++vY5Fvq5D0pofgXPD9n1uPbLUylo1H7lQkCVbNc0hS86g+uEAKAUpOtXg9Wnv9HGfVlzb9E1xc/PGL90mKzmDWhOZ7bslEb/jA=
---

# 更新日志

## [2026-09-15] AdSense 网站审核整改（commit 2b9062b）

### 背景
站点 `3310zx.github.io/mbti-test` 接入 Google AdSense 后，网站审核被拒，后台提示违规：
「在不包含发布商内容的屏幕上展示 Google 投放的广告」。

本次整改目标：消除违规广告位，补齐合规文件，重新提交审核。

### 改动明细

#### 1. 删除旧版违规页面（主要整改项）
- 删除嵌套旧版目录 `mbti-site/`（含 3 个广告位：开始页、答题页、结果页）
- 该旧版页面答题页广告在隐藏空容器（`display:none`）上发起广告请求，是审核抓到的核心违规源
- 删除后线上访问 `/mbti-test/mbti-site/` 返回 404

#### 2. 删除重复页面
- 删除 `mbti_test.html`（与 `index.html` 内容完全一致，md5 相同）
- 避免两个 URL 相同内容被判定为重复低价值页面
- 删除后线上访问 `/mbti-test/mbti_test.html` 返回 404

#### 3. 优化广告注入时机
- 修改 `index.html`：
  - 原逻辑：页面加载时即调用 `initAds()`，对初始隐藏的结果页容器注入广告并 `adsbygoogle.push`
  - 新逻辑：仅在结果页真正显示时（`showResult()` 内）调用 `initAds()`，广告位可见且有内容后才发起广告请求
- 当前线上仅保留 1 个广告位：结果页内容之后的 `#ad-result`

#### 4. 新增 ads.txt
- 在仓库根目录新增 `ads.txt`，内容为 AdSense 标准授权行：
  `google.com, pub-8250844529483545, DIRECT, f08c47fec0942fa0`
- 满足「广告资源的授权卖方」政策要求

#### 5. 替换隐私政策占位邮箱
- 修改 `privacy.html`：将占位假邮箱 `support@example.com` 替换为真实联系邮箱 `xiangyinlu601@gmail.com`
- 满足隐私披露要求真实联系方式

### 线上验证结果（部署后实测）
| 检查项 | 结果 |
|---|---|
| 主页 `/mbti-test/` | 200 正常 |
| `/mbti-test/mbti-site/` | 404（已删除） |
| `/mbti-test/mbti_test.html` | 404（已删除） |
| `/mbti-test/ads.txt` | 200，内容正确 |
| `/mbti-test/privacy.html` | 已显示真实邮箱 |

### 后续待办
- 回到 AdSense 后台，勾选「我已确认已解决相关问题」，点击「申请审核」
- 审核期间留意邮箱 `xiangyinlu601@gmail.com` 的通知
- 审核通过后需完成：PIN 验证、W-8BEN 税务表、招行收款账户绑定
*（内容由AI生成，仅供参考）*

## [2026-09-19/20] 高需求朋友测试页上线与白天黑夜切换（commit c42e6e4、20a04b4）

### 背景
为满足「帮朋友测」的场景，上线高需求测试页 `high-need-test/`：采用两阶段流程降低答题成本（前 25 题快速筛查，达标后进入完整分类），并支持手动白天黑夜主题切换（跟随系统 + localStorage 记忆），适配不同使用环境。

### 改动明细

#### 1. 高需求测试页上线（commit c42e6e4）
- 新增 `high-need-test/` 页面，独立于主页的完整 16 类型流程
- 两阶段设计：
  - 阶段一：前 25 题筛查，得分 ≥50% 进入阶段二类型分类
  - 得分 <50% 时直接输出结果，不进入完整分类
- 复用站点主题与结果展示样式

#### 2. 手动白天黑夜切换（commit 20a04b4）
- `high-need-test` 支持手动切换白天/黑夜主题
- 默认跟随系统主题，手动选择后通过 localStorage 记忆，下次访问保持用户选择

### 线上验证结果
| 检查项 | 结果 |
|---|---|
| `/mbti-test/high-need-test/` | 200 正常，两阶段流程可用 |
| 主题切换 | 刷新后保持（localStorage） |

## [2026-09-20] SEO/OG 优化上线（commit 73a12fb）

### 背景
提升站点在搜索引擎与社交平台（微信/微博等）的展示效果：补齐分享卡片、搜索结构化数据与流量统计，并对体积过大的头像做压缩，加快页面加载。

### 改动明细

#### 1. og:image 分享卡片
- 全站页面（含 16 类型页）补齐 og:image 系列标签，社交分享时展示正确预览图

#### 2. 首页与高需求测试页互链
- 首页增加高需求测试入口，两页互相链接，形成内链闭环

#### 3. 16 类型页 FAQPage schema
- 每页补充 FAQPage JSON-LD 结构化数据（每页 2-3 个问答），利于搜索引擎富摘要展示

#### 4. high-need-test 补 gtag
- 高需求测试页接入 Google Analytics（gtag），完善流量统计

#### 5. 头像压缩
| 头像 | 压缩前 | 压缩后 |
|---|---|---|
| ESTJ | 111KB | 48KB |
| ENTP | 275KB | 47KB |

### 线上验证结果
- 各页面源码可见 og:image / FAQPage JSON-LD 标签
- 头像加载体积明显下降

## [2026-10-03] 首页 BGM 播放器上线（commit 5655b1b）

### 背景
为提升首页浏览氛围，在 footer 上方加入 BGM 播放器卡片，内置 3 首 Cognitive 系列轻音乐，用户可手动开启。

### 改动明细
- 首页 footer 上方新增 BGM 播放器卡片
- 内置 3 首 MP3（`assets/bgm/`）：cognitive-blue.mp3、cognitive-blue-female-vocal.mp3、cognitive-sax.mp3
- 默认不自动播放，避免打扰用户
- 支持循环播放与上一首/下一首切歌
- 默认音量 0.6
- 播放器关键元素 id：bgmAudio、bgmToggle、bgmPrev、bgmNext

### 线上验证结果
- 首页出现 BGM 卡片，播放/暂停/切歌/循环正常

## [2026-10-03] ADHD 专注模式自动暂停 BGM（commit c266e1c）

### 背景
ADHD 专注模式开启后，背景音乐可能干扰专注；开启 ADHD 时自动暂停正在播放的 BGM，并同步按钮文字。

### 改动明细
- 在 `toggleAdhd()` 开启分支（`index.html` 约 3202-3223 行 ADHD IIFE 内）增加逻辑：
  - 开启 ADHD 时，若 BGM 正在播放则调用 `bgmAudio.pause()` 暂停
  - 同步将 BGM 按钮文字改为「播放」
  - 不自动恢复播放（避免破坏专注状态）
- 直接操作 bgmAudio/bgmToggle，不依赖 BGM 内部状态

### 线上验证结果
- 开启 ADHD 后 BGM 立即暂停且按钮文字同步；关闭后需用户手动恢复播放
