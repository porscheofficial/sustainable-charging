import {
  Box,
  Button,
  FormLabel,
  HStack,
  Input,
  Select,
} from "@chakra-ui/react";
import { Field } from "react-final-form";
import { FieldArray } from "react-final-form-arrays";
import { DeleteIcon } from "@chakra-ui/icons";

export default function UsageArrayField() {
  return (
    <FieldArray name="usage">
      {({ fields }) => (
        <Box>
          <FormLabel>Usage</FormLabel>
          {fields.map((name, index) => (
            <HStack key={name} mb={3}>
              <Field name={`${name}.day`} component="select">
                {({ input }) => (
                  <Select {...input}>
                    <option disabled>Select day</option>
                    <option value="MON">Monday</option>
                    <option value="TUE">Tuesday</option>
                    <option value="WED">Wednesday</option>
                    <option value="THU">Thursday</option>
                    <option value="FRI">Friday</option>
                    <option value="SAT">Saturday</option>
                    <option value="SUN">Sunday</option>
                  </Select>
                )}
              </Field>

              <Field name={`${name}.startTime`} component="input" type="time">
                {({ input }) => <Input {...input} />}
              </Field>

              <Field name={`${name}.endTime`} component="input" type="time">
                {({ input }) => <Input {...input} />}
              </Field>

              <Button onClick={() => fields.remove(index)}>
                <DeleteIcon />
              </Button>
            </HStack>
          ))}
          <Button onClick={() => fields.push({})}>Add Usage</Button>
        </Box>
      )}
    </FieldArray>
  );
}
