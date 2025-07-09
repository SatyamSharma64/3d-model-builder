// import { Worker } from "bullmq";
// import { connection } from "../config/redis";
// import { Job } from "bullmq";

// // Replace this with actual MCP orchestrator HTTP call
// const mockMCPExecute = async (job: Job) => {
//   console.log("⚙️ Executing MCP command:", job.data.command);
//   await new Promise((r) => setTimeout(r, 1000)); 
//   return { status: "done", output: `Result of ${job.data.command}` };
// };

// ["high", "normal", "low"].forEach((priority) => {
//   new Worker(priority, async (job) => {
//     const result = await mockMCPExecute(job);

//     // Here we would emit WebSocket update or save job result to DB
//     console.log(`✅ Job ${job.id} completed for ${job.data.userId}`);
//     return result;
//   }, { connection });
// });
