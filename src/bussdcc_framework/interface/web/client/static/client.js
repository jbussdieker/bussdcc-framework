(function () {
  if (window.BussDCC) {
    return;
  }

  const widgetFactories = new Map();
  const socketHandlers = new Map();
  let socketInstance = null;
  let domReadyBound = false;

  function getSocketConfig() {
    const cfg = window.BUSSDCC_SOCKETIO_CONFIG || {};
    return { ...cfg };
  }

  function ensureSocket() {
    if (socketInstance) {
      return socketInstance;
    }

    if (typeof window.io !== "function") {
      throw new Error("Socket.IO client is not loaded");
    }

    socketInstance = window.io(getSocketConfig());

    socketInstance.on("connect", function () {
      socketInstance.emit("connected", { data: "connected!" });
      console.log("✅ Connected to socket, id:", socketInstance.id);
    });

    socketInstance.on("disconnect", function (reason) {
      console.warn("⚠️ Socket disconnected:", reason);
    });

    socketInstance.on("reconnect_attempt", function (attempt) {
      console.log(`🔄 Attempting to reconnect (#${attempt})...`);
    });

    socketInstance.on("reconnect", function (attempt) {
      console.log(`✅ Reconnected after ${attempt} attempts, id: ${socketInstance.id}`);
      socketInstance.emit("connected", { data: "reconnected!" });
    });

    socketInstance.on("reconnect_error", function (error) {
      console.error("❌ Reconnection error:", error);
    });

    socketInstance.on("reconnect_failed", function () {
      console.error("❌ Could not reconnect");
    });

    return socketInstance;
  }

  function on(eventName, handler) {
    if (typeof handler !== "function") {
      throw new TypeError("handler must be a function");
    }

    const socket = ensureSocket();

    if (!socketHandlers.has(eventName)) {
      socketHandlers.set(eventName, []);

      socket.on(eventName, function (payload) {
        const handlers = socketHandlers.get(eventName) || [];
        for (const fn of handlers) {
          try {
            fn(payload);
          } catch (error) {
            console.error(`❌ Error in BussDCC handler for ${eventName}:`, error);
          }
        }
      });
    }

    socketHandlers.get(eventName).push(handler);
  }

  function emit(eventName, payload) {
    ensureSocket().emit(eventName, payload);
  }

  function registerWidget(name, initFn) {
    if (!name) {
      throw new Error("Widget name is required");
    }

    if (typeof initFn !== "function") {
      throw new TypeError("Widget initializer must be a function");
    }

    widgetFactories.set(name, initFn);
  }

  function initElement(el) {
    if (!(el instanceof Element)) {
      return;
    }

    const widgetName = el.dataset.bussdccWidget;
    if (!widgetName) {
      return;
    }

    if (el.dataset.bussdccInitialized === "true") {
      return;
    }

    const initFn = widgetFactories.get(widgetName);
    if (!initFn) {
      return;
    }

    initFn(el);
    el.dataset.bussdccInitialized = "true";
  }

  function scan(root) {
    const scope = root || document;

    if (scope instanceof Element && scope.matches("[data-bussdcc-widget]")) {
      initElement(scope);
    }

    if (typeof scope.querySelectorAll === "function") {
      scope.querySelectorAll("[data-bussdcc-widget]").forEach(initElement);
    }
  }

  function init(root) {
    scan(root || document);
  }

  function bindDOMContentLoaded() {
    if (domReadyBound) {
      return;
    }

    domReadyBound = true;

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", function () {
        init(document);
      });
    } else {
      init(document);
    }
  }

  window.BussDCC = {
    socket: ensureSocket,
    on,
    emit,
    registerWidget,
    initElement,
    scan,
    init,
  };

  bindDOMContentLoaded();
})();
