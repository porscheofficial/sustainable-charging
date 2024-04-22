import { Tr, Td, Badge, Tag } from "@chakra-ui/react";
import { CommuteType, TrafficLevel } from "../../models/CommuteType";

interface RowItemProps {
  commute: CommuteType;
}

const getTrafficColorScheme = (traffic: TrafficLevel) => {
  switch (traffic) {
    case "LOW":
      return "green";
    case "MEDIUM":
      return "yellow";
    case "HIGH":
      return "red";
    default:
      return "gray";
  }
};

export default function RowItem({ commute }: RowItemProps) {
  return (
    <Tr className="hover:bg-gray-100">
      <Td>{commute.name}</Td>
      <Td>
        {commute.isRoundTrip ? (
          <Badge colorScheme="purple">Round Trip</Badge>
        ) : (
          <Badge colorScheme="blue">Single Trip</Badge>
        )}
      </Td>
      <Td>
        <Badge colorScheme={getTrafficColorScheme(commute.traffic)}>
          {commute.traffic}
        </Badge>
      </Td>
      <Td>{commute.approxDistanceKm} KM</Td>
      <Td>{commute.approxDurationMinutes} Minutes</Td>
      <Td>
        {commute.usage.map((u) => (
          <Tag marginRight={2}>
            {u.day} from {u.startTime} to {u.endTime}
          </Tag>
        ))}
      </Td>
    </Tr>
  );
}
