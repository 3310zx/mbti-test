# -*- coding: utf-8 -*-
"""country 站公共 head 片段与全局常量：GA4 / AdSense / 分享卡 / CSS 缓存版本 / 对比配对清单。

其它构建脚本统一从这里取，避免 66 个页面各自硬编码追踪 ID。
"""

SITE = "https://3310zx.github.io/mbti-test"

# 与主站共用同一 GA4 媒体资源（数据合并统计，无需新建资源）
GA_ID = "G-JCKX59J312"

# 与主站共用同一 AdSense 账号；广告单元沿用主站的响应式单元
ADS_CLIENT = "ca-pub-8250844529483545"
AD_SLOT = "5966315493"

# 分享卡：沿用主站 1200x630 品牌图，避免未审核期的外链图片依赖
OG_IMAGE = SITE + "/images/og-share.png"
OG_IMAGE_W, OG_IMAGE_H = 1200, 630
OG_IMAGE_ALT = "MBTI 人生地理：用世界银行数据算出最适合你生活的国家"
# 日文页树（country/ja/）用日文 alt：分享卡出现在日语搜索结果与 SNS 卡片时，
# 中文 alt 会削弱点击意愿，故按语言给两套文案。
OG_IMAGE_ALT_BY_LANG = {
    "zh": OG_IMAGE_ALT,
    "ja": "MBTI人生地理：世界銀行データから自分に合う住む国を算出",
    "en": "MBTI Life Geography: World Bank country data on where you would live best",
}

# CSS 缓存版本：改 country.css 时同步 +1
CSSV = "20261115c"


def analytics():
    """GA4 基础埋点。"""
    return (
        '<link rel="preconnect" href="https://www.googletagmanager.com">\n'
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
        '<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}'
        f"gtag('js',new Date());gtag('config','{GA_ID}',{{anonymize_ip:true}});</script>\n"
    )


def adsense_head():
    """AdSense 账号声明 + 加载器（真实广告单元由 ad_unit() 插入）。"""
    return (
        f'<meta name="google-adsense-account" content="{ADS_CLIENT}">\n'
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADS_CLIENT}"'
        ' crossorigin="anonymous"></script>\n'
    )


def ad_unit(label="广告", aria="广告"):
    """单个自适应广告单元。放在正文段落之间，不打断首屏与表格。"""
    return f"""<aside class="ad-slot" aria-label="{aria}">
  <p class="ad-label">{label}</p>
  <ins class="adsbygoogle" style="display:block" data-ad-client="{ADS_CLIENT}" data-ad-slot="{AD_SLOT}" data-ad-format="auto" data-full-width-responsive="true"></ins>
  <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>
</aside>
"""


def share_image_meta(lang="zh"):
    alt = OG_IMAGE_ALT_BY_LANG.get(lang, OG_IMAGE_ALT)
    return (
        f'<meta property="og:image" content="{OG_IMAGE}">\n'
        f'<meta property="og:image:width" content="{OG_IMAGE_W}">\n'
        f'<meta property="og:image:height" content="{OG_IMAGE_H}">\n'
        f'<meta property="og:image:alt" content="{alt}">\n'
        f'<meta name="twitter:image" content="{OG_IMAGE}">\n'
    )


# 手工挑选的长尾对比对：同区域互斥选项 + 常见移居取舍路径。
# 顺序即 /country/compare/ 页的推荐顺序；每个国家对自动生成正反同一条 URL。
PAIRS = [
    ("JPN", "KOR"), ("JPN", "THA"), ("JPN", "SGP"), ("KOR", "SGP"),
    ("THA", "VNM"), ("THA", "MYS"), ("MYS", "SGP"), ("IDN", "VNM"),
    ("JPN", "CHN"), ("HKG", "SGP"), ("HKG", "CHN"), ("CHN", "THA"),
    ("SGP", "ARE"),
    ("DEU", "NLD"), ("DEU", "AUT"), ("CHE", "AUT"), ("CHE", "DEU"),
    ("PRT", "ESP"), ("ESP", "ITA"), ("PRT", "GRC"), ("NLD", "BEL"),
    ("IRL", "GBR"), ("GBR", "FRA"), ("FRA", "ITA"),
    ("NOR", "SWE"), ("SWE", "DNK"), ("DNK", "FIN"), ("FIN", "NOR"), ("ISL", "NOR"),
    ("CZE", "POL"), ("HUN", "POL"), ("CZE", "AUT"), ("HRV", "SRB"),
    ("EST", "FIN"), ("ROU", "POL"), ("TUR", "GEO"), ("GRC", "TUR"),
    ("USA", "CAN"), ("AUS", "NZL"), ("AUS", "CAN"), ("CAN", "GBR"), ("NZL", "IRL"),
    ("CHL", "URY"), ("BRA", "ARG"), ("ESP", "MEX"), ("PRT", "BRA"),
    ("ARE", "ISR"), ("MAR", "EGY"), ("IND", "THA"),
]


def pair_slug(a, b):
    return f"{a.lower()}-vs-{b.lower()}"


def pair_url(a, b, prefix="../../"):
    return f"{prefix}compare/{pair_slug(a, b)}/"


def pairs_for(iso):
    """返回所有包含该国的配对，顺序稳定。"""
    return [(a, b) for a, b in PAIRS if iso in (a, b)]
