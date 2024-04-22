import {
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Stack,
  useToast,
  Checkbox,
} from "@chakra-ui/react";
import { Form, Field } from "react-final-form";
import arrayMutators from "final-form-arrays";
import { CommuteType } from "../../models/CommuteType";
import { addCommute } from "../../effects/commutes";
import UsageArrayField from "./components/UsageArrayField";

export default function CommuteForm() {
  const toast = useToast();

  const handleSubmit = async (values: CommuteType) => {
    try {
      const response = await addCommute(values);
      toast({
        title: "Success!",
        description: response.message,
        status: "success",
      });
    } catch (error) {
      toast({
        title: "Error occurred.",
        description: "Couldn't add commute.",
        status: "error",
      });
    }
  };

  return (
    <Form
      onSubmit={handleSubmit}
      mutators={{ ...arrayMutators }}
      initialValues={{
        isRoundTrip: false,
        usage: [],
        approxDistanceKm: 0,
        approxDurationMinutes: 0,
        traffic: "LOW",
      }}
      render={({ handleSubmit, form }) => (
        <form
          onSubmit={(event) => handleSubmit(event)?.then(() => form.reset())}
        >
          <Stack spacing={4}>
            <Field name="userId">
              {({ input }) => (
                <FormControl>
                  <FormLabel>User ID</FormLabel>
                  <Input {...input} type="text" />
                </FormControl>
              )}
            </Field>

            <Field name="name">
              {({ input }) => (
                <FormControl>
                  <FormLabel>Commute Name</FormLabel>
                  <Input {...input} type="text" />
                </FormControl>
              )}
            </Field>

            <Field name="isRoundTrip" type="checkbox">
              {({ input }) => (
                <FormControl>
                  <FormLabel>Round Trip</FormLabel>
                  <Checkbox {...input} />
                </FormControl>
              )}
            </Field>

            <Field name="approxDistanceKm" type="number">
              {({ input }) => (
                <FormControl>
                  <FormLabel>Approximate Distance (km)</FormLabel>
                  <Input {...input} />
                </FormControl>
              )}
            </Field>
            <Field name="approxDurationMinutes" type="number">
              {({ input }) => (
                <FormControl>
                  <FormLabel>Approximate Duration (minutes)</FormLabel>
                  <Input {...input} />
                </FormControl>
              )}
            </Field>
            <Field name="traffic" component="select">
              {({ input }) => (
                <FormControl>
                  <FormLabel>Traffic Level</FormLabel>
                  <Select {...input}>
                    <option value="LOW">Low</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="HIGH">High</option>
                  </Select>
                </FormControl>
              )}
            </Field>

            <UsageArrayField />

            <Button mt={4} bg="#90F59F" type="submit">
              Submit
            </Button>
          </Stack>
        </form>
      )}
    />
  );
}
