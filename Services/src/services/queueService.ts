// import { JobData } from "../types/Job";
// import { queues } from "../config/redis";

// export const addJobToQueue = async (data: JobData) => {
//   const priority = data.priority || "normal";
//   const queue = queues[priority];

//   const job = await queue.add("mcp-task", data, {
//     attempts: 3,
//     backoff: { type: "exponential", delay: 500 },
//     removeOnComplete: true,
//     removeOnFail: false,
//   });

//   return job.id;
// };

// export const getJobStatus = async (queueName: string, jobId: string) => {
//   const queue = queues[queueName as keyof typeof queues];
//   const job = await queue.getJob(jobId);

//   if (!job) return null;

//   return {
//     id: job.id,
//     status: await job.getState(),
//     result: job.returnvalue,
//     failedReason: job.failedReason,
//     attemptsMade: job.attemptsMade,
//   };
// };
