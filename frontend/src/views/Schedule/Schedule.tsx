import { Text, Container, Box, Input } from "@chakra-ui/react";
import { mockSchedule } from "./mockData";
import { useState } from "react";
import ScheduleHeader from "../../components/Schedule/ScheduleHeader";
import TimelineView from "../../components/Schedule/TimelineView";

export default function Schedule() {
  // todo: make request to get schedule for user
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [currentUserId, setCurrentUserId] = useState<string>("");

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

        <TimelineView schedule={mockSchedule} />
      </Container>
    </>
  );
}
