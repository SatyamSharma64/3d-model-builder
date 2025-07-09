import Spinner from "@/utils/spinner";

export default function AppLoader() {
  return (
    <div className="h-screen w-screen flex items-center justify-center bg-black text-white">
      <Spinner />
    </div>
  );
}
