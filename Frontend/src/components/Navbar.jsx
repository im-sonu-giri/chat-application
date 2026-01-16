import React, { useState } from "react";

import { useAuthentication } from "../auth";
import { Link } from "react-router-dom";

const Navbar = () =>{
    const[isSidebarOpen, setSidebarOpen]= useState(false);
    const{ isAuthenticated, logout} = useAuthentication();
    const handleLogourt = () = >{
        logout();
        setMenuOpen(false);
    };
    const toggleSidebar= () =>{
        setSidebarOpen(!isSidebarOpen)
    };

    return(
        <nav className="navbar">
            <div className="navbar-container">
                <Link to ='/' className="navbar-logo-text"> <h2>Chatapp</h2></Link>

            </div>

        </nav>
    )
}