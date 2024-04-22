import { VStack, Text } from "@chakra-ui/react";
import { WindowProps } from "../types";

export default function AvailableChargingWindow({
  window,
  index,
}: WindowProps) {
  return (
    <VStack key={index} p={4} bg="green.100" width="100%">
      <Text fontWeight={800} fontSize="md">
        {window.startTime.toLocaleTimeString()} to{" "}
        {window.endTime.toLocaleTimeString()}
      </Text>
      <Text fontSize="sm">Emissions saved: {window.emissions} kg/CO2</Text>
    </VStack>
  );
}
