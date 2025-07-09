import AuthForm from "@/components/auth/AuthForm";

export default function LoginPage() {
  return (
    <div className="flex h-screen bg-zinc-100">
      <div className="m-auto w-full max-w-md p-6 bg-white rounded-lg shadow">
        <h2 className="text-2xl font-bold mb-6 text-center">Welcome Back</h2>
        <AuthForm mode="login" />
      </div>
    </div>
  );
}
