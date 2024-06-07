import React, { createContext, useContext, useState } from "react";

// UserContext 생성
const UserContext = createContext(null);

export const useUser = () => useContext(UserContext);
