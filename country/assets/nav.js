/* 移动端抽屉导航：<=760px 时由 .nav-toggle 控制 .head-nav.open */
(function () {
  var toggle, nav;

  function els() {
    toggle = toggle || document.querySelector('.nav-toggle');
    nav = nav || document.getElementById('site-nav');
    return toggle && nav;
  }

  function setOpen(open) {
    if (!els()) return;
    nav.classList.toggle('open', open);
    toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    toggle.setAttribute('aria-label', open ? '关闭导航' : '打开导航');
  }

  document.addEventListener('click', function (e) {
    if (!els()) return;
    if (e.target.closest('.nav-toggle')) {
      setOpen(!nav.classList.contains('open'));
      return;
    }
    if (nav.classList.contains('open') && !e.target.closest('.head-nav')) {
      setOpen(false);
    }
  });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && els() && nav.classList.contains('open')) setOpen(false);
  });

  window.addEventListener('resize', function () {
    if (els() && window.innerWidth > 760) setOpen(false);
  });
})();
