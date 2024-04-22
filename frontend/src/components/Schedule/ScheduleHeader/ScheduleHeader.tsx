import { Box, Image } from "@chakra-ui/react";

export default function ScheduleHeader() {
  return (
    <Box
      height={150}
      backgroundRepeat="no-repeat"
      backgroundPosition={"center"}
      backgroundAttachment="fixed"
      backgroundImage="https://news.sap.com/australia/files/2022/11/29/292501_GettyImages-1213148829_medium_jpg.jpg"
    >
      <Box display="flex" justifyContent={"center"}>
        <Image
          position="relative"
          top={50}
          h={150}
          src="https://cdn.drivek.com/configurator-imgs/cars/de/$original$/PORSCHE/TAYCAN/38809_COUPE-4-TURER/porsche-taycan-2019.png"
        />
      </Box>
    </Box>
  );
}
