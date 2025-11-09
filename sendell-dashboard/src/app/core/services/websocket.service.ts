import { Injectable } from '@angular/core';
import { Subject } from 'rxjs';

interface WSMessage {
  type: string;
  data: any;
}

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket!: WebSocket;

  public messages$ = new Subject<WSMessage>();
  public connected$ = new Subject<boolean>();

  connect() {
    this.socket = new WebSocket('ws://localhost:8765/ws');

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.connected$.next(true);
    };

    this.socket.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.messages$.next(message);
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.connected$.next(false);
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.connected$.next(false);

      // Reconnect after 3 seconds
      setTimeout(() => this.connect(), 3000);
    };
  }

  disconnect() {
    if (this.socket) {
      this.socket.close();
    }
  }
}
