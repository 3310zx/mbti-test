---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c246678a38a94bf2e839f4ad8865f533_00521cf6ad0011f18039525400461939
    ReservedCode1: MrxFUvBt3+Q4IPkIo/qbRarldUK2jfF3udOuu5+eY7Y1ERzEH0qbcgEFkSRFF6GVjAPp8y6Ge0O8apBhsIBKb0+I/ArIEdL58xqoZGORT3xgZNat2ht1IxPB4MdUGVUvKXSHptoAsO8M3bKjLkkyQbgT/DwgT23nbPhEgWsBLmsDzH6N6hN6Z8aNcCE=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c246678a38a94bf2e839f4ad8865f533_00521cf6ad0011f18039525400461939
    ReservedCode2: MrxFUvBt3+Q4IPkIo/qbRarldUK2jfF3udOuu5+eY7Y1ERzEH0qbcgEFkSRFF6GVjAPp8y6Ge0O8apBhsIBKb0+I/ArIEdL58xqoZGORT3xgZNat2ht1IxPB4MdUGVUvKXSHptoAsO8M3bKjLkkyQbgT/DwgT23nbPhEgWsBLmsDzH6N6hN6Z8aNcCE=
---

# MBTI 认知功能测试

基于认知功能栈判定的 MBTI 测试，Material Design 3 风格，桌面 / 移动端自适应。

## 特点

- 32 道陈述题（每维度 8 题，正反陈述各半）
- 6 级程度评分（无"不确定"中间项，规避巴纳姆效应）
- 认知功能栈 + 加权计分，弱倾向维度自动提示复核
- 响应式布局，电脑 / 手机通用
- 预留 Google AdSense 广告位

## 本地预览

直接双击打开 `index.html` 即可，或运行：

```bash
python3 -m http.server 8000
# 浏览器访问 http://localhost:8000
```

## 部署到 GitHub Pages

1. 创建 GitHub 仓库（如 `mbti-test`），推入本目录文件
2. 仓库 Settings → Pages → Source 选择 `main` 分支的 `/ (root)` 目录
3. 访问 `https://<你的用户名>.github.io/mbti-test/`

## 接入 Google AdSense

编辑 `index.html` 顶部 JS 中的配置：

```javascript
var ADS_CLIENT = 'ca-pub-xxxxxxxxxxxx';  // 发布商 ID
var ADS_SLOT   = '1234567890';           // 广告单元 slot（可留空）
```

- 留空则页面不加载任何广告代码
- 广告位位于：开始页底部 / 答题页底部 / 结果页下方
- 需先通过 Google AdSense 审核，并在仓库根目录放置后台生成的 `ads.txt`
*（内容由AI生成，仅供参考）*
