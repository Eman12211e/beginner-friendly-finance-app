// DEV ONLY. Fake data. Never loaded without ?mock=1. Integrator deletes this file.
(function () {
  "use strict";

  var AS_OF = "2026-01-01T00:00:00Z";
  var NA = "Data not available";

  function ok(data) {
    return { ok: true, data: data, source: "demo", as_of: AS_OF, error: null };
  }

  function fail(code, message) {
    return { ok: false, data: null, source: null, as_of: null, error: { code: code, message: message } };
  }

  var SNAPSHOTS = {
    EXMPL: {
      ticker: "EXMPL", name: "Example Corp", is_etf: false, exchange: "NASDAQ", currency: "USD",
      sector: "Technology", description: "Example Corp makes widgets. It sells them in many countries.",
      price: { value: 123.45, display: "$123.45" },
      change_percent: { value: 1.2, display: "+1.2%" },
      market_cap: { value: 1.5e12, display: "$1.50T" },
      dividend_yield: { value: 0.5, display: "0.50%" },
      expense_ratio: { value: null, display: NA },
    },
    EXMPLF: {
      ticker: "EXMPLF", name: null, is_etf: true, exchange: null, currency: "USD", sector: null,
      description: "Example Fund tracks an example index.",
      price: { value: 50.0, display: "$50.00" },
      change_percent: { value: -0.4, display: "-0.4%" },
      market_cap: { value: null, display: NA },
      dividend_yield: { value: 1.1, display: "1.10%" },
      expense_ratio: { value: 0.05, display: "0.05%" },
    },
  };

  var EARNINGS = {
    EXMPL: {
      ticker: "EXMPL", is_etf: false, etf_message: null,
      period: { label: "Quarter ended Jun 27, 2026", period_end: "2026-06-27" },
      headline: { comparison: "above", label: "EPS vs. analyst estimate: Above", explain: "Mock headline explanation." },
      sections: {
        revenue: {
          title: "Revenue", value: { value: 1.0e10, display: "$10.00B" },
          prior_year_value: { value: 9.5e9, display: "$9.50B" }, change_percent: { value: 5.3, display: "+5.3%" },
          direction: "up", explain: "Mock revenue explanation.",
        },
        profit: {
          title: "Profit (net income)", value: { value: null, display: NA },
          prior_year_value: { value: 1.8e9, display: "$1.80B" }, change_percent: { value: null, display: NA },
          direction: null, explain: null,
        },
        eps: {
          title: "Earnings per share vs. analyst estimate", period_label: "Quarter ended Jun 27, 2026",
          report_date: "2026-07-30", actual: { value: 1.23, display: "$1.23" },
          estimate: { value: 1.2, display: "$1.20" }, difference: { value: 0.03, display: "$0.03" },
          comparison: "above", source_label: "Analyst average estimate (source: demo data)",
          explain: "Mock EPS explanation.",
        },
        cash: { title: "Cash and cash equivalents", value: { value: 3.0e10, display: "$30.00B" }, explain: "Mock cash explanation." },
        dividend: {
          title: "Dividend", pays_dividend: true, last_amount: { value: 0.25, display: "$0.25" },
          last_ex_date: "2026-08-10", explain: "Mock dividend explanation.",
        },
      },
      questions_to_think_about: ["Mock question one?", "Mock question two?", "Mock question three?"],
      explanation_source: "ai",
    },
    EXMPLF: {
      ticker: "EXMPLF", is_etf: true,
      etf_message: "ETFs hold many companies. They do not report earnings. Look at the fund's holdings and fees instead.",
      etf_explain: "Mock ETF explanation.", period: null, headline: null, sections: null,
      questions_to_think_about: ["Mock fund question one?", "Mock fund question two?", "Mock fund question three?"],
      explanation_source: "fallback",
    },
  };

  function route(url, options) {
    var m = url.match(/^\/api\/stocks\/([^/]+)\/(snapshot|earnings)/);
    if (m) {
      var ticker = decodeURIComponent(m[1]);
      var table = m[2] === "snapshot" ? SNAPSHOTS : EARNINGS;
      return table[ticker] ? ok(table[ticker]) : fail("DATA_NOT_AVAILABLE", "No data is available for " + ticker + ".");
    }
    if (url.indexOf("/api/chat") === 0) {
      return { ok: true, data: { reply: "Mock reply.", show_checklist_link: /buy|sell|hold/i.test(options && options.body || "") }, source: null, as_of: null, error: null };
    }
    if (url.indexOf("/api/alerts") === 0) return { ok: true, data: { alerts: [] }, source: "demo", as_of: AS_OF, error: null };
    if (url.indexOf("/api/health") === 0) return ok({ status: "ok", data_mode: "mock", keys_present: {} });
    return fail("INTERNAL_ERROR", "Mock has no response for this request.");
  }

  window.MOCK_RESPONSES = {
    // Random delay so fast clicking exercises the stale-response guard.
    respond: function (url, options) {
      return new Promise(function (resolve) {
        setTimeout(function () { resolve(route(url, options)); }, 100 + Math.random() * 500);
      });
    },
  };

  document.addEventListener("DOMContentLoaded", function () {
    var banner = document.createElement("div");
    banner.className = "mock-banner";
    banner.textContent = "MOCK MODE: fake data";
    document.body.insertBefore(banner, document.body.firstChild);
  });
})();
