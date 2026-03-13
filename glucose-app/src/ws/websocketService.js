class WebSocketService {
  socket = null;
  handlers = {};

  connect(url) {
    this.socket = new WebSocket(url);

    this.socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      console.log(msg)
      const handlers = this.handlers[msg.type] || [];
      handlers.forEach((h) => h(msg));
    };
  }

  on(type, handler) {
    if (!this.handlers[type]) {
      this.handlers[type] = [];
    }
    this.handlers[type].push(handler);
  }

  off(type, handler) {
    this.handlers[type] =
      (this.handlers[type] || []).filter(h => h !== handler);
  }
}

export default new WebSocketService();
