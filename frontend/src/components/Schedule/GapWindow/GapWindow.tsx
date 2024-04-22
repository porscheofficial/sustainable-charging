import { VStack, Text } from "@chakra-ui/react";
import { WindowProps } from "../types";

export default function GapWindow({ window, index }: WindowProps) {
  return (
    <VStack key={`gap-${index}`} p={4} bg="red.100" width="100%">
      <Text fontWeight={800} fontSize="md">
        {window.startTime.toLocaleTimeString()} to{" "}
        {window.endTime.toLocaleTimeString()}
      </Text>
      <Text fontSize="sm">No Charging</Text>
    </VStack>
  );
}
