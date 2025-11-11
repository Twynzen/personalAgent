import { Component, Input, AfterViewInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';

export type ProjectStatus = 'working' | 'ready' | 'offline';

@Component({
  selector: 'activity-graph',
  standalone: true,
  template: `<canvas #canvas></canvas>`,
  styles: [`
    canvas {
      width: 100%;
      height: 100%;
      display: block;
    }
  `]
})
export class ActivityGraphComponent implements AfterViewInit, OnDestroy {
  @ViewChild('canvas', { static: false }) canvasRef!: ElementRef<HTMLCanvasElement>;
  @Input() status: ProjectStatus = 'offline';
  @Input() activityLevel: number = 50; // 0-100

  private ctx!: CanvasRenderingContext2D;
  private animationFrame: number = 0;
  private dataPoints: number[] = [];
  private readonly maxPoints = 60;
  private time = 0;
  private heartbeatCounter = 0;

  ngAfterViewInit() {
    this.initCanvas();
    this.startAnimation();
  }

  ngOnDestroy() {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
  }

  private initCanvas() {
    const canvas = this.canvasRef.nativeElement;
    this.ctx = canvas.getContext('2d')!;

    // Set canvas size
    canvas.width = canvas.offsetWidth * 2; // High DPI
    canvas.height = canvas.offsetHeight * 2;
    this.ctx.scale(2, 2);

    // Initialize data points
    this.dataPoints = new Array(this.maxPoints).fill(50);
  }

  private animationCounter = 0;

  private startAnimation() {
    const animate = () => {
      // Update every 6 frames instead of every frame (much slower scroll)
      this.animationCounter++;
      if (this.animationCounter % 6 === 0) {
        this.updateDataPoints();
      }
      this.draw();
      this.animationFrame = requestAnimationFrame(animate);
    };
    animate();
  }

  private updateDataPoints() {
    // Shift data points left
    this.dataPoints.shift();

    let newPoint = 50;

    if (this.status === 'working') {
      this.heartbeatCounter++;

      // ECG-style heartbeat pattern
      // Heartbeat occurs every 50 frames (~5 seconds at current speed)
      const beatInterval = 50;
      const positionInBeat = this.heartbeatCounter % beatInterval;

      if (positionInBeat < 8) {
        // Heartbeat spike sequence
        if (positionInBeat === 0) newPoint = 55; // Start rise
        else if (positionInBeat === 1) newPoint = 70; // Sharp rise
        else if (positionInBeat === 2) newPoint = 85; // Peak
        else if (positionInBeat === 3) newPoint = 75; // Start fall
        else if (positionInBeat === 4) newPoint = 40; // Dip below baseline
        else if (positionInBeat === 5) newPoint = 60; // Small rebound
        else if (positionInBeat === 6) newPoint = 52; // Return to baseline
        else if (positionInBeat === 7) newPoint = 50; // Baseline
      } else {
        // Baseline with minimal variation between beats
        newPoint = 50 + (Math.random() - 0.5) * 3;
      }
    } else if (this.status === 'ready') {
      // Blue flat line with minimal variation
      newPoint = 50 + (Math.random() - 0.5) * 5;
    } else {
      // Red flat line
      newPoint = 50;
    }

    this.dataPoints.push(newPoint);
  }

  private draw() {
    const canvas = this.canvasRef.nativeElement;
    const width = canvas.offsetWidth;
    const height = canvas.offsetHeight;

    // Clear canvas
    this.ctx.clearRect(0, 0, width, height);

    // Draw grid background
    this.drawGrid(width, height);

    // Draw waveform
    this.drawWaveform(width, height);
  }

  private drawGrid(width: number, height: number) {
    this.ctx.strokeStyle = '#1a1a1a';
    this.ctx.lineWidth = 1;

    // Horizontal lines
    for (let y = 0; y <= height; y += 20) {
      this.ctx.beginPath();
      this.ctx.moveTo(0, y);
      this.ctx.lineTo(width, y);
      this.ctx.stroke();
    }

    // Vertical lines
    for (let x = 0; x <= width; x += 20) {
      this.ctx.beginPath();
      this.ctx.moveTo(x, 0);
      this.ctx.lineTo(x, height);
      this.ctx.stroke();
    }
  }

  private drawWaveform(width: number, height: number) {
    const pointSpacing = width / (this.maxPoints - 1);

    // Set color based on status
    let color = '#ff0055'; // Red (offline)
    let glowColor = 'rgba(255, 0, 85, 0.5)';

    if (this.status === 'working') {
      color = '#00ff00'; // Green
      glowColor = 'rgba(0, 255, 0, 0.8)';
    } else if (this.status === 'ready') {
      color = '#00ffff'; // Cyan
      glowColor = 'rgba(0, 255, 255, 0.5)';
    }

    // Draw glow effect
    this.ctx.shadowBlur = 10;
    this.ctx.shadowColor = glowColor;

    // Draw line
    this.ctx.strokeStyle = color;
    this.ctx.lineWidth = 2;
    this.ctx.beginPath();

    for (let i = 0; i < this.dataPoints.length; i++) {
      const x = i * pointSpacing;
      const y = height - (this.dataPoints[i] / 100) * height;

      if (i === 0) {
        this.ctx.moveTo(x, y);
      } else {
        this.ctx.lineTo(x, y);
      }
    }

    this.ctx.stroke();

    // Reset shadow
    this.ctx.shadowBlur = 0;
  }
}
