export interface ChargingWindow {
  startTime: Date;
  endTime: Date;
  emissions: number | null;
}

export interface Schedule {
  availableChargingWindows: ChargingWindow[];
}
