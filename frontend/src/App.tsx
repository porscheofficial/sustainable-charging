import { ChakraProvider } from "@chakra-ui/react";
import Navbar from "./components/common/Navbar";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import CommuteAdd from "./views/CommuteAdd";
import CommutesList from "./views/CommutesList";
import Schedule from "./views/Schedule";

const App = () => {
  return (
    <ChakraProvider>
      <Navbar />

      <BrowserRouter>
        <Routes>
          <Route path="/" element={<CommuteAdd />} />
          <Route path="/commutes" element={<CommutesList />} />
          <Route path="/schedule" element={<Schedule />} />
        </Routes>
      </BrowserRouter>
    </ChakraProvider>
  );
};

export default App;
