import { useState } from "react";
import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function MainLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true); 

  return (
    <div className="flex flex-col h-screen w-screen">
      <Navbar onToggleSidebar={() => setSidebarOpen((prev) => !prev)} />
      <div className="flex flex-1 overflow-hidden">
        {sidebarOpen && (
          <div className="hidden md:block">
            <Sidebar />
          </div>
        )}

        <main className="flex-1 overflow-hidden bg-gray-100 dark:bg-zinc-900">
          {children}
        </main>
      </div>
    </div>
  );
}
