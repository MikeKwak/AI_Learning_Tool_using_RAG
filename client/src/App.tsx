import React from "react";
import { ThemeProvider } from "@mui/material/styles";
import { Route, Routes } from "react-router-dom";
import theme from "./theme";

import MainPage from "./pages/MainPage";

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Routes>
        <Route path="/" element={<MainPage />} />
        <Route path="*" element={<h1>Not Found</h1>} />
      </Routes>
    </ThemeProvider>
  );
}

export default App;
