/*
 * "Try the Demo" on /alternative-home-page/.
 *
 * Signs the visitor in to the Chap demo DHIS2 instance in the background,
 * then opens the Modeling App dashboard in a new tab. Because chap.dhis2.org
 * and climate.im.dhis2.org are on the same site (dhis2.org), the browser
 * keeps the DHIS2 session cookie and the new tab is already signed in.
 *
 * Requirements on the DHIS2 instance:
 *   - https://chap.dhis2.org must be on the CORS allowlist
 *     (System Settings -> Access -> CORS allowlist).
 *
 * The credentials below are for a shared demo account and are visible to
 * anyone who views this file. Never put a real account here.
 */
(function () {
  "use strict";

  var DHIS2_BASE = "https://climate.im.dhis2.org/climate-demo";
  var DASHBOARD_URL = DHIS2_BASE + "/apps/dhis2-chapmodeling-app#/dashboard";
  var LOGIN_URL = DHIS2_BASE + "/api/auth/login";
  var DEMO_USERNAME = "admin";
  var DEMO_PASSWORD = "district";

  var button = document.getElementById("chap-demo-open");
  var status = document.getElementById("chap-demo-status");
  if (!button || button.dataset.chapDemoReady) {
    return;
  }
  button.dataset.chapDemoReady = "true";

  function setStatus(text) {
    if (!status) {
      return;
    }
    status.textContent = text;
    status.style.display = text ? "block" : "none";
  }

  function showLoadingScreen(tab) {
    try {
      tab.document.write(
        "<!doctype html><html><head><meta charset=\"utf-8\">" +
        "<title>Opening the Chap demo…</title></head>" +
        "<body style=\"margin:0;height:100vh;display:flex;align-items:center;justify-content:center;" +
        "font-family:Roboto,Helvetica,Arial,sans-serif;color:#002147;\">" +
        "<p>Signing you in to the Chap demo…</p></body></html>"
      );
      tab.document.close();
    } catch (error) {
      /* Cosmetic only; ignore if the browser does not allow it. */
    }
  }

  async function signIn() {
    var response;
    try {
      response = await fetch(LOGIN_URL, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: DEMO_USERNAME, password: DEMO_PASSWORD })
      });
    } catch (error) {
      throw new Error(
        "The browser blocked the sign-in request. " + location.origin +
        " is probably missing from the DHIS2 CORS allowlist."
      );
    }
    var text = await response.text();
    if (!text) {
      throw new Error(
        "DHIS2 returned an empty response. " + location.origin +
        " is probably missing from the DHIS2 CORS allowlist."
      );
    }
    var data;
    try {
      data = JSON.parse(text);
    } catch (error) {
      throw new Error("DHIS2 returned an unexpected response (HTTP " + response.status + ").");
    }
    if (!response.ok || data.loginStatus !== "SUCCESS") {
      throw new Error("DHIS2 rejected the sign-in (" + (data.loginStatus || "HTTP " + response.status) + ").");
    }
  }

  button.addEventListener("click", async function (event) {
    // Let modifier-clicks and middle-clicks behave like a normal link.
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
      return;
    }
    event.preventDefault();

    // Open the tab right away, while the click still counts as a user gesture,
    // so pop-up blockers do not stop it. It is navigated once sign-in is done.
    var tab = window.open("about:blank", "_blank");
    if (!tab) {
      setStatus("Your browser blocked the new tab. Allow pop-ups for this site and try again.");
      return;
    }
    showLoadingScreen(tab);

    button.setAttribute("aria-busy", "true");
    setStatus("Signing in to the demo…");
    try {
      await signIn();
      setStatus("");
    } catch (error) {
      console.warn("[chap-demo] Automatic sign-in failed: " + error.message);
      setStatus(
        "We could not sign you in automatically. Log in with username " +
        DEMO_USERNAME + " and password " + DEMO_PASSWORD + "."
      );
    } finally {
      tab.location.href = DASHBOARD_URL;
      button.removeAttribute("aria-busy");
    }
  });
})();
