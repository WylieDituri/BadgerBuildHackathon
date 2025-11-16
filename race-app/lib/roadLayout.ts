export const ROAD_WIDTH = 24;

export type RoadSegment = {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
};

const createHorizontal = (
  y: number,
  segments: Array<[number, number]>
): RoadSegment[] => segments.map(([x1, x2]) => ({ x1, y1: y, x2, y2: y }));

const createVertical = (
  x: number,
  segments: Array<[number, number]>
): RoadSegment[] => segments.map(([y1, y2]) => ({ x1: x, y1, x2: x, y2 }));

export const roadSegments: RoadSegment[] = [
  // Perimeter ring (top, bottom, left, right)
  { x1: -190, y1: -190, x2: 190, y2: -190 },
  { x1: -190, y1: 190, x2: 190, y2: 190 },
  { x1: -190, y1: -190, x2: -190, y2: 190 },
  { x1: 190, y1: -190, x2: 190, y2: 190 },
  // Horizontal roads with gaps
  ...createHorizontal(-120, [
    [-180, -60],
    [-20, 60],
    [100, 180],
  ]),
  ...createHorizontal(0, [
    [-180, -80],
    [80, 180],
  ]),
  ...createHorizontal(120, [
    [-180, -60],
    [-20, 60],
    [100, 180],
  ]),
  // Vertical roads with gaps
  ...createVertical(-150, [
    [-180, -60],
    [-20, 60],
    [100, 180],
  ]),
  ...createVertical(-60, [
    [-180, -100],
    [-60, 0],
    [40, 180],
  ]),
  ...createVertical(60, [
    [-180, -100],
    [-60, 0],
    [40, 180],
  ]),
  ...createVertical(150, [
    [-180, -60],
    [-20, 60],
    [100, 180],
  ]),
  // Diagonals
  { x1: -100, y1: -100, x2: -40, y2: -40 },
  { x1: 40, y1: 40, x2: 100, y2: 100 },
  { x1: -100, y1: 100, x2: -40, y2: 40 },
  { x1: 40, y1: -40, x2: 100, y2: -100 },
];

const tolerance = ROAD_WIDTH / 2;

export const distanceToSegment = (px: number, py: number, segment: RoadSegment) => {
  const { x1, y1, x2, y2 } = segment;
  const dx = x2 - x1;
  const dy = y2 - y1;
  if (dx === 0 && dy === 0) {
    return Math.hypot(px - x1, py - y1);
  }
  const t = Math.max(
    0,
    Math.min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy))
  );
  const projX = x1 + t * dx;
  const projY = y1 + t * dy;
  const dist = Math.hypot(px - projX, py - projY);
  return { dist, projX, projY };
};

export const isPointOnRoad = (px: number, py: number, pad = tolerance) => {
  return roadSegments.some((segment) => distanceToSegment(px, py, segment).dist <= pad);
};

export const snapPointToRoad = (px: number, py: number) => {
  let best = { dist: Infinity, projX: px, projY: py };
  for (const segment of roadSegments) {
    const result = distanceToSegment(px, py, segment);
    if (result.dist < best.dist) {
      best = result;
    }
  }
  return { x: best.projX, y: best.projY };
};

export const drawRoadLayout = (
  ctx: CanvasRenderingContext2D,
  centerX: number,
  centerY: number,
  scale: number
) => {
  ctx.strokeStyle = "#2d3748";
  ctx.lineWidth = ROAD_WIDTH * scale;
  ctx.lineCap = "round";

  roadSegments.forEach(({ x1, y1, x2, y2 }) => {
    ctx.beginPath();
    ctx.moveTo(centerX + x1 * scale, centerY + y1 * scale);
    ctx.lineTo(centerX + x2 * scale, centerY + y2 * scale);
    ctx.stroke();
  });
};
