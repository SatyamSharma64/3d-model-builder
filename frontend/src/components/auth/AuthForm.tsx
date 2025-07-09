import { useState } from "react";
import { useDispatch } from "react-redux";
import { login, signup } from "@/features/auth/authSlice";
import { useNavigate } from "react-router-dom";
import GoogleButton from "./GoogleButton";
import type { AppDispatch } from "@/app/store";

export default function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (mode === "login") {
        await dispatch(login({ email, password })).unwrap(); 
      } else {
        await dispatch(signup({ email, password })).unwrap();
      }
      navigate("/");
    } catch (err: any) {
      console.error("Auth error:", err);
      setError(err.message || "Authentication failed");
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <input
        type="email"
        required
        placeholder="Email"
        className="w-full px-4 py-2 border rounded"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        required
        placeholder="Password"
        className="w-full px-4 py-2 border rounded"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p className="text-red-500 text-sm">{error}</p>}
      <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">
        {mode === "login" ? "Log In" : "Sign Up"}
      </button>
      <GoogleButton />
      <div className="text-sm text-center">
        {mode === "login" ? (
          <>Don't have an account? <a href="/signup" className="text-blue-600">Sign up</a></>
        ) : (
          <>Already have an account? <a href="/login" className="text-blue-600">Log in</a></>
        )}
      </div>
    </form>
  );
}
