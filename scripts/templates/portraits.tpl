<!DOCTYPE html>
<html lang="zh-CN">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JCKX59J312"></script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" crossorigin="anonymous"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-JCKX59J312');
</script>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{{TITLE}}</title>
<meta name="description" content="{{DESC}}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{{CANONICAL}}">
{{HREFLANG}}
<meta property="og:type" content="article">
<meta property="og:site_name" content="MBTI 认知功能测试">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESC}}">
<meta property="og:url" content="{{CANONICAL}}">
<meta property="og:locale" content="{{OG_LOCALE}}">
<meta property="og:image" content="{{OG_IMAGE}}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{{TITLE}}">
<meta name="twitter:description" content="{{DESC}}">
<meta name="twitter:image" content="{{OG_IMAGE}}">
{{JSONLD}}
<style>
:root{
  --md-primary:#0071E3; --md-primary-deep:#0077ED; --md-on-primary:#FFFFFF;
  --md-primary-container:#E8F2FF; --md-on-primary-container:#0B3D91;
  --md-secondary:#6E6E73; --md-secondary-container:#F0F0F2;
  --md-surface:#FFFFFF; --md-surface-container-low:#F5F5F7; --md-surface-container:#F5F5F7;
  --md-on-surface:#1D1D1F; --md-on-surface-variant:#6E6E73;
  --md-outline:#D2D2D7; --md-outline-variant:#D2D2D7; --md-warning:#D70015;
  --elev-1:0 1px 0 rgba(0,0,0,.04),0 10px 28px -14px rgba(0,0,0,.12);
  --elev-2:0 2px 8px rgba(0,0,0,.08),0 18px 40px -18px rgba(0,0,0,.18);
  --radius:18px; --radius-pill:980px;
  --appbar-bg:rgba(251,251,253,.78); --appbar-border:rgba(0,0,0,.08);
  --md-tonal-bg:rgba(0,0,0,.05); --md-tonal-bg-hover:rgba(0,0,0,.09);
  --md-track:#E8E8ED;
  --rt-c1:#4056E8; --rt-c2:#7C6BF0; --rt-c3:#2EC4B6;
  --rt-bg1:#D9D5F8; --rt-bg2:#CFEFEC; --rt-bg3:#EBEEFE;
}
html[data-theme="dark"]{
  --md-primary:#0A84FF; --md-on-primary:#FFFFFF; --md-primary-container:#1F3A5F;
  --md-on-primary-container:#BFDBFF; --md-secondary:#98989D; --md-secondary-container:#2C2C2E;
  --md-surface:#0D0D0D; --md-surface-container-low:#161617; --md-surface-container:#000000;
  --md-on-surface:#F5F5F7; --md-on-surface-variant:#6E6E73;
  --md-outline:#3A3A3C; --md-outline-variant:#2C2C2E;
  --elev-1:0 1px 0 rgba(255,255,255,.06),0 10px 28px -14px rgba(0,0,0,.6);
  --elev-2:0 2px 8px rgba(0,0,0,.5),0 18px 40px -18px rgba(0,0,0,.7);
  --appbar-bg:rgba(13,13,13,.78); --appbar-border:rgba(255,255,255,.08);
  --md-tonal-bg:rgba(255,255,255,.08); --md-tonal-bg-hover:rgba(255,255,255,.14);
  --md-track:#2C2C2E;
  --rt-c1:#7C8CFF; --rt-c2:#9B8CF8; --rt-c3:#4EE0D2;
  --rt-bg1:#2A2450; --rt-bg2:#103834; --rt-bg3:#14182E;
}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:-apple-system,BlinkMacSystemFont,"SF Pro SC","PingFang SC","Noto Sans SC","Helvetica Neue",sans-serif;
  background:var(--md-surface-container); color:var(--md-on-surface); line-height:1.65; min-height:100vh;
  letter-spacing:.01em; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility;
  transition:background .4s ease-out,color .3s ease-out;
}
a{color:inherit;text-decoration:none}
.appbar{position:sticky;top:0;z-index:10;background:var(--appbar-bg);
  -webkit-backdrop-filter:saturate(1.8) blur(20px);backdrop-filter:saturate(1.8) blur(20px);
  border-bottom:1px solid var(--appbar-border)}
