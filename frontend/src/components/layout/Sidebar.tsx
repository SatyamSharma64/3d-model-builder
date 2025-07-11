import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useProjects } from "@/hooks/useProjects";
import { NavLink } from "react-router-dom";
import DialogBox from "../project/ProjectDialog";

export default function Sidebar() {
  const { projects } = useProjects();

  return (
    <aside className="w-64 h-full bg-zinc-900 text-white flex flex-col border-r border-zinc-800">
      <div className="p-4">
        <h2 className="text-sm font-medium uppercase tracking-wide mb-2 text-gray-300">Projects</h2>
      </div>
      <ScrollArea className="flex-1 px-2">
        <div className="space-y-2">
          {projects.map((project) => (
            <NavLink
              to={`/viewer/${project._id}`}
              key={project._id}
              className={({ isActive }) =>
                `w-full block px-4 py-2 rounded text-left text-sm ${
                  isActive ? "bg-zinc-800 font-semibold" : "hover:bg-zinc-800"
                }`
              }
            >
              {project.name}
            </NavLink>
          ))}
        </div>
      </ScrollArea>
      <div className="p-4">
        <DialogBox 
          trigger = {<Button
          className="w-full"
        >
          + New Project
        </Button>} />
      </div>
    </aside>
  );
}
