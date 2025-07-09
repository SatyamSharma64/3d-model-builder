import mongoose from "mongoose";

export interface IProject extends mongoose.Document {
  name: string;
  description?: string;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

const ProjectSchema = new mongoose.Schema<IProject>({
  name: { type: String, required: true },
  description: { type: String },
  userId: { type: String, required: true },
}, { timestamps: true });

export const Project = mongoose.model<IProject>("Project", ProjectSchema);
