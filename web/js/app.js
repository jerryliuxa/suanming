/* 玄机阁 · 前端应用逻辑 */
"use strict";

const WX_COLOR = { "木": "var(--wx-mu)", "火": "var(--wx-huo)", "土": "var(--wx-tu)", "金": "var(--wx-jin)", "水": "var(--wx-shui)" };
const CITIES = [
  ["北京", 116.41], ["上海", 121.47], ["广州", 113.27], ["深圳", 114.06], ["天津", 117.20],
  ["重庆", 106.55], ["成都", 104.07], ["杭州", 120.16], ["南京", 118.78], ["武汉", 114.31],
  ["西安", 108.95], ["郑州", 113.63], ["济南", 117.00], ["沈阳", 123.43], ["哈尔滨", 126.53],
  ["长春", 125.32], ["大连", 121.62], ["呼和浩特", 111.75], ["太原", 112.55], ["石家庄", 114.51],
  ["长沙", 112.94], ["南昌", 115.89], ["合肥", 117.27], ["福州", 119.30], ["厦门", 118.09],
  ["昆明", 102.73], ["贵阳", 106.63], ["南宁", 108.37], ["海口", 110.32], ["兰州", 103.83],
  ["西宁", 101.78], ["银川", 106.23], ["乌鲁木齐", 87.62], ["拉萨", 91.11], ["香港", 114.17],
  ["澳门", 113.55], ["台北", 121.56],
];
const HOURS = [["23", "23点 · 夜子时"], ["0", "0点 · 早子时"], ["1", "1点 · 丑时"], ["2", "2点 · 丑时"],
  ["3", "3点 · 寅时"], ["4", "4点 · 寅时"], ["5", "5点 · 卯时"], ["6", "6点 · 卯时"],
  ["7", "7点 · 辰时"], ["8", "8点 · 辰时"], ["9", "9点 · 巳时"], ["10", "10点 · 巳时"],
  ["11", "11点 · 午时"], ["12", "12点 · 午时"], ["13", "13点 · 未时"], ["14", "14点 · 未时"],
  ["15", "15点 · 申时"], ["16", "16点 · 申时"], ["17", "17点 · 酉时"], ["18", "18点 · 酉时"],
  ["19", "19点 · 戌时"], ["20", "20点 · 戌时"], ["21", "21点 · 亥时"], ["22", "22点 · 亥时"]];

const HOURS12 = [["0", "子时"], ["2", "丑时"], ["4", "寅时"], ["6", "卯时"], ["8", "辰时"], ["10", "巳时"],
  ["12", "午时"], ["14", "未时"], ["16", "申时"], ["18", "酉时"], ["20", "戌时"], ["22", "亥时"]];
const HUA_CLASS = { "化禄": "hua", "化权": "hua hq", "化科": "hua hk2", "化忌": "hua hk" };
const ZW_AREA = { "巳": "si", "午": "wu", "未": "wei", "申": "shen", "辰": "chen", "酉": "you",
  "卯": "mao", "戌": "xu", "寅": "yin", "丑": "chou", "子": "zi", "亥": "hai" };
const TRI_BITS = { "乾": [1, 1, 1], "兑": [1, 1, 0], "离": [1, 0, 1], "震": [1, 0, 0],
  "巽": [0, 1, 1], "坎": [0, 1, 0], "艮": [0, 0, 1], "坤": [0, 0, 0] };
const ASTRO_CITIES = [
  ["北京", 116.41, 39.90], ["上海", 121.47, 31.23], ["广州", 113.27, 23.13], ["深圳", 114.06, 22.54],
  ["成都", 104.07, 30.57], ["重庆", 106.55, 29.56], ["武汉", 114.31, 30.59], ["西安", 108.95, 34.27],
  ["杭州", 120.16, 30.27], ["南京", 118.78, 32.06], ["沈阳", 123.43, 41.80], ["哈尔滨", 126.53, 45.80],
  ["乌鲁木齐", 87.62, 43.83], ["拉萨", 91.11, 29.65], ["昆明", 102.73, 25.04], ["海口", 110.32, 20.03],
  ["香港", 114.17, 22.32], ["台北", 121.56, 25.03], ["兰州", 103.83, 36.06], ["呼和浩特", 111.75, 40.84],
];
const WX_ELEM_COLOR = { "火": "#b03a2e", "土": "#a07414", "风": "#5d8aa8", "水": "#1f618d" };
const TRI_SYM = { "111": "☰", "110": "☱", "101": "☲", "100": "☳", "011": "☴", "010": "☵", "001": "☶", "000": "☷" };
const HEX_NAMES = {
  "乾": { "乾": "乾为天", "兑": "天泽履", "离": "天火同人", "震": "天雷无妄", "巽": "天风姤", "坎": "天水讼", "艮": "天山遁", "坤": "天地否" },
  "兑": { "乾": "泽天夬", "兑": "兑为泽", "离": "泽火革", "震": "泽雷随", "巽": "泽风大过", "坎": "泽水困", "艮": "泽山咸", "坤": "泽地萃" },
  "离": { "乾": "火天大有", "兑": "火泽睽", "离": "离为火", "震": "火雷噬嗑", "巽": "火风鼎", "坎": "火水未济", "艮": "火山旅", "坤": "火地晋" },
  "震": { "乾": "雷天大壮", "兑": "雷泽归妹", "离": "雷火丰", "震": "震为雷", "巽": "雷风恒", "坎": "雷水解", "艮": "雷山小过", "坤": "雷地豫" },
  "巽": { "乾": "风天小畜", "兑": "风泽中孚", "离": "风火家人", "震": "风雷益", "巽": "巽为风", "坎": "风水涣", "艮": "风山渐", "坤": "风地观" },
  "坎": { "乾": "水天需", "兑": "水泽节", "离": "水火既济", "震": "水雷屯", "巽": "水风井", "坎": "坎为水", "艮": "水山蹇", "坤": "水地比" },
  "艮": { "乾": "山天大畜", "兑": "山泽损", "离": "山火贲", "震": "山雷颐", "巽": "山风蛊", "坎": "山水蒙", "艮": "艮为山", "坤": "山地剥" },
  "坤": { "乾": "地天泰", "兑": "地泽临", "离": "地火明夷", "震": "地雷复", "巽": "地风升", "坎": "地水师", "艮": "地山谦", "坤": "坤为地" },
};

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function scoreClass(s) {
  if (s >= 80) return "s5"; if (s >= 70) return "s4"; if (s >= 58) return "s3";
  if (s >= 45) return "s2"; return "s1";
}
function gradeBadge(g) { return '<span class="grade-badge g-' + esc(g) + '">' + esc(g) + "</span>"; }
function toast(msg) {
  const t = document.getElementById("toast");
  t.textContent = msg; t.hidden = false;
  clearTimeout(toast._h); toast._h = setTimeout(() => { t.hidden = true; }, 2400);
}

