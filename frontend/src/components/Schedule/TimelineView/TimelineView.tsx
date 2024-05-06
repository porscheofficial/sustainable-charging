import { VStack, Text, Box } from "@chakra-ui/react";
import { findGaps } from "../utils";
import AvailableChargingWindow from "../AvailableChargingWindow";
import GapWindow from "../GapWindow";
import { ChargingWindow } from "../../../models/ScheduleType";

export default function TimelineView({ schedule }: { schedule: ChargingWindow[] }) {
  // Merge and sort windows and gaps
  const mergedTimeline = [
    ...schedule,
    ...findGaps(schedule),
  ].sort((a, b) => a.startTime.getTime() - b.startTime.getTime());

  // Split the timeline into chunks for each day
  const timelineChunks: { [key: string]: ChargingWindow[] } = {};
  mergedTimeline.forEach((item) => {
    const dayKey = item.startTime.toISOString().split("T")[0];
    timelineChunks[dayKey] = timelineChunks[dayKey] || [];
    timelineChunks[dayKey].push(item);
  });

  return (
    <Box w="100%" p={5}>
      {Object.entries(timelineChunks).map(([day, items]) => (
        <Box key={day} mb={8}>
          <Text fontSize="lg" color="gray.600" mb={4}>
            Schedule for {day}
          </Text>
          <VStack spacing={4}>
            {items.map((item, index) =>
              item.emissions ? (
                <AvailableChargingWindow index={index} window={item} />
              ) : (
                <GapWindow index={index} window={item} />
              )
            )}
          </VStack>
        </Box>
      ))}
    </Box>
  );
}
