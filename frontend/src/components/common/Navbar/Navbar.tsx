import {
  Box,
  Stack,
  Heading,
  Flex,
  Text,
  Button,
  Link,
} from "@chakra-ui/react";

export default function Navbar(props: object) {
  return (
    <Flex
      as="nav"
      align="center"
      justify="space-between"
      wrap="wrap"
      padding={6}
      bg="#052D2E"
      color="#90F59F"
      {...props}
    >
      <Flex align="center" mr={5}>
        <Link href="/" textDecoration="none">
          <Heading as="h1" size="lg" letterSpacing={"tighter"}>
            Chargify
          </Heading>
        </Link>
      </Flex>

      <Stack width="auto" flexGrow={1}>
        <Link href="/commutes" textDecoration="none">
          <Text mx={2}>Commutes</Text>
        </Link>
      </Stack>

      <Box mt={{ base: 4, md: 0 }}>
        <Link href="/schedule" textDecoration="none">
          <Button _hover={{ bg: "#90F59F" }}>View Schedule</Button>
        </Link>
      </Box>
    </Flex>
  );
}
