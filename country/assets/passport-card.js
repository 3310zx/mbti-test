/* 护照风分享卡：1080×1440 canvas，无外部依赖 */
(function () {
  var W = 1080, H = 1440;
  var NAVY = "#1b2a4a", INK = "#14213d", GOLD = "#a8853f", PAPER = "#f5f2e9";
  var LABEL = "#7b8296", MUTED = "#8f8b80", BLUE = "rgba(32,56,107,";

  function font(ctx, size, weight, family) {
    ctx.font = (weight ? weight + " " : "") + size + "px " +
      (family || 'Georgia,"Songti SC","PingFang SC",serif');
  }
  function spaced(ctx, text, x, y, sp, align) {
    var chars = String(text).split(""), i, w = [], total = 0, sx;
    for (i = 0; i < chars.length; i++) { w.push(ctx.measureText(chars[i]).width); total += w[i] + (i < chars.length - 1 ? sp : 0); }
    sx = align === "right" ? x - total : (align === "center" ? x - total / 2 : x);
    ctx.textAlign = "left";
    for (i = 0; i < chars.length; i++) { ctx.fillText(chars[i], sx, y); sx += w[i] + sp; }
    return total;
  }
  function star(ctx, cx, cy, r, rot) {
    var i, a;
    ctx.beginPath();
    for (i = 0; i < 10; i++) {
      a = (rot || -Math.PI / 2) + i * Math.PI / 5;
      var rr = i % 2 ? r * 0.42 : r;
      i ? ctx.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr)
        : ctx.moveTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr);
    }
    ctx.closePath(); ctx.fill();
  }
  function paper(ctx) {
    ctx.fillStyle = PAPER; ctx.fillRect(0, 0, W, H);
    var g = ctx.createLinearGradient(0, 0, W, H);
    g.addColorStop(0, "rgba(226,232,240,0.55)");
    g.addColorStop(.5, "rgba(250,248,241,0.15)");
    g.addColorStop(1, "rgba(219,226,236,0.5)");
    ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
  }
  function guilloche(ctx) {
    var x, y, i, t;
    ctx.lineWidth = 0.9;
    for (i = 0; i < 26; i++) {
      y = 150 + i * 44;
      ctx.strokeStyle = "rgba(96,120,158," + (0.05 + (i % 3) * 0.022) + ")";
      ctx.beginPath();
      for (x = 0; x <= W; x += 6) {
        t = y + Math.sin(x / (52 + i * 3) + i) * (5 + (i % 4) * 2.4);
        x ? ctx.lineTo(x, t) : ctx.moveTo(x, t);
      }
      ctx.stroke();
    }
    for (i = 0; i < 18; i++) {
      x = 30 + i * 60;
      ctx.strokeStyle = "rgba(96,120,158," + (0.04 + (i % 3) * 0.018) + ")";
      ctx.beginPath();
      for (y = 140; y <= 1230; y += 6) {
        t = x + Math.cos(y / (60 + i * 2.5) + i) * (4 + (i % 3) * 2);
        y === 140 ? ctx.moveTo(t, y) : ctx.lineTo(t, y);
      }
      ctx.stroke();
    }
  }
  function watermark(ctx) {
    var cx = 540, cy = 700, r = 430, i, a;
    var g = ctx.createRadialGradient(cx, cy, 20, cx, cy, r);
    g.addColorStop(0, "rgba(27,42,74,0.055)");
    g.addColorStop(0.7, "rgba(27,42,74,0.03)");
    g.addColorStop(1, "rgba(27,42,74,0)");
    ctx.fillStyle = g; ctx.beginPath(); ctx.arc(cx, cy, r, 0, 7); ctx.fill();
    ctx.save();
    ctx.strokeStyle = "rgba(27,42,74,0.11)"; ctx.setLineDash([7, 9]);
    [r * 0.98, r * 0.9, r * 0.56].forEach(function (rr) {
      ctx.lineWidth = rr > r * 0.9 ? 1 : 1.6;
      ctx.beginPath(); ctx.arc(cx, cy, rr, 0, 7); ctx.stroke();
    });
    ctx.restore();
    ctx.fillStyle = "rgba(27,42,74,0.10)";
    for (i = 0; i < 26; i++) {
      a = i * Math.PI * 2 / 26;
      star(ctx, cx + Math.cos(a) * r * 0.76, cy + Math.sin(a) * r * 0.76, 9, a + Math.PI / 2);
    }
    ctx.fillStyle = "rgba(27,42,74,0.07)";
    star(ctx, cx, cy, 92, -Math.PI / 2);
    ctx.strokeStyle = "rgba(27,42,74,0.10)"; ctx.lineWidth = 1.4;
    ctx.beginPath(); ctx.arc(cx, cy, 120, 0, 7); ctx.stroke();
  }
  function header(ctx, d) {
    ctx.fillStyle = NAVY; ctx.fillRect(0, 0, W, 132);
    ctx.fillStyle = GOLD; ctx.fillRect(0, 132, W, 5);
    ctx.fillStyle = "#ffffff";
    font(ctx, 34, "", 'Georgia,"Songti SC",serif');
    spaced(ctx, "PASSPORT", 64, 62, 9);
    font(ctx, 15, "", '"PingFang SC","Songti SC",sans-serif');
    ctx.fillStyle = "rgba(255,255,255,0.66)";
    spaced(ctx, "护 照", 66, 96, 3);
    font(ctx, 19, "", 'Georgia,"Songti SC",serif');
    ctx.fillStyle = "rgba(255,255,255,0.9)";
    spaced(ctx, "WHERE TO LIVE", 1016, 60, 3, "right");
    font(ctx, 13, "", '"PingFang SC",sans-serif');
    ctx.fillStyle = "rgba(255,255,255,0.6)";
    spaced(ctx, "国家匹配测试 · 55 国 · 六维度", 1016, 92, 1.6, "right");
  }
  function checkDigit(str) {
    var total = 0, w = [7, 3, 1], i, ch, v;
    for (i = 0; i < str.length; i++) {
      ch = str.charAt(i);
      v = ch === "<" ? 0 : (ch >= "0" && ch <= "9" ? +ch : ch.charCodeAt(0) - 55);
      total += v * w[i % 3];
    }
    return total % 10;
  }
  function pad(s, n, fill) { s = String(s); while (s.length < n) s += (fill || "<"); return s.slice(0, n); }

  function render(d) {
    var cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    var ctx = cv.getContext("2d");
    var c1 = d.countries[0] || { zh: "—", iso3: "WLD", score: 0 };
    var date = (d.date || "").replace(/-/g, "").slice(2);
    var no = String(checkDigit(c1.iso3 + date) + "" + (d.countries.length) + (c1.score | 0));
    var i;

    paper(ctx); guilloche(ctx); watermark(ctx); header(ctx);

    /* 顶栏信息：TYPE / CODE / NO. */
    var cols = [["TYPE", "P"], ["CODE", c1.iso3], ["PASSPORT NO.", pad(no, 8, "0")]];
    cols.forEach(function (c, idx) {
      var x = 64 + idx * 236;
      font(ctx, 12, "", '"Helvetica Neue","PingFang SC",sans-serif');
      ctx.fillStyle = LABEL; spaced(ctx, c[0], x, 200, 2.2);
      font(ctx, 24, "", 'Menlo,Consolas,"Courier New",monospace');
      ctx.fillStyle = NAVY; spaced(ctx, c[1], x, 238, 2);
    });

    /* 证件照位：首位匹配国 */
    ctx.fillStyle = "rgba(255,255,255,0.55)";
    ctx.fillRect(762, 176, 254, 322);
    ctx.strokeStyle = NAVY; ctx.lineWidth = 3; ctx.strokeRect(762, 176, 254, 322);
    ctx.strokeStyle = BLUE + "0.25)"; ctx.lineWidth = 1; ctx.strokeRect(770, 184, 238, 306);
    ctx.textAlign = "center";
    font(ctx, 12, "", '"Helvetica Neue","PingFang SC",sans-serif');
    ctx.fillStyle = LABEL; spaced(ctx, "DESTINATION", 889, 214, 2.4, "center");
    font(ctx, 21, "", '"PingFang SC","Songti SC",sans-serif');
    ctx.fillStyle = INK; ctx.fillText(c1.zh, 889, 330);
    font(ctx, 54, "", 'Georgia,serif');
    ctx.fillStyle = NAVY; spaced(ctx, c1.iso3, 889, 396, 4, "center");
    ctx.fillStyle = BLUE + "0.18)"; ctx.fillRect(800, 414, 178, 1);
    font(ctx, 15, "", 'Menlo,Consolas,monospace');
    ctx.fillStyle = "#4c576e";
    spaced(ctx, "RANK 01 / 55", 889, 448, 1.6, "center");
    font(ctx, 26, "", 'Georgia,serif');
    ctx.fillStyle = NAVY; ctx.fillText(Number(c1.score).toFixed(1), 889, 484);

    /* 字段区 */
    var fields = [
      ["SURNAME / 首选地", c1.zh + "（" + c1.iso3 + "）"],
      ["PRIORITY / 最在意", d.topDim ? d.topDim.zh + "  " + Number(d.topDim.weight).toFixed(1) + "×" : "综合均衡"],
      ["DATE OF ISSUE / 测试日", d.date || ""],
      ["AUTHORITY / 签发机关", "WHERE-TO-LIVE TEST"]
    ];
    fields.forEach(function (f, idx) {
      var y = 340 + idx * 116;
      font(ctx, 12, "", '"Helvetica Neue","PingFang SC",sans-serif');
      ctx.fillStyle = LABEL; spaced(ctx, f[0], 64, y, 2.2);
      font(ctx, 29, "", 'Georgia,"Songti SC","PingFang SC",serif');
      ctx.fillStyle = INK; ctx.textAlign = "left";
      ctx.fillText(f[1], 64, y + 40);
    });

    /* 三强列表 */
    var listY = 846;
    font(ctx, 12, "", '"Helvetica Neue","PingFang SC",sans-serif');
    ctx.fillStyle = LABEL; spaced(ctx, "TOP 3 MATCHES / 三强", 64, listY, 2.4);
    d.countries.slice(0, 3).forEach(function (c, idx) {
      var y = listY + 40 + idx * 82;
      ctx.strokeStyle = "rgba(20,33,61,0.13)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(64, y); ctx.lineTo(700, y); ctx.stroke();
      font(ctx, 15, "", 'Menlo,Consolas,monospace');
      ctx.fillStyle = GOLD; ctx.textAlign = "left";
      ctx.fillText("0" + (idx + 1), 64, y + 46);
      font(ctx, 27, "", 'Georgia,"Songti SC",serif');
      ctx.fillStyle = INK;
      ctx.fillText(c.zh, 128, y + 48);
      font(ctx, 15, "", 'Menlo,Consolas,monospace');
      ctx.fillStyle = LABEL;
      ctx.fillText(c.iso3, 400, y + 46);
      font(ctx, 24, "", 'Georgia,serif');
      ctx.fillStyle = NAVY; ctx.textAlign = "right";
      ctx.fillText(Number(c.score).toFixed(1), 700, y + 47);
      ctx.textAlign = "left";
    });

    /* 印章 */
    var sx = 872, sy = 1046, sr = 108;
    ctx.save();
    ctx.translate(sx, sy); ctx.rotate(-0.21);
    ctx.strokeStyle = BLUE + "0.55)";
    ctx.lineWidth = 3.4; ctx.beginPath(); ctx.arc(0, 0, sr, 0, 7); ctx.stroke();
    ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(0, 0, sr - 12, 0, 7); ctx.stroke();
    ctx.fillStyle = BLUE + "0.6)";
    font(ctx, 17, "", '"Helvetica Neue",sans-serif');
    spaced(ctx, "APPROVED", 0, -14, 3, "center");
    font(ctx, 13, "", 'Menlo,Consolas,monospace');
    spaced(ctx, (d.date || "").replace(/-/g, "."), 0, 18, 1.5, "center");
    font(ctx, 11, "", '"Helvetica Neue",sans-serif');
    ctx.fillStyle = BLUE + "0.42)";
    spaced(ctx, "WTL · 55", 0, 46, 2.2, "center");
    star(ctx, 0, -46, 11, -Math.PI / 2);
    ctx.restore();

    /* MRZ 机读区 */
    ctx.fillStyle = "rgba(27,42,74,0.055)";
    ctx.fillRect(0, 1236, W, 156);
    ctx.strokeStyle = "rgba(27,42,74,0.18)"; ctx.lineWidth = 1;
    ctx.setLineDash([9, 8]);
    ctx.beginPath(); ctx.moveTo(0, 1236); ctx.lineTo(W, 1236); ctx.stroke();
    ctx.setLineDash([]);
    var l1 = pad("P<WTL" + c1.iso3 + "<<GEOGRAPHIC<PROFILE", 44);
    var body2 = pad(String(Math.round(c1.score * 10)), 4, "0") + c1.iso3 + date + "<" + checkDigit(pad(String(Math.round(c1.score * 10)), 4, "0") + c1.iso3 + date);
    var l2 = pad(body2, 44);
    font(ctx, 27, "", 'Menlo,Consolas,"Courier New",monospace');
    ctx.fillStyle = NAVY; ctx.textAlign = "left";
    spaced(ctx, l1, 60, 1300, 1.1);
    spaced(ctx, l2, 60, 1352, 1.1);

    /* 页脚 */
    font(ctx, 13, "", '"Helvetica Neue","PingFang SC",sans-serif');
    ctx.fillStyle = MUTED; ctx.textAlign = "center";
    spaced(ctx, d.url || "3310zx.github.io/mbti-test/country/", 540, 1416, 1.2, "center");
    ctx.textAlign = "left";
    return cv.toDataURL("image/png");
  }

  function download(d) {
    var url = render(d);
    var iso = (d.countries[0] && d.countries[0].iso3 || "WTL").toLowerCase();
    var a = document.createElement("a");
    a.href = url;
    a.download = "passport-" + iso + ".png";
    document.body.appendChild(a); a.click();
    setTimeout(function () { a.parentNode && a.parentNode.removeChild(a); }, 0);
  }

  window.PassportCard = { render: render, download: download };
})();
