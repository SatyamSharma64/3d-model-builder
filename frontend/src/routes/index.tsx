import { Routes, Route, Navigate } from "react-router-dom";
// import Dashboard from "../pages/Dashboard";
import Viewer from "../pages/Viewer";
import Login from "../pages/Login";
import AppLoader from "../components/viewer/PageLoader"
import SignupPage from "@/pages/Signup";
import { useSelector } from "react-redux";
import type { RootState } from "@/app/store";

export default function AppRoutes() {

  const {user, isLoading} = useSelector((state: RootState) => state.auth);
  console.log("from routes line 12:", user)

  if(isLoading){
    return <AppLoader />
  }
  
  return (
    <Routes>
      <Route path="/" element={user ? <Viewer /> : <Navigate to="/login" />} />
      <Route
        path="/viewer/:projectId"
        element={user ? <Viewer /> : <Navigate to="/login" />}
      />
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<SignupPage />} />
    </Routes>
  );
}
