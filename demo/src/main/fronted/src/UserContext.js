import React, { createContext, useContext, useState } from 'react';

// UserContext 생성
const UserContext = createContext(null);

// UserContext를 사용하기 위한 커스텀 훅
export const useUser = () => useContext(UserContext);

// UserProvider 컴포넌트
export const UserProvider = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [username, setUsername] = useState("");

    const handleLogin = (username) => {
        setIsLoggedIn(true);
        setUsername(username);
    };

    const handleLogout = () => {
        setIsLoggedIn(false);
        setUsername("");
    };

    return (
        <UserContext.Provider value={{ isLoggedIn, username, handleLogin, handleLogout }}>
            {children}
        </UserContext.Provider>
    );
};
