import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";

export default function ProtectedRoute({ allowedRole, children }) {
  const [status, setStatus] = useState("loading"); // loading | allowed | denied
  const [role, setRole] = useState(null);

  useEffect(() => {
    const checkMe = async () => {
      try {
        const res = await fetch("/auth/me", {
          method: "GET",
          credentials: "include",
        });

        const data = await res.json();

        if (!res.ok) {
          setStatus("denied");
          return;
        }

        setRole(data.role);
        setStatus("allowed");
      } catch (e) {
        setStatus("denied");
      }
    };

    checkMe();
  }, []);

  if (status === "loading") {
    return <div style={{ padding: 20 }}>Checking session...</div>;
  }

  // Not logged in
  if (status === "denied") {
    return <Navigate to="/login" replace />;
  }

  // Logged in but wrong role
  if (allowedRole && role !== allowedRole) {
    return <Navigate to={role === "teacher" ? "/teacher" : "/student"} replace />;
  }

  return children;
}
