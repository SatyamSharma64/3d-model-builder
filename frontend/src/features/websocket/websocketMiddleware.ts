// import type { Middleware, MiddlewareAPI, Dispatch, UnknownAction } from "@reduxjs/toolkit";
// import { messageReceived } from "./websocketSlice";
// import { receiveMessage } from "../chat/chatSlice";
// import { setPreviewUrl } from "../projects/projectSlice";

// interface JobStartedPayload {
//   type: "job_started";
//   job_id: string;
// }

// interface JobCompletedPayload {
//   type: "job_completed";
//   job_id: string;
//   result: string;
//   base64data: string;
//   project_id: string;
// }

// interface JobFailedPayload {
//   type: "job_failed";
//   job_id: string;
//   error: string;
// }

// type WebSocketPayload = JobStartedPayload | JobCompletedPayload | JobFailedPayload | { type: string; [key: string]: any };

// export const websocketMiddleware: Middleware = (store: MiddlewareAPI<Dispatch<UnknownAction>, any>) => (next: Dispatch<UnknownAction>) => (action: UnknownAction) => {
//   if (action.type === messageReceived.type) {
//     const payload = action.payload as WebSocketPayload;

//     switch (payload.type) {
//       case "job_started":
//         store.dispatch(
//           receiveMessage({
//             sender: "system",
//             content: `Job started (ID: ${payload.job_id})`,
//           })
//         );
//         break;

//       case "job_completed":
//         store.dispatch(
//           receiveMessage({
//             sender: "ai",
//             content: payload.result,
//           })
//         );
//         store.dispatch(
//           setPreviewUrl({
//             projectId: payload.project_id,
//             url: payload.base64data,
//           })
//         );
//         break;

//       case "job_failed":
//         store.dispatch(
//           receiveMessage({
//             sender: "system",
//             content: `Job failed: ${payload.error}`,
//           })
//         );
//         break;

//       default:
//         console.warn("Unknown WebSocket message type:", payload.type);
//     }
//   }

//   return next(action);
// };
