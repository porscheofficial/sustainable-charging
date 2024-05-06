import { Text, Container, Box, Input } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import ScheduleHeader from "../../components/Schedule/ScheduleHeader";
import TimelineView from "../../components/Schedule/TimelineView";
import { getSchedule } from "../../effects/schedule";
import { ChargingWindow } from "../../models/ScheduleType";

export default function Schedule() {
  const [schedule, setSchedule] = useState<ChargingWindow[]>([]);
  const [currentUserId, setCurrentUserId] = useState<string>("");

  useEffect(() => {
    const fetchSchedule = async () => {
      const response = await getSchedule(currentUserId);

      const converted: ChargingWindow[] = response.map((item: any) => ({
        startTime: new Date(item.startTime),
        endTime: new Date(item.endTime),
        emissions: item.emissions
        }));

      setSchedule(converted);
    };
    fetchSchedule();

    // todo: use debouncing instead of this approach for typing
  }, [currentUserId]);

  return (
    <>
      <ScheduleHeader />
      <Container maxW="container.xl" marginTop={20}>
        <Box display="flex" gap={10} flexDirection="row" marginBottom={10}>
          <Text fontSize="3xl" fontWeight="bold">
            Schedule
          </Text>
          <Input
            type="text"
            placeholder="User ID: e.g. max@uni-potsdam.de"
            size="lg"
            onChange={(e) => setCurrentUserId(e.target.value)}
          />
        </Box>
        {schedule.length !== 0 && <TimelineView schedule={schedule} />}
      </Container>
    </>
  );
}
