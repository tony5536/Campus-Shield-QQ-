// Centralized WebSocket configuration and lightweight reconnect helper
// - Chooses ws/wss based on window.location.protocol
// - Uses window.location.host by default
// - Allows override via REACT_APP_WS_URL

const DEFAULT_PATH = '/ws/alerts';

export function getWsUrl(path = DEFAULT_PATH) {
  // Allow explicit full URL override
  const env = process.env.REACT_APP_WS_URL;
  if (env) return env;

  const p = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  // If caller passed a full path (starting with '/'), join it
  const suffix = path.startsWith('/') ? path : `/${path}`;
  return `${p}//${host}${suffix}`;
}

// Lightweight managed WebSocket with auto-reconnect (3s) and basic handlers.
// Returns an object with `close()` to stop reconnect attempts.
export function connectWithAutoReconnect(pathOrUrl, handlers = {}) {
  const url = pathOrUrl.startsWith('ws:') || pathOrUrl.startsWith('wss:')
    ? pathOrUrl
    : getWsUrl(pathOrUrl);

  let ws = null;
  let shouldReconnect = true;
  const RECONNECT_MS = 3000;
  let reconnectTimer = null;

  function clearTimer() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function create() {
    ws = new WebSocket(url);

    ws.onopen = (ev) => {
      handlers.onOpen?.(ev);
    };

    ws.onmessage = (ev) => {
      handlers.onMessage?.(ev);
    };

    ws.onerror = (ev) => {
      handlers.onError?.(ev);
    };

    ws.onclose = (ev) => {
      handlers.onClose?.(ev);
      if (shouldReconnect) {
        clearTimer();
        reconnectTimer = setTimeout(() => create(), RECONNECT_MS);
      }
    };

    return ws;
  }

  // Start connection immediately
  create();

  return {
    get current() {
      return ws;
    },
    url,
    close() {
      shouldReconnect = false;
      clearTimer();
      try {
        ws?.close();
      } catch (e) {
        // ignore
      }
    }
  };
}
