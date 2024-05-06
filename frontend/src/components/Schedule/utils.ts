import { ChargingWindow } from "../../models/ScheduleType";

export const findGaps = (schedule: ChargingWindow[]): ChargingWindow[] => {
  let gaps: ChargingWindow[] = [];
  let windows = schedule;

  // Sort windows by start time
  windows.sort((a, b) => a.startTime.getTime() - b.startTime.getTime());

  // Initialize day start and end
  let dayStart = new Date(windows[0].startTime);
  dayStart.setHours(0, 0, 0, 0);
  let dayEnd = new Date(dayStart);
  dayEnd.setHours(23, 59, 59, 999);

  windows.forEach((window, index) => {
    // If new day, reset dayEnd
    if (window.startTime > dayEnd) {
      dayStart = new Date(window.startTime);
      dayStart.setHours(0, 0, 0, 0);
      dayEnd = new Date(dayStart);
      dayEnd.setHours(23, 59, 59, 999);
    }

    // Check for gap after the current window and before the next
    const nextWindow = windows[index + 1];
    if (!nextWindow || nextWindow.startTime > dayEnd) {
      if (window.endTime < dayEnd) {
        gaps.push({
          startTime: window.endTime,
          endTime: dayEnd,
          emissions: null,
        });
      }
    } else if (window.endTime < nextWindow.startTime) {
      gaps.push({
        startTime: window.endTime,
        endTime: nextWindow.startTime,
        emissions: null,
      });
    }
  });

  return gaps;
};
