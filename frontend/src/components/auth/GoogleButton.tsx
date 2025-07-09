export default function GoogleButton() {
  const handleGoogleLogin = () => {
    window.location.href = `${import.meta.env.VITE_API_URL}/api/auth/google`;
  };

  return (
    <button
      type="button"
      onClick={handleGoogleLogin}
      className="w-full flex items-center justify-center border py-2 rounded mt-2 hover:bg-gray-100"
    >
      <img src="/google-logo.svg" alt="Google" className="w-5 h-5 mr-2" />
      Continue with Google
    </button>
  );
}