const App = {
  state: { input: null, chart: null, fortuneYear: null, selectedMonth: null, selectedDay: null },

  async api(path, method, body) {
    const opt = { method: method || "GET", headers: { "Content-Type": "application/json" } };
    if (body !== undefined) opt.body = JSON.stringify(body);
    const res = await fetch(path, opt);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || ("请求失败 " + res.status));
    return data;
  },

  save() { localStorage.setItem("xjg_state", JSON.stringify({ input: this.state.input, chart: this.state.chart })); },
  load() {
    try {
      const s = JSON.parse(localStorage.getItem("xjg_state") || "{}");
      if (s.input) this.state.input = s.input;
      if (s.chart) this.state.chart = s.chart;
    } catch (e) { /* ignore */ }
  },

  updateBadge() {
    const b = document.getElementById("chartBadge");
    if (this.state.chart) {
      const bs = this.state.chart.basic;
      b.hidden = false;
      b.textContent = "当前命例：" + (bs.name || "未命名") + "（" + bs.gender + "）" + bs.solar_text;
    } else b.hidden = true;
  },

  segInit(id, onPick) {
    const box = document.getElementById(id);
    box.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", () => {
        box.querySelectorAll("button").forEach(x => x.classList.remove("on"));
        btn.classList.add("on");
        if (onPick) onPick(btn.dataset.v);
      });
    });
  },
  segValue(id) {
    const on = document.querySelector("#" + id + " button.on");
    return on ? on.dataset.v : null;
  },
  segSet(id, v) {
    document.querySelectorAll("#" + id + " button").forEach(b => b.classList.toggle("on", b.dataset.v === v));
  },

  initForm() {
    const hourSel = document.getElementById("f_hour");
    HOURS.forEach(([v, label]) => {
      const o = document.createElement("option"); o.value = v; o.textContent = label; hourSel.appendChild(o);
    });
    const citySel = document.getElementById("f_city");
    CITIES.forEach(([name, lon]) => {
      const o = document.createElement("option"); o.value = lon; o.textContent = name + "（东经" + lon + "°）"; citySel.appendChild(o);
    });
    this.segInit("f_gender");
    this.segInit("f_calendar", v => {
      document.getElementById("row_leap").hidden = v !== "lunar";
      document.getElementById("f_d").max = v === "lunar" ? 30 : 31;
    });
    this.segInit("f_zi");
    document.getElementById("f_true_solar").addEventListener("change", e => {
      document.getElementById("row_city").hidden = !e.target.checked;
    });
    document.getElementById("paipanForm").addEventListener("submit", e => {
      e.preventDefault(); this.submitPaipan();
    });
  },

  collectInput() {
    const err = document.getElementById("formError");
    err.hidden = true;
    const y = parseInt(document.getElementById("f_y").value, 10);
    const m = parseInt(document.getElementById("f_m").value, 10);
    const d = parseInt(document.getElementById("f_d").value, 10);
    if (!y || !m || !d) { err.textContent = "请先填写完整的年月日。"; err.hidden = false; throw new Error("incomplete"); }
    const hv = document.getElementById("f_hour").value;
    const inp = {
      name: document.getElementById("f_name").value.trim(),
      gender: this.segValue("f_gender"),
      calendar: this.segValue("f_calendar"),
      y, m, d,
      hour: hv === "" ? null : parseInt(hv, 10),
      minute: parseInt(document.getElementById("f_minute").value, 10),
      leap: document.getElementById("f_leap").checked,
      zi_mode: this.segValue("f_zi"),
      true_solar: document.getElementById("f_true_solar").checked,
      lon: document.getElementById("f_true_solar").checked ? parseFloat(document.getElementById("f_city").value) : null,
    };
    return inp;
  },

  fillForm(inp) {
    document.getElementById("f_name").value = inp.name || "";
    this.segSet("f_gender", inp.gender || "male");
    this.segSet("f_calendar", inp.calendar || "solar");
    document.getElementById("row_leap").hidden = (inp.calendar !== "lunar");
    document.getElementById("f_y").value = inp.y || "";
    document.getElementById("f_m").value = inp.m || "";
    document.getElementById("f_d").value = inp.d || "";
    document.getElementById("f_leap").checked = !!inp.leap;
    document.getElementById("f_hour").value = inp.hour == null ? "" : String(inp.hour);
    document.getElementById("f_minute").value = String(inp.minute == null ? 0 : inp.minute);
    this.segSet("f_zi", inp.zi_mode || "late_swap");
    document.getElementById("f_true_solar").checked = !!inp.true_solar;
    document.getElementById("row_city").hidden = !inp.true_solar;
    if (inp.lon) document.getElementById("f_city").value = String(inp.lon);
  },

  async submitPaipan() {
    let inp;
    try { inp = this.collectInput(); } catch (e) { return; }
    try {
      const chart = await this.api("/api/paipan", "POST", inp);
      this.state.input = inp; this.state.chart = chart;
      this.save(); this.updateBadge();
      document.getElementById("paipanResult").innerHTML = this.renderChartHTML(chart);
      document.getElementById("paipanResult").scrollIntoView({ behavior: "smooth", block: "start" });
    } catch (e) {
      const err = document.getElementById("formError");
      err.textContent = e.message; err.hidden = false;
    }
  },

  demoChart() {
    const inp = { name: "示例 · 张三", gender: "male", calendar: "solar", y: 1990, m: 8, d: 16, hour: 9, minute: 30, leap: false, zi_mode: "late_swap", true_solar: false, lon: null };
    this.fillForm(inp);
    location.hash = "#/paipan";
    setTimeout(() => this.submitPaipan(), 60);
  },

  /* ---------- 排盘结果 ---------- */
  pillarHTML(key, p, dayKw) {
    if (!p) {
      return '<div class="pillar"><div class="p-tag">' + key + '</div><div class="p-ss">—</div><div class="p-gan">─</div><div class="p-zhi">─</div><div class="p-cg">时辰未知</div></div>';
    }
    const tags = { year: "年柱", month: "月柱", day: "日柱", hour: "时柱" };
    const cg = p.canggan.map(c => "<b style='color:" + WX_COLOR[c.wx] + "'>" + c.c + "</b>" + c.shishen).join("<br>");
    const ssk = (p.shensha || []).map(s => '<span class="chip red">' + esc(s) + "</span>").join("");
    const kw = (key === "day" || key === "year") && dayKw ? '<div class="p-ny">空亡：' + dayKw.join("、") + "</div>" : "";
    return '<div class="pillar' + (key === "day" ? " is-day" : "") + '">' +
      '<div class="p-tag">' + tags[key] + '</div>' +
      '<div class="p-ss">' + esc(p.shishen_gan) + '</div>' +
      '<div class="p-gan" style="color:' + WX_COLOR[p.gan.wx] + '">' + p.gan.c + '</div>' +
      '<div class="p-wx">' + p.gan.wx + " · " + p.gan.yy + '</div>' +
      '<div class="p-zhi" style="color:' + WX_COLOR[p.zhi.wx] + '">' + p.zhi.c + '</div>' +
      '<div class="p-wx">' + p.zhi.wx + " · " + p.zhi.sx + '</div>' +
      '<div class="p-cg">' + cg + '</div>' +
      '<div class="p-ny">' + esc(p.nayin) + '</div>' +
      '<div class="p-ds">' + esc(p.dish) + '</div>' + kw +
      (ssk ? '<div class="p-ssk">' + ssk + "</div>" : "") +
      "</div>";
  },

  renderChartHTML(chart) {
    const b = chart.basic;
    const ts = b.true_solar && b.true_solar.true_solar
      ? '<span class="ch-item">真太阳时 <b>' + esc(b.true_solar.true_text) + "</b>（钟表 " + esc(b.true_solar.clock_text) + "）</span>" : "";
    const warns = (chart.warnings || []).map(w => "<li>" + esc(w) + "</li>").join("");
    const wxRows = Object.entries(chart.wuxing.percent).map(([k, v]) => {
      const val = chart.wuxing.scores[k];
      return '<div class="wx-row"><span class="wx-name" style="color:' + WX_COLOR[k] + '">' + k + "</span>" +
        '<span class="wx-bar"><i style="width:' + Math.max(v, 1.5) + "%;background:" + WX_COLOR[k] + '"></i></span>' +
        '<span class="wx-val">' + v + "%</span></div>";
    }).join("");
    const missing = chart.wuxing.missing.length ? '<div class="alert warn">五行缺「' + chart.wuxing.missing.join("、") + "」，批文中会给出补益建议。</div>" : "";
    const dy = chart.dayun;
    const dyCells = dy ? dy.list.map(r =>
      '<div class="dayun-cell" onclick="App.gotoFortuneYear(' + r.start_year + ')" title="点击查看该运流年">' +
      '<div class="dc-age">' + r.start_age + "岁</div>" +
      '<div class="dc-gz" style="color:' + WX_COLOR[r.wx_gan] + '">' + r.ganzhi[0] + '</div>' +
      '<div class="dc-gz" style="color:' + WX_COLOR[r.wx_zhi] + '">' + r.ganzhi[1] + '</div>' +
      '<div class="dc-ss">' + esc(r.shishen_gan) + '</div>' +
      '<div class="dc-yr">' + r.start_year + "～" + r.end_year + "</div></div>").join("") : "";
    return '<div class="card">' +
      '<h2 class="card-title">命盘</h2>' +
      '<div class="chart-head">' +
      '<span class="ch-name">' + esc(b.name) + '</span>' +
      '<span class="ch-item"><b>' + esc(b.gender) + '命</b></span>' +
      '<span class="ch-item">公历 <b>' + esc(b.solar_text) + "</b></span>" +
      '<span class="ch-item">农历 <b>' + esc(b.lunar_text) + "</b></span>" +
      '<span class="ch-item">生肖 <b>' + esc(b.zodiac) + "</b></span>" +
      '<span class="ch-item">星座 <b>' + esc(b.xingzuo) + "座</b></span>" +
      '<span class="ch-item">胎元 <b>' + esc(chart.taiyuan) + "</b></span>" + ts + "</div>" +
      (warns ? '<ul class="warn-list">' + warns + "</ul>" : "") +
      '<div class="pillars">' +
      this.pillarHTML("year", chart.pillars.year, chart.kongwang.day) +
      this.pillarHTML("month", chart.pillars.month, null) +
      this.pillarHTML("day", chart.pillars.day, chart.kongwang.day) +
      this.pillarHTML("hour", chart.pillars.hour, null) + "</div>" +
      missing +
      '<div class="sec-block"><h3>五行分布（含藏干加权）</h3><div class="wx-block">' + wxRows + "</div></div>" +
      (dy ? '<div class="sec-block" style="margin-top:16px"><h3>大运 · ' + esc(dy.direction_text) + " · " + esc(dy.start_age_text) + "起运（" + esc(dy.jiaojie_date) + " 交" + esc(dy.jiaojie_jieqi) + "）</h3>" +
        '<div class="dayun-scroll">' + dyCells + "</div></div>" : "") +
      '<div class="ops-row">' +
      '<button class="btn primary" onclick="location.hash=\'#/pazi\'">查看批八字</button>' +
      '<button class="btn ghost" onclick="location.hash=\'#/fortune\'">流年流月运程</button>' +
      '<button class="btn ghost" onclick="location.hash=\'#/today\'">今日运程</button>' +
      '<button class="btn line" onclick="App.saveChart()">存入命例库</button>' +
      "</div></div>";
  },

  gotoFortuneYear(year) {
    this.state.fortuneYear = year;
    location.hash = "#/fortune";
  },

  /* ---------- 命例库 ---------- */
  async saveChart() {
    if (!this.state.input) return toast("请先排盘");
    try {
      await this.api("/api/charts", "POST", { input: this.state.input });
      toast("已存入命例库"); this.refreshSaved();
    } catch (e) { toast("保存失败：" + e.message); }
  },
  async refreshSaved() {
    const box = document.getElementById("savedList");
    try {
      const data = await this.api("/api/charts");
      if (!data.charts.length) { box.innerHTML = '<p class="muted">暂无保存的命例</p>'; return; }
      box.innerHTML = data.charts.map(c =>
        '<div class="saved-item"><div><div class="si-name">' + esc(c.name) + "（" + esc(c.gender === "male" ? "男" : "女") + '）</div>' +
        '<div class="si-sub">' + esc(c.summary) + "</div></div>" +
        '<div class="si-ops"><button class="btn small ghost" onclick="App.loadChart(' + c.id + ')">载入</button>' +
        '<button class="btn small line" onclick="App.delChart(' + c.id + ')">删除</button></div></div>').join("");
    } catch (e) { box.innerHTML = '<p class="muted">加载失败</p>'; }
  },
  async loadChart(id) {
    try {
      const data = await this.api("/api/charts");
      const c = data.charts.find(x => x.id === id);
      if (!c) return toast("命例不存在");
      this.fillForm(c.input);
      this.submitPaipan();
    } catch (e) { toast("载入失败"); }
  },
  async delChart(id) {
    try { await this.api("/api/charts/" + id, "DELETE"); toast("已删除"); this.refreshSaved(); }
    catch (e) { toast("删除失败"); }
  },

  /* ---------- 批八字 ---------- */
  async renderPazi() {
    const box = document.getElementById("paziBody");
    if (!this.state.chart) { box.innerHTML = this.needChartHTML(); return; }
    box.innerHTML = '<p class="muted" style="text-align:center;padding:40px">正在研命排盘…</p>';
    try {
      const a = await this.api("/api/analysis", "POST", this.state.input);
      const st = a.strength;
      const pats = (a.patterns || []).map(p => '<span class="chip red">' + esc(p.text.split("，")[0]) + "</span>").join("");
      const secs = a.sections.map(s =>
        '<div class="card sec-block"><h3>' + esc(s.title) + "</h3>" +
        s.paragraphs.map(p => "<p>" + esc(p) + "</p>").join("") + "</div>").join("");
      box.innerHTML =
        '<div class="card"><h2 class="card-title">批八字 · ' + esc(this.state.chart.basic.name) + "</h2>" +
        '<div class="summary-band">' + esc(a.summary) + "</div>" +
        '<table class="kv-table">' +
        "<tr><td>旺衰判定</td><td><b>" + esc(st.grade) + "</b>（" + esc(st.score) + " 分）· 得令 " + esc(st.detail["得令"]) + " 分 · 得地 " + esc(st.detail["得地"]) + " 分 · 得势 " + esc(st.detail["得势"]) + " 分</td></tr>" +
        "<tr><td>喜用神</td><td><b style='color:var(--bamboo)'>" + a.xiyong.map(esc).join("、") + "</b></td></tr>" +
        "<tr><td>忌神</td><td><b style='color:var(--cinnabar)'>" + a.ji.map(esc).join("、") + "</b></td></tr>" +
        (pats ? "<tr><td>格局提示</td><td>" + pats + "</td></tr>" : "") +
        "</table>" +
        '<div class="ops-row"><button class="btn line" onclick="window.print()">打印批文</button>' +
        '<button class="btn ghost" onclick="location.hash=\'#/fortune\'">看流年运程</button></div>' +
        '<p class="disclaimer">' + esc(a.disclaimer) + "</p></div>" + secs;
    } catch (e) {
      box.innerHTML = '<div class="alert err">' + esc(e.message) + "</div>";
    }
  },

  /* ---------- 流年流月 ---------- */
  async renderFortune() {
    const box = document.getElementById("fortuneBody");
    if (!this.state.chart) { box.innerHTML = this.needChartHTML(); return; }
    if (!this.state.fortuneYear) this.state.fortuneYear = new Date().getFullYear();
    await this.loadFortuneYear(this.state.fortuneYear);
  },

  async loadFortuneYear(year) {
    const box = document.getElementById("fortuneBody");
    if (!this.state.chart) { box.innerHTML = this.needChartHTML(); return; }
    box.innerHTML = '<p class="muted" style="text-align:center;padding:40px">正在推演 ' + year + " 年运程…</p>";
    try {
      const yf = await this.api("/api/fortune/year", "POST", { input: this.state.input, year });
      this.state.fortuneYear = year;
      this._lastYF = yf;
      this.renderFortuneData(yf);
    } catch (e) {
      box.innerHTML = '<div class="alert err">' + esc(e.message) + "</div>";
    }
  },

  renderFortuneData(yf) {
    const box = document.getElementById("fortuneBody");
    const dy = this.state.chart.dayun;
    const decadeChips = (dy ? dy.list : []).map(r => {
      const on = yf.year >= r.start_year && yf.year <= r.end_year ? " on" : "";
      return '<span class="chip' + on + '" onclick="App.loadFortuneYear(' + r.start_year + ')">' + r.ganzhi + "运 " + r.start_year + "～" + r.end_year + "</span>";
    }).join("");
    const months = yf.months.map((m, i) => {
      const on = this.state.selectedMonth === i ? " on" : "";
      return '<div class="month-cell' + on + '" onclick="App.selectMonth(' + i + ')">' +
        '<div class="mc-top"><span class="mc-label">' + esc(m.label) + '</span>' + gradeBadge(m.grade) + "</div>" +
        '<div class="mc-gz">' + esc(m.ganzhi) + " · " + m.start + " ~ " + m.end + "</div>" +
        '<div class="mc-bar"><i class="' + scoreClass(m.score) + '" style="width:' + m.score + '%"></i></div>' +
        '<div class="muted" style="font-size:12.5px">评分 ' + m.score + " · " + m.themes.map(esc).join(" / ") + "</div></div>";
    }).join("");
    const sm = this.state.selectedMonth != null ? yf.months[this.state.selectedMonth] : null;
    const smHTML = sm ? this.fortuneDetailHTML(sm, "流月详解 · " + sm.label) : "";
    box.innerHTML =
      '<div class="card"><div class="year-nav">' +
      '<button class="btn line" onclick="App.loadFortuneYear(' + (yf.year - 1) + ')">‹ 上一年</button>' +
      '<span class="yn-year">' + yf.year + " · " + esc(yf.ganzhi) + "年</span>" +
      '<button class="btn line" onclick="App.loadFortuneYear(' + (yf.year + 1) + ')">下一年 ›</button></div>' +
      (yf.decade ? '<p style="text-align:center" class="muted">当前行 <b>' + esc(yf.decade.ganzhi) + "</b> 大运（" + yf.decade.start_year + "～" + yf.decade.end_year + " 年，" + yf.decade.start_age + " 岁起）</p>" : "") +
      '<div class="decade-chips">' + decadeChips + "</div>" +
      this.fortuneDetailHTML(yf, "流年总运 · " + yf.ganzhi + "年", true) +
      '<div class="sec-block" style="margin-top:18px"><h3>十二流月</h3><div class="months-grid">' + months + "</div></div>" +
      '<div class="month-detail">' + smHTML + "</div></div>";
  },

  selectMonth(i) {
    this.state.selectedMonth = (this.state.selectedMonth === i) ? null : i;
    this.renderFortuneData(this._lastYF);
  },

  fortuneDetailHTML(f, title, isYear) {
    const chips = (f.chips || []).map(c => '<span class="chip">' + esc(c) + "</span>").join("");
    const themes = (f.themes || []).map(t => '<span class="chip blue">' + esc(t) + "</span>").join("");
    return '<div class="sec-block" style="margin-top:8px"><h3>' + esc(title) + "</h3>" +
      '<div class="g-fortune-grid">' +
      '<div class="score-ring" style="--p:' + f.score + ';--ring:' + this.ringColor(f.score) + '">' +
      '<div class="sr-num">' + f.score + "<small>" + esc(f.grade) + "</small></div></div>" +
      "<div><div>" + gradeBadge(f.grade) + ' <span class="muted" style="font-size:14px">十神：' + esc(f.shishen) + " · " + esc(f.ganzhi) + "</span></div>" +
      '<div class="fortune-themes">' + themes + (chips ? "" : "") + "</div>" +
      (chips ? '<div class="fortune-themes">' + chips + "</div>" : "") +
      '<p class="fortune-brief">' + esc(f.brief) + "</p>" +
      '<div class="yiji"><span class="yi"><b>宜</b> ' + f.yi.map(esc).join(" · ") + "</span>" +
      '<span class="ji"><b>忌</b> ' + f.ji.map(esc).join(" · ") + "</span></div></div></div></div>";
  },

  ringColor(s) {
    if (s >= 80) return "var(--cinnabar)"; if (s >= 70) return "var(--bamboo)";
    if (s >= 58) return "var(--indigo)"; if (s >= 45) return "var(--gold)"; return "#8a8378";
  },

  /* ---------- 今日运程 ---------- */
  async renderToday() {
    const box = document.getElementById("todayBody");
    if (!this.state.chart) { box.innerHTML = this.needChartHTML(); return; }
    box.innerHTML = '<p class="muted" style="text-align:center;padding:40px">正在观测天时…</p>';
    try {
      const tf = await this.api("/api/fortune/today", "POST", this.state.input);
      this._lastToday = tf;
      this.state.selectedDay = tf.today_date;
      this.renderTodayData(tf);
    } catch (e) {
      box.innerHTML = '<div class="alert err">' + esc(e.message) + "</div>";
    }
  },

  renderTodayData(tf) {
    const box = document.getElementById("todayBody");
    const card = (title, f, extra) =>
      '<div class="today-card"><div class="tc-head">' +
      '<div class="score-ring" style="--p:' + f.score + ';--ring:' + this.ringColor(f.score) + '"><div class="sr-num">' + f.score + "<small>" + esc(f.grade) + "</small></div></div>" +
      "<div><div class=\"tc-title\">" + title + '</div><div class="tc-gz">' + esc(f.ganzhi) + "</div>" +
      '<div style="font-size:13px;color:var(--ink-soft)">' + esc(f.shishen) + (extra || "") + "</div></div></div>" +
      '<div class="fortune-themes">' + (f.themes || []).map(t => '<span class="chip blue">' + esc(t) + "</span>").join("") + "</div>" +
      '<p class="fortune-brief">' + esc(f.brief) + "</p>" +
      '<div class="yiji"><span class="yi"><b>宜</b> ' + f.yi.map(esc).join(" · ") + '</span><span class="ji"><b>忌</b> ' + f.ji.map(esc).join(" · ") + "</span></div></div>";

    const now = new Date(tf.today_date + "T00:00:00");
    const firstDow = (new Date(now.getFullYear(), now.getMonth(), 1).getDay() + 6) % 7;
    const daysInMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    let cells = "";
    for (let i = 0; i < firstDow; i++) cells += "<div></div>";
    tf.calendar.forEach(d => {
      const day = parseInt(d.date.slice(-2), 10);
      const on = this.state.selectedDay === d.date ? " on" : "";
      cells += '<div class="cal-cell' + on + " " + scoreClass(d.score) + '" onclick="App.selectDay(\'' + d.date + '\')">' +
        '<div class="cc-d">' + day + '</div><div class="cc-gz">' + esc(d.ganzhi) + '</div><div class="cc-s">' + d.score + "</div></div>";
    });
    const sel = tf.calendar.find(d => d.date === this.state.selectedDay);
    const selHTML = sel ? this.fortuneDetailHTML(sel, "流日详解 · " + sel.date + "（" + sel.weekday + "）") : "";
    box.innerHTML =
      '<div class="card"><h2 class="card-title">今日运程 · ' + esc(tf.today_date) + "</h2>" +
      '<div class="today-grid">' +
      card("当年 · " + tf.year.year + " " + tf.year.ganzhi + "年", tf.year) +
      card("当月 · " + tf.month.label, tf.month) +
      card("今日 · " + tf.day.weekday, tf.day) + "</div>" +
      '<div class="sec-block"><h3>' + (now.getMonth() + 1) + "月每日运程</h3>" +
      '<div class="cal-head">' + ["一", "二", "三", "四", "五", "六", "日"].map(x => "<span>" + x + "</span>").join("") + "</div>" +
      '<div class="cal-grid">' + cells + "</div>" +
      '<div class="cal-legend"><span>吉凶：</span><i class="s5"></i>上吉 <i class="s4"></i>吉 <i class="s3"></i>平 <i class="s2"></i>起伏 <i class="s1"></i>低伏</div>' +
      '<div class="day-detail">' + selHTML + "</div></div></div>";
  },

  selectDay(date) {
    this.state.selectedDay = date;
    this.renderTodayData(this._lastToday);
  },

  needChartHTML() {
    return '<div class="empty-tip"><h2>尚未排盘</h2><p>请先录入出生信息，完成八字排盘后即可查看此处内容。</p>' +
      '<button class="btn primary" onclick="location.hash=\'#/paipan\'">前往排盘</button>' +
      '<button class="btn ghost" onclick="App.demoChart()">试试示例命例</button></div>';
  },

  /* ---------- 紫微斗数 ---------- */
  initZiwei() {
    const sel = document.getElementById("z_hour");
    HOURS12.forEach(([v, label]) => { const o = document.createElement("option"); o.value = v; o.textContent = label; sel.appendChild(o); });
    this.segInit("z_gender");
    document.getElementById("ziweiForm").addEventListener("submit", e => { e.preventDefault(); this.submitZiwei(); });
  },

  ziweiDemo() {
    document.getElementById("z_y").value = 1990;
    document.getElementById("z_m").value = 6;
    document.getElementById("z_d").value = 26;
    document.getElementById("z_leap").checked = false;
    document.getElementById("z_hour").value = "8";
    this.segSet("z_gender", "male");
    this.submitZiwei();
  },

  async submitZiwei() {
    const err = document.getElementById("ziweiError"); err.hidden = true;
    const body = {
      gender: this.segValue("z_gender"),
      y: parseInt(document.getElementById("z_y").value, 10),
      m: parseInt(document.getElementById("z_m").value, 10),
      d: parseInt(document.getElementById("z_d").value, 10),
      leap: document.getElementById("z_leap").checked,
      hour: parseInt(document.getElementById("z_hour").value, 10),
    };
    if (!body.y || !body.m || !body.d) { err.textContent = "请填写完整农历年月日。"; err.hidden = false; return; }
    try {
      const r = await this.api("/api/ziwei", "POST", body);
      this.renderZiwei(r);
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  },

  renderZiwei(r) {
    const b = r.basic;
    const huaMap = r.hua_map || {};
    const cell = p => {
      const stars = p.major.map(s => {
        const h = huaMap[s];
        return '<span class="star">' + s + "</span>" + (h ? '<span class="' + (HUA_CLASS[h] || "hua") + '">' + h + "</span>" : "");
      }).join("<br>");
      const minor = p.minor.length ? '<div class="zw-minor">' + p.minor.map(esc).join(" · ") + "</div>" : "";
      const borrow = (!p.major.length && p.borrowed) ? '<div class="zw-borrow">借对宫：' + p.borrowed.join("、") + "</div>" : "";
      return '<div class="zw-cell' + (p.name === "命宫" ? " is-ming" : "") + '" style="grid-area:' + ZW_AREA[p.branch] + '">' +
        '<div class="zw-head"><span>' + esc(p.limit) + '</span><span>' + esc(p.gan) + esc(p.branch) + '</span></div>' +
        '<div class="zw-palace">' + esc(p.name) + "</div>" +
        (p.is_shen ? '<span class="zw-shen">身宫</span>' : "") +
        '<div class="zw-major">' + (stars || '<span class="muted" style="font-size:12px">空宫</span>') + "</div>" +
        borrow + minor + "</div>";
    };
    const mid = '<div class="zw-mid mid1"><b>' + esc(b.gender) + "命</b> · " + esc(b.year_gz) + "年<br>农历 " + esc(b.lunar) + "<br>" + esc(b.hour) + "</div>" +
      '<div class="zw-mid mid2"><b>' + esc(b.wuxing_ju) + "</b><br>命宫 " + esc(b.ming_gong) + " · 身宫 " + esc(b.shen_gong) + "<br>大限" + esc(b.direction) + "</div>" +
      '<div class="zw-mid mid3"><b>紫微在' + esc(r.ziwei_pos) + "</b><br>四化：" + esc(r.hua) + "</div>" +
      '<div class="zw-mid mid4" style="font-size:12px;color:var(--ink-soft)">未列庙旺亮度与流曜，流派差异见左侧说明。</div>';
    document.getElementById("ziweiResult").innerHTML =
      '<div class="card"><h2 class="card-title">紫微命盘 · ' + esc(b.lunar) + " " + esc(b.hour) + "（" + esc(b.gender) + "）</h2>" +
      '<p style="line-height:1.9;font-size:14.5px">' + esc(r.brief) + "</p>" +
      '<div class="zw-grid">' + r.palaces.map(cell).join("") + mid + "</div>" +
      '<p class="disclaimer">' + esc(r.note) + "</p></div>";
  },

  /* ---------- 梅花易数 ---------- */
  initMeihua() {
    const sel = document.getElementById("m_hour");
    HOURS12.forEach(([v, label]) => { const o = document.createElement("option"); o.value = v; o.textContent = label; sel.appendChild(o); });
    this.segInit("m_mode", v => {
      document.getElementById("m_time_block").hidden = v !== "time";
      document.getElementById("m_num_block").hidden = v !== "numbers";
    });
    document.getElementById("meihuaForm").addEventListener("submit", e => { e.preventDefault(); this.submitMeihua(); });
    const now = new Date();
    document.getElementById("m_y").value = now.getFullYear();
    document.getElementById("m_m").value = now.getMonth() + 1;
    document.getElementById("m_d").value = now.getDate();
    document.getElementById("m_hour").value = String([23, 0].includes(now.getHours()) ? 0 : now.getHours() % 2 === 1 ? now.getHours() - 1 : now.getHours());
  },

  meihuaDemo() {
    const now = new Date();
    document.getElementById("m_y").value = now.getFullYear();
    document.getElementById("m_m").value = now.getMonth() + 1;
    document.getElementById("m_d").value = now.getDate();
    document.getElementById("m_hour").value = "0";
    this.segSet("m_mode", "time");
    document.getElementById("m_time_block").hidden = false;
    document.getElementById("m_num_block").hidden = true;
    this.submitMeihua();
  },

  async submitMeihua() {
    const err = document.getElementById("meihuaError"); err.hidden = true;
    const mode = this.segValue("m_mode");
    let body;
    if (mode === "numbers") {
      body = { mode, n1: parseInt(document.getElementById("m_n1").value, 10), n2: parseInt(document.getElementById("m_n2").value, 10) };
      if (!body.n1 || !body.n2) { err.textContent = "请输入两个起卦数字。"; err.hidden = false; return; }
    } else {
      body = { mode, y: parseInt(document.getElementById("m_y").value, 10), m: parseInt(document.getElementById("m_m").value, 10),
               d: parseInt(document.getElementById("m_d").value, 10), hour: parseInt(document.getElementById("m_hour").value, 10) };
      if (!body.y || !body.m || !body.d) { err.textContent = "请填写完整日期。"; err.hidden = false; return; }
    }
    try {
      const r = await this.api("/api/meihua", "POST", body);
      this.renderMeihua(r);
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  },

  hexFigHTML(name, lines, dongYao) {
    const rows = lines.map((v, i) => '<div class="yao ' + (v ? "yang" : "yin") + ((i + 1) === dongYao ? " dong" : "") + '"></div>').join("");
    return '<div class="hex-fig"><div class="hex-lines">' + rows + '</div><div class="hex-sym">' + this.hexSymbol(lines) + '</div><div class="hex-name">' + esc(name) + "</div></div>";
  },

  hexSymbol(lines) {
    const tri = bits => TRI_SYM[bits.join("")];
    return tri(lines.slice(3, 6)) + tri(lines.slice(0, 3));
  },

  renderMeihua(r) {
    const byName = {};
    Object.entries(HEX_NAMES).forEach(([up, row]) => Object.entries(row).forEach(([lo, nm]) => byName[nm] = [up, lo]));
    const hu = byName[r.hu], bian = byName[r.bian];
    const huLines = TRI_BITS[hu[1]].concat(TRI_BITS[hu[0]]);
    const benLines = r.lines;
    const bianLines = benLines.slice(0, r.dong - 1).concat([1 - benLines[r.dong - 1]]).concat(benLines.slice(r.dong));
    document.getElementById("meihuaResult").innerHTML =
      '<div class="card"><h2 class="card-title">卦象解析 · ' + esc(r.rel) + "</h2>" +
      '<div class="hex-versus">' +
      this.hexFigHTML(r.name, benLines, r.dong) +
      this.hexFigHTML(r.hu + "（互）", huLines, 0) +
      this.hexFigHTML(r.bian + "（变）", bianLines, 0) +
      '<div style="flex:1;min-width:230px"><div class="g-fortune-grid">' +
      '<div class="score-ring" style="--p:' + r.score + ';--ring:' + this.ringColor(r.score) + '"><div class="sr-num">' + r.score + "<small>" + esc(r.grade) + "</small></div></div>" +
      '<div><div>' + gradeBadge(r.grade) + '</div><div class="muted" style="font-size:14px;margin-top:8px">体卦 ' + esc(r.ti.sym + r.ti.name) + "（" + esc(r.ti.wx) + "）<br>用卦 " + esc(r.yong.sym + r.yong.name) + "（" + esc(r.yong.wx) + "）<br>动爻第 " + r.dong + " 爻</div></div></div></div></div>" +
      r.paragraphs.map(p => '<p style="line-height:1.95;font-size:15px;text-align:justify">' + esc(p) + "</p>").join("") +
      '<p class="disclaimer">梅花易数解卦由规则引擎生成，心诚则灵，仅供文化娱乐参考。</p></div>';
  },

  /* ---------- 八字合婚 ---------- */
  initHehun() {
    document.querySelectorAll(".hour-select").forEach(sel => {
      HOURS.forEach(([v, label]) => { const o = document.createElement("option"); o.value = v; o.textContent = label; sel.appendChild(o); });
    });
    this.segInit("ha_gender");
    this.segInit("hb_gender");
  },

  hehunDemo() {
    document.getElementById("ha_name").value = "甲 · 张生";
    this.segSet("ha_gender", "male");
    document.getElementById("ha_y").value = 1990; document.getElementById("ha_m").value = 8;
    document.getElementById("ha_d").value = 16; document.getElementById("ha_hour").value = "9";
    document.getElementById("hb_name").value = "乙 · 李娘";
    this.segSet("hb_gender", "female");
    document.getElementById("hb_y").value = 1992; document.getElementById("hb_m").value = 3;
    document.getElementById("hb_d").value = 8; document.getElementById("hb_hour").value = "14";
    this.submitHehun();
  },

  readSide(prefix) {
    const y = parseInt(document.getElementById(prefix + "_y").value, 10);
    const m = parseInt(document.getElementById(prefix + "_m").value, 10);
    const d = parseInt(document.getElementById(prefix + "_d").value, 10);
    if (!y || !m || !d) throw new Error("请填写完整的" + (prefix === "ha" ? "甲方" : "乙方") + "年月日");
    const hv = document.getElementById(prefix + "_hour").value;
    return { name: document.getElementById(prefix + "_name").value.trim(),
             gender: this.segValue(prefix + "_gender"),
             calendar: "solar", y, m, d,
             hour: hv === "" ? null : parseInt(hv, 10), minute: 0 };
  },

  async submitHehun() {
    const err = document.getElementById("hehunError"); err.hidden = true;
    try {
      const body = { a: this.readSide("ha"), b: this.readSide("hb") };
      const r = await this.api("/api/hehun", "POST", body);
      this.renderHehun(r);
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  },

  renderHehun(r) {
    const strip = '<div class="pair-strip"><span><b>' + esc(r.a.name || "甲方") + "</b>（" + esc(r.a.gender) + "）" + esc(r.a.year_gz) + "年 " + esc(r.a.day_gz) + "日</span>" +
      "<span>❤</span><span><b>" + esc(r.b.name || "乙方") + "</b>（" + esc(r.b.gender) + "）" + esc(r.b.year_gz) + "年 " + esc(r.b.day_gz) + "日</span></div>";
    const parts = r.parts.map(p =>
      "<tr><td>" + esc(p.name) + '</td><td style="color:' + (p.score >= 8 ? "var(--bamboo)" : p.score <= -4 ? "var(--cinnabar)" : "var(--ink-soft)") + '">' +
      (p.score >= 0 ? "+" : "") + p.score + "</td><td>" + esc(p.text) + "</td></tr>").join("");
    document.getElementById("hehunResult").innerHTML =
      '<div class="card"><h2 class="card-title">合婚结果</h2>' + strip +
      '<div class="g-fortune-grid" style="margin-bottom:14px">' +
      '<div class="score-ring" style="--p:' + r.score + ';--ring:' + this.ringColor(r.score) + ';width:110px;height:110px"><div class="sr-num">' + r.score + "<small>" + esc(r.grade) + "</small></div></div>" +
      '<div><div>' + gradeBadge(r.grade) + '</div><p class="fortune-brief">' + esc(r.verdict) + "</p></div></div>" +
      '<table class="kv-table"><tr><td style="width:110px">项目</td><td style="width:60px">得分</td><td>说明</td></tr>' + parts + "</table>" +
      '<p class="disclaimer">' + esc(r.advice) + "</p></div>";
  },

  /* ---------- 生肖流年 ---------- */
  async renderZodiac() {
    await this.loadZodiac(this._zodiacYear || new Date().getFullYear());
  },

  async loadZodiac(year) {
    const box = document.getElementById("zodiacBody");
    box.innerHTML = '<p class="muted" style="text-align:center;padding:40px">正在推演 ' + year + " 年生肖运程…</p>";
    try {
      const r = await this.api("/api/zodiac/" + year);
      this._zodiacYear = year;
      const mySx = this.state.chart ? this.state.chart.basic.zodiac : null;
      const cells = r.list.map((x, i) => {
        const on = this.state._zodiacSel === i ? " on" : "";
        const mine = mySx === x.shengxiao ? '<span class="chip red" style="margin-left:4px">本命</span>' : "";
        return '<div class="zodiac-cell' + on + '" onclick="App.selectZodiac(' + i + ')">' +
          '<div class="zx" style="color:' + (mySx === x.shengxiao ? "var(--cinnabar)" : "var(--ink)") + '">' + esc(x.shengxiao) + "</div>" +
          '<div class="zx-name">' + esc(x.zhi) + " · " + esc(x.shengxiao) + mine + "</div>" +
          '<span class="grade-badge rel-' + esc(x.relation) + '">' + esc(x.relation) + "</span>" +
          '<div class="zx-bar"><i class="' + scoreClass(x.score) + '" style="width:' + x.score + '%"></i></div>' +
          '<div class="muted" style="font-size:12px">运势基线 ' + x.score + "</div></div>";
      }).join("");
      const sel = this.state._zodiacSel != null ? r.list[this.state._zodiacSel] : null;
      const detail = sel ? '<div class="card zodiac-detail"><h2 class="card-title">' + sel.shengxiao + "（" + sel.zhi + "）· " + esc(sel.relation) + '</h2><p style="line-height:1.9">' + esc(sel.text) + "</p></div>" : "";
      box.innerHTML = '<div class="card"><div class="year-nav">' +
        '<button class="btn line" onclick="App.loadZodiac(' + (year - 1) + ')">‹ ' + (year - 1) + "</button>" +
        '<span class="yn-year">' + year + " · " + esc(r.taisui_gz) + "年</span>" +
        '<button class="btn line" onclick="App.loadZodiac(' + (year + 1) + ')">' + (year + 1) + " ›</button></div>" +
        '<p style="text-align:center" class="muted">太岁 <b>' + esc(r.taisui_gz) + "</b>，值年生肖 " + esc(r.taisui_zhi) + "。刑冲破害者，主动应变、诸事谨慎。</p>" +
        '<div class="zodiac-grid">' + cells + "</div>" + detail +
        '<p class="disclaimer">生肖流年以年支与太岁关系论吉凶，为民俗参考；个人运势请以八字流年为准。</p></div>';
    } catch (e) {
      box.innerHTML = '<div class="alert err">' + esc(e.message) + "</div>";
    }
  },

  selectZodiac(i) {
    this.state._zodiacSel = (this.state._zodiacSel === i) ? null : i;
    this.loadZodiac(this._zodiacYear);
  },

  /* ---------- 星座命盘 ---------- */
  initAstro() {
    const hourSel = document.getElementById("a_hour");
    HOURS.forEach(([v, label]) => { const o = document.createElement("option"); o.value = v; o.textContent = label; hourSel.appendChild(o); });
    const citySel = document.getElementById("a_city");
    ASTRO_CITIES.forEach(([name, lon, lat]) => {
      const o = document.createElement("option");
      o.value = lon + "," + lat; o.textContent = name + "（东经" + lon + "° · 北纬" + lat + "°）";
      citySel.appendChild(o);
    });
    document.getElementById("astroForm").addEventListener("submit", e => { e.preventDefault(); this.submitAstro(); });
  },

  astroDemo() {
    document.getElementById("a_name").value = "Alice";
    document.getElementById("a_y").value = 1990;
    document.getElementById("a_m").value = 8;
    document.getElementById("a_d").value = 16;
    document.getElementById("a_hour").value = "9";
    document.getElementById("a_minute").value = "30";
    this.submitAstro();
  },

  async submitAstro(withToday) {
    const err = document.getElementById("astroError"); err.hidden = true;
    const y = parseInt(document.getElementById("a_y").value, 10);
    const m = parseInt(document.getElementById("a_m").value, 10);
    const d = parseInt(document.getElementById("a_d").value, 10);
    if (!y || !m || !d) { err.textContent = "请填写完整出生日期。"; err.hidden = false; return; }
    const hv = document.getElementById("a_hour").value;
    const [lon, lat] = document.getElementById("a_city").value.split(",").map(parseFloat);
    const body = { name: document.getElementById("a_name").value.trim(), y, m, d,
                   hour: hv === "" ? null : parseInt(hv, 10),
                   minute: parseInt(document.getElementById("a_minute").value, 10),
                   lon, lat, with_today: true };
    try {
      const r = await this.api("/api/astro", "POST", body);
      this._lastAstro = r;
      this.renderAstro(r);
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  },

  renderAstro(r) {
    const rows = r.placements.map(p =>
      "<tr><td><b>" + esc(p.body) + '</b><span class="muted" style="font-size:11.5px"> ' + esc(p.role) + '</span></td>' +
      '<td style="color:' + WX_ELEM_COLOR[p.element] + '">' + esc(p.sym) + " <b>" + esc(p.sign) + "</b> " + p.deg + "°</td>" +
      "<td>" + (p.house ? "第 " + p.house + " 宫" : "—") + "</td>" +
      '<td><span class="chip" style="border-color:' + WX_ELEM_COLOR[p.element] + ';color:' + WX_ELEM_COLOR[p.element] + '">' + esc(p.element) + "</span></td></tr>").join("");
    const elems = Object.entries(r.elements).map(([k, v]) =>
      '<div class="wx-row"><span class="wx-name" style="color:' + WX_ELEM_COLOR[k] + '">' + k + "</span>" +
      '<span class="wx-bar"><i style="width:' + (v * 20) + "%;background:" + WX_ELEM_COLOR[k] + '"></i></span>' +
      '<span class="wx-val">' + v + " 星</span></div>").join("");
    let traits = '<div class="sec-block" style="margin-top:14px"><h3>性格解读</h3>' +
      '<p>【太阳 ' + esc(r.basic.sun_sign) + "】" + esc(r.sun_trait) + "</p>";
    if (r.basic.asc_sign) traits += "<p>" + esc(r.asc_trait) + "</p>";
    traits += "<p class=\"muted\" style=\"font-size:13px\">" + esc("月亮在" + r.basic.moon_sign + "。") + "月亮星座是情绪与安全感的模式：你如何应对压力、如何表达需要、什么环境让你安心。</p></div>";

    let todayHTML = "";
    if (r.today) {
      const t = r.today;
      const aspects = t.aspects.length
        ? t.aspects.map(a => "<li" + (a.good > 0 ? ' style="color:var(--bamboo)"' : a.good < 0 ? ' style="color:var(--cinnabar)"' : "") + ">" + esc(a.text) + "</li>").join("")
        : "<li class=\"muted\">今日七曜与本命行星暂无紧密相位，平静的一天。</li>";
      const trList = Object.entries(t.transits).map(([k, v]) => esc(k) + "在" + esc(v)).join(" · ");
      todayHTML = '<div class="sec-block" style="margin-top:16px"><h3>今日天象 · ' + esc(t.date) + "（" + esc(t.grade) + " " + t.score + "）</h3>" +
        '<p class="muted" style="font-size:13px">' + trList + "</p><ul style=\"line-height:1.9;font-size:14px\">" + aspects + "</ul></div>";
    }

    const pairBox = '<div class="card" style="margin-top:0"><h2 class="card-title">星座配对速查</h2>' +
      '<div class="form-grid2">' +
      '<div class="form-row"><label>你的太阳星座</label><select id="pair_a"></select></div>' +
      '<div class="form-row"><label>对方太阳星座</label><select id="pair_b"></select></div></div>' +
      '<button class="btn primary" onclick="App.submitPair()">看配对</button>' +
      '<div id="pairResult" style="margin-top:14px"></div></div>';

    document.getElementById("astroResult").innerHTML =
      '<div class="card"><h2 class="card-title">星盘 · ' + esc(r.basic.name) + "（" + esc(r.basic.birth) + "）</h2>" +
      '<div class="chart-head"><span class="ch-item">太阳 <b>' + esc(r.basic.sun_sign) + "</b></span>" +
      '<span class="ch-item">月亮 <b>' + esc(r.basic.moon_sign) + "</b></span>" +
      (r.basic.asc_sign ? '<span class="ch-item">上升 <b>' + esc(r.basic.asc_sign) + "</b></span>" : "") + "</div>" +
      '<table class="kv-table"><tr><td>星体</td><td>星座与度数</td><td>整宫宫位</td><td>元素</td></tr>' + rows + "</table>" +
      '<div class="sec-block" style="margin-top:14px"><h3>五行(四元素)能量</h3><div class="wx-block">' + elems + "</div></div>" +
      traits +
      '<p class="disclaimer">' + esc(r.note) + "</p>" +
      '<div class="ops-row"><button class="btn line" onclick="App.refreshToday()">刷新今日天象</button></div>' +
      todayHTML + "</div>" + pairBox;
    const sels = ["pair_a", "pair_b"];
    const SIGNS = ["白羊", "金牛", "双子", "巨蟹", "狮子", "处女", "天秤", "天蝎", "射手", "摩羯", "水瓶", "双鱼"];
    sels.forEach((id, k) => {
      const sel = document.getElementById(id);
      sel.innerHTML = SIGNS.map(s => "<option" + (k === 0 && s === r.basic.sun_sign ? " selected" : "") + ">" + s + "</option>").join("");
    });
    document.getElementById("astroPairBox").innerHTML = "";
  },

  async refreshToday() {
    const r = this._lastAstro;
    if (!r) return;
    try {
      const t = await this.api("/api/astro", "POST", Object.assign({}, r.input, { with_today: true }));
      this._lastAstro = t; this.renderAstro(t);
    } catch (e) { toast("刷新失败"); }
  },

  async submitPair() {
    const a = document.getElementById("pair_a").value;
    const b = document.getElementById("pair_b").value;
    try {
      const r = await this.api("/api/astro/pair", "POST", { a, b });
      document.getElementById("pairResult").innerHTML =
        '<div class="summary-band"><b>' + esc(r.pair) + "</b>（" + esc(r.elements) + "）" +
        ' <span class="grade-badge g-吉">' + esc(r.grade) + " " + r.score + "</span><br>" + esc(r.verdict) +
        '<br><span class="muted" style="font-size:12.5px">' + esc(r.advice) + "</span></div>";
    } catch (e) { toast(e.message); }
  },

  /* ---------- 塔罗牌 ---------- */
  async tarotDaily() {
    const name = document.getElementById("t_name").value.trim();
    const r = await this.api("/api/tarot", "POST", { mode: "daily", name });
    this._lastTarot = r;
    this.renderTarotCards([r.card], [r.reversed], ["今日指引"], r.meaning, r.advice, r.date + " · 每日一抽");
  },

  async tarotSpread() {
    const question = document.getElementById("t_question").value.trim();
    const r = await this.api("/api/tarot", "POST", { mode: "three", question });
    this._lastTarot = r;
    this.renderTarotCards(r.cards.map(c => c.card), r.cards.map(c => c.reversed),
      r.cards.map(c => c.position), null, r.synthesis + "<br><span class='muted' style='font-size:12.5px'>" + esc(r.advice) + "</span>", "三牌阵");
  },

  renderTarotCards(cards, reversedFlags, positions, singleMeaning, footer, title) {
    const ROMAN = ["0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI"];
    const html = cards.map((card, i) => {
      const rev = reversedFlags[i];
      const isMajor = card.arcana === "大";
      const badge = isMajor ? ROMAN[card.num] : card.suit;
      const art = isMajor ? card.name[0] : card.name[0];
      const meaning = (cards.length === 1 && singleMeaning) ? singleMeaning : (rev ? card.rev : card.up);
      return '<div class="tarot-slot"><div class="tarot-card' + (rev ? " rev" : "") + '">' +
        '<div class="tc-inner"><div class="tc-top">' + esc(badge) + "</div>" +
        '<div class="tc-art">' + esc(art) + "</div>" +
        '<div class="tc-name">' + esc(card.name) + "</div>" +
        '<div class="tc-en">' + esc(card.en) + "</div></div></div>" +
        '<div class="tc-pos">' + esc(positions[i]) + (rev ? " · <b style='color:var(--cinnabar)'>逆位</b>" : " · 正位") + "</div>" +
        '<div class="tarot-mean"><b>' + esc(card.name) + (rev ? "（逆位）" : "（正位）") + "</b>：" + esc(meaning) + "</div></div>";
    }).join("");
    document.getElementById("tarotResult").innerHTML =
      '<div class="card"><h2 class="card-title">' + esc(title) + "</h2>" +
      '<div class="tarot-row">' + html + "</div>" +
      (footer ? '<p class="fortune-brief" style="margin-top:14px">' + footer + "</p>" : "") + "</div>";
  },

  /* ---------- 路由 ---------- */
  async route() {
    const hash = location.hash.replace("#/", "") || "home";
    const views = ["home", "paipan", "pazi", "fortune", "today", "ziwei", "meihua", "hehun", "zodiac", "astro", "tarot"];
    const view = views.includes(hash) ? hash : "home";
    views.forEach(v => { document.getElementById("view-" + v).hidden = v !== view; });
    document.querySelectorAll("#nav a").forEach(a => a.classList.toggle("on", a.dataset.view === view));
    if (view === "paipan") this.refreshSaved();
    if (view === "pazi") await this.renderPazi();
    if (view === "fortune") await this.renderFortune();
    if (view === "today") await this.renderToday();
    if (view === "zodiac") await this.renderZodiac();
  },
  async initHome() {
    try {
      const meta = await this.api("/api/meta");
      const g = meta.today_ganzhi;
      document.getElementById("homeMeta").innerHTML =
        "今日 " + esc(meta.today) + " · <b>" + esc(g.year) + "年 " + esc(g.month) + "月 " + esc(g.day) + "日</b>";
    } catch (e) {
      document.getElementById("homeMeta").textContent = "服务未连接";
    }
  },

  async init() {
    this.load();
    this.initForm();
    this.initZiwei();
    this.initMeihua();
    this.initHehun();
    this.initAstro();
    this.updateBadge();
    window.addEventListener("hashchange", () => this.route());
    await this.route();
    this.initHome();
  },
};

window.App = App;
App.init();
