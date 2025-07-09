import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { Suspense, useEffect, useState } from "react";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
// import * as THREE from "three";
import { useProjects } from "@/hooks/useProjects";


function ModelViewer({ url }: { url: string }) {
  const gltf = useLoader(GLTFLoader, url);

  // useEffect(() => {
  //   if (!gltf?.scene) return;
  //   gltf.scene.traverse((child) => {
  //     if ((child as THREE.Mesh).isMesh) {
  //       const mesh = child as THREE.Mesh;
  //       console.log("Mesh:", mesh.name);
  //       console.log("Material:", mesh.material);
        
  //       mesh.scale.set(1.5, 1.5, 1.5);

  //       if (mesh.name === "Cube004") {
  //         mesh.position.setX(2); 
  //       }
  //       if (mesh.name === "Cube005") {
  //         mesh.position.setX(-2); 
  //       }
  //     }
  //   });
  // }, [gltf]);

  return <primitive object={gltf.scene} scale={1.5} />;
}


function Model({ base64 }: { base64: string }) {
  const [url, setUrl] = useState<string | null>(null);

  useEffect(() => {
    if (!base64) return;

    try {
      const cleanBase64 = JSON.parse(base64); 
      const binary = atob(cleanBase64);
      const array = Uint8Array.from(binary, char => char.charCodeAt(0));
      const blob = new Blob([array], { type: "model/gltf-binary" });
      const objectUrl = URL.createObjectURL(blob);
      setUrl(objectUrl);

      return () => {
        URL.revokeObjectURL(objectUrl);
      };
    } catch (err) {
      console.error("Failed to parse base64 or generate blob:", err);
    }
  }, [base64]);

  return url ? <ModelViewer url={url} /> : null;
}

export default function ThreeCanvas({ projectId }: { projectId: string }) {
  const { activeProject } = useProjects();
  const previewUrl = activeProject?.previewUrl;

  return (
    <div className="h-full w-full bg-black text-white">
      {previewUrl ? (
        <Canvas camera={{ position: [0, 2, 5], fov: 50 }}>
          <ambientLight intensity={0.6} />
          <directionalLight position={[5, 5, 5]} intensity={1} />
          <axesHelper args={[5]} />
          <gridHelper args={[10, 10]} />
          <Suspense fallback={null}>
            <Model base64={previewUrl} />
          </Suspense>
          <OrbitControls />
        </Canvas>
      ) : (
        <div className="flex h-full items-center justify-center text-gray-400">
          No Preview Available
        </div>
      )}
    </div>
  );
}
