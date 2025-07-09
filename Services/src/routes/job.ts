// import express from "express";
// import { JobSchema } from "../validators/validateJob";
// import { addJobToQueue, getJobStatus } from "../services/queueService";

// const router = express.Router();

// router.post("/enqueue", async (req, res) => {
//   try {
//     const job = JobSchema.parse(req.body);
//     const jobId = await addJobToQueue(job);
//     res.status(200).json({ jobId, status: "queued" });
//   } catch (err: any) {
//     res.status(400).json({ error: err.errors || "Invalid job request" });
//   }
// });

// router.get("/status/:queue/:id", async (req, res) => {
//   const { id, queue } = req.params;

//   try {
//     const status = await getJobStatus(queue, id);
//     if (!status){
//         res.status(404).json({ error: "Job not found" });
//         return
//     }
//     res.status(200).json(status);
//   } catch (err) {
//     res.status(500).json({ error: "Could not fetch job status" });
//   }
// });

// export default router;
