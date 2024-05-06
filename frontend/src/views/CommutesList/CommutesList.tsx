import {
  Container,
  Table,
  TableContainer,
  Tbody,
  Th,
  Thead,
  Tr,
  Text,
  Input,
  Box,
} from "@chakra-ui/react";
import RowItem from "../../components/RowItem";
import { CommuteType } from "../../models/CommuteType";
import { useEffect, useState } from "react";
import { getCommutes } from "../../effects/commutes";

// todo: refactor into more components, utils, and hooks

const isValidEmail = (email: string): boolean =>
  /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/.test(email);

export default function CommutesList() {
  const [commutes, setCommutes] = useState<CommuteType[]>([]);
  const [currentUserId, setCurrentUserId] = useState<string>("");

  useEffect(() => {
    const fetchCommutes = async () => {
      const response = await getCommutes(currentUserId);
      setCommutes(response);
    };
    if (currentUserId !== '') {
      fetchCommutes();
    }
    // todo: use debouncing instead of this approach for typing
  }, [currentUserId]);

  return (
    <Container maxW="container.xl" marginTop={10}>
      <Box display="flex" gap={10} flexDirection="row" marginBottom={10}>
        <Text fontSize="3xl" fontWeight="bold">
          Commutes
        </Text>
        <Input
          type="text"
          placeholder="User ID: e.g. max@uni-potsdam.de"
          size="lg"
          onChange={(e) => setCurrentUserId(e.target.value)}
        />
      </Box>
      <TableContainer className="py-4">
        <Table size="md">
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Single/Round Trip</Th>
              <Th>Traffic Level</Th>
              <Th>Approx. Distance (KM)</Th>
              <Th>Approx Duration (Mins)</Th>
              <Th>Usage</Th>
            </Tr>
          </Thead>

          <Tbody>
            {commutes?.map((commute) => (
              <RowItem commute={commute} />
            ))}
          </Tbody>
        </Table>
      </TableContainer>
    </Container>
  );
}