.appbar-inner{max-width:1080px;margin:0 auto;padding:14px 22px;display:flex;align-items:center;gap:12px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:12px;cursor:pointer}
.brand:hover .brand-name{color:var(--md-primary)}
.appbar-icon{width:34px;height:34px;border-radius:10px;display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,var(--rt-c1),var(--rt-c2));color:#fff;font-weight:700;font-size:18px}
.brand-name{font-size:15px;font-weight:600;line-height:1.2}
.brand-sub{font-size:11px;color:var(--md-on-surface-variant)}
.spacer{margin-left:auto}
.nav-link{font-size:13px;font-weight:500;color:var(--md-on-surface);padding:7px 14px;border-radius:var(--radius-pill);
  border:1px solid var(--md-outline-variant);background:var(--md-surface);transition:transform .15s ease,border-color .2s}
.nav-link:hover{transform:scale(1.03);border-color:var(--rt-c1);color:var(--rt-c1)}
.theme-toggle{width:38px;height:38px;border-radius:50%;border:1px solid var(--md-outline-variant);
  background:var(--md-surface);color:var(--md-on-surface);cursor:pointer;font-size:16px;
  display:flex;align-items:center;justify-content:center;transition:transform .15s ease,background .2s}
.theme-toggle:hover{background:var(--md-surface-container-low);transform:scale(1.06)}
.wrap{max-width:1080px;margin:0 auto;padding:40px 22px 70px}
/* hero */
.hero{border-radius:28px;padding:44px 40px;color:#fff;position:relative;overflow:hidden;
  background:linear-gradient(135deg,var(--rt-c1),var(--rt-c2) 55%,var(--rt-c3));
  box-shadow:var(--elev-2);animation:fadeIn .5s ease-out both}
.hero .letters{font-size:52px;font-weight:800;letter-spacing:10px;line-height:1.1;text-shadow:0 2px 18px rgba(0,0,0,.18)}
.hero .cname{font-size:22px;font-weight:600;margin-top:6px;opacity:.96}
.hero .family{margin-top:12px;display:inline-block;font-size:13px;font-weight:600;padding:5px 14px;border-radius:var(--radius-pill);
  background:rgba(255,255,255,.22);backdrop-filter:blur(4px)}
.hero .hdesc{margin-top:18px;font-size:16px;max-width:760px;opacity:.96;line-height:1.7}
/* section */
.sec{margin-top:36px}
.sec-title{font-size:20px;font-weight:700;display:flex;align-items:center;gap:10px;margin-bottom:16px}
.sec-title::before{content:"";width:5px;height:22px;border-radius:3px;background:linear-gradient(180deg,var(--rt-c1),var(--rt-c3))}
.card{background:var(--md-surface);border-radius:var(--radius);padding:28px;box-shadow:var(--elev-1);
  border:1px solid var(--md-outline-variant)}
/* stack */
.stack-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.stack-card{background:var(--md-surface);border-radius:var(--radius);padding:20px;box-shadow:var(--elev-1);
  border:1px solid var(--md-outline-variant);border-top:4px solid var(--rt-c1)}
