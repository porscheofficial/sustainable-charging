export enum DayOfWeek {
  SUN = "SUN",
  MON = "MON",
  TUE = "TUE",
  WED = "WED",
  THU = "THU",
  FRI = "FRI",
  SAT = "SAT",
}

export enum TrafficLevel {
  LOW = "LOW",
  MEDIUM = "MEDIUM",
  HIGH = "HIGH",
}

export interface UsageEntry {
  day: DayOfWeek;
  startTime: string;
  endTime: string;
}

export interface CommuteType {
  userId: string;
  name: string;
  isRoundTrip: boolean;
  usage: UsageEntry[];
  approxDistanceKm: number;
  approxDurationMinutes: number;
  traffic: TrafficLevel;
}
