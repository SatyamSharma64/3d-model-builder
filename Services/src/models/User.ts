import mongoose from "mongoose";

export interface IUser extends mongoose.Document {
  email: string;
  password?: string;
  name?: string;
  provider: "credentials" | "google";
  createdAt: Date;
  _id: mongoose.Types.ObjectId; 
}

const UserSchema = new mongoose.Schema<IUser>({
  email: { type: String, required: true, unique: true },
  password: { type: String },
  name: { type: String },
  provider: {
    type: String,
    enum: ["credentials", "google"],
    default: "credentials",
  },
  createdAt: { type: Date, default: Date.now },
});

export const User = mongoose.model<IUser>("User", UserSchema);