.stack-card:nth-child(2){border-top-color:var(--rt-c2)}
.stack-card:nth-child(3){border-top-color:var(--rt-c3)}
.stack-card:nth-child(4){border-top-color:var(--md-outline)}
.stack-role{font-size:12px;font-weight:600;color:var(--md-on-surface-variant);letter-spacing:.04em}
.stack-fn{font-size:34px;font-weight:800;margin:6px 0 2px;background:linear-gradient(120deg,var(--rt-c1),var(--rt-c2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.stack-name{font-size:15px;font-weight:700}
.stack-desc{font-size:13px;color:var(--md-on-surface-variant);margin-top:8px;line-height:1.6}
/* features & careers */
.feature-list{list-style:none}
.feature-list li{padding:10px 0 10px 26px;position:relative;border-bottom:1px solid var(--md-outline-variant);font-size:15px}
.feature-list li:last-child{border-bottom:none}
.feature-list li::before{content:"";position:absolute;left:4px;top:17px;width:8px;height:8px;border-radius:50%;
  background:linear-gradient(135deg,var(--rt-c1),var(--rt-c3))}
.chips{display:flex;flex-wrap:wrap;gap:10px}
.chip{font-size:13px;font-weight:500;padding:8px 16px;border-radius:var(--radius-pill);
  background:var(--md-tonal-bg);border:1px solid var(--md-outline-variant);color:var(--md-on-surface)}
/* figure */
.fig-wrap{display:flex;gap:26px;align-items:flex-start;flex-wrap:wrap}
.fig-portrait{width:96px;height:96px;border-radius:50%;overflow:hidden;flex:none;
  border:3px solid var(--md-avatar-ring,#fff);box-shadow:var(--elev-2);background:var(--md-surface-container-low)}
.fig-portrait img{width:100%;height:100%;object-fit:cover}
.fig-fallback{width:100%;height:100%;display:flex;align-items:center;justify-content:center;
  font-size:38px;font-weight:800;color:#fff;background:linear-gradient(135deg,var(--rt-c1),var(--rt-c3))}
.fig-name{font-size:18px;font-weight:700}
.fig-role{font-size:14px;color:var(--md-on-surface-variant);margin-top:4px}
.fig-mot{margin-top:14px;font-size:15px;line-height:1.8;padding:16px 18px;border-radius:14px;
  background:var(--md-tonal-bg);border-left:4px solid var(--rt-c1)}
/* cta */
.cta{display:block;margin:40px auto 0;text-align:center;max-width:420px;padding:16px 28px;border-radius:var(--radius-pill);
  background:linear-gradient(135deg,var(--rt-c1),var(--rt-c2));color:#fff;font-size:16px;font-weight:700;
  box-shadow:var(--elev-2);transition:transform .15s ease,opacity .2s}
.cta:hover{transform:scale(1.03)}
.cta small{display:block;font-weight:400;font-size:12px;opacity:.9;margin-top:2px}
/* type nav */
.type-nav{margin-top:36px}
.type-nav-title{font-size:13px;font-weight:600;color:var(--md-on-surface-variant);margin-bottom:12px;letter-spacing:.05em}
.type-nav-grid{display:grid;grid-template-columns:repeat(8,1fr);gap:8px}
.type-nav-item{text-align:center;padding:9px 4px;border-radius:12px;border:1px solid var(--md-outline-variant);
  background:var(--md-surface);font-size:12px;font-weight:600;transition:transform .12s ease,border-color .15s,color .15s}
.type-nav-item small{display:block;font-weight:400;font-size:10px;color:var(--md-on-surface-variant);margin-top:2px}
.type-nav-item:hover{transform:translateY(-2px);border-color:var(--rt-c1);color:var(--rt-c1)}
footer{padding:26px 22px;border-top:1px solid var(--md-outline-variant);color:var(--md-on-surface-variant);font-size:12px;
  text-align:center;line-height:1.9}
footer a{color:var(--md-primary);font-weight:500}
@media (max-width:760px){
  .stack-grid{grid-template-columns:repeat(2,1fr)}
  .type-nav-grid{grid-template-columns:repeat(4,1fr)}
  .hero{padding:32px 24px}.hero .letters{font-size:38px;letter-spacing:6px}
}
@media (max-width:420px){
  .stack-grid{grid-template-columns:1fr}
}
@media (prefers-reduced-motion: reduce){
  *{animation:none!important;transition:none!important}
}
@keyframes fadeIn{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}
</style>
<style>
.tcard-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}
.tcard{background:var(--md-surface);border-radius:var(--radius);padding:24px;box-shadow:var(--elev-1);
  border:1px solid var(--md-outline-variant);border-top:4px solid var(--card-c1);
  transition:transform .15s ease,box-shadow .2s;display:flex;flex-direction:column;gap:8px}
.tcard:hover{transform:translateY(-3px);box-shadow:var(--elev-2)}
.tc-letters{font-size:26px;font-weight:800;letter-spacing:3px;background:linear-gradient(120deg,var(--card-c1),var(--card-c2));
  -webkit-background-clip:text;background-clip:text;color:transparent}
.tc-name{font-size:16px;font-weight:700}
.tc-desc{font-size:12px;color:var(--md-on-surface-variant);line-height:1.6;flex:1}
.tc-more{font-size:13px;font-weight:600;color:var(--md-primary)}
@media (max-width:900px){.tcard-grid{grid-template-columns:repeat(2,1fr)}}
@media (max-width:480px){.tcard-grid{grid-template-columns:1fr}}
</style>
<style>
.pf-chips{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));gap:8px;margin:0 0 22px}
.pf-chip{display:flex;align-items:center;justify-content:center;padding:8px 6px;border-radius:10px;
  background:var(--md-surface-variant,#f2f2f5);border:1px solid var(--md-outline-variant);color:var(--md-on-surface,#1d1d1f);
  font-size:12.5px;font-weight:700;text-decoration:none;letter-spacing:.5px}
.pf-chip:hover{border-color:var(--md-primary);color:var(--md-primary)}
.pf-list{display:flex;flex-direction:column;gap:16px}
.pf-item{display:flex;gap:20px;background:var(--md-surface);border:1px solid var(--md-outline-variant);
  border-left:4px solid var(--card-c1);border-radius:var(--radius);padding:20px;box-shadow:var(--elev-1);scroll-margin-top:80px}
.pf-media{flex:0 0 148px;align-self:flex-start;position:relative}
.pf-media img{width:100%;aspect-ratio:3/4;height:auto;object-fit:cover;object-position:center top;display:block;
  border-radius:14px;background:var(--md-surface-variant,#f2f2f5)}
.pf-badge{position:absolute;left:8px;top:8px;padding:2px 8px;border-radius:980px;font-size:11px;font-weight:800;
  letter-spacing:1px;color:#fff;background:linear-gradient(120deg,var(--card-c1),var(--card-c2))}
.pf-body{flex:1 1 auto;min-width:0;display:flex;flex-direction:column}
.pf-name{margin:0 0 6px;font-size:19px;font-weight:700;display:flex;flex-wrap:wrap;align-items:baseline;gap:8px}
.pf-life{font-size:12px;font-weight:500;color:#5f5f66;letter-spacing:.5px}
.pf-tags{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 12px}
.pf-tag{font-size:11.5px;font-weight:600;padding:3px 9px;border-radius:6px;background:var(--md-surface-variant,#f2f2f5);
  color:#5f5f66}
.pf-p{margin:0 0 10px;font-size:14px;line-height:1.78;color:var(--md-on-surface,#1d1d1f)}
.pf-k{display:inline-block;margin-right:8px;font-size:12px;font-weight:800;letter-spacing:.5px;color:var(--card-c1)}
.pf-quote{margin:12px 0 10px;padding:10px 14px;border-radius:10px;font-size:13.5px;line-height:1.7;
  background:var(--md-surface-variant,#f7f7fa);border-left:3px solid var(--card-c2);color:var(--md-on-surface,#333)}
.pf-second{margin:14px 0 12px;padding:14px 16px;border-radius:12px;background:var(--md-surface-variant,#f7f7fa);
  border:1px dashed var(--md-outline-variant);border-left:3px solid var(--card-c2)}
.pf-second-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px}
.pf-second-label{font-size:11px;font-weight:800;letter-spacing:.08em;color:var(--card-c2);text-transform:uppercase}
.pf-second-name{font-size:15.5px;font-weight:700}
.pf-second .pf-tags{margin:8px 0 6px}
.pf-second .pf-p{font-size:13.5px;line-height:1.75;margin:0 0 8px}
.pf-second .pf-p:last-child{margin-bottom:0}
.pf-second .pf-k{font-size:11.5px}
.pf-more{display:inline-block;margin-top:auto;padding-top:4px;font-size:13px;font-weight:600;color:var(--md-primary);text-decoration:none}
.pf-note{font-size:12.5px;line-height:1.8;color:#5f5f66;margin:0 0 8px}
@media (max-width:900px){
  .pf-chips{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media (max-width:720px){
  .pf-chips{display:flex;flex-wrap:nowrap;gap:6px;overflow-x:auto;-webkit-overflow-scrolling:touch;
    padding-bottom:6px;scrollbar-width:none}
  .pf-chips::-webkit-scrollbar{display:none}
  .pf-chip{flex:0 0 auto;padding:7px 13px;border-radius:980px}
  .pf-item{flex-direction:row;gap:12px;padding:14px}
  .pf-media{flex:0 0 96px}
  .pf-name{font-size:16px}
  .pf-p{font-size:13px;line-height:1.72}
  .pf-second{padding:12px 13px;margin:12px 0 10px}
  .pf-second .pf-p{font-size:12.5px;line-height:1.7}
  .pf-second-name{font-size:14.5px}
  .pf-note{font-size:12px}
}
@media (max-width:420px){
  .pf-item{flex-direction:column;gap:12px}
  .pf-media{flex:none;width:132px}
}
</style>
</head>
<body>
  <div class="appbar">
    <div class="appbar-inner">
      <a class="brand" href="../index.html" aria-label="返回 MBTI 测试首页">
        <div class="appbar-icon">M</div>
        <div>
          <div class="brand-name">MBTI 认知功能测试</div>
          <div class="brand-sub">16 型人物图鉴</div>
        </div>
      </a>
      <div class="spacer"></div>
      <a class="nav-link" href="../types/index.html">16 型百科</a>
      <a class="nav-link" href="../index.html">开始测试</a>
      <button class="theme-toggle" id="themeToggle" type="button" onclick="toggleTheme()" aria-label="切换深色模式">🌙</button>
      <select class="lang-switch" aria-label="语言" style="height:38px;padding:0 12px;border-radius:980px;border:1px solid var(--md-outline-variant);background:var(--md-surface);color:var(--md-on-surface);font-size:13px;font-weight:500;cursor:pointer;outline:none;max-width:132px;" onchange="location.href=this.value">
{{LANG_OPTIONS}}
</select>
    </div>
  </div>

  <div class="wrap">
    <nav class="breadcrumb-nav" aria-label="面包屑导航" style="font-size:13px;line-height:1.5;display:flex;flex-wrap:wrap;align-items:center;gap:6px;color:var(--md-on-surface-variant,#6e6e73);">
      <a href="../index.html" style="color:var(--md-primary,#0071e3);text-decoration:none;font-weight:500;">首页</a>
      <span aria-hidden="true" style="opacity:.55;">›</span>
      <a href="../types/index.html" style="color:var(--md-primary,#0071e3);text-decoration:none;font-weight:500;">16 型百科</a>
      <span aria-hidden="true" style="opacity:.55;">›</span>
      <span aria-current="page" style="color:var(--md-on-surface-variant,#6e6e73);text-decoration:none;font-weight:500;">{{CRUMB}}</span>
    </nav>

    <header class="hero">
      <h1 style="margin:0;padding:0;font-size:inherit;font-weight:inherit;line-height:inherit;">
        <span class="letters" style="letter-spacing:3px;display:block;">16 PORTRAITS</span>
        <span class="cname" style="display:block;">{{H1}}</span>
      </h1>
      <div class="family">{{FAMILY}}</div>
      <p class="hdesc">{{INTRO}}</p>
    </header>

    <section class="sec">
      <div class="pf-chips">
{{CHIPS}}
      </div>
    </section>

    <section class="sec">
{{ITEMS}}
    </section>

    <section class="sec" id="credit">
      <h2 class="sec-title">关于人物与插画</h2>
      <p class="pf-note">本站插画为程序生成（AI）的示意肖像，用于表达人物气质，并非真实照片，也不代表人物本人、其家属或相关机构的立场。人物生平信息来自公开史料，仅作认知功能类型的通俗举例；把历史人物归入某一 MBTI 类型属于公众解读，不是其本人做过测评的结论。</p>
      <p class="pf-note">{{SECOND_NOTE}}</p>
      <p class="pf-note">引用许可：本站插画与图鉴文字由 MBTI 认知功能测试站原创，可按 CC BY-NC 4.0 方式署名非商业转载（署名格式：MBTI 认知功能测试 · portraits）。</p>
      <p class="pf-note">延伸阅读：<a href="../types/index.html">16 种 MBTI 人格类型大全</a>（认知功能栈、性格特征与适合方向）· <a href="../index.html">开始认知功能测试</a>。</p>
    </section>
  </div>

  <footer>
    <div><a href="../index.html">MBTI 认知功能测试</a> · <a href="../types/index.html">16 种人格类型百科</a> · <a href="index.html">16 型人格人物图鉴</a> · <a href="../country/index.html">最适合生活的国家测试</a></div>
    <div>© 2026 MBTI 认知功能测试 · 仅供自我认知参考，非心理诊断</div>
  </footer>
<script>
/* 深浅主题：localStorage 记忆 + 首载跟随系统（与主站同键，跨页同步） */
(function(){
  var KEY = 'mbti-theme';
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch(e) {}
  var prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  var theme = saved || (prefersDark ? 'dark' : 'light');
  root.setAttribute('data-theme', theme);
  window.__mbtiTheme = theme;
  function syncBtn(t){
    var b = document.getElementById('themeToggle');
    if(!b) return;
    b.textContent = (t === 'dark') ? '☀️' : '🌙';
    b.setAttribute('aria-label', (t === 'dark') ? '切换到浅色模式' : '切换到深色模式');
  }
  window.toggleTheme = function(){
    var next = (root.getAttribute('data-theme') === 'dark') ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    window.__mbtiTheme = next;
    try { localStorage.setItem(KEY, next); } catch(e) {}
    syncBtn(next);
  };
  if(window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').addEventListener){
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function(e){
      var cur = null; try { cur = localStorage.getItem(KEY); } catch(_) {}
      if(!cur){
        var t = e.matches ? 'dark' : 'light';
        root.setAttribute('data-theme', t);
        window.__mbtiTheme = t;
        syncBtn(t);
      }
    });
  }
  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', function(){ syncBtn(root.getAttribute('data-theme')); });
  } else { syncBtn(root.getAttribute('data-theme')); }
})();
</script>
<div id="cookieBanner" style="position:fixed;left:0;right:0;bottom:0;z-index:99999;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:10px 16px;background:rgba(250,250,250,0.97);color:#333;font-size:12px;line-height:1.5;border-top:1px solid rgba(0,0,0,0.08);box-shadow:0 -1px 8px rgba(0,0,0,0.05);font-family:-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif;">
  <span>本站使用 Cookie 以改善浏览体验，继续访问即表示同意。</span>
  <button id="cookieOk" style="flex:none;padding:5px 16px;border:0;border-radius:980px;background:#0071e3;color:#fff;font-size:12px;font-weight:600;cursor:pointer;">同意</button>
</div>
<script>
(function(){var k='mbti_cookie_ok',b=document.getElementById('cookieBanner');if(!b)return;var ok=false;try{ok=localStorage.getItem(k)==='1';}catch(e){}if(ok){b.style.display='none';return;}b.querySelector('#cookieOk').addEventListener('click',function(){try{localStorage.setItem(k,'1');}catch(e){}b.style.display='none';});})();
</script>
</body>
</html>