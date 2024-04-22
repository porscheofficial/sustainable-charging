import { Container, Text } from "@chakra-ui/react";
import CommuteForm from "../../components/CommuteForm";

export default function CommuteAdd() {
  return (
    <Container marginTop={10}>
      <Text fontSize="3xl" fontWeight="bold" marginBottom={5}>
        Add a commute
      </Text>
      <CommuteForm />
    </Container>
  );
}
