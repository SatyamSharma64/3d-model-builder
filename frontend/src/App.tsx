import { BrowserRouter } from "react-router-dom";
import AppRoutes from "./routes";
import { useDispatch } from "react-redux";
import { useEffect } from "react";
import { api } from "./services/api";
import { logout, setUser } from "./features/auth/authSlice";

export default function App() {

  const dispatch = useDispatch();

  useEffect(() => {
    api.get("/auth/me", { withCredentials: true })
      .then(res => {
        console.log("dispatching set user");
        if (res.data?.user) dispatch(setUser(res.data.user));
        console.log("dispatched set user")
      })
      .catch(err => {
        console.log("User not authenticated");
        dispatch(logout());
      });
  }, []);


  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}
