import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuthentication } from "../auth";

function ProtectedRoute({ children }) {
    const { isAuthenticated } = useAuthentication();
    const navigate = useNavigate();

    useEffect(() => {
        if (isAuthenticated === null) return; 

        if (!isAuthenticated) {
         
            navigate('/login');
        } else if (isAuthenticated && (window.location.pathname === '/login' || window.location.pathname === '/register')) {

            navigate('/chats');
        }
    }, [isAuthenticated, navigate]);

    if (isAuthenticated === null) {

        return <div>Loading...</div>;
    }

    if (!isAuthenticated) {

        return null;
    }

    return children;
}

export default ProtectedRoute;