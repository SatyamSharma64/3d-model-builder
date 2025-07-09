import { useProjects } from "../hooks/useProjects";
import ProjectCard from "../components/project/ProjectCard";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const { projects, status } = useProjects();
  const navigate = useNavigate();

  return (
    <div className="p-4">
      <h1 className="text-2xl mb-4">Your Projects</h1>
      {status === "loading" ? (
        <p>Loading...</p>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          {projects.map((p) => (
            <ProjectCard
              key={p._id}
              project={p}
              onOpen={(id: string) => navigate(`/viewer/${id}`)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
