import { MenuIcon } from "lucide-react";
import { Sheet, SheetTrigger, SheetContent } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import Sidebar from "./Sidebar";

interface NavbarProps {
  onToggleSidebar: () => void;
}

export default function Navbar({ onToggleSidebar }: NavbarProps) {
  return (
    <header className="h-14 px-4 bg-zinc-900 text-white flex items-center justify-between border-b border-zinc-700">
      <div className="flex items-center gap-2">
        {/* Unified Toggle Button */}
        <div className="block md:hidden">
          {/* Mobile View: Sheet Toggle */}
          <Sheet>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon">
                <MenuIcon className="w-5 h-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="left" className="p-0 w-64">
              <Sidebar />
            </SheetContent>
          </Sheet>
        </div>

        <div className="hidden md:block">
          {/* Desktop View: Collapse Toggle */}
          <Button variant="ghost" size="icon" onClick={onToggleSidebar}>
            <MenuIcon className="w-5 h-5" />
          </Button>
        </div>

        <h1 className="text-lg font-semibold">3D Design AI</h1>
      </div>

      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm">Settings</Button>
        <Avatar className="h-8 w-8 cursor-pointer">
          <AvatarFallback>U</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
}
